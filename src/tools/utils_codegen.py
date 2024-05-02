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
import os
import textwrap

from src.tools.constants import GENERATED_CLASSES_LOCATION, \
    UTILS_CODEGEN_FILE_NAME, LICENCES_STRING

class UtilsCodeGen:

    def generate_utils(self, 
                       output_folder=GENERATED_CLASSES_LOCATION, 
                       file_name=UTILS_CODEGEN_FILE_NAME) -> None:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        output_file = os.path.join(output_folder, file_name)
        
        with open(output_file, "w") as file:
            license = self.generate_license()
            file.write(license)
            imports = self.generate_imports()
            file.write(imports)
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
            file.write("\n\n")

            # add Singleton class
            client = self.generate_client()
            file.write(client)
            file.write("\n\n")

    def generate_client(self) -> str:
        """
        Generate the singleton sagemaker client.

        Returns:
            str: The singleton sagemaker client.

        """
        client = '''\
        class SageMakerClient:
            _instance = None

            @staticmethod
            def getInstance():
                if SageMakerClient._instance == None:
                    SageMakerClient()
                return SageMakerClient._instance

            def __init__(self, session=None, region_name='us-west-2', service_name='sagemaker'):
                if SageMakerClient._instance != None:
                    raise Exception("This class is a singleton!")
                else:
                    if session is None:
                        session = boto3.Session(region_name=region_name)
                    SageMakerClient._instance = session.client(service_name)
        '''
        wrapped_client = textwrap.indent(textwrap.dedent(client),
                                                             prefix='')
        return wrapped_client
    
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
        imports += "import boto3\n"
        imports += "\n"
        imports += "from pydantic import BaseModel\n"
        imports += "from typing import Optional\n"
        imports += "\n\n"
        return imports