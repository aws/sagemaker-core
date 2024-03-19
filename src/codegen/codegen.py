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
"""A class for generating class structure from Service Model JSON."""
from __future__ import absolute_import

import datetime
import json
import os
import re


CLASS_TEMPLATE ='''
class {class_name}:
    """{docstring}"""
    {init_method_body}
'''

BASIC_JSON_TYPES_TO_PYTHON_TYPES = {
    "string": "str",
    "integer": "int",
    "boolean": "bool",
    "long": "int",
    "float": "float",
    "map": "dict",
    "double": "float",
    "list": "list",
    "timestamp": "datetime.datetime",
    "placeholder": "placeholder",  # To be removed after validation
}


def add_indent(text, num_spaces=4):
    """
    Add customizable indent spaces to a given text.

    Parameters:
        text (str): The text to which the indent spaces will be added.
        num_spaces (int): Number of spaces to be added for each level of indentation. Default is 4.

    Returns:
        str: The text with added indent spaces.
    """
    indent = ' ' * num_spaces
    lines = text.split('\n')
    indented_text = '\n'.join(indent + line for line in lines)
    return indented_text.rstrip(' ')


def clean_documentaion(documentation):
    documentation = re.sub(r'<\/?p>', '', documentation)
    documentation = re.sub(r'<\/?code>', "'", documentation)
    return documentation


def convert_to_snake_case(entity_name):
    """
    Convert a string to snake_case.

    Args:
        entity_name (str): The string to convert.

    Returns:
        str: The converted string in snake_case.
    """
    snake_case_string = re.sub(r'(?<!^)(?=[A-Z])', '_', entity_name).lower()
    return snake_case_string


class CodeGen:
    """Builds the pythonic structure from an input Botocore service.json"""

    def __init__(self, service_json=None):
        """

        :param service_json: The Botocore Service Json in python dict format.
        """
        self.service_json = service_json

    def build_graph(self):
        """Builds DAG for Service Json Shapes

        Steps:
        1. Loop over the Service Json shapes.
            1.1. If dependency(members) found, add association of node -> dependency.
                1.1.1. Sometimes members are not shape themselves, but have associated links to actual shapes.
                    In that case add link to node -> dependency (actual)
                        CreateExperimentRequest -> [ExperimentEntityName, ExperimentDescription, TagList]
            1.2. else leaf node found (no dependent members), add association of node -> None.

        :param data:
        :return: A dict which defines the structure of the DAG in the format:
            {key : [dependencies]}
            Example input:
                {'CreateExperimentRequest': ['ExperimentEntityName', 'ExperimentEntityName',
                    'ExperimentDescription', 'TagList'],
                'CreateExperimentResponse': ['ExperimentArn'],
                'DeleteExperimentRequest': ['ExperimentEntityName'],
                'DeleteExperimentResponse': ['ExperimentArn']}
        """
        graph = {}
        shapes_dict = self.service_json["shapes"]

        for node, attributes in shapes_dict.items():
            if "members" in attributes:
                for member, member_attributes in attributes["members"].items():
                    # add shapes and not shape attribute
                    # i.e. ExperimentEntityName taken over ExperimentName
                    if member_attributes["shape"] in shapes_dict.keys():
                        node_deps = graph.get(node, [])
                        node_deps.append(member_attributes["shape"])
                        graph[node] = node_deps
            else:
                graph[node] = None
        return graph

    def topological_sort(self):
        """Returns the topological sort of the DAG via depth-first-search traversal.

        :return:
        """
        graph = self.build_graph()
        visited = set()
        stack = []

        def dfs(node):
            visited.add(node)
            # unless leaf node is reached do dfs
            if graph.get(node) is not None:
                for neighbor in graph.get(node, []):
                    if neighbor not in visited:
                        dfs(neighbor)
            stack.append(node)

        for node in graph:
            if node not in visited:
                dfs(node)

        return stack

    def _generate_init_body_from_shape_members(self, shape):
        shape_dict = self.service_json['shapes'][shape]
        members = shape_dict["members"]
        required_args = shape_dict.get("required", [])
        init_arg_list = ""
        init_data_body = f"super().__init__(**kwargs)\n"
        for member_name, member_attrs in members.items():
            member_shape = member_attrs["shape"]
            if self.service_json["shapes"][member_shape]:
                member_shape_type = self.service_json["shapes"][member_shape]["type"]
                if member_shape_type == "structure":
                    member_type = member_shape
                else:
                    # Shape is a simple type like string
                    member_type = BASIC_JSON_TYPES_TO_PYTHON_TYPES[member_shape_type]
            else:
                member_type = "placeholder"
            member_name_snake_case = convert_to_snake_case(member_name)
            if member_name in required_args:
                init_arg_list += f"{member_name_snake_case}: {member_type} = None,\n"
                init_data_body += f"self.{member_name_snake_case} = {member_name_snake_case},\n"
            else:
                init_arg_list += f"{member_name_snake_case}: Optional[{member_type}] = None,\n"
                init_data_body += f"self.{member_name_snake_case} = {member_name_snake_case},\n"
        init_data = f"def __init__(\n"
        init_data += add_indent(f"self,\n{init_arg_list}**kwargs\n", 8)
        init_data += add_indent("):\n", 4)
        init_data += add_indent(init_data_body, 8)
        return init_data

    def generate_class_for_shape(self, shape):
        class_name = shape
        init_data = self._generate_init_body_from_shape_members(shape)
        return CLASS_TEMPLATE.format(
            class_name=class_name + "(Shape)",
            init_method_body=init_data,
            docstring="TBA",
        )

    def generate_imports(self):
        imports = "from typing import Optional\n"
        imports += "import datetime\n"
        imports += "\n"
        return imports

    def generate_base_class_for_shape(self):
        class_shape_init = "def __init__(self, **kwargs):\n"
        class_shape_init += add_indent("for key, value in kwargs.items():\n", 8)
        class_shape_init += add_indent("setattr(self, key, value)\n", 12)
        return CLASS_TEMPLATE.format(
            class_name="Shape",
            init_method_body=class_shape_init,
            docstring="TBA",
        )

    def generate_classes(self, output_folder="src/sagemaker-core"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_file = os.path.join(output_folder, f"generated_classes_{current_datetime}.py")

        with open(output_file, "w") as file:
            imports = self.generate_imports()
            file.write(imports)
            base_class = self.generate_base_class_for_shape()
            file.write(base_class)

            # iterate through shapes in topological order an generate classes.
            topological_order = self.topological_sort()
            for shape in topological_order:
                shape_dict = self.service_json['shapes'][shape]
                shape_type = shape_dict["type"]
                if shape_type == "structure":
                    shape_class = self.generate_class_for_shape(shape)
                    file.write(shape_class)


with open('src/codegen/experiments-sample.json') as f:
# with open('src/codegen/sagemaker-service.json') as f:
    data = json.load(f)

codegen = CodeGen(service_json=data)

codegen.generate_classes()
