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
"""Utility module for common utility methods."""
import re
import subprocess


def add_indent(text, num_spaces=4):
    """
    Add customizable indent spaces to a given text.

    Parameters:
        text (str): The text to which the indent spaces will be added.
        num_spaces (int): Number of spaces to be added for each level of indentation. Default is 4.

    Returns:
        str: The text with added indent spaces.
    """
    indent = " " * num_spaces
    lines = text.split("\n")
    indented_text = "\n".join(indent + line for line in lines)
    return indented_text.rstrip(" ")


def clean_documentaion(documentation):
    documentation = re.sub(r"<\/?p>", "", documentation)
    documentation = re.sub(r"<\/?code>", "'", documentation)
    return documentation


def convert_to_snake_case(entity_name):
    """
    Convert a string to snake_case.

    Args:
        entity_name (str): The string to convert.

    Returns:
        str: The converted string in snake_case.
    """
    snake_case_string = re.sub(r"(?<!^)(?=[A-Z])", "_", entity_name).lower()
    return snake_case_string


def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
    components = snake_str.split("_")
    return "".join(x.title() for x in components[0:])


def reformat_file_with_black(filename):
    try:
        # Run black with specific options using subprocess
        subprocess.run(["black", "-l", "100", filename], check=True)
        print(f"File '{filename}' reformatted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while reformatting '{filename}': {e}")
