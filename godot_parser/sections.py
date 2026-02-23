import re
from collections import OrderedDict
from typing import Any, List, Optional, Type, TypeVar, Union

from .objects import ExtResource, SubResource
from .output import Outputable, OutputFormat
from .util import Identifiable, stringify_object

__all__ = [
    "GDSectionHeader",
    "GDSection",
    "GDNodeSection",
    "GDBaseResourceSection",
    "GDExtResourceSection",
    "GDSubResourceSection",
    "GDResourceSection",
    "GDFileHeader",
]


GD_SECTION_REGISTRY = {}


class GDSectionHeader(Outputable):
    """
    Represents the header for a section

    example::

        [node name="Sprite" type="Sprite" index="3"]
    """

    def __init__(self, _name: str, **kwargs) -> None:
        self.name = _name
        self.attributes = OrderedDict()
        for k, v in kwargs.items():
            self.attributes[k] = v

    def __contains__(self, k: str) -> bool:
        return k in self.attributes

    def __getitem__(self, k: str) -> Any:
        return self.attributes[k]

    def __setitem__(self, k: str, v: Any) -> None:
        self.attributes[k] = v

    def __delitem__(self, k: str):
        del self.attributes[k]

    def get(self, k: str, default: Any = None) -> Any:
        return self.attributes.get(k, default)

    @classmethod
    def from_parser(cls: Type["GDSectionHeader"], parse_result) -> "GDSectionHeader":
        factory = cls

        if parse_result[0] in ["gd_resource", "gd_scene"]:
            factory = GDFileHeader

        header = factory(parse_result[0])
        for attribute in parse_result[1:]:
            header.attributes[attribute[0]] = attribute[1]
        return header

    def _get_key_priority(self, key: str) -> int:
        return 0

    def _output_to_string(self, output_format: OutputFormat) -> str:
        attribute_str = ""
        if self.attributes:
            keys = sorted(
                self.attributes.keys(), key=self._get_key_priority, reverse=True
            )

            attribute_str = " " + " ".join(
                [
                    "%s=%s" % (k, stringify_object(self.attributes[k], output_format))
                    for k in keys
                ]
            )
        return "[" + self.name + attribute_str + "]"

    def __repr__(self) -> str:
        return "GDSectionHeader(%s)" % self.__str__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GDSectionHeader):
            return False
        return self.name == other.name and self.attributes == other.attributes

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class GDFileHeader(GDSectionHeader):
    def _get_key_priority(self, key: str) -> int:
        if key == "uid":
            return -10
        return super()._get_key_priority(key)


class GDSectionMeta(type):
    """Still trying to be too clever"""

    def __new__(cls, name, bases, dct):
        x = super().__new__(cls, name, bases, dct)
        section_name_camel = name[2:-7]
        section_name = re.sub(r"(?<!^)(?=[A-Z])", "_", section_name_camel).lower()
        GD_SECTION_REGISTRY[section_name] = x
        return x


GDSectionType = TypeVar("GDSectionType", bound="GDSection")


class GDSection(Outputable, metaclass=GDSectionMeta):
    """
    Represents a full section of a GD file

    example::

        [node name="Sprite" type="Sprite"]
        texture = ExtResource( 1 )

    """

    def __init__(self, header: GDSectionHeader, **kwargs) -> None:
        self.header = header
        self.properties = OrderedDict()
        for k, v in kwargs.items():
            self.properties[k] = v

    def __contains__(self, k: str) -> bool:
        return k in self.properties

    def __getitem__(self, k: str) -> Any:
        return self.properties[k]

    def __setitem__(self, k: str, v: Any) -> None:
        self.properties[k] = v

    def __delitem__(self, k: str) -> None:
        del self.properties[k]

    def get(self, k: str, default: Any = None) -> Any:
        return self.properties.get(k, default)

    @classmethod
    def from_parser(cls: Type[GDSectionType], parse_result) -> GDSectionType:
        header = parse_result[0]
        factory = GD_SECTION_REGISTRY.get(header.name, cls)
        section = factory.__new__(factory)
        section.header = header
        section.properties = OrderedDict()
        for k, v in parse_result[1:]:
            section[k] = v
        return section

    def _output_to_string(self, output_format: OutputFormat) -> str:
        ret = self.header.output_to_string(output_format)
        if self.properties:
            ret += "\n" + "\n".join(
                [
                    "%s = %s"
                    % (
                        '"' + k + '"' if " " in k else k,
                        stringify_object(v, output_format),
                    )
                    for k, v in self.properties.items()
                ]
            )
        return ret

    def __repr__(self) -> str:
        return "%s(%s)" % (type(self).__name__, self.__str__())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GDSection):
            return False
        return self.header == other.header and self.properties == other.properties

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class GDBaseResourceSection(GDSection, Identifiable):
    @property
    def type(self) -> str:
        return self.header["type"]

    @type.setter
    def type(self, type: str) -> None:
        self.header["type"] = type

    @property
    def id(self) -> Optional[Union[int, str]]:
        if "id" in self.header:
            return self.header["id"]
        return None

    @id.setter
    def id(self, id: Union[int, str]) -> None:
        self.header["id"] = id

    def get_id(self) -> Optional[Union[int, str]]:
        return self.id


