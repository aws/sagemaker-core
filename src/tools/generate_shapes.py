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
"""A class for generating class structure from Service Model JSON.

To run the script be sure to set the PYTHONPATH
export PYTHONPATH=<sagemaker-code-gen repo directory>:$PYTHONPATH
"""
import json
import os
import textwrap

from src.tools.generator import Generator
from src.util.util import add_indent


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


class ShapeGenerator(Generator):
    """Builds the pythonic structure from an input Botocore service.json"""

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
                        # evaluate the member shape and then append to node deps
                        member_shape = shapes_dict[member_attributes["shape"]]
                        if member_shape["type"] == "list":
                            node_deps.append(member_shape["member"]["shape"])
                        elif member_shape["type"] == "map":
                            node_deps.append(member_shape["key"]["shape"])
                            node_deps.append(member_shape["value"]["shape"])
                        else:
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

    def generate_data_class_for_shape(self, shape):
        class_name = shape
        init_data = self.generate_data_shape_members(shape)
        try:
            data_class_members = add_indent(init_data, 4)
        except Exception:
            print("DEBUG HELP\n", init_data)
            raise
        return DATA_CLASS_TEMPLATE.format(
            class_name=class_name + "(Base)",
            data_class_members=data_class_members,
            docstring="TBA",
        )

    def generate_imports(self):
        imports = "import datetime\n"
        imports += "\n"
        imports += "from dataclasses import dataclass\n"
        imports += "from typing import List, Dict, Optional\n"
        imports += "\n"
        return imports

    def generate_base_class(self):
        # more customizations would be added later
        return CLASS_TEMPLATE.format(
            class_name="Base",
            init_method_body=add_indent("pass", 4),
            docstring="TBA",
        )

    def _filter_input_output_shapes(self, shape):
        """Filter Operation Input Output shapes, to not generate Shape Classes"""

        operation_input_output_shapes = []
        for operation, attrs in self.service_json["operations"].items():
            if attrs.get("input"):
                operation_input_output_shapes.append(attrs["input"]["shape"])
            if attrs.get("output"):
                operation_input_output_shapes.append(attrs["output"]["shape"])

        if shape in operation_input_output_shapes:
            return False
        return True

    def generate_shapes(self, output_folder="src/generated"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        #current_datetime = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_file = os.path.join(output_folder, f"shapes.py")

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
                if self._filter_input_output_shapes(shape):
                    shape_dict = self.service_json['shapes'][shape]
                    shape_type = shape_dict["type"]
                    if shape_type == "structure":
                        shape_class = self.generate_data_class_for_shape(shape)
                        file.write(shape_class)


with open('sample/sagemaker/2017-07-24/service-2.json') as f:
    data = json.load(f)

codegen = ShapeGenerator(service_json=data)

codegen.generate_shapes()
