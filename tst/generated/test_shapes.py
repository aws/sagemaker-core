import ast
import unittest

from pydantic import BaseModel, ValidationError

from src.generated.shapes import Base, AdditionalS3DataSource, Unassigned
from src.tools.constants import GENERATED_CLASSES_LOCATION, SHAPES_CODEGEN_FILE_NAME

FILE_NAME = GENERATED_CLASSES_LOCATION + "/" + SHAPES_CODEGEN_FILE_NAME


class TestGeneratedShape(unittest.TestCase):
    def test_generated_shapes_have_pydantic_enabled(self):
        # This test ensures that all generated shapes inherit Base which inherits BaseModel, thereby forcing pydantic validiation
        assert issubclass(Base, BaseModel)
        assert (
            self._fetch_number_of_classes_in_file_not_inheriting_a_class(
                FILE_NAME, "Base"
            )
            == 2
        )  # 2 Because Base class itself does not inherit and Unassigned does not need to inherit

    def test_pydantic_validation_for_generated_class_success(self):
        additional_s3_data_source = AdditionalS3DataSource(
            s3_data_type="filestring", s3_uri="s3/uri"
        )
        assert isinstance(additional_s3_data_source.s3_data_type, str)
        assert isinstance(additional_s3_data_source.s3_uri, str)
        assert isinstance(additional_s3_data_source.compression_type, Unassigned)

    def test_pydantic_validation_for_generated_class_success_with_optional_attributes_provided(
        self,
    ):
        additional_s3_data_source = AdditionalS3DataSource(
            s3_data_type="filestring", s3_uri="s3/uri", compression_type="zip"
        )
        assert isinstance(additional_s3_data_source.s3_data_type, str)
        assert isinstance(additional_s3_data_source.s3_uri, str)
        assert isinstance(additional_s3_data_source.compression_type, str)

    def test_pydantic_validation_for_generated_class_throws_error_for_incorrect_input(
        self,
    ):
        with self.assertRaises(ValidationError):
            AdditionalS3DataSource(s3_data_type="str", s3_uri=12)

    def _fetch_number_of_classes_in_file_not_inheriting_a_class(
        self, filepath: str, base_class_name: str
    ):
        count = 0
        with open(filepath, "r") as file:
            tree = ast.parse(file.read(), filename=filepath)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    if not any(
                        base_class.id == base_class_name for base_class in node.bases
                    ):
                        count = count + 1
        return count

    def test_serialize_method_returns_dict(self):
        additional_s3_data_source = AdditionalS3DataSource(
            s3_data_type="filestring", s3_uri="s3/uri"
        )
        serialized_data = additional_s3_data_source.serialize()
        assert isinstance(serialized_data, dict)

    def test_serialize_method_returns_correct_data(self):
        additional_s3_data_source = AdditionalS3DataSource(
            s3_data_type="filestring", s3_uri="s3/uri"
        )
        serialized_data = additional_s3_data_source.serialize()
        assert serialized_data["S3DataType"] == "filestring"
        assert serialized_data["S3Uri"] == "s3/uri"
