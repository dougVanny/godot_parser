import base64
import os
import unittest

import tests
from godot_parser import GDPackedScene, NodePath, StringName, TypedArray, parse
from godot_parser.id_generator import SequentialHexGenerator
from godot_parser.objects import (
    PackedByteArray,
    PackedVector4Array,
    TypedDictionary,
    Vector4,
)
from godot_parser.output import VersionOutputFormat


class TestVersionOutput(unittest.TestCase):
    def setUp(self):
        self.scene = GDPackedScene()
        root = self.scene.add_node("Root", "Node3D")
        child = self.scene.add_node("Child", "Node", ".")

        ext1 = self.scene.add_ext_resource("res://external.tres", "CustomResource1")
        root["resource1"] = ext1.reference

        extScript = self.scene.add_ext_resource("res://custom_resource.gd", "Script")
        extScript2 = self.scene.add_ext_resource("res://custom_resource_2.gd", "Script")

        sub1 = self.scene.add_sub_resource("Resource")
        sub1["script"] = extScript.reference

        sub2 = self.scene.add_sub_resource("Resource")
        sub2["script"] = extScript.reference

        sub3 = self.scene.add_sub_resource("Resource")
        sub3["script"] = extScript2.reference

        root["resourceArray"] = TypedArray(
            extScript.reference, [sub1.reference, sub2.reference]
        )
        root["typedDict"] = TypedDictionary(
            "StringName",
            extScript2.reference,
            {StringName("Two"): sub3.reference},
        )

        byte_array = bytes([10, 20, 15])
        self.byte_array_base64 = base64.b64encode(byte_array).decode("utf-8")

        child["str"] = "'hello\\me'\n\"HI\""
        child["string name"] = StringName("StringName")
        child["packedByte"] = PackedByteArray.FromBytes(byte_array)
        child["packedVector4"] = PackedVector4Array.FromList([Vector4(1, 3, 5, 7)])
        child["nodepath"] = NodePath(".")

    def test_godot_3(self):
        self.assertEqual(
            self.scene.output_to_string(VersionOutputFormat("3.6")),
            """[gd_scene load_steps=7 format=2]

[ext_resource path="res://external.tres" type="CustomResource1" id=1]
[ext_resource path="res://custom_resource.gd" type="Script" id=2]
[ext_resource path="res://custom_resource_2.gd" type="Script" id=3]

[sub_resource type="Resource" id=1]
script = ExtResource( 2 )

[sub_resource type="Resource" id=2]
script = ExtResource( 2 )

[sub_resource type="Resource" id=3]
script = ExtResource( 3 )

[node name="Root" type="Node3D"]
resource1 = ExtResource( 1 )
resourceArray = [ SubResource( 1 ), SubResource( 2 ) ]
typedDict = {
"Two": SubResource( 3 )
}

[node name="Child" type="Node" parent="."]
str = "'hello\\\\me'
\\\"HI\\\""
"string name" = "StringName"
packedByte = PoolByteArray( 10, 20, 15 )
packedVector4 = [ Vector4( 1, 3, 5, 7 ) ]
nodepath = NodePath(".")
""",
        )

    def test_godot_4_0(self):
        output_format = VersionOutputFormat("4.0")
        output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            self.scene.output_to_string(output_format),
            """[gd_scene load_steps=7 format=3]

[ext_resource path="res://external.tres" type="CustomResource1" id="1_1"]
[ext_resource path="res://custom_resource.gd" type="Script" id="2_2"]
[ext_resource path="res://custom_resource_2.gd" type="Script" id="3_3"]

[sub_resource type="Resource" id="Resource_4"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_5"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_6"]
script = ExtResource("3_3")

[node name="Root" type="Node3D"]
resource1 = ExtResource("1_1")
resourceArray = Array[ExtResource("2_2")]([SubResource("Resource_4"), SubResource("Resource_5")])
typedDict = {
&"Two": SubResource("Resource_6")
}

[node name="Child" type="Node" parent="."]
str = "'hello\\\\me'
\\\"HI\\\""
"string name" = &"StringName"
packedByte = PackedByteArray(10, 20, 15)
packedVector4 = Array[Vector4]([Vector4(1, 3, 5, 7)])
nodepath = NodePath(".")
""",
        )

    def test_godot_4_3(self):
        output_format = VersionOutputFormat("4.3")
        output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            self.scene.output_to_string(output_format),
            """[gd_scene load_steps=7 format=4]

[ext_resource path="res://external.tres" type="CustomResource1" id="1_1"]
[ext_resource path="res://custom_resource.gd" type="Script" id="2_2"]
[ext_resource path="res://custom_resource_2.gd" type="Script" id="3_3"]

[sub_resource type="Resource" id="Resource_4"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_5"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_6"]
script = ExtResource("3_3")

[node name="Root" type="Node3D"]
resource1 = ExtResource("1_1")
resourceArray = Array[ExtResource("2_2")]([SubResource("Resource_4"), SubResource("Resource_5")])
typedDict = {
&"Two": SubResource("Resource_6")
}

[node name="Child" type="Node" parent="."]
str = "'hello\\\\me'
\\\"HI\\\""
"string name" = &"StringName"
packedByte = PackedByteArray("%s")
packedVector4 = PackedVector4Array(1, 3, 5, 7)
nodepath = NodePath(".")
""" % self.byte_array_base64,
        )

    def test_godot_4_4(self):
        output_format = VersionOutputFormat("4.4")
        output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            self.scene.output_to_string(output_format),
            """[gd_scene load_steps=7 format=4]

[ext_resource path="res://external.tres" type="CustomResource1" id="1_1"]
[ext_resource path="res://custom_resource.gd" type="Script" id="2_2"]
[ext_resource path="res://custom_resource_2.gd" type="Script" id="3_3"]

[sub_resource type="Resource" id="Resource_4"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_5"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_6"]
script = ExtResource("3_3")

[node name="Root" type="Node3D"]
resource1 = ExtResource("1_1")
resourceArray = Array[ExtResource("2_2")]([SubResource("Resource_4"), SubResource("Resource_5")])
typedDict = Dictionary[StringName, ExtResource("3_3")]({
&"Two": SubResource("Resource_6")
})

[node name="Child" type="Node" parent="."]
str = "'hello\\\\me'
\\\"HI\\\""
"string name" = &"StringName"
packedByte = PackedByteArray("%s")
packedVector4 = PackedVector4Array(1, 3, 5, 7)
nodepath = NodePath(".")
""" % self.byte_array_base64,
        )

    def test_godot_4_6(self):
        output_format = VersionOutputFormat("4.6")
        output_format._id_generator = SequentialHexGenerator()

        self.assertEqual(
            self.scene.output_to_string(output_format),
            """[gd_scene format=4]

[ext_resource path="res://external.tres" type="CustomResource1" id="1_1"]
[ext_resource path="res://custom_resource.gd" type="Script" id="2_2"]
[ext_resource path="res://custom_resource_2.gd" type="Script" id="3_3"]

[sub_resource type="Resource" id="Resource_4"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_5"]
script = ExtResource("2_2")

[sub_resource type="Resource" id="Resource_6"]
script = ExtResource("3_3")

[node name="Root" type="Node3D"]
resource1 = ExtResource("1_1")
resourceArray = Array[ExtResource("2_2")]([SubResource("Resource_4"), SubResource("Resource_5")])
typedDict = Dictionary[StringName, ExtResource("3_3")]({
&"Two": SubResource("Resource_6")
})

[node name="Child" type="Node" parent="."]
str = "'hello\\\\me'
\\\"HI\\\""
"string name" = &"StringName"
packedByte = PackedByteArray("%s")
packedVector4 = PackedVector4Array(1, 3, 5, 7)
nodepath = NodePath(".")
""" % self.byte_array_base64,
        )


class TestRealProject(unittest.TestCase):
    def test_projects(self):
        project_folder = os.path.join(os.path.dirname(tests.__file__), "projects")
        for root, _dirs, files in os.walk(project_folder, topdown=False):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in [".tscn", ".tres"]:
                    continue
                filepath = os.path.join(root, file)
                version, filename = os.path.split(
                    os.path.relpath(filepath, project_folder)
                )

                with self.subTest("%s - %s" % (version, filename)):
                    output_format = VersionOutputFormat(version)

                    # Required as Godot uses format=4 not if the tres contains a PackedVector4Array or
                    # base64 PackedByteArray, but if the originating script contains any such properties
                    #
                    # Since we have no access to the original script, we hack this with the prior knowledge that the
                    # files used for this test contained those types
                    output_format._force_format_4_if_available = True

                    with open(filepath, "r", encoding="utf-8") as input_file:
                        file_content = input_file.read()
                        parsed_file = parse(file_content)
                        self.assertEqual(
                            file_content,
                            parsed_file.output_to_string(output_format),
                        )
                        self.assertEqual(
                            file_content,
                            parsed_file.output_to_string(
                                VersionOutputFormat.guess_version(parsed_file)
                            ),
                        )
