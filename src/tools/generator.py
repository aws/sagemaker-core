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
"""Base class for common generator methods."""
from src.util.util import add_indent, convert_to_snake_case

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
}


class Generator:
    """Base class for common generator methods"""
    def __init__(self, service_json=None):
        """

        :param service_json: The Botocore Service Json in python dict format.
        """
        self.service_json = service_json

    def generate_data_shape_members(self, shape):
        shape_dict = self.service_json['shapes'][shape]
        members = shape_dict["members"]
        required_args = shape_dict.get("required", [])
        init_data_body = ""
        # bring the required members in front
        ordered_members = {key: members[key] for key in required_args if key in members}
        ordered_members.update(members)
        for member_name, member_attrs in ordered_members.items():
            member_shape = member_attrs["shape"]
            if self.service_json["shapes"][member_shape]:
                member_shape_type = self.service_json["shapes"][member_shape]["type"]
                if member_shape_type == "structure":
                    member_type = member_shape
                else:
                    # Shape is a simple type like string
                    member_type = BASIC_JSON_TYPES_TO_PYTHON_TYPES[member_shape_type]
            else:
                raise Exception("The Shape definition mush exist. The Json Data might be corrupt")
            member_name_snake_case = convert_to_snake_case(member_name)
            if member_name in required_args:
                init_data_body += f"{member_name_snake_case}: {member_type}\n"
            else:
                if member_name_snake_case == "lambda":
                    # ToDo handle this edge case later
                    init_data_body += f"# {member_name_snake_case}: Optional[{member_type}] = Unassigned()\n"
                else:
                    init_data_body += f"{member_name_snake_case}: Optional[{member_type}] = Unassigned()\n"
        init_data = add_indent(init_data_body, 4)
        return init_data
