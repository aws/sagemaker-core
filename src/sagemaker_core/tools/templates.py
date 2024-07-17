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

RESOURCE_METHOD_EXCEPTION_DOCSTRING = """
Raises:
    botocore.exceptions.ClientError: This exception is raised for AWS service related errors. 
        The error message and error code can be parsed from the exception as follows:
        ```
        try:
            # AWS service call here
        except botocore.exceptions.ClientError as e:
            error_message = e.response['Error']['Message']
            error_code = e.response['Error']['Code']
        ```"""

CREATE_METHOD_TEMPLATE = """
@classmethod
@populate_inputs_decorator
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
{docstring}
    logger.debug("Creating {resource_lower} resource.")
    client = Base.get_sagemaker_client(session=session, region_name=region, service_name='{service_name}')

    operation_input_args = {{
{operation_input_args}
    }}
    
    operation_input_args = Base.populate_chained_attributes(resource_name='{resource_name}', operation_input_args=operation_input_args)
        
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize_args(operation_input_args)
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
{docstring}
    logger.debug("Creating {resource_lower} resource.")
    client =Base.get_sagemaker_client(session=session, region_name=region, service_name='{service_name}')

    operation_input_args = {{
{operation_input_args}
    }}
    
    operation_input_args = Base.populate_chained_attributes(resource_name='{resource_name}', operation_input_args=operation_input_args)
        
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize_args(operation_input_args)
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
{docstring}
    logger.debug(f"Importing {resource_lower} resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='{service_name}').client

    operation_input_args = {{
{operation_input_args}
    }}

    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = cls._serialize_args(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # import the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return cls.get({get_args}, session=session, region=region)
"""

GET_NAME_METHOD_TEMPLATE = """
def get_name(self) -> str:
    attributes = vars(self)
    resource_name = '{resource_lower}_name'
    resource_name_split = resource_name.split('_')
    attribute_name_candidates = []
    
    l = len(resource_name_split)
    for i in range(0, l):
        attribute_name_candidates.append("_".join(resource_name_split[i:l]))
    
    for attribute, value in attributes.items():
        if attribute == 'name' or attribute in attribute_name_candidates:
            return value
    logger.error("Name attribute not found for object {resource_lower}")
    return None
"""


UPDATE_METHOD_TEMPLATE = """
@populate_inputs_decorator
def update(
    self,
{update_args}
) -> Optional["{resource_name}"]:
{docstring}
    logger.debug("Updating {resource_lower} resource.")
    client = Base.get_sagemaker_client()

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize_args(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")
    self.refresh()

    return self
"""


UPDATE_METHOD_TEMPLATE_WITHOUT_DECORATOR = """
def update(
    self,
{update_args}
) -> Optional["{resource_name}"]:
{docstring}
    logger.debug("Updating {resource_lower} resource.")
    client = Base.get_sagemaker_client()

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize_args(operation_input_args)
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
{docstring}
    logger.debug(f"Invoking {resource_lower} resource.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client
    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize_args(operation_input_args)
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
{docstring}
    logger.debug(f"Invoking {resource_lower} resource Async.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client
    
    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize_args(operation_input_args)
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
{docstring}
    logger.debug(f"Invoking {resource_lower} resource with Response Stream.")
    client = SageMakerRuntimeClient(service_name="{service_name}").client

    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")
    # serialize the input request
    operation_input_args = {resource_name}._serialize_args(operation_input_args)
    logger.debug(f"Serialized input request: {{operation_input_args}}")

    # create the resource
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")

    return response
"""


POPULATE_DEFAULTS_DECORATOR_TEMPLATE = """
def populate_inputs_decorator(create_func):
    @functools.wraps(create_func)
    def wrapper(*args, **kwargs):
        config_schema_for_resource = \\
{config_schema_for_resource}
        return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "{resource_name}", **kwargs))
    return wrapper
"""

