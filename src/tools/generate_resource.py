from .generate_resource_plan import ResourceExtractor
import json
import os

from src.tools.generator import Generator
from src.util.util import add_indent, convert_to_snake_case

RESOURCE_CLASS_TEMPLATE ='''
class {class_name}:
{data_class_members}
{init_method}
{class_methods}
{object_methods}
'''

INIT_METHOD_TEMPLATE = '''
def __init__(self, 
    session: Optional[Session] = None, 
    region: Optional[str] = None
    {init_args}):
    self.session = session
    self.region = region
    {init_assignments}

'''

CREATE_METHOD_TEMPLATE = '''
@classmethod
def create(
    cls,
    {create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:

'''

GET_METHOD_TEMPLATE = '''
@classmethod
def get(
    cls,
    {describe_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    {resource_lower} = cls(session, region)

    operation_input_args = {operation_input_args}
    response = {resource_lower}.client.{operation}(**operation_input_args)

    pprint(response)

    # deserialize the response
{object_attribute_assignments}
    return {resource_lower}
'''


class ResourceGenerator(Generator):
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            service_json = json.load(file)
        super().__init__(service_json)

        self.version = self.service_json['metadata']['apiVersion']
        self.protocol = self.service_json['metadata']['protocol']
        self.service = self.service_json['metadata']['serviceFullName']
        self.service_id = self.service_json['metadata']['serviceId']
        self.uid = self.service_json['metadata']['uid']
        self.operations = self.service_json['operations']
        self.shapes = self.service_json['shapes']

        if self.service_id != 'SageMaker':
            raise Exception(f"ServiceId {self.service_id} not supported")
        
        if self.protocol != 'json':
            raise Exception(f"Protocol {self.protocol} not supported")
    
        self.resource_extractor = ResourceExtractor(self.service_json)
        self.generate_resources()

    def generate_imports(self):
        imports = "import datetime\n"
        imports += "\n"
        imports += "from dataclasses import dataclass\n"
        imports += "from typing import List, Dict, Optional\n"
        imports += "\n"
        return imports


    def generate_resources(self, output_folder="src/generated"):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        output_file = os.path.join(output_folder, f"resources.py")
        self.df = self.resource_extractor.get_resource_plan()

        with open(output_file, "w") as file:
            imports = self.generate_imports()
            file.write(imports)
            file.write("\n\n")

            for index, row in self.df.iterrows():
                resource_name = row['resource_name']
                class_methods = row['class_methods']
                object_methods = row['object_methods']
                additional_methods = row['additional_methods']
                raw_actions = row['raw_actions']

    def generate_init_method(self, row):
        pass

    def generate_get_method(self, resource):
        """Auto-Generate GET Method [describe API] for a resource.

        Usage:
            get_method_response = res_gen.generate_get_method("Model")
            from pprint import pprint
            pprint(get_method_response)

        :param resource: (str) Resource Name string. (Ex. Model)
        :return: (str) Formatted Get Method template.
        """
        resource_operation = self.operations["Describe" + resource]
        resource_operation_input_shape_name = resource_operation["input"]["shape"]
        resource_operation_output_shape_name = resource_operation["output"]["shape"]
        describe_args = ""
        typed_shape_members = self.generate_shape_members(resource_operation_input_shape_name)
        for attr, type in typed_shape_members.items():
            describe_args += f"{attr}: {type},\n"
        # remove the last \n
        describe_args = describe_args.rstrip("\n")
        resource_lower = convert_to_snake_case(resource)

        input_shape_members = self.shapes[resource_operation_input_shape_name]["members"].keys()

        operation_input_args = {}
        for member in input_shape_members:
            operation_input_args[member] = convert_to_snake_case(member)

        operation = convert_to_snake_case("Describe" + resource)

        # ToDo: The direct assignments would be replaced by multi-level deserialization logic.
        object_attribute_assignments = ""
        output_shape_members = self.shapes[resource_operation_output_shape_name]["members"]
        for member in output_shape_members.keys():
            attribute_from_member = convert_to_snake_case(member)
            object_attribute_assignments += f"{resource_lower}.{attribute_from_member} = response[\"{member}\"]\n"
        object_attribute_assignments = add_indent(object_attribute_assignments, 4)

        formatted_method = GET_METHOD_TEMPLATE.format(
            describe_args=describe_args,
            resource_lower=resource_lower,
            operation_input_args=operation_input_args,
            operation=operation,
            object_attribute_assignments=object_attribute_assignments,
        )
        return formatted_method

    def get_attributes_and_its_type(self, row) -> dict:
        pass

    def generate_resource_class(self, row) -> str:
        pass

if __name__ == "__main__":
    file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
    resource_generator = ResourceGenerator(file_path)
