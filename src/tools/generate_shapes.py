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
import json
import os
import re
import textwrap


CLASS_TEMPLATE ='''
class {class_name}:
    """{docstring}"""
{init_method_body}
'''

DATA_CLASS_TEMPLATE ='''
@dataclass
class {class_name}:
    """{docstring}"""
{data_class_members}
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


def filter_req_resp_shapes(shape):
    # OidcConfigForRequest, WorkforceVpcConfigRequest and WorkforceVpcConfigResponse
    # are valid Shape Structures with no associated operation
    # ToDo: need to make this list dynamically so that future instances are covered.
    # req_resp_list = []
    # for shape in data["shapes"].keys():
    #     if shape.endswith("Request") or shape.endswith("Response"):
    #         req_resp_list.append(shape)
    # req = [r.replace("Request", "") for r in req_resp_list if r.endswith("Request")]
    # resp = [r.replace("Response", "") for r in req_resp_list if r.endswith("Response")]
    # [r for r in resp if r not in data["operations"].keys()]
    # ['OidcConfigFor', 'WorkforceVpcConfig']
    # [r for r in req if r not in data["operations"].keys()]
    # ['WorkforceVpcConfig']
    if shape in ["OidcConfigForResponse", "WorkforceVpcConfigRequest", "WorkforceVpcConfigResponse"]:
        return True
    if shape.endswith("Request") or shape.endswith("Response"):
        return False
    return True


class ShapeGenerator:
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

    def _generate_data_shape_members(self, shape):
        shape_dict = self.service_json['shapes'][shape]
        members = shape_dict["members"]
        required_args = shape_dict.get("required", [])
        init_data_body = ""
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
                init_data_body += f"{member_name_snake_case}: {member_type}\n"
            else:
                init_data_body += f"{member_name_snake_case}: Optional[{member_type}] = Unassigned()\n"
        init_data = add_indent(init_data_body, 4)
        return init_data

    def generate_data_class_for_shape(self, shape):
        class_name = shape
        init_data = self._generate_data_shape_members(shape)
        return DATA_CLASS_TEMPLATE.format(
            class_name=class_name + "(Base)",
            data_class_members=init_data,
            docstring="TBA",
        )

    def generate_imports(self):
        imports = "import datetime\n"
        imports += "\n"
        imports += "from dataclasses import dataclass\n"
        imports += "from typing import Optional\n"
        imports += "\n"
        return imports

    def generate_base_class(self):
        # more customizations would be added later
        return CLASS_TEMPLATE.format(
            class_name="Base",
            init_method_body=add_indent("pass", 4),
            docstring="TBA",
        )

    def generate_shapes(self, output_folder="src/generated"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        #current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_file = os.path.join(output_folder, f"generate_shapes.py")

        with open(output_file, "w") as file:
            imports = self.generate_imports()
            file.write(imports)
            base_class = self.generate_base_class()
            file.write(base_class)
            file.write("\n\n")
            # add Unassigned class
            class_definition_string = '''\
            class Unassigned:
                """A custom type used to signify an undefined optional argument."""
                _instance = None

                def __new__(cls):
                    if cls._instance is None:
                        cls._instance = super().__new__(cls)
                    return cls._instance
            '''
            wrapped_class_definition = textwrap.indent(textwrap.dedent(class_definition_string),
                                                       prefix='')
            file.write(wrapped_class_definition)
            file.write("\n")
            # iterate through shapes in topological order an generate classes.
            topological_order = self.topological_sort()
            for shape in topological_order:
                if filter_req_resp_shapes(shape):
                    shape_dict = self.service_json['shapes'][shape]
                    shape_type = shape_dict["type"]
                    if shape_type == "structure":
                        shape_class = self.generate_data_class_for_shape(shape)
                        file.write(shape_class)


with open('src/tools/experiments-sample.json') as f:
#with open('../sample/sagemaker/2017-07-24/service-2.json') as f:
    data = json.load(f)

codegen = ShapeGenerator(service_json=data)

codegen.generate_shapes()