GET_METHOD_TEMPLATE = """
@classmethod
def get(
    cls,
{describe_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional["{resource_name}"]:
{docstring}
    operation_input_args = {{
{operation_input_args}
    }}
    client = Base.get_sagemaker_client(session=session, region_name=region, service_name='{service_name}')
    response = client.{operation}(**operation_input_args)

    pprint(response)

    # deserialize the response
    transformed_response = transform(response, '{describe_operation_output_shape}')
    {resource_lower} = cls(**transformed_response)
    return {resource_lower}
"""

REFRESH_METHOD_TEMPLATE = """
def refresh(
    self,
 {refresh_args}   
    ) -> Optional["{resource_name}"]:
{docstring}
    operation_input_args = {{
{operation_input_args}
    }}
    client = Base.get_sagemaker_client()
    response = client.{operation}(**operation_input_args)

    # deserialize response and update self
    transform(response, '{describe_operation_output_shape}', self)
    return self
"""

FAILED_STATUS_ERROR_TEMPLATE = """
if "failed" in current_status.lower():
    raise FailedStatusError(resource_type="{resource_name}", status=current_status, reason={reason})
"""

WAIT_METHOD_TEMPLATE = '''
def wait(
    self,
    poll: int = 5,
    timeout: Optional[int] = None
) -> None:
    """
    Wait for a {resource_name} resource.
    
    Parameters:
        poll: The number of seconds to wait between each poll.
        timeout: The maximum number of seconds to wait before timing out.
    
    Raises:
        TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
        FailedStatusError:   If the resource reaches a failed state.
        WaiterError: Raised when an error occurs while waiting.
    
    """
    terminal_states = {terminal_resource_states}
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if current_status in terminal_states:
            print(f"\\nFinal Resource Status: {{current_status}}")
{failed_error_block}
            return

        if timeout is not None and time.time() - start_time >= timeout:
            raise TimeoutExceededError(resouce_type="{resource_name}", status=current_status)
        print("-", end="")
        time.sleep(poll)
'''

WAIT_FOR_STATUS_METHOD_TEMPLATE = '''
def wait_for_status(
    self,
    status: Literal{resource_states},
    poll: int = 5,
    timeout: Optional[int] = None
) -> None:
    """
    Wait for a {resource_name} resource to reach certain status.
    
    Parameters:
        status: The status to wait for.
        poll: The number of seconds to wait between each poll.
        timeout: The maximum number of seconds to wait before timing out.
    
    Raises:
        TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
        FailedStatusError:   If the resource reaches a failed state.
        WaiterError: Raised when an error occurs while waiting.
    """
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self{status_key_path}

        if status == current_status:
            print(f"\\nFinal Resource Status: {{current_status}}")
            return
{failed_error_block}
        if timeout is not None and time.time() - start_time >= timeout:
            raise TimeoutExceededError(resouce_type="{resource_name}", status=current_status)
        print("-", end="")
        time.sleep(poll)
'''

WAIT_FOR_DELETE_METHOD_TEMPLATE = '''
def wait_for_delete(
    self,
    poll: int = 5,
    timeout: Optional[int] = None,
) -> None:
    """
    Wait for a {resource_name} resource to be deleted.
    
    Parameters:
        poll: The number of seconds to wait between each poll.
        timeout: The maximum number of seconds to wait before timing out.
    
    Raises:
        botocore.exceptions.ClientError: This exception is raised for AWS service related errors. 
            The error message and error code can be parsed from the exception as follows:
            ```
            try:
                # AWS service call here
            except botocore.exceptions.ClientError as e:
                error_message = e.response['Error']['Message']
                error_code = e.response['Error']['Code']
            ```
        TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
        DeleteFailedStatusError:   If the resource reaches a failed state.
        WaiterError: Raised when an error occurs while waiting.
    """
    start_time = time.time()

    while True:
        try:
            self.refresh()
            current_status = self{status_key_path}
{delete_failed_error_block}
{deleted_status_check}

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="{resource_name}", status=current_status)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            
            if "ResourceNotFound" in error_code or "ValidationException" in error_code:
                print("Resource was not found. It may have been deleted.")
                return
            raise e
        
        print("-", end="")
        time.sleep(poll)
'''

