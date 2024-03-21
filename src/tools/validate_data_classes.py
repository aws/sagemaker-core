"""Script to be run from parent repo folder 'sagemaker-code-gen' using:

python src/tools/validate_data_classes.py

The script would validate data classes present in src.generated.generated_classes module.
"""

import inspect
import importlib
from dataclasses import is_dataclass, asdict
from datetime import datetime
import os
import sys
from typing import Union

current_directory = os.getcwd()
# this will require script to be run from parent repo folder ""
sys.path.append(current_directory)

from src.code_injection.se_de import serialize, deserialize
from src.generated.shapes import Unassigned

module_name = 'src.generated.shapes'

# Import the module dynamically
module = importlib.import_module(module_name)

# Get all members of the module
members = inspect.getmembers(module)

# Filter out the data classes
data_classes = [member[1] for member in members if is_dataclass(member[1])]

# Dummy input attribute parameter values
dummy_values = {
    str: "dummy_string",
    int: 123,
    float: 3.14,
    bool: True,
    list: [1, 2, 3],
    dict: {"key": "value"},
    datetime: datetime.now()
}

for data_class in data_classes:
    # print(data_class)
    # print(data_class.__dataclass_fields__)
    fields = [(field.name, field.type) for field in data_class.__dataclass_fields__.values()]
    # print(fields)

    dummy_attributes = {}
    for name, type_ in fields:
        if type_ in dummy_values:
            dummy_attributes[name] = dummy_values[type_]
        elif hasattr(type_, "__origin__") and type_.__origin__ is Union:
            # signifies the use of typing.Optional
            inner_types = type_.__args__
            # Look for the non-None type in Union
            dummy_attributes[name] = dummy_values.get(inner_types[0], Unassigned())
        else:
            dummy_attributes[name] = Unassigned()

    # print(dummy_attributes)
    instance = data_class(**dummy_attributes)

    # Print instance details
    print("Instance of class:", data_class.__name__)
    print(f"Attributes:{asdict(instance)}")
    serialised_data = serialize(instance)
    print(f"Serialised Attributes:{serialised_data}")
    de_serialised_object = deserialize(serialised_data, data_class)
    print(f"De-serialised object:{de_serialised_object}")
    print()
    comparison = asdict(de_serialised_object) == asdict(instance)
    if not comparison:
        raise Exception("The de-serialised(serialised(instance)) does not match the input.")
print("VALIDATED SUCCESSFULLY")
