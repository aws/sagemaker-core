from generate_resource_plan import ResourceExtractor
import json
import os

RESOURCE_CLASS_TEMPLATE ='''
class {class_name}:
{init_method}
{class_methods}
{object_methods}
'''

class ResourceGenerator:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.service_json = json.load(file)

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

    def generate_resources(self):
        self.df = self.resource_extractor.get_resource_plan()

        for index, row in self.df.iterrows():
            resource_name = row['resource_name']
            class_methods = row['class_methods']
            object_methods = row['object_methods']
            additional_methods = row['additional_methods']
            raw_actions = row['raw_actions']

            print(f"Resource: {resource_name}")
            print(f"Class Methods: {class_methods}")
            print(f"Object Methods: {object_methods}")
            print(f"Additional Methods: {additional_methods}")
            print(f"Raw actions: {raw_actions}")
            print("\n")


if __name__ == "__main__":
    file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
    resource_generator = ResourceGenerator(file_path)