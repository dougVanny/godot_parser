from typing import Any, Optional, Tuple, Union

from packaging.version import Version

from .id_generator import RandomIdGenerator


class OutputFormat(object):
    def __init__(
        self,
        punctuation_spaces: bool = False,
        single_line_on_empty_dict: bool = True,
        resource_ids_as_strings: bool = True,
        typed_array_support: bool = True,
        packed_byte_array_base64_support: bool = True,
        packed_vector4_array_support: bool = True,
        typed_dictionary_support: bool = True,
        string_name_support=True,
        load_steps: bool = False,
        packed_array_format="Packed%sArray",
    ):
        self.punctuation_spaces = punctuation_spaces
        self.single_line_on_empty_dict = single_line_on_empty_dict
        self.resource_ids_as_strings = resource_ids_as_strings
        self.typed_array_support = typed_array_support
        self.packed_byte_array_base64_support = packed_byte_array_base64_support
        self.packed_vector4_array_support = packed_vector4_array_support
        self.typed_dictionary_support = typed_dictionary_support
        self.string_name_support = string_name_support
        self.load_steps = load_steps
        self.packed_array_format = packed_array_format

        self._force_format_4_if_available = False
        self._id_generator = RandomIdGenerator()

    def surround_string(
        self, punctuation: Union[str, Tuple[str, str]], content: str
    ) -> str:
        if isinstance(punctuation, str):
            right = left = punctuation
        else:
            left = punctuation[0]
            right = punctuation[1]

        if self.punctuation_spaces:
            left += " "
            right = " " + right

        return left + content + right

    def surround_parentheses(self, content: str) -> str:
        return self.surround_string(("(", ")"), content)

    def surround_brackets(self, content: str) -> str:
        return self.surround_string(("[", "]"), content)

    def generate_id(self, section: Any) -> str:
        return self._id_generator.generate(section)


class VersionOutputFormat(OutputFormat):
    __V36 = Version("3.6")
    __V40 = Version("4.0")
    __V43 = Version("4.3")
    __V44 = Version("4.4")
    __V46 = Version("4.6")

    def __init__(self, version: Union[str, Version]):
        if not isinstance(version, Version):
            version = Version(version)

        self.version = version

        super().__init__(
            punctuation_spaces=version < self.__V40,
            single_line_on_empty_dict=version >= self.__V40,
            resource_ids_as_strings=version >= self.__V40,
            typed_array_support=version >= self.__V40,
            packed_byte_array_base64_support=version >= self.__V43,
            packed_vector4_array_support=version >= self.__V43,
            typed_dictionary_support=version >= self.__V44,
            string_name_support=version >= self.__V40,
            load_steps=version < self.__V46,
            packed_array_format=(
                "Pool%sArray" if version < self.__V40 else "Packed%sArray"
            ),
        )

    @classmethod
    def guess_version(cls, gd_common_file) -> "VersionOutputFormat":
        from .objects import (
            ExtResource,
            PackedByteArray,
            PackedVector4Array,
            SubResource,
            TypedDictionary,
        )

        format = None

        if "format" in gd_common_file._sections[0].header:
            format = gd_common_file._sections[0].header["format"]

        version = cls.__V40

        if format == 2:
            version = cls.__V36
            return cls(version)
        if not "load_steps" in gd_common_file._sections[0].header:
            version = cls.__V46

        force_format_4 = False

        if format == 4:
            version = max(version, cls.__V43)
            force_format_4 = True

        for reference in gd_common_file._iter_resource_references():
            if isinstance(reference, SubResource) and isinstance(reference.id, int):
                version = cls.__V36
                return cls(version)
            elif isinstance(reference, ExtResource) and isinstance(reference.id, int):
                version = cls.__V36
                return cls(version)
            elif isinstance(reference, TypedDictionary):
                version = max(version, cls.__V44)
            elif isinstance(reference, PackedVector4Array):
                version = max(version, cls.__V43)
            elif (
                isinstance(reference, PackedByteArray) and reference._stored_as_base64()
            ):
                version = max(version, cls.__V43)

        output_format = cls(version)

        if force_format_4:
            output_format._force_format_4_if_available = True

        return output_format


class Outputable(object):
    def _output_to_string(self, output_format: OutputFormat) -> str:
        raise NotImplementedError(
            "output_to_string method not defined in %s" % type(self)
        )

    def output_to_string(self, output_format: Optional[OutputFormat] = None) -> str:
        if output_format is None:
            output_format = OutputFormat()
        return self._output_to_string(output_format)

    def __str__(self) -> str:
        return self.output_to_string()
