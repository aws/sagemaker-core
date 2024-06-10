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

RESOURCE_CLASS_TEMPLATE = """
class {class_name}:
{data_class_members}
{init_method}
{class_methods}
{object_methods}
"""

INIT_METHOD_TEMPLATE = """
def __init__(self, 
    session: Optional[Session] = None, 
    region: Optional[str] = None
    {init_args}):
    self.session = session
    self.region = region
    {init_assignments}

"""

CREATE_METHOD_TEMPLATE = """
@classmethod
@populate_inputs_decorator
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
    logger.debug("Creating {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}
    
    operation_input_args = Base.populate_chained_attributes(resource_name='{resource_name}', operation_input_args=operation_input_args)
        
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({get_args}, session=session, region=region)
"""

CREATE_METHOD_TEMPLATE_WITHOUT_DEFAULTS = """
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
    logger.debug("Creating {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}
    
    operation_input_args = Base.populate_chained_attributes(resource_name='{resource_name}', operation_input_args=operation_input_args)
        
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({get_args}, session=session, region=region)
"""

IMPORT_METHOD_TEMPLATE = """
@classmethod
def load(
    cls,
{import_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
    logger.debug(f"Importing {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}

    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # import the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({get_args}, session=session, region=region)
"""

GET_NAME_METHOD_TEMPLATE = """
def get_name(self) -> str:
    attributes = vars(self)
    for attribute, value in attributes.items():
        if attribute == 'name' or attribute == '{resource_lower}_name':
            return value
    raise Exception("Name attribute not found for object")
"""


UPDATE_METHOD_TEMPLATE = """
def update(
    self,
{update_args}
) -> Optional["{resource_name}"]:
    logger.debug("Creating {resource_lower} resource.")
    client = SageMakerClient().client

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")
    self.refresh()

    return self
"""

INVOKE_METHOD_TEMPLATE = """
def invoke(self, 
{invoke_args}
) -> Optional[object]:
    logger.debug(f"Invoking {resource_lower} resource.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client
    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return response
"""

INVOKE_ASYNC_METHOD_TEMPLATE = """
def invoke_async(self, 
{create_args}
) -> Optional[object]:
    logger.debug(f"Invoking {resource_lower} resource Async.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client
    
    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return response
"""

INVOKE_WITH_RESPONSE_STREAM_METHOD_TEMPLATE = """
def invoke_with_response_stream(self, 
{create_args}
) -> Optional[object]:
    logger.debug(f"Invoking {resource_lower} resource with Response Stream.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return response
"""


GET_CONFIG_VALUE_TEMPLATE = """
def get_config_value(attribute, resource_defaults, global_defaults):
   if resource_defaults and attribute in resource_defaults:
       return resource_defaults[attribute]
   if global_defaults and attribute in global_defaults:
       return global_defaults[attribute]
   logger.warn("Configurable value not entered in parameters or present in the Config")
   return None
"""

POPULATE_DEFAULTS_DECORATOR_TEMPLATE = """
def populate_inputs_decorator(create_func):
    def wrapper(*args, **kwargs):
        config_schema_for_resource = \\
{config_schema_for_resource}
        return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "{resource_name}", **kwargs))
    return wrapper
"""

CREATE_METHOD_TEMPLATE_WITHOUT_DECORATOR = """
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
    logger.debug("Creating {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}')

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
"""

GET_METHOD_TEMPLATE = """
@classmethod
def get(
    cls,
{describe_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
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
"""

REFRESH_METHOD_TEMPLATE = """
def refresh(self) -> Optional["{resource_name}"]:

    operation_input_args = {{
{operation_input_args}
    }}
    client = SageMakerClient().client
    response = client.{operation}(**operation_input_args)

    # deserialize response and update self
    transform(response, '{describe_operation_output_shape}', self)
    return self
"""

FAILED_STATUS_ERROR_TEMPLATE = """
if "failed" in current_status.lower():
    raise FailedStatusError(resource_type="{resource_name}", status=current_status, reason={reason})
"""

WAIT_METHOD_TEMPLATE = """
def wait(
    self,
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional["{resource_name}"]:
    terminal_states = {terminal_resource_states}
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if current_status in terminal_states:
{failed_error_block}
            return self

        if timeout is not None and time.time() - start_time >= timeout:
            raise TimeoutExceededError(resouce_type="{resource_name}", status=current_status)
        print("-", end="")
        time.sleep(poll)
"""

WAIT_FOR_STATUS_METHOD_TEMPLATE = """
def wait_for_status(
    self,
    status: Literal{resource_states},
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional["{resource_name}"]:
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if status == current_status:
            return self
{failed_error_block}
        if timeout is not None and time.time() - start_time >= timeout:
            raise TimeoutExceededError(resouce_type="{resource_name}", status=current_status)
        print("-", end="")
        time.sleep(poll)
"""

DELETE_METHOD_TEMPLATE = """
def delete(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
"""

STOP_METHOD_TEMPLATE = """
def stop(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
"""

GET_ALL_METHOD_WITH_ARGS_TEMPLATE = """
@classmethod
def get_all(
    cls,
{get_all_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
    client = SageMakerClient(session=session, region_name=region, service_name="{service_name}").client
        
    operation_input_args = {{
{operation_input_args}
    }}
{custom_key_mapping}
    operation_input_args = {{k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}}
    
    return ResourceIterator(
{resource_iterator_args}
    )
"""

