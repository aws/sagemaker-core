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
import logging

from dataclasses import asdict
from src.code_injection.shape_dag import SHAPE_DAG
from src.code_injection.constants import BASIC_TYPES, STRUCTURE_TYPE, LIST_TYPE, MAP_TYPE

# need to set this to set the shape classes in globals()
from src.generated.shapes import *


def pascal_to_snake(pascal_str):
    """
    Converts a PascalCase string to snake_case.

    Args:
        pascal_str (str): The PascalCase string to be converted.

    Returns:
        str: The converted snake_case string.
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in pascal_str]).lstrip('_')


def deserialize(data, cls) -> object:
    """
    Deserialize the given data into an instance of the specified class.

    Args:
        data (dict): The data to be deserialized.
        cls (str or type): The class or class name to deserialize into.

    Returns:
        object: An instance of the specified class with the deserialized data.
    """
    # Convert the keys to snake_case
    data = {pascal_to_snake(k): v for k, v in data.items()}

    # Get the class from the cls_name string
    if type(cls) == str:
        cls = globals()[cls]

    # Create a new instance of the class
    instance = cls(**data)

    return instance


def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components[0:])


def serialize(data) -> object:
    """
    Serializes the given data object into a dictionary.

    Args:
        data: The data object to be serialized.

    Returns:
        A dictionary containing the serialized data.

    """
    data_dict = asdict(data)

    # Convert the keys to pascalCase
    data_dict = {snake_to_pascal(k): v for k, v in data_dict.items() if v is not None}

    return data_dict


def _evaluate_list_type(raw_list, shape):
    """
    Evaluates a list type based on the given shape.

    Args:
        raw_list (list): The raw list to be evaluated.
        shape (dict): The shape of the list.

    Returns:
        list: The evaluated list based on the shape.

    Raises:
        ValueError: If an unhandled list member type is encountered.

    """
    _shape_member_type = shape["member_type"]
    _shape_member_shape = shape["member_shape"]
    if _shape_member_type in BASIC_TYPES:
        # if basic types directly assign list value.
        _evaluated_list = raw_list
    elif _shape_member_type == STRUCTURE_TYPE:
        # if structure type deserialize each list item and assign value.
        _evaluated_list = []
        # traverse through response list and set the object instance
        for item in raw_list:
            # create an instance of member["member_shape"]
            member_instance = deserialize(item, _shape_member_shape)
            deserializer(member_instance, item, _shape_member_shape)
            _evaluated_list.append(member_instance)
    else:
        raise ValueError(f"Unhandled List member type "
                         f"[{_shape_member_type}] encountered. "
                         "Needs additional logic for support")
    return _evaluated_list


def _evaluate_map_type(raw_map, shape):
    """
    Evaluates a map type based on the given shape.

    Args:
        raw_map (dict): The raw map to be evaluated.
        shape (dict): The shape of the map.

    Returns:
        dict: The evaluated map.

    Raises:
        ValueError: If an unhandled map key type or list member type is encountered.
    """
    _shape_key_type = shape["key_type"]
    _shape_value_type = shape["value_type"]
    _shape_value_shape = shape["value_shape"]
    if _shape_key_type != "string":
        raise ValueError(f"Unhandled Map key type "
                         f"[{_shape_key_type}] encountered. "
                         "Needs additional logic for support")

    _evaluated_map = {}
    if _shape_value_type in BASIC_TYPES:
        # if basic types directly assign value.
        # Ex. response["map_member"] = {"key":"value"}
        _evaluated_map = raw_map
    elif _shape_value_type == STRUCTURE_TYPE:
        # if structure type deserialize each list item and assign value.
        _evaluated_map = {}
        for k, v in raw_map.items():
            # create an instance of shape data class and do a multilevel deserialize
            value_instance = deserialize(v, _shape_value_shape)
            deserializer(value_instance, v, _shape_value_shape)
            _evaluated_map[k] = value_instance
    elif _shape_value_type == LIST_TYPE:
        _evaluated_map = {}
        for k, v in raw_map.items():
            _list_type_shape = SHAPE_DAG[_shape_value_shape]
            evaluated_values = _evaluate_list_type(v, _list_type_shape)
            _evaluated_map[k] = evaluated_values
    elif _shape_value_type == MAP_TYPE:
        _evaluated_map = {}
        for k, v in raw_map.items():
            _map_type_shape = SHAPE_DAG[_shape_value_shape]
            evaluated_values = _evaluate_map_type(v, _map_type_shape)
            _evaluated_map[k] = evaluated_values
    else:
        raise ValueError(f"Unhandled List member type "
                         f"[{_shape_value_type}] encountered. "
                         "Needs additional logic for support")

    return _evaluated_map


def deserializer(object_instance, operation_response, operation_output_shape):
    """ Deserialize the API Operation Response and set the Resource class object attributes.

    :param object_instance: Resource class object, the attributes of which will be set.
    :param operation_response: Raw API Operation response.
    :param operation_output_shape: Output Shape of the API Operation.
    """
    _operation_output_state_shape = SHAPE_DAG[operation_output_shape]
    if _operation_output_state_shape["type"] in BASIC_TYPES:
        raise ValueError("Unexpected low-level operation model shape")
    for member in _operation_output_state_shape["members"]:
        _member_name = member["name"]
        _member_shape = member["shape"]
        _member_type = member["type"]
        logging.debug(f"Evaluating member: {member}")
        if operation_response.get(_member_name) is None:
            logging.debug(f"Member {member} not set, continuing...")
            continue
        # 1. set snake case attribute name
        attribute_name = pascal_to_snake(_member_name)
        if _member_type in BASIC_TYPES:
            logging.debug(f"Basic type encountered, evaluating member: {member}")
            # 2. directly assign the response value for basic types.
            evaluated_value = operation_response[_member_name]
        elif _member_type == STRUCTURE_TYPE:
            logging.debug(f"Structure type encountered, evaluating member: {member}")
            # 2. deserialize the shape structure and infer the value.
            evaluated_value = deserialize(operation_response[_member_name], _member_shape)
            # recursively deserialize the structure further.
            deserializer(evaluated_value, operation_response[_member_name], _member_shape)
        elif _member_type == LIST_TYPE:
            logging.debug(f"List type encountered, evaluating member: {member}")
            _list_type_shape = SHAPE_DAG[member["shape"]]
            # 2. set the value
            evaluated_value = _evaluate_list_type(operation_response[_member_name],
                                                   _list_type_shape)
        elif _member_type == MAP_TYPE:
            logging.debug(f"Map type encountered, evaluating member: {member}")
            _map_type_shape = SHAPE_DAG[member["shape"]]
            # 2. evaluate the attribute values
            evaluated_value = _evaluate_map_type(operation_response[_member_name], _map_type_shape)
        else:
            raise ValueError(f"Unexpected member type encountered: {_member_type}")

        # 3. set the object attribute
        setattr(object_instance, attribute_name, evaluated_value)
