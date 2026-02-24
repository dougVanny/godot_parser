#!/usr/bin/env python
import argparse
import difflib
import io
import os
import re
import sys
import traceback

from godot_parser import parse
from godot_parser.output import VersionOutputFormat

# Regex to detect space sequences
space_re = re.compile(r" +")
# Regex to detect all spaces not surrounded by alphanumeric characters
line_normalizer_re = re.compile(r"(?<=\W) +| +(?=\W)")
# Regex to detect quotes and possible escape sequences
find_quote_re = re.compile(r"(\\*\")")


def join_lines_within_quotes(input: list[str], unescape: bool):
    buffer_list = []
    lines = []
    buffer = ""

    for part in input:
        # Find all quotes that are not escaped
        # " is not escaped. \" is escaped. \\" is not escaped as \\ becomes \, leaving the quote unescaped
        read_pos = 0
        for match in find_quote_re.finditer(part):
            span = match.span()
            match_text = part[span[0] : span[1]]
            buffer += part[read_pos : span[1]]
            read_pos = span[1]
            if len(match_text) % 2 == 1:
                buffer_list.append(buffer)
                buffer = ""
        buffer += part[read_pos:]

        if (len(buffer_list) % 2 == 0) and buffer:
            buffer_list.append(buffer)
            buffer = ""

        if buffer:
            buffer += "\n"
        else:
            for i in range(len(buffer_list)):
                if i % 2 == 0:
                    buffer_list[i] = space_re.sub(" ", buffer_list[i])
                    buffer_list[i] = line_normalizer_re.sub("", buffer_list[i])
                elif unescape:
                    buffer_list[i] = (
                        buffer_list[i]
                        .encode("latin-1", "backslashreplace")
                        .decode("unicode-escape")
                    )
            lines.append("".join(buffer_list) + "\n")
            buffer_list = []
            buffer = ""

    if buffer:
        buffer_list.append(buffer)
    if buffer_list:
        for i in range(len(buffer_list)):
            if i % 2 == 0:
                buffer_list[i] = space_re.sub(" ", buffer_list[i])
                buffer_list[i] = line_normalizer_re.sub("", buffer_list[i])
            elif unescape:
                buffer_list[i] = (
                    buffer_list[i]
                    .encode("latin-1", "backslashreplace")
                    .decode("unicode-escape")
                )
        lines.append("".join(buffer_list) + "\n")

    return lines


def _parse_and_test_file(filename: str, verbose: bool) -> bool:
    if verbose:
        print("Parsing %s" % filename)
    with open(filename, "r", encoding="utf-8") as ifile:
        original_file = ifile.read()
    try:
        parsed_file = parse(original_file)
        output_format = VersionOutputFormat.guess_version(parsed_file)
        output_file = parsed_file.output_to_string(output_format)
    except Exception:
        print("! Parsing error on %s" % filename, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

    diff = list(
        difflib.context_diff(
            io.StringIO(original_file).readlines(),
            io.StringIO(str(output_file)).readlines(),
            fromfile=filename,
            tofile="PARSED FILE",
        )
    )
    diff = ["    " + "\n    ".join(l.strip().split("\n")) + "\n" for l in diff]

    if len(diff) == 0:
        return True

    print("! Difference detected on %s" % filename)
    print("  Version detected: %s" % output_format.version)
    sys.stdout.writelines(diff)
    return False


def main():
    """Test the parsing of one tscn file or all files in directory"""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("file_or_dir", help="Parse file or files under this directory")
    parser.add_argument(
        "--all", action="store_true", help="Tests all files even if one fails"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Prints all file paths as they're parsed",
    )
    args = parser.parse_args()
    if os.path.isfile(args.file_or_dir):
        _parse_and_test_file(args.file_or_dir, args.verbose)
    else:
        all_passed = True
        for root, _dirs, files in os.walk(args.file_or_dir, topdown=False):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".tscn", ".tres"]:
                    continue
                filepath = os.path.join(root, file)
                if not _parse_and_test_file(filepath, args.verbose):
                    all_passed = False
                    if not args.all:
                        return 1

        if all_passed:
            print("All tests passed!")


if __name__ == "__main__":
    sys.exit(main())
