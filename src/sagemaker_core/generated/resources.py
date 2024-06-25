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
from sagemaker_core.code_injection.codec import transform
from sagemaker_core.generated.utils import (
    SageMakerClient,
    SageMakerRuntimeClient,
    ResourceIterator,
    Unassigned,
    snake_to_pascal,
    pascal_to_snake,
    is_not_primitive,
    is_not_str_dict,
)
from sagemaker_core.generated.intelligent_defaults_helper import (
    load_default_configs_for_resource_name,
    get_config_value,
)
from sagemaker_core.generated.shapes import *
from sagemaker_core.generated.exceptions import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), validate_assignment=True)

    @classmethod
    def _serialize(cls, value: any) -> any:
        if isinstance(value, Unassigned):
            return None
        elif isinstance(value, List):
            return cls._serialize_list(value)
        elif isinstance(value, Dict):
            return cls._serialize_dict(value)
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
    def _serialize_dict(cls, value: Dict):
        serialized_dict = {}
        for k, v in value.items():
            if serialize_result := cls._serialize(v):
                serialized_dict.update({k: serialize_result})
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
                    formatted_attribute = pascal_to_snake(configurable_attribute)
                    if config_value := get_config_value(
                        formatted_attribute, resource_defaults, global_defaults
                    ):
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
            if (
                arg_snake.endswith("name")
                and arg_snake[: -len("_name")] != resource_name_in_snake_case
                and arg_snake != "name"
            ):
                if value and value != Unassigned() and type(value) != str:
                    updated_args[arg] = value.get_name()
            elif isinstance(value, list):
                updated_args[arg] = [
                    Base.populate_chained_attributes(
                        resource_name=type(list_item).__name__,
                        operation_input_args={
                            snake_to_pascal(k): v for k, v in Base._get_items(list_item)
                        },
                    )
                    for list_item in value
                ]
            elif is_not_primitive(value) and is_not_str_dict(value):
                obj_dict = {snake_to_pascal(k): v for k, v in Base._get_items(value)}
                updated_args[arg] = Base.populate_chained_attributes(
                    resource_name=type(value).__name__, operation_input_args=obj_dict
                )
        return updated_args

    @staticmethod
    def _get_items(object):
        return object.items() if type(object) == dict else object.__dict__.items()


