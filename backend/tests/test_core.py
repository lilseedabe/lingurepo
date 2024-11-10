import unittest
import os
from lingustruct.core import LinguStruct

class TestLinguStruct(unittest.TestCase):
    def setUp(self):
        self.lingu = LinguStruct(template_dir=os.path.join(os.path.dirname(__file__), '..', 'lingustruct', 'templates'))
        self.replacements = {
            "PROJECT_ID": "test_project",
            "VERSION": "1.0"
        }

    def test_generate_master_json(self):
        output_path = 'test_master.json'
        self.lingu.generate_master_json(self.replacements, output_path)
        self.assertTrue(os.path.exists(output_path))
        with open(output_path, 'r', encoding='utf-8') as f:
            data = f.read()
            self.assertIn('"project_id": "test_project"', data)
            self.assertIn('"version": "1.0"', data)
        os.remove(output_path)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
