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

from src.tools.constants import BASIC_IMPORTS_STRING, GENERATED_CLASSES_LOCATION, \
    UTILS_CODEGEN_FILE_NAME, LICENCES_STRING, LOGGER_STRING

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
            logger = self.generate_logging()
            file.write(logger)
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
        class SingletonMeta(type):
            """
            Singleton metaclass. Ensures that a single instance of a class using this metaclass is created.
            """
            _instances = {}

            def __call__(cls, *args, **kwargs):
                """
                Overrides the call method to return an existing instance of the class if it exists,
                or create a new one if it doesn't.
                """
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
                return cls._instances[cls]


        class SageMakerClient(metaclass=SingletonMeta):
            """
            A singleton class for creating a SageMaker client.
            """
            def __init__(self, session: Session, region_name: str, service_name='sagemaker'):
                """
                Initializes the SageMakerClient with a boto3 session, region name, and service name.
                Creates a boto3 client using the provided session, region, and service.
                """
                if session is None:
                    logger.warning("No boto3 session provided. Creating a new session.")
                    session = Session()

                if region_name is None:
                    logger.warning("No region provided. Using default region.")
                    region = session.region_name

                self.session = session
                self.region_name = region_name
                self.service_name = service_name
                self.client = session.client(service_name, region_name)
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
        imports = BASIC_IMPORTS_STRING
        imports += "\n"
        imports += "from boto3.session import Session\n"
        imports += "\n"
        return imports
    
    def generate_logging(self) -> str:
        """
        Generate the logging statements for the generated resources file.

        Returns:
            str: The logging statements.

        """
        return LOGGER_STRING