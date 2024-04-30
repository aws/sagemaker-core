import os
from src.tools.resources_codegen import ResourcesCodeGen
from src.tools.constants import SERVICE_JSON_FILE_PATH

class TestGenerateResource:
    @classmethod
    def setup_class(cls):
        # Initialize parameters here
        cls.resource_generator = ResourcesCodeGen(SERVICE_JSON_FILE_PATH)

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
def refresh(
    self
) -> Optional[object]:

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
