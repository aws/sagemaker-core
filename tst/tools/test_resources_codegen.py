import json
from src.tools.resources_codegen import ResourcesCodeGen
from src.tools.constants import SERVICE_JSON_FILE_PATH

class TestGenerateResource:
    @classmethod
    def setup_class(cls):
        # TODO: leverage pytest fixtures
        with open(SERVICE_JSON_FILE_PATH, 'r') as file:
            service_json = json.load(file)
        
        # Initialize parameters here
        cls.resource_generator = ResourcesCodeGen(service_json)

    # create a unit test for generate_create_method()
    def test_generate_create_method(self):
        expected_output = '''
@classmethod
def create(
    cls,
    compilation_job_name: str,
    role_arn: str,
    output_config: OutputConfig,
    stopping_condition: StoppingCondition,
    model_package_version_arn: Optional[str] = Unassigned(),
    input_config: Optional[InputConfig] = Unassigned(),
    vpc_config: Optional[NeoVpcConfig] = Unassigned(),
    tags: Optional[List[Tag]] = Unassigned(),
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    logger.debug(f"Creating compilation_job resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client

    operation_input_args = {
        'CompilationJobName': compilation_job_name,
        'RoleArn': role_arn,
        'ModelPackageVersionArn': model_package_version_arn,
        'InputConfig': input_config,
        'OutputConfig': output_config,
        'VpcConfig': vpc_config,
        'StoppingCondition': stopping_condition,
        'Tags': tags,
    }
    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # create the resource
    response = client.create_compilation_job(**operation_input_args)
    logger.debug(f"Response: {response}")

    return cls.get(compilation_job_name=compilation_job_name, session=session, region=region)
'''
        assert self.resource_generator.generate_create_method("CompilationJob", needs_defaults_decorator=False) == expected_output

    def test_generate_update_method(self):
        expected_output = '''
def update(self) -> Optional[object]:
    logger.debug(f"Creating endpoint resource.")
    client = SageMakerClient().client

    operation_input_args = {
        'EndpointName': self.endpoint_name,
        'EndpointConfigName': self.endpoint_config_name,
        'RetainAllVariantProperties': self.retain_all_variant_properties,
        'ExcludeRetainedVariantProperties': self.exclude_retained_variant_properties,
        'DeploymentConfig': self.deployment_config,
        'RetainDeploymentConfig': self.retain_deployment_config,
    }
    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = Endpoint._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # create the resource
    response = client.update_endpoint(**operation_input_args)
    logger.debug(f"Response: {response}")
    self.refresh()

    return self
'''
        assert self.resource_generator.generate_update_method(
            "Endpoint") == expected_output

    def test_generate_get_method(self):
        expected_output = '''
@classmethod
def get(
    cls,
    domain_id: str,
    app_type: str,
    app_name: str,
    user_profile_name: Optional[str] = Unassigned(),
    space_name: Optional[str] = Unassigned(),
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    operation_input_args = {
        'DomainId': domain_id,
        'UserProfileName': user_profile_name,
        'SpaceName': space_name,
        'AppType': app_type,
        'AppName': app_name,
    }
    client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    response = client.describe_app(**operation_input_args)

    pprint(response)

    # deserialize the response
    transformed_response = transform(response, 'DescribeAppResponse')
    app = cls(**transformed_response)
    return app
'''
        assert self.resource_generator.generate_get_method("App") == expected_output

    def test_generate_refresh_method(self):
        expected_output = '''
def refresh(self) -> Optional[object]:

    operation_input_args = {
        'DomainId': self.domain_id,
        'UserProfileName': self.user_profile_name,
        'SpaceName': self.space_name,
        'AppType': self.app_type,
        'AppName': self.app_name,
    }
    client = SageMakerClient().client
    response = client.describe_app(**operation_input_args)

    # deserialize response and update self
    transform(response, 'DescribeAppResponse', self)
    return self
'''
        assert self.resource_generator.generate_refresh_method("App") == expected_output

    def test_generate_delete_method(self):
        expected_output = '''
def delete(self) -> None:

    operation_input_args = {
        'CompilationJobName': self.compilation_job_name,
    }
    self.client.delete_compilation_job(**operation_input_args)
'''
        assert self.resource_generator.generate_delete_method("CompilationJob") == expected_output

    # create a unit test for generate_stop_method
    def test_generate_stop_method(self):
        expected_output = '''
def stop(self) -> None:

    operation_input_args = {
        'CompilationJobName': self.compilation_job_name,
    }
    self.client.stop_compilation_job(**operation_input_args)
'''
        assert self.resource_generator.generate_stop_method("CompilationJob") == expected_output
        
    def test_generate_wait_method(self):
        expected_output = '''
@validate_call
def wait(
    self,
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional[object]:
    terminal_states = ['Completed', 'Failed', 'Stopped']
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self.training_job_status

        if current_status in terminal_states:
            return

        # TODO: Raise some generated TimeOutError
        if timeout is not None and time.time() - start_time >= timeout:
            raise Exception("Timeout exceeded. Final resource state - " + current_status)
        print("-", end="")
        time.sleep(poll)
'''
        assert self.resource_generator.generate_wait_method("TrainingJob") == expected_output
        
    def test_generate_wait_for_status_method(self):
        expected_output = '''
@validate_call
def wait_for_status(
    self,
    status: Literal['InService', 'Creating', 'Updating', 'Failed', 'Deleting'],
    poll: int = 5,
    timeout: Optional[int] = None
) -> Optional[object]:
    start_time = time.time()

    while True:
        self.refresh()
        current_status = self.inference_component_status

        if status == current_status:
            return

        # TODO: Raise some generated TimeOutError
        if timeout is not None and time.time() - start_time >= timeout:
            raise Exception("Timeout exceeded. Final resource state - " + current_status)
        print("-", end="")
        time.sleep(poll)
'''
        assert self.resource_generator.generate_wait_for_status_method("InferenceComponent") == expected_output

