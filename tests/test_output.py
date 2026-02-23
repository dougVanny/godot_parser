import base64
import unittest

from godot_parser import (
    GDExtResourceSection,
    GDResource,
    GDSubResourceSection,
    Vector3,
    TypedArray,
    GDObject,
)
from godot_parser.id_generator import SequentialHexGenerator
from godot_parser.objects import (
    PackedVector4Array,
    Vector4,
    TypedDictionary,
    PackedByteArray,
)
from godot_parser.output import OutputFormat, VersionOutputFormat


class TestOutputFormat(unittest.TestCase):
    def test_version_output_format(self):
        version_output_format = VersionOutputFormat("3.6")
        self.assertTrue(version_output_format.punctuation_spaces)
        self.assertFalse(version_output_format.resource_ids_as_strings)
        self.assertFalse(version_output_format.typed_array_support)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.0")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.1")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.3")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.4")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.5")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.typed_dictionary_support)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.6")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.typed_array_support)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.typed_dictionary_support)
        self.assertFalse(version_output_format.load_steps)

    def test_punctuation_spaces(self):
        resource = GDResource()
        resource["array"] = [Vector3(1, 2, 3)]

        self.assertEqual(
            resource.output_to_string(OutputFormat(punctuation_spaces=False)),
            """[gd_resource format=3]

[resource]
array = [Vector3(1, 2, 3)]\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(punctuation_spaces=True)),
            """[gd_resource format=3]

[resource]
array = [ Vector3( 1, 2, 3 ) ]\n""",
        )

    def test_load_steps(self):
        resource = GDResource()
        resource["toggle"] = True

        true_output_format = OutputFormat(load_steps=True)
        true_output_format._id_generator = SequentialHexGenerator()

        false_output_format = OutputFormat(load_steps=False)
        false_output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            resource.output_to_string(false_output_format),
            """[gd_resource format=3]

[resource]
toggle = true\n""",
        )
        self.assertEqual(
            resource.output_to_string(true_output_format),
            """[gd_resource load_steps=1 format=3]

[resource]
toggle = true\n""",
        )

        resource.add_ext_resource("res://a.tres", "CustomResource")

        self.assertEqual(
            resource.output_to_string(false_output_format),
            """[gd_resource format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1_1"]

[resource]
toggle = true\n""",
        )
        self.assertEqual(
            resource.output_to_string(true_output_format),
            """[gd_resource load_steps=2 format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1_1"]

[resource]
toggle = true\n""",
        )

        resource.add_sub_resource("CustomResource")

        self.assertEqual(
            resource.output_to_string(false_output_format),
            """[gd_resource format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1_1"]

[sub_resource type="CustomResource" id="1_2"]

[resource]
toggle = true\n""",
        )
        self.assertEqual(
            resource.output_to_string(true_output_format),
            """[gd_resource load_steps=3 format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1_1"]

[sub_resource type="CustomResource" id="1_2"]

[resource]
toggle = true\n""",
        )

    def test_resource_ids_as_string(self):
        resource = GDResource()
        resource["toggle"] = True
        resource.add_ext_resource("res://a.tres", "CustomResource")
        resource.add_sub_resource("CustomResource")

        false_output_format = OutputFormat(resource_ids_as_strings=False)

        self.assertEqual(
            resource.output_to_string(false_output_format),
            """[gd_resource format=2]

[ext_resource path="res://a.tres" type="CustomResource" id=1]

[sub_resource type="CustomResource" id=1]

[resource]
toggle = true\n""",
        )

        resource = GDResource()
        resource["toggle"] = True
        resource.add_ext_resource("res://a.tres", "CustomResource")
        resource.add_sub_resource("CustomResource")

        true_output_format = OutputFormat(resource_ids_as_strings=True)
        true_output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            resource.output_to_string(true_output_format),
            """[gd_resource format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1_1"]

[sub_resource type="CustomResource" id="1_2"]

[resource]
toggle = true\n""",
        )

    def test_resource_ids_as_string_migration(self):
        resource = GDResource()
        ext = GDExtResourceSection("res://a.tres", "CustomResource", 1)
        sub = GDSubResourceSection("CustomResource", 1)

        resource.add_section(ext)
        resource.add_section(sub)

        resource["ext"] = ext.reference
        resource["sub"] = sub.reference

        self.assertEqual(
            resource.output_to_string(OutputFormat(resource_ids_as_strings=False)),
            """[gd_resource format=2]

[ext_resource path="res://a.tres" type="CustomResource" id=1]

[sub_resource type="CustomResource" id=1]

[resource]
ext = ExtResource(1)
sub = SubResource(1)\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(resource_ids_as_strings=True)),
            """[gd_resource format=3]

[ext_resource path="res://a.tres" type="CustomResource" id="1"]

[sub_resource type="CustomResource" id="1"]

[resource]
ext = ExtResource("1")
sub = SubResource("1")\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(resource_ids_as_strings=False)),
            """[gd_resource format=2]

[ext_resource path="res://a.tres" type="CustomResource" id=1]

[sub_resource type="CustomResource" id=1]

[resource]
ext = ExtResource(1)
sub = SubResource(1)\n""",
        )

    def test_typed_array_support(self):
        resource = GDResource()
        resource["test"] = TypedArray("int", [3, 1, 2])

        self.assertEqual(
            resource.output_to_string(OutputFormat(typed_array_support=True)),
            """[gd_resource format=3]

[resource]
test = Array[int]([3, 1, 2])\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(typed_array_support=False)),
            """[gd_resource format=3]

[resource]
test = [3, 1, 2]\n""",
        )

    def test_typed_dictionary_support(self):
        resource = GDResource()
        resource["test"] = TypedDictionary(
            "int",
            "String",
            {
                1: "One",
                2: "Two",
            },
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(typed_dictionary_support=True)),
            """[gd_resource format=3]

[resource]
test = Dictionary[int, String]({
1: "One",
2: "Two"
})\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(typed_dictionary_support=False)),
            """[gd_resource format=3]

[resource]
test = {
1: "One",
2: "Two"
}\n""",
        )

    def test_packed_vector4_array_support(self):
        resource = GDResource()
        resource["test"] = PackedVector4Array([Vector4(1, 2, 3, 4)])

        self.assertEqual(
            resource.output_to_string(OutputFormat(packed_vector4_array_support=True)),
            """[gd_resource format=4]

[resource]
test = PackedVector4Array(1, 2, 3, 4)\n""",
        )

        self.assertEqual(
            resource.output_to_string(OutputFormat(packed_vector4_array_support=False)),
            """[gd_resource format=3]

[resource]
test = Array[Vector4]([Vector4(1, 2, 3, 4)])\n""",
        )

        self.assertEqual(
            resource.output_to_string(
                OutputFormat(
                    packed_vector4_array_support=False, typed_array_support=False
                )
            ),
            """[gd_resource format=3]

[resource]
test = [Vector4(1, 2, 3, 4)]\n""",
        )

    def test_packed_byte_array_base64_support(self):
        bytes_ = bytes([5, 88, 10])

        resource = GDResource()
        resource["test"] = PackedByteArray(bytes_)

        self.assertEqual(
            resource.output_to_string(
                OutputFormat(packed_byte_array_base64_support=True)
            ),
            """[gd_resource format=4]

[resource]
test = PackedByteArray("%s")\n""" % base64.b64encode(bytes_).decode("utf-8"),
        )

        self.assertEqual(
            resource.output_to_string(
                OutputFormat(packed_byte_array_base64_support=False)
            ),
            """[gd_resource format=3]

[resource]
test = PackedByteArray(5, 88, 10)\n""",
        )

    def test_packed_array_format(self):
        resource = GDResource()
        resource["test1"] = PackedByteArray(bytes(range(4)))
        resource["test2"] = GDObject("PackedVector2Array", *range(4))

        self.assertEqual(
            resource.output_to_string(
                OutputFormat(packed_byte_array_base64_support=False)
            ),
            """[gd_resource format=3]

[resource]
test1 = PackedByteArray(0, 1, 2, 3)
test2 = PackedVector2Array(0, 1, 2, 3)\n""",
        )

        self.assertEqual(
            resource.output_to_string(
                OutputFormat(
                    packed_array_format="Pool%sArray",
                    packed_byte_array_base64_support=False,
                )
            ),
            """[gd_resource format=3]

[resource]
test1 = PoolByteArray(0, 1, 2, 3)
test2 = PoolVector2Array(0, 1, 2, 3)\n""",
        )
