import os
from src.tools.resources_codegen import ResourcesCodeGen
from src.tools.constants import SERVICE_JSON_FILE_PATH

class TestGenerateResource:
    @classmethod
    def setup_class(cls):
        # Initialize parameters here
        cls.resource_generator = ResourcesCodeGen(SERVICE_JSON_FILE_PATH)

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
    compilation_job = cls(session, region)

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
    response = compilation_job.client.create_compilation_job(**operation_input_args)

    pprint(response)

    # deserialize the response

    return compilation_job
'''
        assert self.resource_generator.generate_create_method("CompilationJob") == expected_output

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
    app = cls(session, region)

    operation_input_args = {
        'DomainId': domain_id,
        'UserProfileName': user_profile_name,
        'SpaceName': space_name,
        'AppType': app_type,
        'AppName': app_name,
    }
    response = app.client.describe_app(**operation_input_args)

    pprint(response)

    # deserialize the response
    deserializer(app, response, 'DescribeAppResponse')
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
    response = self.client.describe_app(**operation_input_args)

    # deserialize the response
    deserializer(self, response, 'DescribeAppResponse')
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

