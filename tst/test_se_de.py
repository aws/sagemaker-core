import unittest
from ..src.code_injection.se_de import _pascal_to_snake

class TestConversion(unittest.TestCase):
    def test_pascal_to_snake(self):
        self.assertEqual(_pascal_to_snake('PascalCase'), 'pascal_case')
        self.assertEqual(_pascal_to_snake('AnotherExample'), 'another_example')
        self.assertEqual(_pascal_to_snake('test'), 'test')

if __name__ == '__main__':
    unittest.main()