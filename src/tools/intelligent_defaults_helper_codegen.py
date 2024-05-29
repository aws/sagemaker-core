import os
from src.tools.constants import (
    GENERATED_CLASSES_LOCATION,
    INTELLIGENT_DEFAULTS_HELPER_CODEGEN_FILE_NAME,
    LICENCES_STRING,
    BASIC_IMPORTS_STRING,
    LOGGER_STRING,
)
from src.tools.templates import (
    LOAD_DEFAULT_CONFIGS_AND_HELPERS_TEMPLATE,
    LOAD_CONFIG_VALUES_FOR_RESOURCE_TEMPLATE,
    GET_CONFIG_VALUE_TEMPLATE,
)


class IntelligentDefaultsHelperCodeGen:
    """
    Code generator for IntelligentDefaultsHelper
    """

    def generate_helper_functions(
        self,
        output_folder=GENERATED_CLASSES_LOCATION,
        file_name=INTELLIGENT_DEFAULTS_HELPER_CODEGEN_FILE_NAME,
    ):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_file = os.path.join(output_folder, file_name)

        with open(output_file, "w") as file:
            license = self.generate_license()
            file.write(license)
            imports = self.generate_imports()
            file.write(imports)
            logging = self.generate_logging()
            file.write(logging)

            file.write(LOAD_DEFAULT_CONFIGS_AND_HELPERS_TEMPLATE)
            file.write("\n\n")
            file.write(LOAD_CONFIG_VALUES_FOR_RESOURCE_TEMPLATE)
            file.write("\n\n")
            file.write(GET_CONFIG_VALUE_TEMPLATE)
            file.write("\n\n")

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
        imports = [
            BASIC_IMPORTS_STRING,
            "import os",
            "from platformdirs import site_config_dir, user_config_dir",
            "import jsonschema",
            "from functools import lru_cache",
            "from .shapes import *",
            "from .config_schema import SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA",
            "from botocore.utils import merge_dicts",
            "import boto3",
            "from six.moves.urllib.parse import urlparse",
            "from typing import List",
            "import yaml",
            "import pathlib",
        ]
        formated_imports = "\n".join(imports)
        formated_imports += "\n\n"
        return formated_imports

    def generate_logging(self) -> str:
        """
        Generate the logging statements for the generated resources file.

        Returns:
            str: The logging statements.

        """
        return LOGGER_STRING
