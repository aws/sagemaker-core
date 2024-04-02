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

    def _evaluate_list_type(self, member_shape):
        list_shape_name = member_shape["member"]["shape"]
        list_shape_type = self.service_json["shapes"][list_shape_name]["type"]
        if list_shape_type in ["list", "map"]:
            raise Exception(
                "Unhandled list shape key type encountered, needs extra logic to handle this")
        if list_shape_type == "structure":
            # handling an edge case of nested structure
            if list_shape_name == "SearchExpression":
                member_type = f"List['{list_shape_name}']"
            else:
                member_type = f"List[{list_shape_name}]"
        else:
            member_type = f"List[{BASIC_JSON_TYPES_TO_PYTHON_TYPES[list_shape_type]}]"
        return member_type

    def _evaluate_map_type(self, member_shape):
        map_key_shape_name = member_shape["key"]["shape"]
        map_value_shape_name = member_shape["value"]["shape"]
        map_key_shape = self.service_json["shapes"][map_key_shape_name]
        map_value_shape = self.service_json["shapes"][map_value_shape_name]
        map_key_shape_type = map_key_shape["type"]
        map_value_shape_type = map_value_shape["type"]
        # Map keys are always expected to be "string" type
        if map_key_shape_type != "string":
            raise Exception(
                "Unhandled map shape key type encountered, needs extra logic to handle this")
        if map_value_shape_type == "structure":
            member_type = f"Dict[{BASIC_JSON_TYPES_TO_PYTHON_TYPES[map_key_shape_type]}, " \
                          f"{map_value_shape_name}]"
        elif map_value_shape_type == "list":
            member_type = f"Dict[{BASIC_JSON_TYPES_TO_PYTHON_TYPES[map_key_shape_type]}, " \
                          f"{self._evaluate_list_type(map_value_shape)}]"
        elif map_value_shape_type == "map":
            member_type = f"Dict[{BASIC_JSON_TYPES_TO_PYTHON_TYPES[map_key_shape_type]}, " \
                          f"{self._evaluate_map_type(map_value_shape)}]"
        else:
            member_type = f"Dict[{BASIC_JSON_TYPES_TO_PYTHON_TYPES[map_key_shape_type]}, " \
                          f"{BASIC_JSON_TYPES_TO_PYTHON_TYPES[map_value_shape_type]}]"
        return member_type

    def generate_data_shape_members(self, shape):
        shape_members = self.generate_shape_members(shape)
        init_data_body = ""
        for attr, value in shape_members.items():
            if attr == "lambda":
                init_data_body += f"# {attr}: {value}\n"
            else:
                init_data_body += f"{attr}: {value}\n"
        return init_data_body

    def generate_shape_members(self, shape):
        shape_dict = self.service_json['shapes'][shape]
        members = shape_dict["members"]
        required_args = shape_dict.get("required", [])
        init_data_body = {}
        # bring the required members in front
        ordered_members = {key: members[key] for key in required_args if key in members}
        ordered_members.update(members)
        for member_name, member_attrs in ordered_members.items():
            member_shape_name = member_attrs["shape"]
            if self.service_json["shapes"][member_shape_name]:
                member_shape = self.service_json["shapes"][member_shape_name]
                member_shape_type = member_shape["type"]
                if member_shape_type == "structure":
                    member_type = member_shape_name
                elif member_shape_type == "list":
                    member_type = self._evaluate_list_type(member_shape)
                elif member_shape_type == "map":
                    member_type = self._evaluate_map_type(member_shape)
                else:
                    # Shape is a simple type like string
                    member_type = BASIC_JSON_TYPES_TO_PYTHON_TYPES[member_shape_type]
            else:
                raise Exception("The Shape definition mush exist. The Json Data might be corrupt")
            member_name_snake_case = convert_to_snake_case(member_name)
            if member_name in required_args:
                init_data_body[f"{member_name_snake_case}"] = f"{member_type}"
            else:
                init_data_body[f"{member_name_snake_case}"] = f"Optional[{member_type}] = Unassigned()"
        return init_data_body
