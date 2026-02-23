from typing import Any, Optional, Tuple, Union

from packaging.version import Version

from .id_generator import RandomIdGenerator


class OutputFormat(object):
    def __init__(
        self,
        punctuation_spaces: bool = False,
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
        self.resource_ids_as_strings = resource_ids_as_strings
        self.typed_array_support = typed_array_support
        self.packed_byte_array_base64_support = packed_byte_array_base64_support
        self.packed_vector4_array_support = packed_vector4_array_support
        self.typed_dictionary_support = typed_dictionary_support
        self.string_name_support = string_name_support
        self.load_steps = load_steps
        self.packed_array_format = packed_array_format

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

    def generate_id(self, section: Any, index: int) -> str:
        return self._id_generator.generate(section, index)


class VersionOutputFormat(OutputFormat):
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
