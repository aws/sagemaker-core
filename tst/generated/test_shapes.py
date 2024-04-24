import ast
import unittest

from pydantic import BaseModel

from generated.shapes import Base

FILE_NAME = '../src/generated/shapes.py'


class TestGeneratedShape(unittest.TestCase):
    def test_generated_shapes_have_pydantic_enabled(self):
        # This test ensures that all generated shapes inherit Base which inherits BaseModel, thereby forcing pydantic validiation
        assert issubclass(Base, BaseModel)
        assert self._fetch_number_of_classes_in_file_not_inheriting_a_class(FILE_NAME,
                                                                            'Base') == 2  # 2 Because Base class itself does not inherit and Unassigned does not need to inherit

    def _fetch_number_of_classes_in_file_not_inheriting_a_class(self,
                                                                filepath: str,
                                                                base_class_name: str):
        count = 0
        with open(filepath, 'r') as file:
            tree = ast.parse(file.read(), filename=filepath)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    if not any(base_class.id == base_class_name for base_class in node.bases):
                        count = count + 1
        return count
