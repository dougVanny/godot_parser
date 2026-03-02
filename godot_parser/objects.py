"""Wrappers for Godot's non-primitive object types"""

import base64
import json
import re
from functools import partial
from math import floor
from typing import Any, Iterable, List, Optional, Type, TypeVar, Union

from .output import Outputable, OutputFormat
from .util import Identifiable, stringify_object

GD_OBJECT_REGISTRY = {}


class GDObjectMeta(type):
    """
    This is me trying to be too clever for my own good

    Odds are high that it'll cause some weird hard-to-debug issues at some point, but
    isn't it neeeeeat? -_-
    """

    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        GD_OBJECT_REGISTRY[name] = x
        return x


GDObjectType = TypeVar("GDObjectType", bound="GDObject")


class GDObject(Outputable, metaclass=GDObjectMeta):
    """
    Base class for all GD Object types

    Can be used to represent any GD type. For example::

        GDObject('Vector2', 1, 2) == Vector2(1, 2)
    """

    def __init__(self, name, *args) -> None:
        self.name = name
        self.args: List[Any] = list(args)

    def __contains__(self, idx: int) -> bool:
        return idx in self.args

    def __getitem__(self, idx: int) -> float:
        return self.args[idx]

    def __setitem__(self, idx: int, value: float) -> None:
        self.args[idx] = value

    def __delitem__(self, idx: int) -> None:
        del self.args[idx]

    @classmethod
    def from_parser(cls: Type[GDObjectType], parse_result) -> GDObjectType:
        name = parse_result[0]
        factory = GD_OBJECT_REGISTRY.get(name, partial(GDObject, name))
        return factory(*parse_result[1:])

    __packed_array_re = re.compile(r"^(Packed|Pool)(?P<InnerType>[A-Z]\w+)Array$")

    def _output_to_string(self, output_format: OutputFormat) -> str:
        name = self.name

        match = self.__packed_array_re.match(name)
        if match:
            name = output_format.packed_array_format % match.group("InnerType")

        return name + output_format.surround_parentheses(
            ", ".join([stringify_object(v, output_format) for v in self.args])
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, GDObject):
            return False
        return self.name == other.name and self.args == other.args

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset((self.name, *self.args)))


class Vector2(GDObject):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("Vector2", x, y)

    @property
    def x(self) -> float:
        """Getter for x"""
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """Setter for x"""
        self.args[0] = x

    @property
    def y(self) -> float:
        """Getter for y"""
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """Setter for y"""
        self.args[1] = y


class Vector3(GDObject):
    def __init__(self, x: float, y: float, z: float) -> None:
        super().__init__("Vector3", x, y, z)

    @property
    def x(self) -> float:
        """Getter for x"""
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """Setter for x"""
        self.args[0] = x

    @property
    def y(self) -> float:
        """Getter for y"""
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """Setter for y"""
        self.args[1] = y

    @property
    def z(self) -> float:
        """Getter for z"""
        return self.args[2]

    @z.setter
    def z(self, z: float) -> None:
        """Setter for z"""
        self.args[2] = z


class Vector4(GDObject):
    def __init__(self, x: float, y: float, z: float, w: float) -> None:
        super().__init__("Vector4", x, y, z, w)

    @property
    def x(self) -> float:
        """Getter for x"""
        return self.args[0]

    @x.setter
    def x(self, x: float) -> None:
        """Setter for x"""
        self.args[0] = x

    @property
    def y(self) -> float:
        """Getter for y"""
        return self.args[1]

    @y.setter
    def y(self, y: float) -> None:
        """Setter for y"""
        self.args[1] = y

    @property
    def z(self) -> float:
        """Getter for z"""
        return self.args[2]

    @z.setter
    def z(self, z: float) -> None:
        """Setter for z"""
        self.args[2] = z

    @property
    def w(self) -> float:
        """Getter for w"""
        return self.args[3]

    @w.setter
    def w(self, w: float) -> None:
        """Setter for w"""
        self.args[3] = w


