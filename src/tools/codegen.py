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
"""Generates the code for the service model."""
import json
from src.tools.constants import SERVICE_JSON_FILE_PATH
from src.tools.utils_codegen import UtilsCodeGen
from src.tools.shapes_codegen import ShapesCodeGen
from src.tools.resources_codegen import ResourcesCodeGen

def generate_code() -> None:
    """
    Generates the code for the given code generators.

    Note ordering is important, generate the utils and lower level classes first
    then generate the higher level classes.

    Returns:
        None
    """
    
    # TODO: Inject service JSON file path & run through with all the sagemaker service JSON files
    with open(SERVICE_JSON_FILE_PATH, 'r') as file:
        service_json = json.load(file)
    
    utils_code_gen = UtilsCodeGen()
    shapes_code_gen = ShapesCodeGen(service_json=service_json)
    resources_code_gen = ResourcesCodeGen(service_json=service_json)

    utils_code_gen.generate_utils()
    shapes_code_gen.generate_shapes()
    resources_code_gen.generate_resources()

''' 
Initializes all the code generator classes and triggers generator.
'''
if __name__ == "__main__":
    generate_code()
