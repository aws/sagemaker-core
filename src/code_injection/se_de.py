import logging

from dataclasses import asdict
from src.code_injection.shape_dag import SHAPE_DAG

# need to set this to set the shape classes in globals()
from src.generated.shapes import *

BASIC_TYPES = ["string", "boolean", "integer", "long", "double", "timestamp"]


def _pascal_to_snake(pascal_str):
    return ''.join(['_' + i.lower() if i.isupper() else i for i in pascal_str]).lstrip('_')


def deserialize(data, cls) -> object:
    # Convert the keys to snake_case
    data = {_pascal_to_snake(k): v for k, v in data.items()}

    # Get the class from the cls_name string
    if type(cls) == str:
        cls = globals()[cls]

    # Create a new instance of the class
    instance = cls(**data)

    return instance


def _snake_to_pascal(snake_str):
    components = snake_str.split('_')
    return ''.join(x.title() for x in components[0:])


def serialize(data) -> object:
    data_dict = asdict(data)

    # Convert the keys to pascalCase
    data_dict = {_snake_to_pascal(k): v for k, v in data_dict.items() if v is not None}

    return data_dict


def _evaluate_list_type(raw_list, shape):
    if shape["member_type"] in BASIC_TYPES:
        # if basic types directly assign list value.
        _evaluated_list = raw_list
    elif shape["member_type"] == "structure":
        # if structure type deserialize each list item and assign value.
        _evaluated_list = []
        # traverse through response list and set the object instance
        for item in raw_list:
            # create an instance of member["member_shape"]
            member_instance = deserialize(item, shape["member_shape"])
            deserializer(member_instance, item, shape["member_shape"])
            _evaluated_list.append(member_instance)
    else:
        raise ValueError(f"Unhandled List member type "
                         f"[{shape['member_type']}] encountered. "
                         "Needs additional logic for support")
    return _evaluated_list


def _evaluate_map_type(raw_map, shape):
    if shape["key_type"] != "string":
        raise ValueError(f"Unhandled Map key type "
                         f"[{shape['key_type']}] encountered. "
                         "Needs additional logic for support")

    _evaluated_map = {}
    if shape["value_type"] in BASIC_TYPES:
        # if basic types directly assign value.
        # Ex. response["map_member"] = {"key":"value"}
        _evaluated_map = raw_map
    elif shape["value_type"] == "structure":
        # if structure type deserialize each list item and assign value.
        _evaluated_map = {}
        for k, v in raw_map.items():
            # create an instance of shape data class and do a multilevel deserialize
            value_instance = deserialize(v, shape["value_shape"])
            deserializer(value_instance, v, shape["value_shape"])
            _evaluated_map[k] = value_instance
    elif shape["value_type"] == "list":
        _evaluated_map = {}
        for k, v in raw_map.items():
            _list_type_shape = SHAPE_DAG[shape["value_shape"]]
            evaluated_values = _evaluate_list_type(raw_map, _list_type_shape)
            _evaluated_map[k] = evaluated_values
    elif shape["value_type"] == "map":
        _evaluated_map = {}
        for k, v in raw_map.items():
            _map_type_shape = SHAPE_DAG[shape["value_shape"]]
            evaluated_values = _evaluate_map_type(v, _map_type_shape)
            _evaluated_map[k] = evaluated_values
    else:
        raise ValueError(f"Unhandled List member type "
                         f"[{shape['value_type']}] encountered. "
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
        logging.debug("Evaluating member:", member)
        if not operation_response.get(member["name"]):
            logging.debug("Member not set, continuing...")
            continue
        # 1. set snake case attribute name
        attribute_name = _pascal_to_snake(member["name"])
        if member["type"] in BASIC_TYPES:
            logging.debug("Basic type encountered, evaluating...", member)
            # 2. directly assign the response value for basic types.
            evaluated_value = operation_response[member["name"]]
        elif member["type"] == "structure":
            logging.debug("Structure type encountered, evaluating...", member)
            # 2. deserialize the shape structure and infer the value.
            evaluated_value = deserialize(operation_response[member["name"]], member["shape"])
            # recursively deserialize the structure further.
            deserializer(evaluated_value, operation_response[member["name"]], member["shape"])
        elif member["type"] == "list":
            logging.debug("List type encountered, evaluating...", member)
            _list_type_shape = SHAPE_DAG[member["shape"]]
            # 2. set the value
            evaluated_value = _evaluate_list_type(operation_response[member["name"]],
                                                   _list_type_shape)
        elif member["type"] == "map":
            logging.debug("Map type encountered, evaluating...", member)
            _map_type_shape = SHAPE_DAG[member["shape"]]
            # 2. evaluate the attribute values
            evaluated_value = _evaluate_map_type(operation_response[member["name"]], _map_type_shape)

        # 3. set the object attribute
        setattr(object_instance, attribute_name, evaluated_value)
