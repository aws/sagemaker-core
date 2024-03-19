import json
from functools import cache
import os

class ResourceExtractor:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        self.version = data['metadata']['apiVersion']
        self.protocol = data['metadata']['protocol']
        self.service = data['metadata']['serviceFullName']
        self.service_id = data['metadata']['serviceId']
        self.uid = data['metadata']['uid']
        self.operations = data['operations']
        self.shapes = data['shapes']

        if self.protocol == 'json':
            self.resource_actions = self.extract_resource_and_api_actions()
        else:
            raise Exception(f"Protocol {self.protocol} not supported")
    
    def extract_resource_and_api_actions(self):
        self.actions = self.operations.keys()
        
        print(f"Total actions - {len(self.actions)}")
        self.create_resources = set([key[len('Create'):] for key in self.actions if key.startswith('Create')])
        
        self.add_resources = set([key[len('Add'):] for key in self.actions if key.startswith('Add')])
        self.start_resources = set([key[len('Start'):] for key in self.actions if key.startswith('Start')])
        self.register_resources = set([key[len('Register'):] for key in self.actions if key.startswith('Register')])
        self.import_resources = set([key[len('Import'):] for key in self.actions if key.startswith('Import')])

        self.resources = self.create_resources | self.add_resources | self.start_resources | self.register_resources | self.import_resources
        print(f"Total resource - {len(self.resources)}")

        self.actions_under_resource = set()
        self.resource_actions = {}
        for resource in sorted(self.resources):
            # filter action in actions
            filtered_actions = [a for a in self.actions if a.endswith(resource) or (a.startswith('List') and a.endswith(resource +'s'))]
            self.actions_under_resource.update(filtered_actions)
            self.resource_actions[resource] = filtered_actions

        print(f"Total actions_under_resource - {len(self.actions_under_resource)}")

        self.actions_not_under_resource = set(self.actions) - set(self.actions_under_resource)

        for resource, self.actions in self.resource_actions.items():
            print(f"{resource} -- {self.actions}")


file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
resource_extractor = ResourceExtractor(file_path)