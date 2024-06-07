
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

import logging

import datetime
import time
import os
from pprint import pprint
from pydantic import validate_call
from typing import Dict, List, Literal, Optional, Union
from boto3.session import Session
from src.code_injection.codec import transform
from src.generated.utils import SageMakerClient, SageMakerRuntimeClient, ResourceIterator, Unassigned, snake_to_pascal, pascal_to_snake, is_not_primitive
from src.generated.intelligent_defaults_helper import load_default_configs_for_resource_name, get_config_value
from src.generated.shapes import *
from src.generated.exceptions import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    @classmethod
    def _serialize(cls, data: Dict) -> Dict:
        result = {}
        for attr, value in data.items():
            if isinstance(value, Unassigned):
                continue
            elif isinstance(value, List):
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
        return [
            cls._serialize(v)
                for v in value
                ]
    
    @classmethod
    def _serialize_dict(cls, value: Dict):
        return {
            k: cls._serialize(v)
            for k, v in value.items()
        }
    
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
                                                     operation_input_args={snake_to_pascal(k): v for k, v in list_item.__dict__.items()})
                    for list_item in value
                ]
            elif is_not_primitive(value):
                obj_dict = {snake_to_pascal(k): v for k, v in value.__dict__.items()}
                updated_args[arg] = Base.populate_chained_attributes(resource_name=type(value).__name__, operation_input_args=obj_dict)
        return updated_args

        