class Action(Base):
    """
    Class representing resource Action

    Attributes:
        action_name:The name of the action.
        action_arn:The Amazon Resource Name (ARN) of the action.
        source:The source of the action.
        action_type:The type of the action.
        description:The description of the action.
        status:The status of the action.
        properties:A list of the action's properties.
        creation_time:When the action was created.
        created_by:
        last_modified_time:When the action was last modified.
        last_modified_by:
        metadata_properties:
        lineage_group_arn:The Amazon Resource Name (ARN) of the lineage group.

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
            if attribute == "name" or attribute == "action_name":
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
        """
        Create a Action resource

        Parameters:
            action_name:The name of the action. Must be unique to your account in an Amazon Web Services Region.
            source:The source type, ID, and URI.
            action_type:The action type.
            description:The description of the action.
            status:The status of the action.
            properties:A list of properties to add to the action.
            metadata_properties:
            tags:A list of tags to apply to the action.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Action resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating action resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ActionName": action_name,
            "Source": source,
            "ActionType": action_type,
            "Description": description,
            "Status": status,
            "Properties": properties,
            "MetadataProperties": metadata_properties,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Action", operation_input_args=operation_input_args
        )

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
        """
        Get a Action resource

        Parameters:
            action_name:The name of the action to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Action resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "ActionName": action_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_action(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeActionResponse")
        action = cls(**transformed_response)
        return action

    def refresh(self) -> Optional["Action"]:
        """
        Refresh a Action resource

        Returns:
            The Action resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "ActionName": self.action_name,
        }
        client = SageMakerClient().client
        response = client.describe_action(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeActionResponse", self)
        return self

    def update(
        self,
        description: Optional[str] = Unassigned(),
        status: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Action"]:
        """
        Update a Action resource

        Parameters:
            properties_to_remove:A list of properties to remove.

        Returns:
            The Action resource.

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
            ConflictException: There was a conflict when you attempted to modify a SageMaker entity such as an Experiment or Artifact.
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating action resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ActionName": self.action_name,
            "Description": description,
            "Status": status,
            "Properties": properties,
            "PropertiesToRemove": properties_to_remove,
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
        """
        Delete a Action resource


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
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient().client

        operation_input_args = {
            "ActionName": self.action_name,
        }
        client.delete_action(**operation_input_args)

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
        """
        Get all Action resources

        Parameters:
            source_uri:A filter that returns only actions with the specified source URI.
            action_type:A filter that returns only actions of the specified type.
            created_after:A filter that returns only actions created on or after the specified time.
            created_before:A filter that returns only actions created on or before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            next_token:If the previous call to ListActions didn't return the full set of actions, the call returns a token for getting the next set of actions.
            max_results:The maximum number of actions to return in the response. The default value is 10.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Action resources.

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
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "SourceUri": source_uri,
            "ActionType": action_type,
            "CreatedAfter": created_after,
            "CreatedBefore": created_before,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_actions",
            summaries_key="ActionSummaries",
            summary_name="ActionSummary",
            resource_cls=Action,
            list_method_kwargs=operation_input_args,
        )


class Algorithm(Base):
    """
    Class representing resource Algorithm

    Attributes:
        algorithm_name:The name of the algorithm being described.
        algorithm_arn:The Amazon Resource Name (ARN) of the algorithm.
        creation_time:A timestamp specifying when the algorithm was created.
        training_specification:Details about training jobs run by this algorithm.
        algorithm_status:The current status of the algorithm.
        algorithm_status_details:Details about the current status of the algorithm.
        algorithm_description:A brief summary about the algorithm.
        inference_specification:Details about inference jobs that the algorithm runs.
        validation_specification:Details about configurations for one or more training jobs that SageMaker runs to test the algorithm.
        product_id:The product identifier of the algorithm.
        certify_for_marketplace:Whether the algorithm is certified to be listed in Amazon Web Services Marketplace.

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
            if attribute == "name" or attribute == "algorithm_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "training_specification": {
                    "additional_s3_data_source": {
                        "s3_data_type": {"type": "string"},
                        "s3_uri": {"type": "string"},
                    }
                },
                "validation_specification": {"validation_role": {"type": "string"}},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Algorithm", **kwargs
                ),
            )

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
        """
        Create a Algorithm resource

        Parameters:
            algorithm_name:The name of the algorithm.
            training_specification:Specifies details about training jobs run by this algorithm, including the following:   The Amazon ECR path of the container and the version digest of the algorithm.   The hyperparameters that the algorithm supports.   The instance types that the algorithm supports for training.   Whether the algorithm supports distributed training.   The metrics that the algorithm emits to Amazon CloudWatch.   Which metrics that the algorithm emits can be used as the objective metric for hyperparameter tuning jobs.   The input channels that the algorithm supports for training data. For example, an algorithm might support train, validation, and test channels.
            algorithm_description:A description of the algorithm.
            inference_specification:Specifies details about inference jobs that the algorithm runs, including the following:   The Amazon ECR paths of containers that contain the inference code and model artifacts.   The instance types that the algorithm supports for transform jobs and real-time endpoints used for inference.   The input and output content formats that the algorithm supports for inference.
            validation_specification:Specifies configurations for one or more training jobs and that SageMaker runs to test the algorithm's training code and, optionally, one or more batch transform jobs that SageMaker runs to test the algorithm's inference code.
            certify_for_marketplace:Whether to certify the algorithm so that it can be listed in Amazon Web Services Marketplace.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Algorithm resource.

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
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating algorithm resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "AlgorithmName": algorithm_name,
            "AlgorithmDescription": algorithm_description,
            "TrainingSpecification": training_specification,
            "InferenceSpecification": inference_specification,
            "ValidationSpecification": validation_specification,
            "CertifyForMarketplace": certify_for_marketplace,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Algorithm", operation_input_args=operation_input_args
        )

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
        """
        Get a Algorithm resource

        Parameters:
            algorithm_name:The name of the algorithm to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Algorithm resource.

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
        """

        operation_input_args = {
            "AlgorithmName": algorithm_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_algorithm(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeAlgorithmOutput")
        algorithm = cls(**transformed_response)
        return algorithm

    def refresh(self) -> Optional["Algorithm"]:
        """
        Refresh a Algorithm resource

        Returns:
            The Algorithm resource.

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
        """

        operation_input_args = {
            "AlgorithmName": self.algorithm_name,
        }
        client = SageMakerClient().client
        response = client.describe_algorithm(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeAlgorithmOutput", self)
        return self

    def delete(self) -> None:
        """
        Delete a Algorithm resource


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
            ConflictException: There was a conflict when you attempted to modify a SageMaker entity such as an Experiment or Artifact.
        """

        client = SageMakerClient().client

        operation_input_args = {
            "AlgorithmName": self.algorithm_name,
        }
        client.delete_algorithm(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Pending", "InProgress", "Completed", "Failed", "Deleting"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Algorithm"]:
        """
        Wait for a Algorithm resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Algorithm resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.algorithm_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Algorithm", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all Algorithm resources

        Parameters:
            creation_time_after:A filter that returns only algorithms created after the specified time (timestamp).
            creation_time_before:A filter that returns only algorithms created before the specified time (timestamp).
            max_results:The maximum number of algorithms to return in the response.
            name_contains:A string in the algorithm name. This filter returns only algorithms whose name contains the specified string.
            next_token:If the response to a previous ListAlgorithms request was truncated, the response includes a NextToken. To retrieve the next set of algorithms, use the token in the next request.
            sort_by:The parameter by which to sort the results. The default is CreationTime.
            sort_order:The sort order for the results. The default is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Algorithm resources.

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
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "NameContains": name_contains,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_algorithms",
            summaries_key="AlgorithmSummaryList",
            summary_name="AlgorithmSummary",
            resource_cls=Algorithm,
            list_method_kwargs=operation_input_args,
        )