GET_ALL_METHOD_NO_ARGS_TEMPLATE = """
@classmethod
def get_all(
    cls,
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
    client = SageMakerClient(session=session, region_name=region, service_name="{service_name}").client
{custom_key_mapping}
    return ResourceIterator(
{resource_iterator_args}
    )
"""

GET_ALL_METHOD_WITH_ARGS_TEMPLATE = """
@classmethod
def get_all(
    cls,
{get_all_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
    client = SageMakerClient(session=session, region_name=region, service_name="{service_name}").client
        
    operation_input_args = {{
{operation_input_args}
    }}
{custom_key_mapping}
    operation_input_args = {{k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}}
    
    return ResourceIterator(
{resource_iterator_args}
    )
"""

GET_ALL_METHOD_NO_ARGS_TEMPLATE = """
@classmethod
def get_all(
    cls,
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
    client = SageMakerClient(session=session, region_name=region, service_name="{service_name}").client
{custom_key_mapping}
    return ResourceIterator(
{resource_iterator_args}
    )
"""

GENERIC_METHOD_TEMPLATE = """
{decorator}
def {method_name}(
{method_args}
) -> {return_type}:
{serialize_operation_input}
{initialize_client}
{call_operation_api}
{deserialize_response}
"""

SERIALIZE_INPUT_TEMPLATE = """
    operation_input_args = {{
{operation_input_args}
    }}"""

INITIALIZE_CLIENT_TEMPLATE = """
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client"""

CALL_OPERATION_API_TEMPLATE = """
    response = client.{operation}(**operation_input_args)"""

DESERIALIZE_RESPONSE_TEMPLATE = """
    transformed_response = transform(response, '{operation_output_shape}')
    return {return_type_conversion}(**transformed_response)"""

DESERIALIZE_RESPONSE_TO_BASIC_TYPE_TEMPLATE = """
    return list(response.values())[0]"""

RESOURCE_BASE_CLASS_TEMPLATE = """
class Base(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    @classmethod
    def _serialize(cls, value: any) -> any:
        if isinstance(value, Unassigned):
            return None
        elif isinstance(value, List):
            return cls._serialize_list(value)
        elif isinstance(value, Dict):
            return cls._serialize_dict(value)
        elif hasattr(value, 'serialize'):
            return value.serialize()
        else:
            return value

    @classmethod
    def _serialize_list(cls, value: List):
        serialized_list = []
        for v in value:
            if serialize_result := cls._serialize(v):
                serialized_list.append(serialize_result)
        return serialized_list

    @classmethod
    def _serialize_dict(cls, value: Dict):
        serialized_dict = {}
        for k, v in value.items():
            if serialize_result := cls._serialize(v):
                serialized_dict.update({k: serialize_result})
        return serialized_dict
    
    @staticmethod
    def get_updated_kwargs_with_configured_attributes(config_schema_for_resource: dict, resource_name: str, **kwargs):
        try:
            for configurable_attribute in config_schema_for_resource:
                if kwargs.get(configurable_attribute) is None:
                    resource_defaults = load_default_configs_for_resource_name(resource_name=resource_name)
                    global_defaults = load_default_configs_for_resource_name(resource_name="GlobalDefaults")
                    formatted_attribute = pascal_to_snake(configurable_attribute)
                    if config_value := get_config_value(formatted_attribute,
                     resource_defaults,
                     global_defaults):
                        kwargs[formatted_attribute] = config_value
        except BaseException as e:
            logger.info("Could not load Default Configs. Continuing.", exc_info=True)
            # Continue with existing kwargs if no default configs found
        return kwargs 
        
    
    @staticmethod
    def populate_chained_attributes(resource_name: str, operation_input_args: dict) -> dict:
        resource_name_in_snake_case = pascal_to_snake(resource_name)
        updated_args = operation_input_args
        for arg, value in operation_input_args.items():
            arg_snake = pascal_to_snake(arg)
            if value == Unassigned() or value == None or not value:
                continue
            if arg_snake.endswith('name') and arg_snake[
                                              :-len('_name')] != resource_name_in_snake_case and arg_snake != 'name':
                if value and value != Unassigned() and type(value) != str:
                    updated_args[arg] = value.get_name()
            elif isinstance(value, list):
                updated_args[arg] = [
                    Base.populate_chained_attributes(resource_name=type(list_item).__name__,
                                                     operation_input_args={
                                                         snake_to_pascal(k): v
                                                         for k, v in Base._get_items(list_item)
                                                     })
                    for list_item in value
                ]
            elif is_not_primitive(value):
                obj_dict = {snake_to_pascal(k): v for k, v in Base._get_items(value)}
                updated_args[arg] = Base.populate_chained_attributes(resource_name=type(value).__name__, operation_input_args=obj_dict)
        return updated_args

    @staticmethod
    def _get_items(object):
        return object.items() if type(object) == dict else object.__dict__.items()

        
"""

SHAPE_BASE_CLASS_TEMPLATE = """
class {class_name}:
    model_config = ConfigDict(protected_namespaces=())
    
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
"""

SHAPE_CLASS_TEMPLATE = '''
class {class_name}:
    """
    {docstring}
    """
{data_class_members}

'''
