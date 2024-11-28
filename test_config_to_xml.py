import unittest
from config_to_xml import ConfigParser

class TestConfigParser(unittest.TestCase):
    def test_simple_constant(self):
        input_text = "const server_port = 8080;"
        parser = ConfigParser(input_text)
        parser.parse()
        self.assertEqual(parser.constants, {"server_port": 8080})

    def test_list_constant(self):
        input_text = "const server_ips = list(19216801, 19216802);"
        parser = ConfigParser(input_text)
        parser.parse()
        self.assertEqual(parser.constants, {"server_ips": [19216801, 19216802]})

    def test_nested_list(self):
        input_text = "const data = list(1, list(2, 3));"
        parser = ConfigParser(input_text)
        parser.parse()
        self.assertEqual(parser.constants, {"data": [1, [2, 3]]})

    def test_string_list(self):
        input_text = "const player_names = list(Alice, Bob, Charlie);"
        parser = ConfigParser(input_text)
        parser.parse()
        self.assertEqual(parser.constants, {"player_names": ["Alice", "Bob", "Charlie"]})

    def test_undefined_constant(self):
        input_text = "const combined = list($undefined$);"
        parser = ConfigParser(input_text)
        with self.assertRaises(ValueError):  # Expecting a ValueError due to undefined constant
            parser.parse()


if __name__ == "__main__":
    unittest.main()