class App(Base):
    """
    Class representing resource App

    Attributes:
        app_arn:The Amazon Resource Name (ARN) of the app.
        app_type:The type of app.
        app_name:The name of the app.
        domain_id:The domain ID.
        user_profile_name:The user profile name.
        space_name:The name of the space. If this value is not set, then UserProfileName must be set.
        status:The status.
        last_health_check_timestamp:The timestamp of the last health check.
        last_user_activity_timestamp:The timestamp of the last user's activity. LastUserActivityTimestamp is also updated when SageMaker performs health checks without user activity. As a result, this value is set to the same value as LastHealthCheckTimestamp.
        creation_time:The creation time of the application.  After an application has been shut down for 24 hours, SageMaker deletes all metadata for the application. To be considered an update and retain application metadata, applications must be restarted within 24 hours after the previous application has been shut down. After this time window, creation of an application is considered a new application rather than an update of the previous application.
        failure_reason:The failure reason.
        resource_spec:The instance type and the Amazon Resource Name (ARN) of the SageMaker image created on the instance.

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
            if attribute == "name" or attribute == "app_name":
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
        """
        Create a App resource

        Parameters:
            domain_id:The domain ID.
            app_type:The type of app.
            app_name:The name of the app.
            user_profile_name:The user profile name. If this value is not set, then SpaceName must be set.
            space_name:The name of the space. If this value is not set, then UserProfileName must be set.
            tags:Each tag consists of a key and an optional value. Tag keys must be unique per resource.
            resource_spec:The instance type and the Amazon Resource Name (ARN) of the SageMaker image created on the instance.  The value of InstanceType passed as part of the ResourceSpec in the CreateApp call overrides the value passed as part of the ResourceSpec configured for the user profile or the domain. If InstanceType is not specified in any of those three ResourceSpec values for a KernelGateway app, the CreateApp call fails with a request validation error.
            session: Boto3 session.
            region: Region name.

        Returns:
            The App resource.

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
            ResourceInUse: Resource being accessed is in use.
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating app resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "DomainId": domain_id,
            "UserProfileName": user_profile_name,
            "SpaceName": space_name,
            "AppType": app_type,
            "AppName": app_name,
            "Tags": tags,
            "ResourceSpec": resource_spec,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="App", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_app(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            domain_id=domain_id,
            app_type=app_type,
            app_name=app_name,
            session=session,
            region=region,
        )

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
        """
        Get a App resource

        Parameters:
            domain_id:The domain ID.
            app_type:The type of app.
            app_name:The name of the app.
            user_profile_name:The user profile name. If this value is not set, then SpaceName must be set.
            space_name:The name of the space.
            session: Boto3 session.
            region: Region name.

        Returns:
            The App resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "DomainId": domain_id,
            "UserProfileName": user_profile_name,
            "SpaceName": space_name,
            "AppType": app_type,
            "AppName": app_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_app(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeAppResponse")
        app = cls(**transformed_response)
        return app

    def refresh(self) -> Optional["App"]:
        """
        Refresh a App resource

        Returns:
            The App resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "DomainId": self.domain_id,
            "UserProfileName": self.user_profile_name,
            "SpaceName": self.space_name,
            "AppType": self.app_type,
            "AppName": self.app_name,
        }
        client = SageMakerClient().client
        response = client.describe_app(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeAppResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a App resource


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
            ResourceInUse: Resource being accessed is in use.
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient().client

        operation_input_args = {
            "DomainId": self.domain_id,
            "UserProfileName": self.user_profile_name,
            "SpaceName": self.space_name,
            "AppType": self.app_type,
            "AppName": self.app_name,
        }
        client.delete_app(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Deleted", "Deleting", "Failed", "InService", "Pending"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["App"]:
        """
        Wait for a App resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The App resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="App", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all App resources

        Parameters:
            next_token:If the previous response was truncated, you will receive this token. Use it in your next request to receive the next set of results.
            max_results:The total number of items to return in the response. If the total number of items available is more than the value specified, a NextToken is provided in the response. To resume pagination, provide the NextToken value in the as part of a subsequent call. The default value is 10.
            sort_order:The sort order for the results. The default is Ascending.
            sort_by:The parameter by which to sort the results. The default is CreationTime.
            domain_id_equals:A parameter to search for the domain ID.
            user_profile_name_equals:A parameter to search by user profile name. If SpaceNameEquals is set, then this value cannot be set.
            space_name_equals:A parameter to search by space name. If UserProfileNameEquals is set, then this value cannot be set.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed App resources.

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
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "SortOrder": sort_order,
            "SortBy": sort_by,
            "DomainIdEquals": domain_id_equals,
            "UserProfileNameEquals": user_profile_name_equals,
            "SpaceNameEquals": space_name_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_apps",
            summaries_key="Apps",
            summary_name="AppDetails",
            resource_cls=App,
            list_method_kwargs=operation_input_args,
        )


class AppImageConfig(Base):
    """
    Class representing resource AppImageConfig

    Attributes:
        app_image_config_arn:The ARN of the AppImageConfig.
        app_image_config_name:The name of the AppImageConfig.
        creation_time:When the AppImageConfig was created.
        last_modified_time:When the AppImageConfig was last modified.
        kernel_gateway_image_config:The configuration of a KernelGateway app.
        jupyter_lab_app_image_config:The configuration of the JupyterLab app.

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
            if attribute == "name" or attribute == "app_image_config_name":
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
        """
        Create a AppImageConfig resource

        Parameters:
            app_image_config_name:The name of the AppImageConfig. Must be unique to your account.
            tags:A list of tags to apply to the AppImageConfig.
            kernel_gateway_image_config:The KernelGatewayImageConfig. You can only specify one image kernel in the AppImageConfig API. This kernel will be shown to users before the image starts. Once the image runs, all kernels are visible in JupyterLab.
            jupyter_lab_app_image_config:The JupyterLabAppImageConfig. You can only specify one image kernel in the AppImageConfig API. This kernel is shown to users before the image starts. After the image runs, all kernels are visible in JupyterLab.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AppImageConfig resource.

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
            ResourceInUse: Resource being accessed is in use.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating app_image_config resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "AppImageConfigName": app_image_config_name,
            "Tags": tags,
            "KernelGatewayImageConfig": kernel_gateway_image_config,
            "JupyterLabAppImageConfig": jupyter_lab_app_image_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="AppImageConfig", operation_input_args=operation_input_args
        )

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
        """
        Get a AppImageConfig resource

        Parameters:
            app_image_config_name:The name of the AppImageConfig to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AppImageConfig resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "AppImageConfigName": app_image_config_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_app_image_config(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeAppImageConfigResponse")
        app_image_config = cls(**transformed_response)
        return app_image_config

    def refresh(self) -> Optional["AppImageConfig"]:
        """
        Refresh a AppImageConfig resource

        Returns:
            The AppImageConfig resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "AppImageConfigName": self.app_image_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_app_image_config(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeAppImageConfigResponse", self)
        return self

    def update(
        self,
        kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned(),
        jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned(),
    ) -> Optional["AppImageConfig"]:
        """
        Update a AppImageConfig resource


        Returns:
            The AppImageConfig resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating app_image_config resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "AppImageConfigName": self.app_image_config_name,
            "KernelGatewayImageConfig": kernel_gateway_image_config,
            "JupyterLabAppImageConfig": jupyter_lab_app_image_config,
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
        """
        Delete a AppImageConfig resource


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
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient().client

        operation_input_args = {
            "AppImageConfigName": self.app_image_config_name,
        }
        client.delete_app_image_config(**operation_input_args)

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
        """
        Get all AppImageConfig resources

        Parameters:
            max_results:The total number of items to return in the response. If the total number of items available is more than the value specified, a NextToken is provided in the response. To resume pagination, provide the NextToken value in the as part of a subsequent call. The default value is 10.
            next_token:If the previous call to ListImages didn't return the full set of AppImageConfigs, the call returns a token for getting the next set of AppImageConfigs.
            name_contains:A filter that returns only AppImageConfigs whose name contains the specified string.
            creation_time_before:A filter that returns only AppImageConfigs created on or before the specified time.
            creation_time_after:A filter that returns only AppImageConfigs created on or after the specified time.
            modified_time_before:A filter that returns only AppImageConfigs modified on or before the specified time.
            modified_time_after:A filter that returns only AppImageConfigs modified on or after the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed AppImageConfig resources.

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
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "ModifiedTimeBefore": modified_time_before,
            "ModifiedTimeAfter": modified_time_after,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_app_image_configs",
            summaries_key="AppImageConfigs",
            summary_name="AppImageConfigDetails",
            resource_cls=AppImageConfig,
            list_method_kwargs=operation_input_args,
        )


class Artifact(Base):
    """
    Class representing resource Artifact

    Attributes:
        artifact_name:The name of the artifact.
        artifact_arn:The Amazon Resource Name (ARN) of the artifact.
        source:The source of the artifact.
        artifact_type:The type of the artifact.
        properties:A list of the artifact's properties.
        creation_time:When the artifact was created.
        created_by:
        last_modified_time:When the artifact was last modified.
        last_modified_by:
        metadata_properties:
        lineage_group_arn:The Amazon Resource Name (ARN) of the lineage group.

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
            if attribute == "name" or attribute == "artifact_name":
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
        """
        Create a Artifact resource

        Parameters:
            source:The ID, ID type, and URI of the source.
            artifact_type:The artifact type.
            artifact_name:The name of the artifact. Must be unique to your account in an Amazon Web Services Region.
            properties:A list of properties to add to the artifact.
            metadata_properties:
            tags:A list of tags to apply to the artifact.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Artifact resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating artifact resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ArtifactName": artifact_name,
            "Source": source,
            "ArtifactType": artifact_type,
            "Properties": properties,
            "MetadataProperties": metadata_properties,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Artifact", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_artifact(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(artifact_arn=response["ArtifactArn"], session=session, region=region)

    @classmethod
    def get(
        cls,
        artifact_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Artifact"]:
        """
        Get a Artifact resource

        Parameters:
            artifact_arn:The Amazon Resource Name (ARN) of the artifact to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Artifact resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "ArtifactArn": artifact_arn,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_artifact(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeArtifactResponse")
        artifact = cls(**transformed_response)
        return artifact

    def refresh(self) -> Optional["Artifact"]:
        """
        Refresh a Artifact resource

        Returns:
            The Artifact resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "ArtifactArn": self.artifact_arn,
        }
        client = SageMakerClient().client
        response = client.describe_artifact(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeArtifactResponse", self)
        return self

    def update(
        self,
        artifact_name: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Artifact"]:
        """
        Update a Artifact resource

        Parameters:
            properties_to_remove:A list of properties to remove.

        Returns:
            The Artifact resource.

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
            ConflictException: There was a conflict when you attempted to modify a SageMaker entity such as an Experiment or Artifact.
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating artifact resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ArtifactArn": self.artifact_arn,
            "ArtifactName": artifact_name,
            "Properties": properties,
            "PropertiesToRemove": properties_to_remove,
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
        """
        Delete a Artifact resource


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
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient().client

        operation_input_args = {
            "ArtifactArn": self.artifact_arn,
            "Source": self.source,
        }
        client.delete_artifact(**operation_input_args)

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
        """
        Get all Artifact resources

        Parameters:
            source_uri:A filter that returns only artifacts with the specified source URI.
            artifact_type:A filter that returns only artifacts of the specified type.
            created_after:A filter that returns only artifacts created on or after the specified time.
            created_before:A filter that returns only artifacts created on or before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            next_token:If the previous call to ListArtifacts didn't return the full set of artifacts, the call returns a token for getting the next set of artifacts.
            max_results:The maximum number of artifacts to return in the response. The default value is 10.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Artifact resources.

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
            ResourceNotFound: Resource being access is not found.
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "SourceUri": source_uri,
            "ArtifactType": artifact_type,
            "CreatedAfter": created_after,
            "CreatedBefore": created_before,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_artifacts",
            summaries_key="ArtifactSummaries",
            summary_name="ArtifactSummary",
            resource_cls=Artifact,
            list_method_kwargs=operation_input_args,
        )
