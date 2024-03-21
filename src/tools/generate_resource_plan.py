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
    
    def __init__(self, service_json):
        self.service_json = service_json
        self.operations = self.service_json['operations']
        self.resource_actions = {}
        self.actions_under_resource = set()

        self._extract_resources_plan()
        
    
    def _filter_actions_for_resources(self, resources):
        for resource in sorted(resources, key=len, reverse=True):
            # filter action in actions
            filtered_actions = set([a for a in self.actions if a.endswith(resource) or (a.startswith('List') and a.endswith(resource +'s'))])
            self.actions_under_resource.update(filtered_actions)
            self.resource_actions[resource] = filtered_actions

            self.actions = self.actions - filtered_actions

    def _extract_resources_plan(self):
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
        self._extract_resource_plan_as_dataframe()

    def _extract_resource_plan_as_dataframe(self):
        # built a dataframe for each resources and it has
        # resource_name, type, class_methods, object_methods, additional_methods and raw_actions
        self.df = pd.DataFrame(columns=['resource_name', 'type', 
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

                if action_low.split(resource_low)[0] in CLASS_METHODS:
                    class_methods.add(action_low.split(resource_low)[0])
                elif action_low.split(resource_low)[0] in OBJECT_METHODS:
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

            self.df = pd.concat([self.df, new_row], ignore_index=True)

        # df.to_csv('resource_plan.csv', index=False)

    def get_resource_plan(self):
        return self.df
    


file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/service-2.json'
with open(file_path, 'r') as file:
    data = json.load(file)
resource_extractor = ResourceExtractor(data)