class GDExtResourceSection(GDBaseResourceSection):
    """Section representing an [ext_resource]"""

    def __init__(self, path: str, type_: str, id_: Optional[Union[int, str]] = None):
        super().__init__(GDSectionHeader("ext_resource", path=path, type=type_, id=id_))

    @property
    def path(self) -> str:
        return self.header["path"]

    @path.setter
    def path(self, path: str) -> None:
        self.header["path"] = path

    @property
    def reference(self) -> ExtResource:
        return ExtResource(self)


class GDSubResourceSection(GDBaseResourceSection):
    """Section representing a [sub_resource]"""

    def __init__(self, type_: str, id_: Optional[Union[int, str]] = None, **kwargs):
        super().__init__(GDSectionHeader("sub_resource", type=type_, id=id_), **kwargs)

    @property
    def reference(self) -> SubResource:
        return SubResource(self)


class GDNodeSection(GDSection):
    """Section representing a [node]"""

    def __init__(
        self,
        name: str,
        type: Optional[str] = None,
        parent: Optional[str] = None,
        instance: Optional[int] = None,
        index: Optional[int] = None,
        groups: Optional[List[str]] = None,
        # TODO: instance_placeholder, owner are referenced in the docs, but I
        # haven't seen them come up yet in my project
    ):
        kwargs = {
            "name": name,
            "type": type,
            "parent": parent,
            "instance": ExtResource(instance) if instance is not None else None,
            "index": str(index) if index is not None else None,
            "groups": groups,
        }
        super().__init__(
            GDSectionHeader(
                "node", **{k: v for k, v in kwargs.items() if v is not None}
            )
        )

    @classmethod
    def ext_node(
        cls,
        name: str,
        instance: int,
        parent: Optional[str] = None,
        index: Optional[int] = None,
    ):
        return cls(name, parent=parent, instance=instance, index=index)

    @property
    def name(self) -> str:
        return self.header["name"]

    @name.setter
    def name(self, name: str) -> None:
        self.header["name"] = name

    @property
    def type(self) -> Optional[str]:
        return self.header.get("type")

    @type.setter
    def type(self, type: Optional[str]) -> None:
        if type is None:
            if "type" in self.header:
                del self.header["type"]
        else:
            self.header["type"] = type
            self.instance = None

    @property
    def parent(self) -> Optional[str]:
        return self.header.get("parent")

    @parent.setter
    def parent(self, parent: Optional[str]) -> None:
        if parent is None:
            if "parent" in self.header:
                del self.header["parent"]
        else:
            self.header["parent"] = parent

    @property
    def instance(self) -> Optional[int]:
        resource = self.header.get("instance")
        if resource is not None:
            return resource.id
        return None

    @instance.setter
    def instance(self, instance: Optional[int]) -> None:
        if instance is None:
            if "instance" in self.header:
                del self.header["instance"]
        else:
            self.header["instance"] = ExtResource(instance)
            self.type = None

    @property
    def index(self) -> Optional[int]:
        idx = self.header.get("index")
        if idx is not None:
            return int(idx)
        return None

    @index.setter
    def index(self, index: Optional[int]) -> None:
        if index is None:
            if "index" in self.header:
                del self.header["index"]
        else:
            self.header["index"] = str(index)

    @property
    def groups(self) -> Optional[List[str]]:
        return self.header.get("groups")

    @groups.setter
    def groups(self, groups: Optional[List[str]]) -> None:
        if groups is None:
            if "groups" in self.header:
                del self.header["groups"]
        else:
            self.header["groups"] = groups


class GDResourceSection(GDSection):
    """Represents a [resource] section"""

    def __init__(self, **kwargs):
        super().__init__(GDSectionHeader("resource"), **kwargs)