class Color(GDObject):
    def __init__(self, r: float, g: float, b: float, a: float) -> None:
        assert 0 <= r <= 1
        assert 0 <= g <= 1
        assert 0 <= b <= 1
        assert 0 <= a <= 1
        super().__init__("Color", r, g, b, a)

    @property
    def r(self) -> float:
        """Getter for r"""
        return self.args[0]

    @r.setter
    def r(self, r: float) -> None:
        """Setter for r"""
        self.args[0] = r

    @property
    def g(self) -> float:
        """Getter for g"""
        return self.args[1]

    @g.setter
    def g(self, g: float) -> None:
        """Setter for g"""
        self.args[1] = g

    @property
    def b(self) -> float:
        """Getter for b"""
        return self.args[2]

    @b.setter
    def b(self, b: float) -> None:
        """Setter for b"""
        self.args[2] = b

    @property
    def a(self) -> float:
        """Getter for a"""
        return self.args[3]

    @a.setter
    def a(self, a: float) -> None:
        """Setter for a"""
        self.args[3] = a


class PackedVector4Array(GDObject):
    def __init__(self, *args) -> None:
        super().__init__("PackedVector4Array", *args)

    @classmethod
    def FromList(cls, list_: List[Vector4]) -> "PackedVector4Array":
        return cls(*sum([[v.x, v.y, v.z, v.w] for v in list_], []))

    def get_vector4(self, idx: int) -> Vector4:
        return Vector4(
            self.args[idx * 4 + 0],
            self.args[idx * 4 + 1],
            self.args[idx * 4 + 2],
            self.args[idx * 4 + 3],
        )

    def set_vector4(self, idx: int, value: Vector4) -> None:
        self.args[idx * 4 + 0] = value.x
        self.args[idx * 4 + 1] = value.y
        self.args[idx * 4 + 2] = value.z
        self.args[idx * 4 + 3] = value.w

    def remove_vector4_at(self, idx: int) -> None:
        del self.args[idx * 4]
        del self.args[idx * 4]
        del self.args[idx * 4]
        del self.args[idx * 4]

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if output_format.packed_vector4_array_support:
            return super()._output_to_string(output_format)
        else:
            return TypedArray(
                "Vector4",
                [self.get_vector4(i) for i in range(floor(len(self.args) / 4))],
            ).output_to_string(output_format)


class PackedByteArray(GDObject):
    def __init__(self, *args) -> None:
        super().__init__("PackedByteArray", *args)

    @classmethod
    def FromBytes(cls, bytes_: bytes) -> "PackedByteArray":
        return cls(*list(bytes_))

    def _stored_as_base64(self) -> bool:
        return len(self.args) == 1 and isinstance(self.args[0], str)

    @property
    def bytes_(self) -> bytes:
        if self._stored_as_base64():
            return base64.b64decode(self.args[0])
        return bytes(self.args)

    @bytes_.setter
    def bytes_(self, bytes_: bytes) -> None:
        self.args = list(bytes_)

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if output_format.packed_byte_array_base64_support:
            if not self._stored_as_base64():
                self.args = [base64.b64encode(self.bytes_).decode("utf-8")]
        elif self._stored_as_base64():
            self.bytes_ = self.bytes_
        return super()._output_to_string(output_format)


class NodePath(GDObject):
    def __init__(self, path: str) -> None:
        super().__init__("NodePath", path)

    @property
    def path(self) -> str:
        """Getter for path"""
        return self.args[0]

    @path.setter
    def path(self, path: str) -> None:
        """Setter for path"""
        self.args[0] = path

    def _output_to_string(self, output_format: OutputFormat) -> str:
        original_punctuation_spaces = output_format.punctuation_spaces
        output_format.punctuation_spaces = False
        ret = super()._output_to_string(output_format)
        output_format.punctuation_spaces = original_punctuation_spaces
        return ret


class ResourceReference(GDObject):
    def __init__(self, name: str, resource: Union[int, str, Identifiable]):
        self.resource = resource
        if isinstance(resource, Identifiable):
            super().__init__(name)
        else:
            super().__init__(name, resource)

    @property
    def id(self) -> Optional[Union[int, str]]:
        """Getter for id"""
        if isinstance(self.resource, Identifiable):
            return self.resource.get_id()
        else:
            return self.resource

    @id.setter
    def id(self, id: Union[int, str]) -> None:
        """Setter for id"""
        self.resource = id
        self.args = [id]

    @classmethod
    def get_id_key(cls, index: Optional[int] = None) -> str:
        return "Resource"

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if isinstance(self.resource, Identifiable):
            id = self.resource.get_id()
            if id is not None:
                self.id = id
        return super()._output_to_string(output_format)