DELETE_FAILED_STATUS_CHECK = """
if "delete_failed" in current_status.lower() or "deletefailed" in current_status.lower():
    raise DeleteFailedStatusError(resource_type="{resource_name}", reason={reason})
"""

DELETED_STATUS_CHECK = """
if current_status.lower() == "deleted":
    print("Resource was deleted.")
    return
"""

DELETE_METHOD_TEMPLATE = """
def delete(
    self,
{delete_args}
    ) -> None:
{docstring}
    client = Base.get_sagemaker_client()

    operation_input_args = {{
{operation_input_args}
    }}
    client.{operation}(**operation_input_args)
    
    logger.info(f"Deleting {{self.__class__.__name__}} - {{self.get_name()}}")
"""

STOP_METHOD_TEMPLATE = """
def stop(self) -> None:
{docstring}
    client = SageMakerClient().client

    operation_input_args = {{
{operation_input_args}
    }}
    client.{operation}(**operation_input_args)
"""

GET_ALL_METHOD_WITH_ARGS_TEMPLATE = """
@classmethod
def get_all(
    cls,
{get_all_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
{docstring}
    client = Base.get_sagemaker_client(session=session, region_name=region, service_name="{service_name}")
        
    operation_input_args = {{
{operation_input_args}
    }}
{custom_key_mapping}
    operation_input_args = {{k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}}
    
    return ResourceIterator(
{resource_iterator_args}
    )
"""

GET_ALL_METHOD_NO_ARGS_TEMPLATE = '''
@classmethod
def get_all(
    cls,
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> ResourceIterator["{resource}"]:
    """
    Get all {resource} resources.
    
    Parameters:
        session: Boto3 session.
        region: Region name.

    Returns:
        Iterator for listed {resource} resources.

    """
    client = Base.get_sagemaker_client(session=session, region_name=region, service_name="{service_name}")
{custom_key_mapping}
    return ResourceIterator(
{resource_iterator_args}
    )
'''

GENERIC_METHOD_TEMPLATE = """
{decorator}
def {method_name}(
{method_args}
) -> {return_type}:
{docstring}
{serialize_operation_input}
{initialize_client}
{call_operation_api}
{deserialize_response}
"""

SERIALIZE_INPUT_TEMPLATE = """
    operation_input_args = {{
{operation_input_args}
    }}
    logger.debug(f"Input request: {{operation_input_args}}")"""

INITIALIZE_CLIENT_TEMPLATE = """
    client = Base.get_sagemaker_client(session=session, region_name=region, service_name='{service_name}')"""

CALL_OPERATION_API_TEMPLATE = """
    logger.debug(f"Calling {operation} API")
    response = client.{operation}(**operation_input_args)
    logger.debug(f"Response: {{response}}")"""

CALL_OPERATION_API_NO_ARG_TEMPLATE = """
    logger.debug(f"Calling {operation} API")
    response = client.{operation}()
    logger.debug(f"Response: {{response}}")"""

DESERIALIZE_RESPONSE_TEMPLATE = """
    transformed_response = transform(response, '{operation_output_shape}')
    return {return_type_conversion}(**transformed_response)"""

DESERIALIZE_RESPONSE_TO_BASIC_TYPE_TEMPLATE = """
    return list(response.values())[0]"""

SERIALIZE_LIST_INPUT_TEMPLATE = """
    operation_input_args = {{
{operation_input_args}
    }}
    operation_input_args = {{k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}}
    logger.debug(f"Input request: {{operation_input_args}}")"""

RETURN_ITERATOR_TEMPLATE = """
    return ResourceIterator(
{resource_iterator_args}
    )"""

DESERIALIZE_INPUT_AND_RESPONSE_TO_CLS_TEMPLATE = """
    transformed_response = transform(response, '{operation_output_shape}')
    return cls(**operation_input_args, **transformed_response)"""

