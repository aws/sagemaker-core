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
import json
import os

from constants import BASIC_JSON_TYPES_TO_PYTHON_TYPES, \
                        GENERATED_CLASSES_LOCATION, \
                        RESOURCES_CODEGEN_FILE_NAME, \
                        LICENCES_STRING
from src.util.util import add_indent, convert_to_snake_case
from resources_extractor import ResourcesExtractor
from shapes_extractor import ShapesExtractor
from templates import GET_METHOD_TEMPLATE

class ResourcesCodeGen():
    """
    A class for generating resources based on a service JSON file.

    Args:
        file_path (str): The path to the service JSON file.

    Attributes:
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

    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.service_json = json.load(file)

        self.version = self.service_json['metadata']['apiVersion']
        self.protocol = self.service_json['metadata']['protocol']
        self.service = self.service_json['metadata']['serviceFullName']
        self.service_id = self.service_json['metadata']['serviceId']
        self.uid = self.service_json['metadata']['uid']
        self.operations = self.service_json['operations']
        self.shapes = self.service_json['shapes']

        if self.service_id != 'SageMaker':
            raise Exception(f"ServiceId {self.service_id} not supported in this resource generator")
        
        if self.protocol != 'json':
            raise Exception(f"Protocol {self.protocol} not supported in this resource generator")
    
        # Extract resources and its actions (aka resource plan) in dataframe format
        self.resources_extractor = ResourcesExtractor(self.service_json)
        self.resources_plan = self.resources_extractor.get_resource_plan()

        self.shapes_extractor = ShapesExtractor(self.service_json)
        self.shape_dag = self.shapes_extractor.get_shapes_dag()

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
        imports = "import datetime\n"
        # TODO: used for debugging remove in the final code
        imports += "import pprint\n"
        imports += "import boto3\n"
        imports += "\n"
        imports += "from pydantic import BaseModel\n"
        imports += "from typing import List, Dict, Optional\n"
        imports += "from boto3.session import Session\n"
        imports += "from utils import Unassigned\n"
        imports += "from shapes import *\n"
        imports += "\n\n"
        return imports

    def generate_resources(self, 
                           output_folder=GENERATED_CLASSES_LOCATION,
                           file_name=RESOURCES_CODEGEN_FILE_NAME) -> None:
        """
        Generate the resources file.

        Args:
            output_folder (str, optional): The output folder path. Defaults to "GENERATED_CLASSES_LOCATION".

        """
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        output_file = os.path.join(output_folder, file_name)
        
        with open(output_file, "w") as file:
            license = self.generate_license()
            file.write(license)
            imports = self.generate_imports()
            file.write(imports)

            for index, row in self.resources_plan.iterrows():
                resource_name = row['resource_name']
                class_methods = row['class_methods']
                object_methods = row['object_methods']
                additional_methods = row['additional_methods']
                raw_actions = row['raw_actions']

                resource_class = self.generate_resource_class(resource_name, 
                                                              class_methods, 
                                                              object_methods, 
                                                              additional_methods, 
                                                              raw_actions)
                
                if resource_class:
                    file.write(resource_class)
                    file.write("\n\n")

    def generate_resource_class(self, 
                                resource_name: str, 
                                class_methods: list, 
                                object_methods: list, 
                                additional_methods: list, 
                                raw_actions: list) -> str:
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
        class_attributes = self.generate_class_and_object_attributes(resource_name=resource_name,
                                                                     class_methods=class_methods)
        init_method = self.generate_init_method(resource_name)
        class_methods = self.generate_class_methods(class_methods)
        object_methods = self.generate_object_methods(object_methods)
        additional_methods = self.generate_additional_methods(additional_methods)

        resource_class = class_attributes
        # resource_class += class_methods
        # resource_class += object_methods
        # resource_class += additional_methods
        # resource_class += raw_actions

        return resource_class
    
    def generate_class_and_object_attributes(self, 
                                             resource_name: str, 
                                             class_methods: list) -> str:
        resource_class = ""
        if 'get' in class_methods:
            resource_class = f"class {resource_name}(BaseModel):\n"
            get_operation = self.operations["Describe" + resource_name]
            get_operation_shape = get_operation["output"]["shape"]

            init_data = self.shapes_extractor.generate_data_shape_members(get_operation_shape)
            get_method = self.generate_get_method(resource_name)
            try:
                resource_class += add_indent(init_data, 4)
                resource_class += "\n"
                resource_class += add_indent(get_method, 4)
            except Exception:
                print("DEBUG HELP\n", init_data)
                raise

        else:
            print(f"Resource {resource_name} does not have a GET method")

        return resource_class
    
    def generate_class_attributes(self, resource_name: str) -> str:
        pass
    
    def generate_class_methods(self, class_methods: list) -> str:
        pass

    def generate_object_methods(self, object_methods: list) -> str:
        pass

    def generate_additional_methods(self, additional_methods: list) -> str:
        pass

    def generate_init_method(self, resource_name: str) -> str:
        """
        Generate the __init__ method for a resource class.

        Args:
            row (Series): The row containing the resource information.

        """
        pass

    def generate_get_method(self, resource_name) -> str:
        """
        Auto-generate the GET method (describe API) for a resource.

        Args:
            resource (str): The resource name.

        Returns:
            str: The formatted Get Method template.

        """
        resource_operation = self.operations["Describe" + resource_name]
        resource_operation_input_shape_name = resource_operation["input"]["shape"]
        resource_operation_output_shape_name = resource_operation["output"]["shape"]
        describe_args = ""
        typed_shape_members = self.shapes_extractor.generate_shape_members(resource_operation_input_shape_name)
        for attr, type in typed_shape_members.items():
            describe_args += f"{attr}: {type},\n"
        # remove the last \n
        describe_args = describe_args.rstrip("\n")
        resource_lower = convert_to_snake_case(resource_name)

        input_shape_members = self.shapes[resource_operation_input_shape_name]["members"].keys()

        operation_input_args = {}
        for member in input_shape_members:
            operation_input_args[member] = convert_to_snake_case(member)

        operation = convert_to_snake_case("Describe" + resource_name)

        # ToDo: The direct assignments would be replaced by multi-level deserialization logic.
        object_attribute_assignments = ""
        output_shape_members = self.shapes[resource_operation_output_shape_name]["members"]
        for member in output_shape_members.keys():
            attribute_from_member = convert_to_snake_case(member)
            object_attribute_assignments += f"{resource_lower}.{attribute_from_member} = response[\"{member}\"]\n"
        object_attribute_assignments = add_indent(object_attribute_assignments, 4)

        formatted_method = GET_METHOD_TEMPLATE.format(
            describe_args=describe_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            object_attribute_assignments=object_attribute_assignments,
        )
        return formatted_method
    
    def get_attributes_and_its_type(self, row) -> dict:
        """
        Get the attributes and their types for a resource.

        Args:
            row (Series): The row containing the resource information.

        Returns:
            dict: The attributes and their types.

        """
        pass


if __name__ == "__main__":
    file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
    resource_generator = ResourcesCodeGen(file_path)
