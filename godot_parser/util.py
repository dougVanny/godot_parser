"""Utils"""

import os
from typing import Optional, Union

from .output import Outputable, OutputFormat


def stringify_object(value, output_format: OutputFormat = OutputFormat()):
    """Serialize a value to the godot file format"""
    if value is None:
        return "null"
    elif isinstance(value, str):
        return '"%s"' % value.replace("\\", "\\\\").replace('"', '\\"')
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, dict):
        if len(value.values()) == 0:
            if output_format.single_line_on_empty_dict:
                return "{}"
            else:
                return "{\n}"
        return (
            "{\n"
            + ",\n".join(
                [
                    "%s: %s"
                    % (
                        stringify_object(k, output_format),
                        stringify_object(v, output_format),
                    )
                    for k, v in value.items()
                ]
            )
            + "\n}"
        )
    elif isinstance(value, list):
        return output_format.surround_brackets(
            ", ".join([stringify_object(v, output_format) for v in value])
        )
    elif isinstance(value, Outputable):
        return value.output_to_string(output_format)
    else:
        return str(value)


def find_project_root(start: str) -> Optional[str]:
    curdir = start
    if os.path.isfile(start):
        curdir = os.path.dirname(start)
    while True:
        if os.path.isfile(os.path.join(curdir, "project.godot")):
            return curdir
        next_dir = os.path.dirname(curdir)
        if next_dir == curdir:
            return None
        curdir = next_dir


def gdpath_to_filepath(root: str, path: str) -> str:
    if not is_gd_path(path):
        raise ValueError("'%s' is not a godot resource path" % path)
    pieces = path[6:].split("/")
    return os.path.join(root, *pieces)


def filepath_to_gdpath(root: str, path: str) -> str:
    return "res://" + os.path.relpath(path, root).replace("\\", "/")


def is_gd_path(path: str) -> bool:
    return path.startswith("res://")


class Identifiable(object):
    def get_id(self) -> Optional[Union[int, str]]:
        return None