RESOURCE_BASE_CLASS_TEMPLATE = """
class Base(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), validate_assignment=True)
    
    @classmethod
    def get_sagemaker_client(cls, session = None, region_name = None, service_name = 'sagemaker'):
        return SageMakerClient(session=session, region_name=region_name, service_name=service_name).client
    
    @classmethod
    def _serialize_args(cls, value: dict) -> dict:
        serialized_dict = {}
        for k, v in value.items():
            if serialize_result := cls._serialize(v):
                serialized_dict.update({k: serialize_result})
        return serialized_dict

    @classmethod
    def _serialize(cls, value: any) -> any:
        if isinstance(value, Unassigned):
            return None
        elif isinstance(value, List):
            return cls._serialize_list(value)
        elif is_not_primitive(value) and not isinstance(value, dict):
            return cls._serialize_object(value)
        elif hasattr(value, "serialize"):
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
    def _serialize_object(cls, value: any):
        serialized_dict = {}
        for k, v in vars(value).items():
            if serialize_result := cls._serialize(v):
                key = snake_to_pascal(k) if is_snake_case(k) else k
                serialized_dict.update({key[0].upper() + key[1:]: serialize_result})
        return serialized_dict
    
    @staticmethod
    def get_updated_kwargs_with_configured_attributes(
        config_schema_for_resource: dict, resource_name: str, **kwargs
    ):
        try:
            for configurable_attribute in config_schema_for_resource:
                if kwargs.get(configurable_attribute) is None:
                    resource_defaults = load_default_configs_for_resource_name(
                        resource_name=resource_name
                    )
                    global_defaults = load_default_configs_for_resource_name(
                        resource_name="GlobalDefaults"
                    )
                    if config_value := get_config_value(
                        configurable_attribute, resource_defaults, global_defaults
                    ):
                        resource_name = snake_to_pascal(configurable_attribute)
                        class_object = globals()[resource_name]
                        kwargs[configurable_attribute] = class_object(**config_value)
        except BaseException as e:
            logger.info("Could not load Default Configs. Continuing.", exc_info=True)
            # Continue with existing kwargs if no default configs found
        return kwargs 
        
    
    @staticmethod
    def populate_chained_attributes(resource_name: str, operation_input_args: Union[dict, object]):
        resource_name_in_snake_case = pascal_to_snake(resource_name)
        updated_args = vars(operation_input_args) if type(operation_input_args) == object else operation_input_args
        unassigned_args = []
        keys = operation_input_args.keys()
        for arg in keys:
            value = operation_input_args.get(arg)
            arg_snake = pascal_to_snake(arg)

            if value == Unassigned() :
                unassigned_args.append(arg)
            elif value == None or not value:
                continue
            elif (
                arg_snake.endswith("name")
                and arg_snake[: -len("_name")] != resource_name_in_snake_case
                and arg_snake != "name"
            ):
                if value and value != Unassigned() and type(value) != str:
                    updated_args[arg] = value.get_name()
            elif isinstance(value, list) and is_primitive_list(value):
                continue
            elif isinstance(value, list) and value != []:
                updated_args[arg] = [
                    Base._get_chained_attribute(list_item)
                    for list_item in value
                ]
            elif is_not_primitive(value) and is_not_str_dict(value) and type(value) == object:
                updated_args[arg] = Base._get_chained_attribute(item_value=value)

        for unassigned_arg in unassigned_args:
            del updated_args[unassigned_arg]
        return updated_args

    @staticmethod
    def _get_chained_attribute(item_value: any):
        resource_name = type(item_value).__name__
        class_object = globals()[resource_name]
        return class_object(**Base.populate_chained_attributes(
            resource_name=resource_name,
            operation_input_args=vars(item_value)
        ))

        
"""

SHAPE_BASE_CLASS_TEMPLATE = """
class {class_name}:
    model_config = ConfigDict(protected_namespaces=(), validate_assignment=True)
    
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

RESOURCE_METHOD_EXCEPTION_DOCSTRING = """
Raises:
    botocore.exceptions.ClientError: This exception is raised for AWS service related errors. 
        The error message and error code can be parsed from the exception as follows:
        ```
        try:
            # AWS service call here
        except botocore.exceptions.ClientError as e:
            error_message = e.response['Error']['Message']
            error_code = e.response['Error']['Code']
        ```"""
