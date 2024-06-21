import importlib, inspect
import unittest
from unittest.mock import patch, MagicMock


class ResourcesTest(unittest.TestCase):
    MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME = {}
    SHAPE_CLASSES_BY_SHAPE_NAME = {}

    def setUp(self) -> None:
        for name, cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.resources"), inspect.isclass
        ):
            if cls.__module__ == "sagemaker_core.generated.resources":
                if hasattr(cls, "get") and callable(cls.get):
                    self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME[name] = (
                        self._get_required_parameters_for_function(cls.get)
                    )

        for shape_name, shape_cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.shapes"), inspect.isclass
        ):
            if shape_cls.__module__ == "sagemaker_core.generated.shapes":
                self.SHAPE_CLASSES_BY_SHAPE_NAME[shape_name] = shape_cls

    @patch("sagemaker_core.generated.resources.transform")
    @patch("sagemaker_core.generated.resources.Base.get_sagemaker_client")
    def test_resources(self, mock_get_sagemaker_client, mock_transform):
        for name, cls in inspect.getmembers(
            importlib.import_module("sagemaker_core.generated.resources"), inspect.isclass
        ):
            if cls.__module__ == "sagemaker_core.generated.resources":
                if hasattr(cls, "get") and callable(cls.get):
                    function_name = f"describe_{name.lower()}"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    cls.get(**self._get_required_parameters_for_function(cls.get))
                if hasattr(cls, "get_all") and callable(cls.get_all):
                    function_name = f"list_{name.lower()}s"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    cls.get_all(**self._get_required_parameters_for_function(cls.get_all))
                if hasattr(cls, "refresh") and callable(cls.refresh):
                    function_name = f"refresh_{name.lower()}"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    class_instance = cls(**self._get_required_parameters_for_function(cls.get))
                    class_instance.refresh(
                        **self._get_required_parameters_for_function(cls.refresh)
                    )
                if hasattr(cls, "delete") and callable(cls.delete):
                    function_name = f"delete_{name.lower()}"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    class_instance = cls(**self._get_required_parameters_for_function(cls.get))
                    class_instance.delete(**self._get_required_parameters_for_function(cls.delete))
                if hasattr(cls, "create") and callable(cls.create):
                    get_function_name = f"describe_{name.lower()}"
                    create_function_name = f"create_{name.lower()}"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, create_function_name, mocked_method)
                    setattr(mock_get_sagemaker_client, get_function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    cls.create(**self._get_required_parameters_for_function(cls.create))
                if hasattr(cls, "update") and callable(cls.update):
                    get_function_name = f"describe_{name.lower()}"
                    create_function_name = f"update_{name.lower()}"
                    mocked_method = MagicMock()
                    setattr(mock_get_sagemaker_client, create_function_name, mocked_method)
                    setattr(mock_get_sagemaker_client, get_function_name, mocked_method)
                    mock_transform.return_value = self.MOCK_RESOURCES_RESPONSE_BY_RESOURCE_NAME.get(
                        name
                    )
                    class_instance = cls(**self._get_required_parameters_for_function(cls.get))
                    class_instance.update(**self._get_required_parameters_for_function(cls.update))

    def _get_required_parameters_for_function(self, func) -> dict:
        params = {}
        for key, val in inspect.signature(func).parameters.items():
            attribute_type = str(val)
            if (
                "Optional" not in attribute_type
                and key != "self"
                and "utils.Unassigned" not in attribute_type
            ):
                if "str" in attribute_type:
                    params[key] = "Random-String"
                elif "int" in attribute_type or "float" in attribute_type:
                    params[key] = 0
                elif "bool" in attribute_type:
                    params[key] = False
                elif "List" in attribute_type:
                    params[key] = []
                else:
                    shape = attribute_type.split(".")[-1]
                    params[key] = self._generate_test_shape(
                        self.SHAPE_CLASSES_BY_SHAPE_NAME.get(shape)
                    )
        return params

    def _generate_test_shape(self, shape_cls):
        params = {}
        if shape_cls == None:
            return None
        for key, val in inspect.signature(shape_cls).parameters.items():
            attribute_type = str(val.annotation)
            if "Optional" not in attribute_type:
                if "List[str]" in attribute_type and "utils.Unassigned" not in str(val):
                    params[key] = ["Random-String"]
                elif "List" in attribute_type:
                    params[key] = []
                elif "Dict" in attribute_type:
                    params[key] = {}
                elif "bool" in attribute_type:
                    params[key] = False
                elif "str" in attribute_type:
                    params[key] = "Random-String"
                elif "int" in attribute_type or "float" in attribute_type:
                    params[key] = 0
                else:
                    shape = str(val).split(".")[-1]
                    params[key] = self._generate_test_shape(
                        self.SHAPE_CLASSES_BY_SHAPE_NAME.get(shape)
                    )

        return shape_cls(**params)
