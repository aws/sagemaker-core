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
from constants import SERVICE_JSON_FILE_PATH
from utils_codegen import UtilsCodeGen
# TODO: shapes_codegen is failing with alias='json' error. Need to fix it.
#from shapes_codegen import ShapesCodeGen
from resources_codegen import ResourcesCodeGen

def generate_code(utils_code_gen: UtilsCodeGen, 
                  #shapes_code_gen: ShapesCodeGen,
                  resources_code_gen: ResourcesCodeGen) -> None:
    """
    Generates the code for the given code generators.

    Note ordering is important, generate the utils and lower level classes first
    then generate the higher level classes.

    Args:
        utils_code_gen (UtilsCodeGen): The code generator for utility classes.
        shapes_code_gen (ShapesCodeGen): The code generator for shape classes.
        resources_code_gen (ResourcesCodeGen): The code generator for resource classes.

    Returns:
        None
    """
    utils_code_gen.generate_utils()
    #shapes_code_gen.generate_shapes()
    resources_code_gen.generate_resources()

''' 
Initializes all the code generator classes and triggers generator.
'''
if __name__ == "__main__":
    # TODO: Inject service JSON file path & run through with all the sagemaker service JSON files
    utils_code_gen = UtilsCodeGen()
    #shapes_code_gen = ShapesCodeGen()
    resources_code_gen = ResourcesCodeGen(file_path=SERVICE_JSON_FILE_PATH)

    generate_code(utils_code_gen=utils_code_gen,
                  #shapes_code_gen=shapes_code_gen,
                  resources_code_gen=resources_code_gen)