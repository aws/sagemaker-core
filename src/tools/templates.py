# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Templates for generating resources."""

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
@populate_inputs_decorator
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    logger.debug(f"Creating {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}
        
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({resource_identifier}, session=session, region=region)
'''

CREATE_METHOD_TEMPLATE_WITHOUT_DEFAULTS = '''
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    logger.debug(f"Creating {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({resource_identifier}, session=session, region=region)
'''

GET_CONFIG_VALUE_TEMPLATE = '''
def get_config_value(attribute, resource_defaults, global_defaults):
   if attribute in resource_defaults:
       return resource_defaults[attribute]
   if attribute in global_defaults:
       return global_defaults[attribute]
   raise Exception("Configurable value not present in Configs")
'''

POPULATE_DEFAULTS_DECORATOR_TEMPLATE = '''
def populate_inputs_decorator(create_func):
    def wrapper(*args, **kwargs):
        config_schema_for_resource = \\
{config_schema_for_resource}
        create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, **kwargs))
    return wrapper
'''

GET_METHOD_TEMPLATE = '''
@classmethod
def get(
    cls,
{describe_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    operation_input_args = {{
{operation_input_args}
    }}
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client
    response = client.{operation}(**operation_input_args)

    pprint(response)

    # deserialize the response
    transformed_response = transform(response, '{describe_operation_output_shape}')
    {resource_lower} = cls(**transformed_response)
    return {resource_lower}
'''

REFRESH_METHOD_TEMPLATE = '''
def refresh(self) -> Optional[object]:

    operation_input_args = {{
{operation_input_args}
    }}
    client = SageMakerClient().client
    response = client.{operation}(**operation_input_args)

    # deserialize response and update self
    transform(response, '{describe_operation_output_shape}', self)
    return self
'''

WAIT_METHOD_TEMPLATE = '''
@validate_call
def wait(
    self,
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional[object]:
    terminal_states = {terminal_resource_states}
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if current_status in terminal_states:
            return

        # TODO: Raise some generated TimeOutError
        if timeout is not None and time.time() - start_time >= timeout:
            raise Exception("Timeout exceeded. Final resource state - " + current_status)
        print("-", end="")
        time.sleep(poll)
'''

WAIT_FOR_STATUS_METHOD_TEMPLATE = '''
@validate_call
def wait_for_status(
    self,
    status: Literal{resource_states},
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional[object]:
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if status == current_status:
            return

        # TODO: Raise some generated TimeOutError
        if timeout is not None and time.time() - start_time >= timeout:
            raise Exception("Timeout exceeded. Final resource state - " + current_status)
        print("-", end="")
        time.sleep(poll)
'''

DELETE_METHOD_TEMPLATE = '''
def delete(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
'''

STOP_METHOD_TEMPLATE = '''
def stop(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
'''

RESOURCE_BASE_CLASS_TEMPLATE ='''
class Base(BaseModel):
    @classmethod
    def _serialize_dict(cls, data: Dict) -> Dict:
        result = {}
        for attr, value in data.items():
            if isinstance(value, Unassigned):
                continue
            formatted_attribute = snake_to_pascal(attr) if '_' in attr else cls._capfirst(attr)
            serialized_value = cls._serialize(value)
            result[formatted_attribute] = serialized_value
        return result
    
    @classmethod
    def _serialize_list(cls, value: List):
        return [cls._serialize(v) for v in value]

    @classmethod
    def _serialize(cls, value: any):
        if isinstance(value, List):
            return cls._serialize_list(value)
        if isinstance(value, Dict):
            return cls._serialize_dict(value)
        if hasattr(value, 'serialize'):
            return value.serialize()
        return value

    @staticmethod
    def _capfirst(s: str):
        return s[:1].upper() + s[1:]
            
    @staticmethod
    def get_updated_kwargs_with_configured_attributes(config_schema_for_resource: dict, **kwargs):
        for configurable_attribute in config_schema_for_resource:
            if kwargs.get(configurable_attribute) is None:
                resource_defaults = load_default_configs_for_resource_name(resource_name="Cluster")
                global_defaults = load_default_configs_for_resource_name(resource_name="GlobalDefaults")
                formatted_attribute = pascal_to_snake(configurable_attribute)
                kwargs[formatted_attribute] = get_config_value(formatted_attribute,
                 resource_defaults,
                 global_defaults)
        return kwargs
        
'''
LOAD_DEFAULT_CONFIGS_TEMPLATE = '''
@lru_cache(maxsize=None)
def load_default_configs():
    configs_file_path = os.getcwd() + '/sample/sagemaker/2017-07-24/default-configs.json'
    with open(configs_file_path, 'r') as file:
        configs_data = json.load(file)
    jsonschema.validate(configs_data, SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA)
    return configs_data
'''

LOAD_CONFIG_VALUES_FOR_RESOURCE_TEMPLATE = '''
@lru_cache(maxsize=None)
def load_default_configs_for_resource_name(resource_name: str):
    configs_data = load_default_configs()
    return configs_data["SageMaker"]["PythonSDK"]["Resources"].get(resource_name)
'''

SHAPE_BASE_CLASS_TEMPLATE ='''
class {class_name}:
    def serialize(self):
        result = {{}}
        for attr, value in self.__dict__.items():
            if isinstance(value, Unassigned):
                continue
            
            components = attr.split('_')
            pascal_attr = ''.join(x.title() for x in components[0:])
            if isinstance(value, List):
                result[pascal_attr] = self._serialize_list(value)
            elif isinstance(value, Dict):
                result[pascal_attr] = self._serialize_dict(value)
            elif hasattr(value, 'serialize'):
                result[pascal_attr] = value.serialize()
            else:
                result[pascal_attr] = value
        return result

    def _serialize_list(self, value: List):
        return [v.serialize() if hasattr(v, 'serialize') else v for v in value]
    
    def _serialize_dict(self, value: Dict):
        return {{k: v.serialize() if hasattr(v, 'serialize') else v for k, v in value.items()}}
'''

SHAPE_CLASS_TEMPLATE ='''
class {class_name}:
    """
    {docstring}
    """
{data_class_members}
'''

SNAKE_TO_PASCAL_FUNCTION = '''
def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components[0:])
'''



PASCAL_TO_SNAKE_FUNCTION = '''
def pascal_to_snake(pascal_str):
    """
    Converts a PascalCase string to snake_case.

    Args:
        pascal_str (str): The PascalCase string to be converted.

    Returns:
        str: The converted snake_case string.
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in pascal_str]).lstrip('_')
'''
