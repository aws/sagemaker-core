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
) -> Optional[object]:
    logger.debug("Creating {resource_lower} resource.")
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

    return cls.get({get_args}, session=session, region=region)
"""

CREATE_METHOD_TEMPLATE_WITHOUT_DEFAULTS = """
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    logger.debug("Creating {resource_lower} resource.")
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

    return cls.get({get_args}, session=session, region=region)
"""

IMPORT_METHOD_TEMPLATE = """
@classmethod
def load(
    cls,
{import_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
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

UPDATE_METHOD_TEMPLATE = """
def update(self,
 {update_args}
 ) -> Optional[object]:
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
        create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "{resource_name}", **kwargs))
    return wrapper
"""

CREATE_METHOD_TEMPLATE_WITHOUT_DECORATOR = """
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
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
"""

REFRESH_METHOD_TEMPLATE = """
def refresh(self) -> Optional[object]:

    operation_input_args = {{
{operation_input_args}
    }}
    client = SageMakerClient().client
    response = client.{operation}(**operation_input_args)

    # deserialize response and update self
    transform(response, '{describe_operation_output_shape}', self)
    return self
"""

WAIT_METHOD_TEMPLATE = """
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
"""

WAIT_FOR_STATUS_METHOD_TEMPLATE = """
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

RESOURCE_BASE_CLASS_TEMPLATE = """
class Base(BaseModel):
    @classmethod
    def _serialize(cls, data: Dict) -> Dict:
        result = {}
        for attr, value in data.items():
            if isinstance(value, Unassigned):
                continue
            
            if isinstance(value, List):
                result[attr] = cls._serialize_list(value)
            elif isinstance(value, Dict):
                result[attr] = cls._serialize_dict(value)
            elif hasattr(value, 'serialize'):
                result[attr] = value.serialize()
            else:
                result[attr] = value
        return result
    
    @classmethod
    def _serialize_list(cls, value: List):
        return [v.serialize() if hasattr(v, 'serialize') else v for v in value]
    
    @classmethod
    def _serialize_dict(cls, value: Dict):
        return {k: v.serialize() if hasattr(v, 'serialize') else v for k, v in value.items()}
    
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
"""

LOAD_DEFAULT_CONFIGS_AND_HELPERS_TEMPLATE = '''
_APP_NAME = "sagemaker"
# The default name of the config file.
_CONFIG_FILE_NAME = "config.yaml"
# The default config file location of the Administrator provided config file. This path can be
# overridden with `SAGEMAKER_ADMIN_CONFIG_OVERRIDE` environment variable.
_DEFAULT_ADMIN_CONFIG_FILE_PATH = os.path.join(site_config_dir(_APP_NAME), _CONFIG_FILE_NAME)
# The default config file location of the user provided config file. This path can be
# overridden with `SAGEMAKER_USER_CONFIG_OVERRIDE` environment variable.
_DEFAULT_USER_CONFIG_FILE_PATH = os.path.join(user_config_dir(_APP_NAME), _CONFIG_FILE_NAME)
# The default config file location of the local mode.
_DEFAULT_LOCAL_MODE_CONFIG_FILE_PATH = os.path.join(
    os.path.expanduser("~"), ".sagemaker", _CONFIG_FILE_NAME
)
ENV_VARIABLE_ADMIN_CONFIG_OVERRIDE = "SAGEMAKER_ADMIN_CONFIG_OVERRIDE"
ENV_VARIABLE_USER_CONFIG_OVERRIDE = "SAGEMAKER_USER_CONFIG_OVERRIDE"

S3_PREFIX = "s3://"

def load_default_configs(additional_config_paths: List[str] = None, s3_resource=None):
    default_config_path = os.getenv(
        ENV_VARIABLE_ADMIN_CONFIG_OVERRIDE, _DEFAULT_ADMIN_CONFIG_FILE_PATH
    )
    user_config_path = os.getenv(ENV_VARIABLE_USER_CONFIG_OVERRIDE, _DEFAULT_USER_CONFIG_FILE_PATH)
    
    config_paths = [default_config_path, user_config_path]
    if additional_config_paths:
        config_paths += additional_config_paths
    config_paths = list(filter(lambda item: item is not None, config_paths))
    merged_config = {}
    for file_path in config_paths:
        config_from_file = {}
        if file_path.startswith(S3_PREFIX):
            config_from_file = _load_config_from_s3(file_path, s3_resource)
        else:
            try:
                config_from_file = _load_config_from_file(file_path)
            except ValueError as error:
                if file_path not in (
                    _DEFAULT_ADMIN_CONFIG_FILE_PATH,
                    _DEFAULT_USER_CONFIG_FILE_PATH,
                ):
                    # Throw exception only when User provided file path is invalid.
                    # If there are no files in the Default config file locations, don't throw
                    # Exceptions.
                    raise

                logger.debug(error)
        if config_from_file:
            validate_sagemaker_config(config_from_file)
            merge_dicts(merged_config, config_from_file)
            print("Fetched defaults config from location: %s", file_path)
        else:
            print("Not applying SDK defaults from location: %s", file_path)

    return merged_config
    
def validate_sagemaker_config(sagemaker_config: dict = None):
    """Validates whether a given dictionary adheres to the schema.

    Args:
        sagemaker_config: A dictionary containing default values for the
                SageMaker Python SDK. (default: None).
    """
    jsonschema.validate(sagemaker_config, SAGEMAKER_PYTHON_SDK_CONFIG_SCHEMA)
    

def _load_config_from_s3(s3_uri, s3_resource_for_config) -> dict:
    """Placeholder docstring"""
    if not s3_resource_for_config:
        # Constructing a default Boto3 S3 Resource from a default Boto3 session.
        boto_session = boto3.DEFAULT_SESSION or boto3.Session()
        boto_region_name = boto_session.region_name
        if boto_region_name is None:
            raise ValueError(
                "Must setup local AWS configuration with a region supported by SageMaker."
            )
        s3_resource_for_config = boto_session.resource("s3", region_name=boto_region_name)

    logger.debug("Fetching defaults config from location: %s", s3_uri)
    inferred_s3_uri = _get_inferred_s3_uri(s3_uri, s3_resource_for_config)
    parsed_url = urlparse(inferred_s3_uri)
    bucket, key_prefix = parsed_url.netloc, parsed_url.path.lstrip("/")
    s3_object = s3_resource_for_config.Object(bucket, key_prefix)
    s3_file_content = s3_object.get()["Body"].read()
    return yaml.safe_load(s3_file_content.decode("utf-8"))
    
    
def _get_inferred_s3_uri(s3_uri, s3_resource_for_config):
    """Placeholder docstring"""
    parsed_url = urlparse(s3_uri)
    bucket, key_prefix = parsed_url.netloc, parsed_url.path.lstrip("/")
    s3_bucket = s3_resource_for_config.Bucket(name=bucket)
    s3_objects = s3_bucket.objects.filter(Prefix=key_prefix).all()
    s3_files_with_same_prefix = [
        "{}{}/{}".format(S3_PREFIX, bucket, s3_object.key) for s3_object in s3_objects
    ]
    if len(s3_files_with_same_prefix) == 0:
        # Customer provided us with an incorrect s3 path.
        raise ValueError("Provide a valid S3 path instead of {}".format(s3_uri))
    if len(s3_files_with_same_prefix) > 1:
        # Customer has provided us with a S3 URI which points to a directory
        # search for s3://<bucket>/directory-key-prefix/config.yaml
        inferred_s3_uri = str(pathlib.PurePosixPath(s3_uri, _CONFIG_FILE_NAME)).replace(
            "s3:/", "s3://"
        )
        if inferred_s3_uri not in s3_files_with_same_prefix:
            # We don't know which file we should be operating with.
            raise ValueError(
                f"Provide an S3 URI of a directory that has a {_CONFIG_FILE_NAME} file."
            )
        # Customer has a config.yaml present in the directory that was provided as the S3 URI
        return inferred_s3_uri
    return s3_uri

def _load_config_from_file(file_path: str) -> dict:
    """Placeholder docstring"""
    inferred_file_path = file_path
    if os.path.isdir(file_path):
        inferred_file_path = os.path.join(file_path, _CONFIG_FILE_NAME)
    if not os.path.exists(inferred_file_path):
        raise ValueError(
            f"Unable to load the config file from the location: {file_path}"
            f"Provide a valid file path"
        )
    logger.debug("Fetching defaults config from location: %s", file_path)
    with open(inferred_file_path, "r") as f:
        content = yaml.safe_load(f)
    return content
'''

LOAD_CONFIG_VALUES_FOR_RESOURCE_TEMPLATE = """
@lru_cache(maxsize=None)
def load_default_configs_for_resource_name(resource_name: str):
    configs_data = load_default_configs()
    return configs_data["SageMaker"]["PythonSDK"]["Resources"].get(resource_name)
"""

SHAPE_BASE_CLASS_TEMPLATE = """
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
"""

SHAPE_CLASS_TEMPLATE = '''
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
