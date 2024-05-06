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
import os

from src.tools.constants import GENERATED_CLASSES_LOCATION, \
                        RESOURCES_CODEGEN_FILE_NAME, \
                        LICENCES_STRING, \
                        TERMINAL_STATES, \
                        BASIC_IMPORTS_STRING, \
                        LOGGER_STRING
from src.util.util import add_indent, convert_to_snake_case, snake_to_pascal
from src.tools.resources_extractor import ResourcesExtractor
from src.tools.shapes_extractor import ShapesExtractor
from src.tools.templates import CREATE_METHOD_TEMPLATE, \
    GET_METHOD_TEMPLATE, REFRESH_METHOD_TEMPLATE, \
    RESOURCE_BASE_CLASS_TEMPLATE, \
    STOP_METHOD_TEMPLATE, DELETE_METHOD_TEMPLATE, \
    WAIT_METHOD_TEMPLATE, WAIT_FOR_STATUS_METHOD_TEMPLATE

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


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
        metadata = self.service_json['metadata']
        self.version = metadata['apiVersion']
        self.protocol = metadata['protocol']
        self.service = metadata['serviceFullName']
        self.service_id = metadata['serviceId']
        self.uid = metadata['uid']

        # Check if the service ID and protocol are supported
        if self.service_id != 'SageMaker':
            raise Exception(f"ServiceId {self.service_id} not supported in this resource generator")
        if self.protocol != 'json':
            raise Exception(f"Protocol {self.protocol} not supported in this resource generator")

        # Extract the operations and shapes
        self.operations = self.service_json['operations']
        self.shapes = self.service_json['shapes']

        # Initialize the resources and shapes extractors
        self.resources_extractor = ResourcesExtractor(service_json=service_json)
        self.shapes_extractor = ShapesExtractor(service_json=service_json)

        # Extract the resources plan and shapes DAG
        self.resources_plan = self.resources_extractor.get_resource_plan()

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
            "import boto3",
            "import time",
            "from pprint import pprint",
            "from pydantic import BaseModel, validate_call",
            "from typing import List, Dict, Optional, Literal",
            "from boto3.session import Session",
            "from .utils import SageMakerClient, Unassigned",
            "from .shapes import *",
            "\nfrom src.code_injection.codec import transform"
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

    def generate_resources(self,
                           output_folder=GENERATED_CLASSES_LOCATION,
                           file_name=RESOURCES_CODEGEN_FILE_NAME) -> None:
        """
        Generate the resources file.

        Args:
            output_folder (str, optional): The output folder path. Defaults to "GENERATED_CLASSES_LOCATION".
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
            
            # Iterate over the rows in the resources plan
            for _, row in self.resources_plan.iterrows():
                # Extract the necessary data from the row
                resource_name = row['resource_name']
                class_methods = row['class_methods']
                object_methods = row['object_methods']
                additional_methods = row['additional_methods']
                raw_actions = row['raw_actions']
                resource_status_chain = row['resource_status_chain']
                resource_states = row['resource_states']

                # Generate the resource class
                resource_class = self.generate_resource_class(resource_name, 
                                                              class_methods, 
                                                              object_methods, 
                                                              additional_methods, 
                                                              raw_actions,
                                                              resource_status_chain,
                                                              resource_states)
                
                # If the resource class was successfully generated, write it to the file
                if resource_class:
                    file.write(f"{resource_class}\n\n")

    def _evaluate_method(self, resource_name, method_name, methods):
        """Evaluate the specified method for a resource.

        Args:
            resource_name (str): The name of the resource.
            method_name (str): The name of the method to evaluate.
            methods (list): The list of methods for the resource.

        Returns:
            str: Formatted method if needed for a resource, else returns an empty string.
        """
        if method_name in methods:
            return getattr(self, f"generate_{method_name}_method")(resource_name)
        else:
            log.warning(f"Resource {resource_name} does not have a {method_name.upper()} method")
            return ""
    
    def generate_resource_class(self, 
                                resource_name: str, 
                                class_methods: list, 
                                object_methods: list, 
                                additional_methods: list, 
                                raw_actions: list,
                                resource_status_chain: list,
                                resource_states: list) -> str:
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
        if 'get' in class_methods:
            # Start defining the class
            resource_class = f"class {resource_name}(Base):\n"

            # Get the operation and shape for the 'get' method
            get_operation = self.operations["Describe" + resource_name]
            get_operation_shape = get_operation["output"]["shape"]

            # Generate the class attributes based on the shape
            class_attributes = self.shapes_extractor.generate_data_shape_members(get_operation_shape)

            # Generate the 'get' method
            get_method = self.generate_get_method(resource_name)

            try:
                # Add the class attributes and methods to the class definition
                resource_class += add_indent(class_attributes, 4)

                if create_method := self._evaluate_method(resource_name, "create", class_methods):
                    resource_class += add_indent(create_method, 4)

                resource_class += add_indent(get_method, 4)

                if refresh_method := self._evaluate_method(resource_name, "refresh", object_methods):
                    resource_class += add_indent(refresh_method, 4)

                if delete_method := self._evaluate_method(resource_name, "delete", object_methods):
                    resource_class += add_indent(delete_method, 4)

                if stop_method := self._evaluate_method(resource_name, "stop", object_methods):
                    resource_class += add_indent(stop_method, 4)
                
                if wait_method := self._evaluate_method(resource_name, "wait", object_methods):
                    resource_class += add_indent(wait_method, 4)
                    
                if wait_for_status_method := self._evaluate_method(resource_name, "wait_for_status", object_methods):
                    resource_class += add_indent(wait_for_status_method, 4)
                                        
            except Exception:
                # If there's an error, log the class attributes for debugging and raise the error
                log.error(f"DEBUG HELP {class_attributes} \n {create_method} \n {get_method} \n"
                          f"{refresh_method}")
                raise
        else:
            # If there's no 'get' method, log a message
            # TODO: Handle the resources without 'get' differently
            log.warning(f"Resource {resource_name} does not have a GET method")

        # Return the class definition
        return resource_class

    def _generate_operation_input_args(self, resource_operation, is_class_method):
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
            args = (f"'{member}': {convert_to_snake_case(member)}"
            for member in input_shape_members)
        else:
            args = (f"'{member}': self.{convert_to_snake_case(member)}"
                    for member in input_shape_members)

        operation_input_args = ",\n".join(args)
        operation_input_args += ","
        operation_input_args = add_indent(operation_input_args, 8)

        return operation_input_args

    def generate_create_method(self, resource_name) -> str:
        """
        Auto-generate the CREATE method for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Create Method template.

        """
        # Get the operation and shape for the 'create' method
        operation_name = "Create" + resource_name
        operation = self.operations[operation_name]
        operation_input_shape_name = operation["input"]["shape"]

        # Generate the arguments for the 'create' method
        typed_shape_members = self.shapes_extractor.generate_shape_members(operation_input_shape_name)
        create_args = ",\n".join(f"{attr}: {type}" for attr, type in typed_shape_members.items())
        create_args += ","
        create_args = add_indent(create_args)

        # Convert the resource name to snake case
        resource_lower = convert_to_snake_case(resource_name)

        operation_input_args = self._generate_operation_input_args(
            operation, is_class_method=True
        )

        # Convert the operation name to snake case
        operation = convert_to_snake_case(operation_name)

        # Initialize an empty string for the object attribute assignments
        object_attribute_assignments = ""

        # Check if the operation has an 'output'
        if "output" in operation:
            # Get the shape for the operation output
            operation_output_shape_name = operation["output"]["shape"]
            output_shape_members = self.shapes[operation_output_shape_name]["members"]

            # Generate the object attribute assignments
            for member in output_shape_members.keys():
                attribute_from_member = convert_to_snake_case(member)
                object_attribute_assignments += f"{resource_lower}.{attribute_from_member} = response[\"{member}\"]\n"

            # Add indentation to the object attribute assignments
            object_attribute_assignments = add_indent(object_attribute_assignments, 4)

        # Get the identifier(s)
        describe_operation = self.operations["Describe" + resource_name]
        describe_operation_input_shape_name = describe_operation["input"]["shape"]

        required_members = self.shapes_extractor.get_required_members(
            describe_operation_input_shape_name
        )

        create_required_members = self.shapes_extractor.get_required_members(
            operation_input_shape_name
        )

        identifiers = []
        for member in required_members:
            if member not in create_required_members:
                identifiers.append(f"{member}=response[\'{snake_to_pascal(member)}\']")
            else:
                identifiers.append(f"{member}={member}")

        resource_identifier = ", ".join(identifiers)

        # Format the method using the CREATE_METHOD_TEMPLATE
        formatted_method = CREATE_METHOD_TEMPLATE.format(
            create_args=create_args,
            service_name='sagemaker', # TODO: change service name based on the service - runtime, sagemaker, etc.
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            object_attribute_assignments=object_attribute_assignments,
            resource_identifier=resource_identifier,
        )

        # Return the formatted method
        return formatted_method
    
    def generate_get_method(self, resource_name) -> str:
        """
        Auto-generate the GET method (describe API) for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted Get Method template.

        """
        operation_name = "Describe" + resource_name
        resource_operation = self.operations[operation_name]
        resource_operation_input_shape_name = resource_operation["input"]["shape"]
        resource_operation_output_shape_name = resource_operation["output"]["shape"]

        operation_input_args = self._generate_operation_input_args(
            resource_operation, is_class_method=True
        )

        typed_shape_members = self.shapes_extractor.generate_shape_members(
            resource_operation_input_shape_name
        )

        describe_args = ",\n".join(f"{attr}: {type}" for attr, type in typed_shape_members.items())
        describe_args += ","
        describe_args = add_indent(describe_args)

        resource_lower = convert_to_snake_case(resource_name)

        operation = convert_to_snake_case(operation_name)

        formatted_method = GET_METHOD_TEMPLATE.format(
            service_name='sagemaker', # TODO: change service name based on the service - runtime, sagemaker, etc.
            describe_args=describe_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            describe_operation_output_shape=resource_operation_output_shape_name,
        )
        return formatted_method

    def generate_refresh_method(self, resource_name):
        """Auto-Generate 'refresh' object Method [describe API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted refresh Method template.
        """
        operation_name = "Describe" + resource_name
        resource_operation = self.operations[operation_name]
        resource_operation_output_shape_name = resource_operation["output"]["shape"]

        operation_input_args = self._generate_operation_input_args(
            resource_operation, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = REFRESH_METHOD_TEMPLATE.format(
            operation_input_args=operation_input_args,
            operation=operation,
            describe_operation_output_shape=resource_operation_output_shape_name,
        )
        return formatted_method

    def generate_delete_method(self, resource_name):
        """Auto-Generate 'delete' object Method [delete API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted delete Method template.
        """
        operation_name = "Delete" + resource_name
        resource_operation = self.operations[operation_name]

        operation_input_args = self._generate_operation_input_args(
            resource_operation, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = DELETE_METHOD_TEMPLATE.format(
            operation_input_args=operation_input_args,
            operation=operation,
        )
        return formatted_method

    def generate_stop_method(self, resource_name):
        """Auto-Generate 'stop' object Method [delete API] for a resource.

        Args:
            resource_name (str): The resource name.

        Returns:
            str: The formatted stop Method template.
        """
        operation_name = "Stop" + resource_name
        resource_operation = self.operations[operation_name]

        operation_input_args = self._generate_operation_input_args(
            resource_operation, is_class_method=False
        )

        operation = convert_to_snake_case(operation_name)

        formatted_method = STOP_METHOD_TEMPLATE.format(
            operation_input_args=operation_input_args,
            operation=operation,
        )
        return formatted_method
    
    def generate_wait_method(self, resource_name) -> str:
        """Auto-Generate WAIT Method for a waitable resource.

        Args:
            resource_name (str): The resource name.
            
        Returns:
            str: The formatted Wait Method template.

        """
        resource_status_chain, resource_states = self.resources_extractor.get_status_chain_and_states(resource_name)
        
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


        formatted_method = WAIT_METHOD_TEMPLATE.format(
            terminal_resource_states=terminal_resource_states,
            status_key_path=status_key_path
        )
        return formatted_method
    
    def generate_wait_for_status_method(self, resource_name) -> str:
        """Auto-Generate WAIT_FOR_STATUS Method for a waitable resource.

        Args:
            resource_name (str): The resource name.
            
        Returns:
            str: The formatted wait_for_status Method template.

        """
        resource_status_chain, resource_states = self.resources_extractor.get_status_chain_and_states(resource_name)

        # Get resource status key path
        status_key_path = ""
        for member in resource_status_chain:
            status_key_path += f'.{convert_to_snake_case(member["name"])}'

        formatted_method = WAIT_FOR_STATUS_METHOD_TEMPLATE.format(
            resource_states=resource_states,
            status_key_path=status_key_path
        )
        return formatted_method
