import os
import boto3
from botocore.config import Config

class Base:
    def __init__(self, session=None, region=None):
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        profile_name = os.getenv('AWS_PROFILE')

        if session is None:
            if all([aws_access_key_id, aws_secret_access_key, aws_session_token]):
                self.session = boto3.Session(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token
                )
            elif profile_name:
                self.session = boto3.Session(profile_name=profile_name)
            else:
                self.session = boto3.Session()

        self.region = region if region else os.getenv('AWS_REGION')

        # Create a custom config with the user agent
        custom_config = Config(
            region_name=self.region,
            user_agent_extra='SageMakerSDK/3.0'
        )

        self.client = self.session.client("sagemaker", config=custom_config)