class ExtResource(ResourceReference):
    def __init__(self, resource: Union[int, str, Identifiable]) -> None:
        super().__init__("ExtResource", resource)

    @classmethod
    def get_id_key(cls, index: Optional[int] = None) -> str:
        return str(index)


class SubResource(ResourceReference):
    def __init__(self, resource: Union[int, str, Identifiable]) -> None:
        super().__init__("SubResource", resource)


class GDIterable:
    def _iter_objects(self) -> Iterable[Any]:
        return iter([])


class TypedArray(GDIterable, Outputable):
    def __init__(self, type, list_) -> None:
        self.name = "Array"
        self.type = type
        self.list_: list = list_

    @classmethod
    def WithCustomName(cls: Type["TypedArray"], name, type, list_) -> "TypedArray":
        custom_array = TypedArray(type, list_)
        custom_array.name = name
        return custom_array

    @classmethod
    def from_parser(cls: Type["TypedArray"], parse_result) -> "TypedArray":
        return TypedArray.WithCustomName(*parse_result)

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if output_format.typed_array_support:
            return (
                self.name
                + output_format.surround_brackets(
                    self.type.output_to_string(output_format)
                    if isinstance(self.type, Outputable)
                    else self.type
                )
                + output_format.surround_parentheses(
                    stringify_object(self.list_, output_format)
                )
            )
        else:
            return stringify_object(self.list_, output_format)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, TypedArray):
            return False
        return (
            self.name == other.name
            and self.type == other.type
            and self.list_ == other.list_
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset((self.name, self.type, self.list_)))

    def _iter_objects(self) -> Iterable[Any]:
        yield self.type
        yield from self.list_


class TypedDictionary(GDIterable, Outputable):
    def __init__(self, key_type, value_type, dict_) -> None:
        self.name = "Dictionary"
        self.key_type = key_type
        self.value_type = value_type
        self.dict_: dict = dict_

    @classmethod
    def WithCustomName(
        cls: Type["TypedDictionary"], name, key_type, value_type, dict_
    ) -> "TypedDictionary":
        custom_dict = TypedDictionary(key_type, value_type, dict_)
        custom_dict.name = name
        return custom_dict

    @classmethod
    def from_parser(cls: Type["TypedDictionary"], parse_result) -> "TypedDictionary":
        return TypedDictionary.WithCustomName(*parse_result)

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if output_format.typed_dictionary_support:
            return (
                self.name
                + output_format.surround_brackets(
                    "%s, %s"
                    % (
                        (
                            self.key_type.output_to_string(output_format)
                            if isinstance(self.key_type, Outputable)
                            else self.key_type
                        ),
                        (
                            self.value_type.output_to_string(output_format)
                            if isinstance(self.value_type, Outputable)
                            else self.value_type
                        ),
                    )
                )
                + output_format.surround_parentheses(
                    stringify_object(self.dict_, output_format)
                )
            )
        else:
            return stringify_object(self.dict_, output_format)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, TypedDictionary):
            return False
        return (
            self.name == other.name
            and self.key_type == other.key_type
            and self.value_type == other.value_type
            and self.dict_ == other.dict_
        )

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset((self.name, self.key_type, self.value_type, self.dict_)))

    def _iter_objects(self) -> Iterable[Any]:
        yield self.key_type
        yield self.value_type
        yield from self.dict_.keys()
        yield from self.dict_.values()


class StringName(Outputable):
    def __init__(self, str) -> None:
        self.str = str

    @classmethod
    def from_parser(cls: Type["StringName"], parse_result) -> "StringName":
        return StringName(parse_result[0])

    def _output_to_string(self, output_format: OutputFormat) -> str:
        if output_format.string_name_support:
            return "&" + json.dumps(self.str, ensure_ascii=False).replace("'", "\\'")
        else:
            return stringify_object(self.str, output_format)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, StringName):
            return False
        return self.str == other.str

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.str)
