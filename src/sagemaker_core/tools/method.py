from enum import Enum

from sagemaker_core.main.utils import remove_html_tags


class MethodType(Enum):
    CLASS = "class"
    OBJECT = "object"
    STATIC = "static"


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
    docstring_title: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get_docstring_title(self, operation):
        title = remove_html_tags(operation["documentation"])
        self.docstring_title = title.split(".")[0] + "."

    # TODO: add some templates for common methods
