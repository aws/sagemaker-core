import json
from src.tools.resources_codegen import ResourcesCodeGen
from src.tools.constants import SERVICE_JSON_FILE_PATH


class TestGenerateResource:
    @classmethod
    def setup_class(cls):
        # TODO: leverage pytest fixtures
        with open(SERVICE_JSON_FILE_PATH, "r") as file:
            service_json = json.load(file)

        # Initialize parameters here
        cls.resource_generator = ResourcesCodeGen(service_json)

    # create a unit test for generate_create_method()
    def test_generate_create_method(self):
        expected_output = """
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
    logger.debug("Creating compilation_job resource.")
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
"""
        assert (
            self.resource_generator.generate_create_method(
                "CompilationJob", needs_defaults_decorator=False
            )
            == expected_output
        )

    def test_generate_import_method(self):
        expected_output = """
@classmethod
def load(
    cls,
    hub_content_name: str,
    hub_content_type: str,
    document_schema_version: str,
    hub_name: str,
    hub_content_document: str,
    hub_content_version: Optional[str] = Unassigned(),
    hub_content_display_name: Optional[str] = Unassigned(),
    hub_content_description: Optional[str] = Unassigned(),
    hub_content_markdown: Optional[str] = Unassigned(),
    hub_content_search_keywords: Optional[List[str]] = Unassigned(),
    tags: Optional[List[Tag]] = Unassigned(),
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    logger.debug(f"Importing hub_content resource.")
    client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client

    operation_input_args = {
        'HubContentName': hub_content_name,
        'HubContentVersion': hub_content_version,
        'HubContentType': hub_content_type,
        'DocumentSchemaVersion': document_schema_version,
        'HubName': hub_name,
        'HubContentDisplayName': hub_content_display_name,
        'HubContentDescription': hub_content_description,
        'HubContentMarkdown': hub_content_markdown,
        'HubContentDocument': hub_content_document,
        'HubContentSearchKeywords': hub_content_search_keywords,
        'Tags': tags,
    }

    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = cls._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # import the resource
    response = client.import_hub_content(**operation_input_args)
    logger.debug(f"Response: {response}")

    return cls.get(hub_name=hub_name, hub_content_type=hub_content_type, hub_content_name=hub_content_name, session=session, region=region)
"""
        assert (
            self.resource_generator.generate_import_method("HubContent")
            == expected_output
        )

    def test_generate_update_method(self):
        expected_output = """
def update(self) -> Optional[object]:
    logger.debug("Creating endpoint resource.")
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
"""
        assert (
            self.resource_generator.generate_update_method("Endpoint")
            == expected_output
        )

    def test_generate_get_method(self):
        expected_output = """
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
"""
        assert self.resource_generator.generate_get_method("App") == expected_output

    def test_generate_refresh_method(self):
        expected_output = """
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
"""
        assert self.resource_generator.generate_refresh_method("App") == expected_output

    def test_generate_delete_method(self):
        expected_output = """
def delete(self) -> None:

    operation_input_args = {
        'CompilationJobName': self.compilation_job_name,
    }
    self.client.delete_compilation_job(**operation_input_args)
"""
        assert (
            self.resource_generator.generate_delete_method("CompilationJob")
            == expected_output
        )

    # create a unit test for generate_stop_method
    def test_generate_stop_method(self):
        expected_output = """
def stop(self) -> None:

    operation_input_args = {
        'CompilationJobName': self.compilation_job_name,
    }
    self.client.stop_compilation_job(**operation_input_args)
"""
        assert (
            self.resource_generator.generate_stop_method("CompilationJob")
            == expected_output
        )

    def test_generate_wait_method(self):
        expected_output = """
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
"""
        assert (
            self.resource_generator.generate_wait_method("TrainingJob")
            == expected_output
        )

    def test_generate_wait_for_status_method(self):
        expected_output = """
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
"""
        assert (
            self.resource_generator.generate_wait_for_status_method(
                "InferenceComponent"
            )
            == expected_output
        )

    def test_generate_invoke_method(self):
        expected_output = """
def invoke(self, 
    body: str,
    content_type: Optional[str] = Unassigned(),
    accept: Optional[str] = Unassigned(),
    custom_attributes: Optional[str] = Unassigned(),
    target_model: Optional[str] = Unassigned(),
    target_variant: Optional[str] = Unassigned(),
    target_container_hostname: Optional[str] = Unassigned(),
    inference_id: Optional[str] = Unassigned(),
    enable_explanations: Optional[str] = Unassigned(),
    inference_component_name: Optional[str] = Unassigned(),
) -> Optional[object]:
    logger.debug(f"Invoking endpoint resource.")
    client = SageMakerClient(service_name="sagemaker-runtime").client

    operation_input_args = {
        'EndpointName': self.endpoint_name,
        'Body': body,
        'ContentType': content_type,
        'Accept': accept,
        'CustomAttributes': custom_attributes,
        'TargetModel': target_model,
        'TargetVariant': target_variant,
        'TargetContainerHostname': target_container_hostname,
        'InferenceId': inference_id,
        'EnableExplanations': enable_explanations,
        'InferenceComponentName': inference_component_name,
    }
    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = Endpoint._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # create the resource
    response = client.invoke_endpoint(**operation_input_args)
    logger.debug(f"Response: {response}")

    return response
"""
        assert (
            self.resource_generator.generate_invoke_method(
                "Endpoint", resource_attributes=["endpoint_name"]
            )
            == expected_output
        )

    def test_generate_invoke_async_method(self):
        expected_output = """
def invoke_async(self, 
    input_location: str,
    content_type: Optional[str] = Unassigned(),
    accept: Optional[str] = Unassigned(),
    custom_attributes: Optional[str] = Unassigned(),
    inference_id: Optional[str] = Unassigned(),
    request_t_t_l_seconds: Optional[int] = Unassigned(),
    invocation_timeout_seconds: Optional[int] = Unassigned(),
) -> Optional[object]:
    logger.debug(f"Invoking endpoint resource Async.")
    client = SageMakerClient(service_name="sagemaker-runtime").client

    operation_input_args = {
        'EndpointName': self.endpoint_name,
        'ContentType': content_type,
        'Accept': accept,
        'CustomAttributes': custom_attributes,
        'InferenceId': inference_id,
        'InputLocation': input_location,
        'RequestTTLSeconds': request_t_t_l_seconds,
        'InvocationTimeoutSeconds': invocation_timeout_seconds,
    }
    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = Endpoint._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # create the resource
    response = client.invoke_endpoint_async(**operation_input_args)
    logger.debug(f"Response: {response}")

    return response
"""
        assert (
            self.resource_generator.generate_invoke_async_method(
                "Endpoint", resource_attributes=["endpoint_name"]
            )
            == expected_output
        )

    def test_generate_invoke_with_response_stream_method(self):
        expected_output = """
def invoke_with_response_stream(self, 
    body: str,
    content_type: Optional[str] = Unassigned(),
    accept: Optional[str] = Unassigned(),
    custom_attributes: Optional[str] = Unassigned(),
    target_variant: Optional[str] = Unassigned(),
    target_container_hostname: Optional[str] = Unassigned(),
    inference_id: Optional[str] = Unassigned(),
    inference_component_name: Optional[str] = Unassigned(),
) -> Optional[object]:
    logger.debug(f"Invoking endpoint resource with Response Stream.")
    client = SageMakerClient(service_name="sagemaker-runtime").client

    operation_input_args = {
        'EndpointName': self.endpoint_name,
        'Body': body,
        'ContentType': content_type,
        'Accept': accept,
        'CustomAttributes': custom_attributes,
        'TargetVariant': target_variant,
        'TargetContainerHostname': target_container_hostname,
        'InferenceId': inference_id,
        'InferenceComponentName': inference_component_name,
    }
    logger.debug(f"Input request: {operation_input_args}")
    # serialize the input request
    operation_input_args = Endpoint._serialize(operation_input_args)
    logger.debug(f"Serialized input request: {operation_input_args}")

    # create the resource
    response = client.invoke_endpoint_with_response_stream(**operation_input_args)
    logger.debug(f"Response: {response}")

    return response
"""
        assert (
            self.resource_generator.generate_invoke_with_response_stream_method(
                "Endpoint", resource_attributes=["endpoint_name"]
            )
            == expected_output
        )