class Action(Base):
    """
    Action 
     Class representing resource Action
    Attributes
    ---------------------
    action_name:<p>The name of the action.</p>
    action_arn:<p>The Amazon Resource Name (ARN) of the action.</p>
    source:<p>The source of the action.</p>
    action_type:<p>The type of the action.</p>
    description:<p>The description of the action.</p>
    status:<p>The status of the action.</p>
    properties:<p>A list of the action's properties.</p>
    creation_time:<p>When the action was created.</p>
    created_by:
    last_modified_time:<p>When the action was last modified.</p>
    last_modified_by:
    metadata_properties:
    lineage_group_arn:<p>The Amazon Resource Name (ARN) of the lineage group.</p>
    
    """
    action_name: str
    action_arn: Optional[str] = Unassigned()
    source: Optional[ActionSource] = Unassigned()
    action_type: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'action_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        action_name: str,
        source: ActionSource,
        action_type: str,
        description: Optional[str] = Unassigned(),
        status: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Action"]:
        logger.debug("Creating action resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ActionName': action_name,
            'Source': source,
            'ActionType': action_type,
            'Description': description,
            'Status': status,
            'Properties': properties,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Action', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_action(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(action_name=action_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        action_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Action"]:
        operation_input_args = {
            'ActionName': action_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_action(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeActionResponse')
        action = cls(**transformed_response)
        return action
    
    def refresh(self) -> Optional["Action"]:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        client = SageMakerClient().client
        response = client.describe_action(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeActionResponse', self)
        return self
    
    def update(
        self,
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Action"]:
        logger.debug("Creating action resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ActionName': self.action_name,
            'Description': self.description,
            'Status': self.status,
            'Properties': self.properties,
            'PropertiesToRemove': properties_to_remove,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Action._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_action(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        self.client.delete_action(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        source_uri: Optional[str] = Unassigned(),
        action_type: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Action"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SourceUri': source_uri,
            'ActionType': action_type,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_actions',
            summaries_key='ActionSummaries',
            summary_name='ActionSummary',
            resource_cls=Action,
            list_method_kwargs=operation_input_args
        )


class Algorithm(Base):
    """
    Algorithm 
     Class representing resource Algorithm
    Attributes
    ---------------------
    algorithm_name:<p>The name of the algorithm being described.</p>
    algorithm_arn:<p>The Amazon Resource Name (ARN) of the algorithm.</p>
    creation_time:<p>A timestamp specifying when the algorithm was created.</p>
    training_specification:<p>Details about training jobs run by this algorithm.</p>
    algorithm_status:<p>The current status of the algorithm.</p>
    algorithm_status_details:<p>Details about the current status of the algorithm.</p>
    algorithm_description:<p>A brief summary about the algorithm.</p>
    inference_specification:<p>Details about inference jobs that the algorithm runs.</p>
    validation_specification:<p>Details about configurations for one or more training jobs that SageMaker runs to test the algorithm.</p>
    product_id:<p>The product identifier of the algorithm.</p>
    certify_for_marketplace:<p>Whether the algorithm is certified to be listed in Amazon Web Services Marketplace.</p>
    
    """
    algorithm_name: str
    algorithm_arn: Optional[str] = Unassigned()
    algorithm_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    training_specification: Optional[TrainingSpecification] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned()
    algorithm_status: Optional[str] = Unassigned()
    algorithm_status_details: Optional[AlgorithmStatusDetails] = Unassigned()
    product_id: Optional[str] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'algorithm_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "training_specification": {
            "additional_s3_data_source": {
              "s3_data_type": {
                "type": "string"
              },
              "s3_uri": {
                "type": "string"
              }
            }
          },
          "validation_specification": {
            "validation_role": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Algorithm", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        algorithm_name: str,
        training_specification: TrainingSpecification,
        algorithm_description: Optional[str] = Unassigned(),
        inference_specification: Optional[InferenceSpecification] = Unassigned(),
        validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned(),
        certify_for_marketplace: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Algorithm"]:
        logger.debug("Creating algorithm resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'AlgorithmName': algorithm_name,
            'AlgorithmDescription': algorithm_description,
            'TrainingSpecification': training_specification,
            'InferenceSpecification': inference_specification,
            'ValidationSpecification': validation_specification,
            'CertifyForMarketplace': certify_for_marketplace,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Algorithm', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_algorithm(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(algorithm_name=algorithm_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        algorithm_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Algorithm"]:
        operation_input_args = {
            'AlgorithmName': algorithm_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_algorithm(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAlgorithmOutput')
        algorithm = cls(**transformed_response)
        return algorithm
    
    def refresh(self) -> Optional["Algorithm"]:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        client = SageMakerClient().client
        response = client.describe_algorithm(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAlgorithmOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        self.client.delete_algorithm(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Algorithm"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.algorithm_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Algorithm", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Algorithm", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Algorithm"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_algorithms',
            summaries_key='AlgorithmSummaryList',
            summary_name='AlgorithmSummary',
            resource_cls=Algorithm,
            list_method_kwargs=operation_input_args
        )


class App(Base):
    """
    App 
     Class representing resource App
    Attributes
    ---------------------
    app_arn:<p>The Amazon Resource Name (ARN) of the app.</p>
    app_type:<p>The type of app.</p>
    app_name:<p>The name of the app.</p>
    domain_id:<p>The domain ID.</p>
    user_profile_name:<p>The user profile name.</p>
    space_name:<p>The name of the space. If this value is not set, then <code>UserProfileName</code> must be set.</p>
    status:<p>The status.</p>
    last_health_check_timestamp:<p>The timestamp of the last health check.</p>
    last_user_activity_timestamp:<p>The timestamp of the last user's activity. <code>LastUserActivityTimestamp</code> is also updated when SageMaker performs health checks without user activity. As a result, this value is set to the same value as <code>LastHealthCheckTimestamp</code>.</p>
    creation_time:<p>The creation time of the application.</p> <note> <p>After an application has been shut down for 24 hours, SageMaker deletes all metadata for the application. To be considered an update and retain application metadata, applications must be restarted within 24 hours after the previous application has been shut down. After this time window, creation of an application is considered a new application rather than an update of the previous application.</p> </note>
    failure_reason:<p>The failure reason.</p>
    resource_spec:<p>The instance type and the Amazon Resource Name (ARN) of the SageMaker image created on the instance.</p>
    
    """
    domain_id: str
    app_type: str
    app_name: str
    app_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_health_check_timestamp: Optional[datetime.datetime] = Unassigned()
    last_user_activity_timestamp: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    resource_spec: Optional[ResourceSpec] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'app_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        app_type: str,
        app_name: str,
        user_profile_name: Optional[Union[str, object]] = Unassigned(),
        space_name: Optional[Union[str, object]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        resource_spec: Optional[ResourceSpec] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["App"]:
        logger.debug("Creating app resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SpaceName': space_name,
            'AppType': app_type,
            'AppName': app_name,
            'Tags': tags,
            'ResourceSpec': resource_spec,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='App', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_app(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, app_type=app_type, app_name=app_name, session=session, region=region)
    
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
    ) -> Optional["App"]:
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
    
    def refresh(self) -> Optional["App"]:
    
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
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
            'SpaceName': self.space_name,
            'AppType': self.app_type,
            'AppName': self.app_name,
        }
        self.client.delete_app(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Deleted', 'Deleting', 'Failed', 'InService', 'Pending'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["App"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="App", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="App", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        domain_id_equals: Optional[str] = Unassigned(),
        user_profile_name_equals: Optional[str] = Unassigned(),
        space_name_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["App"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortOrder': sort_order,
            'SortBy': sort_by,
            'DomainIdEquals': domain_id_equals,
            'UserProfileNameEquals': user_profile_name_equals,
            'SpaceNameEquals': space_name_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_apps',
            summaries_key='Apps',
            summary_name='AppDetails',
            resource_cls=App,
            list_method_kwargs=operation_input_args
        )


class AppImageConfig(Base):
    """
    AppImageConfig 
     Class representing resource AppImageConfig
    Attributes
    ---------------------
    app_image_config_arn:<p>The ARN of the AppImageConfig.</p>
    app_image_config_name:<p>The name of the AppImageConfig.</p>
    creation_time:<p>When the AppImageConfig was created.</p>
    last_modified_time:<p>When the AppImageConfig was last modified.</p>
    kernel_gateway_image_config:<p>The configuration of a KernelGateway app.</p>
    jupyter_lab_app_image_config:<p>The configuration of the JupyterLab app.</p>
    
    """
    app_image_config_name: str
    app_image_config_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'app_image_config_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        app_image_config_name: str,
        tags: Optional[List[Tag]] = Unassigned(),
        kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned(),
        jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AppImageConfig"]:
        logger.debug("Creating app_image_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
            'Tags': tags,
            'KernelGatewayImageConfig': kernel_gateway_image_config,
            'JupyterLabAppImageConfig': jupyter_lab_app_image_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='AppImageConfig', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_app_image_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(app_image_config_name=app_image_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        app_image_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AppImageConfig"]:
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_app_image_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAppImageConfigResponse')
        app_image_config = cls(**transformed_response)
        return app_image_config
    
    def refresh(self) -> Optional["AppImageConfig"]:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_app_image_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAppImageConfigResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["AppImageConfig"]:
        logger.debug("Creating app_image_config resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
            'KernelGatewayImageConfig': self.kernel_gateway_image_config,
            'JupyterLabAppImageConfig': self.jupyter_lab_app_image_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = AppImageConfig._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_app_image_config(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        self.client.delete_app_image_config(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        modified_time_before: Optional[datetime.datetime] = Unassigned(),
        modified_time_after: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["AppImageConfig"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'ModifiedTimeBefore': modified_time_before,
            'ModifiedTimeAfter': modified_time_after,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_app_image_configs',
            summaries_key='AppImageConfigs',
            summary_name='AppImageConfigDetails',
            resource_cls=AppImageConfig,
            list_method_kwargs=operation_input_args
        )


class Artifact(Base):
    """
    Artifact 
     Class representing resource Artifact
    Attributes
    ---------------------
    artifact_name:<p>The name of the artifact.</p>
    artifact_arn:<p>The Amazon Resource Name (ARN) of the artifact.</p>
    source:<p>The source of the artifact.</p>
    artifact_type:<p>The type of the artifact.</p>
    properties:<p>A list of the artifact's properties.</p>
    creation_time:<p>When the artifact was created.</p>
    created_by:
    last_modified_time:<p>When the artifact was last modified.</p>
    last_modified_by:
    metadata_properties:
    lineage_group_arn:<p>The Amazon Resource Name (ARN) of the lineage group.</p>
    
    """
    artifact_arn: str
    artifact_name: Optional[str] = Unassigned()
    source: Optional[ArtifactSource] = Unassigned()
    artifact_type: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'artifact_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        source: ArtifactSource,
        artifact_type: str,
        artifact_name: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Artifact"]:
        logger.debug("Creating artifact resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ArtifactName': artifact_name,
            'Source': source,
            'ArtifactType': artifact_type,
            'Properties': properties,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Artifact', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_artifact(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(artifact_arn=response['ArtifactArn'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        artifact_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Artifact"]:
        operation_input_args = {
            'ArtifactArn': artifact_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_artifact(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeArtifactResponse')
        artifact = cls(**transformed_response)
        return artifact
    
    def refresh(self) -> Optional["Artifact"]:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
        }
        client = SageMakerClient().client
        response = client.describe_artifact(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeArtifactResponse', self)
        return self
    
    def update(
        self,
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Artifact"]:
        logger.debug("Creating artifact resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
            'ArtifactName': self.artifact_name,
            'Properties': self.properties,
            'PropertiesToRemove': properties_to_remove,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Artifact._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_artifact(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
            'Source': self.source,
        }
        self.client.delete_artifact(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        source_uri: Optional[str] = Unassigned(),
        artifact_type: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Artifact"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SourceUri': source_uri,
            'ArtifactType': artifact_type,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_artifacts',
            summaries_key='ArtifactSummaries',
            summary_name='ArtifactSummary',
            resource_cls=Artifact,
            list_method_kwargs=operation_input_args
        )


class AutoMLJob(Base):
    """
    AutoMLJob 
     Class representing resource AutoMLJob
    Attributes
    ---------------------
    auto_m_l_job_name:<p>Returns the name of the AutoML job.</p>
    auto_m_l_job_arn:<p>Returns the ARN of the AutoML job.</p>
    input_data_config:<p>Returns the input data configuration for the AutoML job.</p>
    output_data_config:<p>Returns the job's output data config.</p>
    role_arn:<p>The ARN of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.</p>
    creation_time:<p>Returns the creation time of the AutoML job.</p>
    last_modified_time:<p>Returns the job's last modified time.</p>
    auto_m_l_job_status:<p>Returns the status of the AutoML job.</p>
    auto_m_l_job_secondary_status:<p>Returns the secondary status of the AutoML job.</p>
    auto_m_l_job_objective:<p>Returns the job's objective.</p>
    problem_type:<p>Returns the job's problem type.</p>
    auto_m_l_job_config:<p>Returns the configuration for the AutoML job.</p>
    end_time:<p>Returns the end time of the AutoML job.</p>
    failure_reason:<p>Returns the failure reason for an AutoML job, when applicable.</p>
    partial_failure_reasons:<p>Returns a list of reasons for partial failures within an AutoML job.</p>
    best_candidate:<p>The best model candidate selected by SageMaker Autopilot using both the best objective metric and lowest <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-metrics-validation.html">InferenceLatency</a> for an experiment.</p>
    generate_candidate_definitions_only:<p>Indicates whether the output for an AutoML job generates candidate definitions only.</p>
    auto_m_l_job_artifacts:<p>Returns information on the job's artifacts found in <code>AutoMLJobArtifacts</code>.</p>
    resolved_attributes:<p>Contains <code>ProblemType</code>, <code>AutoMLJobObjective</code>, and <code>CompletionCriteria</code>. If you do not provide these values, they are inferred.</p>
    model_deploy_config:<p>Indicates whether the model was deployed automatically to an endpoint and the name of that endpoint if deployed automatically.</p>
    model_deploy_result:<p>Provides information about endpoint for the model deployment.</p>
    
    """
    auto_m_l_job_name: str
    auto_m_l_job_arn: Optional[str] = Unassigned()
    input_data_config: Optional[List[AutoMLChannel]] = Unassigned()
    output_data_config: Optional[AutoMLOutputDataConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    auto_m_l_job_config: Optional[AutoMLJobConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    auto_m_l_job_status: Optional[str] = Unassigned()
    auto_m_l_job_secondary_status: Optional[str] = Unassigned()
    generate_candidate_definitions_only: Optional[bool] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[ResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'auto_m_l_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "output_data_config": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "auto_m_l_job_config": {
            "security_config": {
              "volume_kms_key_id": {
                "type": "string"
              },
              "vpc_config": {
                "security_group_ids": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                },
                "subnets": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                }
              }
            },
            "candidate_generation_config": {
              "feature_specification_s3_uri": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "AutoMLJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        auto_m_l_job_name: str,
        input_data_config: List[AutoMLChannel],
        output_data_config: AutoMLOutputDataConfig,
        role_arn: str,
        problem_type: Optional[str] = Unassigned(),
        auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned(),
        auto_m_l_job_config: Optional[AutoMLJobConfig] = Unassigned(),
        generate_candidate_definitions_only: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        model_deploy_config: Optional[ModelDeployConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AutoMLJob"]:
        logger.debug("Creating auto_m_l_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
            'InputDataConfig': input_data_config,
            'OutputDataConfig': output_data_config,
            'ProblemType': problem_type,
            'AutoMLJobObjective': auto_m_l_job_objective,
            'AutoMLJobConfig': auto_m_l_job_config,
            'RoleArn': role_arn,
            'GenerateCandidateDefinitionsOnly': generate_candidate_definitions_only,
            'Tags': tags,
            'ModelDeployConfig': model_deploy_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='AutoMLJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_auto_m_l_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(auto_m_l_job_name=auto_m_l_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AutoMLJob"]:
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_auto_m_l_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAutoMLJobResponse')
        auto_m_l_job = cls(**transformed_response)
        return auto_m_l_job
    
    def refresh(self) -> Optional["AutoMLJob"]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAutoMLJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        self.client.stop_auto_m_l_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["AutoMLJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="AutoMLJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="AutoMLJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["AutoMLJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortOrder': sort_order,
            'SortBy': sort_by,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_auto_m_l_jobs',
            summaries_key='AutoMLJobSummaries',
            summary_name='AutoMLJobSummary',
            resource_cls=AutoMLJob,
            list_method_kwargs=operation_input_args
        )


class AutoMLJobV2(Base):
    """
    AutoMLJobV2 
     Class representing resource AutoMLJobV2
    Attributes
    ---------------------
    auto_m_l_job_name:<p>Returns the name of the AutoML job V2.</p>
    auto_m_l_job_arn:<p>Returns the Amazon Resource Name (ARN) of the AutoML job V2.</p>
    auto_m_l_job_input_data_config:<p>Returns an array of channel objects describing the input data and their location.</p>
    output_data_config:<p>Returns the job's output data config.</p>
    role_arn:<p>The ARN of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.</p>
    creation_time:<p>Returns the creation time of the AutoML job V2.</p>
    last_modified_time:<p>Returns the job's last modified time.</p>
    auto_m_l_job_status:<p>Returns the status of the AutoML job V2.</p>
    auto_m_l_job_secondary_status:<p>Returns the secondary status of the AutoML job V2.</p>
    auto_m_l_job_objective:<p>Returns the job's objective.</p>
    auto_m_l_problem_type_config:<p>Returns the configuration settings of the problem type set for the AutoML job V2.</p>
    auto_m_l_problem_type_config_name:<p>Returns the name of the problem type configuration set for the AutoML job V2.</p>
    end_time:<p>Returns the end time of the AutoML job V2.</p>
    failure_reason:<p>Returns the reason for the failure of the AutoML job V2, when applicable.</p>
    partial_failure_reasons:<p>Returns a list of reasons for partial failures within an AutoML job V2.</p>
    best_candidate:<p>Information about the candidate produced by an AutoML training job V2, including its status, steps, and other properties.</p>
    auto_m_l_job_artifacts:
    resolved_attributes:<p>Returns the resolved attributes used by the AutoML job V2.</p>
    model_deploy_config:<p>Indicates whether the model was deployed automatically to an endpoint and the name of that endpoint if deployed automatically.</p>
    model_deploy_result:<p>Provides information about endpoint for the model deployment.</p>
    data_split_config:<p>Returns the configuration settings of how the data are split into train and validation datasets.</p>
    security_config:<p>Returns the security configuration for traffic encryption or Amazon VPC settings.</p>
    
    """
    auto_m_l_job_name: str
    auto_m_l_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_input_data_config: Optional[List[AutoMLJobChannel]] = Unassigned()
    output_data_config: Optional[AutoMLOutputDataConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    auto_m_l_problem_type_config: Optional[AutoMLProblemTypeConfig] = Unassigned()
    auto_m_l_problem_type_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    auto_m_l_job_status: Optional[str] = Unassigned()
    auto_m_l_job_secondary_status: Optional[str] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[AutoMLResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned()
    security_config: Optional[AutoMLSecurityConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'auto_m_l_job_v2_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "output_data_config": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "auto_m_l_problem_type_config": {
            "time_series_forecasting_job_config": {
              "feature_specification_s3_uri": {
                "type": "string"
              }
            },
            "tabular_job_config": {
              "feature_specification_s3_uri": {
                "type": "string"
              }
            }
          },
          "security_config": {
            "volume_kms_key_id": {
              "type": "string"
            },
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "AutoMLJobV2", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        auto_m_l_job_name: Union[str, object],
        auto_m_l_job_input_data_config: List[AutoMLJobChannel],
        output_data_config: AutoMLOutputDataConfig,
        auto_m_l_problem_type_config: AutoMLProblemTypeConfig,
        role_arn: str,
        tags: Optional[List[Tag]] = Unassigned(),
        security_config: Optional[AutoMLSecurityConfig] = Unassigned(),
        auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned(),
        model_deploy_config: Optional[ModelDeployConfig] = Unassigned(),
        data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AutoMLJobV2"]:
        logger.debug("Creating auto_m_l_job_v2 resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
            'AutoMLJobInputDataConfig': auto_m_l_job_input_data_config,
            'OutputDataConfig': output_data_config,
            'AutoMLProblemTypeConfig': auto_m_l_problem_type_config,
            'RoleArn': role_arn,
            'Tags': tags,
            'SecurityConfig': security_config,
            'AutoMLJobObjective': auto_m_l_job_objective,
            'ModelDeployConfig': model_deploy_config,
            'DataSplitConfig': data_split_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='AutoMLJobV2', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_auto_m_l_job_v2(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(auto_m_l_job_name=auto_m_l_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["AutoMLJobV2"]:
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeAutoMLJobV2Response')
        auto_m_l_job_v2 = cls(**transformed_response)
        return auto_m_l_job_v2
    
    def refresh(self) -> Optional["AutoMLJobV2"]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeAutoMLJobV2Response', self)
        return self
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["AutoMLJobV2"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="AutoMLJobV2", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="AutoMLJobV2", status=current_status)
            print("-", end="")
            time.sleep(poll)


class Cluster(Base):
    """
    Cluster 
     Class representing resource Cluster
    Attributes
    ---------------------
    cluster_arn:<p>The Amazon Resource Name (ARN) of the SageMaker HyperPod cluster.</p>
    cluster_status:<p>The status of the SageMaker HyperPod cluster.</p>
    instance_groups:<p>The instance groups of the SageMaker HyperPod cluster.</p>
    cluster_name:<p>The name of the SageMaker HyperPod cluster.</p>
    creation_time:<p>The time when the SageMaker Cluster is created.</p>
    failure_message:<p>The failure message of the SageMaker HyperPod cluster.</p>
    vpc_config:
    
    """
    cluster_name: str
    cluster_arn: Optional[str] = Unassigned()
    cluster_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_message: Optional[str] = Unassigned()
    instance_groups: Optional[List[ClusterInstanceGroupDetails]] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'cluster_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "vpc_config": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "subnets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Cluster", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        cluster_name: str,
        instance_groups: List[ClusterInstanceGroupSpecification],
        vpc_config: Optional[VpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Cluster"]:
        logger.debug("Creating cluster resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ClusterName': cluster_name,
            'InstanceGroups': instance_groups,
            'VpcConfig': vpc_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Cluster', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_cluster(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(cluster_name=cluster_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        cluster_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Cluster"]:
        operation_input_args = {
            'ClusterName': cluster_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_cluster(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeClusterResponse')
        cluster = cls(**transformed_response)
        return cluster
    
    def refresh(self) -> Optional["Cluster"]:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        client = SageMakerClient().client
        response = client.describe_cluster(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeClusterResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["Cluster"]:
        logger.debug("Creating cluster resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
            'InstanceGroups': self.instance_groups,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Cluster._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_cluster(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        self.client.delete_cluster(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Creating', 'Deleting', 'Failed', 'InService', 'RollingBack', 'SystemUpdating', 'Updating'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Cluster"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.cluster_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Cluster", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Cluster", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Cluster"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_clusters',
            summaries_key='ClusterSummaries',
            summary_name='ClusterSummary',
            resource_cls=Cluster,
            list_method_kwargs=operation_input_args
        )


class CodeRepository(Base):
    """
    CodeRepository 
     Class representing resource CodeRepository
    Attributes
    ---------------------
    code_repository_name:<p>The name of the Git repository.</p>
    code_repository_arn:<p>The Amazon Resource Name (ARN) of the Git repository.</p>
    creation_time:<p>The date and time that the repository was created.</p>
    last_modified_time:<p>The date and time that the repository was last changed.</p>
    git_config:<p>Configuration details about the repository, including the URL where the repository is located, the default branch, and the Amazon Resource Name (ARN) of the Amazon Web Services Secrets Manager secret that contains the credentials used to access the repository.</p>
    
    """
    code_repository_name: str
    code_repository_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    git_config: Optional[GitConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'code_repository_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        code_repository_name: str,
        git_config: GitConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["CodeRepository"]:
        logger.debug("Creating code_repository resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
            'GitConfig': git_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='CodeRepository', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_code_repository(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(code_repository_name=code_repository_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        code_repository_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["CodeRepository"]:
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_code_repository(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeCodeRepositoryOutput')
        code_repository = cls(**transformed_response)
        return code_repository
    
    def refresh(self) -> Optional["CodeRepository"]:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        client = SageMakerClient().client
        response = client.describe_code_repository(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeCodeRepositoryOutput', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["CodeRepository"]:
        logger.debug("Creating code_repository resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
            'GitConfig': self.git_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = CodeRepository._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_code_repository(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        self.client.delete_code_repository(**operation_input_args)


class CompilationJob(Base):
    """
    CompilationJob 
     Class representing resource CompilationJob
    Attributes
    ---------------------
    compilation_job_name:<p>The name of the model compilation job.</p>
    compilation_job_arn:<p>The Amazon Resource Name (ARN) of the model compilation job.</p>
    compilation_job_status:<p>The status of the model compilation job.</p>
    stopping_condition:<p>Specifies a limit to how long a model compilation job can run. When the job reaches the time limit, Amazon SageMaker ends the compilation job. Use this API to cap model training costs.</p>
    creation_time:<p>The time that the model compilation job was created.</p>
    last_modified_time:<p>The time that the status of the model compilation job was last modified.</p>
    failure_reason:<p>If a model compilation job failed, the reason it failed. </p>
    model_artifacts:<p>Information about the location in Amazon S3 that has been configured for storing the model artifacts used in the compilation job.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker assumes to perform the model compilation job.</p>
    input_config:<p>Information about the location in Amazon S3 of the input model artifacts, the name and shape of the expected data inputs, and the framework in which the model was trained.</p>
    output_config:<p>Information about the output location for the compiled model and the target device that the model runs on.</p>
    compilation_start_time:<p>The time when the model compilation job started the <code>CompilationJob</code> instances. </p> <p>You are billed for the time between this timestamp and the timestamp in the <code>CompilationEndTime</code> field. In Amazon CloudWatch Logs, the start time might be later than this time. That's because it takes time to download the compilation job, which depends on the size of the compilation job container. </p>
    compilation_end_time:<p>The time when the model compilation job on a compilation job instance ended. For a successful or stopped job, this is when the job's model artifacts have finished uploading. For a failed job, this is when Amazon SageMaker detected that the job failed. </p>
    inference_image:<p>The inference image to use when compiling a model. Specify an image only if the target device is a cloud instance.</p>
    model_package_version_arn:<p>The Amazon Resource Name (ARN) of the versioned model package that was provided to SageMaker Neo when you initiated a compilation job.</p>
    model_digests:<p>Provides a BLAKE2 hash value that identifies the compiled model artifacts in Amazon S3.</p>
    vpc_config:<p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> object that specifies the VPC that you want your compilation job to connect to. Control access to your models by configuring the VPC. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/neo-vpc.html">Protect Compilation Jobs by Using an Amazon Virtual Private Cloud</a>.</p>
    derived_information:<p>Information that SageMaker Neo automatically derived about the model.</p>
    
    """
    compilation_job_name: str
    compilation_job_arn: Optional[str] = Unassigned()
    compilation_job_status: Optional[str] = Unassigned()
    compilation_start_time: Optional[datetime.datetime] = Unassigned()
    compilation_end_time: Optional[datetime.datetime] = Unassigned()
    stopping_condition: Optional[StoppingCondition] = Unassigned()
    inference_image: Optional[str] = Unassigned()
    model_package_version_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    model_artifacts: Optional[ModelArtifacts] = Unassigned()
    model_digests: Optional[ModelDigests] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    input_config: Optional[InputConfig] = Unassigned()
    output_config: Optional[OutputConfig] = Unassigned()
    vpc_config: Optional[NeoVpcConfig] = Unassigned()
    derived_information: Optional[DerivedInformation] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'compilation_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "model_artifacts": {
            "s3_model_artifacts": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "input_config": {
            "s3_uri": {
              "type": "string"
            }
          },
          "output_config": {
            "s3_output_location": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "vpc_config": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "subnets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "CompilationJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
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
    ) -> Optional["CompilationJob"]:
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
        
        operation_input_args = Base.populate_chained_attributes(resource_name='CompilationJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_compilation_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(compilation_job_name=compilation_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        compilation_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["CompilationJob"]:
        operation_input_args = {
            'CompilationJobName': compilation_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_compilation_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeCompilationJobResponse')
        compilation_job = cls(**transformed_response)
        return compilation_job
    
    def refresh(self) -> Optional["CompilationJob"]:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_compilation_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeCompilationJobResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        self.client.delete_compilation_job(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        self.client.stop_compilation_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["CompilationJob"]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.compilation_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="CompilationJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="CompilationJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["CompilationJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_compilation_jobs',
            summaries_key='CompilationJobSummaries',
            summary_name='CompilationJobSummary',
            resource_cls=CompilationJob,
            list_method_kwargs=operation_input_args
        )


class Context(Base):
    """
    Context 
     Class representing resource Context
    Attributes
    ---------------------
    context_name:<p>The name of the context.</p>
    context_arn:<p>The Amazon Resource Name (ARN) of the context.</p>
    source:<p>The source of the context.</p>
    context_type:<p>The type of the context.</p>
    description:<p>The description of the context.</p>
    properties:<p>A list of the context's properties.</p>
    creation_time:<p>When the context was created.</p>
    created_by:
    last_modified_time:<p>When the context was last modified.</p>
    last_modified_by:
    lineage_group_arn:<p>The Amazon Resource Name (ARN) of the lineage group.</p>
    
    """
    context_name: str
    context_arn: Optional[str] = Unassigned()
    source: Optional[ContextSource] = Unassigned()
    context_type: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'context_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        context_name: str,
        source: ContextSource,
        context_type: str,
        description: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Context"]:
        logger.debug("Creating context resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ContextName': context_name,
            'Source': source,
            'ContextType': context_type,
            'Description': description,
            'Properties': properties,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Context', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_context(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(context_name=context_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        context_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Context"]:
        operation_input_args = {
            'ContextName': context_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_context(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeContextResponse')
        context = cls(**transformed_response)
        return context
    
    def refresh(self) -> Optional["Context"]:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        client = SageMakerClient().client
        response = client.describe_context(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeContextResponse', self)
        return self
    
    def update(
        self,
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Context"]:
        logger.debug("Creating context resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ContextName': self.context_name,
            'Description': self.description,
            'Properties': self.properties,
            'PropertiesToRemove': properties_to_remove,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Context._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_context(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        self.client.delete_context(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        source_uri: Optional[str] = Unassigned(),
        context_type: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Context"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SourceUri': source_uri,
            'ContextType': context_type,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_contexts',
            summaries_key='ContextSummaries',
            summary_name='ContextSummary',
            resource_cls=Context,
            list_method_kwargs=operation_input_args
        )


class DataQualityJobDefinition(Base):
    """
    DataQualityJobDefinition 
     Class representing resource DataQualityJobDefinition
    Attributes
    ---------------------
    job_definition_arn:<p>The Amazon Resource Name (ARN) of the data quality monitoring job definition.</p>
    job_definition_name:<p>The name of the data quality monitoring job definition.</p>
    creation_time:<p>The time that the data quality monitoring job definition was created.</p>
    data_quality_app_specification:<p>Information about the container that runs the data quality monitoring job.</p>
    data_quality_job_input:<p>The list of inputs for the data quality monitoring job. Currently endpoints are supported.</p>
    data_quality_job_output_config:
    job_resources:
    role_arn:<p>The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.</p>
    data_quality_baseline_config:<p>The constraints and baselines for the data quality monitoring job definition.</p>
    network_config:<p>The networking configuration for the data quality monitoring job.</p>
    stopping_condition:
    
    """
    job_definition_name: str
    job_definition_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    data_quality_baseline_config: Optional[DataQualityBaselineConfig] = Unassigned()
    data_quality_app_specification: Optional[DataQualityAppSpecification] = Unassigned()
    data_quality_job_input: Optional[DataQualityJobInput] = Unassigned()
    data_quality_job_output_config: Optional[MonitoringOutputConfig] = Unassigned()
    job_resources: Optional[MonitoringResources] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'data_quality_job_definition_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "data_quality_job_input": {
            "endpoint_input": {
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            },
            "batch_transform_input": {
              "data_captured_destination_s3_uri": {
                "type": "string"
              },
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            }
          },
          "data_quality_job_output_config": {
            "kms_key_id": {
              "type": "string"
            }
          },
          "job_resources": {
            "cluster_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            }
          },
          "role_arn": {
            "type": "string"
          },
          "data_quality_baseline_config": {
            "constraints_resource": {
              "s3_uri": {
                "type": "string"
              }
            },
            "statistics_resource": {
              "s3_uri": {
                "type": "string"
              }
            }
          },
          "network_config": {
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "DataQualityJobDefinition", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        job_definition_name: str,
        data_quality_app_specification: DataQualityAppSpecification,
        data_quality_job_input: DataQualityJobInput,
        data_quality_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        data_quality_baseline_config: Optional[DataQualityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["DataQualityJobDefinition"]:
        logger.debug("Creating data_quality_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'DataQualityBaselineConfig': data_quality_baseline_config,
            'DataQualityAppSpecification': data_quality_app_specification,
            'DataQualityJobInput': data_quality_job_input,
            'DataQualityJobOutputConfig': data_quality_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='DataQualityJobDefinition', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_data_quality_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["DataQualityJobDefinition"]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_data_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDataQualityJobDefinitionResponse')
        data_quality_job_definition = cls(**transformed_response)
        return data_quality_job_definition
    
    def refresh(self) -> Optional["DataQualityJobDefinition"]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_data_quality_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDataQualityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_data_quality_job_definition(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        endpoint_name: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["DataQualityJobDefinition"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'EndpointName': endpoint_name,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
        custom_key_mapping = {"monitoring_job_definition_name": "job_definition_name", "monitoring_job_definition_arn": "job_definition_arn"}
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_data_quality_job_definitions',
            summaries_key='JobDefinitionSummaries',
            summary_name='MonitoringJobDefinitionSummary',
            resource_cls=DataQualityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args
        )


class DeviceFleet(Base):
    """
    DeviceFleet 
     Class representing resource DeviceFleet
    Attributes
    ---------------------
    device_fleet_name:<p>The name of the fleet.</p>
    device_fleet_arn:<p>The The Amazon Resource Name (ARN) of the fleet.</p>
    output_config:<p>The output configuration for storing sampled data.</p>
    creation_time:<p>Timestamp of when the device fleet was created.</p>
    last_modified_time:<p>Timestamp of when the device fleet was last updated.</p>
    description:<p>A description of the fleet.</p>
    role_arn:<p>The Amazon Resource Name (ARN) that has access to Amazon Web Services Internet of Things (IoT).</p>
    iot_role_alias:<p>The Amazon Resource Name (ARN) alias created in Amazon Web Services Internet of Things (IoT).</p>
    
    """
    device_fleet_name: str
    device_fleet_arn: Optional[str] = Unassigned()
    output_config: Optional[EdgeOutputConfig] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    iot_role_alias: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'device_fleet_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "output_config": {
            "s3_output_location": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "iot_role_alias": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "DeviceFleet", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        device_fleet_name: str,
        output_config: EdgeOutputConfig,
        role_arn: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        enable_iot_role_alias: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["DeviceFleet"]:
        logger.debug("Creating device_fleet resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
            'RoleArn': role_arn,
            'Description': description,
            'OutputConfig': output_config,
            'Tags': tags,
            'EnableIotRoleAlias': enable_iot_role_alias,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='DeviceFleet', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_device_fleet(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(device_fleet_name=device_fleet_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        device_fleet_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["DeviceFleet"]:
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_device_fleet(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDeviceFleetResponse')
        device_fleet = cls(**transformed_response)
        return device_fleet
    
    def refresh(self) -> Optional["DeviceFleet"]:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        client = SageMakerClient().client
        response = client.describe_device_fleet(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDeviceFleetResponse', self)
        return self
    
    def update(
        self,
        enable_iot_role_alias: Optional[bool] = Unassigned(),
    ) -> Optional["DeviceFleet"]:
        logger.debug("Creating device_fleet resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
            'RoleArn': self.role_arn,
            'Description': self.description,
            'OutputConfig': self.output_config,
            'EnableIotRoleAlias': enable_iot_role_alias,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = DeviceFleet._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_device_fleet(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        self.client.delete_device_fleet(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["DeviceFleet"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_device_fleets',
            summaries_key='DeviceFleetSummaries',
            summary_name='DeviceFleetSummary',
            resource_cls=DeviceFleet,
            list_method_kwargs=operation_input_args
        )


class Domain(Base):
    """
    Domain 
     Class representing resource Domain
    Attributes
    ---------------------
    domain_arn:<p>The domain's Amazon Resource Name (ARN).</p>
    domain_id:<p>The domain ID.</p>
    domain_name:<p>The domain name.</p>
    home_efs_file_system_id:<p>The ID of the Amazon Elastic File System managed by this Domain.</p>
    single_sign_on_managed_application_instance_id:<p>The IAM Identity Center managed application instance ID.</p>
    single_sign_on_application_arn:<p>The ARN of the application managed by SageMaker in IAM Identity Center. This value is only returned for domains created after October 1, 2023.</p>
    status:<p>The status.</p>
    creation_time:<p>The creation time.</p>
    last_modified_time:<p>The last modified time.</p>
    failure_reason:<p>The failure reason.</p>
    security_group_id_for_domain_boundary:<p>The ID of the security group that authorizes traffic between the <code>RSessionGateway</code> apps and the <code>RStudioServerPro</code> app.</p>
    auth_mode:<p>The domain's authentication mode.</p>
    default_user_settings:<p>Settings which are applied to UserProfiles in this domain if settings are not explicitly specified in a given UserProfile. </p>
    domain_settings:<p>A collection of <code>Domain</code> settings.</p>
    app_network_access_type:<p>Specifies the VPC used for non-EFS traffic. The default value is <code>PublicInternetOnly</code>.</p> <ul> <li> <p> <code>PublicInternetOnly</code> - Non-EFS traffic is through a VPC managed by Amazon SageMaker, which allows direct internet access</p> </li> <li> <p> <code>VpcOnly</code> - All traffic is through the specified VPC and subnets</p> </li> </ul>
    home_efs_file_system_kms_key_id:<p>Use <code>KmsKeyId</code>.</p>
    subnet_ids:<p>The VPC subnets that the domain uses for communication.</p>
    url:<p>The domain's URL.</p>
    vpc_id:<p>The ID of the Amazon Virtual Private Cloud (VPC) that the domain uses for communication.</p>
    kms_key_id:<p>The Amazon Web Services KMS customer managed key used to encrypt the EFS volume attached to the domain.</p>
    app_security_group_management:<p>The entity that creates and manages the required security groups for inter-app communication in <code>VPCOnly</code> mode. Required when <code>CreateDomain.AppNetworkAccessType</code> is <code>VPCOnly</code> and <code>DomainSettings.RStudioServerProDomainSettings.DomainExecutionRoleArn</code> is provided.</p>
    default_space_settings:<p>The default settings used to create a space.</p>
    
    """
    domain_id: str
    domain_arn: Optional[str] = Unassigned()
    domain_name: Optional[str] = Unassigned()
    home_efs_file_system_id: Optional[str] = Unassigned()
    single_sign_on_managed_application_instance_id: Optional[str] = Unassigned()
    single_sign_on_application_arn: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    security_group_id_for_domain_boundary: Optional[str] = Unassigned()
    auth_mode: Optional[str] = Unassigned()
    default_user_settings: Optional[UserSettings] = Unassigned()
    domain_settings: Optional[DomainSettings] = Unassigned()
    app_network_access_type: Optional[str] = Unassigned()
    home_efs_file_system_kms_key_id: Optional[str] = Unassigned()
    subnet_ids: Optional[List[str]] = Unassigned()
    url: Optional[str] = Unassigned()
    vpc_id: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    app_security_group_management: Optional[str] = Unassigned()
    default_space_settings: Optional[DefaultSpaceSettings] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'domain_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "security_group_id_for_domain_boundary": {
            "type": "string"
          },
          "default_user_settings": {
            "execution_role": {
              "type": "string"
            },
            "security_groups": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "sharing_settings": {
              "s3_output_path": {
                "type": "string"
              },
              "s3_kms_key_id": {
                "type": "string"
              }
            },
            "canvas_app_settings": {
              "time_series_forecasting_settings": {
                "amazon_forecast_role_arn": {
                  "type": "string"
                }
              },
              "model_register_settings": {
                "cross_account_model_register_role_arn": {
                  "type": "string"
                }
              },
              "workspace_settings": {
                "s3_artifact_path": {
                  "type": "string"
                },
                "s3_kms_key_id": {
                  "type": "string"
                }
              },
              "generative_ai_settings": {
                "amazon_bedrock_role_arn": {
                  "type": "string"
                }
              }
            }
          },
          "domain_settings": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "r_studio_server_pro_domain_settings": {
              "domain_execution_role_arn": {
                "type": "string"
              }
            },
            "execution_role_identity_config": {
              "type": "string"
            }
          },
          "home_efs_file_system_kms_key_id": {
            "type": "string"
          },
          "subnet_ids": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "kms_key_id": {
            "type": "string"
          },
          "app_security_group_management": {
            "type": "string"
          },
          "default_space_settings": {
            "execution_role": {
              "type": "string"
            },
            "security_groups": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Domain", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        domain_name: str,
        auth_mode: str,
        default_user_settings: UserSettings,
        subnet_ids: List[str],
        vpc_id: str,
        domain_settings: Optional[DomainSettings] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        app_network_access_type: Optional[str] = Unassigned(),
        home_efs_file_system_kms_key_id: Optional[str] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        app_security_group_management: Optional[str] = Unassigned(),
        default_space_settings: Optional[DefaultSpaceSettings] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Domain"]:
        logger.debug("Creating domain resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'DomainName': domain_name,
            'AuthMode': auth_mode,
            'DefaultUserSettings': default_user_settings,
            'DomainSettings': domain_settings,
            'SubnetIds': subnet_ids,
            'VpcId': vpc_id,
            'Tags': tags,
            'AppNetworkAccessType': app_network_access_type,
            'HomeEfsFileSystemKmsKeyId': home_efs_file_system_kms_key_id,
            'KmsKeyId': kms_key_id,
            'AppSecurityGroupManagement': app_security_group_management,
            'DefaultSpaceSettings': default_space_settings,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Domain', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_domain(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=response['DomainId'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Domain"]:
        operation_input_args = {
            'DomainId': domain_id,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_domain(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeDomainResponse')
        domain = cls(**transformed_response)
        return domain
    
    def refresh(self) -> Optional["Domain"]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
        }
        client = SageMakerClient().client
        response = client.describe_domain(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeDomainResponse', self)
        return self
    
    def update(
        self,
        domain_settings_for_update: Optional[DomainSettingsForUpdate] = Unassigned(),
    ) -> Optional["Domain"]:
        logger.debug("Creating domain resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'DefaultUserSettings': self.default_user_settings,
            'DomainSettingsForUpdate': domain_settings_for_update,
            'AppSecurityGroupManagement': self.app_security_group_management,
            'DefaultSpaceSettings': self.default_space_settings,
            'SubnetIds': self.subnet_ids,
            'AppNetworkAccessType': self.app_network_access_type,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Domain._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_domain(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'RetentionPolicy': self.retention_policy,
        }
        self.client.delete_domain(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Domain"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Domain", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Domain", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Domain"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
    
        return ResourceIterator(
            client=client,
            list_method='list_domains',
            summaries_key='Domains',
            summary_name='DomainDetails',
            resource_cls=Domain
        )


class EdgeDeploymentPlan(Base):
    """
    EdgeDeploymentPlan 
     Class representing resource EdgeDeploymentPlan
    Attributes
    ---------------------
    edge_deployment_plan_arn:<p>The ARN of edge deployment plan.</p>
    edge_deployment_plan_name:<p>The name of the edge deployment plan.</p>
    model_configs:<p>List of models associated with the edge deployment plan.</p>
    device_fleet_name:<p>The device fleet used for this edge deployment plan.</p>
    stages:<p>List of stages in the edge deployment plan.</p>
    edge_deployment_success:<p>The number of edge devices with the successful deployment.</p>
    edge_deployment_pending:<p>The number of edge devices yet to pick up deployment, or in progress.</p>
    edge_deployment_failed:<p>The number of edge devices that failed the deployment.</p>
    next_token:<p>Token to use when calling the next set of stages in the edge deployment plan.</p>
    creation_time:<p>The time when the edge deployment plan was created.</p>
    last_modified_time:<p>The time when the edge deployment plan was last updated.</p>
    
    """
    edge_deployment_plan_name: str
    edge_deployment_plan_arn: Optional[str] = Unassigned()
    model_configs: Optional[List[EdgeDeploymentModelConfig]] = Unassigned()
    device_fleet_name: Optional[str] = Unassigned()
    edge_deployment_success: Optional[int] = Unassigned()
    edge_deployment_pending: Optional[int] = Unassigned()
    edge_deployment_failed: Optional[int] = Unassigned()
    stages: Optional[List[DeploymentStageStatusSummary]] = Unassigned()
    next_token: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'edge_deployment_plan_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        edge_deployment_plan_name: str,
        model_configs: List[EdgeDeploymentModelConfig],
        device_fleet_name: Union[str, object],
        stages: Optional[List[DeploymentStage]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgeDeploymentPlan"]:
        logger.debug("Creating edge_deployment_plan resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'ModelConfigs': model_configs,
            'DeviceFleetName': device_fleet_name,
            'Stages': stages,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='EdgeDeploymentPlan', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_edge_deployment_plan(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(edge_deployment_plan_name=edge_deployment_plan_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        edge_deployment_plan_name: str,
        next_token: Optional[str] = Unassigned(),
        max_results: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgeDeploymentPlan"]:
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'NextToken': next_token,
            'MaxResults': max_results,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_edge_deployment_plan(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEdgeDeploymentPlanResponse')
        edge_deployment_plan = cls(**transformed_response)
        return edge_deployment_plan
    
    def refresh(self) -> Optional["EdgeDeploymentPlan"]:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
            'NextToken': self.next_token,
            'MaxResults': self.max_results,
        }
        client = SageMakerClient().client
        response = client.describe_edge_deployment_plan(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEdgeDeploymentPlanResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
        }
        self.client.delete_edge_deployment_plan(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        device_fleet_name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["EdgeDeploymentPlan"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'DeviceFleetNameContains': device_fleet_name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_edge_deployment_plans',
            summaries_key='EdgeDeploymentPlanSummaries',
            summary_name='EdgeDeploymentPlanSummary',
            resource_cls=EdgeDeploymentPlan,
            list_method_kwargs=operation_input_args
        )


class EdgePackagingJob(Base):
    """
    EdgePackagingJob 
     Class representing resource EdgePackagingJob
    Attributes
    ---------------------
    edge_packaging_job_arn:<p>The Amazon Resource Name (ARN) of the edge packaging job.</p>
    edge_packaging_job_name:<p>The name of the edge packaging job.</p>
    edge_packaging_job_status:<p>The current status of the packaging job.</p>
    compilation_job_name:<p>The name of the SageMaker Neo compilation job that is used to locate model artifacts that are being packaged.</p>
    model_name:<p>The name of the model.</p>
    model_version:<p>The version of the model.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to download and upload the model, and to contact Neo.</p>
    output_config:<p>The output configuration for the edge packaging job.</p>
    resource_key:<p>The Amazon Web Services KMS key to use when encrypting the EBS volume the job run on.</p>
    edge_packaging_job_status_message:<p>Returns a message describing the job status and error messages.</p>
    creation_time:<p>The timestamp of when the packaging job was created.</p>
    last_modified_time:<p>The timestamp of when the job was last updated.</p>
    model_artifact:<p>The Amazon Simple Storage (S3) URI where model artifacts ares stored.</p>
    model_signature:<p>The signature document of files in the model artifact.</p>
    preset_deployment_output:<p>The output of a SageMaker Edge Manager deployable resource.</p>
    
    """
    edge_packaging_job_name: str
    edge_packaging_job_arn: Optional[str] = Unassigned()
    compilation_job_name: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    model_version: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    output_config: Optional[EdgeOutputConfig] = Unassigned()
    resource_key: Optional[str] = Unassigned()
    edge_packaging_job_status: Optional[str] = Unassigned()
    edge_packaging_job_status_message: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    model_artifact: Optional[str] = Unassigned()
    model_signature: Optional[str] = Unassigned()
    preset_deployment_output: Optional[EdgePresetDeploymentOutput] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'edge_packaging_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "role_arn": {
            "type": "string"
          },
          "output_config": {
            "s3_output_location": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "EdgePackagingJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        edge_packaging_job_name: str,
        compilation_job_name: Union[str, object],
        model_name: Union[str, object],
        model_version: str,
        role_arn: str,
        output_config: EdgeOutputConfig,
        resource_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgePackagingJob"]:
        logger.debug("Creating edge_packaging_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'EdgePackagingJobName': edge_packaging_job_name,
            'CompilationJobName': compilation_job_name,
            'ModelName': model_name,
            'ModelVersion': model_version,
            'RoleArn': role_arn,
            'OutputConfig': output_config,
            'ResourceKey': resource_key,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='EdgePackagingJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_edge_packaging_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(edge_packaging_job_name=edge_packaging_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        edge_packaging_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgePackagingJob"]:
        operation_input_args = {
            'EdgePackagingJobName': edge_packaging_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_edge_packaging_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEdgePackagingJobResponse')
        edge_packaging_job = cls(**transformed_response)
        return edge_packaging_job
    
    def refresh(self) -> Optional["EdgePackagingJob"]:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_edge_packaging_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEdgePackagingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        self.client.stop_edge_packaging_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["EdgePackagingJob"]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.edge_packaging_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="EdgePackagingJob", status=current_status, reason=self.edge_packaging_job_status_message)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="EdgePackagingJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        model_name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["EdgePackagingJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'ModelNameContains': model_name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_edge_packaging_jobs',
            summaries_key='EdgePackagingJobSummaries',
            summary_name='EdgePackagingJobSummary',
            resource_cls=EdgePackagingJob,
            list_method_kwargs=operation_input_args
        )


class Endpoint(Base):
    """
    Endpoint 
     Class representing resource Endpoint
    Attributes
    ---------------------
    endpoint_name:<p>Name of the endpoint.</p>
    endpoint_arn:<p>The Amazon Resource Name (ARN) of the endpoint.</p>
    endpoint_status:<p>The status of the endpoint.</p> <ul> <li> <p> <code>OutOfService</code>: Endpoint is not available to take incoming requests.</p> </li> <li> <p> <code>Creating</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpoint.html">CreateEndpoint</a> is executing.</p> </li> <li> <p> <code>Updating</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html">UpdateEndpoint</a> or <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> is executing.</p> </li> <li> <p> <code>SystemUpdating</code>: Endpoint is undergoing maintenance and cannot be updated or deleted or re-scaled until it has completed. This maintenance operation does not change any customer-specified values such as VPC config, KMS encryption, model, instance type, or instance count.</p> </li> <li> <p> <code>RollingBack</code>: Endpoint fails to scale up or down or change its variant weight and is in the process of rolling back to its previous configuration. Once the rollback completes, endpoint returns to an <code>InService</code> status. This transitional status only applies to an endpoint that has autoscaling enabled and is undergoing variant weight or capacity changes as part of an <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> call or when the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> operation is called explicitly.</p> </li> <li> <p> <code>InService</code>: Endpoint is available to process incoming requests.</p> </li> <li> <p> <code>Deleting</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DeleteEndpoint.html">DeleteEndpoint</a> is executing.</p> </li> <li> <p> <code>Failed</code>: Endpoint could not be created, updated, or re-scaled. Use the <code>FailureReason</code> value returned by <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeEndpoint.html">DescribeEndpoint</a> for information about the failure. <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DeleteEndpoint.html">DeleteEndpoint</a> is the only operation that can be performed on a failed endpoint.</p> </li> <li> <p> <code>UpdateRollbackFailed</code>: Both the rolling deployment and auto-rollback failed. Your endpoint is in service with a mix of the old and new endpoint configurations. For information about how to remedy this issue and restore the endpoint's status to <code>InService</code>, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/deployment-guardrails-rolling.html">Rolling Deployments</a>.</p> </li> </ul>
    creation_time:<p>A timestamp that shows when the endpoint was created.</p>
    last_modified_time:<p>A timestamp that shows when the endpoint was last modified.</p>
    endpoint_config_name:<p>The name of the endpoint configuration associated with this endpoint.</p>
    production_variants:<p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ProductionVariantSummary.html">ProductionVariantSummary</a> objects, one for each model hosted behind this endpoint.</p>
    data_capture_config:
    failure_reason:<p>If the status of the endpoint is <code>Failed</code>, the reason why it failed. </p>
    last_deployment_config:<p>The most recent deployment configuration for the endpoint.</p>
    async_inference_config:<p>Returns the description of an endpoint configuration created using the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html"> <code>CreateEndpointConfig</code> </a> API.</p>
    pending_deployment_summary:<p>Returns the summary of an in-progress deployment. This field is only returned when the endpoint is creating or updating with a new endpoint configuration.</p>
    explainer_config:<p>The configuration parameters for an explainer.</p>
    shadow_production_variants:<p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ProductionVariantSummary.html">ProductionVariantSummary</a> objects, one for each model that you want to host at this endpoint in shadow mode with production traffic replicated from the model specified on <code>ProductionVariants</code>.</p>
    
    """
    endpoint_name: str
    endpoint_arn: Optional[str] = Unassigned()
    endpoint_config_name: Optional[str] = Unassigned()
    production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    endpoint_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_deployment_config: Optional[DeploymentConfig] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    pending_deployment_summary: Optional[PendingDeploymentSummary] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'endpoint_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "data_capture_config": {
            "destination_s3_uri": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "async_inference_config": {
            "output_config": {
              "kms_key_id": {
                "type": "string"
              },
              "s3_output_path": {
                "type": "string"
              },
              "s3_failure_path": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Endpoint", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        endpoint_name: str,
        endpoint_config_name: Union[str, object],
        deployment_config: Optional[DeploymentConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Endpoint"]:
        logger.debug("Creating endpoint resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'EndpointName': endpoint_name,
            'EndpointConfigName': endpoint_config_name,
            'DeploymentConfig': deployment_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Endpoint', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_endpoint(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(endpoint_name=endpoint_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        endpoint_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Endpoint"]:
        operation_input_args = {
            'EndpointName': endpoint_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_endpoint(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEndpointOutput')
        endpoint = cls(**transformed_response)
        return endpoint
    
    def refresh(self) -> Optional["Endpoint"]:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEndpointOutput', self)
        return self
    
    def update(
        self,
        retain_all_variant_properties: Optional[bool] = Unassigned(),
        exclude_retained_variant_properties: Optional[List[VariantProperty]] = Unassigned(),
        deployment_config: Optional[DeploymentConfig] = Unassigned(),
        retain_deployment_config: Optional[bool] = Unassigned(),
    ) -> Optional["Endpoint"]:
        logger.debug("Creating endpoint resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
            'EndpointConfigName': self.endpoint_config_name,
            'RetainAllVariantProperties': retain_all_variant_properties,
            'ExcludeRetainedVariantProperties': exclude_retained_variant_properties,
            'DeploymentConfig': deployment_config,
            'RetainDeploymentConfig': retain_deployment_config,
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
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        self.client.delete_endpoint(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['OutOfService', 'Creating', 'Updating', 'SystemUpdating', 'RollingBack', 'InService', 'Deleting', 'Failed', 'UpdateRollbackFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Endpoint"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.endpoint_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Endpoint", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Endpoint", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    def invoke(self, 
        body: Any,
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
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client
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
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client
        
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
    
    def invoke_with_response_stream(self, 
        body: Any,
        content_type: Optional[str] = Unassigned(),
        accept: Optional[str] = Unassigned(),
        custom_attributes: Optional[str] = Unassigned(),
        target_variant: Optional[str] = Unassigned(),
        target_container_hostname: Optional[str] = Unassigned(),
        inference_id: Optional[str] = Unassigned(),
        inference_component_name: Optional[str] = Unassigned(),
    ) -> Optional[object]:
        logger.debug(f"Invoking endpoint resource with Response Stream.")
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client
    
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
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Endpoint"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'StatusEquals': status_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_endpoints',
            summaries_key='Endpoints',
            summary_name='EndpointSummary',
            resource_cls=Endpoint,
            list_method_kwargs=operation_input_args
        )


class EndpointConfig(Base):
    """
    EndpointConfig 
     Class representing resource EndpointConfig
    Attributes
    ---------------------
    endpoint_config_name:<p>Name of the SageMaker endpoint configuration.</p>
    endpoint_config_arn:<p>The Amazon Resource Name (ARN) of the endpoint configuration.</p>
    production_variants:<p>An array of <code>ProductionVariant</code> objects, one for each model that you want to host at this endpoint.</p>
    creation_time:<p>A timestamp that shows when the endpoint configuration was created.</p>
    data_capture_config:
    kms_key_id:<p>Amazon Web Services KMS key ID Amazon SageMaker uses to encrypt data when storing it on the ML storage volume attached to the instance.</p>
    async_inference_config:<p>Returns the description of an endpoint configuration created using the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html"> <code>CreateEndpointConfig</code> </a> API.</p>
    explainer_config:<p>The configuration parameters for an explainer.</p>
    shadow_production_variants:<p>An array of <code>ProductionVariant</code> objects, one for each model that you want to host at this endpoint in shadow mode with production traffic replicated from the model specified on <code>ProductionVariants</code>.</p>
    execution_role_arn:<p>The Amazon Resource Name (ARN) of the IAM role that you assigned to the endpoint configuration.</p>
    vpc_config:
    enable_network_isolation:<p>Indicates whether all model containers deployed to the endpoint are isolated. If they are, no inbound or outbound network calls can be made to or from the model containers.</p>
    
    """
    endpoint_config_name: str
    endpoint_config_arn: Optional[str] = Unassigned()
    production_variants: Optional[List[ProductionVariant]] = Unassigned()
    data_capture_config: Optional[DataCaptureConfig] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariant]] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'endpoint_config_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "data_capture_config": {
            "destination_s3_uri": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "kms_key_id": {
            "type": "string"
          },
          "async_inference_config": {
            "output_config": {
              "kms_key_id": {
                "type": "string"
              },
              "s3_output_path": {
                "type": "string"
              },
              "s3_failure_path": {
                "type": "string"
              }
            }
          },
          "execution_role_arn": {
            "type": "string"
          },
          "vpc_config": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "subnets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "EndpointConfig", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        endpoint_config_name: str,
        production_variants: List[ProductionVariant],
        data_capture_config: Optional[DataCaptureConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        async_inference_config: Optional[AsyncInferenceConfig] = Unassigned(),
        explainer_config: Optional[ExplainerConfig] = Unassigned(),
        shadow_production_variants: Optional[List[ProductionVariant]] = Unassigned(),
        execution_role_arn: Optional[str] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EndpointConfig"]:
        logger.debug("Creating endpoint_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'EndpointConfigName': endpoint_config_name,
            'ProductionVariants': production_variants,
            'DataCaptureConfig': data_capture_config,
            'Tags': tags,
            'KmsKeyId': kms_key_id,
            'AsyncInferenceConfig': async_inference_config,
            'ExplainerConfig': explainer_config,
            'ShadowProductionVariants': shadow_production_variants,
            'ExecutionRoleArn': execution_role_arn,
            'VpcConfig': vpc_config,
            'EnableNetworkIsolation': enable_network_isolation,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='EndpointConfig', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_endpoint_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(endpoint_config_name=endpoint_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        endpoint_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EndpointConfig"]:
        operation_input_args = {
            'EndpointConfigName': endpoint_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_endpoint_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeEndpointConfigOutput')
        endpoint_config = cls(**transformed_response)
        return endpoint_config
    
    def refresh(self) -> Optional["EndpointConfig"]:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeEndpointConfigOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        self.client.delete_endpoint_config(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["EndpointConfig"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_endpoint_configs',
            summaries_key='EndpointConfigs',
            summary_name='EndpointConfigSummary',
            resource_cls=EndpointConfig,
            list_method_kwargs=operation_input_args
        )


class Experiment(Base):
    """
    Experiment 
     Class representing resource Experiment
    Attributes
    ---------------------
    experiment_name:<p>The name of the experiment.</p>
    experiment_arn:<p>The Amazon Resource Name (ARN) of the experiment.</p>
    display_name:<p>The name of the experiment as displayed. If <code>DisplayName</code> isn't specified, <code>ExperimentName</code> is displayed.</p>
    source:<p>The Amazon Resource Name (ARN) of the source and, optionally, the type.</p>
    description:<p>The description of the experiment.</p>
    creation_time:<p>When the experiment was created.</p>
    created_by:<p>Who created the experiment.</p>
    last_modified_time:<p>When the experiment was last modified.</p>
    last_modified_by:<p>Who last modified the experiment.</p>
    
    """
    experiment_name: str
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'experiment_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        experiment_name: str,
        display_name: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Experiment"]:
        logger.debug("Creating experiment resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ExperimentName': experiment_name,
            'DisplayName': display_name,
            'Description': description,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Experiment', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(experiment_name=experiment_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        experiment_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Experiment"]:
        operation_input_args = {
            'ExperimentName': experiment_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeExperimentResponse')
        experiment = cls(**transformed_response)
        return experiment
    
    def refresh(self) -> Optional["Experiment"]:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        client = SageMakerClient().client
        response = client.describe_experiment(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeExperimentResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["Experiment"]:
        logger.debug("Creating experiment resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
            'DisplayName': self.display_name,
            'Description': self.description,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Experiment._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        self.client.delete_experiment(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Experiment"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_experiments',
            summaries_key='ExperimentSummaries',
            summary_name='ExperimentSummary',
            resource_cls=Experiment,
            list_method_kwargs=operation_input_args
        )


class FeatureGroup(Base):
    """
    FeatureGroup 
     Class representing resource FeatureGroup
    Attributes
    ---------------------
    feature_group_arn:<p>The Amazon Resource Name (ARN) of the <code>FeatureGroup</code>. </p>
    feature_group_name:<p>he name of the <code>FeatureGroup</code>.</p>
    record_identifier_feature_name:<p>The name of the <code>Feature</code> used for <code>RecordIdentifier</code>, whose value uniquely identifies a record stored in the feature store.</p>
    event_time_feature_name:<p>The name of the feature that stores the <code>EventTime</code> of a Record in a <code>FeatureGroup</code>.</p> <p> An <code>EventTime</code> is a point in time when a new event occurs that corresponds to the creation or update of a <code>Record</code> in a <code>FeatureGroup</code>. All <code>Records</code> in the <code>FeatureGroup</code> have a corresponding <code>EventTime</code>.</p>
    feature_definitions:<p>A list of the <code>Features</code> in the <code>FeatureGroup</code>. Each feature is defined by a <code>FeatureName</code> and <code>FeatureType</code>.</p>
    creation_time:<p>A timestamp indicating when SageMaker created the <code>FeatureGroup</code>.</p>
    next_token:<p>A token to resume pagination of the list of <code>Features</code> (<code>FeatureDefinitions</code>).</p>
    last_modified_time:<p>A timestamp indicating when the feature group was last updated.</p>
    online_store_config:<p>The configuration for the <code>OnlineStore</code>.</p>
    offline_store_config:<p>The configuration of the offline store. It includes the following configurations:</p> <ul> <li> <p>Amazon S3 location of the offline store.</p> </li> <li> <p>Configuration of the Glue data catalog.</p> </li> <li> <p>Table format of the offline store.</p> </li> <li> <p>Option to disable the automatic creation of a Glue table for the offline store.</p> </li> <li> <p>Encryption configuration.</p> </li> </ul>
    throughput_config:
    role_arn:<p>The Amazon Resource Name (ARN) of the IAM execution role used to persist data into the OfflineStore if an OfflineStoreConfig is provided.</p>
    feature_group_status:<p>The status of the feature group.</p>
    offline_store_status:<p>The status of the <code>OfflineStore</code>. Notifies you if replicating data into the <code>OfflineStore</code> has failed. Returns either: <code>Active</code> or <code>Blocked</code> </p>
    last_update_status:<p>A value indicating whether the update made to the feature group was successful.</p>
    failure_reason:<p>The reason that the <code>FeatureGroup</code> failed to be replicated in the <code>OfflineStore</code>. This is failure can occur because:</p> <ul> <li> <p>The <code>FeatureGroup</code> could not be created in the <code>OfflineStore</code>.</p> </li> <li> <p>The <code>FeatureGroup</code> could not be deleted from the <code>OfflineStore</code>.</p> </li> </ul>
    description:<p>A free form description of the feature group.</p>
    online_store_total_size_bytes:<p>The size of the <code>OnlineStore</code> in bytes.</p>
    
    """
    feature_group_name: str
    feature_group_arn: Optional[str] = Unassigned()
    record_identifier_feature_name: Optional[str] = Unassigned()
    event_time_feature_name: Optional[str] = Unassigned()
    feature_definitions: Optional[List[FeatureDefinition]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    online_store_config: Optional[OnlineStoreConfig] = Unassigned()
    offline_store_config: Optional[OfflineStoreConfig] = Unassigned()
    throughput_config: Optional[ThroughputConfigDescription] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    feature_group_status: Optional[str] = Unassigned()
    offline_store_status: Optional[OfflineStoreStatus] = Unassigned()
    last_update_status: Optional[LastUpdateStatus] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    online_store_total_size_bytes: Optional[int] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'feature_group_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "online_store_config": {
            "security_config": {
              "kms_key_id": {
                "type": "string"
              }
            }
          },
          "offline_store_config": {
            "s3_storage_config": {
              "s3_uri": {
                "type": "string"
              },
              "kms_key_id": {
                "type": "string"
              },
              "resolved_output_s3_uri": {
                "type": "string"
              }
            }
          },
          "role_arn": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "FeatureGroup", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        feature_group_name: str,
        record_identifier_feature_name: str,
        event_time_feature_name: str,
        feature_definitions: List[FeatureDefinition],
        online_store_config: Optional[OnlineStoreConfig] = Unassigned(),
        offline_store_config: Optional[OfflineStoreConfig] = Unassigned(),
        throughput_config: Optional[ThroughputConfig] = Unassigned(),
        role_arn: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["FeatureGroup"]:
        logger.debug("Creating feature_group resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'FeatureGroupName': feature_group_name,
            'RecordIdentifierFeatureName': record_identifier_feature_name,
            'EventTimeFeatureName': event_time_feature_name,
            'FeatureDefinitions': feature_definitions,
            'OnlineStoreConfig': online_store_config,
            'OfflineStoreConfig': offline_store_config,
            'ThroughputConfig': throughput_config,
            'RoleArn': role_arn,
            'Description': description,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='FeatureGroup', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_feature_group(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(feature_group_name=feature_group_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        feature_group_name: str,
        next_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["FeatureGroup"]:
        operation_input_args = {
            'FeatureGroupName': feature_group_name,
            'NextToken': next_token,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_feature_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeFeatureGroupResponse')
        feature_group = cls(**transformed_response)
        return feature_group
    
    def refresh(self) -> Optional["FeatureGroup"]:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
            'NextToken': self.next_token,
        }
        client = SageMakerClient().client
        response = client.describe_feature_group(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeFeatureGroupResponse', self)
        return self
    
    def update(
        self,
        feature_additions: Optional[List[FeatureDefinition]] = Unassigned(),
    ) -> Optional["FeatureGroup"]:
        logger.debug("Creating feature_group resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
            'FeatureAdditions': feature_additions,
            'OnlineStoreConfig': self.online_store_config,
            'ThroughputConfig': self.throughput_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = FeatureGroup._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_feature_group(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
        }
        self.client.delete_feature_group(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Creating', 'Created', 'CreateFailed', 'Deleting', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["FeatureGroup"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.feature_group_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="FeatureGroup", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="FeatureGroup", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        feature_group_status_equals: Optional[str] = Unassigned(),
        offline_store_status_equals: Optional[str] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["FeatureGroup"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'NameContains': name_contains,
            'FeatureGroupStatusEquals': feature_group_status_equals,
            'OfflineStoreStatusEquals': offline_store_status_equals,
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'SortOrder': sort_order,
            'SortBy': sort_by,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_feature_groups',
            summaries_key='FeatureGroupSummaries',
            summary_name='FeatureGroupSummary',
            resource_cls=FeatureGroup,
            list_method_kwargs=operation_input_args
        )


class FlowDefinition(Base):
    """
    FlowDefinition 
     Class representing resource FlowDefinition
    Attributes
    ---------------------
    flow_definition_arn:<p>The Amazon Resource Name (ARN) of the flow defintion.</p>
    flow_definition_name:<p>The Amazon Resource Name (ARN) of the flow definition.</p>
    flow_definition_status:<p>The status of the flow definition. Valid values are listed below.</p>
    creation_time:<p>The timestamp when the flow definition was created.</p>
    output_config:<p>An object containing information about the output file.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of the Amazon Web Services Identity and Access Management (IAM) execution role for the flow definition.</p>
    human_loop_request_source:<p>Container for configuring the source of human task requests. Used to specify if Amazon Rekognition or Amazon Textract is used as an integration source.</p>
    human_loop_activation_config:<p>An object containing information about what triggers a human review workflow.</p>
    human_loop_config:<p>An object containing information about who works on the task, the workforce task price, and other task details.</p>
    failure_reason:<p>The reason your flow definition failed.</p>
    
    """
    flow_definition_name: str
    flow_definition_arn: Optional[str] = Unassigned()
    flow_definition_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    human_loop_request_source: Optional[HumanLoopRequestSource] = Unassigned()
    human_loop_activation_config: Optional[HumanLoopActivationConfig] = Unassigned()
    human_loop_config: Optional[HumanLoopConfig] = Unassigned()
    output_config: Optional[FlowDefinitionOutputConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'flow_definition_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "output_config": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "FlowDefinition", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        flow_definition_name: str,
        output_config: FlowDefinitionOutputConfig,
        role_arn: str,
        human_loop_request_source: Optional[HumanLoopRequestSource] = Unassigned(),
        human_loop_activation_config: Optional[HumanLoopActivationConfig] = Unassigned(),
        human_loop_config: Optional[HumanLoopConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["FlowDefinition"]:
        logger.debug("Creating flow_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
            'HumanLoopRequestSource': human_loop_request_source,
            'HumanLoopActivationConfig': human_loop_activation_config,
            'HumanLoopConfig': human_loop_config,
            'OutputConfig': output_config,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='FlowDefinition', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_flow_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(flow_definition_name=flow_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        flow_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["FlowDefinition"]:
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_flow_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeFlowDefinitionResponse')
        flow_definition = cls(**transformed_response)
        return flow_definition
    
    def refresh(self) -> Optional["FlowDefinition"]:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_flow_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeFlowDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        self.client.delete_flow_definition(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Initializing', 'Active', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["FlowDefinition"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.flow_definition_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="FlowDefinition", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="FlowDefinition", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["FlowDefinition"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_flow_definitions',
            summaries_key='FlowDefinitionSummaries',
            summary_name='FlowDefinitionSummary',
            resource_cls=FlowDefinition,
            list_method_kwargs=operation_input_args
        )


class Hub(Base):
    """
    Hub 
     Class representing resource Hub
    Attributes
    ---------------------
    hub_name:<p>The name of the hub.</p>
    hub_arn:<p>The Amazon Resource Name (ARN) of the hub.</p>
    hub_status:<p>The status of the hub.</p>
    creation_time:<p>The date and time that the hub was created.</p>
    last_modified_time:<p>The date and time that the hub was last modified.</p>
    hub_display_name:<p>The display name of the hub.</p>
    hub_description:<p>A description of the hub.</p>
    hub_search_keywords:<p>The searchable keywords for the hub.</p>
    s3_storage_config:<p>The Amazon S3 storage configuration for the hub.</p>
    failure_reason:<p>The failure reason if importing hub content failed.</p>
    
    """
    hub_name: str
    hub_arn: Optional[str] = Unassigned()
    hub_display_name: Optional[str] = Unassigned()
    hub_description: Optional[str] = Unassigned()
    hub_search_keywords: Optional[List[str]] = Unassigned()
    s3_storage_config: Optional[HubS3StorageConfig] = Unassigned()
    hub_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'hub_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "s3_storage_config": {
            "s3_output_path": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Hub", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        hub_name: str,
        hub_description: str,
        hub_display_name: Optional[str] = Unassigned(),
        hub_search_keywords: Optional[List[str]] = Unassigned(),
        s3_storage_config: Optional[HubS3StorageConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Hub"]:
        logger.debug("Creating hub resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'HubName': hub_name,
            'HubDescription': hub_description,
            'HubDisplayName': hub_display_name,
            'HubSearchKeywords': hub_search_keywords,
            'S3StorageConfig': s3_storage_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Hub', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_hub(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(hub_name=hub_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Hub"]:
        operation_input_args = {
            'HubName': hub_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hub(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHubResponse')
        hub = cls(**transformed_response)
        return hub
    
    def refresh(self) -> Optional["Hub"]:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        client = SageMakerClient().client
        response = client.describe_hub(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHubResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["Hub"]:
        logger.debug("Creating hub resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubDescription': self.hub_description,
            'HubDisplayName': self.hub_display_name,
            'HubSearchKeywords': self.hub_search_keywords,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Hub._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_hub(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        self.client.delete_hub(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['InService', 'Creating', 'Updating', 'Deleting', 'CreateFailed', 'UpdateFailed', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Hub"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hub_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Hub", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Hub", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Hub"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_hubs',
            summaries_key='HubSummaries',
            summary_name='HubInfo',
            resource_cls=Hub,
            list_method_kwargs=operation_input_args
        )


class HubContent(Base):
    """
    HubContent 
     Class representing resource HubContent
    Attributes
    ---------------------
    hub_content_name:<p>The name of the hub content.</p>
    hub_content_arn:<p>The Amazon Resource Name (ARN) of the hub content.</p>
    hub_content_version:<p>The version of the hub content.</p>
    hub_content_type:<p>The type of hub content.</p>
    document_schema_version:<p>The document schema version for the hub content.</p>
    hub_name:<p>The name of the hub that contains the content.</p>
    hub_arn:<p>The Amazon Resource Name (ARN) of the hub that contains the content. </p>
    hub_content_document:<p>The hub content document that describes information about the hub content such as type, associated containers, scripts, and more.</p>
    hub_content_status:<p>The status of the hub content.</p>
    creation_time:<p>The date and time that hub content was created.</p>
    hub_content_display_name:<p>The display name of the hub content.</p>
    hub_content_description:<p>A description of the hub content.</p>
    hub_content_markdown:<p>A string that provides a description of the hub content. This string can include links, tables, and standard markdown formating.</p>
    hub_content_search_keywords:<p>The searchable keywords for the hub content.</p>
    hub_content_dependencies:<p>The location of any dependencies that the hub content has, such as scripts, model artifacts, datasets, or notebooks.</p>
    failure_reason:<p>The failure reason if importing hub content failed.</p>
    
    """
    hub_name: str
    hub_content_type: str
    hub_content_name: str
    hub_content_arn: Optional[str] = Unassigned()
    hub_content_version: Optional[str] = Unassigned()
    document_schema_version: Optional[str] = Unassigned()
    hub_arn: Optional[str] = Unassigned()
    hub_content_display_name: Optional[str] = Unassigned()
    hub_content_description: Optional[str] = Unassigned()
    hub_content_markdown: Optional[str] = Unassigned()
    hub_content_document: Optional[str] = Unassigned()
    hub_content_search_keywords: Optional[List[str]] = Unassigned()
    hub_content_dependencies: Optional[List[HubContentDependency]] = Unassigned()
    hub_content_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'hub_content_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        hub_content_type: str,
        hub_content_name: str,
        hub_content_version: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HubContent"]:
        operation_input_args = {
            'HubName': hub_name,
            'HubContentType': hub_content_type,
            'HubContentName': hub_content_name,
            'HubContentVersion': hub_content_version,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hub_content(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHubContentResponse')
        hub_content = cls(**transformed_response)
        return hub_content
    
    def refresh(self) -> Optional["HubContent"]:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        client = SageMakerClient().client
        response = client.describe_hub_content(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHubContentResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        self.client.delete_hub_content(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Available', 'Importing', 'Deleting', 'ImportFailed', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["HubContent"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hub_content_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="HubContent", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="HubContent", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
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
    ) -> Optional["HubContent"]:
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
    
    @classmethod
    def get_all(
        cls,
        hub_name: str,
        hub_content_type: str,
        name_contains: Optional[str] = Unassigned(),
        max_schema_version: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["HubContent"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'HubName': hub_name,
            'HubContentType': hub_content_type,
            'NameContains': name_contains,
            'MaxSchemaVersion': max_schema_version,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_hub_contents',
            summaries_key='HubContentSummaries',
            summary_name='HubContentInfo',
            resource_cls=HubContent,
            list_method_kwargs=operation_input_args
        )


class HumanTaskUi(Base):
    """
    HumanTaskUi 
     Class representing resource HumanTaskUi
    Attributes
    ---------------------
    human_task_ui_arn:<p>The Amazon Resource Name (ARN) of the human task user interface (worker task template).</p>
    human_task_ui_name:<p>The name of the human task user interface (worker task template).</p>
    creation_time:<p>The timestamp when the human task user interface was created.</p>
    ui_template:
    human_task_ui_status:<p>The status of the human task user interface (worker task template). Valid values are listed below.</p>
    
    """
    human_task_ui_name: str
    human_task_ui_arn: Optional[str] = Unassigned()
    human_task_ui_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    ui_template: Optional[UiTemplateInfo] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'human_task_ui_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        human_task_ui_name: str,
        ui_template: UiTemplate,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HumanTaskUi"]:
        logger.debug("Creating human_task_ui resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
            'UiTemplate': ui_template,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='HumanTaskUi', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_human_task_ui(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(human_task_ui_name=human_task_ui_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        human_task_ui_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HumanTaskUi"]:
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_human_task_ui(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHumanTaskUiResponse')
        human_task_ui = cls(**transformed_response)
        return human_task_ui
    
    def refresh(self) -> Optional["HumanTaskUi"]:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        client = SageMakerClient().client
        response = client.describe_human_task_ui(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHumanTaskUiResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        self.client.delete_human_task_ui(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Active', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["HumanTaskUi"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.human_task_ui_status
    
            if status == current_status:
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="HumanTaskUi", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["HumanTaskUi"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_human_task_uis',
            summaries_key='HumanTaskUiSummaries',
            summary_name='HumanTaskUiSummary',
            resource_cls=HumanTaskUi,
            list_method_kwargs=operation_input_args
        )


class HyperParameterTuningJob(Base):
    """
    HyperParameterTuningJob 
     Class representing resource HyperParameterTuningJob
    Attributes
    ---------------------
    hyper_parameter_tuning_job_name:<p>The name of the hyperparameter tuning job.</p>
    hyper_parameter_tuning_job_arn:<p>The Amazon Resource Name (ARN) of the tuning job.</p>
    hyper_parameter_tuning_job_config:<p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobConfig.html">HyperParameterTuningJobConfig</a> object that specifies the configuration of the tuning job.</p>
    hyper_parameter_tuning_job_status:<p>The status of the tuning job.</p>
    creation_time:<p>The date and time that the tuning job started.</p>
    training_job_status_counters:<p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TrainingJobStatusCounters.html">TrainingJobStatusCounters</a> object that specifies the number of training jobs, categorized by status, that this tuning job launched.</p>
    objective_status_counters:<p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ObjectiveStatusCounters.html">ObjectiveStatusCounters</a> object that specifies the number of training jobs, categorized by the status of their final objective metric, that this tuning job launched.</p>
    training_job_definition:<p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTrainingJobDefinition.html">HyperParameterTrainingJobDefinition</a> object that specifies the definition of the training jobs that this tuning job launches.</p>
    training_job_definitions:<p>A list of the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTrainingJobDefinition.html">HyperParameterTrainingJobDefinition</a> objects launched for this tuning job.</p>
    hyper_parameter_tuning_end_time:<p>The date and time that the tuning job ended.</p>
    last_modified_time:<p>The date and time that the status of the tuning job was modified. </p>
    best_training_job:<p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TrainingJobSummary.html">TrainingJobSummary</a> object that describes the training job that completed with the best current <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobObjective.html">HyperParameterTuningJobObjective</a>.</p>
    overall_best_training_job:<p>If the hyperparameter tuning job is an warm start tuning job with a <code>WarmStartType</code> of <code>IDENTICAL_DATA_AND_ALGORITHM</code>, this is the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TrainingJobSummary.html">TrainingJobSummary</a> for the training job with the best objective metric value of all training jobs launched by this tuning job and all parent jobs specified for the warm start tuning job.</p>
    warm_start_config:<p>The configuration for starting the hyperparameter parameter tuning job using one or more previous tuning jobs as a starting point. The results of previous tuning jobs are used to inform which combinations of hyperparameters to search over in the new tuning job.</p>
    autotune:<p>A flag to indicate if autotune is enabled for the hyperparameter tuning job.</p>
    failure_reason:<p>If the tuning job failed, the reason it failed.</p>
    tuning_job_completion_details:<p>Tuning job completion information returned as the response from a hyperparameter tuning job. This information tells if your tuning job has or has not converged. It also includes the number of training jobs that have not improved model performance as evaluated against the objective function.</p>
    consumed_resources:
    
    """
    hyper_parameter_tuning_job_name: str
    hyper_parameter_tuning_job_arn: Optional[str] = Unassigned()
    hyper_parameter_tuning_job_config: Optional[HyperParameterTuningJobConfig] = Unassigned()
    training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned()
    training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = Unassigned()
    hyper_parameter_tuning_job_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    hyper_parameter_tuning_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    training_job_status_counters: Optional[TrainingJobStatusCounters] = Unassigned()
    objective_status_counters: Optional[ObjectiveStatusCounters] = Unassigned()
    best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    overall_best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned()
    autotune: Optional[Autotune] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    tuning_job_completion_details: Optional[HyperParameterTuningJobCompletionDetails] = Unassigned()
    consumed_resources: Optional[HyperParameterTuningJobConsumedResources] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'hyper_parameter_tuning_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "training_job_definition": {
            "role_arn": {
              "type": "string"
            },
            "output_data_config": {
              "s3_output_path": {
                "type": "string"
              },
              "kms_key_id": {
                "type": "string"
              }
            },
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            },
            "resource_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            },
            "hyper_parameter_tuning_resource_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            },
            "checkpoint_config": {
              "s3_uri": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "HyperParameterTuningJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        hyper_parameter_tuning_job_name: str,
        hyper_parameter_tuning_job_config: HyperParameterTuningJobConfig,
        training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned(),
        training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = Unassigned(),
        warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        autotune: Optional[Autotune] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HyperParameterTuningJob"]:
        logger.debug("Creating hyper_parameter_tuning_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
            'HyperParameterTuningJobConfig': hyper_parameter_tuning_job_config,
            'TrainingJobDefinition': training_job_definition,
            'TrainingJobDefinitions': training_job_definitions,
            'WarmStartConfig': warm_start_config,
            'Tags': tags,
            'Autotune': autotune,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='HyperParameterTuningJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_hyper_parameter_tuning_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        hyper_parameter_tuning_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HyperParameterTuningJob"]:
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeHyperParameterTuningJobResponse')
        hyper_parameter_tuning_job = cls(**transformed_response)
        return hyper_parameter_tuning_job
    
    def refresh(self) -> Optional["HyperParameterTuningJob"]:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeHyperParameterTuningJobResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        self.client.delete_hyper_parameter_tuning_job(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        self.client.stop_hyper_parameter_tuning_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["HyperParameterTuningJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped', 'DeleteFailed']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.hyper_parameter_tuning_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="HyperParameterTuningJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="HyperParameterTuningJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["HyperParameterTuningJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'StatusEquals': status_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_hyper_parameter_tuning_jobs',
            summaries_key='HyperParameterTuningJobSummaries',
            summary_name='HyperParameterTuningJobSummary',
            resource_cls=HyperParameterTuningJob,
            list_method_kwargs=operation_input_args
        )


class Image(Base):
    """
    Image 
     Class representing resource Image
    Attributes
    ---------------------
    creation_time:<p>When the image was created.</p>
    description:<p>The description of the image.</p>
    display_name:<p>The name of the image as displayed.</p>
    failure_reason:<p>When a create, update, or delete operation fails, the reason for the failure.</p>
    image_arn:<p>The ARN of the image.</p>
    image_name:<p>The name of the image.</p>
    image_status:<p>The status of the image.</p>
    last_modified_time:<p>When the image was last modified.</p>
    role_arn:<p>The ARN of the IAM role that enables Amazon SageMaker to perform tasks on your behalf.</p>
    
    """
    image_name: str
    creation_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    image_arn: Optional[str] = Unassigned()
    image_status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'image_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "role_arn": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Image", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        image_name: str,
        role_arn: str,
        description: Optional[str] = Unassigned(),
        display_name: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Image"]:
        logger.debug("Creating image resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'Description': description,
            'DisplayName': display_name,
            'ImageName': image_name,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Image', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_image(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(image_name=image_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Image"]:
        operation_input_args = {
            'ImageName': image_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_image(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeImageResponse')
        image = cls(**transformed_response)
        return image
    
    def refresh(self) -> Optional["Image"]:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        client = SageMakerClient().client
        response = client.describe_image(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeImageResponse', self)
        return self
    
    def update(
        self,
        delete_properties: Optional[List[str]] = Unassigned(),
    ) -> Optional["Image"]:
        logger.debug("Creating image resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'DeleteProperties': delete_properties,
            'Description': self.description,
            'DisplayName': self.display_name,
            'ImageName': self.image_name,
            'RoleArn': self.role_arn,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Image._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_image(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        self.client.delete_image(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['CREATING', 'CREATED', 'CREATE_FAILED', 'UPDATING', 'UPDATE_FAILED', 'DELETING', 'DELETE_FAILED'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Image"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.image_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Image", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Image", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Image"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_images',
            summaries_key='Images',
            summary_name='Image',
            resource_cls=Image,
            list_method_kwargs=operation_input_args
        )


class ImageVersion(Base):
    """
    ImageVersion 
     Class representing resource ImageVersion
    Attributes
    ---------------------
    base_image:<p>The registry path of the container image on which this image version is based.</p>
    container_image:<p>The registry path of the container image that contains this image version.</p>
    creation_time:<p>When the version was created.</p>
    failure_reason:<p>When a create or delete operation fails, the reason for the failure.</p>
    image_arn:<p>The ARN of the image the version is based on.</p>
    image_version_arn:<p>The ARN of the version.</p>
    image_version_status:<p>The status of the version.</p>
    last_modified_time:<p>When the version was last modified.</p>
    version:<p>The version number.</p>
    vendor_guidance:<p>The stability of the image version specified by the maintainer.</p> <ul> <li> <p> <code>NOT_PROVIDED</code>: The maintainers did not provide a status for image version stability.</p> </li> <li> <p> <code>STABLE</code>: The image version is stable.</p> </li> <li> <p> <code>TO_BE_ARCHIVED</code>: The image version is set to be archived. Custom image versions that are set to be archived are automatically archived after three months.</p> </li> <li> <p> <code>ARCHIVED</code>: The image version is archived. Archived image versions are not searchable and are no longer actively supported. </p> </li> </ul>
    job_type:<p>Indicates SageMaker job type compatibility.</p> <ul> <li> <p> <code>TRAINING</code>: The image version is compatible with SageMaker training jobs.</p> </li> <li> <p> <code>INFERENCE</code>: The image version is compatible with SageMaker inference jobs.</p> </li> <li> <p> <code>NOTEBOOK_KERNEL</code>: The image version is compatible with SageMaker notebook kernels.</p> </li> </ul>
    m_l_framework:<p>The machine learning framework vended in the image version.</p>
    programming_lang:<p>The supported programming language and its version.</p>
    processor:<p>Indicates CPU or GPU compatibility.</p> <ul> <li> <p> <code>CPU</code>: The image version is compatible with CPU.</p> </li> <li> <p> <code>GPU</code>: The image version is compatible with GPU.</p> </li> </ul>
    horovod:<p>Indicates Horovod compatibility.</p>
    release_notes:<p>The maintainer description of the image version.</p>
    
    """
    base_image: Optional[str] = Unassigned()
    container_image: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    image_arn: Optional[str] = Unassigned()
    image_version_arn: Optional[str] = Unassigned()
    image_version_status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    version: Optional[int] = Unassigned()
    vendor_guidance: Optional[str] = Unassigned()
    job_type: Optional[str] = Unassigned()
    m_l_framework: Optional[str] = Unassigned()
    programming_lang: Optional[str] = Unassigned()
    processor: Optional[str] = Unassigned()
    horovod: Optional[bool] = Unassigned()
    release_notes: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'image_version_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        base_image: str,
        client_token: str,
        image_name: Union[str, object],
        aliases: Optional[List[str]] = Unassigned(),
        vendor_guidance: Optional[str] = Unassigned(),
        job_type: Optional[str] = Unassigned(),
        m_l_framework: Optional[str] = Unassigned(),
        programming_lang: Optional[str] = Unassigned(),
        processor: Optional[str] = Unassigned(),
        horovod: Optional[bool] = Unassigned(),
        release_notes: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ImageVersion"]:
        logger.debug("Creating image_version resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'BaseImage': base_image,
            'ClientToken': client_token,
            'ImageName': image_name,
            'Aliases': aliases,
            'VendorGuidance': vendor_guidance,
            'JobType': job_type,
            'MLFramework': m_l_framework,
            'ProgrammingLang': programming_lang,
            'Processor': processor,
            'Horovod': horovod,
            'ReleaseNotes': release_notes,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ImageVersion', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_image_version(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(image_name=image_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        version: Optional[int] = Unassigned(),
        alias: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ImageVersion"]:
        operation_input_args = {
            'ImageName': image_name,
            'Version': version,
            'Alias': alias,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_image_version(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeImageVersionResponse')
        image_version = cls(**transformed_response)
        return image_version
    
    def refresh(self) -> Optional["ImageVersion"]:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        client = SageMakerClient().client
        response = client.describe_image_version(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeImageVersionResponse', self)
        return self
    
    def update(
        self,
        image_name: str,
        alias: Optional[str] = Unassigned(),
        aliases_to_add: Optional[List[str]] = Unassigned(),
        aliases_to_delete: Optional[List[str]] = Unassigned(),
    ) -> Optional["ImageVersion"]:
        logger.debug("Creating image_version resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ImageName': image_name,
            'Alias': alias,
            'Version': self.version,
            'AliasesToAdd': aliases_to_add,
            'AliasesToDelete': aliases_to_delete,
            'VendorGuidance': self.vendor_guidance,
            'JobType': self.job_type,
            'MLFramework': self.m_l_framework,
            'ProgrammingLang': self.programming_lang,
            'Processor': self.processor,
            'Horovod': self.horovod,
            'ReleaseNotes': self.release_notes,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = ImageVersion._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_image_version(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        self.client.delete_image_version(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['CREATING', 'CREATED', 'CREATE_FAILED', 'DELETING', 'DELETE_FAILED'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ImageVersion"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.image_version_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="ImageVersion", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ImageVersion", status=current_status)
            print("-", end="")
            time.sleep(poll)


class InferenceComponent(Base):
    """
    InferenceComponent 
     Class representing resource InferenceComponent
    Attributes
    ---------------------
    inference_component_name:<p>The name of the inference component.</p>
    inference_component_arn:<p>The Amazon Resource Name (ARN) of the inference component.</p>
    endpoint_name:<p>The name of the endpoint that hosts the inference component.</p>
    endpoint_arn:<p>The Amazon Resource Name (ARN) of the endpoint that hosts the inference component.</p>
    creation_time:<p>The time when the inference component was created.</p>
    last_modified_time:<p>The time when the inference component was last updated.</p>
    variant_name:<p>The name of the production variant that hosts the inference component.</p>
    failure_reason:<p>If the inference component status is <code>Failed</code>, the reason for the failure.</p>
    specification:<p>Details about the resources that are deployed with this inference component.</p>
    runtime_config:<p>Details about the runtime settings for the model that is deployed with the inference component.</p>
    inference_component_status:<p>The status of the inference component.</p>
    
    """
    inference_component_name: str
    inference_component_arn: Optional[str] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    endpoint_arn: Optional[str] = Unassigned()
    variant_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    specification: Optional[InferenceComponentSpecificationSummary] = Unassigned()
    runtime_config: Optional[InferenceComponentRuntimeConfigSummary] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    inference_component_status: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'inference_component_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        inference_component_name: str,
        endpoint_name: Union[str, object],
        variant_name: str,
        specification: InferenceComponentSpecification,
        runtime_config: InferenceComponentRuntimeConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceComponent"]:
        logger.debug("Creating inference_component resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
            'EndpointName': endpoint_name,
            'VariantName': variant_name,
            'Specification': specification,
            'RuntimeConfig': runtime_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='InferenceComponent', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_component(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(inference_component_name=inference_component_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        inference_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceComponent"]:
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceComponentOutput')
        inference_component = cls(**transformed_response)
        return inference_component
    
    def refresh(self) -> Optional["InferenceComponent"]:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_component(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceComponentOutput', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["InferenceComponent"]:
        logger.debug("Creating inference_component resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
            'Specification': self.specification,
            'RuntimeConfig': self.runtime_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = InferenceComponent._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_inference_component(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        self.client.delete_inference_component(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['InService', 'Creating', 'Updating', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["InferenceComponent"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.inference_component_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="InferenceComponent", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="InferenceComponent", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        endpoint_name_equals: Optional[str] = Unassigned(),
        variant_name_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["InferenceComponent"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'StatusEquals': status_equals,
            'EndpointNameEquals': endpoint_name_equals,
            'VariantNameEquals': variant_name_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_inference_components',
            summaries_key='InferenceComponents',
            summary_name='InferenceComponentSummary',
            resource_cls=InferenceComponent,
            list_method_kwargs=operation_input_args
        )


class InferenceExperiment(Base):
    """
    InferenceExperiment 
     Class representing resource InferenceExperiment
    Attributes
    ---------------------
    arn:<p>The ARN of the inference experiment being described.</p>
    name:<p>The name of the inference experiment.</p>
    type:<p>The type of the inference experiment.</p>
    status:<p> The status of the inference experiment. The following are the possible statuses for an inference experiment: </p> <ul> <li> <p> <code>Creating</code> - Amazon SageMaker is creating your experiment. </p> </li> <li> <p> <code>Created</code> - Amazon SageMaker has finished the creation of your experiment and will begin the experiment at the scheduled time. </p> </li> <li> <p> <code>Updating</code> - When you make changes to your experiment, your experiment shows as updating. </p> </li> <li> <p> <code>Starting</code> - Amazon SageMaker is beginning your experiment. </p> </li> <li> <p> <code>Running</code> - Your experiment is in progress. </p> </li> <li> <p> <code>Stopping</code> - Amazon SageMaker is stopping your experiment. </p> </li> <li> <p> <code>Completed</code> - Your experiment has completed. </p> </li> <li> <p> <code>Cancelled</code> - When you conclude your experiment early using the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_StopInferenceExperiment.html">StopInferenceExperiment</a> API, or if any operation fails with an unexpected error, it shows as cancelled. </p> </li> </ul>
    endpoint_metadata:<p>The metadata of the endpoint on which the inference experiment ran.</p>
    model_variants:<p> An array of <code>ModelVariantConfigSummary</code> objects. There is one for each variant in the inference experiment. Each <code>ModelVariantConfigSummary</code> object in the array describes the infrastructure configuration for deploying the corresponding variant. </p>
    schedule:<p>The duration for which the inference experiment ran or will run.</p>
    status_reason:<p> The error message or client-specified <code>Reason</code> from the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_StopInferenceExperiment.html">StopInferenceExperiment</a> API, that explains the status of the inference experiment. </p>
    description:<p>The description of the inference experiment.</p>
    creation_time:<p>The timestamp at which you created the inference experiment.</p>
    completion_time:<p> The timestamp at which the inference experiment was completed. </p>
    last_modified_time:<p>The timestamp at which you last modified the inference experiment.</p>
    role_arn:<p> The ARN of the IAM role that Amazon SageMaker can assume to access model artifacts and container images, and manage Amazon SageMaker Inference endpoints for model deployment. </p>
    data_storage_config:<p>The Amazon S3 location and configuration for storing inference request and response data.</p>
    shadow_mode_config:<p> The configuration of <code>ShadowMode</code> inference experiment type, which shows the production variant that takes all the inference requests, and the shadow variant to which Amazon SageMaker replicates a percentage of the inference requests. For the shadow variant it also shows the percentage of requests that Amazon SageMaker replicates. </p>
    kms_key:<p> The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the endpoint. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateInferenceExperiment.html">CreateInferenceExperiment</a>. </p>
    
    """
    name: str
    arn: Optional[str] = Unassigned()
    type: Optional[str] = Unassigned()
    schedule: Optional[InferenceExperimentSchedule] = Unassigned()
    status: Optional[str] = Unassigned()
    status_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    endpoint_metadata: Optional[EndpointMetadata] = Unassigned()
    model_variants: Optional[List[ModelVariantConfigSummary]] = Unassigned()
    data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned()
    shadow_mode_config: Optional[ShadowModeConfig] = Unassigned()
    kms_key: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'inference_experiment_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "role_arn": {
            "type": "string"
          },
          "data_storage_config": {
            "kms_key": {
              "type": "string"
            }
          },
          "kms_key": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "InferenceExperiment", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        name: str,
        type: str,
        role_arn: str,
        endpoint_name: Union[str, object],
        model_variants: List[ModelVariantConfig],
        shadow_mode_config: ShadowModeConfig,
        schedule: Optional[InferenceExperimentSchedule] = Unassigned(),
        description: Optional[str] = Unassigned(),
        data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned(),
        kms_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceExperiment"]:
        logger.debug("Creating inference_experiment resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'Name': name,
            'Type': type,
            'Schedule': schedule,
            'Description': description,
            'RoleArn': role_arn,
            'EndpointName': endpoint_name,
            'ModelVariants': model_variants,
            'DataStorageConfig': data_storage_config,
            'ShadowModeConfig': shadow_mode_config,
            'KmsKey': kms_key,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='InferenceExperiment', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(name=name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceExperiment"]:
        operation_input_args = {
            'Name': name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceExperimentResponse')
        inference_experiment = cls(**transformed_response)
        return inference_experiment
    
    def refresh(self) -> Optional["InferenceExperiment"]:
    
        operation_input_args = {
            'Name': self.name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_experiment(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceExperimentResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["InferenceExperiment"]:
        logger.debug("Creating inference_experiment resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'Name': self.name,
            'Schedule': self.schedule,
            'Description': self.description,
            'ModelVariants': self.model_variants,
            'DataStorageConfig': self.data_storage_config,
            'ShadowModeConfig': self.shadow_mode_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = InferenceExperiment._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_inference_experiment(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'Name': self.name,
        }
        self.client.delete_inference_experiment(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'Name': self.name,
            'ModelVariantActions': self.model_variant_actions,
            'DesiredModelVariants': self.desired_model_variants,
            'DesiredState': self.desired_state,
            'Reason': self.reason,
        }
        self.client.stop_inference_experiment(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Creating', 'Created', 'Updating', 'Running', 'Starting', 'Stopping', 'Completed', 'Cancelled'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["InferenceExperiment"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="InferenceExperiment", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        type: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["InferenceExperiment"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'NameContains': name_contains,
            'Type': type,
            'StatusEquals': status_equals,
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_inference_experiments',
            summaries_key='InferenceExperiments',
            summary_name='InferenceExperimentSummary',
            resource_cls=InferenceExperiment,
            list_method_kwargs=operation_input_args
        )


class InferenceRecommendationsJob(Base):
    """
    InferenceRecommendationsJob 
     Class representing resource InferenceRecommendationsJob
    Attributes
    ---------------------
    job_name:<p>The name of the job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.</p>
    job_type:<p>The job type that you provided when you initiated the job.</p>
    job_arn:<p>The Amazon Resource Name (ARN) of the job.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of the Amazon Web Services Identity and Access Management (IAM) role you provided when you initiated the job.</p>
    status:<p>The status of the job.</p>
    creation_time:<p>A timestamp that shows when the job was created.</p>
    last_modified_time:<p>A timestamp that shows when the job was last modified.</p>
    input_config:<p>Returns information about the versioned model package Amazon Resource Name (ARN), the traffic pattern, and endpoint configurations you provided when you initiated the job.</p>
    job_description:<p>The job description that you provided when you initiated the job.</p>
    completion_time:<p>A timestamp that shows when the job completed.</p>
    failure_reason:<p>If the job fails, provides information why the job failed.</p>
    stopping_conditions:<p>The stopping conditions that you provided when you initiated the job.</p>
    inference_recommendations:<p>The recommendations made by Inference Recommender.</p>
    endpoint_performances:<p>The performance results from running an Inference Recommender job on an existing endpoint.</p>
    
    """
    job_name: str
    job_description: Optional[str] = Unassigned()
    job_type: Optional[str] = Unassigned()
    job_arn: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    input_config: Optional[RecommendationJobInputConfig] = Unassigned()
    stopping_conditions: Optional[RecommendationJobStoppingConditions] = Unassigned()
    inference_recommendations: Optional[List[InferenceRecommendation]] = Unassigned()
    endpoint_performances: Optional[List[EndpointPerformance]] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'inference_recommendations_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "role_arn": {
            "type": "string"
          },
          "input_config": {
            "volume_kms_key_id": {
              "type": "string"
            },
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "InferenceRecommendationsJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        job_name: str,
        job_type: str,
        role_arn: str,
        input_config: RecommendationJobInputConfig,
        job_description: Optional[str] = Unassigned(),
        stopping_conditions: Optional[RecommendationJobStoppingConditions] = Unassigned(),
        output_config: Optional[RecommendationJobOutputConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceRecommendationsJob"]:
        logger.debug("Creating inference_recommendations_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'JobName': job_name,
            'JobType': job_type,
            'RoleArn': role_arn,
            'InputConfig': input_config,
            'JobDescription': job_description,
            'StoppingConditions': stopping_conditions,
            'OutputConfig': output_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='InferenceRecommendationsJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_inference_recommendations_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_name=job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceRecommendationsJob"]:
        operation_input_args = {
            'JobName': job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_inference_recommendations_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeInferenceRecommendationsJobResponse')
        inference_recommendations_job = cls(**transformed_response)
        return inference_recommendations_job
    
    def refresh(self) -> Optional["InferenceRecommendationsJob"]:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_recommendations_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeInferenceRecommendationsJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        self.client.stop_inference_recommendations_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["InferenceRecommendationsJob"]:
        terminal_states = ['COMPLETED', 'FAILED', 'STOPPED', 'DELETED']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="InferenceRecommendationsJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="InferenceRecommendationsJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        model_name_equals: Optional[str] = Unassigned(),
        model_package_version_arn_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["InferenceRecommendationsJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'ModelNameEquals': model_name_equals,
            'ModelPackageVersionArnEquals': model_package_version_arn_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_inference_recommendations_jobs',
            summaries_key='InferenceRecommendationsJobs',
            summary_name='InferenceRecommendationsJob',
            resource_cls=InferenceRecommendationsJob,
            list_method_kwargs=operation_input_args
        )


class LabelingJob(Base):
    """
    LabelingJob 
     Class representing resource LabelingJob
    Attributes
    ---------------------
    labeling_job_status:<p>The processing status of the labeling job. </p>
    label_counters:<p>Provides a breakdown of the number of data objects labeled by humans, the number of objects labeled by machine, the number of objects than couldn't be labeled, and the total number of objects labeled. </p>
    creation_time:<p>The date and time that the labeling job was created.</p>
    last_modified_time:<p>The date and time that the labeling job was last updated.</p>
    job_reference_code:<p>A unique identifier for work done as part of a labeling job.</p>
    labeling_job_name:<p>The name assigned to the labeling job when it was created.</p>
    labeling_job_arn:<p>The Amazon Resource Name (ARN) of the labeling job.</p>
    input_config:<p>Input configuration information for the labeling job, such as the Amazon S3 location of the data objects and the location of the manifest file that describes the data objects.</p>
    output_config:<p>The location of the job's output data and the Amazon Web Services Key Management Service key ID for the key used to encrypt the output data, if any.</p>
    role_arn:<p>The Amazon Resource Name (ARN) that SageMaker assumes to perform tasks on your behalf during data labeling.</p>
    human_task_config:<p>Configuration information required for human workers to complete a labeling task.</p>
    failure_reason:<p>If the job failed, the reason that it failed. </p>
    label_attribute_name:<p>The attribute used as the label in the output manifest file.</p>
    label_category_config_s3_uri:<p>The S3 location of the JSON file that defines the categories used to label data objects. Please note the following label-category limits:</p> <ul> <li> <p>Semantic segmentation labeling jobs using automated labeling: 20 labels</p> </li> <li> <p>Box bounding labeling jobs (all): 10 labels</p> </li> </ul> <p>The file is a JSON structure in the following format:</p> <p> <code>{</code> </p> <p> <code> "document-version": "2018-11-28"</code> </p> <p> <code> "labels": [</code> </p> <p> <code> {</code> </p> <p> <code> "label": "<i>label 1</i>"</code> </p> <p> <code> },</code> </p> <p> <code> {</code> </p> <p> <code> "label": "<i>label 2</i>"</code> </p> <p> <code> },</code> </p> <p> <code> ...</code> </p> <p> <code> {</code> </p> <p> <code> "label": "<i>label n</i>"</code> </p> <p> <code> }</code> </p> <p> <code> ]</code> </p> <p> <code>}</code> </p>
    stopping_conditions:<p>A set of conditions for stopping a labeling job. If any of the conditions are met, the job is automatically stopped.</p>
    labeling_job_algorithms_config:<p>Configuration information for automated data labeling.</p>
    tags:<p>An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services Resources</a>.</p>
    labeling_job_output:<p>The location of the output produced by the labeling job.</p>
    
    """
    labeling_job_name: str
    labeling_job_status: Optional[str] = Unassigned()
    label_counters: Optional[LabelCounters] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    job_reference_code: Optional[str] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    label_attribute_name: Optional[str] = Unassigned()
    input_config: Optional[LabelingJobInputConfig] = Unassigned()
    output_config: Optional[LabelingJobOutputConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    label_category_config_s3_uri: Optional[str] = Unassigned()
    stopping_conditions: Optional[LabelingJobStoppingConditions] = Unassigned()
    labeling_job_algorithms_config: Optional[LabelingJobAlgorithmsConfig] = Unassigned()
    human_task_config: Optional[HumanTaskConfig] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    labeling_job_output: Optional[LabelingJobOutput] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'labeling_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "input_config": {
            "data_source": {
              "s3_data_source": {
                "manifest_s3_uri": {
                  "type": "string"
                }
              }
            }
          },
          "output_config": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "human_task_config": {
            "ui_config": {
              "ui_template_s3_uri": {
                "type": "string"
              }
            }
          },
          "label_category_config_s3_uri": {
            "type": "string"
          },
          "labeling_job_algorithms_config": {
            "labeling_job_resource_config": {
              "volume_kms_key_id": {
                "type": "string"
              },
              "vpc_config": {
                "security_group_ids": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                },
                "subnets": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  }
                }
              }
            }
          },
          "labeling_job_output": {
            "output_dataset_s3_uri": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "LabelingJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        labeling_job_name: str,
        label_attribute_name: str,
        input_config: LabelingJobInputConfig,
        output_config: LabelingJobOutputConfig,
        role_arn: str,
        human_task_config: HumanTaskConfig,
        label_category_config_s3_uri: Optional[str] = Unassigned(),
        stopping_conditions: Optional[LabelingJobStoppingConditions] = Unassigned(),
        labeling_job_algorithms_config: Optional[LabelingJobAlgorithmsConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["LabelingJob"]:
        logger.debug("Creating labeling_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'LabelingJobName': labeling_job_name,
            'LabelAttributeName': label_attribute_name,
            'InputConfig': input_config,
            'OutputConfig': output_config,
            'RoleArn': role_arn,
            'LabelCategoryConfigS3Uri': label_category_config_s3_uri,
            'StoppingConditions': stopping_conditions,
            'LabelingJobAlgorithmsConfig': labeling_job_algorithms_config,
            'HumanTaskConfig': human_task_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='LabelingJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_labeling_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(labeling_job_name=labeling_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        labeling_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["LabelingJob"]:
        operation_input_args = {
            'LabelingJobName': labeling_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_labeling_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeLabelingJobResponse')
        labeling_job = cls(**transformed_response)
        return labeling_job
    
    def refresh(self) -> Optional["LabelingJob"]:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_labeling_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeLabelingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        self.client.stop_labeling_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["LabelingJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.labeling_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="LabelingJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="LabelingJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["LabelingJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'StatusEquals': status_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_labeling_jobs',
            summaries_key='LabelingJobSummaryList',
            summary_name='LabelingJobSummary',
            resource_cls=LabelingJob,
            list_method_kwargs=operation_input_args
        )


class Model(Base):
    """
    Model 
     Class representing resource Model
    Attributes
    ---------------------
    model_name:<p>Name of the SageMaker model.</p>
    creation_time:<p>A timestamp that shows when the model was created.</p>
    model_arn:<p>The Amazon Resource Name (ARN) of the model.</p>
    primary_container:<p>The location of the primary inference code, associated artifacts, and custom environment map that the inference code uses when it is deployed in production. </p>
    containers:<p>The containers in the inference pipeline.</p>
    inference_execution_config:<p>Specifies details of how containers in a multi-container endpoint are called.</p>
    execution_role_arn:<p>The Amazon Resource Name (ARN) of the IAM role that you specified for the model.</p>
    vpc_config:<p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> object that specifies the VPC that this model has access to. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/host-vpc.html">Protect Endpoints by Using an Amazon Virtual Private Cloud</a> </p>
    enable_network_isolation:<p>If <code>True</code>, no inbound or outbound network calls can be made to or from the model container.</p>
    deployment_recommendation:<p>A set of recommended deployment configurations for the model.</p>
    
    """
    model_name: str
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[List[ContainerDefinition]] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_arn: Optional[str] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "primary_container": {
            "model_data_source": {
              "s3_data_source": {
                "s3_uri": {
                  "type": "string"
                },
                "s3_data_type": {
                  "type": "string"
                }
              }
            }
          },
          "execution_role_arn": {
            "type": "string"
          },
          "vpc_config": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "subnets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Model", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        model_name: str,
        primary_container: Optional[ContainerDefinition] = Unassigned(),
        containers: Optional[List[ContainerDefinition]] = Unassigned(),
        inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned(),
        execution_role_arn: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Model"]:
        logger.debug("Creating model resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ModelName': model_name,
            'PrimaryContainer': primary_container,
            'Containers': containers,
            'InferenceExecutionConfig': inference_execution_config,
            'ExecutionRoleArn': execution_role_arn,
            'Tags': tags,
            'VpcConfig': vpc_config,
            'EnableNetworkIsolation': enable_network_isolation,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Model', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_name=model_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Model"]:
        operation_input_args = {
            'ModelName': model_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelOutput')
        model = cls(**transformed_response)
        return model
    
    def refresh(self) -> Optional["Model"]:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        client = SageMakerClient().client
        response = client.describe_model(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        self.client.delete_model(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Model"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_models',
            summaries_key='Models',
            summary_name='ModelSummary',
            resource_cls=Model,
            list_method_kwargs=operation_input_args
        )


class ModelBiasJobDefinition(Base):
    """
    ModelBiasJobDefinition 
     Class representing resource ModelBiasJobDefinition
    Attributes
    ---------------------
    job_definition_arn:<p>The Amazon Resource Name (ARN) of the model bias job.</p>
    job_definition_name:<p>The name of the bias job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.</p>
    creation_time:<p>The time at which the model bias job was created.</p>
    model_bias_app_specification:<p>Configures the model bias job to run a specified Docker container image.</p>
    model_bias_job_input:<p>Inputs for the model bias job.</p>
    model_bias_job_output_config:
    job_resources:
    role_arn:<p>The Amazon Resource Name (ARN) of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.</p>
    model_bias_baseline_config:<p>The baseline configuration for a model bias job.</p>
    network_config:<p>Networking options for a model bias job.</p>
    stopping_condition:
    
    """
    job_definition_name: str
    job_definition_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_bias_baseline_config: Optional[ModelBiasBaselineConfig] = Unassigned()
    model_bias_app_specification: Optional[ModelBiasAppSpecification] = Unassigned()
    model_bias_job_input: Optional[ModelBiasJobInput] = Unassigned()
    model_bias_job_output_config: Optional[MonitoringOutputConfig] = Unassigned()
    job_resources: Optional[MonitoringResources] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_bias_job_definition_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "model_bias_job_input": {
            "ground_truth_s3_input": {
              "s3_uri": {
                "type": "string"
              }
            },
            "endpoint_input": {
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            },
            "batch_transform_input": {
              "data_captured_destination_s3_uri": {
                "type": "string"
              },
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            }
          },
          "model_bias_job_output_config": {
            "kms_key_id": {
              "type": "string"
            }
          },
          "job_resources": {
            "cluster_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            }
          },
          "role_arn": {
            "type": "string"
          },
          "model_bias_baseline_config": {
            "constraints_resource": {
              "s3_uri": {
                "type": "string"
              }
            }
          },
          "network_config": {
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelBiasJobDefinition", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        job_definition_name: str,
        model_bias_app_specification: ModelBiasAppSpecification,
        model_bias_job_input: ModelBiasJobInput,
        model_bias_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_bias_baseline_config: Optional[ModelBiasBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelBiasJobDefinition"]:
        logger.debug("Creating model_bias_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelBiasBaselineConfig': model_bias_baseline_config,
            'ModelBiasAppSpecification': model_bias_app_specification,
            'ModelBiasJobInput': model_bias_job_input,
            'ModelBiasJobOutputConfig': model_bias_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelBiasJobDefinition', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_bias_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelBiasJobDefinition"]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_bias_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelBiasJobDefinitionResponse')
        model_bias_job_definition = cls(**transformed_response)
        return model_bias_job_definition
    
    def refresh(self) -> Optional["ModelBiasJobDefinition"]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_bias_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelBiasJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_bias_job_definition(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        endpoint_name: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelBiasJobDefinition"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'EndpointName': endpoint_name,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
        custom_key_mapping = {"monitoring_job_definition_name": "job_definition_name", "monitoring_job_definition_arn": "job_definition_arn"}
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_bias_job_definitions',
            summaries_key='JobDefinitionSummaries',
            summary_name='MonitoringJobDefinitionSummary',
            resource_cls=ModelBiasJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args
        )


class ModelCard(Base):
    """
    ModelCard 
     Class representing resource ModelCard
    Attributes
    ---------------------
    model_card_arn:<p>The Amazon Resource Name (ARN) of the model card.</p>
    model_card_name:<p>The name of the model card.</p>
    model_card_version:<p>The version of the model card.</p>
    content:<p>The content of the model card.</p>
    model_card_status:<p>The approval status of the model card within your organization. Different organizations might have different criteria for model card review and approval.</p> <ul> <li> <p> <code>Draft</code>: The model card is a work in progress.</p> </li> <li> <p> <code>PendingReview</code>: The model card is pending review.</p> </li> <li> <p> <code>Approved</code>: The model card is approved.</p> </li> <li> <p> <code>Archived</code>: The model card is archived. No more updates should be made to the model card, but it can still be exported.</p> </li> </ul>
    creation_time:<p>The date and time the model card was created.</p>
    created_by:
    security_config:<p>The security configuration used to protect model card content.</p>
    last_modified_time:<p>The date and time the model card was last modified.</p>
    last_modified_by:
    model_card_processing_status:<p>The processing status of model card deletion. The <code>ModelCardProcessingStatus</code> updates throughout the different deletion steps.</p> <ul> <li> <p> <code>DeletePending</code>: Model card deletion request received.</p> </li> <li> <p> <code>DeleteInProgress</code>: Model card deletion is in progress.</p> </li> <li> <p> <code>ContentDeleted</code>: Deleted model card content.</p> </li> <li> <p> <code>ExportJobsDeleted</code>: Deleted all export jobs associated with the model card.</p> </li> <li> <p> <code>DeleteCompleted</code>: Successfully deleted the model card.</p> </li> <li> <p> <code>DeleteFailed</code>: The model card failed to delete.</p> </li> </ul>
    
    """
    model_card_name: str
    model_card_arn: Optional[str] = Unassigned()
    model_card_version: Optional[int] = Unassigned()
    content: Optional[str] = Unassigned()
    model_card_status: Optional[str] = Unassigned()
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    model_card_processing_status: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_card_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "security_config": {
            "kms_key_id": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelCard", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        model_card_name: str,
        content: str,
        model_card_status: str,
        security_config: Optional[ModelCardSecurityConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelCard"]:
        logger.debug("Creating model_card resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'SecurityConfig': security_config,
            'Content': content,
            'ModelCardStatus': model_card_status,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelCard', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_card(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_card_name=model_card_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_card_name: str,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelCard"]:
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_card(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelCardResponse')
        model_card = cls(**transformed_response)
        return model_card
    
    def refresh(self) -> Optional["ModelCard"]:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
            'ModelCardVersion': self.model_card_version,
        }
        client = SageMakerClient().client
        response = client.describe_model_card(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelCardResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["ModelCard"]:
        logger.debug("Creating model_card resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
            'Content': self.content,
            'ModelCardStatus': self.model_card_status,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = ModelCard._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_model_card(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
        }
        self.client.delete_model_card(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Draft', 'PendingReview', 'Approved', 'Archived'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ModelCard"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_card_status
    
            if status == current_status:
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ModelCard", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        model_card_status: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelCard"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'ModelCardStatus': model_card_status,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_cards',
            summaries_key='ModelCardSummaries',
            summary_name='ModelCardSummary',
            resource_cls=ModelCard,
            list_method_kwargs=operation_input_args
        )


class ModelCardExportJob(Base):
    """
    ModelCardExportJob 
     Class representing resource ModelCardExportJob
    Attributes
    ---------------------
    model_card_export_job_name:<p>The name of the model card export job to describe.</p>
    model_card_export_job_arn:<p>The Amazon Resource Name (ARN) of the model card export job.</p>
    status:<p>The completion status of the model card export job.</p> <ul> <li> <p> <code>InProgress</code>: The model card export job is in progress.</p> </li> <li> <p> <code>Completed</code>: The model card export job is complete.</p> </li> <li> <p> <code>Failed</code>: The model card export job failed. To see the reason for the failure, see the <code>FailureReason</code> field in the response to a <code>DescribeModelCardExportJob</code> call.</p> </li> </ul>
    model_card_name:<p>The name or Amazon Resource Name (ARN) of the model card that the model export job exports.</p>
    model_card_version:<p>The version of the model card that the model export job exports.</p>
    output_config:<p>The export output details for the model card.</p>
    created_at:<p>The date and time that the model export job was created.</p>
    last_modified_at:<p>The date and time that the model export job was last modified.</p>
    failure_reason:<p>The failure reason if the model export job fails.</p>
    export_artifacts:<p>The exported model card artifacts.</p>
    
    """
    model_card_export_job_arn: str
    model_card_export_job_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    model_card_name: Optional[str] = Unassigned()
    model_card_version: Optional[int] = Unassigned()
    output_config: Optional[ModelCardExportOutputConfig] = Unassigned()
    created_at: Optional[datetime.datetime] = Unassigned()
    last_modified_at: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    export_artifacts: Optional[ModelCardExportArtifacts] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_card_export_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "output_config": {
            "s3_output_path": {
              "type": "string"
            }
          },
          "export_artifacts": {
            "s3_export_artifacts": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelCardExportJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        model_card_name: Union[str, object],
        model_card_export_job_name: str,
        output_config: ModelCardExportOutputConfig,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelCardExportJob"]:
        logger.debug("Creating model_card_export_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
            'ModelCardExportJobName': model_card_export_job_name,
            'OutputConfig': output_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelCardExportJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_card_export_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_card_export_job_arn=response['ModelCardExportJobArn'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_card_export_job_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelCardExportJob"]:
        operation_input_args = {
            'ModelCardExportJobArn': model_card_export_job_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_card_export_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelCardExportJobResponse')
        model_card_export_job = cls(**transformed_response)
        return model_card_export_job
    
    def refresh(self) -> Optional["ModelCardExportJob"]:
    
        operation_input_args = {
            'ModelCardExportJobArn': self.model_card_export_job_arn,
        }
        client = SageMakerClient().client
        response = client.describe_model_card_export_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelCardExportJobResponse', self)
        return self
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ModelCardExportJob"]:
        terminal_states = ['Completed', 'Failed']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="ModelCardExportJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ModelCardExportJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        model_card_name: str,
        model_card_version: Optional[int] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        model_card_export_job_name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelCardExportJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'ModelCardExportJobNameContains': model_card_export_job_name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_card_export_jobs',
            summaries_key='ModelCardExportJobSummaries',
            summary_name='ModelCardExportJobSummary',
            resource_cls=ModelCardExportJob,
            list_method_kwargs=operation_input_args
        )


class ModelExplainabilityJobDefinition(Base):
    """
    ModelExplainabilityJobDefinition 
     Class representing resource ModelExplainabilityJobDefinition
    Attributes
    ---------------------
    job_definition_arn:<p>The Amazon Resource Name (ARN) of the model explainability job.</p>
    job_definition_name:<p>The name of the explainability job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.</p>
    creation_time:<p>The time at which the model explainability job was created.</p>
    model_explainability_app_specification:<p>Configures the model explainability job to run a specified Docker container image.</p>
    model_explainability_job_input:<p>Inputs for the model explainability job.</p>
    model_explainability_job_output_config:
    job_resources:
    role_arn:<p>The Amazon Resource Name (ARN) of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.</p>
    model_explainability_baseline_config:<p>The baseline configuration for a model explainability job.</p>
    network_config:<p>Networking options for a model explainability job.</p>
    stopping_condition:
    
    """
    job_definition_name: str
    job_definition_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned()
    model_explainability_app_specification: Optional[ModelExplainabilityAppSpecification] = Unassigned()
    model_explainability_job_input: Optional[ModelExplainabilityJobInput] = Unassigned()
    model_explainability_job_output_config: Optional[MonitoringOutputConfig] = Unassigned()
    job_resources: Optional[MonitoringResources] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_explainability_job_definition_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "model_explainability_job_input": {
            "endpoint_input": {
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            },
            "batch_transform_input": {
              "data_captured_destination_s3_uri": {
                "type": "string"
              },
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            }
          },
          "model_explainability_job_output_config": {
            "kms_key_id": {
              "type": "string"
            }
          },
          "job_resources": {
            "cluster_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            }
          },
          "role_arn": {
            "type": "string"
          },
          "model_explainability_baseline_config": {
            "constraints_resource": {
              "s3_uri": {
                "type": "string"
              }
            }
          },
          "network_config": {
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelExplainabilityJobDefinition", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        job_definition_name: str,
        model_explainability_app_specification: ModelExplainabilityAppSpecification,
        model_explainability_job_input: ModelExplainabilityJobInput,
        model_explainability_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelExplainabilityJobDefinition"]:
        logger.debug("Creating model_explainability_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelExplainabilityBaselineConfig': model_explainability_baseline_config,
            'ModelExplainabilityAppSpecification': model_explainability_app_specification,
            'ModelExplainabilityJobInput': model_explainability_job_input,
            'ModelExplainabilityJobOutputConfig': model_explainability_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelExplainabilityJobDefinition', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_explainability_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelExplainabilityJobDefinition"]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_explainability_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelExplainabilityJobDefinitionResponse')
        model_explainability_job_definition = cls(**transformed_response)
        return model_explainability_job_definition
    
    def refresh(self) -> Optional["ModelExplainabilityJobDefinition"]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_explainability_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelExplainabilityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_explainability_job_definition(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        endpoint_name: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelExplainabilityJobDefinition"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'EndpointName': endpoint_name,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
        custom_key_mapping = {"monitoring_job_definition_name": "job_definition_name", "monitoring_job_definition_arn": "job_definition_arn"}
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_explainability_job_definitions',
            summaries_key='JobDefinitionSummaries',
            summary_name='MonitoringJobDefinitionSummary',
            resource_cls=ModelExplainabilityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args
        )


class ModelPackage(Base):
    """
    ModelPackage 
     Class representing resource ModelPackage
    Attributes
    ---------------------
    model_package_name:<p>The name of the model package being described.</p>
    model_package_arn:<p>The Amazon Resource Name (ARN) of the model package.</p>
    creation_time:<p>A timestamp specifying when the model package was created.</p>
    model_package_status:<p>The current status of the model package.</p>
    model_package_status_details:<p>Details about the current status of the model package.</p>
    model_package_group_name:<p>If the model is a versioned model, the name of the model group that the versioned model belongs to.</p>
    model_package_version:<p>The version of the model package.</p>
    model_package_description:<p>A brief summary of the model package.</p>
    inference_specification:<p>Details about inference jobs that you can run with models based on this model package.</p>
    source_algorithm_specification:<p>Details about the algorithm that was used to create the model package.</p>
    validation_specification:<p>Configurations for one or more transform jobs that SageMaker runs to test the model package.</p>
    certify_for_marketplace:<p>Whether the model package is certified for listing on Amazon Web Services Marketplace.</p>
    model_approval_status:<p>The approval status of the model package.</p>
    created_by:
    metadata_properties:
    model_metrics:<p>Metrics for the model.</p>
    last_modified_time:<p>The last time that the model package was modified.</p>
    last_modified_by:
    approval_description:<p>A description provided for the model approval.</p>
    domain:<p>The machine learning domain of the model package you specified. Common machine learning domains include computer vision and natural language processing.</p>
    task:<p>The machine learning task you specified that your model package accomplishes. Common machine learning tasks include object detection and image classification.</p>
    sample_payload_url:<p>The Amazon Simple Storage Service (Amazon S3) path where the sample payload are stored. This path points to a single gzip compressed tar archive (.tar.gz suffix).</p>
    customer_metadata_properties:<p>The metadata properties associated with the model package versions.</p>
    drift_check_baselines:<p>Represents the drift check baselines that can be used when the model monitor is set using the model package. For more information, see the topic on <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-quality-clarify-baseline-lifecycle.html#pipelines-quality-clarify-baseline-drift-detection">Drift Detection against Previous Baselines in SageMaker Pipelines</a> in the <i>Amazon SageMaker Developer Guide</i>. </p>
    additional_inference_specifications:<p>An array of additional Inference Specification objects. Each additional Inference Specification specifies artifacts based on this model package that can be used on inference endpoints. Generally used with SageMaker Neo to store the compiled artifacts.</p>
    skip_model_validation:<p>Indicates if you want to skip model validation.</p>
    source_uri:<p>The URI of the source for the model package.</p>
    
    """
    model_package_name: str
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_arn: Optional[str] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned()
    validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned()
    model_package_status: Optional[str] = Unassigned()
    model_package_status_details: Optional[ModelPackageStatusDetails] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    model_metrics: Optional[ModelMetrics] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    approval_description: Optional[str] = Unassigned()
    domain: Optional[str] = Unassigned()
    task: Optional[str] = Unassigned()
    sample_payload_url: Optional[str] = Unassigned()
    customer_metadata_properties: Optional[Dict[str, str]] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    additional_inference_specifications: Optional[List[AdditionalInferenceSpecificationDefinition]] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()
    source_uri: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_package_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "validation_specification": {
            "validation_role": {
              "type": "string"
            }
          },
          "model_metrics": {
            "model_quality": {
              "statistics": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "constraints": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "model_data_quality": {
              "statistics": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "constraints": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "bias": {
              "report": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "pre_training_report": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "post_training_report": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "explainability": {
              "report": {
                "s3_uri": {
                  "type": "string"
                }
              }
            }
          },
          "drift_check_baselines": {
            "bias": {
              "config_file": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "pre_training_constraints": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "post_training_constraints": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "explainability": {
              "constraints": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "config_file": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "model_quality": {
              "statistics": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "constraints": {
                "s3_uri": {
                  "type": "string"
                }
              }
            },
            "model_data_quality": {
              "statistics": {
                "s3_uri": {
                  "type": "string"
                }
              },
              "constraints": {
                "s3_uri": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelPackage", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        model_package_name: Optional[str] = Unassigned(),
        model_package_group_name: Optional[Union[str, object]] = Unassigned(),
        model_package_description: Optional[str] = Unassigned(),
        inference_specification: Optional[InferenceSpecification] = Unassigned(),
        validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned(),
        source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned(),
        certify_for_marketplace: Optional[bool] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        model_approval_status: Optional[str] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        model_metrics: Optional[ModelMetrics] = Unassigned(),
        client_token: Optional[str] = Unassigned(),
        domain: Optional[str] = Unassigned(),
        task: Optional[str] = Unassigned(),
        sample_payload_url: Optional[str] = Unassigned(),
        customer_metadata_properties: Optional[Dict[str, str]] = Unassigned(),
        drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned(),
        additional_inference_specifications: Optional[List[AdditionalInferenceSpecificationDefinition]] = Unassigned(),
        skip_model_validation: Optional[str] = Unassigned(),
        source_uri: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackage"]:
        logger.debug("Creating model_package resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ModelPackageName': model_package_name,
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageDescription': model_package_description,
            'InferenceSpecification': inference_specification,
            'ValidationSpecification': validation_specification,
            'SourceAlgorithmSpecification': source_algorithm_specification,
            'CertifyForMarketplace': certify_for_marketplace,
            'Tags': tags,
            'ModelApprovalStatus': model_approval_status,
            'MetadataProperties': metadata_properties,
            'ModelMetrics': model_metrics,
            'ClientToken': client_token,
            'Domain': domain,
            'Task': task,
            'SamplePayloadUrl': sample_payload_url,
            'CustomerMetadataProperties': customer_metadata_properties,
            'DriftCheckBaselines': drift_check_baselines,
            'AdditionalInferenceSpecifications': additional_inference_specifications,
            'SkipModelValidation': skip_model_validation,
            'SourceUri': source_uri,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelPackage', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_package(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_package_name=response['ModelPackageName'], session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_package_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackage"]:
        operation_input_args = {
            'ModelPackageName': model_package_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_package(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelPackageOutput')
        model_package = cls(**transformed_response)
        return model_package
    
    def refresh(self) -> Optional["ModelPackage"]:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelPackageOutput', self)
        return self
    
    def update(
        self,
        customer_metadata_properties_to_remove: Optional[List[str]] = Unassigned(),
        additional_inference_specifications_to_add: Optional[List[AdditionalInferenceSpecificationDefinition]] = Unassigned(),
    ) -> Optional["ModelPackage"]:
        logger.debug("Creating model_package resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ModelPackageArn': self.model_package_arn,
            'ModelApprovalStatus': self.model_approval_status,
            'ApprovalDescription': self.approval_description,
            'CustomerMetadataProperties': self.customer_metadata_properties,
            'CustomerMetadataPropertiesToRemove': customer_metadata_properties_to_remove,
            'AdditionalInferenceSpecificationsToAdd': additional_inference_specifications_to_add,
            'InferenceSpecification': self.inference_specification,
            'SourceUri': self.source_uri,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = ModelPackage._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_model_package(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        self.client.delete_model_package(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ModelPackage"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_package_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="ModelPackage", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ModelPackage", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        model_approval_status: Optional[str] = Unassigned(),
        model_package_group_name: Optional[str] = Unassigned(),
        model_package_type: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelPackage"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'ModelApprovalStatus': model_approval_status,
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageType': model_package_type,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_packages',
            summaries_key='ModelPackageSummaryList',
            summary_name='ModelPackageSummary',
            resource_cls=ModelPackage,
            list_method_kwargs=operation_input_args
        )


class ModelPackageGroup(Base):
    """
    ModelPackageGroup 
     Class representing resource ModelPackageGroup
    Attributes
    ---------------------
    model_package_group_name:<p>The name of the model group.</p>
    model_package_group_arn:<p>The Amazon Resource Name (ARN) of the model group.</p>
    creation_time:<p>The time that the model group was created.</p>
    created_by:
    model_package_group_status:<p>The status of the model group.</p>
    model_package_group_description:<p>A description of the model group.</p>
    
    """
    model_package_group_name: str
    model_package_group_arn: Optional[str] = Unassigned()
    model_package_group_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    model_package_group_status: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_package_group_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        model_package_group_name: str,
        model_package_group_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackageGroup"]:
        logger.debug("Creating model_package_group resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageGroupDescription': model_package_group_description,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelPackageGroup', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_package_group(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(model_package_group_name=model_package_group_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        model_package_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackageGroup"]:
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_package_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelPackageGroupOutput')
        model_package_group = cls(**transformed_response)
        return model_package_group
    
    def refresh(self) -> Optional["ModelPackageGroup"]:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package_group(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelPackageGroupOutput', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        self.client.delete_model_package_group(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'InProgress', 'Completed', 'Failed', 'Deleting', 'DeleteFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ModelPackageGroup"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.model_package_group_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="ModelPackageGroup", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ModelPackageGroup", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelPackageGroup"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_package_groups',
            summaries_key='ModelPackageGroupSummaryList',
            summary_name='ModelPackageGroupSummary',
            resource_cls=ModelPackageGroup,
            list_method_kwargs=operation_input_args
        )


class ModelQualityJobDefinition(Base):
    """
    ModelQualityJobDefinition 
     Class representing resource ModelQualityJobDefinition
    Attributes
    ---------------------
    job_definition_arn:<p>The Amazon Resource Name (ARN) of the model quality job.</p>
    job_definition_name:<p>The name of the quality job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.</p>
    creation_time:<p>The time at which the model quality job was created.</p>
    model_quality_app_specification:<p>Configures the model quality job to run a specified Docker container image.</p>
    model_quality_job_input:<p>Inputs for the model quality job.</p>
    model_quality_job_output_config:
    job_resources:
    role_arn:<p>The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.</p>
    model_quality_baseline_config:<p>The baseline configuration for a model quality job.</p>
    network_config:<p>Networking options for a model quality job.</p>
    stopping_condition:
    
    """
    job_definition_name: str
    job_definition_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_quality_baseline_config: Optional[ModelQualityBaselineConfig] = Unassigned()
    model_quality_app_specification: Optional[ModelQualityAppSpecification] = Unassigned()
    model_quality_job_input: Optional[ModelQualityJobInput] = Unassigned()
    model_quality_job_output_config: Optional[MonitoringOutputConfig] = Unassigned()
    job_resources: Optional[MonitoringResources] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'model_quality_job_definition_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "model_quality_job_input": {
            "ground_truth_s3_input": {
              "s3_uri": {
                "type": "string"
              }
            },
            "endpoint_input": {
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            },
            "batch_transform_input": {
              "data_captured_destination_s3_uri": {
                "type": "string"
              },
              "s3_input_mode": {
                "type": "string"
              },
              "s3_data_distribution_type": {
                "type": "string"
              }
            }
          },
          "model_quality_job_output_config": {
            "kms_key_id": {
              "type": "string"
            }
          },
          "job_resources": {
            "cluster_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            }
          },
          "role_arn": {
            "type": "string"
          },
          "model_quality_baseline_config": {
            "constraints_resource": {
              "s3_uri": {
                "type": "string"
              }
            }
          },
          "network_config": {
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ModelQualityJobDefinition", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        job_definition_name: str,
        model_quality_app_specification: ModelQualityAppSpecification,
        model_quality_job_input: ModelQualityJobInput,
        model_quality_job_output_config: MonitoringOutputConfig,
        job_resources: MonitoringResources,
        role_arn: str,
        model_quality_baseline_config: Optional[ModelQualityBaselineConfig] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelQualityJobDefinition"]:
        logger.debug("Creating model_quality_job_definition resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
            'ModelQualityBaselineConfig': model_quality_baseline_config,
            'ModelQualityAppSpecification': model_quality_app_specification,
            'ModelQualityJobInput': model_quality_job_input,
            'ModelQualityJobOutputConfig': model_quality_job_output_config,
            'JobResources': job_resources,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ModelQualityJobDefinition', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_model_quality_job_definition(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(job_definition_name=job_definition_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelQualityJobDefinition"]:
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_model_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeModelQualityJobDefinitionResponse')
        model_quality_job_definition = cls(**transformed_response)
        return model_quality_job_definition
    
    def refresh(self) -> Optional["ModelQualityJobDefinition"]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_quality_job_definition(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeModelQualityJobDefinitionResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_quality_job_definition(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        endpoint_name: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ModelQualityJobDefinition"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'EndpointName': endpoint_name,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
        }
        custom_key_mapping = {"monitoring_job_definition_name": "job_definition_name", "monitoring_job_definition_arn": "job_definition_arn"}
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_model_quality_job_definitions',
            summaries_key='JobDefinitionSummaries',
            summary_name='MonitoringJobDefinitionSummary',
            resource_cls=ModelQualityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args
        )


class MonitoringSchedule(Base):
    """
    MonitoringSchedule 
     Class representing resource MonitoringSchedule
    Attributes
    ---------------------
    monitoring_schedule_arn:<p>The Amazon Resource Name (ARN) of the monitoring schedule.</p>
    monitoring_schedule_name:<p>Name of the monitoring schedule.</p>
    monitoring_schedule_status:<p>The status of an monitoring job.</p>
    creation_time:<p>The time at which the monitoring job was created.</p>
    last_modified_time:<p>The time at which the monitoring job was last modified.</p>
    monitoring_schedule_config:<p>The configuration object that specifies the monitoring schedule and defines the monitoring job.</p>
    monitoring_type:<p>The type of the monitoring job that this schedule runs. This is one of the following values.</p> <ul> <li> <p> <code>DATA_QUALITY</code> - The schedule is for a data quality monitoring job.</p> </li> <li> <p> <code>MODEL_QUALITY</code> - The schedule is for a model quality monitoring job.</p> </li> <li> <p> <code>MODEL_BIAS</code> - The schedule is for a bias monitoring job.</p> </li> <li> <p> <code>MODEL_EXPLAINABILITY</code> - The schedule is for an explainability monitoring job.</p> </li> </ul>
    failure_reason:<p>A string, up to one KB in size, that contains the reason a monitoring job failed, if it failed.</p>
    endpoint_name:<p> The name of the endpoint for the monitoring job.</p>
    last_monitoring_execution_summary:<p>Describes metadata on the last execution to run, if there was one.</p>
    
    """
    monitoring_schedule_name: str
    monitoring_schedule_arn: Optional[str] = Unassigned()
    monitoring_schedule_status: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_config: Optional[MonitoringScheduleConfig] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'monitoring_schedule_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "monitoring_schedule_config": {
            "monitoring_job_definition": {
              "monitoring_output_config": {
                "kms_key_id": {
                  "type": "string"
                }
              },
              "monitoring_resources": {
                "cluster_config": {
                  "volume_kms_key_id": {
                    "type": "string"
                  }
                }
              },
              "role_arn": {
                "type": "string"
              },
              "baseline_config": {
                "constraints_resource": {
                  "s3_uri": {
                    "type": "string"
                  }
                },
                "statistics_resource": {
                  "s3_uri": {
                    "type": "string"
                  }
                }
              },
              "network_config": {
                "vpc_config": {
                  "security_group_ids": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "subnets": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "MonitoringSchedule", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        monitoring_schedule_name: str,
        monitoring_schedule_config: MonitoringScheduleConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["MonitoringSchedule"]:
        logger.debug("Creating monitoring_schedule resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
            'MonitoringScheduleConfig': monitoring_schedule_config,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='MonitoringSchedule', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_monitoring_schedule(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(monitoring_schedule_name=monitoring_schedule_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        monitoring_schedule_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["MonitoringSchedule"]:
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_monitoring_schedule(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeMonitoringScheduleResponse')
        monitoring_schedule = cls(**transformed_response)
        return monitoring_schedule
    
    def refresh(self) -> Optional["MonitoringSchedule"]:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        client = SageMakerClient().client
        response = client.describe_monitoring_schedule(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeMonitoringScheduleResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["MonitoringSchedule"]:
        logger.debug("Creating monitoring_schedule resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
            'MonitoringScheduleConfig': self.monitoring_schedule_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = MonitoringSchedule._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_monitoring_schedule(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        self.client.delete_monitoring_schedule(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        self.client.stop_monitoring_schedule(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'Failed', 'Scheduled', 'Stopped'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["MonitoringSchedule"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.monitoring_schedule_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="MonitoringSchedule", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="MonitoringSchedule", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        endpoint_name: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        monitoring_job_definition_name: Optional[str] = Unassigned(),
        monitoring_type_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["MonitoringSchedule"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'EndpointName': endpoint_name,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'StatusEquals': status_equals,
            'MonitoringJobDefinitionName': monitoring_job_definition_name,
            'MonitoringTypeEquals': monitoring_type_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_monitoring_schedules',
            summaries_key='MonitoringScheduleSummaries',
            summary_name='MonitoringScheduleSummary',
            resource_cls=MonitoringSchedule,
            list_method_kwargs=operation_input_args
        )


class NotebookInstance(Base):
    """
    NotebookInstance 
     Class representing resource NotebookInstance
    Attributes
    ---------------------
    notebook_instance_arn:<p>The Amazon Resource Name (ARN) of the notebook instance.</p>
    notebook_instance_name:<p>The name of the SageMaker notebook instance. </p>
    notebook_instance_status:<p>The status of the notebook instance.</p>
    failure_reason:<p>If status is <code>Failed</code>, the reason it failed.</p>
    url:<p>The URL that you use to connect to the Jupyter notebook that is running in your notebook instance. </p>
    instance_type:<p>The type of ML compute instance running on the notebook instance.</p>
    subnet_id:<p>The ID of the VPC subnet.</p>
    security_groups:<p>The IDs of the VPC security groups.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of the IAM role associated with the instance. </p>
    kms_key_id:<p>The Amazon Web Services KMS key ID SageMaker uses to encrypt data when storing it on the ML storage volume attached to the instance. </p>
    network_interface_id:<p>The network interface IDs that SageMaker created at the time of creating the instance. </p>
    last_modified_time:<p>A timestamp. Use this parameter to retrieve the time when the notebook instance was last modified. </p>
    creation_time:<p>A timestamp. Use this parameter to return the time when the notebook instance was created</p>
    notebook_instance_lifecycle_config_name:<p>Returns the name of a notebook instance lifecycle configuration.</p> <p>For information about notebook instance lifestyle configurations, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-lifecycle-config.html">Step 2.1: (Optional) Customize a Notebook Instance</a> </p>
    direct_internet_access:<p>Describes whether SageMaker provides internet access to the notebook instance. If this value is set to <i>Disabled</i>, the notebook instance does not have internet access, and cannot connect to SageMaker training and endpoint services.</p> <p>For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/appendix-additional-considerations.html#appendix-notebook-and-internet-access">Notebook Instances Are Internet-Enabled by Default</a>.</p>
    volume_size_in_g_b:<p>The size, in GB, of the ML storage volume attached to the notebook instance.</p>
    accelerator_types:<p>A list of the Elastic Inference (EI) instance types associated with this notebook instance. Currently only one EI instance type can be associated with a notebook instance. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/ei.html">Using Elastic Inference in Amazon SageMaker</a>.</p>
    default_code_repository:<p>The Git repository associated with the notebook instance as its default code repository. This can be either the name of a Git repository stored as a resource in your account, or the URL of a Git repository in <a href="https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html">Amazon Web Services CodeCommit</a> or in any other Git repository. When you open a notebook instance, it opens in the directory that contains this repository. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/nbi-git-repo.html">Associating Git Repositories with SageMaker Notebook Instances</a>.</p>
    additional_code_repositories:<p>An array of up to three Git repositories associated with the notebook instance. These can be either the names of Git repositories stored as resources in your account, or the URL of Git repositories in <a href="https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html">Amazon Web Services CodeCommit</a> or in any other Git repository. These repositories are cloned at the same level as the default repository of your notebook instance. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/nbi-git-repo.html">Associating Git Repositories with SageMaker Notebook Instances</a>.</p>
    root_access:<p>Whether root access is enabled or disabled for users of the notebook instance.</p> <note> <p>Lifecycle configurations need root access to be able to set up a notebook instance. Because of this, lifecycle configurations associated with a notebook instance always run with root access even if you disable root access for users.</p> </note>
    platform_identifier:<p>The platform identifier of the notebook instance runtime environment.</p>
    instance_metadata_service_configuration:<p>Information on the IMDS configuration of the notebook instance</p>
    
    """
    notebook_instance_name: str
    notebook_instance_arn: Optional[str] = Unassigned()
    notebook_instance_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    subnet_id: Optional[str] = Unassigned()
    security_groups: Optional[List[str]] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    network_interface_id: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    direct_internet_access: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    accelerator_types: Optional[List[str]] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[List[str]] = Unassigned()
    root_access: Optional[str] = Unassigned()
    platform_identifier: Optional[str] = Unassigned()
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'notebook_instance_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "subnet_id": {
            "type": "string"
          },
          "security_groups": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "kms_key_id": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "NotebookInstance", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        notebook_instance_name: str,
        instance_type: str,
        role_arn: str,
        subnet_id: Optional[str] = Unassigned(),
        security_group_ids: Optional[List[str]] = Unassigned(),
        kms_key_id: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        lifecycle_config_name: Optional[str] = Unassigned(),
        direct_internet_access: Optional[str] = Unassigned(),
        volume_size_in_g_b: Optional[int] = Unassigned(),
        accelerator_types: Optional[List[str]] = Unassigned(),
        default_code_repository: Optional[str] = Unassigned(),
        additional_code_repositories: Optional[List[str]] = Unassigned(),
        root_access: Optional[str] = Unassigned(),
        platform_identifier: Optional[str] = Unassigned(),
        instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstance"]:
        logger.debug("Creating notebook_instance resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'NotebookInstanceName': notebook_instance_name,
            'InstanceType': instance_type,
            'SubnetId': subnet_id,
            'SecurityGroupIds': security_group_ids,
            'RoleArn': role_arn,
            'KmsKeyId': kms_key_id,
            'Tags': tags,
            'LifecycleConfigName': lifecycle_config_name,
            'DirectInternetAccess': direct_internet_access,
            'VolumeSizeInGB': volume_size_in_g_b,
            'AcceleratorTypes': accelerator_types,
            'DefaultCodeRepository': default_code_repository,
            'AdditionalCodeRepositories': additional_code_repositories,
            'RootAccess': root_access,
            'PlatformIdentifier': platform_identifier,
            'InstanceMetadataServiceConfiguration': instance_metadata_service_configuration,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='NotebookInstance', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_notebook_instance(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(notebook_instance_name=notebook_instance_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        notebook_instance_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstance"]:
        operation_input_args = {
            'NotebookInstanceName': notebook_instance_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_notebook_instance(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeNotebookInstanceOutput')
        notebook_instance = cls(**transformed_response)
        return notebook_instance
    
    def refresh(self) -> Optional["NotebookInstance"]:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeNotebookInstanceOutput', self)
        return self
    
    def update(
        self,
        lifecycle_config_name: Optional[str] = Unassigned(),
        disassociate_lifecycle_config: Optional[bool] = Unassigned(),
        disassociate_accelerator_types: Optional[bool] = Unassigned(),
        disassociate_default_code_repository: Optional[bool] = Unassigned(),
        disassociate_additional_code_repositories: Optional[bool] = Unassigned(),
    ) -> Optional["NotebookInstance"]:
        logger.debug("Creating notebook_instance resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
            'InstanceType': self.instance_type,
            'RoleArn': self.role_arn,
            'LifecycleConfigName': lifecycle_config_name,
            'DisassociateLifecycleConfig': disassociate_lifecycle_config,
            'VolumeSizeInGB': self.volume_size_in_g_b,
            'DefaultCodeRepository': self.default_code_repository,
            'AdditionalCodeRepositories': self.additional_code_repositories,
            'AcceleratorTypes': self.accelerator_types,
            'DisassociateAcceleratorTypes': disassociate_accelerator_types,
            'DisassociateDefaultCodeRepository': disassociate_default_code_repository,
            'DisassociateAdditionalCodeRepositories': disassociate_additional_code_repositories,
            'RootAccess': self.root_access,
            'InstanceMetadataServiceConfiguration': self.instance_metadata_service_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = NotebookInstance._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_notebook_instance(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        self.client.delete_notebook_instance(**operation_input_args)
    
    def stop(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        self.client.stop_notebook_instance(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'InService', 'Stopping', 'Stopped', 'Failed', 'Deleting', 'Updating'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["NotebookInstance"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.notebook_instance_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="NotebookInstance", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="NotebookInstance", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        notebook_instance_lifecycle_config_name_contains: Optional[str] = Unassigned(),
        default_code_repository_contains: Optional[str] = Unassigned(),
        additional_code_repository_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["NotebookInstance"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'StatusEquals': status_equals,
            'NotebookInstanceLifecycleConfigNameContains': notebook_instance_lifecycle_config_name_contains,
            'DefaultCodeRepositoryContains': default_code_repository_contains,
            'AdditionalCodeRepositoryEquals': additional_code_repository_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_notebook_instances',
            summaries_key='NotebookInstances',
            summary_name='NotebookInstanceSummary',
            resource_cls=NotebookInstance,
            list_method_kwargs=operation_input_args
        )


class NotebookInstanceLifecycleConfig(Base):
    """
    NotebookInstanceLifecycleConfig 
     Class representing resource NotebookInstanceLifecycleConfig
    Attributes
    ---------------------
    notebook_instance_lifecycle_config_arn:<p>The Amazon Resource Name (ARN) of the lifecycle configuration.</p>
    notebook_instance_lifecycle_config_name:<p>The name of the lifecycle configuration.</p>
    on_create:<p>The shell script that runs only once, when you create a notebook instance.</p>
    on_start:<p>The shell script that runs every time you start a notebook instance, including when you create the notebook instance.</p>
    last_modified_time:<p>A timestamp that tells when the lifecycle configuration was last modified.</p>
    creation_time:<p>A timestamp that tells when the lifecycle configuration was created.</p>
    
    """
    notebook_instance_lifecycle_config_name: str
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'notebook_instance_lifecycle_config_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        notebook_instance_lifecycle_config_name: str,
        on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstanceLifecycleConfig"]:
        logger.debug("Creating notebook_instance_lifecycle_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
            'OnCreate': on_create,
            'OnStart': on_start,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='NotebookInstanceLifecycleConfig', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_notebook_instance_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(notebook_instance_lifecycle_config_name=notebook_instance_lifecycle_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        notebook_instance_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstanceLifecycleConfig"]:
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeNotebookInstanceLifecycleConfigOutput')
        notebook_instance_lifecycle_config = cls(**transformed_response)
        return notebook_instance_lifecycle_config
    
    def refresh(self) -> Optional["NotebookInstanceLifecycleConfig"]:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeNotebookInstanceLifecycleConfigOutput', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["NotebookInstanceLifecycleConfig"]:
        logger.debug("Creating notebook_instance_lifecycle_config resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
            'OnCreate': self.on_create,
            'OnStart': self.on_start,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = NotebookInstanceLifecycleConfig._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_notebook_instance_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        self.client.delete_notebook_instance_lifecycle_config(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["NotebookInstanceLifecycleConfig"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_notebook_instance_lifecycle_configs',
            summaries_key='NotebookInstanceLifecycleConfigs',
            summary_name='NotebookInstanceLifecycleConfigSummary',
            resource_cls=NotebookInstanceLifecycleConfig,
            list_method_kwargs=operation_input_args
        )


class Pipeline(Base):
    """
    Pipeline 
     Class representing resource Pipeline
    Attributes
    ---------------------
    pipeline_arn:<p>The Amazon Resource Name (ARN) of the pipeline.</p>
    pipeline_name:<p>The name of the pipeline.</p>
    pipeline_display_name:<p>The display name of the pipeline.</p>
    pipeline_definition:<p>The JSON pipeline definition.</p>
    pipeline_description:<p>The description of the pipeline.</p>
    role_arn:<p>The Amazon Resource Name (ARN) that the pipeline uses to execute.</p>
    pipeline_status:<p>The status of the pipeline execution.</p>
    creation_time:<p>The time when the pipeline was created.</p>
    last_modified_time:<p>The time when the pipeline was last modified.</p>
    last_run_time:<p>The time when the pipeline was last run.</p>
    created_by:
    last_modified_by:
    parallelism_configuration:<p>Lists the parallelism configuration applied to the pipeline.</p>
    
    """
    pipeline_name: str
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_display_name: Optional[str] = Unassigned()
    pipeline_definition: Optional[str] = Unassigned()
    pipeline_description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    pipeline_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_run_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'pipeline_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "role_arn": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Pipeline", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        pipeline_name: str,
        client_request_token: str,
        role_arn: str,
        pipeline_display_name: Optional[str] = Unassigned(),
        pipeline_definition: Optional[str] = Unassigned(),
        pipeline_definition_s3_location: Optional[PipelineDefinitionS3Location] = Unassigned(),
        pipeline_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Pipeline"]:
        logger.debug("Creating pipeline resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'PipelineName': pipeline_name,
            'PipelineDisplayName': pipeline_display_name,
            'PipelineDefinition': pipeline_definition,
            'PipelineDefinitionS3Location': pipeline_definition_s3_location,
            'PipelineDescription': pipeline_description,
            'ClientRequestToken': client_request_token,
            'RoleArn': role_arn,
            'Tags': tags,
            'ParallelismConfiguration': parallelism_configuration,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Pipeline', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_pipeline(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(pipeline_name=pipeline_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        pipeline_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Pipeline"]:
        operation_input_args = {
            'PipelineName': pipeline_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_pipeline(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribePipelineResponse')
        pipeline = cls(**transformed_response)
        return pipeline
    
    def refresh(self) -> Optional["Pipeline"]:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribePipelineResponse', self)
        return self
    
    def update(
        self,
        pipeline_definition_s3_location: Optional[PipelineDefinitionS3Location] = Unassigned(),
    ) -> Optional["Pipeline"]:
        logger.debug("Creating pipeline resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
            'PipelineDisplayName': self.pipeline_display_name,
            'PipelineDefinition': self.pipeline_definition,
            'PipelineDefinitionS3Location': pipeline_definition_s3_location,
            'PipelineDescription': self.pipeline_description,
            'RoleArn': self.role_arn,
            'ParallelismConfiguration': self.parallelism_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Pipeline._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_pipeline(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.delete_pipeline(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Active', 'Deleting'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Pipeline"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.pipeline_status
    
            if status == current_status:
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Pipeline", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        pipeline_name_prefix: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Pipeline"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'PipelineNamePrefix': pipeline_name_prefix,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_pipelines',
            summaries_key='PipelineSummaries',
            summary_name='PipelineSummary',
            resource_cls=Pipeline,
            list_method_kwargs=operation_input_args
        )


class PipelineExecution(Base):
    """
    PipelineExecution 
     Class representing resource PipelineExecution
    Attributes
    ---------------------
    pipeline_arn:<p>The Amazon Resource Name (ARN) of the pipeline.</p>
    pipeline_execution_arn:<p>The Amazon Resource Name (ARN) of the pipeline execution.</p>
    pipeline_execution_display_name:<p>The display name of the pipeline execution.</p>
    pipeline_execution_status:<p>The status of the pipeline execution.</p>
    pipeline_execution_description:<p>The description of the pipeline execution.</p>
    pipeline_experiment_config:
    failure_reason:<p>If the execution failed, a message describing why.</p>
    creation_time:<p>The time when the pipeline execution was created.</p>
    last_modified_time:<p>The time when the pipeline execution was modified last.</p>
    created_by:
    last_modified_by:
    parallelism_configuration:<p>The parallelism configuration applied to the pipeline.</p>
    selective_execution_config:<p>The selective execution configuration applied to the pipeline run.</p>
    
    """
    pipeline_execution_arn: str
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_execution_display_name: Optional[str] = Unassigned()
    pipeline_execution_status: Optional[str] = Unassigned()
    pipeline_execution_description: Optional[str] = Unassigned()
    pipeline_experiment_config: Optional[PipelineExperimentConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned()
    selective_execution_config: Optional[SelectiveExecutionConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'pipeline_execution_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def get(
        cls,
        pipeline_execution_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["PipelineExecution"]:
        operation_input_args = {
            'PipelineExecutionArn': pipeline_execution_arn,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_pipeline_execution(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribePipelineExecutionResponse')
        pipeline_execution = cls(**transformed_response)
        return pipeline_execution
    
    def refresh(self) -> Optional["PipelineExecution"]:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline_execution(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribePipelineExecutionResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["PipelineExecution"]:
        logger.debug("Creating pipeline_execution resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
            'PipelineExecutionDescription': self.pipeline_execution_description,
            'PipelineExecutionDisplayName': self.pipeline_execution_display_name,
            'ParallelismConfiguration': self.parallelism_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = PipelineExecution._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_pipeline_execution(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.stop_pipeline_execution(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Executing', 'Stopping', 'Stopped', 'Failed', 'Succeeded'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["PipelineExecution"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.pipeline_execution_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="PipelineExecution", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="PipelineExecution", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        pipeline_name: str,
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["PipelineExecution"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'PipelineName': pipeline_name,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_pipeline_executions',
            summaries_key='PipelineExecutionSummaries',
            summary_name='PipelineExecutionSummary',
            resource_cls=PipelineExecution,
            list_method_kwargs=operation_input_args
        )


class ProcessingJob(Base):
    """
    ProcessingJob 
     Class representing resource ProcessingJob
    Attributes
    ---------------------
    processing_job_name:<p>The name of the processing job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.</p>
    processing_resources:<p>Identifies the resources, ML compute instances, and ML storage volumes to deploy for a processing job. In distributed training, you specify more than one instance.</p>
    app_specification:<p>Configures the processing job to run a specified container image.</p>
    processing_job_arn:<p>The Amazon Resource Name (ARN) of the processing job.</p>
    processing_job_status:<p>Provides the status of a processing job.</p>
    creation_time:<p>The time at which the processing job was created.</p>
    processing_inputs:<p>The inputs for a processing job.</p>
    processing_output_config:<p>Output configuration for the processing job.</p>
    stopping_condition:<p>The time limit for how long the processing job is allowed to run.</p>
    environment:<p>The environment variables set in the Docker container.</p>
    network_config:<p>Networking options for a processing job.</p>
    role_arn:<p>The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.</p>
    experiment_config:<p>The configuration information used to create an experiment.</p>
    exit_message:<p>An optional string, up to one KB in size, that contains metadata from the processing container when the processing job exits.</p>
    failure_reason:<p>A string, up to one KB in size, that contains the reason a processing job failed, if it failed.</p>
    processing_end_time:<p>The time at which the processing job completed.</p>
    processing_start_time:<p>The time at which the processing job started.</p>
    last_modified_time:<p>The time at which the processing job was last modified.</p>
    monitoring_schedule_arn:<p>The ARN of a monitoring schedule for an endpoint associated with this processing job.</p>
    auto_m_l_job_arn:<p>The ARN of an AutoML job associated with this processing job.</p>
    training_job_arn:<p>The ARN of a training job associated with this processing job.</p>
    
    """
    processing_job_name: str
    processing_inputs: Optional[List[ProcessingInput]] = Unassigned()
    processing_output_config: Optional[ProcessingOutputConfig] = Unassigned()
    processing_resources: Optional[ProcessingResources] = Unassigned()
    stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned()
    app_specification: Optional[AppSpecification] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    network_config: Optional[NetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    processing_job_arn: Optional[str] = Unassigned()
    processing_job_status: Optional[str] = Unassigned()
    exit_message: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    processing_end_time: Optional[datetime.datetime] = Unassigned()
    processing_start_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    training_job_arn: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'processing_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "processing_resources": {
            "cluster_config": {
              "volume_kms_key_id": {
                "type": "string"
              }
            }
          },
          "processing_output_config": {
            "kms_key_id": {
              "type": "string"
            }
          },
          "network_config": {
            "vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          },
          "role_arn": {
            "type": "string"
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "ProcessingJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        processing_job_name: str,
        processing_resources: ProcessingResources,
        app_specification: AppSpecification,
        role_arn: str,
        processing_inputs: Optional[List[ProcessingInput]] = Unassigned(),
        processing_output_config: Optional[ProcessingOutputConfig] = Unassigned(),
        stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        network_config: Optional[NetworkConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ProcessingJob"]:
        logger.debug("Creating processing_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ProcessingInputs': processing_inputs,
            'ProcessingOutputConfig': processing_output_config,
            'ProcessingJobName': processing_job_name,
            'ProcessingResources': processing_resources,
            'StoppingCondition': stopping_condition,
            'AppSpecification': app_specification,
            'Environment': environment,
            'NetworkConfig': network_config,
            'RoleArn': role_arn,
            'Tags': tags,
            'ExperimentConfig': experiment_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='ProcessingJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_processing_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(processing_job_name=processing_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        processing_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ProcessingJob"]:
        operation_input_args = {
            'ProcessingJobName': processing_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_processing_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeProcessingJobResponse')
        processing_job = cls(**transformed_response)
        return processing_job
    
    def refresh(self) -> Optional["ProcessingJob"]:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_processing_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeProcessingJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        self.client.stop_processing_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["ProcessingJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.processing_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="ProcessingJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ProcessingJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["ProcessingJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_processing_jobs',
            summaries_key='ProcessingJobSummaries',
            summary_name='ProcessingJobSummary',
            resource_cls=ProcessingJob,
            list_method_kwargs=operation_input_args
        )


class Project(Base):
    """
    Project 
     Class representing resource Project
    Attributes
    ---------------------
    project_arn:<p>The Amazon Resource Name (ARN) of the project.</p>
    project_name:<p>The name of the project.</p>
    project_id:<p>The ID of the project.</p>
    service_catalog_provisioning_details:<p>Information used to provision a service catalog product. For information, see <a href="https://docs.aws.amazon.com/servicecatalog/latest/adminguide/introduction.html">What is Amazon Web Services Service Catalog</a>.</p>
    project_status:<p>The status of the project.</p>
    creation_time:<p>The time when the project was created.</p>
    project_description:<p>The description of the project.</p>
    service_catalog_provisioned_product_details:<p>Information about a provisioned service catalog product.</p>
    created_by:
    last_modified_time:<p>The timestamp when project was last modified.</p>
    last_modified_by:
    
    """
    project_name: str
    project_arn: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioning_details: Optional[ServiceCatalogProvisioningDetails] = Unassigned()
    service_catalog_provisioned_product_details: Optional[ServiceCatalogProvisionedProductDetails] = Unassigned()
    project_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'project_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        project_name: str,
        service_catalog_provisioning_details: ServiceCatalogProvisioningDetails,
        project_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Project"]:
        logger.debug("Creating project resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'ProjectName': project_name,
            'ProjectDescription': project_description,
            'ServiceCatalogProvisioningDetails': service_catalog_provisioning_details,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Project', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_project(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(project_name=project_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        project_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Project"]:
        operation_input_args = {
            'ProjectName': project_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_project(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeProjectOutput')
        project = cls(**transformed_response)
        return project
    
    def refresh(self) -> Optional["Project"]:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        client = SageMakerClient().client
        response = client.describe_project(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeProjectOutput', self)
        return self
    
    def update(
        self,
        service_catalog_provisioning_update_details: Optional[ServiceCatalogProvisioningUpdateDetails] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
    ) -> Optional["Project"]:
        logger.debug("Creating project resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'ProjectName': self.project_name,
            'ProjectDescription': self.project_description,
            'ServiceCatalogProvisioningUpdateDetails': service_catalog_provisioning_update_details,
            'Tags': tags,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Project._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_project(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        self.client.delete_project(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Pending', 'CreateInProgress', 'CreateCompleted', 'CreateFailed', 'DeleteInProgress', 'DeleteFailed', 'DeleteCompleted', 'UpdateInProgress', 'UpdateCompleted', 'UpdateFailed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Project"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.project_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Project", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Project", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Project"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'NameContains': name_contains,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_projects',
            summaries_key='ProjectSummaryList',
            summary_name='ProjectSummary',
            resource_cls=Project,
            list_method_kwargs=operation_input_args
        )


class Space(Base):
    """
    Space 
     Class representing resource Space
    Attributes
    ---------------------
    domain_id:<p>The ID of the associated domain.</p>
    space_arn:<p>The space's Amazon Resource Name (ARN).</p>
    space_name:<p>The name of the space.</p>
    home_efs_file_system_uid:<p>The ID of the space's profile in the Amazon EFS volume.</p>
    status:<p>The status.</p>
    last_modified_time:<p>The last modified time.</p>
    creation_time:<p>The creation time.</p>
    failure_reason:<p>The failure reason.</p>
    space_settings:<p>A collection of space settings.</p>
    ownership_settings:<p>The collection of ownership settings for a space.</p>
    space_sharing_settings:<p>The collection of space sharing settings for a space.</p>
    space_display_name:<p>The name of the space that appears in the Amazon SageMaker Studio UI.</p>
    url:<p>Returns the URL of the space. If the space is created with Amazon Web Services IAM Identity Center (Successor to Amazon Web Services Single Sign-On) authentication, users can navigate to the URL after appending the respective redirect parameter for the application type to be federated through Amazon Web Services IAM Identity Center.</p> <p>The following application types are supported:</p> <ul> <li> <p>Studio Classic: <code>&amp;redirect=JupyterServer</code> </p> </li> <li> <p>JupyterLab: <code>&amp;redirect=JupyterLab</code> </p> </li> <li> <p>Code Editor, based on Code-OSS, Visual Studio Code - Open Source: <code>&amp;redirect=CodeEditor</code> </p> </li> </ul>
    
    """
    domain_id: str
    space_name: str
    space_arn: Optional[str] = Unassigned()
    home_efs_file_system_uid: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    space_settings: Optional[SpaceSettings] = Unassigned()
    ownership_settings: Optional[OwnershipSettings] = Unassigned()
    space_sharing_settings: Optional[SpaceSharingSettings] = Unassigned()
    space_display_name: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'space_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        space_name: str,
        tags: Optional[List[Tag]] = Unassigned(),
        space_settings: Optional[SpaceSettings] = Unassigned(),
        ownership_settings: Optional[OwnershipSettings] = Unassigned(),
        space_sharing_settings: Optional[SpaceSharingSettings] = Unassigned(),
        space_display_name: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Space"]:
        logger.debug("Creating space resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
            'Tags': tags,
            'SpaceSettings': space_settings,
            'OwnershipSettings': ownership_settings,
            'SpaceSharingSettings': space_sharing_settings,
            'SpaceDisplayName': space_display_name,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Space', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_space(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, space_name=space_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        space_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Space"]:
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_space(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeSpaceResponse')
        space = cls(**transformed_response)
        return space
    
    def refresh(self) -> Optional["Space"]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        client = SageMakerClient().client
        response = client.describe_space(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeSpaceResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["Space"]:
        logger.debug("Creating space resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
            'SpaceSettings': self.space_settings,
            'SpaceDisplayName': self.space_display_name,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Space._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_space(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        self.client.delete_space(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Space"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Space", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Space", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        domain_id_equals: Optional[str] = Unassigned(),
        space_name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Space"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortOrder': sort_order,
            'SortBy': sort_by,
            'DomainIdEquals': domain_id_equals,
            'SpaceNameContains': space_name_contains,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_spaces',
            summaries_key='Spaces',
            summary_name='SpaceDetails',
            resource_cls=Space,
            list_method_kwargs=operation_input_args
        )


class StudioLifecycleConfig(Base):
    """
    StudioLifecycleConfig 
     Class representing resource StudioLifecycleConfig
    Attributes
    ---------------------
    studio_lifecycle_config_arn:<p>The ARN of the Lifecycle Configuration to describe.</p>
    studio_lifecycle_config_name:<p>The name of the Amazon SageMaker Studio Lifecycle Configuration that is described.</p>
    creation_time:<p>The creation time of the Amazon SageMaker Studio Lifecycle Configuration.</p>
    last_modified_time:<p>This value is equivalent to CreationTime because Amazon SageMaker Studio Lifecycle Configurations are immutable.</p>
    studio_lifecycle_config_content:<p>The content of your Amazon SageMaker Studio Lifecycle Configuration script.</p>
    studio_lifecycle_config_app_type:<p>The App type that the Lifecycle Configuration is attached to.</p>
    
    """
    studio_lifecycle_config_name: str
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_content: Optional[str] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'studio_lifecycle_config_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        studio_lifecycle_config_name: str,
        studio_lifecycle_config_content: str,
        studio_lifecycle_config_app_type: str,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["StudioLifecycleConfig"]:
        logger.debug("Creating studio_lifecycle_config resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
            'StudioLifecycleConfigContent': studio_lifecycle_config_content,
            'StudioLifecycleConfigAppType': studio_lifecycle_config_app_type,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='StudioLifecycleConfig', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_studio_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(studio_lifecycle_config_name=studio_lifecycle_config_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        studio_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["StudioLifecycleConfig"]:
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_studio_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeStudioLifecycleConfigResponse')
        studio_lifecycle_config = cls(**transformed_response)
        return studio_lifecycle_config
    
    def refresh(self) -> Optional["StudioLifecycleConfig"]:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_studio_lifecycle_config(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeStudioLifecycleConfigResponse', self)
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        self.client.delete_studio_lifecycle_config(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        app_type_equals: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        modified_time_before: Optional[datetime.datetime] = Unassigned(),
        modified_time_after: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["StudioLifecycleConfig"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'NameContains': name_contains,
            'AppTypeEquals': app_type_equals,
            'CreationTimeBefore': creation_time_before,
            'CreationTimeAfter': creation_time_after,
            'ModifiedTimeBefore': modified_time_before,
            'ModifiedTimeAfter': modified_time_after,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_studio_lifecycle_configs',
            summaries_key='StudioLifecycleConfigs',
            summary_name='StudioLifecycleConfigDetails',
            resource_cls=StudioLifecycleConfig,
            list_method_kwargs=operation_input_args
        )


class TrainingJob(Base):
    """
    TrainingJob 
     Class representing resource TrainingJob
    Attributes
    ---------------------
    training_job_name:<p> Name of the model training job. </p>
    training_job_arn:<p>The Amazon Resource Name (ARN) of the training job.</p>
    model_artifacts:<p>Information about the Amazon S3 location that is configured for storing model artifacts. </p>
    training_job_status:<p>The status of the training job.</p> <p>SageMaker provides the following training job statuses:</p> <ul> <li> <p> <code>InProgress</code> - The training is in progress.</p> </li> <li> <p> <code>Completed</code> - The training job has completed.</p> </li> <li> <p> <code>Failed</code> - The training job has failed. To see the reason for the failure, see the <code>FailureReason</code> field in the response to a <code>DescribeTrainingJobResponse</code> call.</p> </li> <li> <p> <code>Stopping</code> - The training job is stopping.</p> </li> <li> <p> <code>Stopped</code> - The training job has stopped.</p> </li> </ul> <p>For more detailed information, see <code>SecondaryStatus</code>. </p>
    secondary_status:<p> Provides detailed information about the state of the training job. For detailed information on the secondary status of the training job, see <code>StatusMessage</code> under <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_SecondaryStatusTransition.html">SecondaryStatusTransition</a>.</p> <p>SageMaker provides primary statuses and secondary statuses that apply to each of them:</p> <dl> <dt>InProgress</dt> <dd> <ul> <li> <p> <code>Starting</code> - Starting the training job.</p> </li> <li> <p> <code>Downloading</code> - An optional stage for algorithms that support <code>File</code> training input mode. It indicates that data is being downloaded to the ML storage volumes.</p> </li> <li> <p> <code>Training</code> - Training is in progress.</p> </li> <li> <p> <code>Interrupted</code> - The job stopped because the managed spot training instances were interrupted. </p> </li> <li> <p> <code>Uploading</code> - Training is complete and the model artifacts are being uploaded to the S3 location.</p> </li> </ul> </dd> <dt>Completed</dt> <dd> <ul> <li> <p> <code>Completed</code> - The training job has completed.</p> </li> </ul> </dd> <dt>Failed</dt> <dd> <ul> <li> <p> <code>Failed</code> - The training job has failed. The reason for the failure is returned in the <code>FailureReason</code> field of <code>DescribeTrainingJobResponse</code>.</p> </li> </ul> </dd> <dt>Stopped</dt> <dd> <ul> <li> <p> <code>MaxRuntimeExceeded</code> - The job stopped because it exceeded the maximum allowed runtime.</p> </li> <li> <p> <code>MaxWaitTimeExceeded</code> - The job stopped because it exceeded the maximum allowed wait time.</p> </li> <li> <p> <code>Stopped</code> - The training job has stopped.</p> </li> </ul> </dd> <dt>Stopping</dt> <dd> <ul> <li> <p> <code>Stopping</code> - Stopping the training job.</p> </li> </ul> </dd> </dl> <important> <p>Valid values for <code>SecondaryStatus</code> are subject to change. </p> </important> <p>We no longer support the following secondary statuses:</p> <ul> <li> <p> <code>LaunchingMLInstances</code> </p> </li> <li> <p> <code>PreparingTraining</code> </p> </li> <li> <p> <code>DownloadingTrainingImage</code> </p> </li> </ul>
    algorithm_specification:<p>Information about the algorithm used for training, and algorithm metadata. </p>
    resource_config:<p>Resources, including ML compute instances and ML storage volumes, that are configured for model training. </p>
    stopping_condition:<p>Specifies a limit to how long a model training job can run. It also specifies how long a managed Spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs.</p> <p>To stop a job, SageMaker sends the algorithm the <code>SIGTERM</code> signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts, so the results of training are not lost. </p>
    creation_time:<p>A timestamp that indicates when the training job was created.</p>
    tuning_job_arn:<p>The Amazon Resource Name (ARN) of the associated hyperparameter tuning job if the training job was launched by a hyperparameter tuning job.</p>
    labeling_job_arn:<p>The Amazon Resource Name (ARN) of the SageMaker Ground Truth labeling job that created the transform or training job.</p>
    auto_m_l_job_arn:<p>The Amazon Resource Name (ARN) of an AutoML job.</p>
    failure_reason:<p>If the training job failed, the reason it failed. </p>
    hyper_parameters:<p>Algorithm-specific parameters. </p>
    role_arn:<p>The Amazon Web Services Identity and Access Management (IAM) role configured for the training job. </p>
    input_data_config:<p>An array of <code>Channel</code> objects that describes each data input channel. </p>
    output_data_config:<p>The S3 path where model artifacts that you configured when creating the job are stored. SageMaker creates subfolders for model artifacts. </p>
    warm_pool_status:<p>The status of the warm pool associated with the training job.</p>
    vpc_config:<p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> object that specifies the VPC that this training job has access to. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-vpc.html">Protect Training Jobs by Using an Amazon Virtual Private Cloud</a>.</p>
    training_start_time:<p>Indicates the time when the training job starts on training instances. You are billed for the time interval between this time and the value of <code>TrainingEndTime</code>. The start time in CloudWatch Logs might be later than this time. The difference is due to the time it takes to download the training data and to the size of the training container.</p>
    training_end_time:<p>Indicates the time when the training job ends on training instances. You are billed for the time interval between the value of <code>TrainingStartTime</code> and this time. For successful jobs and stopped jobs, this is the time after model artifacts are uploaded. For failed jobs, this is the time when SageMaker detects a job failure.</p>
    last_modified_time:<p>A timestamp that indicates when the status of the training job was last modified.</p>
    secondary_status_transitions:<p>A history of all of the secondary statuses that the training job has transitioned through.</p>
    final_metric_data_list:<p>A collection of <code>MetricData</code> objects that specify the names, values, and dates and times that the training algorithm emitted to Amazon CloudWatch.</p>
    enable_network_isolation:<p>If you want to allow inbound or outbound network calls, except for calls between peers within a training cluster for distributed training, choose <code>True</code>. If you enable network isolation for training jobs that are configured to use a VPC, SageMaker downloads and uploads customer data and model artifacts through the specified VPC, but the training container does not have network access.</p>
    enable_inter_container_traffic_encryption:<p>To encrypt all communications between ML compute instances in distributed training, choose <code>True</code>. Encryption provides greater security for distributed training, but training might take longer. How long it takes depends on the amount of communication between compute instances, especially if you use a deep learning algorithms in distributed training.</p>
    enable_managed_spot_training:<p>A Boolean indicating whether managed spot training is enabled (<code>True</code>) or not (<code>False</code>).</p>
    checkpoint_config:
    training_time_in_seconds:<p>The training time in seconds.</p>
    billable_time_in_seconds:<p>The billable time in seconds. Billable time refers to the absolute wall-clock time.</p> <p>Multiply <code>BillableTimeInSeconds</code> by the number of instances (<code>InstanceCount</code>) in your training cluster to get the total compute time SageMaker bills you if you run distributed training. The formula is as follows: <code>BillableTimeInSeconds * InstanceCount</code> .</p> <p>You can calculate the savings from using managed spot training using the formula <code>(1 - BillableTimeInSeconds / TrainingTimeInSeconds) * 100</code>. For example, if <code>BillableTimeInSeconds</code> is 100 and <code>TrainingTimeInSeconds</code> is 500, the savings is 80%.</p>
    debug_hook_config:
    experiment_config:
    debug_rule_configurations:<p>Configuration information for Amazon SageMaker Debugger rules for debugging output tensors.</p>
    tensor_board_output_config:
    debug_rule_evaluation_statuses:<p>Evaluation status of Amazon SageMaker Debugger rules for debugging on a training job.</p>
    profiler_config:
    profiler_rule_configurations:<p>Configuration information for Amazon SageMaker Debugger rules for profiling system and framework metrics.</p>
    profiler_rule_evaluation_statuses:<p>Evaluation status of Amazon SageMaker Debugger rules for profiling on a training job.</p>
    profiling_status:<p>Profiling status of a training job.</p>
    environment:<p>The environment variables to set in the Docker container.</p>
    retry_strategy:<p>The number of times to retry the job when the job fails due to an <code>InternalServerError</code>.</p>
    remote_debug_config:<p>Configuration for remote debugging. To learn more about the remote debugging functionality of SageMaker, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-remote-debugging.html">Access a training container through Amazon Web Services Systems Manager (SSM) for remote debugging</a>.</p>
    infra_check_config:<p>Contains information about the infrastructure health check configuration for the training job.</p>
    
    """
    training_job_name: str
    training_job_arn: Optional[str] = Unassigned()
    tuning_job_arn: Optional[str] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    model_artifacts: Optional[ModelArtifacts] = Unassigned()
    training_job_status: Optional[str] = Unassigned()
    secondary_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    hyper_parameters: Optional[Dict[str, str]] = Unassigned()
    algorithm_specification: Optional[AlgorithmSpecification] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    input_data_config: Optional[List[Channel]] = Unassigned()
    output_data_config: Optional[OutputDataConfig] = Unassigned()
    resource_config: Optional[ResourceConfig] = Unassigned()
    warm_pool_status: Optional[WarmPoolStatus] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    stopping_condition: Optional[StoppingCondition] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    secondary_status_transitions: Optional[List[SecondaryStatusTransition]] = Unassigned()
    final_metric_data_list: Optional[List[MetricData]] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_managed_spot_training: Optional[bool] = Unassigned()
    checkpoint_config: Optional[CheckpointConfig] = Unassigned()
    training_time_in_seconds: Optional[int] = Unassigned()
    billable_time_in_seconds: Optional[int] = Unassigned()
    debug_hook_config: Optional[DebugHookConfig] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    debug_rule_configurations: Optional[List[DebugRuleConfiguration]] = Unassigned()
    tensor_board_output_config: Optional[TensorBoardOutputConfig] = Unassigned()
    debug_rule_evaluation_statuses: Optional[List[DebugRuleEvaluationStatus]] = Unassigned()
    profiler_config: Optional[ProfilerConfig] = Unassigned()
    profiler_rule_configurations: Optional[List[ProfilerRuleConfiguration]] = Unassigned()
    profiler_rule_evaluation_statuses: Optional[List[ProfilerRuleEvaluationStatus]] = Unassigned()
    profiling_status: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    remote_debug_config: Optional[RemoteDebugConfig] = Unassigned()
    infra_check_config: Optional[InfraCheckConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'training_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "model_artifacts": {
            "s3_model_artifacts": {
              "type": "string"
            }
          },
          "resource_config": {
            "volume_kms_key_id": {
              "type": "string"
            }
          },
          "role_arn": {
            "type": "string"
          },
          "output_data_config": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "vpc_config": {
            "security_group_ids": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "subnets": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "checkpoint_config": {
            "s3_uri": {
              "type": "string"
            }
          },
          "debug_hook_config": {
            "s3_output_path": {
              "type": "string"
            }
          },
          "tensor_board_output_config": {
            "s3_output_path": {
              "type": "string"
            }
          },
          "profiler_config": {
            "s3_output_path": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "TrainingJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        training_job_name: str,
        algorithm_specification: AlgorithmSpecification,
        role_arn: str,
        output_data_config: OutputDataConfig,
        resource_config: ResourceConfig,
        stopping_condition: StoppingCondition,
        hyper_parameters: Optional[Dict[str, str]] = Unassigned(),
        input_data_config: Optional[List[Channel]] = Unassigned(),
        vpc_config: Optional[VpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        enable_network_isolation: Optional[bool] = Unassigned(),
        enable_inter_container_traffic_encryption: Optional[bool] = Unassigned(),
        enable_managed_spot_training: Optional[bool] = Unassigned(),
        checkpoint_config: Optional[CheckpointConfig] = Unassigned(),
        debug_hook_config: Optional[DebugHookConfig] = Unassigned(),
        debug_rule_configurations: Optional[List[DebugRuleConfiguration]] = Unassigned(),
        tensor_board_output_config: Optional[TensorBoardOutputConfig] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        profiler_config: Optional[ProfilerConfig] = Unassigned(),
        profiler_rule_configurations: Optional[List[ProfilerRuleConfiguration]] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        retry_strategy: Optional[RetryStrategy] = Unassigned(),
        remote_debug_config: Optional[RemoteDebugConfig] = Unassigned(),
        infra_check_config: Optional[InfraCheckConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TrainingJob"]:
        logger.debug("Creating training_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'TrainingJobName': training_job_name,
            'HyperParameters': hyper_parameters,
            'AlgorithmSpecification': algorithm_specification,
            'RoleArn': role_arn,
            'InputDataConfig': input_data_config,
            'OutputDataConfig': output_data_config,
            'ResourceConfig': resource_config,
            'VpcConfig': vpc_config,
            'StoppingCondition': stopping_condition,
            'Tags': tags,
            'EnableNetworkIsolation': enable_network_isolation,
            'EnableInterContainerTrafficEncryption': enable_inter_container_traffic_encryption,
            'EnableManagedSpotTraining': enable_managed_spot_training,
            'CheckpointConfig': checkpoint_config,
            'DebugHookConfig': debug_hook_config,
            'DebugRuleConfigurations': debug_rule_configurations,
            'TensorBoardOutputConfig': tensor_board_output_config,
            'ExperimentConfig': experiment_config,
            'ProfilerConfig': profiler_config,
            'ProfilerRuleConfigurations': profiler_rule_configurations,
            'Environment': environment,
            'RetryStrategy': retry_strategy,
            'RemoteDebugConfig': remote_debug_config,
            'InfraCheckConfig': infra_check_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='TrainingJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_training_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(training_job_name=training_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        training_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TrainingJob"]:
        operation_input_args = {
            'TrainingJobName': training_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_training_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrainingJobResponse')
        training_job = cls(**transformed_response)
        return training_job
    
    def refresh(self) -> Optional["TrainingJob"]:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_training_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrainingJobResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["TrainingJob"]:
        logger.debug("Creating training_job resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
            'ProfilerConfig': self.profiler_config,
            'ProfilerRuleConfigurations': self.profiler_rule_configurations,
            'ResourceConfig': self.resource_config,
            'RemoteDebugConfig': self.remote_debug_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = TrainingJob._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_training_job(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        self.client.stop_training_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["TrainingJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.training_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="TrainingJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="TrainingJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        warm_pool_status_equals: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["TrainingJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'WarmPoolStatusEquals': warm_pool_status_equals,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_training_jobs',
            summaries_key='TrainingJobSummaries',
            summary_name='TrainingJobSummary',
            resource_cls=TrainingJob,
            list_method_kwargs=operation_input_args
        )


class TransformJob(Base):
    """
    TransformJob 
     Class representing resource TransformJob
    Attributes
    ---------------------
    transform_job_name:<p>The name of the transform job.</p>
    transform_job_arn:<p>The Amazon Resource Name (ARN) of the transform job.</p>
    transform_job_status:<p>The status of the transform job. If the transform job failed, the reason is returned in the <code>FailureReason</code> field.</p>
    model_name:<p>The name of the model used in the transform job.</p>
    transform_input:<p>Describes the dataset to be transformed and the Amazon S3 location where it is stored.</p>
    transform_resources:<p>Describes the resources, including ML instance types and ML instance count, to use for the transform job.</p>
    creation_time:<p>A timestamp that shows when the transform Job was created.</p>
    failure_reason:<p>If the transform job failed, <code>FailureReason</code> describes why it failed. A transform job creates a log file, which includes error messages, and stores it as an Amazon S3 object. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/logging-cloudwatch.html">Log Amazon SageMaker Events with Amazon CloudWatch</a>.</p>
    max_concurrent_transforms:<p>The maximum number of parallel requests on each instance node that can be launched in a transform job. The default value is 1.</p>
    model_client_config:<p>The timeout and maximum number of retries for processing a transform job invocation.</p>
    max_payload_in_m_b:<p>The maximum payload size, in MB, used in the transform job.</p>
    batch_strategy:<p>Specifies the number of records to include in a mini-batch for an HTTP inference request. A <i>record</i> <i/> is a single unit of input data that inference can be made on. For example, a single line in a CSV file is a record. </p> <p>To enable the batch strategy, you must set <code>SplitType</code> to <code>Line</code>, <code>RecordIO</code>, or <code>TFRecord</code>.</p>
    environment:<p>The environment variables to set in the Docker container. We support up to 16 key and values entries in the map.</p>
    transform_output:<p>Identifies the Amazon S3 location where you want Amazon SageMaker to save the results from the transform job.</p>
    data_capture_config:<p>Configuration to control how SageMaker captures inference data.</p>
    transform_start_time:<p>Indicates when the transform job starts on ML instances. You are billed for the time interval between this time and the value of <code>TransformEndTime</code>.</p>
    transform_end_time:<p>Indicates when the transform job has been completed, or has stopped or failed. You are billed for the time interval between this time and the value of <code>TransformStartTime</code>.</p>
    labeling_job_arn:<p>The Amazon Resource Name (ARN) of the Amazon SageMaker Ground Truth labeling job that created the transform or training job.</p>
    auto_m_l_job_arn:<p>The Amazon Resource Name (ARN) of the AutoML transform job.</p>
    data_processing:
    experiment_config:
    
    """
    transform_job_name: str
    transform_job_arn: Optional[str] = Unassigned()
    transform_job_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    max_concurrent_transforms: Optional[int] = Unassigned()
    model_client_config: Optional[ModelClientConfig] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    transform_input: Optional[TransformInput] = Unassigned()
    transform_output: Optional[TransformOutput] = Unassigned()
    data_capture_config: Optional[BatchDataCaptureConfig] = Unassigned()
    transform_resources: Optional[TransformResources] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    transform_start_time: Optional[datetime.datetime] = Unassigned()
    transform_end_time: Optional[datetime.datetime] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    data_processing: Optional[DataProcessing] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'transform_job_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "transform_input": {
            "data_source": {
              "s3_data_source": {
                "s3_data_type": {
                  "type": "string"
                },
                "s3_uri": {
                  "type": "string"
                }
              }
            }
          },
          "transform_resources": {
            "volume_kms_key_id": {
              "type": "string"
            }
          },
          "transform_output": {
            "s3_output_path": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          },
          "data_capture_config": {
            "destination_s3_uri": {
              "type": "string"
            },
            "kms_key_id": {
              "type": "string"
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "TransformJob", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        transform_job_name: str,
        model_name: Union[str, object],
        transform_input: TransformInput,
        transform_output: TransformOutput,
        transform_resources: TransformResources,
        max_concurrent_transforms: Optional[int] = Unassigned(),
        model_client_config: Optional[ModelClientConfig] = Unassigned(),
        max_payload_in_m_b: Optional[int] = Unassigned(),
        batch_strategy: Optional[str] = Unassigned(),
        environment: Optional[Dict[str, str]] = Unassigned(),
        data_capture_config: Optional[BatchDataCaptureConfig] = Unassigned(),
        data_processing: Optional[DataProcessing] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        experiment_config: Optional[ExperimentConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TransformJob"]:
        logger.debug("Creating transform_job resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'TransformJobName': transform_job_name,
            'ModelName': model_name,
            'MaxConcurrentTransforms': max_concurrent_transforms,
            'ModelClientConfig': model_client_config,
            'MaxPayloadInMB': max_payload_in_m_b,
            'BatchStrategy': batch_strategy,
            'Environment': environment,
            'TransformInput': transform_input,
            'TransformOutput': transform_output,
            'DataCaptureConfig': data_capture_config,
            'TransformResources': transform_resources,
            'DataProcessing': data_processing,
            'Tags': tags,
            'ExperimentConfig': experiment_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='TransformJob', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_transform_job(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(transform_job_name=transform_job_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        transform_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TransformJob"]:
        operation_input_args = {
            'TransformJobName': transform_job_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_transform_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTransformJobResponse')
        transform_job = cls(**transformed_response)
        return transform_job
    
    def refresh(self) -> Optional["TransformJob"]:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_transform_job(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTransformJobResponse', self)
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        self.client.stop_transform_job(**operation_input_args)
    
    def wait(
        self,
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["TransformJob"]:
        terminal_states = ['Completed', 'Failed', 'Stopped']
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.transform_job_status
    
            if current_status in terminal_states:
                
                if "failed" in current_status.lower():
                    raise FailedStatusError(resource_type="TransformJob", status=current_status, reason=self.failure_reason)
    
                return self
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="TransformJob", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["TransformJob"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'CreationTimeAfter': creation_time_after,
            'CreationTimeBefore': creation_time_before,
            'LastModifiedTimeAfter': last_modified_time_after,
            'LastModifiedTimeBefore': last_modified_time_before,
            'NameContains': name_contains,
            'StatusEquals': status_equals,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_transform_jobs',
            summaries_key='TransformJobSummaries',
            summary_name='TransformJobSummary',
            resource_cls=TransformJob,
            list_method_kwargs=operation_input_args
        )


class Trial(Base):
    """
    Trial 
     Class representing resource Trial
    Attributes
    ---------------------
    trial_name:<p>The name of the trial.</p>
    trial_arn:<p>The Amazon Resource Name (ARN) of the trial.</p>
    display_name:<p>The name of the trial as displayed. If <code>DisplayName</code> isn't specified, <code>TrialName</code> is displayed.</p>
    experiment_name:<p>The name of the experiment the trial is part of.</p>
    source:<p>The Amazon Resource Name (ARN) of the source and, optionally, the job type.</p>
    creation_time:<p>When the trial was created.</p>
    created_by:<p>Who created the trial.</p>
    last_modified_time:<p>When the trial was last modified.</p>
    last_modified_by:<p>Who last modified the trial.</p>
    metadata_properties:
    
    """
    trial_name: str
    trial_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    source: Optional[TrialSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'trial_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        trial_name: str,
        experiment_name: Union[str, object],
        display_name: Optional[str] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Trial"]:
        logger.debug("Creating trial resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'TrialName': trial_name,
            'DisplayName': display_name,
            'ExperimentName': experiment_name,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Trial', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_trial(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(trial_name=trial_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Trial"]:
        operation_input_args = {
            'TrialName': trial_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_trial(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrialResponse')
        trial = cls(**transformed_response)
        return trial
    
    def refresh(self) -> Optional["Trial"]:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrialResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["Trial"]:
        logger.debug("Creating trial resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'TrialName': self.trial_name,
            'DisplayName': self.display_name,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Trial._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_trial(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        self.client.delete_trial(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        experiment_name: Optional[str] = Unassigned(),
        trial_component_name: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Trial"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'ExperimentName': experiment_name,
            'TrialComponentName': trial_component_name,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_trials',
            summaries_key='TrialSummaries',
            summary_name='TrialSummary',
            resource_cls=Trial,
            list_method_kwargs=operation_input_args
        )


class TrialComponent(Base):
    """
    TrialComponent 
     Class representing resource TrialComponent
    Attributes
    ---------------------
    trial_component_name:<p>The name of the trial component.</p>
    trial_component_arn:<p>The Amazon Resource Name (ARN) of the trial component.</p>
    display_name:<p>The name of the component as displayed. If <code>DisplayName</code> isn't specified, <code>TrialComponentName</code> is displayed.</p>
    source:<p>The Amazon Resource Name (ARN) of the source and, optionally, the job type.</p>
    status:<p>The status of the component. States include:</p> <ul> <li> <p>InProgress</p> </li> <li> <p>Completed</p> </li> <li> <p>Failed</p> </li> </ul>
    start_time:<p>When the component started.</p>
    end_time:<p>When the component ended.</p>
    creation_time:<p>When the component was created.</p>
    created_by:<p>Who created the trial component.</p>
    last_modified_time:<p>When the component was last modified.</p>
    last_modified_by:<p>Who last modified the component.</p>
    parameters:<p>The hyperparameters of the component.</p>
    input_artifacts:<p>The input artifacts of the component.</p>
    output_artifacts:<p>The output artifacts of the component.</p>
    metadata_properties:
    metrics:<p>The metrics for the component.</p>
    lineage_group_arn:<p>The Amazon Resource Name (ARN) of the lineage group.</p>
    sources:<p>A list of ARNs and, if applicable, job types for multiple sources of an experiment run.</p>
    
    """
    trial_component_name: str
    trial_component_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[TrialComponentSource] = Unassigned()
    status: Optional[TrialComponentStatus] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned()
    input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    metrics: Optional[List[TrialComponentMetricSummary]] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    sources: Optional[List[TrialComponentSource]] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'trial_component_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        trial_component_name: str,
        display_name: Optional[str] = Unassigned(),
        status: Optional[TrialComponentStatus] = Unassigned(),
        start_time: Optional[datetime.datetime] = Unassigned(),
        end_time: Optional[datetime.datetime] = Unassigned(),
        parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned(),
        input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TrialComponent"]:
        logger.debug("Creating trial_component resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'TrialComponentName': trial_component_name,
            'DisplayName': display_name,
            'Status': status,
            'StartTime': start_time,
            'EndTime': end_time,
            'Parameters': parameters,
            'InputArtifacts': input_artifacts,
            'OutputArtifacts': output_artifacts,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='TrialComponent', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_trial_component(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(trial_component_name=trial_component_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        trial_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["TrialComponent"]:
        operation_input_args = {
            'TrialComponentName': trial_component_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_trial_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeTrialComponentResponse')
        trial_component = cls(**transformed_response)
        return trial_component
    
    def refresh(self) -> Optional["TrialComponent"]:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial_component(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeTrialComponentResponse', self)
        return self
    
    def update(
        self,
        parameters_to_remove: Optional[List[str]] = Unassigned(),
        input_artifacts_to_remove: Optional[List[str]] = Unassigned(),
        output_artifacts_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["TrialComponent"]:
        logger.debug("Creating trial_component resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
            'DisplayName': self.display_name,
            'Status': self.status,
            'StartTime': self.start_time,
            'EndTime': self.end_time,
            'Parameters': self.parameters,
            'ParametersToRemove': parameters_to_remove,
            'InputArtifacts': self.input_artifacts,
            'InputArtifactsToRemove': input_artifacts_to_remove,
            'OutputArtifacts': self.output_artifacts,
            'OutputArtifactsToRemove': output_artifacts_to_remove,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = TrialComponent._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_trial_component(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        self.client.delete_trial_component(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['InProgress', 'Completed', 'Failed', 'Stopping', 'Stopped'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["TrialComponent"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status.primary_status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="TrialComponent", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="TrialComponent", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        experiment_name: Optional[str] = Unassigned(),
        trial_name: Optional[str] = Unassigned(),
        source_arn: Optional[str] = Unassigned(),
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["TrialComponent"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'ExperimentName': experiment_name,
            'TrialName': trial_name,
            'SourceArn': source_arn,
            'CreatedAfter': created_after,
            'CreatedBefore': created_before,
            'SortBy': sort_by,
            'SortOrder': sort_order,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_trial_components',
            summaries_key='TrialComponentSummaries',
            summary_name='TrialComponentSummary',
            resource_cls=TrialComponent,
            list_method_kwargs=operation_input_args
        )


class UserProfile(Base):
    """
    UserProfile 
     Class representing resource UserProfile
    Attributes
    ---------------------
    domain_id:<p>The ID of the domain that contains the profile.</p>
    user_profile_arn:<p>The user profile Amazon Resource Name (ARN).</p>
    user_profile_name:<p>The user profile name.</p>
    home_efs_file_system_uid:<p>The ID of the user's profile in the Amazon Elastic File System volume.</p>
    status:<p>The status.</p>
    last_modified_time:<p>The last modified time.</p>
    creation_time:<p>The creation time.</p>
    failure_reason:<p>The failure reason.</p>
    single_sign_on_user_identifier:<p>The IAM Identity Center user identifier.</p>
    single_sign_on_user_value:<p>The IAM Identity Center user value.</p>
    user_settings:<p>A collection of settings.</p>
    
    """
    domain_id: str
    user_profile_name: str
    user_profile_arn: Optional[str] = Unassigned()
    home_efs_file_system_uid: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    single_sign_on_user_identifier: Optional[str] = Unassigned()
    single_sign_on_user_value: Optional[str] = Unassigned()
    user_settings: Optional[UserSettings] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'user_profile_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "user_settings": {
            "execution_role": {
              "type": "string"
            },
            "security_groups": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "sharing_settings": {
              "s3_output_path": {
                "type": "string"
              },
              "s3_kms_key_id": {
                "type": "string"
              }
            },
            "canvas_app_settings": {
              "time_series_forecasting_settings": {
                "amazon_forecast_role_arn": {
                  "type": "string"
                }
              },
              "model_register_settings": {
                "cross_account_model_register_role_arn": {
                  "type": "string"
                }
              },
              "workspace_settings": {
                "s3_artifact_path": {
                  "type": "string"
                },
                "s3_kms_key_id": {
                  "type": "string"
                }
              },
              "generative_ai_settings": {
                "amazon_bedrock_role_arn": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "UserProfile", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        domain_id: str,
        user_profile_name: str,
        single_sign_on_user_identifier: Optional[str] = Unassigned(),
        single_sign_on_user_value: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        user_settings: Optional[UserSettings] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["UserProfile"]:
        logger.debug("Creating user_profile resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SingleSignOnUserIdentifier': single_sign_on_user_identifier,
            'SingleSignOnUserValue': single_sign_on_user_value,
            'Tags': tags,
            'UserSettings': user_settings,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='UserProfile', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_user_profile(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(domain_id=domain_id, user_profile_name=user_profile_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        user_profile_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["UserProfile"]:
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_user_profile(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeUserProfileResponse')
        user_profile = cls(**transformed_response)
        return user_profile
    
    def refresh(self) -> Optional["UserProfile"]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        client = SageMakerClient().client
        response = client.describe_user_profile(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeUserProfileResponse', self)
        return self
    
    def update(
        self,
    
    ) -> Optional["UserProfile"]:
        logger.debug("Creating user_profile resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
            'UserSettings': self.user_settings,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = UserProfile._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_user_profile(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        self.client.delete_user_profile(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Deleting', 'Failed', 'InService', 'Pending', 'Updating', 'Update_Failed', 'Delete_Failed'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["UserProfile"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="UserProfile", status=current_status, reason=self.failure_reason)
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="UserProfile", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        domain_id_equals: Optional[str] = Unassigned(),
        user_profile_name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["UserProfile"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortOrder': sort_order,
            'SortBy': sort_by,
            'DomainIdEquals': domain_id_equals,
            'UserProfileNameContains': user_profile_name_contains,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_user_profiles',
            summaries_key='UserProfiles',
            summary_name='UserProfileDetails',
            resource_cls=UserProfile,
            list_method_kwargs=operation_input_args
        )


class Workforce(Base):
    """
    Workforce 
     Class representing resource Workforce
    Attributes
    ---------------------
    workforce:<p>A single private workforce, which is automatically created when you create your first private work team. You can create one private work force in each Amazon Web Services Region. By default, any workforce-related API operation used in a specific region will apply to the workforce created in that region. To learn how to create a private workforce, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-create-private.html">Create a Private Workforce</a>.</p>
    
    """
    workforce: Optional[Workforce] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'workforce_name':
                return value
        raise Exception("Name attribute not found for object")

    
    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = \
        {
          "workforce": {
            "workforce_vpc_config": {
              "security_group_ids": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              },
              "subnets": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
            return create_func(*args, **Base.get_updated_kwargs_with_configured_attributes(config_schema_for_resource, "Workforce", **kwargs))
        return wrapper
    
    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        workforce_name: str,
        cognito_config: Optional[CognitoConfig] = Unassigned(),
        oidc_config: Optional[OidcConfig] = Unassigned(),
        source_ip_config: Optional[SourceIpConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        workforce_vpc_config: Optional[WorkforceVpcConfigRequest] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Workforce"]:
        logger.debug("Creating workforce resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'CognitoConfig': cognito_config,
            'OidcConfig': oidc_config,
            'SourceIpConfig': source_ip_config,
            'WorkforceName': workforce_name,
            'Tags': tags,
            'WorkforceVpcConfig': workforce_vpc_config,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Workforce', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_workforce(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(workforce_name=workforce_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        workforce_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Workforce"]:
        operation_input_args = {
            'WorkforceName': workforce_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_workforce(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeWorkforceResponse')
        workforce = cls(**transformed_response)
        return workforce
    
    def refresh(self) -> Optional["Workforce"]:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        client = SageMakerClient().client
        response = client.describe_workforce(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeWorkforceResponse', self)
        return self
    
    def update(
        self,
        workforce_name: str,
        source_ip_config: Optional[SourceIpConfig] = Unassigned(),
        oidc_config: Optional[OidcConfig] = Unassigned(),
        workforce_vpc_config: Optional[WorkforceVpcConfigRequest] = Unassigned(),
    ) -> Optional["Workforce"]:
        logger.debug("Creating workforce resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'WorkforceName': workforce_name,
            'SourceIpConfig': source_ip_config,
            'OidcConfig': oidc_config,
            'WorkforceVpcConfig': workforce_vpc_config,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Workforce._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_workforce(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        self.client.delete_workforce(**operation_input_args)
    
    def wait_for_status(
        self,
        status: Literal['Initializing', 'Updating', 'Deleting', 'Failed', 'Active'],
        poll: int = 5,
        timeout: Optional[int] = None
    ) -> Optional["Workforce"]:
        start_time = time.time()
    
        while True:
            self.refresh()
            current_status = self.workforce.status
    
            if status == current_status:
                return self
            
            if "failed" in current_status.lower():
                raise FailedStatusError(resource_type="Workforce", status=current_status, reason='(Unknown)')
    
            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Workforce", status=current_status)
            print("-", end="")
            time.sleep(poll)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Workforce"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_workforces',
            summaries_key='Workforces',
            summary_name='Workforce',
            resource_cls=Workforce,
            list_method_kwargs=operation_input_args
        )


class Workteam(Base):
    """
    Workteam 
     Class representing resource Workteam
    Attributes
    ---------------------
    workteam:<p>A <code>Workteam</code> instance that contains information about the work team. </p>
    
    """
    workteam: Optional[Workteam] = Unassigned()
    
    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == 'name' or attribute == 'workteam_name':
                return value
        raise Exception("Name attribute not found for object")
    
    @classmethod
    def create(
        cls,
        workteam_name: str,
        member_definitions: List[MemberDefinition],
        description: str,
        workforce_name: Optional[Union[str, object]] = Unassigned(),
        notification_configuration: Optional[NotificationConfiguration] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Workteam"]:
        logger.debug("Creating workteam resource.")
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
    
        operation_input_args = {
            'WorkteamName': workteam_name,
            'WorkforceName': workforce_name,
            'MemberDefinitions': member_definitions,
            'Description': description,
            'NotificationConfiguration': notification_configuration,
            'Tags': tags,
        }
        
        operation_input_args = Base.populate_chained_attributes(resource_name='Workteam', operation_input_args=operation_input_args)
            
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.create_workteam(**operation_input_args)
        logger.debug(f"Response: {response}")
    
        return cls.get(workteam_name=workteam_name, session=session, region=region)
    
    @classmethod
    def get(
        cls,
        workteam_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Workteam"]:
        operation_input_args = {
            'WorkteamName': workteam_name,
        }
        client = SageMakerClient(session=session, region_name=region, service_name='sagemaker').client
        response = client.describe_workteam(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transformed_response = transform(response, 'DescribeWorkteamResponse')
        workteam = cls(**transformed_response)
        return workteam
    
    def refresh(self) -> Optional["Workteam"]:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        client = SageMakerClient().client
        response = client.describe_workteam(**operation_input_args)
    
        # deserialize response and update self
        transform(response, 'DescribeWorkteamResponse', self)
        return self
    
    def update(
        self,
        workteam_name: str,
        member_definitions: Optional[List[MemberDefinition]] = Unassigned(),
        description: Optional[str] = Unassigned(),
        notification_configuration: Optional[NotificationConfiguration] = Unassigned(),
    ) -> Optional["Workteam"]:
        logger.debug("Creating workteam resource.")
        client = SageMakerClient().client
    
        operation_input_args = {
            'WorkteamName': workteam_name,
            'MemberDefinitions': member_definitions,
            'Description': description,
            'NotificationConfiguration': notification_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Workteam._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")
    
        # create the resource
        response = client.update_workteam(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()
    
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        self.client.delete_workteam(**operation_input_args)
    
    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Workteam"]:
        client = SageMakerClient(session=session, region_name=region, service_name="sagemaker").client
            
        operation_input_args = {
            'SortBy': sort_by,
            'SortOrder': sort_order,
            'NameContains': name_contains,
        }
    
        operation_input_args = {k: v for k, v in operation_input_args.items() if v is not None and not isinstance(v, Unassigned)}
        
        return ResourceIterator(
            client=client,
            list_method='list_workteams',
            summaries_key='Workteams',
            summary_name='Workteam',
            resource_cls=Workteam,
            list_method_kwargs=operation_input_args
        )


