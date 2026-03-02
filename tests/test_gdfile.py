import tempfile
import unittest

from godot_parser.files import (
    GDFile,
    GDObject,
    GDPackedScene,
    GDResource,
    GDResourceSection,
)
from godot_parser.id_generator import SequentialHexGenerator
from godot_parser.objects import StringName, TypedArray, TypedDictionary
from godot_parser.output import OutputFormat
from godot_parser.tree import Node


class TestGDFile(unittest.TestCase):
    """Tests for GDFile"""

    def setUp(self):
        self.test_output_format = OutputFormat()
        self.test_output_format._id_generator = SequentialHexGenerator()

    def test_basic_scene(self):
        """Run the parsing test cases"""
        self.assertEqual(str(GDPackedScene()), "[gd_scene format=3]\n")

    def test_all_data_types(self):
        """Run the parsing test cases"""
        res = GDResource(
            list=[1, 2.0, "string"],
            map={"key": ["nested", GDObject("Vector2", 1, 1)]},
            empty=None,
            escaped='foo("bar")',
        )
        self.assertEqual(
            str(res),
            """[gd_resource format=3]

[resource]
list = [1, 2.0, "string"]
map = {
"key": ["nested", Vector2(1, 1)]
}
empty = null
escaped = "foo(\\"bar\\")"
""",
        )

    def test_ext_resource(self):
        """Test serializing a scene with an ext_resource"""
        scene = GDPackedScene()
        scene.add_ext_resource("res://Other.tscn", "PackedScene")
        self.assertEqual(
            scene.output_to_string(self.test_output_format),
            """[gd_scene format=3]

[ext_resource path="res://Other.tscn" type="PackedScene" id="1_1"]
""",
        )

    def test_sub_resource(self):
        """Test serializing a scene with an sub_resource"""
        scene = GDPackedScene()
        scene.add_sub_resource("Animation")
        self.assertEqual(
            scene.output_to_string(self.test_output_format),
            """[gd_scene format=3]

[sub_resource type="Animation" id="Resource_1"]
""",
        )

    def test_node(self):
        """Test serializing a scene with a node"""
        scene = GDPackedScene()
        scene.add_node("RootNode", type="Node2D")
        scene.add_node("Child", type="Area2D", parent=".")
        self.assertEqual(
            str(scene),
            """[gd_scene format=3]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Area2D" parent="."]
""",
        )

    def test_tree_create(self):
        """Test creating a scene with the tree API"""
        scene = GDPackedScene()
        with scene.use_tree() as tree:
            tree.root = Node("RootNode", type="Node2D")
            tree.root.add_child(
                Node("Child", type="Area2D", properties={"visible": False})
            )
        self.assertEqual(
            str(scene),
            """[gd_scene format=3]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Area2D" parent="."]
visible = false
""",
        )

    def test_tree_deep_create(self):
        """Test creating a scene with nested children using the tree API"""
        scene = GDPackedScene()
        with scene.use_tree() as tree:
            tree.root = Node("RootNode", type="Node2D")
            child = Node("Child", type="Node")
            tree.root.add_child(child)
            child.add_child(Node("ChildChild", type="Node"))
            child.add_child(Node("ChildChild2", type="Node"))
        self.assertEqual(
            str(scene),
            """[gd_scene format=3]

[node name="RootNode" type="Node2D"]

[node name="Child" type="Node" parent="."]

[node name="ChildChild" type="Node" parent="Child"]

[node name="ChildChild2" type="Node" parent="Child"]
""",
        )

    def test_remove_section(self):
        """Test GDScene.remove_section"""
        scene = GDFile()
        res = scene.add_ext_resource("res://Other.tscn", "PackedScene")
        result = scene.remove_section(GDResourceSection())
        self.assertFalse(result)
        self.assertEqual(len(scene.get_sections()), 1)
        result = scene.remove_section(res)
        self.assertTrue(result)
        self.assertEqual(len(scene.get_sections()), 0)

    def test_section_ordering(self):
        """Sections maintain an ordering"""
        scene = GDPackedScene()
        node = scene.add_node("RootNode")
        scene.add_ext_resource("res://Other.tscn", "PackedScene")
        res = scene.find_section("ext_resource")
        self.assertEqual(scene.get_sections()[1:], [res, node])

    def test_add_ext_node(self):
        """Test GDScene.add_ext_node"""
        scene = GDPackedScene()
        res = scene.add_ext_resource("res://Other.tscn", "PackedScene")
        scene.generate_resource_ids()
        node = scene.add_ext_node("Root", res.id)
        self.assertEqual(node.name, "Root")
        self.assertEqual(node.instance, res.id)
        self.assertTrue(scene.is_inherited)

    def test_write(self):
        """Test writing scene out to a file"""
        scene = GDPackedScene()
        outfile = tempfile.mkstemp()[1]
        scene.write(outfile)
        with open(outfile, "r", encoding="utf-8") as ifile:
            gen_scene = GDPackedScene.parse(ifile.read())
        self.assertEqual(scene, gen_scene)

    def test_get_node_none(self):
        """get_node() works with no nodes"""
        scene = GDPackedScene()
        n = scene.get_node()
        self.assertIsNone(n)

    def test_addremove_ext_res(self):
        """Test adding and removing an ext_resource"""
        scene = GDPackedScene()
        res = scene.add_ext_resource("res://Res.tscn", "PackedScene")
        res2 = scene.add_ext_resource("res://Sprite.png", "Texture")
        scene.generate_resource_ids(self.test_output_format)
        self.assertEqual(res.id, "1_1")
        self.assertEqual(res2.id, "2_2")
        node = scene.add_node("Sprite", "Sprite")
        node["texture"] = res2.reference
        node["textures"] = [res2.reference]
        node["texture_map"] = {"tex": res2.reference}
        node["texture_pool"] = GDObject("ResourcePool", res2.reference)

        s = scene.find_section(path="res://Res.tscn")
        scene.remove_section(s)

        s = scene.find_section("ext_resource")
        self.assertEqual(s.id, "2_2")
        self.assertEqual(node["texture"], s.reference)
        self.assertEqual(node["textures"][0], s.reference)
        self.assertEqual(node["texture_map"]["tex"], s.reference)
        self.assertEqual(node["texture_pool"].args[0], s.reference)

    def test_remove_unused_resource(self):
        """Can remove unused resources"""
        scene = GDPackedScene()
        res = scene.add_ext_resource("res://Res.tscn", "PackedScene")
        scene.remove_unused_resources()
        resources = scene.get_sections("ext_resource")
        self.assertEqual(len(resources), 0)

    def test_addremove_sub_res(self):
        """Test adding and removing a sub_resource"""
        scene = GDResource()
        res = scene.add_sub_resource("CircleShape2D")
        res2 = scene.add_sub_resource("AnimationNodeAnimation")
        scene.generate_resource_ids(self.test_output_format)
        self.assertEqual(res.id, "Resource_1")
        self.assertEqual(res2.id, "Resource_2")
        resource = GDResourceSection(shape=res2.reference)
        scene.add_section(resource)

        s = scene.find_sub_resource(type="CircleShape2D")
        scene.remove_section(s)

        s = scene.find_section("sub_resource")
        self.assertEqual(s.id, "Resource_2")
        self.assertEqual(resource["shape"], s.reference)

    def test_remove_unused_nested(self):
        res = GDResource("CustomResource")

        res1 = res.add_sub_resource("CustomResource")
        res["child_resource"] = res1.reference

        res2 = res.add_sub_resource("CustomResource")
        res1["child_resource"] = res2.reference

        res3 = res.add_sub_resource("CustomResource")
        res2["child_resource"] = res3.reference

        res.generate_resource_ids(self.test_output_format)

        self.assertEqual(len(res._sections), 5)
        self.assertIn(res1, res._sections)
        self.assertIn(res2, res._sections)
        self.assertIn(res3, res._sections)

        del res1["child_resource"]
        res.remove_unused_resources()

        self.assertEqual(len(res._sections), 3)
        self.assertIn(res1, res._sections)
        self.assertNotIn(res2, res._sections)
        self.assertNotIn(res3, res._sections)

    def test_remove_unused_typed(self):
        """Won't remove used types"""
        resource = GDResource()

        script1 = resource.add_ext_resource("res://custom_resource.gd", "Script")
        sub_res1 = resource.add_sub_resource("Resource")

        script2 = resource.add_ext_resource("res://custom_resource_2.gd", "Script")
        sub_res2 = resource.add_sub_resource("Resource")

        resource.add_ext_resource("res://custom_resource_3.gd", "Script")

        resource["typedArray"] = TypedArray(script1.reference, [sub_res1.reference])
        resource["typedDict"] = TypedDictionary(
            script2.reference, "String", {sub_res2.reference: "Cool"}
        )

        resource.generate_resource_ids()

        self.assertEqual(len(resource.get_sub_resources()), 2)
        self.assertEqual(len(resource.get_ext_resources()), 3)

        resource.remove_unused_resources()

        self.assertEqual(len(resource.get_sub_resources()), 2)
        self.assertEqual(len(resource.get_ext_resources()), 2)

    def test_find_constraints(self):
        """Test for the find_section constraints"""
        scene = GDPackedScene()
        res1 = scene.add_sub_resource("CircleShape2D", radius=1)
        res2 = scene.add_sub_resource("CircleShape2D", radius=2)
        scene.generate_resource_ids()

        found = list(scene.find_all("sub_resource"))
        self.assertCountEqual(found, [res1, res2])

        found = list(scene.find_all("sub_resource", id=res1.id))
        self.assertEqual(found, [res1])

        found = list(scene.find_all("sub_resource", {"radius": 2}))
        self.assertEqual(found, [res2])

    def test_find_node(self):
        """Test GDScene.find_node"""
        scene = GDPackedScene()
        n1 = scene.add_node("Root", "Node")
        n2 = scene.add_node("Child", "Node", parent=".")
        node = scene.find_node(name="Root")
        self.assertEqual(node, n1)
        node = scene.find_node(parent=".")
        self.assertEqual(node, n2)

    def test_file_equality(self):
        """Tests for GDFile == GDFile"""
        s1 = GDPackedScene(GDResourceSection())
        s2 = GDPackedScene(GDResourceSection())
        self.assertEqual(s1, s2)
        resource = s1.find_section("resource")
        resource["key"] = "value"
        self.assertNotEqual(s1, s2)

    def test_renumber_ids(self):
        output_format = OutputFormat(resource_ids_as_strings=False)

        res = GDResource()
        res1 = res.add_sub_resource("CircleShape2D")
        res2 = res.add_sub_resource("AnimationNodeAnimation")
        res.generate_resource_ids(output_format)

        self.assertEqual(res1.id, 1)
        self.assertEqual(res2.id, 2)

        res.remove_section(res1)
        res.renumber_resource_ids()

        self.assertEqual(res2.id, 1)

    def test_string_special_characters(self):
        input = "".join(
            [
                " ",
                '"',
                "a",
                " ",
                "'",
                "'",
                "\\",
                "\n",
                "\t",
                "\n",
                "\\",
                "n",
                "\n",
            ]
        )

        res = GDResource()
        res["str_value"] = input
        res["str_name"] = StringName(input)

        print(str(res))

        self.assertEqual(
            str(res),
            """[gd_resource format=3]

[resource]
str_value = "%s"
str_name = &"%s"
"""
            % (
                "".join(
                    [
                        " ",
                        "\\",
                        '"',
                        "a",
                        " ",
                        "'",
                        "'",
                        "\\",
                        "\\",
                        "\n",
                        "\t",
                        "\n",
                        "\\",
                        "\\",
                        "n",
                        "\n",
                    ]
                ),
                "".join(
                    [
                        " ",
                        "\\",
                        '"',
                        "a",
                        " ",
                        "\\",
                        "'",
                        "\\",
                        "'",
                        "\\",
                        "\\",
                        "\\",
                        "n",
                        "\\",
                        "t",
                        "\\",
                        "n",
                        "\\",
                        "\\",
                        "n",
                        "\\",
                        "n",
                    ]
                ),
            ),
        )
