import json
from functools import cache
import os
import pandas as pd

CLASS_METHODS = set(['create', 'add', 'start', 'register', 'import', 'list', 'get'])
OBJECT_METHODS = set(['refresh', 'delete', 'update', 'stop', 'deregister'])

'''
This class is used to extract the resources and its actions from the service-2.json file.
'''
class ResourceExtractor:

    # Wire additional methods to resources
    RESOURCE_TO_ADDITIONAL_METHODS = {
        'Cluster': ['DescribeClusterNode', 'ListClusterNodes'],
    }
    
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
        self.resource_actions = {}
        self.actions_under_resource = set()

        if self.service_id != 'SageMaker':
            raise Exception(f"ServiceId {self.service_id} not supported")

        if self.protocol == 'json':
            self._extract_resources_and_its_api_actions()
            self._extract_dataframes()
        else:
            raise Exception(f"Protocol {self.protocol} not supported")
    
    def _filter_actions_for_resources(self, resources):
        for resource in sorted(resources, key=len, reverse=True):
            # filter action in actions
            filtered_actions = set([a for a in self.actions if a.endswith(resource) or (a.startswith('List') and a.endswith(resource +'s'))])
            self.actions_under_resource.update(filtered_actions)
            self.resource_actions[resource] = filtered_actions

            self.actions = self.actions - filtered_actions

    def _extract_resources_and_its_api_actions(self):
        self.actions = set(self.operations.keys())
        
        print(f"Total actions - {len(self.actions)}")
        self.create_resources = set([key[len('Create'):] for key in self.actions if key.startswith('Create')])
        self._filter_actions_for_resources(self.create_resources)

        self.add_resources = set([key[len('Add'):] for key in self.actions if key.startswith('Add')])
        self._filter_actions_for_resources(self.add_resources)

        self.start_resources = set([key[len('Start'):] for key in self.actions if key.startswith('Start')])
        self._filter_actions_for_resources(self.start_resources)

        self.register_resources = set([key[len('Register'):] for key in self.actions if key.startswith('Register')])
        self._filter_actions_for_resources(self.register_resources)

        self.import_resources = set([key[len('Import'):] for key in self.actions if key.startswith('Import')])
        self._filter_actions_for_resources(self.import_resources)

        self.resources = self.create_resources | self.add_resources | self.start_resources | self.register_resources | self.import_resources
        print(f"Total resource - {len(self.resources)}")

        print(f"Total actions_under_resource - {len(self.actions_under_resource)}")

        '''
        for resource, self.actions in self.resource_actions.items():
            print(f"{resource} -- {self.actions}")
        '''

    def _extract_dataframes(self):
        # built a dataframe for each resources and it has
        # resource_name, type, class_methods, object_methods, additional_methods and raw_actions
        df = pd.DataFrame(columns=['resource_name', 'type', 
                                   'class_methods', 'object_methods', 
                                   'additional_methods', 'raw_actions'])

        for resource, actions in sorted(self.resource_actions.items()):
            class_methods = set()
            object_methods = set()
            additional_methods = set()

            for action in actions:
                action_low = action.lower()
                resource_low = resource.lower()

                if action_low.split(resource_low)[0] == 'describe':
                    class_methods.add('get')
                    object_methods.add('refresh')
                    continue

                if action_low.split(resource_low)[0] in self.CLASS_METHODS:
                    class_methods.add(action_low.split(resource_low)[0])
                elif action_low.split(resource_low)[0] in self.OBJECT_METHODS:
                    object_methods.add(action_low.split(resource_low)[0])
                else:
                    additional_methods.add(action)

            # print(f"{resource} -- {sorted(class_methods)} -- {sorted(object_methods)} -- {sorted(additional_methods)} -- {sorted(actions)}")

            if resource in self.RESOURCE_TO_ADDITIONAL_METHODS:
                additional_methods.update(self.RESOURCE_TO_ADDITIONAL_METHODS[resource])

            new_row = pd.DataFrame({
                'resource_name': [resource],
                'type': ['resource'],
                'class_methods': [list(sorted(class_methods))],
                'object_methods': [list(sorted(object_methods))],
                'additional_methods': [list(sorted(additional_methods))],
                'raw_actions': [list(sorted(actions))]
            })

            df = pd.concat([df, new_row], ignore_index=True)

        df.to_csv('resource_plan.csv', index=False)

file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
resource_extractor = ResourceExtractor(file_path)