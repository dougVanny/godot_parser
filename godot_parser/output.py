from typing import Any, Optional, Tuple, Union

from packaging.version import Version

from .id_generator import RandomIdGenerator


class OutputFormat(object):
    def __init__(
        self,
        punctuation_spaces: bool = False,
        resource_ids_as_strings: bool = True,
        explicit_typed_array: bool = True,
        packed_byte_array_base64_support: bool = True,
        explicit_typed_dictionary: bool = True,
        load_steps: bool = False,
    ):
        self.punctuation_spaces = punctuation_spaces
        self.resource_ids_as_strings = resource_ids_as_strings
        self.explicit_typed_array = explicit_typed_array
        self.packed_byte_array_base64_support = packed_byte_array_base64_support
        self.explicit_typed_dictionary = explicit_typed_dictionary
        self.load_steps = load_steps

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
            explicit_typed_array=version >= self.__V40,
            packed_byte_array_base64_support=version >= self.__V43,
            explicit_typed_dictionary=version >= self.__V44,
            load_steps=version < self.__V46,
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
