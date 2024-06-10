from enum import Enum


class MethodType(Enum):
    CLASS = "class"
    OBJECT = "object"
    # TODO: add static if we add operations as static methods in future


class Method:
    """
    A class to store the information of methods to be generated
    """

    operation_name: str
    resource_name: str
    method_name: str
    return_type: str
    method_type: MethodType
    service_name: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    # TODO: add some templates for common methods
