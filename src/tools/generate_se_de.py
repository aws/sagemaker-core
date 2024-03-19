from dataclasses import asdict

def _pascal_to_snake(pascal_str):
    return ''.join(['_' + i.lower() if i.isupper() else i for i in pascal_str]).lstrip('_')

def deserialize(data, cls_name) -> object:
    # Convert the keys to snake_case
    data = {_pascal_to_snake(k): v for k, v in data.items()}

    # Get the class from the cls_name string
    cls = globals()[cls_name]

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