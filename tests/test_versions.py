import unittest

from godot_parser import GDResource, Vector3
from godot_parser.output import VersionOutputFormat, OutputFormat


class TestOutputFormat(unittest.TestCase):
    def test_version_output_format(self):
        version_output_format = VersionOutputFormat("3.6")
        self.assertTrue(version_output_format.punctuation_spaces)
        self.assertFalse(version_output_format.resource_ids_as_strings)
        self.assertFalse(version_output_format.explicit_typed_array)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.0")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.1")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertFalse(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.3")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertFalse(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.4")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.5")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.explicit_typed_dictionary)
        self.assertTrue(version_output_format.load_steps)

        version_output_format = VersionOutputFormat("4.6")
        self.assertFalse(version_output_format.punctuation_spaces)
        self.assertTrue(version_output_format.resource_ids_as_strings)
        self.assertTrue(version_output_format.explicit_typed_array)
        self.assertTrue(version_output_format.packed_byte_array_base64_support)
        self.assertTrue(version_output_format.explicit_typed_dictionary)
        self.assertFalse(version_output_format.load_steps)

    def test_punctuation_spaces(self):
        resource = GDResource()
        resource["array"] = [Vector3(1,2,3)]

        self.assertEqual(resource.output_to_string(OutputFormat(punctuation_spaces=False)),
                         """[gd_resource format=3]

[resource]
array = [Vector3(1, 2, 3)]\n""")

        self.assertEqual(resource.output_to_string(OutputFormat(punctuation_spaces=True)),
                         """[gd_resource format=3]

[resource]
array = [ Vector3( 1, 2, 3 ) ]\n""")