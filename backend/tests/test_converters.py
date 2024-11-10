import unittest
from lingustruct.converters import lingu_struct_to_human_readable, human_readable_to_lingu_struct

class TestConverters(unittest.TestCase):
    def setUp(self):
        self.lingu_struct_data = {
            "t_v": "1.0",
            "p_n": "PN1",
            "p_v": "1.0",
            "desc": "D1",
            "scale": "m"
        }
        self.key_mapping = {
            "t_v": "Template Version",
            "p_n": "Project Name",
            "p_v": "Project Version",
            "desc": "Description",
            "scale": "Scale"
        }
        self.key_mapping_reverse = {v: k for k, v in self.key_mapping.items()}

    def test_lingu_struct_to_human_readable(self):
        expected = {
            "Template Version": "1.0",
            "Project Name": "PN1",
            "Project Version": "1.0",
            "Description": "D1",
            "Scale": "m"
        }
        result = lingu_struct_to_human_readable(self.lingu_struct_data, self.key_mapping)
        self.assertEqual(result, expected)

    def test_human_readable_to_lingu_struct(self):
        human_readable = {
            "Template Version": "1.0",
            "Project Name": "PN1",
            "Project Version": "1.0",
            "Description": "D1",
            "Scale": "m"
        }
        expected = self.lingu_struct_data
        result = human_readable_to_lingu_struct(human_readable, self.key_mapping_reverse)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
