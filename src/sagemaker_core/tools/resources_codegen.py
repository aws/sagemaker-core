# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Generates the resource classes for the service model."""
import logging
from functools import lru_cache

import os
import json
import re
from sagemaker_core.code_injection.codec import pascal_to_snake
from sagemaker_core.generated.config_schema import SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA
from sagemaker_core.tools.constants import (
    BASIC_RETURN_TYPES,
    GENERATED_CLASSES_LOCATION,
    RESOURCES_CODEGEN_FILE_NAME,
    LICENCES_STRING,
    TERMINAL_STATES,
    BASIC_IMPORTS_STRING,
    LOGGER_STRING,
    CONFIG_SCHEMA_FILE_NAME,
    PYTHON_TYPES_TO_BASIC_JSON_TYPES,
    CONFIGURABLE_ATTRIBUTE_SUBSTRINGS,
)
from sagemaker_core.tools.method import Method, MethodType
from sagemaker_core.util.util import (
    add_indent,
    convert_to_snake_case,
    snake_to_pascal,
    remove_html_tags,
)
from sagemaker_core.tools.resources_extractor import ResourcesExtractor
from sagemaker_core.tools.shapes_extractor import ShapesExtractor
from sagemaker_core.tools.templates import (
    CALL_OPERATION_API_TEMPLATE,
    CREATE_METHOD_TEMPLATE,
    DESERIALIZE_RESPONSE_TEMPLATE,
    DESERIALIZE_RESPONSE_TO_BASIC_TYPE_TEMPLATE,
    GENERIC_METHOD_TEMPLATE,
    GET_METHOD_TEMPLATE,
    INITIALIZE_CLIENT_TEMPLATE,
    REFRESH_METHOD_TEMPLATE,
    RESOURCE_BASE_CLASS_TEMPLATE,
    RETURN_ITERATOR_TEMPLATE,
    SERIALIZE_INPUT_TEMPLATE,
    SERIALIZE_LIST_INPUT_TEMPLATE,
    STOP_METHOD_TEMPLATE,
    DELETE_METHOD_TEMPLATE,
    WAIT_METHOD_TEMPLATE,
    WAIT_FOR_STATUS_METHOD_TEMPLATE,
    UPDATE_METHOD_TEMPLATE,
    POPULATE_DEFAULTS_DECORATOR_TEMPLATE,
    CREATE_METHOD_TEMPLATE_WITHOUT_DEFAULTS,
    INVOKE_METHOD_TEMPLATE,
    INVOKE_ASYNC_METHOD_TEMPLATE,
    INVOKE_WITH_RESPONSE_STREAM_METHOD_TEMPLATE,
    IMPORT_METHOD_TEMPLATE,
    FAILED_STATUS_ERROR_TEMPLATE,
    GET_NAME_METHOD_TEMPLATE,
    GET_ALL_METHOD_NO_ARGS_TEMPLATE,
    GET_ALL_METHOD_WITH_ARGS_TEMPLATE,
    UPDATE_METHOD_TEMPLATE_WITHOUT_DECORATOR,
)
from sagemaker_core.tools.data_extractor import (
    load_combined_shapes_data,
    load_combined_operations_data,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

TYPE = "type"
OBJECT = "object"
PROPERTIES = "properties"
SAGEMAKER = "SageMaker"
PYTHON_SDK = "PythonSDK"
SCHEMA_VERSION = "SchemaVersion"
RESOURCES = "Resources"
REQUIRED = "required"
GLOBAL_DEFAULTS = "GlobalDefaults"


class ResourcesCodeGen:
    """
    A class for generating resources based on a service JSON file.

    Args:
        service_json (dict): The Botocore service.json containing the shape definitions.

    Attributes:
        service_json (dict): The Botocore service.json containing the shape definitions.
        version (str): The API version of the service.
        protocol (str): The protocol used by the service.
        service (str): The full name of the service.
        service_id (str): The ID of the service.
        uid (str): The unique identifier of the service.
        operations (dict): The operations supported by the service.
        shapes (dict): The shapes used by the service.
        resources_extractor (ResourcesExtractor): An instance of the ResourcesExtractor class.
        resources_plan (DataFrame): The resource plan in dataframe format.
        shapes_extractor (ShapesExtractor): An instance of the ShapesExtractor class.

    Raises:
        Exception: If the service ID is not supported or the protocol is not supported.

    """

    def __init__(self, service_json: dict):
        # Initialize the service_json dict
        self.service_json = service_json

        # Extract the metadata
        metadata = self.service_json["metadata"]
        self.version = metadata["apiVersion"]
        self.protocol = metadata["protocol"]
        self.service = metadata["serviceFullName"]
        self.service_id = metadata["serviceId"]
        self.uid = metadata["uid"]

        # Check if the service ID and protocol are supported
        if self.service_id != "SageMaker":
            raise Exception(f"ServiceId {self.service_id} not supported in this resource generator")
        if self.protocol != "json":
            raise Exception(f"Protocol {self.protocol} not supported in this resource generator")

        # Extract the operations and shapes
        self.operations = load_combined_operations_data()
        self.shapes = load_combined_shapes_data()

        # Initialize the resources and shapes extractors
        self.resources_extractor = ResourcesExtractor()
        self.shapes_extractor = ShapesExtractor()

        # Extract the resources plan and shapes DAG
        self.resources_plan = self.resources_extractor.get_resource_plan()
        self.resource_methods = self.resources_extractor.get_resource_methods()
        self.shape_dag = self.shapes_extractor.get_shapes_dag()

        # Create the Config Schema
        self.generate_config_schema()
        # Generate the resources
        self.generate_resources()

    def generate_license(self) -> str:
        """
        Generate the license for the generated resources file.

        Returns:
            str: The license.

        """
        return LICENCES_STRING

    def generate_imports(self) -> str:
        """
        Generate the import statements for the generated resources file.

        Returns:
            str: The import statements.
        """
        # List of import statements
        imports = [
            BASIC_IMPORTS_STRING,
            "import datetime",
            "import time",
            "import os",
            "from pprint import pprint",
            "from pydantic import validate_call",
            "from typing import Dict, List, Literal, Optional, Union\n"
            "from boto3.session import Session",
            "from sagemaker_core.code_injection.codec import transform",
            "from sagemaker_core.generated.utils import SageMakerClient, SageMakerRuntimeClient, ResourceIterator, Unassigned, snake_to_pascal, pascal_to_snake, is_not_primitive, is_not_str_dict",
            "from sagemaker_core.generated.intelligent_defaults_helper import load_default_configs_for_resource_name, get_config_value",
            "from sagemaker_core.generated.shapes import *",
            "from sagemaker_core.generated.exceptions import *",
        ]

        formated_imports = "\n".join(imports)
        formated_imports += "\n\n"

        # Join the import statements with a newline character and return
        return formated_imports

    def generate_base_class(self) -> str:
        """
        Generate the base class for the resources.

        Returns:
            str: The base class.

        """
        return RESOURCE_BASE_CLASS_TEMPLATE

    def generate_logging(self) -> str:
        """
        Generate the logging statements for the generated resources file.

        Returns:
            str: The logging statements.

        """
        return LOGGER_STRING

    @staticmethod
    def generate_defaults_decorator(
        config_schema_for_resource: dict, resource_name: str, class_attributes: dict
    ) -> str:
        return POPULATE_DEFAULTS_DECORATOR_TEMPLATE.format(
            config_schema_for_resource=add_indent(
                json.dumps(config_schema_for_resource.get(PROPERTIES), indent=2), 4
            ),
            resource_name=resource_name,
            configurable_attributes=CONFIGURABLE_ATTRIBUTE_SUBSTRINGS,
            class_attributes=class_attributes,
        )

    def generate_resources(
        self,
        output_folder: str = GENERATED_CLASSES_LOCATION,
        file_name: str = RESOURCES_CODEGEN_FILE_NAME,
    ) -> None:
        """
        Generate the resources file.

        Args:
            output_folder (str, optional): The output folder path. Defaults to "GENERATED_CLASSES_LOCATION".
            file_name (str, optional): The output file name. Defaults to "RESOURCES_CODEGEN_FILE_NAME".
        """
        # Check if the output folder exists, if not, create it
        os.makedirs(output_folder, exist_ok=True)

        # Create the full path for the output file
        output_file = os.path.join(output_folder, file_name)

        # Open the output file
        with open(output_file, "w") as file:
            # Generate and write the license to the file
            file.write(self.generate_license())

            # Generate and write the imports to the file
            file.write(self.generate_imports())

            # Generate and write the logging statements to the file
            file.write(self.generate_logging())

            # Generate and write the base class to the file
            file.write(self.generate_base_class())

            self.resource_names = [
                row["resource_name"] for _, row in self.resources_plan.iterrows()
            ]
            # Iterate over the rows in the resources plan
            for _, row in self.resources_plan.iterrows():
                # Extract the necessary data from the row
                resource_name = row["resource_name"]
                class_methods = row["class_methods"]
                object_methods = row["object_methods"]
                additional_methods = row["additional_methods"]
                raw_actions = row["raw_actions"]
                resource_status_chain = row["resource_status_chain"]
                resource_states = row["resource_states"]

                # Generate the resource class
                resource_class = self.generate_resource_class(
                    resource_name,
                    class_methods,
                    object_methods,
                    additional_methods,
                    raw_actions,
                    resource_status_chain,
                    resource_states,
                )

                # If the resource class was successfully generated, write it to the file
                if resource_class:
                    file.write(f"{resource_class}\n\n")

    def _evaluate_method(
        self, resource_name: str, method_name: str, methods: list, **kwargs
    ) -> str:
        """Evaluate the specified method for a resource.

        Args:
            resource_name (str): The name of the resource.
            method_name (str): The name of the method to evaluate.
            methods (list): The list of methods for the resource.

        Returns:
            str: Formatted method if needed for a resource, else returns an empty string.
        """
        if method_name in methods:
            return getattr(self, f"generate_{method_name}_method")(resource_name, **kwargs)
        else:
            # log.warning(f"Resource {resource_name} does not have a {method_name.upper()} method")
            return ""

    def generate_resource_class(
        self,
        resource_name: str,
        class_methods: list,
        object_methods: list,
        additional_methods: list,
        raw_actions: list,
        resource_status_chain: list,
        resource_states: list,
    ) -> str:
        """
        Generate the resource class for a resource.

        Args:
            resource_name (str): The name of the resource.
            class_methods (list): The class methods.
            object_methods (list): The object methods.
            additional_methods (list): The additional methods.
            raw_actions (list): The raw actions.

        Returns:
            str: The formatted resource class.

        """
        # Initialize an empty string for the resource class
        resource_class = ""

        # Check if 'get' is in the class methods
        if self._is_get_in_class_methods(class_methods):
            # Start defining the class
            resource_class = f"class {resource_name}(Base):\n"

            class_attributes = self._get_class_attributes(resource_name)
            class_attributes_string = class_attributes[1]
            get_operation = self.operations["Describe" + resource_name]
            get_operation_shape = get_operation["output"]["shape"]
            class_attributes_and_documentation = (
                self.shapes_extractor.fetch_shape_members_and_doc_strings(get_operation_shape)
            )
            class_documentation_string = self._get_class_documentation_string(
                class_attributes_and_documentation, resource_name
            )
            resource_attributes = list(class_attributes[0].keys())

            defaults_decorator_method = ""
            # Check if 'create' is in the class methods
            if "create" in class_methods or "update" in class_methods:
                if config_schema_for_resource := self._get_config_schema_for_resources().get(
                    resource_name
                ):
                    defaults_decorator_method = self.generate_defaults_decorator(
                        resource_name=resource_name,
                        class_attributes=class_attributes[0],
                        config_schema_for_resource=config_schema_for_resource,
                    )
            needs_defaults_decorator = defaults_decorator_method != ""

            # Generate the 'get' method
            get_method = self.generate_get_method(resource_name)

            # Add the class attributes and methods to the class definition
            resource_class += add_indent(f'"""\n{class_documentation_string}\n"""\n', 4)

            # Add the class attributes and methods to the class definition
            resource_class += add_indent(class_attributes_string, 4)

            resource_lower = convert_to_snake_case(resource_name)
            get_name_method = self.generate_get_name_method(resource_lower=resource_lower)
            resource_class += add_indent(get_name_method, 4)

            if defaults_decorator_method:
                resource_class += "\n"
                resource_class += add_indent(defaults_decorator_method, 4)

            if create_method := self._evaluate_method(
                resource_name,
                "create",
                class_methods,
                needs_defaults_decorator=needs_defaults_decorator,
            ):
                resource_class += add_indent(create_method, 4)

            resource_class += add_indent(get_method, 4)

            if refresh_method := self._evaluate_method(resource_name, "refresh", object_methods):
                resource_class += add_indent(refresh_method, 4)

            if update_method := self._evaluate_method(
                resource_name,
                "update",
                object_methods,
                resource_attributes=resource_attributes,
                needs_defaults_decorator=needs_defaults_decorator,
            ):
                resource_class += add_indent(update_method, 4)

            if delete_method := self._evaluate_method(resource_name, "delete", object_methods):
                resource_class += add_indent(delete_method, 4)

            if stop_method := self._evaluate_method(resource_name, "stop", object_methods):
                resource_class += add_indent(stop_method, 4)

            if wait_method := self._evaluate_method(resource_name, "wait", object_methods):
                resource_class += add_indent(wait_method, 4)

            if wait_for_status_method := self._evaluate_method(
                resource_name, "wait_for_status", object_methods
            ):
                resource_class += add_indent(wait_for_status_method, 4)

            if invoke_method := self._evaluate_method(
                resource_name,
                "invoke",
                object_methods,
                resource_attributes=resource_attributes,
            ):
                resource_class += add_indent(invoke_method, 4)

            if invoke_async_method := self._evaluate_method(
                resource_name,
                "invoke_async",
                object_methods,
                resource_attributes=resource_attributes,
            ):
                resource_class += add_indent(invoke_async_method, 4)

            if invoke_with_response_stream_method := self._evaluate_method(
                resource_name,
                "invoke_with_response_stream",
                object_methods,
                resource_attributes=resource_attributes,
            ):
                resource_class += add_indent(invoke_with_response_stream_method, 4)

            if import_method := self._evaluate_method(resource_name, "import", class_methods):
                resource_class += add_indent(import_method, 4)

            if list_method := self._evaluate_method(resource_name, "get_all", class_methods):
                resource_class += add_indent(list_method, 4)

        else:
            # If there's no 'get' method, log a message
            # TODO: Handle the resources without 'get' differently
            log.warning(f"Resource {resource_name} does not have a GET method")

        if resource_name in self.resource_methods:
            # TODO: use resource_methods for all methods
            for method in self.resource_methods[resource_name].values():
                formatted_method = self.generate_method(method, resource_attributes)
                resource_class += add_indent(formatted_method, 4)

        # Return the class definition
        return resource_class

    def _get_class_attributes(self, resource_name: str) -> tuple:
        """Get the class attributes for a resource.

        Args:
            resource_name (str): The name of the resource.

        Returns:
            tuple[dict, str]: The class attributes and the formatted class attributes string.
        """

        # Get the operation and shape for the 'get' method
        get_operation = self.operations["Describe" + resource_name]
        get_operation_shape = get_operation["output"]["shape"]

        # Use 'get' operation input as the required class attributes.
        # These are the mimumum identifing attributes for a resource object (ie, required for refresh())
        get_operation_input_shape = get_operation["input"]["shape"]
        required_attributes = self.shapes[get_operation_input_shape].get("required", [])

        # Generate the class attributes based on the shape
        class_attributes = self.shapes_extractor.generate_data_shape_members_and_string_body(
            shape=get_operation_shape, required_override=tuple(required_attributes)
        )
        return class_attributes

    def _get_class_documentation_string(
        self, class_attributes_and_documentation, resource_name
    ) -> str:
        documentation_string = f"{resource_name} \n Class representing resource {resource_name}\n"
        documentation_string += f"Attributes\n"
        documentation_string += f"---------------------\n"
        for class_attribute, documentation in class_attributes_and_documentation.items():
            class_attribute_snake = pascal_to_snake(class_attribute)
            if documentation == None:
                documentation_string += f"{class_attribute_snake}:\n"
            else:
                documentation_string += f"{class_attribute_snake}:{documentation}\n"
        return remove_html_tags(documentation_string)

    def _generate_create_method_args(
        self, operation_input_shape_name: str, resource_name: str
    ) -> str:
        """Generates the arguments for a method.
        Args:
            operation_input_shape_name (str): The name of the input shape for the operation.
        Returns:
            str: The generated arguments string.
        """
        typed_shape_members = self.shapes_extractor.generate_shape_members(
            operation_input_shape_name
        )
        resource_name_in_snake_case = pascal_to_snake(resource_name)
        method_args = ""
        last_key = list(typed_shape_members.keys())[-1]
        for attr, attr_type in typed_shape_members.items():
            method_parameter_type = attr_type
            if (
                attr.endswith("name")
                and attr[: -len("_name")] != resource_name_in_snake_case
                and attr != "name"
                and snake_to_pascal(attr[: -len("_name")]) in self.resource_names
            ):
                if attr_type.startswith("Optional"):
                    method_args += f"{attr}: Optional[Union[str, object]] = Unassigned(),"
                else:
                    method_args += f"{attr}: Union[str, object],"
            else:
                method_args += f"{attr}: {method_parameter_type},"
            if attr != last_key:
                method_args += "\n"
        method_args = add_indent(method_args)
        return method_args

    # TODO: use this method to replace _generate_operation_input_args
    def _generate_operation_input_args_updated(
        self,
        resource_operation: dict,
        is_class_method: bool,
        resource_attributes: list,
        exclude_list: list = [],
    ) -> str:
        """Generate the operation input arguments string.

        Args:
            resource_operation (dict): The resource operation dictionary.
            is_class_method (bool): Indicates method is class method, else object method.

        Returns:
            str: The formatted operation input arguments string.
        """
        input_shape_name = resource_operation["input"]["shape"]
        input_shape_members = list(self.shapes[input_shape_name]["members"].keys())

        if is_class_method:
            args = (
                f"'{member}': {convert_to_snake_case(member)}"
                for member in input_shape_members
                if convert_to_snake_case(member) not in exclude_list
            )
        else:
            args = []
            for member in input_shape_members:
                if convert_to_snake_case(member) not in exclude_list:
                    if convert_to_snake_case(member) in resource_attributes:
                        args.append(f"'{member}': self.{convert_to_snake_case(member)}")
                    else:
                        args.append(f"'{member}': {convert_to_snake_case(member)}")

        operation_input_args = ",\n".join(args)
        operation_input_args += ","
        operation_input_args = add_indent(operation_input_args, 8)

        return operation_input_args

    def _generate_operation_input_args(
        self, resource_operation: dict, is_class_method: bool, exclude_list: list = []
    ) -> str:
        """Generate the operation input arguments string.

        Args:
            resource_operation (dict): The resource operation dictionary.
            is_class_method (bool): Indicates method is class method, else object method.

        Returns:
            str: The formatted operation input arguments string.
        """
        input_shape_name = resource_operation["input"]["shape"]
        input_shape_members = list(self.shapes[input_shape_name]["members"].keys())

        if is_class_method:
            args = (
                f"'{member}': {convert_to_snake_case(member)}"
                for member in input_shape_members
                if convert_to_snake_case(member) not in exclude_list
            )
        else:
            args = (
                f"'{member}': self.{convert_to_snake_case(member)}"
                for member in input_shape_members
                if convert_to_snake_case(member) not in exclude_list
            )

        operation_input_args = ",\n".join(args)
        operation_input_args += ","
        operation_input_args = add_indent(operation_input_args, 8)

        return operation_input_args

    def _generate_operation_input_necessary_args(
        self, resource_operation: dict, resource_attributes: list
    ) -> str:
        """
        Generate the operation input arguments string.
        This will try to re-use args from the object attributes if present and it not presebt will use te ones provided in the parameter.
        Args:
            resource_operation (dict): The resource operation dictionary.
            is_class_method (bool): Indicates method is class method, else object method.

        Returns:
            str: The formatted operation input arguments string.
        """
        input_shape_name = resource_operation["input"]["shape"]
        input_shape_members = list(self.shapes[input_shape_name]["members"].keys())

        args = list()
        for member in input_shape_members:
            if convert_to_snake_case(member) in resource_attributes:
                args.append(f"'{member}': self.{convert_to_snake_case(member)}")
            else:
                args.append(f"'{member}': {convert_to_snake_case(member)}")

        operation_input_args = ",\n".join(args)
        operation_input_args += ","
        operation_input_args = add_indent(operation_input_args, 8)

        return operation_input_args

    def _generate_method_args(
        self, operation_input_shape_name: str, exclude_list: list = []
    ) -> str:
        """Generates the arguments for a method.
        This will exclude attributes in the exclude_list from the arguments. For example, This is used for update() method
         which does not require the resource identifier attributes to be passed as arguments.

        Args:
            operation_input_shape_name (str): The name of the input shape for the operation.
            exclude_list (list): The list of attributes to exclude from the arguments.

        Returns:
            str: The generated arguments string.
        """
        typed_shape_members = self.shapes_extractor.generate_shape_members(
            operation_input_shape_name
        )

        args = (
            f"{attr}: {attr_type}"
            for attr, attr_type in typed_shape_members.items()
            if attr not in exclude_list
        )
        method_args = ",\n".join(args)
        if not method_args:
            return ""
        method_args += ","
        method_args = add_indent(method_args)
        return method_args

    def _generate_get_args(self, resource_name: str, operation_input_shape_name: str) -> str:
        """
        Generates a resource identifier based on the required members for the Describe and Create operations.

        Args:
            resource_name (str): The name of the resource.
            operation_input_shape_name (str): The name of the input shape for the operation.

        Returns:
            str: The generated resource identifier.
        """
        describe_operation = self.operations["Describe" + resource_name]
        describe_operation_input_shape_name = describe_operation["input"]["shape"]

        required_members = self.shapes_extractor.get_required_members(
            describe_operation_input_shape_name
        )

        operation_required_members = self.shapes_extractor.get_required_members(
            operation_input_shape_name
        )

        identifiers = []
        for member in required_members:
            if member not in operation_required_members:
                identifiers.append(f"{member}=response['{snake_to_pascal(member)}']")
            else:
                identifiers.append(f"{member}={member}")

        get_args = ", ".join(identifiers)
        return get_args

    def generate_create_method(self, resource_name: str, **kwargs) -> str:
        """
        Auto-generate the CREATE method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Create Method template.

        """
        # Get the operation and shape for the 'create' method
        operation_name = "Create" + resource_name
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        # Generate the arguments for the 'create' method
        create_args = self._generate_create_method_args(operation_input_shape_name, resource_name)

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=True
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        get_args = self._generate_get_args(resource_name, operation_input_shape_name)

        # Format the method using the CREATE_METHOD_TEMPLATE
        if kwargs["needs_defaults_decorator"]:
            formatted_method = CREATE_METHOD_TEMPLATE.format(
                resource_name=resource_name,
                create_args=create_args,
                resource_lower=resource_lower,
                service_name="sagemaker",  # TODO: change service name based on the service - runtime, sagemaker, etc.
                operation_input_args=operation_input_args,
                operation=operation,
                get_args=get_args,
            )
        else:
            formatted_method = CREATE_METHOD_TEMPLATE_WITHOUT_DEFAULTS.format(
                resource_name=resource_name,
                create_args=create_args,
                resource_lower=resource_lower,
                service_name="sagemaker",  # TODO: change service name based on the service - runtime, sagemaker, etc.
                operation_input_args=operation_input_args,
                operation=operation,
                get_args=get_args,
            )

        # Return the formatted method
        return formatted_method

    def generate_import_method(self, resource_name: str) -> str:
        """
        Auto-generate the IMPORT method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Import Method template.

        """
        # Get the operation and shape for the 'import' method
        operation_name = "Import" + resource_name
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        # Generate the arguments for the 'import' method
        import_args = self._generate_method_args(operation_input_shape_name)

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=True
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        get_args = self._generate_get_args(resource_name, operation_input_shape_name)

        # Format the method using the IMPORT_METHOD_TEMPLATE
        formatted_method = IMPORT_METHOD_TEMPLATE.format(
            resource_name=resource_name,
            import_args=import_args,
            resource_lower=resource_lower,
            service_name="sagemaker",  # TODO: change service name based on the service - runtime, sagemaker, etc.
            operation_input_args=operation_input_args,
            operation=operation,
            get_args=get_args,
        )

        # Return the formatted method
        return formatted_method

    def generate_get_name_method(self, resource_lower: str) -> str:
        """
        Autogenerate the method that would return the identifier of the object
        Args:
            resource_name: Name of Resource
        Returns:
            str: Formatted Get Name Method
        """
        return GET_NAME_METHOD_TEMPLATE.format(resource_lower=resource_lower)

    def generate_update_method(self, resource_name: str, **kwargs) -> str:
        """
        Auto-generate the UPDATE method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Update Method template.

        """
        # Get the operation and shape for the 'update' method
        operation_name = "Update" + resource_name
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        required_members = self.shapes[operation_input_shape_name]["required"]

        # Exclude any required attributes that are already present as resource attributes and are also identifiers
        exclude_required_attributes = []
        for member in required_members:
            snake_member = convert_to_snake_case(member)
            if snake_member in kwargs["resource_attributes"] and any(
                id in snake_member for id in ["name", "arn", "id"]
            ):
                exclude_required_attributes.append(snake_member)

        # Generate the arguments for the 'update' method
        update_args = self._generate_method_args(
            operation_input_shape_name, exclude_required_attributes
        )

        operation_input_args = self._generate_operation_input_necessary_args(
            operation_metadata, exclude_required_attributes
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        if kwargs["needs_defaults_decorator"]:
            formatted_method = UPDATE_METHOD_TEMPLATE.format(
                service_name="sagemaker",
                resource_name=resource_name,
                resource_lower=resource_lower,
                update_args=update_args,
                operation_input_args=operation_input_args,
                operation=operation,
            )
        else:
            formatted_method = UPDATE_METHOD_TEMPLATE_WITHOUT_DECORATOR.format(
                service_name="sagemaker",
                resource_name=resource_name,
                resource_lower=resource_lower,
                update_args=update_args,
                operation_input_args=operation_input_args,
                operation=operation,
            )

        # Return the formatted method
        return formatted_method

    def generate_invoke_method(self, resource_name: str, **kwargs) -> str:
        """
        Auto-generate the INVOKE ASYNC method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Update Method template.

        """
        # Get the operation and shape for the 'create' method
        operation_name = "Invoke" + resource_name
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        # Generate the arguments for the 'create' method
        invoke_args = self._generate_method_args(
            operation_input_shape_name, kwargs["resource_attributes"]
        )

        operation_input_args = self._generate_operation_input_necessary_args(
            operation_metadata, kwargs["resource_attributes"]
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        # Format the method using the CREATE_METHOD_TEMPLATE
        formatted_method = INVOKE_METHOD_TEMPLATE.format(
            service_name="sagemaker-runtime",
            invoke_args=invoke_args,
            resource_name=resource_name,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
        )

        # Return the formatted method
        return formatted_method

    def generate_invoke_async_method(self, resource_name: str, **kwargs) -> str:
        """
        Auto-generate the INVOKE method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Update Method template.

        """
        # Get the operation and shape for the 'create' method
        operation_name = "Invoke" + resource_name + "Async"
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        # Generate the arguments for the 'create' method
        invoke_args = self._generate_method_args(
            operation_input_shape_name, kwargs["resource_attributes"]
        )

        operation_input_args = self._generate_operation_input_necessary_args(
            operation_metadata, kwargs["resource_attributes"]
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        # Format the method using the CREATE_METHOD_TEMPLATE
        formatted_method = INVOKE_ASYNC_METHOD_TEMPLATE.format(
            service_name="sagemaker-runtime",
            create_args=invoke_args,
            resource_name=resource_name,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
        )

        # Return the formatted method
        return formatted_method

    def generate_invoke_with_response_stream_method(self, resource_name: str, **kwargs) -> str:
        """
        Auto-generate the INVOKE with response stream method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Update Method template.

        """
        # Get the operation and shape for the 'create' method
        operation_name = "Invoke" + resource_name + "WithResponseStream"
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        # Generate the arguments for the 'create' method
        invoke_args = self._generate_method_args(
            operation_input_shape_name, kwargs["resource_attributes"]
        )

        operation_input_args = self._generate_operation_input_necessary_args(
            operation_metadata, kwargs["resource_attributes"]
        )

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        # Format the method using the CREATE_METHOD_TEMPLATE
        formatted_method = INVOKE_WITH_RESPONSE_STREAM_METHOD_TEMPLATE.format(
            service_name="sagemaker-runtime",
            create_args=invoke_args,
            resource_name=resource_name,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
        )

        # Return the formatted method
        return formatted_method

    def generate_get_method(self, resource_name: str) -> str:
        """
        Auto-generate the GET method (describe API) for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Get Method template.

        """
        operation_name = "Describe" + resource_name
        operation_metadata = self.operations[operation_name]
        resource_operation_input_shape_name = operation_metadata["input"]["shape"]
        resource_operation_output_shape_name = operation_metadata["output"]["shape"]

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=True
        )

        # Generate the arguments for the 'update' method
        describe_args = self._generate_method_args(resource_operation_input_shape_name)

        resource_lower = convert_to_snake_case(resource_name)

        operation = convert_to_snake_case(operation_name)

        formatted_method = GET_METHOD_TEMPLATE.format(
            resource_name=resource_name,
            service_name="sagemaker",  # TODO: change service name based on the service - runtime, sagemaker, etc.
            describe_args=describe_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            describe_operation_output_shape=resource_operation_output_shape_name,
        )
        return formatted_method

    def generate_refresh_method(self, resource_name: str) -> str:
        """Auto-Generate 'refresh' object Method [describe API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted refresh Method template.
        """
        operation_name = "Describe" + resource_name
        operation_metadata = self.operations[operation_name]
        resource_operation_output_shape_name = operation_metadata["output"]["shape"]

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = REFRESH_METHOD_TEMPLATE.format(
            resource_name=resource_name,
            operation_input_args=operation_input_args,
            operation=operation,
            describe_operation_output_shape=resource_operation_output_shape_name,
        )
        return formatted_method

    def generate_delete_method(self, resource_name: str) -> str:
        """Auto-Generate 'delete' object Method [delete API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted delete Method template.
        """
        operation_name = "Delete" + resource_name
        operation_metadata = self.operations[operation_name]

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = DELETE_METHOD_TEMPLATE.format(
            operation_input_args=operation_input_args,
            operation=operation,
        )
        return formatted_method

    def generate_stop_method(self, resource_name: str) -> str:
        """Auto-Generate 'stop' object Method [delete API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted stop Method template.
        """
        operation_name = "Stop" + resource_name
        operation_metadata = self.operations[operation_name]

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = STOP_METHOD_TEMPLATE.format(
            operation_input_args=operation_input_args,
            operation=operation,
        )
        return formatted_method

    def generate_method(self, method: Method, resource_attributes: list):
        # TODO: Use special templates for some methods with different formats like list and wait
        if method.method_name.startswith("get_all"):
            return self.generate_additional_get_all_method(method, resource_attributes)
        operation_metadata = self.operations[method.operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]
        if method.method_type == MethodType.CLASS:
            decorator = "@classmethod"
            method_args = add_indent("cls,\n", 4)
            method_args += self._generate_method_args(operation_input_shape_name)
            operation_input_args = self._generate_operation_input_args_updated(
                operation_metadata, True, resource_attributes
            )
        else:
            decorator = ""
            method_args = add_indent("self,\n", 4)
            method_args += (
                self._generate_method_args(operation_input_shape_name, resource_attributes) + "\n"
            )
            operation_input_args = self._generate_operation_input_args_updated(
                operation_metadata, False, resource_attributes
            )
        method_args += add_indent("session: Optional[Session] = None,\n", 4)
        method_args += add_indent("region: Optional[str] = None,", 4)

        if method.return_type == "None":
            return_type = "None"
            deserialize_response = ""
        elif method.return_type in BASIC_RETURN_TYPES:
            return_type = f"Optional[{method.return_type}]"
            deserialize_response = DESERIALIZE_RESPONSE_TO_BASIC_TYPE_TEMPLATE
        else:
            if method.return_type == "cls":
                return_type = f'Optional["{method.resource_name}"]'
                return_type_conversion = "cls"
            else:
                return_type = f"Optional[{method.return_type}]"
                return_type_conversion = method.return_type
            operation_output_shape = operation_metadata["output"]["shape"]
            deserialize_response = DESERIALIZE_RESPONSE_TEMPLATE.format(
                operation_output_shape=operation_output_shape,
                return_type_conversion=return_type_conversion,
            )

        serialize_operation_input = SERIALIZE_INPUT_TEMPLATE.format(
            operation_input_args=operation_input_args
        )
        initialize_client = INITIALIZE_CLIENT_TEMPLATE.format(service_name=method.service_name)
        call_operation_api = CALL_OPERATION_API_TEMPLATE.format(
            operation=convert_to_snake_case(method.operation_name)
        )
        formatted_method = GENERIC_METHOD_TEMPLATE.format(
            decorator=decorator,
            method_name=method.method_name,
            method_args=method_args,
            return_type=return_type,
            serialize_operation_input=serialize_operation_input,
            initialize_client=initialize_client,
            call_operation_api=call_operation_api,
            deserialize_response=deserialize_response,
        )
        return formatted_method

    def generate_additional_get_all_method(self, method: Method, resource_attributes: list):
        """Auto-Generate methods that return a list of objects.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted method code.
        """
        # TODO: merge this with generate_get_all_method
        operation_metadata = self.operations[method.operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]
        exclude_list = ["next_token", "max_results"]
        if method.method_type == MethodType.CLASS:
            decorator = "@classmethod"
            method_args = add_indent("cls,\n", 4)
            method_args += self._generate_method_args(operation_input_shape_name, exclude_list)
            operation_input_args = self._generate_operation_input_args_updated(
                operation_metadata, True, resource_attributes, exclude_list
            )
        else:
            decorator = ""
            method_args = add_indent("self,\n", 4)
            method_args += self._generate_method_args(
                operation_input_shape_name, exclude_list + resource_attributes
            )
            operation_input_args = self._generate_operation_input_args_updated(
                operation_metadata, False, resource_attributes, exclude_list
            )
        method_args += add_indent("session: Optional[Session] = None,\n", 4)
        method_args += add_indent("region: Optional[str] = None,", 4)

        if method.return_type == method.resource_name:
            return_type = f'ResourceIterator["{method.resource_name}"]'
        else:
            return_type = f"ResourceIterator[{method.return_type}]"

        get_list_operation_output_shape = operation_metadata["output"]["shape"]
        list_operation_output_members = self.shapes[get_list_operation_output_shape]["members"]

        filtered_list_operation_output_members = next(
            {key: value}
            for key, value in list_operation_output_members.items()
            if key != "NextToken"
        )
        summaries_key = next(iter(filtered_list_operation_output_members))
        summaries_shape_name = filtered_list_operation_output_members[summaries_key]["shape"]
        summary_name = self.shapes[summaries_shape_name]["member"]["shape"]

        list_method = convert_to_snake_case(method.operation_name)

        # TODO: add rules for custom key mapping and list methods with no args
        resource_iterator_args_list = [
            "client=client",
            f"list_method='{list_method}'",
            f"summaries_key='{summaries_key}'",
            f"summary_name='{summary_name}'",
            f"resource_cls={method.return_type}",
            "list_method_kwargs=operation_input_args",
        ]

        resource_iterator_args = ",\n".join(resource_iterator_args_list)
        resource_iterator_args = add_indent(resource_iterator_args, 8)
        serialize_operation_input = SERIALIZE_LIST_INPUT_TEMPLATE.format(
            operation_input_args=operation_input_args
        )
        initialize_client = INITIALIZE_CLIENT_TEMPLATE.format(service_name=method.service_name)
        deserialize_response = RETURN_ITERATOR_TEMPLATE.format(
            resource_iterator_args=resource_iterator_args
        )

        return GENERIC_METHOD_TEMPLATE.format(
            decorator=decorator,
            method_name=method.method_name,
            method_args=method_args,
            return_type=return_type,
            serialize_operation_input=serialize_operation_input,
            initialize_client=initialize_client,
            call_operation_api="",
            deserialize_response=deserialize_response,
        )

    def _get_failure_reason_ref(self, resource_name: str) -> str:
        """Get the failure reason reference for a resource object.
        Args:
            resource_name (str): The resource name.
        Returns:
            str: The failure reason reference for resource object
        """
        describe_output = self.operations["Describe" + resource_name]["output"]["shape"]
        shape_members = self.shapes[describe_output]

        for member in shape_members["members"]:
            if "FailureReason" in member or "StatusMessage" in member:
                return f"self.{convert_to_snake_case(member)}"

        return "'(Unknown)'"

    def generate_wait_method(self, resource_name: str) -> str:
        """Auto-Generate WAIT Method for a waitable resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Wait Method template.
        """
        resource_status_chain, resource_states = (
            self.resources_extractor.get_status_chain_and_states(resource_name)
        )

        # Get terminal states for resource
        terminal_resource_states = []
        for state in resource_states:
            # Handles when a resource has terminal states like UpdateCompleted, CreateFailed, etc.
            # Checking lower because case is not consistent accross resources (ie, COMPLETED vs Completed)
            if any(terminal_state.lower() in state.lower() for terminal_state in TERMINAL_STATES):
                terminal_resource_states.append(state)

        # Get resource status key path
        status_key_path = ""
        for member in resource_status_chain:
            status_key_path += f'.{convert_to_snake_case(member["name"])}'

        failure_reason = self._get_failure_reason_ref(resource_name)
        formatted_failed_block = FAILED_STATUS_ERROR_TEMPLATE.format(
            resource_name=resource_name, reason=failure_reason
        )
        formatted_failed_block = add_indent(formatted_failed_block, 12)

        formatted_method = WAIT_METHOD_TEMPLATE.format(
            terminal_resource_states=terminal_resource_states,
            status_key_path=status_key_path,
            failed_error_block=formatted_failed_block,
            resource_name=resource_name,
        )
        return formatted_method

    def generate_wait_for_status_method(self, resource_name: str) -> str:
        """Auto-Generate WAIT_FOR_STATUS Method for a waitable resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted wait_for_status Method template.
        """
        resource_status_chain, resource_states = (
            self.resources_extractor.get_status_chain_and_states(resource_name)
        )

        # Get resource status key path
        status_key_path = ""
        for member in resource_status_chain:
            status_key_path += f'.{convert_to_snake_case(member["name"])}'

        formatted_failed_block = ""
        if any("failed" in state.lower() for state in resource_states):
            failure_reason = self._get_failure_reason_ref(resource_name)
            formatted_failed_block = FAILED_STATUS_ERROR_TEMPLATE.format(
                resource_name=resource_name, reason=failure_reason
            )
            formatted_failed_block = add_indent(formatted_failed_block, 8)

        formatted_method = WAIT_FOR_STATUS_METHOD_TEMPLATE.format(
            resource_states=resource_states,
            status_key_path=status_key_path,
            failed_error_block=formatted_failed_block,
            resource_name=resource_name,
        )
        return formatted_method

    def generate_get_all_method(self, resource_name: str) -> str:
        """Auto-Generate 'get_all' class Method [list API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted get_all Method template.
        """
        operation_name = "List" + resource_name + "s"
        operation_metadata = self.operations[operation_name]
        operation_input_shape_name = operation_metadata["input"]["shape"]

        operation = convert_to_snake_case(operation_name)

        get_list_operation_output_shape = self.operations[operation_name]["output"]["shape"]
        list_operation_output_members = self.shapes[get_list_operation_output_shape]["members"]

        filtered_list_operation_output_members = next(
            {key: value}
            for key, value in list_operation_output_members.items()
            if key != "NextToken"
        )

        summaries_key = next(iter(filtered_list_operation_output_members))
        summaries_shape_name = filtered_list_operation_output_members[summaries_key]["shape"]

        summary_name = self.shapes[summaries_shape_name]["member"]["shape"]
        summary_members = self.shapes[summary_name]["members"].keys()

        get_operation = self.operations["Describe" + resource_name]
        get_operation_input_shape = get_operation["input"]["shape"]
        get_operation_required_input = self.shapes[get_operation_input_shape].get("required", [])

        custom_key_mapping_str = ""
        if all(member not in summary_members for member in get_operation_required_input):
            if "MonitoringJobDefinitionSummary" == summary_name:
                custom_key_mapping = {
                    "monitoring_job_definition_name": "job_definition_name",
                    "monitoring_job_definition_arn": "job_definition_arn",
                }
                custom_key_mapping_str = f"custom_key_mapping = {json.dumps(custom_key_mapping)}"
                custom_key_mapping_str = add_indent(custom_key_mapping_str, 4)
            else:
                log.warning(
                    f"Resource {resource_name} summaries do not have required members to create object instance. Resource may require custom key mapping for get_all().\n"
                    f"List {summary_name} Members: {summary_members}, Object Required Members: {get_operation_required_input}"
                )
                return ""

        resource_iterator_args_list = [
            "client=client",
            f"list_method='{operation}'",
            f"summaries_key='{summaries_key}'",
            f"summary_name='{summary_name}'",
            f"resource_cls={resource_name}",
        ]

        if custom_key_mapping_str:
            resource_iterator_args_list.append(f"custom_key_mapping=custom_key_mapping")

        exclude_list = ["next_token", "max_results"]
        get_all_args = self._generate_method_args(operation_input_shape_name, exclude_list)

        if not get_all_args.strip().strip(","):
            resource_iterator_args = ",\n".join(resource_iterator_args_list)
            resource_iterator_args = add_indent(resource_iterator_args, 8)

            formatted_method = GET_ALL_METHOD_NO_ARGS_TEMPLATE.format(
                service_name="sagemaker",
                resource=resource_name,
                operation=operation,
                custom_key_mapping=custom_key_mapping_str,
                resource_iterator_args=resource_iterator_args,
            )
            return formatted_method

        operation_input_args = self._generate_operation_input_args(
            operation_metadata, is_class_method=True, exclude_list=exclude_list
        )

        resource_iterator_args_list.append("list_method_kwargs=operation_input_args")
        resource_iterator_args = ",\n".join(resource_iterator_args_list)
        resource_iterator_args = add_indent(resource_iterator_args, 8)

        formatted_method = GET_ALL_METHOD_WITH_ARGS_TEMPLATE.format(
            service_name="sagemaker",
            resource=resource_name,
            get_all_args=get_all_args,
            operation_input_args=operation_input_args,
            custom_key_mapping=custom_key_mapping_str,
            resource_iterator_args=resource_iterator_args,
        )
        return formatted_method

    def generate_config_schema(self):
        """
        Generates the Config Schema that is used by json Schema to validate config jsons .
        This function creates a python file with a variable that is consumed in the scripts to further fetch configs.

        Input for generating the Schema is the service JSON that is already loaded in the class

        """
        self.resources_extractor = ResourcesExtractor()
        self.resources_plan = self.resources_extractor.get_resource_plan()

        resource_properties = {}

        for _, row in self.resources_plan.iterrows():
            resource_name = row["resource_name"]
            # Get the operation and shape for the 'get' method
            if self._is_get_in_class_methods(row["class_methods"]):
                get_operation = self.operations["Describe" + resource_name]
                get_operation_shape = get_operation["output"]["shape"]

                # Generate the class attributes based on the shape
                class_attributes = self.shapes_extractor.generate_shape_members(get_operation_shape)
                cleaned_class_attributes = self._cleanup_class_attributes_types(class_attributes)
                resource_name = row["resource_name"]

                if default_attributes := self._get_dict_with_default_configurable_attributes(
                    cleaned_class_attributes
                ):
                    resource_properties[resource_name] = {
                        TYPE: OBJECT,
                        PROPERTIES: default_attributes,
                    }

        combined_config_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            TYPE: OBJECT,
            PROPERTIES: {
                SCHEMA_VERSION: {
                    TYPE: "string",
                    "enum": ["1.0"],
                    "description": "The schema version of the document.",
                },
                SAGEMAKER: {
                    TYPE: OBJECT,
                    PROPERTIES: {
                        PYTHON_SDK: {
                            TYPE: OBJECT,
                            PROPERTIES: {
                                RESOURCES: {
                                    TYPE: OBJECT,
                                    PROPERTIES: resource_properties,
                                }
                            },
                            "required": [RESOURCES],
                        }
                    },
                    "required": [PYTHON_SDK],
                },
            },
            "required": [SAGEMAKER],
        }

        output = f"{GENERATED_CLASSES_LOCATION}/{CONFIG_SCHEMA_FILE_NAME}"
        # Open the output file
        with open(output, "w") as file:
            # Generate and write the license to the file
            file.write(
                f"SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA = {json.dumps(combined_config_schema, indent=4)}"
            )

    def _cleanup_class_attributes_types(self, class_attributes: dict) -> dict:
        """
        Helper function that creates a direct mapping of attribute to type without default parameters assigned and without Optionals
        Args:
            class_attributes: attributes of the class in raw form

        Returns:
            class attributes that have a direct mapping and can be used for processing

        """
        cleaned_class_attributes = {}
        for key, value in class_attributes.items():
            new_val = value.split("=")[0].strip()
            if new_val.startswith("Optional"):
                new_val = new_val.replace("Optional[", "")[:-1]
            cleaned_class_attributes[key] = new_val
        return cleaned_class_attributes

    def _get_dict_with_default_configurable_attributes(self, class_attributes: dict) -> dict:
        """
        Creates default attributes dict for a particular resource.
        Iterates through all class attributes and filters by attributes that have particular substrings in their name
        Args:
            class_attributes: Dict that has all the attributes of a class

        Returns:
            Dict with attributes that can be configurable

        """
        PYTHON_TYPES = ["str", "datetime.datetime", "bool", "int", "float"]
        default_attributes = {}
        for key, value in class_attributes.items():
            if value in PYTHON_TYPES or value.startswith("List"):
                for config_attribute_substring in CONFIGURABLE_ATTRIBUTE_SUBSTRINGS:
                    if config_attribute_substring in key:
                        if value.startswith("List"):
                            element = value.replace("List[", "")[:-1]
                            if element in PYTHON_TYPES:
                                default_attributes[key] = {
                                    TYPE: "array",
                                    "items": {
                                        TYPE: self._get_json_schema_type_from_python_type(element)
                                    },
                                }
                        else:
                            default_attributes[key] = {
                                TYPE: self._get_json_schema_type_from_python_type(value) or value
                            }
            elif value.startswith("List") or value.startswith("Dict"):
                log.info("Script does not currently support list of objects as configurable")
                continue
            else:
                class_attributes = self.shapes_extractor.generate_shape_members(value)
                cleaned_class_attributes = self._cleanup_class_attributes_types(class_attributes)
                if nested_default_attributes := self._get_dict_with_default_configurable_attributes(
                    cleaned_class_attributes
                ):
                    default_attributes[key] = nested_default_attributes

        return default_attributes

    def _get_json_schema_type_from_python_type(self, python_type) -> str:
        """
        Helper for generating Schema
        Converts Python Types to JSON Schema compliant string
        Args:
            python_type: Type as a string

        Returns:
            JSON Schema compliant type
        """
        if python_type.startswith("List"):
            return "array"
        return PYTHON_TYPES_TO_BASIC_JSON_TYPES.get(python_type, None)

    @staticmethod
    def _is_get_in_class_methods(class_methods) -> bool:
        """
        Helper to check if class methods contain Get
        Args:
            class_methods: list of methods

        Returns:
            True if 'get' in list , else False
        """
        return "get" in class_methods

    @staticmethod
    @lru_cache(maxsize=None)
    def _get_config_schema_for_resources():
        """
        Fetches Schema JSON for all resources from generated file
        """
        return SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA[PROPERTIES][SAGEMAKER][PROPERTIES][PYTHON_SDK][
            PROPERTIES
        ][RESOURCES][PROPERTIES]
