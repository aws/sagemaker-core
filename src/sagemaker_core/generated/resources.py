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


class AutoMLJob(Base):
    """
    Class representing resource AutoMLJob

    Attributes:
        auto_m_l_job_name:Returns the name of the AutoML job.
        auto_m_l_job_arn:Returns the ARN of the AutoML job.
        input_data_config:Returns the input data configuration for the AutoML job.
        output_data_config:Returns the job's output data config.
        role_arn:The ARN of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.
        creation_time:Returns the creation time of the AutoML job.
        last_modified_time:Returns the job's last modified time.
        auto_m_l_job_status:Returns the status of the AutoML job.
        auto_m_l_job_secondary_status:Returns the secondary status of the AutoML job.
        auto_m_l_job_objective:Returns the job's objective.
        problem_type:Returns the job's problem type.
        auto_m_l_job_config:Returns the configuration for the AutoML job.
        end_time:Returns the end time of the AutoML job.
        failure_reason:Returns the failure reason for an AutoML job, when applicable.
        partial_failure_reasons:Returns a list of reasons for partial failures within an AutoML job.
        best_candidate:The best model candidate selected by SageMaker Autopilot using both the best objective metric and lowest InferenceLatency for an experiment.
        generate_candidate_definitions_only:Indicates whether the output for an AutoML job generates candidate definitions only.
        auto_m_l_job_artifacts:Returns information on the job's artifacts found in AutoMLJobArtifacts.
        resolved_attributes:Contains ProblemType, AutoMLJobObjective, and CompletionCriteria. If you do not provide these values, they are inferred.
        model_deploy_config:Indicates whether the model was deployed automatically to an endpoint and the name of that endpoint if deployed automatically.
        model_deploy_result:Provides information about endpoint for the model deployment.

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
            if attribute == "name" or attribute == "auto_m_l_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "output_data_config": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "role_arn": {"type": "string"},
                "auto_m_l_job_config": {
                    "security_config": {
                        "volume_kms_key_id": {"type": "string"},
                        "vpc_config": {
                            "security_group_ids": {"type": "array", "items": {"type": "string"}},
                            "subnets": {"type": "array", "items": {"type": "string"}},
                        },
                    },
                    "candidate_generation_config": {
                        "feature_specification_s3_uri": {"type": "string"}
                    },
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "AutoMLJob", **kwargs
                ),
            )

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
        """
        Create a AutoMLJob resource

        Parameters:
            auto_m_l_job_name:Identifies an Autopilot job. The name must be unique to your account and is case insensitive.
            input_data_config:An array of channel objects that describes the input data and its location. Each channel is a named input source. Similar to InputDataConfig supported by HyperParameterTrainingJobDefinition. Format(s) supported: CSV, Parquet. A minimum of 500 rows is required for the training dataset. There is not a minimum number of rows required for the validation dataset.
            output_data_config:Provides information about encryption and the Amazon S3 output path needed to store artifacts from an AutoML job. Format(s) supported: CSV.
            role_arn:The ARN of the role that is used to access the data.
            problem_type:Defines the type of supervised learning problem available for the candidates. For more information, see  SageMaker Autopilot problem types.
            auto_m_l_job_objective:Specifies a metric to minimize or maximize as the objective of a job. If not specified, the default objective metric depends on the problem type. See AutoMLJobObjective for the default values.
            auto_m_l_job_config:A collection of settings used to configure an AutoML job.
            generate_candidate_definitions_only:Generates possible candidates without training the models. A candidate is a combination of data preprocessors, algorithms, and algorithm parameter settings.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web ServicesResources. Tag keys must be unique per resource.
            model_deploy_config:Specifies how to generate the endpoint name for an automatic one-click Autopilot model deployment.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AutoMLJob resource.

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

        logger.debug("Creating auto_m_l_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "AutoMLJobName": auto_m_l_job_name,
            "InputDataConfig": input_data_config,
            "OutputDataConfig": output_data_config,
            "ProblemType": problem_type,
            "AutoMLJobObjective": auto_m_l_job_objective,
            "AutoMLJobConfig": auto_m_l_job_config,
            "RoleArn": role_arn,
            "GenerateCandidateDefinitionsOnly": generate_candidate_definitions_only,
            "Tags": tags,
            "ModelDeployConfig": model_deploy_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="AutoMLJob", operation_input_args=operation_input_args
        )

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
        """
        Get a AutoMLJob resource

        Parameters:
            auto_m_l_job_name:Requests information about an AutoML job using its unique name.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AutoMLJob resource.

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
            "AutoMLJobName": auto_m_l_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_auto_m_l_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeAutoMLJobResponse")
        auto_m_l_job = cls(**transformed_response)
        return auto_m_l_job

    def refresh(self) -> Optional["AutoMLJob"]:
        """
        Refresh a AutoMLJob resource

        Returns:
            The AutoMLJob resource.

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
            "AutoMLJobName": self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeAutoMLJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a AutoMLJob resource


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
            "AutoMLJobName": self.auto_m_l_job_name,
        }
        client.stop_auto_m_l_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["AutoMLJob"]:
        """
        Wait for a AutoMLJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The AutoMLJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="AutoMLJob", status=current_status, reason=self.failure_reason
                    )

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
        """
        Get all AutoMLJob resources

        Parameters:
            creation_time_after:Request a list of jobs, using a filter for time.
            creation_time_before:Request a list of jobs, using a filter for time.
            last_modified_time_after:Request a list of jobs, using a filter for time.
            last_modified_time_before:Request a list of jobs, using a filter for time.
            name_contains:Request a list of jobs, using a search filter for name.
            status_equals:Request a list of jobs, using a filter for status.
            sort_order:The sort order for the results. The default is Descending.
            sort_by:The parameter by which to sort the results. The default is Name.
            max_results:Request a list of jobs up to a specified limit.
            next_token:If the previous response was truncated, you receive this token. Use it in your next request to receive the next set of results.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed AutoMLJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
            "SortOrder": sort_order,
            "SortBy": sort_by,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_auto_m_l_jobs",
            summaries_key="AutoMLJobSummaries",
            summary_name="AutoMLJobSummary",
            resource_cls=AutoMLJob,
            list_method_kwargs=operation_input_args,
        )

    def get_all_candidates(
        self,
        status_equals: Optional[str] = Unassigned(),
        candidate_name_equals: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[AutoMLCandidate]:

        operation_input_args = {
            "AutoMLJobName": self.auto_m_l_job_name,
            "StatusEquals": status_equals,
            "CandidateNameEquals": candidate_name_equals,
            "SortOrder": sort_order,
            "SortBy": sort_by,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_candidates_for_auto_m_l_job",
            summaries_key="Candidates",
            summary_name="AutoMLCandidate",
            resource_cls=AutoMLCandidate,
            list_method_kwargs=operation_input_args,
        )


class AutoMLJobV2(Base):
    """
    Class representing resource AutoMLJobV2

    Attributes:
        auto_m_l_job_name:Returns the name of the AutoML job V2.
        auto_m_l_job_arn:Returns the Amazon Resource Name (ARN) of the AutoML job V2.
        auto_m_l_job_input_data_config:Returns an array of channel objects describing the input data and their location.
        output_data_config:Returns the job's output data config.
        role_arn:The ARN of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.
        creation_time:Returns the creation time of the AutoML job V2.
        last_modified_time:Returns the job's last modified time.
        auto_m_l_job_status:Returns the status of the AutoML job V2.
        auto_m_l_job_secondary_status:Returns the secondary status of the AutoML job V2.
        auto_m_l_job_objective:Returns the job's objective.
        auto_m_l_problem_type_config:Returns the configuration settings of the problem type set for the AutoML job V2.
        auto_m_l_problem_type_config_name:Returns the name of the problem type configuration set for the AutoML job V2.
        end_time:Returns the end time of the AutoML job V2.
        failure_reason:Returns the reason for the failure of the AutoML job V2, when applicable.
        partial_failure_reasons:Returns a list of reasons for partial failures within an AutoML job V2.
        best_candidate:Information about the candidate produced by an AutoML training job V2, including its status, steps, and other properties.
        auto_m_l_job_artifacts:
        resolved_attributes:Returns the resolved attributes used by the AutoML job V2.
        model_deploy_config:Indicates whether the model was deployed automatically to an endpoint and the name of that endpoint if deployed automatically.
        model_deploy_result:Provides information about endpoint for the model deployment.
        data_split_config:Returns the configuration settings of how the data are split into train and validation datasets.
        security_config:Returns the security configuration for traffic encryption or Amazon VPC settings.

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
            if attribute == "name" or attribute == "auto_m_l_job_v2_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "output_data_config": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "role_arn": {"type": "string"},
                "auto_m_l_problem_type_config": {
                    "time_series_forecasting_job_config": {
                        "feature_specification_s3_uri": {"type": "string"}
                    },
                    "tabular_job_config": {"feature_specification_s3_uri": {"type": "string"}},
                },
                "security_config": {
                    "volume_kms_key_id": {"type": "string"},
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    },
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "AutoMLJobV2", **kwargs
                ),
            )

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
        """
        Create a AutoMLJobV2 resource

        Parameters:
            auto_m_l_job_name:Identifies an Autopilot job. The name must be unique to your account and is case insensitive.
            auto_m_l_job_input_data_config:An array of channel objects describing the input data and their location. Each channel is a named input source. Similar to the InputDataConfig attribute in the CreateAutoMLJob input parameters. The supported formats depend on the problem type:   For tabular problem types: S3Prefix, ManifestFile.   For image classification: S3Prefix, ManifestFile, AugmentedManifestFile.   For text classification: S3Prefix.   For time-series forecasting: S3Prefix.   For text generation (LLMs fine-tuning): S3Prefix.
            output_data_config:Provides information about encryption and the Amazon S3 output path needed to store artifacts from an AutoML job.
            auto_m_l_problem_type_config:Defines the configuration settings of one of the supported problem types.
            role_arn:The ARN of the role that is used to access the data.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, such as by purpose, owner, or environment. For more information, see Tagging Amazon Web ServicesResources. Tag keys must be unique per resource.
            security_config:The security configuration for traffic encryption or Amazon VPC settings.
            auto_m_l_job_objective:Specifies a metric to minimize or maximize as the objective of a job. If not specified, the default objective metric depends on the problem type. For the list of default values per problem type, see AutoMLJobObjective.    For tabular problem types: You must either provide both the AutoMLJobObjective and indicate the type of supervised learning problem in AutoMLProblemTypeConfig (TabularJobConfig.ProblemType), or none at all.   For text generation problem types (LLMs fine-tuning): Fine-tuning language models in Autopilot does not require setting the AutoMLJobObjective field. Autopilot fine-tunes LLMs without requiring multiple candidates to be trained and evaluated. Instead, using your dataset, Autopilot directly fine-tunes your target model to enhance a default objective metric, the cross-entropy loss. After fine-tuning a language model, you can evaluate the quality of its generated text using different metrics. For a list of the available metrics, see Metrics for fine-tuning LLMs in Autopilot.
            model_deploy_config:Specifies how to generate the endpoint name for an automatic one-click Autopilot model deployment.
            data_split_config:This structure specifies how to split the data into train and validation datasets. The validation and training datasets must contain the same headers. For jobs created by calling CreateAutoMLJob, the validation dataset must be less than 2 GB in size.  This attribute must not be set for the time-series forecasting problem type, as Autopilot automatically splits the input dataset into training and validation sets.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AutoMLJobV2 resource.

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

        logger.debug("Creating auto_m_l_job_v2 resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "AutoMLJobName": auto_m_l_job_name,
            "AutoMLJobInputDataConfig": auto_m_l_job_input_data_config,
            "OutputDataConfig": output_data_config,
            "AutoMLProblemTypeConfig": auto_m_l_problem_type_config,
            "RoleArn": role_arn,
            "Tags": tags,
            "SecurityConfig": security_config,
            "AutoMLJobObjective": auto_m_l_job_objective,
            "ModelDeployConfig": model_deploy_config,
            "DataSplitConfig": data_split_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="AutoMLJobV2", operation_input_args=operation_input_args
        )

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
        """
        Get a AutoMLJobV2 resource

        Parameters:
            auto_m_l_job_name:Requests information about an AutoML job V2 using its unique name.
            session: Boto3 session.
            region: Region name.

        Returns:
            The AutoMLJobV2 resource.

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
            "AutoMLJobName": auto_m_l_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeAutoMLJobV2Response")
        auto_m_l_job_v2 = cls(**transformed_response)
        return auto_m_l_job_v2

    def refresh(self) -> Optional["AutoMLJobV2"]:
        """
        Refresh a AutoMLJobV2 resource

        Returns:
            The AutoMLJobV2 resource.

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
            "AutoMLJobName": self.auto_m_l_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_auto_m_l_job_v2(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeAutoMLJobV2Response", self)
        return self

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["AutoMLJobV2"]:
        """
        Wait for a AutoMLJobV2 resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The AutoMLJobV2 resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.auto_m_l_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="AutoMLJobV2",
                        status=current_status,
                        reason=self.failure_reason,
                    )

                return self

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="AutoMLJobV2", status=current_status)
            print("-", end="")
            time.sleep(poll)


class Cluster(Base):
    """
    Class representing resource Cluster

    Attributes:
        cluster_arn:The Amazon Resource Name (ARN) of the SageMaker HyperPod cluster.
        cluster_status:The status of the SageMaker HyperPod cluster.
        instance_groups:The instance groups of the SageMaker HyperPod cluster.
        cluster_name:The name of the SageMaker HyperPod cluster.
        creation_time:The time when the SageMaker Cluster is created.
        failure_message:The failure message of the SageMaker HyperPod cluster.
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
            if attribute == "name" or attribute == "cluster_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "vpc_config": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "subnets": {"type": "array", "items": {"type": "string"}},
                }
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Cluster", **kwargs
                ),
            )

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
        """
        Create a Cluster resource

        Parameters:
            cluster_name:The name for the new SageMaker HyperPod cluster.
            instance_groups:The instance groups to be created in the SageMaker HyperPod cluster.
            vpc_config:
            tags:Custom tags for managing the SageMaker HyperPod cluster as an Amazon Web Services resource. You can add tags to your cluster in the same way you add them in other Amazon Web Services services that support tagging. To learn more about tagging Amazon Web Services resources in general, see Tagging Amazon Web Services Resources User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Cluster resource.

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

        logger.debug("Creating cluster resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ClusterName": cluster_name,
            "InstanceGroups": instance_groups,
            "VpcConfig": vpc_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Cluster", operation_input_args=operation_input_args
        )

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
        """
        Get a Cluster resource

        Parameters:
            cluster_name:The string name or the Amazon Resource Name (ARN) of the SageMaker HyperPod cluster.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Cluster resource.

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
            "ClusterName": cluster_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_cluster(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeClusterResponse")
        cluster = cls(**transformed_response)
        return cluster

    def refresh(self) -> Optional["Cluster"]:
        """
        Refresh a Cluster resource

        Returns:
            The Cluster resource.

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
            "ClusterName": self.cluster_name,
        }
        client = SageMakerClient().client
        response = client.describe_cluster(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeClusterResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        instance_groups: List[ClusterInstanceGroupSpecification],
    ) -> Optional["Cluster"]:
        """
        Update a Cluster resource


        Returns:
            The Cluster resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating cluster resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ClusterName": self.cluster_name,
            "InstanceGroups": instance_groups,
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
        """
        Delete a Cluster resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "ClusterName": self.cluster_name,
        }
        client.delete_cluster(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Creating",
            "Deleting",
            "Failed",
            "InService",
            "RollingBack",
            "SystemUpdating",
            "Updating",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Cluster"]:
        """
        Wait for a Cluster resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Cluster resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.cluster_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Cluster", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all Cluster resources

        Parameters:
            creation_time_after:Set a start time for the time range during which you want to list SageMaker HyperPod clusters. Timestamps are formatted according to the ISO 8601 standard.  Acceptable formats include:    YYYY-MM-DDThh:mm:ss.sssTZD (UTC), for example, 2014-10-01T20:30:00.000Z     YYYY-MM-DDThh:mm:ss.sssTZD (with offset), for example, 2014-10-01T12:30:00.000-08:00     YYYY-MM-DD, for example, 2014-10-01    Unix time in seconds, for example, 1412195400. This is also referred to as Unix Epoch time and represents the number of seconds since midnight, January 1, 1970 UTC.   For more information about the timestamp format, see Timestamp in the Amazon Web Services Command Line Interface User Guide.
            creation_time_before:Set an end time for the time range during which you want to list SageMaker HyperPod clusters. A filter that returns nodes in a SageMaker HyperPod cluster created before the specified time. The acceptable formats are the same as the timestamp formats for CreationTimeAfter. For more information about the timestamp format, see Timestamp in the Amazon Web Services Command Line Interface User Guide.
            max_results:Set the maximum number of SageMaker HyperPod clusters to list.
            name_contains:Set the maximum number of instances to print in the list.
            next_token:Set the next token to retrieve the list of SageMaker HyperPod clusters.
            sort_by:The field by which to sort results. The default value is CREATION_TIME.
            sort_order:The sort order for results. The default value is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Cluster resources.

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
            list_method="list_clusters",
            summaries_key="ClusterSummaries",
            summary_name="ClusterSummary",
            resource_cls=Cluster,
            list_method_kwargs=operation_input_args,
        )

    def get_node(
        self,
        node_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[ClusterNodeDetails]:
        """
        Perform DescribeClusterNode on a Cluster resource.

        Parameters:
            node_id:The ID of the instance.

        """

        operation_input_args = {
            "ClusterName": self.cluster_name,
            "NodeId": node_id,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling describe_cluster_node API")
        response = client.describe_cluster_node(**operation_input_args)
        logger.debug(f"Response: {response}")

        transformed_response = transform(response, "DescribeClusterNodeResponse")
        return ClusterNodeDetails(**transformed_response)

    def get_all_nodes(
        self,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        instance_group_name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[ClusterNodeDetails]:

        operation_input_args = {
            "ClusterName": self.cluster_name,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "InstanceGroupNameContains": instance_group_name_contains,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_cluster_nodes",
            summaries_key="ClusterNodeSummaries",
            summary_name="ClusterNodeSummary",
            resource_cls=ClusterNodeDetails,
            list_method_kwargs=operation_input_args,
        )

    def update_software(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "ClusterName": self.cluster_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling update_cluster_software API")
        response = client.update_cluster_software(**operation_input_args)
        logger.debug(f"Response: {response}")


class CodeRepository(Base):
    """
    Class representing resource CodeRepository

    Attributes:
        code_repository_name:The name of the Git repository.
        code_repository_arn:The Amazon Resource Name (ARN) of the Git repository.
        creation_time:The date and time that the repository was created.
        last_modified_time:The date and time that the repository was last changed.
        git_config:Configuration details about the repository, including the URL where the repository is located, the default branch, and the Amazon Resource Name (ARN) of the Amazon Web Services Secrets Manager secret that contains the credentials used to access the repository.

    """

    code_repository_name: str
    code_repository_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    git_config: Optional[GitConfig] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "code_repository_name":
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
        """
        Create a CodeRepository resource

        Parameters:
            code_repository_name:The name of the Git repository. The name must have 1 to 63 characters. Valid characters are a-z, A-Z, 0-9, and - (hyphen).
            git_config:Specifies details about the repository, including the URL where the repository is located, the default branch, and credentials to use to access the repository.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            session: Boto3 session.
            region: Region name.

        Returns:
            The CodeRepository resource.

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

        logger.debug("Creating code_repository resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "CodeRepositoryName": code_repository_name,
            "GitConfig": git_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="CodeRepository", operation_input_args=operation_input_args
        )

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
        """
        Get a CodeRepository resource

        Parameters:
            code_repository_name:The name of the Git repository to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The CodeRepository resource.

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
            "CodeRepositoryName": code_repository_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_code_repository(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeCodeRepositoryOutput")
        code_repository = cls(**transformed_response)
        return code_repository

    def refresh(self) -> Optional["CodeRepository"]:
        """
        Refresh a CodeRepository resource

        Returns:
            The CodeRepository resource.

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
            "CodeRepositoryName": self.code_repository_name,
        }
        client = SageMakerClient().client
        response = client.describe_code_repository(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeCodeRepositoryOutput", self)
        return self

    def update(
        self,
        git_config: Optional[GitConfigForUpdate] = Unassigned(),
    ) -> Optional["CodeRepository"]:
        """
        Update a CodeRepository resource


        Returns:
            The CodeRepository resource.

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

        logger.debug("Updating code_repository resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "CodeRepositoryName": self.code_repository_name,
            "GitConfig": git_config,
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
        """
        Delete a CodeRepository resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "CodeRepositoryName": self.code_repository_name,
        }
        client.delete_code_repository(**operation_input_args)

    def get_all(
        self,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_after: Optional[datetime.datetime] = Unassigned(),
        last_modified_time_before: Optional[datetime.datetime] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["CodeRepository"]:

        operation_input_args = {
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_code_repositories",
            summaries_key="CodeRepositorySummaryList",
            summary_name="CodeRepositorySummary",
            resource_cls=CodeRepository,
            list_method_kwargs=operation_input_args,
        )


class CompilationJob(Base):
    """
    Class representing resource CompilationJob

    Attributes:
        compilation_job_name:The name of the model compilation job.
        compilation_job_arn:The Amazon Resource Name (ARN) of the model compilation job.
        compilation_job_status:The status of the model compilation job.
        stopping_condition:Specifies a limit to how long a model compilation job can run. When the job reaches the time limit, Amazon SageMaker ends the compilation job. Use this API to cap model training costs.
        creation_time:The time that the model compilation job was created.
        last_modified_time:The time that the status of the model compilation job was last modified.
        failure_reason:If a model compilation job failed, the reason it failed.
        model_artifacts:Information about the location in Amazon S3 that has been configured for storing the model artifacts used in the compilation job.
        role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker assumes to perform the model compilation job.
        input_config:Information about the location in Amazon S3 of the input model artifacts, the name and shape of the expected data inputs, and the framework in which the model was trained.
        output_config:Information about the output location for the compiled model and the target device that the model runs on.
        compilation_start_time:The time when the model compilation job started the CompilationJob instances.  You are billed for the time between this timestamp and the timestamp in the CompilationEndTime field. In Amazon CloudWatch Logs, the start time might be later than this time. That's because it takes time to download the compilation job, which depends on the size of the compilation job container.
        compilation_end_time:The time when the model compilation job on a compilation job instance ended. For a successful or stopped job, this is when the job's model artifacts have finished uploading. For a failed job, this is when Amazon SageMaker detected that the job failed.
        inference_image:The inference image to use when compiling a model. Specify an image only if the target device is a cloud instance.
        model_package_version_arn:The Amazon Resource Name (ARN) of the versioned model package that was provided to SageMaker Neo when you initiated a compilation job.
        model_digests:Provides a BLAKE2 hash value that identifies the compiled model artifacts in Amazon S3.
        vpc_config:A VpcConfig object that specifies the VPC that you want your compilation job to connect to. Control access to your models by configuring the VPC. For more information, see Protect Compilation Jobs by Using an Amazon Virtual Private Cloud.
        derived_information:Information that SageMaker Neo automatically derived about the model.

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
            if attribute == "name" or attribute == "compilation_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "model_artifacts": {"s3_model_artifacts": {"type": "string"}},
                "role_arn": {"type": "string"},
                "input_config": {"s3_uri": {"type": "string"}},
                "output_config": {
                    "s3_output_location": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "vpc_config": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "subnets": {"type": "array", "items": {"type": "string"}},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "CompilationJob", **kwargs
                ),
            )

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
        """
        Create a CompilationJob resource

        Parameters:
            compilation_job_name:A name for the model compilation job. The name must be unique within the Amazon Web Services Region and within your Amazon Web Services account.
            role_arn:The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to perform tasks on your behalf.  During model compilation, Amazon SageMaker needs your permission to:   Read input data from an S3 bucket   Write model artifacts to an S3 bucket   Write logs to Amazon CloudWatch Logs   Publish metrics to Amazon CloudWatch   You grant permissions for all of these tasks to an IAM role. To pass this role to Amazon SageMaker, the caller of this API must have the iam:PassRole permission. For more information, see Amazon SageMaker Roles.
            output_config:Provides information about the output location for the compiled model and the target device the model runs on.
            stopping_condition:Specifies a limit to how long a model compilation job can run. When the job reaches the time limit, Amazon SageMaker ends the compilation job. Use this API to cap model training costs.
            model_package_version_arn:The Amazon Resource Name (ARN) of a versioned model package. Provide either a ModelPackageVersionArn or an InputConfig object in the request syntax. The presence of both objects in the CreateCompilationJob request will return an exception.
            input_config:Provides information about the location of input model artifacts, the name and shape of the expected data inputs, and the framework in which the model was trained.
            vpc_config:A VpcConfig object that specifies the VPC that you want your compilation job to connect to. Control access to your models by configuring the VPC. For more information, see Protect Compilation Jobs by Using an Amazon Virtual Private Cloud.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            session: Boto3 session.
            region: Region name.

        Returns:
            The CompilationJob resource.

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

        logger.debug("Creating compilation_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "CompilationJobName": compilation_job_name,
            "RoleArn": role_arn,
            "ModelPackageVersionArn": model_package_version_arn,
            "InputConfig": input_config,
            "OutputConfig": output_config,
            "VpcConfig": vpc_config,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="CompilationJob", operation_input_args=operation_input_args
        )

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
        """
        Get a CompilationJob resource

        Parameters:
            compilation_job_name:The name of the model compilation job that you want information about.
            session: Boto3 session.
            region: Region name.

        Returns:
            The CompilationJob resource.

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
            "CompilationJobName": compilation_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_compilation_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeCompilationJobResponse")
        compilation_job = cls(**transformed_response)
        return compilation_job

    def refresh(self) -> Optional["CompilationJob"]:
        """
        Refresh a CompilationJob resource

        Returns:
            The CompilationJob resource.

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
            "CompilationJobName": self.compilation_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_compilation_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeCompilationJobResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a CompilationJob resource


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
            "CompilationJobName": self.compilation_job_name,
        }
        client.delete_compilation_job(**operation_input_args)

    def stop(self) -> None:
        """
        Stop a CompilationJob resource


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
            "CompilationJobName": self.compilation_job_name,
        }
        client.stop_compilation_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["CompilationJob"]:
        """
        Wait for a CompilationJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The CompilationJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["COMPLETED", "FAILED", "STOPPED"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.compilation_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="CompilationJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all CompilationJob resources

        Parameters:
            next_token:If the result of the previous ListCompilationJobs request was truncated, the response includes a NextToken. To retrieve the next set of model compilation jobs, use the token in the next request.
            max_results:The maximum number of model compilation jobs to return in the response.
            creation_time_after:A filter that returns the model compilation jobs that were created after a specified time.
            creation_time_before:A filter that returns the model compilation jobs that were created before a specified time.
            last_modified_time_after:A filter that returns the model compilation jobs that were modified after a specified time.
            last_modified_time_before:A filter that returns the model compilation jobs that were modified before a specified time.
            name_contains:A filter that returns the model compilation jobs whose name contains a specified string.
            status_equals:A filter that retrieves model compilation jobs with a specific CompilationJobStatus status.
            sort_by:The field by which to sort results. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed CompilationJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
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
            list_method="list_compilation_jobs",
            summaries_key="CompilationJobSummaries",
            summary_name="CompilationJobSummary",
            resource_cls=CompilationJob,
            list_method_kwargs=operation_input_args,
        )


class Context(Base):
    """
    Class representing resource Context

    Attributes:
        context_name:The name of the context.
        context_arn:The Amazon Resource Name (ARN) of the context.
        source:The source of the context.
        context_type:The type of the context.
        description:The description of the context.
        properties:A list of the context's properties.
        creation_time:When the context was created.
        created_by:
        last_modified_time:When the context was last modified.
        last_modified_by:
        lineage_group_arn:The Amazon Resource Name (ARN) of the lineage group.

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
            if attribute == "name" or attribute == "context_name":
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
        """
        Create a Context resource

        Parameters:
            context_name:The name of the context. Must be unique to your account in an Amazon Web Services Region.
            source:The source type, ID, and URI.
            context_type:The context type.
            description:The description of the context.
            properties:A list of properties to add to the context.
            tags:A list of tags to apply to the context.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Context resource.

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

        logger.debug("Creating context resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ContextName": context_name,
            "Source": source,
            "ContextType": context_type,
            "Description": description,
            "Properties": properties,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Context", operation_input_args=operation_input_args
        )

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
        """
        Get a Context resource

        Parameters:
            context_name:The name of the context to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Context resource.

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
            "ContextName": context_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_context(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeContextResponse")
        context = cls(**transformed_response)
        return context

    def refresh(self) -> Optional["Context"]:
        """
        Refresh a Context resource

        Returns:
            The Context resource.

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
            "ContextName": self.context_name,
        }
        client = SageMakerClient().client
        response = client.describe_context(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeContextResponse", self)
        return self

    def update(
        self,
        description: Optional[str] = Unassigned(),
        properties: Optional[Dict[str, str]] = Unassigned(),
        properties_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["Context"]:
        """
        Update a Context resource

        Parameters:
            properties_to_remove:A list of properties to remove.

        Returns:
            The Context resource.

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

        logger.debug("Updating context resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ContextName": self.context_name,
            "Description": description,
            "Properties": properties,
            "PropertiesToRemove": properties_to_remove,
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
        """
        Delete a Context resource


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
            "ContextName": self.context_name,
        }
        client.delete_context(**operation_input_args)

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
        """
        Get all Context resources

        Parameters:
            source_uri:A filter that returns only contexts with the specified source URI.
            context_type:A filter that returns only contexts of the specified type.
            created_after:A filter that returns only contexts created on or after the specified time.
            created_before:A filter that returns only contexts created on or before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            next_token:If the previous call to ListContexts didn't return the full set of contexts, the call returns a token for getting the next set of contexts.
            max_results:The maximum number of contexts to return in the response. The default value is 10.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Context resources.

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
            "ContextType": context_type,
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
            list_method="list_contexts",
            summaries_key="ContextSummaries",
            summary_name="ContextSummary",
            resource_cls=Context,
            list_method_kwargs=operation_input_args,
        )


class DataQualityJobDefinition(Base):
    """
    Class representing resource DataQualityJobDefinition

    Attributes:
        job_definition_arn:The Amazon Resource Name (ARN) of the data quality monitoring job definition.
        job_definition_name:The name of the data quality monitoring job definition.
        creation_time:The time that the data quality monitoring job definition was created.
        data_quality_app_specification:Information about the container that runs the data quality monitoring job.
        data_quality_job_input:The list of inputs for the data quality monitoring job. Currently endpoints are supported.
        data_quality_job_output_config:
        job_resources:
        role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
        data_quality_baseline_config:The constraints and baselines for the data quality monitoring job definition.
        network_config:The networking configuration for the data quality monitoring job.
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
            if attribute == "name" or attribute == "data_quality_job_definition_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "data_quality_job_input": {
                    "endpoint_input": {
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                    "batch_transform_input": {
                        "data_captured_destination_s3_uri": {"type": "string"},
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                },
                "data_quality_job_output_config": {"kms_key_id": {"type": "string"}},
                "job_resources": {"cluster_config": {"volume_kms_key_id": {"type": "string"}}},
                "role_arn": {"type": "string"},
                "data_quality_baseline_config": {
                    "constraints_resource": {"s3_uri": {"type": "string"}},
                    "statistics_resource": {"s3_uri": {"type": "string"}},
                },
                "network_config": {
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "DataQualityJobDefinition", **kwargs
                ),
            )

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
        """
        Create a DataQualityJobDefinition resource

        Parameters:
            job_definition_name:The name for the monitoring job definition.
            data_quality_app_specification:Specifies the container that runs the monitoring job.
            data_quality_job_input:A list of inputs for the monitoring job. Currently endpoints are supported as monitoring inputs.
            data_quality_job_output_config:
            job_resources:
            role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
            data_quality_baseline_config:Configures the constraints and baselines for the monitoring job.
            network_config:Specifies networking configuration for the monitoring job.
            stopping_condition:
            tags:(Optional) An array of key-value pairs. For more information, see  Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The DataQualityJobDefinition resource.

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

        logger.debug("Creating data_quality_job_definition resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "JobDefinitionName": job_definition_name,
            "DataQualityBaselineConfig": data_quality_baseline_config,
            "DataQualityAppSpecification": data_quality_app_specification,
            "DataQualityJobInput": data_quality_job_input,
            "DataQualityJobOutputConfig": data_quality_job_output_config,
            "JobResources": job_resources,
            "NetworkConfig": network_config,
            "RoleArn": role_arn,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="DataQualityJobDefinition", operation_input_args=operation_input_args
        )

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
        """
        Get a DataQualityJobDefinition resource

        Parameters:
            job_definition_name:The name of the data quality monitoring job definition to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The DataQualityJobDefinition resource.

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
            "JobDefinitionName": job_definition_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_data_quality_job_definition(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeDataQualityJobDefinitionResponse")
        data_quality_job_definition = cls(**transformed_response)
        return data_quality_job_definition

    def refresh(self) -> Optional["DataQualityJobDefinition"]:
        """
        Refresh a DataQualityJobDefinition resource

        Returns:
            The DataQualityJobDefinition resource.

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
            "JobDefinitionName": self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_data_quality_job_definition(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeDataQualityJobDefinitionResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a DataQualityJobDefinition resource


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
            "JobDefinitionName": self.job_definition_name,
        }
        client.delete_data_quality_job_definition(**operation_input_args)

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
        """
        Get all DataQualityJobDefinition resources

        Parameters:
            endpoint_name:A filter that lists the data quality job definitions associated with the specified endpoint.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:Whether to sort the results in Ascending or Descending order. The default is Descending.
            next_token:If the result of the previous ListDataQualityJobDefinitions request was truncated, the response includes a NextToken. To retrieve the next set of transform jobs, use the token in the next request.&gt;
            max_results:The maximum number of data quality monitoring job definitions to return in the response.
            name_contains:A string in the data quality monitoring job definition name. This filter returns only data quality monitoring job definitions whose name contains the specified string.
            creation_time_before:A filter that returns only data quality monitoring job definitions created before the specified time.
            creation_time_after:A filter that returns only data quality monitoring job definitions created after the specified time.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed DataQualityJobDefinition resources.

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
            "EndpointName": endpoint_name,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }
        custom_key_mapping = {
            "monitoring_job_definition_name": "job_definition_name",
            "monitoring_job_definition_arn": "job_definition_arn",
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_data_quality_job_definitions",
            summaries_key="JobDefinitionSummaries",
            summary_name="MonitoringJobDefinitionSummary",
            resource_cls=DataQualityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args,
        )


class Device(Base):
    """
    Device
     Class representing resource Device
    Attributes
    ---------------------
    device_name:The unique identifier of the device.
    device_fleet_name:The name of the fleet the device belongs to.
    registration_time:The timestamp of the last registration or de-reregistration.
    device_arn:The Amazon Resource Name (ARN) of the device.
    description:A description of the device.
    iot_thing_name:The Amazon Web Services Internet of Things (IoT) object thing name associated with the device.
    latest_heartbeat:The last heartbeat received from the device.
    models:Models on the device.
    max_models:The maximum number of models.
    next_token:The response from the last list when returning a list large enough to need tokening.
    agent_version:Edge Manager agent version.

    """

    device_name: str
    device_fleet_name: str
    device_arn: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    iot_thing_name: Optional[str] = Unassigned()
    registration_time: Optional[datetime.datetime] = Unassigned()
    latest_heartbeat: Optional[datetime.datetime] = Unassigned()
    models: Optional[List[EdgeModel]] = Unassigned()
    max_models: Optional[int] = Unassigned()
    next_token: Optional[str] = Unassigned()
    agent_version: Optional[str] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "device_name":
                return value
        raise Exception("Name attribute not found for object")

    @classmethod
    def get(
        cls,
        device_name: str,
        device_fleet_name: str,
        next_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Device"]:
        operation_input_args = {
            "NextToken": next_token,
            "DeviceName": device_name,
            "DeviceFleetName": device_fleet_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_device(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeDeviceResponse")
        device = cls(**transformed_response)
        return device

    def refresh(self) -> Optional["Device"]:

        operation_input_args = {
            "NextToken": self.next_token,
            "DeviceName": self.device_name,
            "DeviceFleetName": self.device_fleet_name,
        }
        client = SageMakerClient().client
        response = client.describe_device(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeDeviceResponse", self)
        return self

    @classmethod
    def get_all(
        cls,
        latest_heartbeat_after: Optional[datetime.datetime] = Unassigned(),
        model_name: Optional[str] = Unassigned(),
        device_fleet_name: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Device"]:
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "LatestHeartbeatAfter": latest_heartbeat_after,
            "ModelName": model_name,
            "DeviceFleetName": device_fleet_name,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_devices",
            summaries_key="DeviceSummaries",
            summary_name="DeviceSummary",
            resource_cls=Device,
            list_method_kwargs=operation_input_args,
        )


class DeviceFleet(Base):
    """
    Class representing resource DeviceFleet

    Attributes:
        device_fleet_name:The name of the fleet.
        device_fleet_arn:The The Amazon Resource Name (ARN) of the fleet.
        output_config:The output configuration for storing sampled data.
        creation_time:Timestamp of when the device fleet was created.
        last_modified_time:Timestamp of when the device fleet was last updated.
        description:A description of the fleet.
        role_arn:The Amazon Resource Name (ARN) that has access to Amazon Web Services Internet of Things (IoT).
        iot_role_alias:The Amazon Resource Name (ARN) alias created in Amazon Web Services Internet of Things (IoT).

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
            if attribute == "name" or attribute == "device_fleet_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "output_config": {
                    "s3_output_location": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "role_arn": {"type": "string"},
                "iot_role_alias": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "DeviceFleet", **kwargs
                ),
            )

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
        """
        Create a DeviceFleet resource

        Parameters:
            device_fleet_name:The name of the fleet that the device belongs to.
            output_config:The output configuration for storing sample data collected by the fleet.
            role_arn:The Amazon Resource Name (ARN) that has access to Amazon Web Services Internet of Things (IoT).
            description:A description of the fleet.
            tags:Creates tags for the specified fleet.
            enable_iot_role_alias:Whether to create an Amazon Web Services IoT Role Alias during device fleet creation. The name of the role alias generated will match this pattern: "SageMakerEdge-{DeviceFleetName}". For example, if your device fleet is called "demo-fleet", the name of the role alias will be "SageMakerEdge-demo-fleet".
            session: Boto3 session.
            region: Region name.

        Returns:
            The DeviceFleet resource.

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

        logger.debug("Creating device_fleet resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "DeviceFleetName": device_fleet_name,
            "RoleArn": role_arn,
            "Description": description,
            "OutputConfig": output_config,
            "Tags": tags,
            "EnableIotRoleAlias": enable_iot_role_alias,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="DeviceFleet", operation_input_args=operation_input_args
        )

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
        """
        Get a DeviceFleet resource

        Parameters:
            device_fleet_name:The name of the fleet.
            session: Boto3 session.
            region: Region name.

        Returns:
            The DeviceFleet resource.

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
            "DeviceFleetName": device_fleet_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_device_fleet(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeDeviceFleetResponse")
        device_fleet = cls(**transformed_response)
        return device_fleet

    def refresh(self) -> Optional["DeviceFleet"]:
        """
        Refresh a DeviceFleet resource

        Returns:
            The DeviceFleet resource.

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
            "DeviceFleetName": self.device_fleet_name,
        }
        client = SageMakerClient().client
        response = client.describe_device_fleet(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeDeviceFleetResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        output_config: EdgeOutputConfig,
        role_arn: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        enable_iot_role_alias: Optional[bool] = Unassigned(),
    ) -> Optional["DeviceFleet"]:
        """
        Update a DeviceFleet resource

        Parameters:
            enable_iot_role_alias:Whether to create an Amazon Web Services IoT Role Alias during device fleet creation. The name of the role alias generated will match this pattern: "SageMakerEdge-{DeviceFleetName}". For example, if your device fleet is called "demo-fleet", the name of the role alias will be "SageMakerEdge-demo-fleet".

        Returns:
            The DeviceFleet resource.

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
        """

        logger.debug("Updating device_fleet resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
            "RoleArn": role_arn,
            "Description": description,
            "OutputConfig": output_config,
            "EnableIotRoleAlias": enable_iot_role_alias,
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
        """
        Delete a DeviceFleet resource


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
        """

        client = SageMakerClient().client

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
        }
        client.delete_device_fleet(**operation_input_args)

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
        """
        Get all DeviceFleet resources

        Parameters:
            next_token:The response from the last list when returning a list large enough to need tokening.
            max_results:The maximum number of results to select.
            creation_time_after:Filter fleets where packaging job was created after specified time.
            creation_time_before:Filter fleets where the edge packaging job was created before specified time.
            last_modified_time_after:Select fleets where the job was updated after X
            last_modified_time_before:Select fleets where the job was updated before X
            name_contains:Filter for fleets containing this name in their fleet device name.
            sort_by:The column to sort by.
            sort_order:What direction to sort in.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed DeviceFleet resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
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
            list_method="list_device_fleets",
            summaries_key="DeviceFleetSummaries",
            summary_name="DeviceFleetSummary",
            resource_cls=DeviceFleet,
            list_method_kwargs=operation_input_args,
        )

    def deregister_devices(
        self,
        device_names: List[str],
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
            "DeviceNames": device_names,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling deregister_devices API")
        response = client.deregister_devices(**operation_input_args)
        logger.debug(f"Response: {response}")

    def get_report(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[GetDeviceFleetReportResponse]:

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling get_device_fleet_report API")
        response = client.get_device_fleet_report(**operation_input_args)
        logger.debug(f"Response: {response}")

        transformed_response = transform(response, "GetDeviceFleetReportResponse")
        return GetDeviceFleetReportResponse(**transformed_response)

    def register_devices(
        self,
        devices: List[Device],
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
            "Devices": devices,
            "Tags": tags,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling register_devices API")
        response = client.register_devices(**operation_input_args)
        logger.debug(f"Response: {response}")

    def update_devices(
        self,
        devices: List[Device],
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "DeviceFleetName": self.device_fleet_name,
            "Devices": devices,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling update_devices API")
        response = client.update_devices(**operation_input_args)
        logger.debug(f"Response: {response}")


class Domain(Base):
    """
    Class representing resource Domain

    Attributes:
        domain_arn:The domain's Amazon Resource Name (ARN).
        domain_id:The domain ID.
        domain_name:The domain name.
        home_efs_file_system_id:The ID of the Amazon Elastic File System managed by this Domain.
        single_sign_on_managed_application_instance_id:The IAM Identity Center managed application instance ID.
        single_sign_on_application_arn:The ARN of the application managed by SageMaker in IAM Identity Center. This value is only returned for domains created after October 1, 2023.
        status:The status.
        creation_time:The creation time.
        last_modified_time:The last modified time.
        failure_reason:The failure reason.
        security_group_id_for_domain_boundary:The ID of the security group that authorizes traffic between the RSessionGateway apps and the RStudioServerPro app.
        auth_mode:The domain's authentication mode.
        default_user_settings:Settings which are applied to UserProfiles in this domain if settings are not explicitly specified in a given UserProfile.
        domain_settings:A collection of Domain settings.
        app_network_access_type:Specifies the VPC used for non-EFS traffic. The default value is PublicInternetOnly.    PublicInternetOnly - Non-EFS traffic is through a VPC managed by Amazon SageMaker, which allows direct internet access    VpcOnly - All traffic is through the specified VPC and subnets
        home_efs_file_system_kms_key_id:Use KmsKeyId.
        subnet_ids:The VPC subnets that the domain uses for communication.
        url:The domain's URL.
        vpc_id:The ID of the Amazon Virtual Private Cloud (VPC) that the domain uses for communication.
        kms_key_id:The Amazon Web Services KMS customer managed key used to encrypt the EFS volume attached to the domain.
        app_security_group_management:The entity that creates and manages the required security groups for inter-app communication in VPCOnly mode. Required when CreateDomain.AppNetworkAccessType is VPCOnly and DomainSettings.RStudioServerProDomainSettings.DomainExecutionRoleArn is provided.
        default_space_settings:The default settings used to create a space.

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
            if attribute == "name" or attribute == "domain_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "security_group_id_for_domain_boundary": {"type": "string"},
                "default_user_settings": {
                    "execution_role": {"type": "string"},
                    "security_groups": {"type": "array", "items": {"type": "string"}},
                    "sharing_settings": {
                        "s3_output_path": {"type": "string"},
                        "s3_kms_key_id": {"type": "string"},
                    },
                    "canvas_app_settings": {
                        "time_series_forecasting_settings": {
                            "amazon_forecast_role_arn": {"type": "string"}
                        },
                        "model_register_settings": {
                            "cross_account_model_register_role_arn": {"type": "string"}
                        },
                        "workspace_settings": {
                            "s3_artifact_path": {"type": "string"},
                            "s3_kms_key_id": {"type": "string"},
                        },
                        "generative_ai_settings": {"amazon_bedrock_role_arn": {"type": "string"}},
                    },
                },
                "domain_settings": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "r_studio_server_pro_domain_settings": {
                        "domain_execution_role_arn": {"type": "string"}
                    },
                    "execution_role_identity_config": {"type": "string"},
                },
                "home_efs_file_system_kms_key_id": {"type": "string"},
                "subnet_ids": {"type": "array", "items": {"type": "string"}},
                "kms_key_id": {"type": "string"},
                "app_security_group_management": {"type": "string"},
                "default_space_settings": {
                    "execution_role": {"type": "string"},
                    "security_groups": {"type": "array", "items": {"type": "string"}},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Domain", **kwargs
                ),
            )

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
        """
        Create a Domain resource

        Parameters:
            domain_name:A name for the domain.
            auth_mode:The mode of authentication that members use to access the domain.
            default_user_settings:The default settings to use to create a user profile when UserSettings isn't specified in the call to the CreateUserProfile API.  SecurityGroups is aggregated when specified in both calls. For all other settings in UserSettings, the values specified in CreateUserProfile take precedence over those specified in CreateDomain.
            subnet_ids:The VPC subnets that the domain uses for communication.
            vpc_id:The ID of the Amazon Virtual Private Cloud (VPC) that the domain uses for communication.
            domain_settings:A collection of Domain settings.
            tags:Tags to associated with the Domain. Each tag consists of a key and an optional value. Tag keys must be unique per resource. Tags are searchable using the Search API. Tags that you specify for the Domain are also added to all Apps that the Domain launches.
            app_network_access_type:Specifies the VPC used for non-EFS traffic. The default value is PublicInternetOnly.    PublicInternetOnly - Non-EFS traffic is through a VPC managed by Amazon SageMaker, which allows direct internet access    VpcOnly - All traffic is through the specified VPC and subnets
            home_efs_file_system_kms_key_id:Use KmsKeyId.
            kms_key_id:SageMaker uses Amazon Web Services KMS to encrypt EFS and EBS volumes attached to the domain with an Amazon Web Services managed key by default. For more control, specify a customer managed key.
            app_security_group_management:The entity that creates and manages the required security groups for inter-app communication in VPCOnly mode. Required when CreateDomain.AppNetworkAccessType is VPCOnly and DomainSettings.RStudioServerProDomainSettings.DomainExecutionRoleArn is provided. If setting up the domain for use with RStudio, this value must be set to Service.
            default_space_settings:The default settings used to create a space.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Domain resource.

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

        logger.debug("Creating domain resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "DomainName": domain_name,
            "AuthMode": auth_mode,
            "DefaultUserSettings": default_user_settings,
            "DomainSettings": domain_settings,
            "SubnetIds": subnet_ids,
            "VpcId": vpc_id,
            "Tags": tags,
            "AppNetworkAccessType": app_network_access_type,
            "HomeEfsFileSystemKmsKeyId": home_efs_file_system_kms_key_id,
            "KmsKeyId": kms_key_id,
            "AppSecurityGroupManagement": app_security_group_management,
            "DefaultSpaceSettings": default_space_settings,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Domain", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_domain(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(domain_id=response["DomainId"], session=session, region=region)

    @classmethod
    def get(
        cls,
        domain_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["Domain"]:
        """
        Get a Domain resource

        Parameters:
            domain_id:The domain ID.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Domain resource.

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
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_domain(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeDomainResponse")
        domain = cls(**transformed_response)
        return domain

    def refresh(self) -> Optional["Domain"]:
        """
        Refresh a Domain resource

        Returns:
            The Domain resource.

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
        }
        client = SageMakerClient().client
        response = client.describe_domain(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeDomainResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        default_user_settings: Optional[UserSettings] = Unassigned(),
        domain_settings_for_update: Optional[DomainSettingsForUpdate] = Unassigned(),
        app_security_group_management: Optional[str] = Unassigned(),
        default_space_settings: Optional[DefaultSpaceSettings] = Unassigned(),
        subnet_ids: Optional[List[str]] = Unassigned(),
        app_network_access_type: Optional[str] = Unassigned(),
    ) -> Optional["Domain"]:
        """
        Update a Domain resource

        Parameters:
            domain_settings_for_update:A collection of DomainSettings configuration values to update.

        Returns:
            The Domain resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating domain resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "DomainId": self.domain_id,
            "DefaultUserSettings": default_user_settings,
            "DomainSettingsForUpdate": domain_settings_for_update,
            "AppSecurityGroupManagement": app_security_group_management,
            "DefaultSpaceSettings": default_space_settings,
            "SubnetIds": subnet_ids,
            "AppNetworkAccessType": app_network_access_type,
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
        """
        Delete a Domain resource


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
            "RetentionPolicy": self.retention_policy,
        }
        client.delete_domain(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Deleting",
            "Failed",
            "InService",
            "Pending",
            "Updating",
            "Update_Failed",
            "Delete_Failed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Domain"]:
        """
        Wait for a Domain resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Domain resource.

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
                    resource_type="Domain", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all Domain resources.

        Parameters:
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Domain resources.

        """
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_domains",
            summaries_key="Domains",
            summary_name="DomainDetails",
            resource_cls=Domain,
        )


class EdgeDeploymentPlan(Base):
    """
    Class representing resource EdgeDeploymentPlan

    Attributes:
        edge_deployment_plan_arn:The ARN of edge deployment plan.
        edge_deployment_plan_name:The name of the edge deployment plan.
        model_configs:List of models associated with the edge deployment plan.
        device_fleet_name:The device fleet used for this edge deployment plan.
        stages:List of stages in the edge deployment plan.
        edge_deployment_success:The number of edge devices with the successful deployment.
        edge_deployment_pending:The number of edge devices yet to pick up deployment, or in progress.
        edge_deployment_failed:The number of edge devices that failed the deployment.
        next_token:Token to use when calling the next set of stages in the edge deployment plan.
        creation_time:The time when the edge deployment plan was created.
        last_modified_time:The time when the edge deployment plan was last updated.

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
            if attribute == "name" or attribute == "edge_deployment_plan_name":
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
        """
        Create a EdgeDeploymentPlan resource

        Parameters:
            edge_deployment_plan_name:The name of the edge deployment plan.
            model_configs:List of models associated with the edge deployment plan.
            device_fleet_name:The device fleet used for this edge deployment plan.
            stages:List of stages of the edge deployment plan. The number of stages is limited to 10 per deployment.
            tags:List of tags with which to tag the edge deployment plan.
            session: Boto3 session.
            region: Region name.

        Returns:
            The EdgeDeploymentPlan resource.

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

        logger.debug("Creating edge_deployment_plan resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "EdgeDeploymentPlanName": edge_deployment_plan_name,
            "ModelConfigs": model_configs,
            "DeviceFleetName": device_fleet_name,
            "Stages": stages,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="EdgeDeploymentPlan", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_edge_deployment_plan(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            edge_deployment_plan_name=edge_deployment_plan_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        edge_deployment_plan_name: str,
        next_token: Optional[str] = Unassigned(),
        max_results: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgeDeploymentPlan"]:
        """
        Get a EdgeDeploymentPlan resource

        Parameters:
            edge_deployment_plan_name:The name of the deployment plan to describe.
            next_token:If the edge deployment plan has enough stages to require tokening, then this is the response from the last list of stages returned.
            max_results:The maximum number of results to select (50 by default).
            session: Boto3 session.
            region: Region name.

        Returns:
            The EdgeDeploymentPlan resource.

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
            "EdgeDeploymentPlanName": edge_deployment_plan_name,
            "NextToken": next_token,
            "MaxResults": max_results,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_edge_deployment_plan(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeEdgeDeploymentPlanResponse")
        edge_deployment_plan = cls(**transformed_response)
        return edge_deployment_plan

    def refresh(self) -> Optional["EdgeDeploymentPlan"]:
        """
        Refresh a EdgeDeploymentPlan resource

        Returns:
            The EdgeDeploymentPlan resource.

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
            "EdgeDeploymentPlanName": self.edge_deployment_plan_name,
            "NextToken": self.next_token,
            "MaxResults": self.max_results,
        }
        client = SageMakerClient().client
        response = client.describe_edge_deployment_plan(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeEdgeDeploymentPlanResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a EdgeDeploymentPlan resource


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
        """

        client = SageMakerClient().client

        operation_input_args = {
            "EdgeDeploymentPlanName": self.edge_deployment_plan_name,
        }
        client.delete_edge_deployment_plan(**operation_input_args)

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
        """
        Get all EdgeDeploymentPlan resources

        Parameters:
            next_token:The response from the last list when returning a list large enough to need tokening.
            max_results:The maximum number of results to select (50 by default).
            creation_time_after:Selects edge deployment plans created after this time.
            creation_time_before:Selects edge deployment plans created before this time.
            last_modified_time_after:Selects edge deployment plans that were last updated after this time.
            last_modified_time_before:Selects edge deployment plans that were last updated before this time.
            name_contains:Selects edge deployment plans with names containing this name.
            device_fleet_name_contains:Selects edge deployment plans with a device fleet name containing this name.
            sort_by:The column by which to sort the edge deployment plans. Can be one of NAME, DEVICEFLEETNAME, CREATIONTIME, LASTMODIFIEDTIME.
            sort_order:The direction of the sorting (ascending or descending).
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed EdgeDeploymentPlan resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "DeviceFleetNameContains": device_fleet_name_contains,
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
            list_method="list_edge_deployment_plans",
            summaries_key="EdgeDeploymentPlanSummaries",
            summary_name="EdgeDeploymentPlanSummary",
            resource_cls=EdgeDeploymentPlan,
            list_method_kwargs=operation_input_args,
        )


class EdgePackagingJob(Base):
    """
    Class representing resource EdgePackagingJob

    Attributes:
        edge_packaging_job_arn:The Amazon Resource Name (ARN) of the edge packaging job.
        edge_packaging_job_name:The name of the edge packaging job.
        edge_packaging_job_status:The current status of the packaging job.
        compilation_job_name:The name of the SageMaker Neo compilation job that is used to locate model artifacts that are being packaged.
        model_name:The name of the model.
        model_version:The version of the model.
        role_arn:The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to download and upload the model, and to contact Neo.
        output_config:The output configuration for the edge packaging job.
        resource_key:The Amazon Web Services KMS key to use when encrypting the EBS volume the job run on.
        edge_packaging_job_status_message:Returns a message describing the job status and error messages.
        creation_time:The timestamp of when the packaging job was created.
        last_modified_time:The timestamp of when the job was last updated.
        model_artifact:The Amazon Simple Storage (S3) URI where model artifacts ares stored.
        model_signature:The signature document of files in the model artifact.
        preset_deployment_output:The output of a SageMaker Edge Manager deployable resource.

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
            if attribute == "name" or attribute == "edge_packaging_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "role_arn": {"type": "string"},
                "output_config": {
                    "s3_output_location": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "EdgePackagingJob", **kwargs
                ),
            )

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
        """
        Create a EdgePackagingJob resource

        Parameters:
            edge_packaging_job_name:The name of the edge packaging job.
            compilation_job_name:The name of the SageMaker Neo compilation job that will be used to locate model artifacts for packaging.
            model_name:The name of the model.
            model_version:The version of the model.
            role_arn:The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to download and upload the model, and to contact SageMaker Neo.
            output_config:Provides information about the output location for the packaged model.
            resource_key:The Amazon Web Services KMS key to use when encrypting the EBS volume the edge packaging job runs on.
            tags:Creates tags for the packaging job.
            session: Boto3 session.
            region: Region name.

        Returns:
            The EdgePackagingJob resource.

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

        logger.debug("Creating edge_packaging_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "EdgePackagingJobName": edge_packaging_job_name,
            "CompilationJobName": compilation_job_name,
            "ModelName": model_name,
            "ModelVersion": model_version,
            "RoleArn": role_arn,
            "OutputConfig": output_config,
            "ResourceKey": resource_key,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="EdgePackagingJob", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_edge_packaging_job(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            edge_packaging_job_name=edge_packaging_job_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        edge_packaging_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["EdgePackagingJob"]:
        """
        Get a EdgePackagingJob resource

        Parameters:
            edge_packaging_job_name:The name of the edge packaging job.
            session: Boto3 session.
            region: Region name.

        Returns:
            The EdgePackagingJob resource.

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
            "EdgePackagingJobName": edge_packaging_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_edge_packaging_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeEdgePackagingJobResponse")
        edge_packaging_job = cls(**transformed_response)
        return edge_packaging_job

    def refresh(self) -> Optional["EdgePackagingJob"]:
        """
        Refresh a EdgePackagingJob resource

        Returns:
            The EdgePackagingJob resource.

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
            "EdgePackagingJobName": self.edge_packaging_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_edge_packaging_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeEdgePackagingJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a EdgePackagingJob resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "EdgePackagingJobName": self.edge_packaging_job_name,
        }
        client.stop_edge_packaging_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["EdgePackagingJob"]:
        """
        Wait for a EdgePackagingJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The EdgePackagingJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["COMPLETED", "FAILED", "STOPPED"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.edge_packaging_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="EdgePackagingJob",
                        status=current_status,
                        reason=self.edge_packaging_job_status_message,
                    )

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
        """
        Get all EdgePackagingJob resources

        Parameters:
            next_token:The response from the last list when returning a list large enough to need tokening.
            max_results:Maximum number of results to select.
            creation_time_after:Select jobs where the job was created after specified time.
            creation_time_before:Select jobs where the job was created before specified time.
            last_modified_time_after:Select jobs where the job was updated after specified time.
            last_modified_time_before:Select jobs where the job was updated before specified time.
            name_contains:Filter for jobs containing this name in their packaging job name.
            model_name_contains:Filter for jobs where the model name contains this string.
            status_equals:The job status to filter for.
            sort_by:Use to specify what column to sort by.
            sort_order:What direction to sort by.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed EdgePackagingJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "ModelNameContains": model_name_contains,
            "StatusEquals": status_equals,
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
            list_method="list_edge_packaging_jobs",
            summaries_key="EdgePackagingJobSummaries",
            summary_name="EdgePackagingJobSummary",
            resource_cls=EdgePackagingJob,
            list_method_kwargs=operation_input_args,
        )


class Endpoint(Base):
    """
    Class representing resource Endpoint

    Attributes:
        endpoint_name:Name of the endpoint.
        endpoint_arn:The Amazon Resource Name (ARN) of the endpoint.
        endpoint_status:The status of the endpoint.    OutOfService: Endpoint is not available to take incoming requests.    Creating: CreateEndpoint is executing.    Updating: UpdateEndpoint or UpdateEndpointWeightsAndCapacities is executing.    SystemUpdating: Endpoint is undergoing maintenance and cannot be updated or deleted or re-scaled until it has completed. This maintenance operation does not change any customer-specified values such as VPC config, KMS encryption, model, instance type, or instance count.    RollingBack: Endpoint fails to scale up or down or change its variant weight and is in the process of rolling back to its previous configuration. Once the rollback completes, endpoint returns to an InService status. This transitional status only applies to an endpoint that has autoscaling enabled and is undergoing variant weight or capacity changes as part of an UpdateEndpointWeightsAndCapacities call or when the UpdateEndpointWeightsAndCapacities operation is called explicitly.    InService: Endpoint is available to process incoming requests.    Deleting: DeleteEndpoint is executing.    Failed: Endpoint could not be created, updated, or re-scaled. Use the FailureReason value returned by DescribeEndpoint for information about the failure. DeleteEndpoint is the only operation that can be performed on a failed endpoint.    UpdateRollbackFailed: Both the rolling deployment and auto-rollback failed. Your endpoint is in service with a mix of the old and new endpoint configurations. For information about how to remedy this issue and restore the endpoint's status to InService, see Rolling Deployments.
        creation_time:A timestamp that shows when the endpoint was created.
        last_modified_time:A timestamp that shows when the endpoint was last modified.
        endpoint_config_name:The name of the endpoint configuration associated with this endpoint.
        production_variants:An array of ProductionVariantSummary objects, one for each model hosted behind this endpoint.
        data_capture_config:
        failure_reason:If the status of the endpoint is Failed, the reason why it failed.
        last_deployment_config:The most recent deployment configuration for the endpoint.
        async_inference_config:Returns the description of an endpoint configuration created using the  CreateEndpointConfig  API.
        pending_deployment_summary:Returns the summary of an in-progress deployment. This field is only returned when the endpoint is creating or updating with a new endpoint configuration.
        explainer_config:The configuration parameters for an explainer.
        shadow_production_variants:An array of ProductionVariantSummary objects, one for each model that you want to host at this endpoint in shadow mode with production traffic replicated from the model specified on ProductionVariants.

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
            if attribute == "name" or attribute == "endpoint_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "data_capture_config": {
                    "destination_s3_uri": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "async_inference_config": {
                    "output_config": {
                        "kms_key_id": {"type": "string"},
                        "s3_output_path": {"type": "string"},
                        "s3_failure_path": {"type": "string"},
                    }
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Endpoint", **kwargs
                ),
            )

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
        """
        Create a Endpoint resource

        Parameters:
            endpoint_name:The name of the endpoint.The name must be unique within an Amazon Web Services Region in your Amazon Web Services account. The name is case-insensitive in CreateEndpoint, but the case is preserved and must be matched in InvokeEndpoint.
            endpoint_config_name:The name of an endpoint configuration. For more information, see CreateEndpointConfig.
            deployment_config:
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Endpoint resource.

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

        logger.debug("Creating endpoint resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "EndpointName": endpoint_name,
            "EndpointConfigName": endpoint_config_name,
            "DeploymentConfig": deployment_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Endpoint", operation_input_args=operation_input_args
        )

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
        """
        Get a Endpoint resource

        Parameters:
            endpoint_name:The name of the endpoint.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Endpoint resource.

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
            "EndpointName": endpoint_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_endpoint(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeEndpointOutput")
        endpoint = cls(**transformed_response)
        return endpoint

    def refresh(self) -> Optional["Endpoint"]:
        """
        Refresh a Endpoint resource

        Returns:
            The Endpoint resource.

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
            "EndpointName": self.endpoint_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeEndpointOutput", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        retain_all_variant_properties: Optional[bool] = Unassigned(),
        exclude_retained_variant_properties: Optional[List[VariantProperty]] = Unassigned(),
        deployment_config: Optional[DeploymentConfig] = Unassigned(),
        retain_deployment_config: Optional[bool] = Unassigned(),
    ) -> Optional["Endpoint"]:
        """
        Update a Endpoint resource

        Parameters:
            retain_all_variant_properties:When updating endpoint resources, enables or disables the retention of variant properties, such as the instance count or the variant weight. To retain the variant properties of an endpoint when updating it, set RetainAllVariantProperties to true. To use the variant properties specified in a new EndpointConfig call when updating an endpoint, set RetainAllVariantProperties to false. The default is false.
            exclude_retained_variant_properties:When you are updating endpoint resources with RetainAllVariantProperties, whose value is set to true, ExcludeRetainedVariantProperties specifies the list of type VariantProperty to override with the values provided by EndpointConfig. If you don't specify a value for ExcludeRetainedVariantProperties, no variant properties are overridden.
            deployment_config:The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations.
            retain_deployment_config:Specifies whether to reuse the last deployment configuration. The default value is false (the configuration is not reused).

        Returns:
            The Endpoint resource.

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
        """

        logger.debug("Updating endpoint resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "EndpointName": self.endpoint_name,
            "EndpointConfigName": self.endpoint_config_name,
            "RetainAllVariantProperties": retain_all_variant_properties,
            "ExcludeRetainedVariantProperties": exclude_retained_variant_properties,
            "DeploymentConfig": deployment_config,
            "RetainDeploymentConfig": retain_deployment_config,
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
        """
        Delete a Endpoint resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "EndpointName": self.endpoint_name,
        }
        client.delete_endpoint(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "OutOfService",
            "Creating",
            "Updating",
            "SystemUpdating",
            "RollingBack",
            "InService",
            "Deleting",
            "Failed",
            "UpdateRollbackFailed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Endpoint"]:
        """
        Wait for a Endpoint resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Endpoint resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.endpoint_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Endpoint", status=current_status, reason=self.failure_reason
                )

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="Endpoint", status=current_status)
            print("-", end="")
            time.sleep(poll)

    def invoke(
        self,
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
        """
        Invoke a Endpoint resource

        Parameters:
            body:Provides input data, in the format specified in the ContentType request header. Amazon SageMaker passes all of the data in the body to the model.  For information about the format of the request body, see Common Data Formats-Inference.
            content_type:The MIME type of the input data in the request body.
            accept:The desired MIME type of the inference response from the model container.
            custom_attributes:Provides additional information about a request for an inference submitted to a model hosted at an Amazon SageMaker endpoint. The information is an opaque value that is forwarded verbatim. You could use this value, for example, to provide an ID that you can use to track a request or to provide other metadata that a service endpoint was programmed to process. The value must consist of no more than 1024 visible US-ASCII characters as specified in Section 3.3.6. Field Value Components of the Hypertext Transfer Protocol (HTTP/1.1).  The code in your model is responsible for setting or updating any custom attributes in the response. If your code does not set this value in the response, an empty value is returned. For example, if a custom attribute represents the trace ID, your model can prepend the custom attribute with Trace ID: in your post-processing function.  This feature is currently supported in the Amazon Web Services SDKs but not in the Amazon SageMaker Python SDK.
            target_model:The model to request for inference when invoking a multi-model endpoint.
            target_variant:Specify the production variant to send the inference request to when invoking an endpoint that is running two or more variants. Note that this parameter overrides the default behavior for the endpoint, which is to distribute the invocation traffic based on the variant weights. For information about how to use variant targeting to perform a/b testing, see Test models in production
            target_container_hostname:If the endpoint hosts multiple containers and is configured to use direct invocation, this parameter specifies the host name of the container to invoke.
            inference_id:If you provide a value, it is added to the captured data when you enable data capture on the endpoint. For information about data capture, see Capture Data.
            enable_explanations:An optional JMESPath expression used to override the EnableExplanations parameter of the ClarifyExplainerConfig API. See the EnableExplanations section in the developer guide for more information.
            inference_component_name:If the endpoint hosts one or more inference components, this parameter specifies the name of inference component to invoke.


        Returns:
            The Invoke response.

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
            InternalDependencyException: Your request caused an exception with an internal dependency. Contact customer support.
            InternalFailure: An internal failure occurred.
            ModelError: Model (owned by the customer in the container) returned 4xx or 5xx error code.
            ModelNotReadyException: Either a serverless endpoint variant's resources are still being provisioned, or a multi-model endpoint is still downloading or loading the target model. Wait and try your request again.
            ServiceUnavailable: The service is unavailable. Try your call again.
            ValidationError: Inspect your request and try again.
        """

        logger.debug(f"Invoking endpoint resource.")
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client
        operation_input_args = {
            "EndpointName": self.endpoint_name,
            "Body": body,
            "ContentType": content_type,
            "Accept": accept,
            "CustomAttributes": custom_attributes,
            "TargetModel": target_model,
            "TargetVariant": target_variant,
            "TargetContainerHostname": target_container_hostname,
            "InferenceId": inference_id,
            "EnableExplanations": enable_explanations,
            "InferenceComponentName": inference_component_name,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Endpoint._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.invoke_endpoint(**operation_input_args)
        logger.debug(f"Response: {response}")

        return response

    def invoke_async(
        self,
        input_location: str,
        content_type: Optional[str] = Unassigned(),
        accept: Optional[str] = Unassigned(),
        custom_attributes: Optional[str] = Unassigned(),
        inference_id: Optional[str] = Unassigned(),
        request_t_t_l_seconds: Optional[int] = Unassigned(),
        invocation_timeout_seconds: Optional[int] = Unassigned(),
    ) -> Optional[object]:
        """
        Invoke Async a Endpoint resource

        Parameters:
            input_location:The Amazon S3 URI where the inference request payload is stored.
            content_type:The MIME type of the input data in the request body.
            accept:The desired MIME type of the inference response from the model container.
            custom_attributes:Provides additional information about a request for an inference submitted to a model hosted at an Amazon SageMaker endpoint. The information is an opaque value that is forwarded verbatim. You could use this value, for example, to provide an ID that you can use to track a request or to provide other metadata that a service endpoint was programmed to process. The value must consist of no more than 1024 visible US-ASCII characters as specified in Section 3.3.6. Field Value Components of the Hypertext Transfer Protocol (HTTP/1.1).  The code in your model is responsible for setting or updating any custom attributes in the response. If your code does not set this value in the response, an empty value is returned. For example, if a custom attribute represents the trace ID, your model can prepend the custom attribute with Trace ID: in your post-processing function.  This feature is currently supported in the Amazon Web Services SDKs but not in the Amazon SageMaker Python SDK.
            inference_id:The identifier for the inference request. Amazon SageMaker will generate an identifier for you if none is specified.
            request_t_t_l_seconds:Maximum age in seconds a request can be in the queue before it is marked as expired. The default is 6 hours, or 21,600 seconds.
            invocation_timeout_seconds:Maximum amount of time in seconds a request can be processed before it is marked as expired. The default is 15 minutes, or 900 seconds.


        Returns:
            The Invoke response.

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
            InternalFailure: An internal failure occurred.
            ServiceUnavailable: The service is unavailable. Try your call again.
            ValidationError: Inspect your request and try again.
        """

        logger.debug(f"Invoking endpoint resource Async.")
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client

        operation_input_args = {
            "EndpointName": self.endpoint_name,
            "ContentType": content_type,
            "Accept": accept,
            "CustomAttributes": custom_attributes,
            "InferenceId": inference_id,
            "InputLocation": input_location,
            "RequestTTLSeconds": request_t_t_l_seconds,
            "InvocationTimeoutSeconds": invocation_timeout_seconds,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = Endpoint._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.invoke_endpoint_async(**operation_input_args)
        logger.debug(f"Response: {response}")

        return response

    def invoke_with_response_stream(
        self,
        body: Any,
        content_type: Optional[str] = Unassigned(),
        accept: Optional[str] = Unassigned(),
        custom_attributes: Optional[str] = Unassigned(),
        target_variant: Optional[str] = Unassigned(),
        target_container_hostname: Optional[str] = Unassigned(),
        inference_id: Optional[str] = Unassigned(),
        inference_component_name: Optional[str] = Unassigned(),
    ) -> Optional[object]:
        """
        Invoke with response stream a Endpoint resource

        Parameters:
            body:Provides input data, in the format specified in the ContentType request header. Amazon SageMaker passes all of the data in the body to the model.  For information about the format of the request body, see Common Data Formats-Inference.
            content_type:The MIME type of the input data in the request body.
            accept:The desired MIME type of the inference response from the model container.
            custom_attributes:Provides additional information about a request for an inference submitted to a model hosted at an Amazon SageMaker endpoint. The information is an opaque value that is forwarded verbatim. You could use this value, for example, to provide an ID that you can use to track a request or to provide other metadata that a service endpoint was programmed to process. The value must consist of no more than 1024 visible US-ASCII characters as specified in Section 3.3.6. Field Value Components of the Hypertext Transfer Protocol (HTTP/1.1).  The code in your model is responsible for setting or updating any custom attributes in the response. If your code does not set this value in the response, an empty value is returned. For example, if a custom attribute represents the trace ID, your model can prepend the custom attribute with Trace ID: in your post-processing function.  This feature is currently supported in the Amazon Web Services SDKs but not in the Amazon SageMaker Python SDK.
            target_variant:Specify the production variant to send the inference request to when invoking an endpoint that is running two or more variants. Note that this parameter overrides the default behavior for the endpoint, which is to distribute the invocation traffic based on the variant weights. For information about how to use variant targeting to perform a/b testing, see Test models in production
            target_container_hostname:If the endpoint hosts multiple containers and is configured to use direct invocation, this parameter specifies the host name of the container to invoke.
            inference_id:An identifier that you assign to your request.
            inference_component_name:If the endpoint hosts one or more inference components, this parameter specifies the name of inference component to invoke for a streaming response.


        Returns:
            The Invoke response.

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
            InternalFailure: An internal failure occurred.
            InternalStreamFailure: The stream processing failed because of an unknown error, exception or failure. Try your request again.
            ModelError: Model (owned by the customer in the container) returned 4xx or 5xx error code.
            ModelStreamError: An error occurred while streaming the response body. This error can have the following error codes:  ModelInvocationTimeExceeded  The model failed to finish sending the response within the timeout period allowed by Amazon SageMaker.  StreamBroken  The Transmission Control Protocol (TCP) connection between the client and the model was reset or closed.
            ServiceUnavailable: The service is unavailable. Try your call again.
            ValidationError: Inspect your request and try again.
        """

        logger.debug(f"Invoking endpoint resource with Response Stream.")
        client = SageMakerRuntimeClient(service_name="sagemaker-runtime").client

        operation_input_args = {
            "EndpointName": self.endpoint_name,
            "Body": body,
            "ContentType": content_type,
            "Accept": accept,
            "CustomAttributes": custom_attributes,
            "TargetVariant": target_variant,
            "TargetContainerHostname": target_container_hostname,
            "InferenceId": inference_id,
            "InferenceComponentName": inference_component_name,
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
        """
        Get all Endpoint resources

        Parameters:
            sort_by:Sorts the list of results. The default is CreationTime.
            sort_order:The sort order for results. The default is Descending.
            next_token:If the result of a ListEndpoints request was truncated, the response includes a NextToken. To retrieve the next set of endpoints, use the token in the next request.
            max_results:The maximum number of endpoints to return in the response. This value defaults to 10.
            name_contains:A string in endpoint names. This filter returns only endpoints whose name contains the specified string.
            creation_time_before:A filter that returns only endpoints that were created before the specified time (timestamp).
            creation_time_after:A filter that returns only endpoints with a creation time greater than or equal to the specified time (timestamp).
            last_modified_time_before: A filter that returns only endpoints that were modified before the specified timestamp.
            last_modified_time_after: A filter that returns only endpoints that were modified after the specified timestamp.
            status_equals: A filter that returns only endpoints with the specified status.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Endpoint resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "StatusEquals": status_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_endpoints",
            summaries_key="Endpoints",
            summary_name="EndpointSummary",
            resource_cls=Endpoint,
            list_method_kwargs=operation_input_args,
        )

    def update_weights_and_capacities(
        self,
        desired_weights_and_capacities: List[DesiredWeightAndCapacity],
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "EndpointName": self.endpoint_name,
            "DesiredWeightsAndCapacities": desired_weights_and_capacities,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling update_endpoint_weights_and_capacities API")
        response = client.update_endpoint_weights_and_capacities(**operation_input_args)
        logger.debug(f"Response: {response}")


class EndpointConfig(Base):
    """
    Class representing resource EndpointConfig

    Attributes:
        endpoint_config_name:Name of the SageMaker endpoint configuration.
        endpoint_config_arn:The Amazon Resource Name (ARN) of the endpoint configuration.
        production_variants:An array of ProductionVariant objects, one for each model that you want to host at this endpoint.
        creation_time:A timestamp that shows when the endpoint configuration was created.
        data_capture_config:
        kms_key_id:Amazon Web Services KMS key ID Amazon SageMaker uses to encrypt data when storing it on the ML storage volume attached to the instance.
        async_inference_config:Returns the description of an endpoint configuration created using the  CreateEndpointConfig  API.
        explainer_config:The configuration parameters for an explainer.
        shadow_production_variants:An array of ProductionVariant objects, one for each model that you want to host at this endpoint in shadow mode with production traffic replicated from the model specified on ProductionVariants.
        execution_role_arn:The Amazon Resource Name (ARN) of the IAM role that you assigned to the endpoint configuration.
        vpc_config:
        enable_network_isolation:Indicates whether all model containers deployed to the endpoint are isolated. If they are, no inbound or outbound network calls can be made to or from the model containers.

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
            if attribute == "name" or attribute == "endpoint_config_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "data_capture_config": {
                    "destination_s3_uri": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "kms_key_id": {"type": "string"},
                "async_inference_config": {
                    "output_config": {
                        "kms_key_id": {"type": "string"},
                        "s3_output_path": {"type": "string"},
                        "s3_failure_path": {"type": "string"},
                    }
                },
                "execution_role_arn": {"type": "string"},
                "vpc_config": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "subnets": {"type": "array", "items": {"type": "string"}},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "EndpointConfig", **kwargs
                ),
            )

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
        """
        Create a EndpointConfig resource

        Parameters:
            endpoint_config_name:The name of the endpoint configuration. You specify this name in a CreateEndpoint request.
            production_variants:An array of ProductionVariant objects, one for each model that you want to host at this endpoint.
            data_capture_config:
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            kms_key_id:The Amazon Resource Name (ARN) of a Amazon Web Services Key Management Service key that SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the endpoint. The KmsKeyId can be any of the following formats:    Key ID: 1234abcd-12ab-34cd-56ef-1234567890ab    Key ARN: arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab    Alias name: alias/ExampleAlias    Alias name ARN: arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias    The KMS key policy must grant permission to the IAM role that you specify in your CreateEndpoint, UpdateEndpoint requests. For more information, refer to the Amazon Web Services Key Management Service section Using Key Policies in Amazon Web Services KMS    Certain Nitro-based instances include local storage, dependent on the instance type. Local storage volumes are encrypted using a hardware module on the instance. You can't request a KmsKeyId when using an instance type with local storage. If any of the models that you specify in the ProductionVariants parameter use nitro-based instances with local storage, do not specify a value for the KmsKeyId parameter. If you specify a value for KmsKeyId when using any nitro-based instances with local storage, the call to CreateEndpointConfig fails. For a list of instance types that support local instance storage, see Instance Store Volumes. For more information about local instance storage encryption, see SSD Instance Store Volumes.
            async_inference_config:Specifies configuration for how an endpoint performs asynchronous inference. This is a required field in order for your Endpoint to be invoked using InvokeEndpointAsync.
            explainer_config:A member of CreateEndpointConfig that enables explainers.
            shadow_production_variants:An array of ProductionVariant objects, one for each model that you want to host at this endpoint in shadow mode with production traffic replicated from the model specified on ProductionVariants. If you use this field, you can only specify one variant for ProductionVariants and one variant for ShadowProductionVariants.
            execution_role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform actions on your behalf. For more information, see SageMaker Roles.   To be able to pass this role to Amazon SageMaker, the caller of this action must have the iam:PassRole permission.
            vpc_config:
            enable_network_isolation:Sets whether all model containers deployed to the endpoint are isolated. If they are, no inbound or outbound network calls can be made to or from the model containers.
            session: Boto3 session.
            region: Region name.

        Returns:
            The EndpointConfig resource.

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

        logger.debug("Creating endpoint_config resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "EndpointConfigName": endpoint_config_name,
            "ProductionVariants": production_variants,
            "DataCaptureConfig": data_capture_config,
            "Tags": tags,
            "KmsKeyId": kms_key_id,
            "AsyncInferenceConfig": async_inference_config,
            "ExplainerConfig": explainer_config,
            "ShadowProductionVariants": shadow_production_variants,
            "ExecutionRoleArn": execution_role_arn,
            "VpcConfig": vpc_config,
            "EnableNetworkIsolation": enable_network_isolation,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="EndpointConfig", operation_input_args=operation_input_args
        )

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
        """
        Get a EndpointConfig resource

        Parameters:
            endpoint_config_name:The name of the endpoint configuration.
            session: Boto3 session.
            region: Region name.

        Returns:
            The EndpointConfig resource.

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
            "EndpointConfigName": endpoint_config_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_endpoint_config(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeEndpointConfigOutput")
        endpoint_config = cls(**transformed_response)
        return endpoint_config

    def refresh(self) -> Optional["EndpointConfig"]:
        """
        Refresh a EndpointConfig resource

        Returns:
            The EndpointConfig resource.

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
            "EndpointConfigName": self.endpoint_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_endpoint_config(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeEndpointConfigOutput", self)
        return self

    def delete(self) -> None:
        """
        Delete a EndpointConfig resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "EndpointConfigName": self.endpoint_config_name,
        }
        client.delete_endpoint_config(**operation_input_args)

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
        """
        Get all EndpointConfig resources

        Parameters:
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Descending.
            next_token:If the result of the previous ListEndpointConfig request was truncated, the response includes a NextToken. To retrieve the next set of endpoint configurations, use the token in the next request.
            max_results:The maximum number of training jobs to return in the response.
            name_contains:A string in the endpoint configuration name. This filter returns only endpoint configurations whose name contains the specified string.
            creation_time_before:A filter that returns only endpoint configurations created before the specified time (timestamp).
            creation_time_after:A filter that returns only endpoint configurations with a creation time greater than or equal to the specified time (timestamp).
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed EndpointConfig resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_endpoint_configs",
            summaries_key="EndpointConfigs",
            summary_name="EndpointConfigSummary",
            resource_cls=EndpointConfig,
            list_method_kwargs=operation_input_args,
        )


class Experiment(Base):
    """
    Class representing resource Experiment

    Attributes:
        experiment_name:The name of the experiment.
        experiment_arn:The Amazon Resource Name (ARN) of the experiment.
        display_name:The name of the experiment as displayed. If DisplayName isn't specified, ExperimentName is displayed.
        source:The Amazon Resource Name (ARN) of the source and, optionally, the type.
        description:The description of the experiment.
        creation_time:When the experiment was created.
        created_by:Who created the experiment.
        last_modified_time:When the experiment was last modified.
        last_modified_by:Who last modified the experiment.

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
            if attribute == "name" or attribute == "experiment_name":
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
        """
        Create a Experiment resource

        Parameters:
            experiment_name:The name of the experiment. The name must be unique in your Amazon Web Services account and is not case-sensitive.
            display_name:The name of the experiment as displayed. The name doesn't need to be unique. If you don't specify DisplayName, the value in ExperimentName is displayed.
            description:The description of the experiment.
            tags:A list of tags to associate with the experiment. You can use Search API to search on the tags.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Experiment resource.

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

        logger.debug("Creating experiment resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ExperimentName": experiment_name,
            "DisplayName": display_name,
            "Description": description,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Experiment", operation_input_args=operation_input_args
        )

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
        """
        Get a Experiment resource

        Parameters:
            experiment_name:The name of the experiment to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Experiment resource.

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
            "ExperimentName": experiment_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_experiment(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeExperimentResponse")
        experiment = cls(**transformed_response)
        return experiment

    def refresh(self) -> Optional["Experiment"]:
        """
        Refresh a Experiment resource

        Returns:
            The Experiment resource.

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
            "ExperimentName": self.experiment_name,
        }
        client = SageMakerClient().client
        response = client.describe_experiment(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeExperimentResponse", self)
        return self

    def update(
        self,
        display_name: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
    ) -> Optional["Experiment"]:
        """
        Update a Experiment resource


        Returns:
            The Experiment resource.

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

        logger.debug("Updating experiment resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ExperimentName": self.experiment_name,
            "DisplayName": display_name,
            "Description": description,
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
        """
        Delete a Experiment resource


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
            "ExperimentName": self.experiment_name,
        }
        client.delete_experiment(**operation_input_args)

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
        """
        Get all Experiment resources

        Parameters:
            created_after:A filter that returns only experiments created after the specified time.
            created_before:A filter that returns only experiments created before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            next_token:If the previous call to ListExperiments didn't return the full set of experiments, the call returns a token for getting the next set of experiments.
            max_results:The maximum number of experiments to return in the response. The default value is 10.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Experiment resources.

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
            list_method="list_experiments",
            summaries_key="ExperimentSummaries",
            summary_name="ExperimentSummary",
            resource_cls=Experiment,
            list_method_kwargs=operation_input_args,
        )


class FeatureGroup(Base):
    """
    Class representing resource FeatureGroup

    Attributes:
        feature_group_arn:The Amazon Resource Name (ARN) of the FeatureGroup.
        feature_group_name:he name of the FeatureGroup.
        record_identifier_feature_name:The name of the Feature used for RecordIdentifier, whose value uniquely identifies a record stored in the feature store.
        event_time_feature_name:The name of the feature that stores the EventTime of a Record in a FeatureGroup.  An EventTime is a point in time when a new event occurs that corresponds to the creation or update of a Record in a FeatureGroup. All Records in the FeatureGroup have a corresponding EventTime.
        feature_definitions:A list of the Features in the FeatureGroup. Each feature is defined by a FeatureName and FeatureType.
        creation_time:A timestamp indicating when SageMaker created the FeatureGroup.
        next_token:A token to resume pagination of the list of Features (FeatureDefinitions).
        last_modified_time:A timestamp indicating when the feature group was last updated.
        online_store_config:The configuration for the OnlineStore.
        offline_store_config:The configuration of the offline store. It includes the following configurations:   Amazon S3 location of the offline store.   Configuration of the Glue data catalog.   Table format of the offline store.   Option to disable the automatic creation of a Glue table for the offline store.   Encryption configuration.
        throughput_config:
        role_arn:The Amazon Resource Name (ARN) of the IAM execution role used to persist data into the OfflineStore if an OfflineStoreConfig is provided.
        feature_group_status:The status of the feature group.
        offline_store_status:The status of the OfflineStore. Notifies you if replicating data into the OfflineStore has failed. Returns either: Active or Blocked
        last_update_status:A value indicating whether the update made to the feature group was successful.
        failure_reason:The reason that the FeatureGroup failed to be replicated in the OfflineStore. This is failure can occur because:   The FeatureGroup could not be created in the OfflineStore.   The FeatureGroup could not be deleted from the OfflineStore.
        description:A free form description of the feature group.
        online_store_total_size_bytes:The size of the OnlineStore in bytes.

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
            if attribute == "name" or attribute == "feature_group_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "online_store_config": {"security_config": {"kms_key_id": {"type": "string"}}},
                "offline_store_config": {
                    "s3_storage_config": {
                        "s3_uri": {"type": "string"},
                        "kms_key_id": {"type": "string"},
                        "resolved_output_s3_uri": {"type": "string"},
                    }
                },
                "role_arn": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "FeatureGroup", **kwargs
                ),
            )

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
        """
        Create a FeatureGroup resource

        Parameters:
            feature_group_name:The name of the FeatureGroup. The name must be unique within an Amazon Web Services Region in an Amazon Web Services account. The name:   Must start and end with an alphanumeric character.   Can only include alphanumeric characters, underscores, and hyphens. Spaces are not allowed.
            record_identifier_feature_name:The name of the Feature whose value uniquely identifies a Record defined in the FeatureStore. Only the latest record per identifier value will be stored in the OnlineStore. RecordIdentifierFeatureName must be one of feature definitions' names. You use the RecordIdentifierFeatureName to access data in a FeatureStore. This name:   Must start and end with an alphanumeric character.   Can only contains alphanumeric characters, hyphens, underscores. Spaces are not allowed.
            event_time_feature_name:The name of the feature that stores the EventTime of a Record in a FeatureGroup. An EventTime is a point in time when a new event occurs that corresponds to the creation or update of a Record in a FeatureGroup. All Records in the FeatureGroup must have a corresponding EventTime. An EventTime can be a String or Fractional.     Fractional: EventTime feature values must be a Unix timestamp in seconds.    String: EventTime feature values must be an ISO-8601 string in the format. The following formats are supported yyyy-MM-dd'T'HH:mm:ssZ and yyyy-MM-dd'T'HH:mm:ss.SSSZ where yyyy, MM, and dd represent the year, month, and day respectively and HH, mm, ss, and if applicable, SSS represent the hour, month, second and milliseconds respsectively. 'T' and Z are constants.
            feature_definitions:A list of Feature names and types. Name and Type is compulsory per Feature.  Valid feature FeatureTypes are Integral, Fractional and String.  FeatureNames cannot be any of the following: is_deleted, write_time, api_invocation_time  You can create up to 2,500 FeatureDefinitions per FeatureGroup.
            online_store_config:You can turn the OnlineStore on or off by specifying True for the EnableOnlineStore flag in OnlineStoreConfig. You can also include an Amazon Web Services KMS key ID (KMSKeyId) for at-rest encryption of the OnlineStore. The default value is False.
            offline_store_config:Use this to configure an OfflineFeatureStore. This parameter allows you to specify:   The Amazon Simple Storage Service (Amazon S3) location of an OfflineStore.   A configuration for an Amazon Web Services Glue or Amazon Web Services Hive data catalog.    An KMS encryption key to encrypt the Amazon S3 location used for OfflineStore. If KMS encryption key is not specified, by default we encrypt all data at rest using Amazon Web Services KMS key. By defining your bucket-level key for SSE, you can reduce Amazon Web Services KMS requests costs by up to 99 percent.   Format for the offline store table. Supported formats are Glue (Default) and Apache Iceberg.   To learn more about this parameter, see OfflineStoreConfig.
            throughput_config:
            role_arn:The Amazon Resource Name (ARN) of the IAM execution role used to persist data into the OfflineStore if an OfflineStoreConfig is provided.
            description:A free-form description of a FeatureGroup.
            tags:Tags used to identify Features in each FeatureGroup.
            session: Boto3 session.
            region: Region name.

        Returns:
            The FeatureGroup resource.

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

        logger.debug("Creating feature_group resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "FeatureGroupName": feature_group_name,
            "RecordIdentifierFeatureName": record_identifier_feature_name,
            "EventTimeFeatureName": event_time_feature_name,
            "FeatureDefinitions": feature_definitions,
            "OnlineStoreConfig": online_store_config,
            "OfflineStoreConfig": offline_store_config,
            "ThroughputConfig": throughput_config,
            "RoleArn": role_arn,
            "Description": description,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="FeatureGroup", operation_input_args=operation_input_args
        )

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
        """
        Get a FeatureGroup resource

        Parameters:
            feature_group_name:The name or Amazon Resource Name (ARN) of the FeatureGroup you want described.
            next_token:A token to resume pagination of the list of Features (FeatureDefinitions). 2,500 Features are returned by default.
            session: Boto3 session.
            region: Region name.

        Returns:
            The FeatureGroup resource.

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
            "FeatureGroupName": feature_group_name,
            "NextToken": next_token,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_feature_group(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeFeatureGroupResponse")
        feature_group = cls(**transformed_response)
        return feature_group

    def refresh(self) -> Optional["FeatureGroup"]:
        """
        Refresh a FeatureGroup resource

        Returns:
            The FeatureGroup resource.

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
            "FeatureGroupName": self.feature_group_name,
            "NextToken": self.next_token,
        }
        client = SageMakerClient().client
        response = client.describe_feature_group(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeFeatureGroupResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        feature_additions: Optional[List[FeatureDefinition]] = Unassigned(),
        online_store_config: Optional[OnlineStoreConfigUpdate] = Unassigned(),
        throughput_config: Optional[ThroughputConfigUpdate] = Unassigned(),
    ) -> Optional["FeatureGroup"]:
        """
        Update a FeatureGroup resource

        Parameters:
            feature_additions:Updates the feature group. Updating a feature group is an asynchronous operation. When you get an HTTP 200 response, you've made a valid request. It takes some time after you've made a valid request for Feature Store to update the feature group.

        Returns:
            The FeatureGroup resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating feature_group resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "FeatureGroupName": self.feature_group_name,
            "FeatureAdditions": feature_additions,
            "OnlineStoreConfig": online_store_config,
            "ThroughputConfig": throughput_config,
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
        """
        Delete a FeatureGroup resource


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
            "FeatureGroupName": self.feature_group_name,
        }
        client.delete_feature_group(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Creating", "Created", "CreateFailed", "Deleting", "DeleteFailed"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["FeatureGroup"]:
        """
        Wait for a FeatureGroup resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The FeatureGroup resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.feature_group_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="FeatureGroup", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all FeatureGroup resources

        Parameters:
            name_contains:A string that partially matches one or more FeatureGroups names. Filters FeatureGroups by name.
            feature_group_status_equals:A FeatureGroup status. Filters by FeatureGroup status.
            offline_store_status_equals:An OfflineStore status. Filters by OfflineStore status.
            creation_time_after:Use this parameter to search for FeatureGroupss created after a specific date and time.
            creation_time_before:Use this parameter to search for FeatureGroupss created before a specific date and time.
            sort_order:The order in which feature groups are listed.
            sort_by:The value on which the feature group list is sorted.
            max_results:The maximum number of results returned by ListFeatureGroups.
            next_token:A token to resume pagination of ListFeatureGroups results.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed FeatureGroup resources.

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
            "FeatureGroupStatusEquals": feature_group_status_equals,
            "OfflineStoreStatusEquals": offline_store_status_equals,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "SortOrder": sort_order,
            "SortBy": sort_by,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_feature_groups",
            summaries_key="FeatureGroupSummaries",
            summary_name="FeatureGroupSummary",
            resource_cls=FeatureGroup,
            list_method_kwargs=operation_input_args,
        )


class FeatureMetadata(Base):
    """
    FeatureMetadata
     Class representing resource FeatureMetadata
    Attributes
    ---------------------
    feature_group_arn:The Amazon Resource Number (ARN) of the feature group that contains the feature.
    feature_group_name:The name of the feature group that you've specified.
    feature_name:The name of the feature that you've specified.
    feature_type:The data type of the feature.
    creation_time:A timestamp indicating when the feature was created.
    last_modified_time:A timestamp indicating when the metadata for the feature group was modified. For example, if you add a parameter describing the feature, the timestamp changes to reflect the last time you
    description:The description you added to describe the feature.
    parameters:The key-value pairs that you added to describe the feature.

    """

    feature_group_name: str
    feature_name: str
    feature_group_arn: Optional[str] = Unassigned()
    feature_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    parameters: Optional[List[FeatureParameter]] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "feature_metadata_name":
                return value
        raise Exception("Name attribute not found for object")

    @classmethod
    def get(
        cls,
        feature_group_name: str,
        feature_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["FeatureMetadata"]:
        operation_input_args = {
            "FeatureGroupName": feature_group_name,
            "FeatureName": feature_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_feature_metadata(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeFeatureMetadataResponse")
        feature_metadata = cls(**transformed_response)
        return feature_metadata

    def refresh(self) -> Optional["FeatureMetadata"]:

        operation_input_args = {
            "FeatureGroupName": self.feature_group_name,
            "FeatureName": self.feature_name,
        }
        client = SageMakerClient().client
        response = client.describe_feature_metadata(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeFeatureMetadataResponse", self)
        return self

    def update(
        self,
        description: Optional[str] = Unassigned(),
        parameter_additions: Optional[List[FeatureParameter]] = Unassigned(),
        parameter_removals: Optional[List[str]] = Unassigned(),
    ) -> Optional["FeatureMetadata"]:
        logger.debug("Creating feature_metadata resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "FeatureGroupName": self.feature_group_name,
            "FeatureName": self.feature_name,
            "Description": description,
            "ParameterAdditions": parameter_additions,
            "ParameterRemovals": parameter_removals,
        }
        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = FeatureMetadata._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.update_feature_metadata(**operation_input_args)
        logger.debug(f"Response: {response}")
        self.refresh()

        return self


class FlowDefinition(Base):
    """
    Class representing resource FlowDefinition

    Attributes:
        flow_definition_arn:The Amazon Resource Name (ARN) of the flow defintion.
        flow_definition_name:The Amazon Resource Name (ARN) of the flow definition.
        flow_definition_status:The status of the flow definition. Valid values are listed below.
        creation_time:The timestamp when the flow definition was created.
        output_config:An object containing information about the output file.
        role_arn:The Amazon Resource Name (ARN) of the Amazon Web Services Identity and Access Management (IAM) execution role for the flow definition.
        human_loop_request_source:Container for configuring the source of human task requests. Used to specify if Amazon Rekognition or Amazon Textract is used as an integration source.
        human_loop_activation_config:An object containing information about what triggers a human review workflow.
        human_loop_config:An object containing information about who works on the task, the workforce task price, and other task details.
        failure_reason:The reason your flow definition failed.

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
            if attribute == "name" or attribute == "flow_definition_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "output_config": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "role_arn": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "FlowDefinition", **kwargs
                ),
            )

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
        """
        Create a FlowDefinition resource

        Parameters:
            flow_definition_name:The name of your flow definition.
            output_config:An object containing information about where the human review results will be uploaded.
            role_arn:The Amazon Resource Name (ARN) of the role needed to call other services on your behalf. For example, arn:aws:iam::1234567890:role/service-role/AmazonSageMaker-ExecutionRole-20180111T151298.
            human_loop_request_source:Container for configuring the source of human task requests. Use to specify if Amazon Rekognition or Amazon Textract is used as an integration source.
            human_loop_activation_config:An object containing information about the events that trigger a human workflow.
            human_loop_config:An object containing information about the tasks the human reviewers will perform.
            tags:An array of key-value pairs that contain metadata to help you categorize and organize a flow definition. Each tag consists of a key and a value, both of which you define.
            session: Boto3 session.
            region: Region name.

        Returns:
            The FlowDefinition resource.

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

        logger.debug("Creating flow_definition resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "FlowDefinitionName": flow_definition_name,
            "HumanLoopRequestSource": human_loop_request_source,
            "HumanLoopActivationConfig": human_loop_activation_config,
            "HumanLoopConfig": human_loop_config,
            "OutputConfig": output_config,
            "RoleArn": role_arn,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="FlowDefinition", operation_input_args=operation_input_args
        )

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
        """
        Get a FlowDefinition resource

        Parameters:
            flow_definition_name:The name of the flow definition.
            session: Boto3 session.
            region: Region name.

        Returns:
            The FlowDefinition resource.

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
            "FlowDefinitionName": flow_definition_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_flow_definition(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeFlowDefinitionResponse")
        flow_definition = cls(**transformed_response)
        return flow_definition

    def refresh(self) -> Optional["FlowDefinition"]:
        """
        Refresh a FlowDefinition resource

        Returns:
            The FlowDefinition resource.

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
            "FlowDefinitionName": self.flow_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_flow_definition(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeFlowDefinitionResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a FlowDefinition resource


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
            "FlowDefinitionName": self.flow_definition_name,
        }
        client.delete_flow_definition(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Initializing", "Active", "Failed", "Deleting"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["FlowDefinition"]:
        """
        Wait for a FlowDefinition resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The FlowDefinition resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.flow_definition_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="FlowDefinition",
                    status=current_status,
                    reason=self.failure_reason,
                )

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
        """
        Get all FlowDefinition resources

        Parameters:
            creation_time_after:A filter that returns only flow definitions with a creation time greater than or equal to the specified timestamp.
            creation_time_before:A filter that returns only flow definitions that were created before the specified timestamp.
            sort_order:An optional value that specifies whether you want the results sorted in Ascending or Descending order.
            next_token:A token to resume pagination.
            max_results:The total number of items to return. If the total number of available items is more than the value specified in MaxResults, then a NextToken will be provided in the output that you can use to resume pagination.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed FlowDefinition resources.

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
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_flow_definitions",
            summaries_key="FlowDefinitionSummaries",
            summary_name="FlowDefinitionSummary",
            resource_cls=FlowDefinition,
            list_method_kwargs=operation_input_args,
        )


class Hub(Base):
    """
    Class representing resource Hub

    Attributes:
        hub_name:The name of the hub.
        hub_arn:The Amazon Resource Name (ARN) of the hub.
        hub_status:The status of the hub.
        creation_time:The date and time that the hub was created.
        last_modified_time:The date and time that the hub was last modified.
        hub_display_name:The display name of the hub.
        hub_description:A description of the hub.
        hub_search_keywords:The searchable keywords for the hub.
        s3_storage_config:The Amazon S3 storage configuration for the hub.
        failure_reason:The failure reason if importing hub content failed.

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
            if attribute == "name" or attribute == "hub_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "s3_storage_config": {"s3_output_path": {"type": "string"}}
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Hub", **kwargs
                ),
            )

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
        """
        Create a Hub resource

        Parameters:
            hub_name:The name of the hub to create.
            hub_description:A description of the hub.
            hub_display_name:The display name of the hub.
            hub_search_keywords:The searchable keywords for the hub.
            s3_storage_config:The Amazon S3 storage configuration for the hub.
            tags:Any tags to associate with the hub.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Hub resource.

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

        logger.debug("Creating hub resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "HubName": hub_name,
            "HubDescription": hub_description,
            "HubDisplayName": hub_display_name,
            "HubSearchKeywords": hub_search_keywords,
            "S3StorageConfig": s3_storage_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Hub", operation_input_args=operation_input_args
        )

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
        """
        Get a Hub resource

        Parameters:
            hub_name:The name of the hub to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Hub resource.

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
            "HubName": hub_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_hub(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeHubResponse")
        hub = cls(**transformed_response)
        return hub

    def refresh(self) -> Optional["Hub"]:
        """
        Refresh a Hub resource

        Returns:
            The Hub resource.

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
            "HubName": self.hub_name,
        }
        client = SageMakerClient().client
        response = client.describe_hub(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeHubResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        hub_description: Optional[str] = Unassigned(),
        hub_display_name: Optional[str] = Unassigned(),
        hub_search_keywords: Optional[List[str]] = Unassigned(),
    ) -> Optional["Hub"]:
        """
        Update a Hub resource


        Returns:
            The Hub resource.

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

        logger.debug("Updating hub resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "HubName": self.hub_name,
            "HubDescription": hub_description,
            "HubDisplayName": hub_display_name,
            "HubSearchKeywords": hub_search_keywords,
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
        """
        Delete a Hub resource


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
            "HubName": self.hub_name,
        }
        client.delete_hub(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "InService",
            "Creating",
            "Updating",
            "Deleting",
            "CreateFailed",
            "UpdateFailed",
            "DeleteFailed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Hub"]:
        """
        Wait for a Hub resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Hub resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.hub_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Hub", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all Hub resources

        Parameters:
            name_contains:Only list hubs with names that contain the specified string.
            creation_time_before:Only list hubs that were created before the time specified.
            creation_time_after:Only list hubs that were created after the time specified.
            last_modified_time_before:Only list hubs that were last modified before the time specified.
            last_modified_time_after:Only list hubs that were last modified after the time specified.
            sort_by:Sort hubs by either name or creation time.
            sort_order:Sort hubs by ascending or descending order.
            max_results:The maximum number of hubs to list.
            next_token:If the response to a previous ListHubs request was truncated, the response includes a NextToken. To retrieve the next set of hubs, use the token in the next request.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Hub resources.

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
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
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
            list_method="list_hubs",
            summaries_key="HubSummaries",
            summary_name="HubInfo",
            resource_cls=Hub,
            list_method_kwargs=operation_input_args,
        )


class HubContent(Base):
    """
    Class representing resource HubContent

    Attributes:
        hub_content_name:The name of the hub content.
        hub_content_arn:The Amazon Resource Name (ARN) of the hub content.
        hub_content_version:The version of the hub content.
        hub_content_type:The type of hub content.
        document_schema_version:The document schema version for the hub content.
        hub_name:The name of the hub that contains the content.
        hub_arn:The Amazon Resource Name (ARN) of the hub that contains the content.
        hub_content_document:The hub content document that describes information about the hub content such as type, associated containers, scripts, and more.
        hub_content_status:The status of the hub content.
        creation_time:The date and time that hub content was created.
        hub_content_display_name:The display name of the hub content.
        hub_content_description:A description of the hub content.
        hub_content_markdown:A string that provides a description of the hub content. This string can include links, tables, and standard markdown formating.
        hub_content_search_keywords:The searchable keywords for the hub content.
        hub_content_dependencies:The location of any dependencies that the hub content has, such as scripts, model artifacts, datasets, or notebooks.
        failure_reason:The failure reason if importing hub content failed.

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
            if attribute == "name" or attribute == "hub_content_name":
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
        """
        Get a HubContent resource

        Parameters:
            hub_name:The name of the hub that contains the content to describe.
            hub_content_type:The type of content in the hub.
            hub_content_name:The name of the content to describe.
            hub_content_version:The version of the content to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HubContent resource.

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
            "HubName": hub_name,
            "HubContentType": hub_content_type,
            "HubContentName": hub_content_name,
            "HubContentVersion": hub_content_version,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_hub_content(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeHubContentResponse")
        hub_content = cls(**transformed_response)
        return hub_content

    def refresh(self) -> Optional["HubContent"]:
        """
        Refresh a HubContent resource

        Returns:
            The HubContent resource.

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
            "HubName": self.hub_name,
            "HubContentType": self.hub_content_type,
            "HubContentName": self.hub_content_name,
            "HubContentVersion": self.hub_content_version,
        }
        client = SageMakerClient().client
        response = client.describe_hub_content(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeHubContentResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a HubContent resource


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
            "HubName": self.hub_name,
            "HubContentType": self.hub_content_type,
            "HubContentName": self.hub_content_name,
            "HubContentVersion": self.hub_content_version,
        }
        client.delete_hub_content(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Available", "Importing", "Deleting", "ImportFailed", "DeleteFailed"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["HubContent"]:
        """
        Wait for a HubContent resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The HubContent resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.hub_content_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="HubContent", status=current_status, reason=self.failure_reason
                )

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
        """
        Import a HubContent resource

        Parameters:
            hub_content_name:The name of the hub content to import.
            hub_content_type:The type of hub content to import.
            document_schema_version:The version of the hub content schema to import.
            hub_name:The name of the hub to import content into.
            hub_content_document:The hub content document that describes information about the hub content such as type, associated containers, scripts, and more.
            hub_content_version:The version of the hub content to import.
            hub_content_display_name:The display name of the hub content to import.
            hub_content_description:A description of the hub content to import.
            hub_content_markdown:A string that provides a description of the hub content. This string can include links, tables, and standard markdown formating.
            hub_content_search_keywords:The searchable keywords of the hub content.
            tags:Any tags associated with the hub content.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HubContent resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug(f"Importing hub_content resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "HubContentName": hub_content_name,
            "HubContentVersion": hub_content_version,
            "HubContentType": hub_content_type,
            "DocumentSchemaVersion": document_schema_version,
            "HubName": hub_name,
            "HubContentDisplayName": hub_content_display_name,
            "HubContentDescription": hub_content_description,
            "HubContentMarkdown": hub_content_markdown,
            "HubContentDocument": hub_content_document,
            "HubContentSearchKeywords": hub_content_search_keywords,
            "Tags": tags,
        }

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # import the resource
        response = client.import_hub_content(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            hub_name=hub_name,
            hub_content_type=hub_content_type,
            hub_content_name=hub_content_name,
            session=session,
            region=region,
        )

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
        """
        Get all HubContent resources

        Parameters:
            hub_name:The name of the hub to list the contents of.
            hub_content_type:The type of hub content to list.
            name_contains:Only list hub content if the name contains the specified string.
            max_schema_version:The upper bound of the hub content schema verion.
            creation_time_before:Only list hub content that was created before the time specified.
            creation_time_after:Only list hub content that was created after the time specified.
            sort_by:Sort hub content versions by either name or creation time.
            sort_order:Sort hubs by ascending or descending order.
            max_results:The maximum amount of hub content to list.
            next_token:If the response to a previous ListHubContents request was truncated, the response includes a NextToken. To retrieve the next set of hub content, use the token in the next request.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed HubContent resources.

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
            "HubName": hub_name,
            "HubContentType": hub_content_type,
            "NameContains": name_contains,
            "MaxSchemaVersion": max_schema_version,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
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
            list_method="list_hub_contents",
            summaries_key="HubContentSummaries",
            summary_name="HubContentInfo",
            resource_cls=HubContent,
            list_method_kwargs=operation_input_args,
        )

    def get_all_versions(
        self,
        min_version: Optional[str] = Unassigned(),
        max_schema_version: Optional[str] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["HubContent"]:

        operation_input_args = {
            "HubName": self.hub_name,
            "HubContentType": self.hub_content_type,
            "HubContentName": self.hub_content_name,
            "MinVersion": min_version,
            "MaxSchemaVersion": max_schema_version,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_hub_content_versions",
            summaries_key="HubContentSummaries",
            summary_name="HubContentInfo",
            resource_cls=HubContent,
            list_method_kwargs=operation_input_args,
        )


class HumanTaskUi(Base):
    """
    Class representing resource HumanTaskUi

    Attributes:
        human_task_ui_arn:The Amazon Resource Name (ARN) of the human task user interface (worker task template).
        human_task_ui_name:The name of the human task user interface (worker task template).
        creation_time:The timestamp when the human task user interface was created.
        ui_template:
        human_task_ui_status:The status of the human task user interface (worker task template). Valid values are listed below.

    """

    human_task_ui_name: str
    human_task_ui_arn: Optional[str] = Unassigned()
    human_task_ui_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    ui_template: Optional[UiTemplateInfo] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "human_task_ui_name":
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
        """
        Create a HumanTaskUi resource

        Parameters:
            human_task_ui_name:The name of the user interface you are creating.
            ui_template:
            tags:An array of key-value pairs that contain metadata to help you categorize and organize a human review workflow user interface. Each tag consists of a key and a value, both of which you define.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HumanTaskUi resource.

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

        logger.debug("Creating human_task_ui resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "HumanTaskUiName": human_task_ui_name,
            "UiTemplate": ui_template,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="HumanTaskUi", operation_input_args=operation_input_args
        )

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
        """
        Get a HumanTaskUi resource

        Parameters:
            human_task_ui_name:The name of the human task user interface (worker task template) you want information about.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HumanTaskUi resource.

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
            "HumanTaskUiName": human_task_ui_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_human_task_ui(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeHumanTaskUiResponse")
        human_task_ui = cls(**transformed_response)
        return human_task_ui

    def refresh(self) -> Optional["HumanTaskUi"]:
        """
        Refresh a HumanTaskUi resource

        Returns:
            The HumanTaskUi resource.

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
            "HumanTaskUiName": self.human_task_ui_name,
        }
        client = SageMakerClient().client
        response = client.describe_human_task_ui(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeHumanTaskUiResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a HumanTaskUi resource


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
            "HumanTaskUiName": self.human_task_ui_name,
        }
        client.delete_human_task_ui(**operation_input_args)

    def wait_for_status(
        self, status: Literal["Active", "Deleting"], poll: int = 5, timeout: Optional[int] = None
    ) -> Optional["HumanTaskUi"]:
        """
        Wait for a HumanTaskUi resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The HumanTaskUi resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
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
        """
        Get all HumanTaskUi resources

        Parameters:
            creation_time_after:A filter that returns only human task user interfaces with a creation time greater than or equal to the specified timestamp.
            creation_time_before:A filter that returns only human task user interfaces that were created before the specified timestamp.
            sort_order:An optional value that specifies whether you want the results sorted in Ascending or Descending order.
            next_token:A token to resume pagination.
            max_results:The total number of items to return. If the total number of available items is more than the value specified in MaxResults, then a NextToken will be provided in the output that you can use to resume pagination.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed HumanTaskUi resources.

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
            "SortOrder": sort_order,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_human_task_uis",
            summaries_key="HumanTaskUiSummaries",
            summary_name="HumanTaskUiSummary",
            resource_cls=HumanTaskUi,
            list_method_kwargs=operation_input_args,
        )


class HyperParameterTuningJob(Base):
    """
    Class representing resource HyperParameterTuningJob

    Attributes:
        hyper_parameter_tuning_job_name:The name of the hyperparameter tuning job.
        hyper_parameter_tuning_job_arn:The Amazon Resource Name (ARN) of the tuning job.
        hyper_parameter_tuning_job_config:The HyperParameterTuningJobConfig object that specifies the configuration of the tuning job.
        hyper_parameter_tuning_job_status:The status of the tuning job.
        creation_time:The date and time that the tuning job started.
        training_job_status_counters:The TrainingJobStatusCounters object that specifies the number of training jobs, categorized by status, that this tuning job launched.
        objective_status_counters:The ObjectiveStatusCounters object that specifies the number of training jobs, categorized by the status of their final objective metric, that this tuning job launched.
        training_job_definition:The HyperParameterTrainingJobDefinition object that specifies the definition of the training jobs that this tuning job launches.
        training_job_definitions:A list of the HyperParameterTrainingJobDefinition objects launched for this tuning job.
        hyper_parameter_tuning_end_time:The date and time that the tuning job ended.
        last_modified_time:The date and time that the status of the tuning job was modified.
        best_training_job:A TrainingJobSummary object that describes the training job that completed with the best current HyperParameterTuningJobObjective.
        overall_best_training_job:If the hyperparameter tuning job is an warm start tuning job with a WarmStartType of IDENTICAL_DATA_AND_ALGORITHM, this is the TrainingJobSummary for the training job with the best objective metric value of all training jobs launched by this tuning job and all parent jobs specified for the warm start tuning job.
        warm_start_config:The configuration for starting the hyperparameter parameter tuning job using one or more previous tuning jobs as a starting point. The results of previous tuning jobs are used to inform which combinations of hyperparameters to search over in the new tuning job.
        autotune:A flag to indicate if autotune is enabled for the hyperparameter tuning job.
        failure_reason:If the tuning job failed, the reason it failed.
        tuning_job_completion_details:Tuning job completion information returned as the response from a hyperparameter tuning job. This information tells if your tuning job has or has not converged. It also includes the number of training jobs that have not improved model performance as evaluated against the objective function.
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
            if attribute == "name" or attribute == "hyper_parameter_tuning_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "training_job_definition": {
                    "role_arn": {"type": "string"},
                    "output_data_config": {
                        "s3_output_path": {"type": "string"},
                        "kms_key_id": {"type": "string"},
                    },
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    },
                    "resource_config": {"volume_kms_key_id": {"type": "string"}},
                    "hyper_parameter_tuning_resource_config": {
                        "volume_kms_key_id": {"type": "string"}
                    },
                    "checkpoint_config": {"s3_uri": {"type": "string"}},
                }
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "HyperParameterTuningJob", **kwargs
                ),
            )

        return wrapper

    @classmethod
    @populate_inputs_decorator
    def create(
        cls,
        hyper_parameter_tuning_job_name: str,
        hyper_parameter_tuning_job_config: HyperParameterTuningJobConfig,
        training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned(),
        training_job_definitions: Optional[
            List[HyperParameterTrainingJobDefinition]
        ] = Unassigned(),
        warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        autotune: Optional[Autotune] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HyperParameterTuningJob"]:
        """
        Create a HyperParameterTuningJob resource

        Parameters:
            hyper_parameter_tuning_job_name:The name of the tuning job. This name is the prefix for the names of all training jobs that this tuning job launches. The name must be unique within the same Amazon Web Services account and Amazon Web Services Region. The name must have 1 to 32 characters. Valid characters are a-z, A-Z, 0-9, and : + = @ _ % - (hyphen). The name is not case sensitive.
            hyper_parameter_tuning_job_config:The HyperParameterTuningJobConfig object that describes the tuning job, including the search strategy, the objective metric used to evaluate training jobs, ranges of parameters to search, and resource limits for the tuning job. For more information, see How Hyperparameter Tuning Works.
            training_job_definition:The HyperParameterTrainingJobDefinition object that describes the training jobs that this tuning job launches, including static hyperparameters, input data configuration, output data configuration, resource configuration, and stopping condition.
            training_job_definitions:A list of the HyperParameterTrainingJobDefinition objects launched for this tuning job.
            warm_start_config:Specifies the configuration for starting the hyperparameter tuning job using one or more previous tuning jobs as a starting point. The results of previous tuning jobs are used to inform which combinations of hyperparameters to search over in the new tuning job. All training jobs launched by the new hyperparameter tuning job are evaluated by using the objective metric. If you specify IDENTICAL_DATA_AND_ALGORITHM as the WarmStartType value for the warm start configuration, the training job that performs the best in the new tuning job is compared to the best training jobs from the parent tuning jobs. From these, the training job that performs the best as measured by the objective metric is returned as the overall best training job.  All training jobs launched by parent hyperparameter tuning jobs and the new hyperparameter tuning jobs count against the limit of training jobs for the tuning job.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources. Tags that you specify for the tuning job are also added to all training jobs that the tuning job launches.
            autotune:Configures SageMaker Automatic model tuning (AMT) to automatically find optimal parameters for the following fields:    ParameterRanges: The names and ranges of parameters that a hyperparameter tuning job can optimize.    ResourceLimits: The maximum resources that can be used for a training job. These resources include the maximum number of training jobs, the maximum runtime of a tuning job, and the maximum number of training jobs to run at the same time.    TrainingJobEarlyStoppingType: A flag that specifies whether or not to use early stopping for training jobs launched by a hyperparameter tuning job.    RetryStrategy: The number of times to retry a training job.    Strategy: Specifies how hyperparameter tuning chooses the combinations of hyperparameter values to use for the training jobs that it launches.    ConvergenceDetected: A flag to indicate that Automatic model tuning (AMT) has detected model convergence.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HyperParameterTuningJob resource.

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

        logger.debug("Creating hyper_parameter_tuning_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "HyperParameterTuningJobName": hyper_parameter_tuning_job_name,
            "HyperParameterTuningJobConfig": hyper_parameter_tuning_job_config,
            "TrainingJobDefinition": training_job_definition,
            "TrainingJobDefinitions": training_job_definitions,
            "WarmStartConfig": warm_start_config,
            "Tags": tags,
            "Autotune": autotune,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="HyperParameterTuningJob", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_hyper_parameter_tuning_job(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            hyper_parameter_tuning_job_name=hyper_parameter_tuning_job_name,
            session=session,
            region=region,
        )

    @classmethod
    def get(
        cls,
        hyper_parameter_tuning_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["HyperParameterTuningJob"]:
        """
        Get a HyperParameterTuningJob resource

        Parameters:
            hyper_parameter_tuning_job_name:The name of the tuning job.
            session: Boto3 session.
            region: Region name.

        Returns:
            The HyperParameterTuningJob resource.

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
            "HyperParameterTuningJobName": hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeHyperParameterTuningJobResponse")
        hyper_parameter_tuning_job = cls(**transformed_response)
        return hyper_parameter_tuning_job

    def refresh(self) -> Optional["HyperParameterTuningJob"]:
        """
        Refresh a HyperParameterTuningJob resource

        Returns:
            The HyperParameterTuningJob resource.

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
            "HyperParameterTuningJobName": self.hyper_parameter_tuning_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_hyper_parameter_tuning_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeHyperParameterTuningJobResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a HyperParameterTuningJob resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "HyperParameterTuningJobName": self.hyper_parameter_tuning_job_name,
        }
        client.delete_hyper_parameter_tuning_job(**operation_input_args)

    def stop(self) -> None:
        """
        Stop a HyperParameterTuningJob resource


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
            "HyperParameterTuningJobName": self.hyper_parameter_tuning_job_name,
        }
        client.stop_hyper_parameter_tuning_job(**operation_input_args)

    def wait(
        self, poll: int = 5, timeout: Optional[int] = None
    ) -> Optional["HyperParameterTuningJob"]:
        """
        Wait for a HyperParameterTuningJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The HyperParameterTuningJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped", "DeleteFailed"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.hyper_parameter_tuning_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="HyperParameterTuningJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

                return self

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(
                    resouce_type="HyperParameterTuningJob", status=current_status
                )
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
        """
        Get all HyperParameterTuningJob resources

        Parameters:
            next_token:If the result of the previous ListHyperParameterTuningJobs request was truncated, the response includes a NextToken. To retrieve the next set of tuning jobs, use the token in the next request.
            max_results:The maximum number of tuning jobs to return. The default value is 10.
            sort_by:The field to sort results by. The default is Name.
            sort_order:The sort order for results. The default is Ascending.
            name_contains:A string in the tuning job name. This filter returns only tuning jobs whose name contains the specified string.
            creation_time_after:A filter that returns only tuning jobs that were created after the specified time.
            creation_time_before:A filter that returns only tuning jobs that were created before the specified time.
            last_modified_time_after:A filter that returns only tuning jobs that were modified after the specified time.
            last_modified_time_before:A filter that returns only tuning jobs that were modified before the specified time.
            status_equals:A filter that returns only tuning jobs with the specified status.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed HyperParameterTuningJob resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "StatusEquals": status_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_hyper_parameter_tuning_jobs",
            summaries_key="HyperParameterTuningJobSummaries",
            summary_name="HyperParameterTuningJobSummary",
            resource_cls=HyperParameterTuningJob,
            list_method_kwargs=operation_input_args,
        )

    def get_all_training_jobs(
        self,
        status_equals: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[HyperParameterTrainingJobSummary]:

        operation_input_args = {
            "HyperParameterTuningJobName": self.hyper_parameter_tuning_job_name,
            "StatusEquals": status_equals,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_training_jobs_for_hyper_parameter_tuning_job",
            summaries_key="TrainingJobSummaries",
            summary_name="HyperParameterTrainingJobSummary",
            resource_cls=HyperParameterTrainingJobSummary,
            list_method_kwargs=operation_input_args,
        )


class Image(Base):
    """
    Class representing resource Image

    Attributes:
        creation_time:When the image was created.
        description:The description of the image.
        display_name:The name of the image as displayed.
        failure_reason:When a create, update, or delete operation fails, the reason for the failure.
        image_arn:The ARN of the image.
        image_name:The name of the image.
        image_status:The status of the image.
        last_modified_time:When the image was last modified.
        role_arn:The ARN of the IAM role that enables Amazon SageMaker to perform tasks on your behalf.

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
            if attribute == "name" or attribute == "image_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {"role_arn": {"type": "string"}}
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Image", **kwargs
                ),
            )

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
        """
        Create a Image resource

        Parameters:
            image_name:The name of the image. Must be unique to your account.
            role_arn:The ARN of an IAM role that enables Amazon SageMaker to perform tasks on your behalf.
            description:The description of the image.
            display_name:The display name of the image. If not provided, ImageName is displayed.
            tags:A list of tags to apply to the image.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Image resource.

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

        logger.debug("Creating image resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "Description": description,
            "DisplayName": display_name,
            "ImageName": image_name,
            "RoleArn": role_arn,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Image", operation_input_args=operation_input_args
        )

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
        """
        Get a Image resource

        Parameters:
            image_name:The name of the image to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Image resource.

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
            "ImageName": image_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_image(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeImageResponse")
        image = cls(**transformed_response)
        return image

    def refresh(self) -> Optional["Image"]:
        """
        Refresh a Image resource

        Returns:
            The Image resource.

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
            "ImageName": self.image_name,
        }
        client = SageMakerClient().client
        response = client.describe_image(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeImageResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        delete_properties: Optional[List[str]] = Unassigned(),
        description: Optional[str] = Unassigned(),
        display_name: Optional[str] = Unassigned(),
        role_arn: Optional[str] = Unassigned(),
    ) -> Optional["Image"]:
        """
        Update a Image resource

        Parameters:
            delete_properties:A list of properties to delete. Only the Description and DisplayName properties can be deleted.

        Returns:
            The Image resource.

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

        logger.debug("Updating image resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "DeleteProperties": delete_properties,
            "Description": description,
            "DisplayName": display_name,
            "ImageName": self.image_name,
            "RoleArn": role_arn,
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
        """
        Delete a Image resource


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
            "ImageName": self.image_name,
        }
        client.delete_image(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "CREATING",
            "CREATED",
            "CREATE_FAILED",
            "UPDATING",
            "UPDATE_FAILED",
            "DELETING",
            "DELETE_FAILED",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Image"]:
        """
        Wait for a Image resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Image resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.image_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Image", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all Image resources

        Parameters:
            creation_time_after:A filter that returns only images created on or after the specified time.
            creation_time_before:A filter that returns only images created on or before the specified time.
            last_modified_time_after:A filter that returns only images modified on or after the specified time.
            last_modified_time_before:A filter that returns only images modified on or before the specified time.
            max_results:The maximum number of images to return in the response. The default value is 10.
            name_contains:A filter that returns only images whose name contains the specified string.
            next_token:If the previous call to ListImages didn't return the full set of images, the call returns a token for getting the next set of images.
            sort_by:The property used to sort results. The default value is CREATION_TIME.
            sort_order:The sort order. The default value is DESCENDING.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Image resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
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
            list_method="list_images",
            summaries_key="Images",
            summary_name="Image",
            resource_cls=Image,
            list_method_kwargs=operation_input_args,
        )


class ImageVersion(Base):
    """
    Class representing resource ImageVersion

    Attributes:
        base_image:The registry path of the container image on which this image version is based.
        container_image:The registry path of the container image that contains this image version.
        creation_time:When the version was created.
        failure_reason:When a create or delete operation fails, the reason for the failure.
        image_arn:The ARN of the image the version is based on.
        image_version_arn:The ARN of the version.
        image_version_status:The status of the version.
        last_modified_time:When the version was last modified.
        version:The version number.
        vendor_guidance:The stability of the image version specified by the maintainer.    NOT_PROVIDED: The maintainers did not provide a status for image version stability.    STABLE: The image version is stable.    TO_BE_ARCHIVED: The image version is set to be archived. Custom image versions that are set to be archived are automatically archived after three months.    ARCHIVED: The image version is archived. Archived image versions are not searchable and are no longer actively supported.
        job_type:Indicates SageMaker job type compatibility.    TRAINING: The image version is compatible with SageMaker training jobs.    INFERENCE: The image version is compatible with SageMaker inference jobs.    NOTEBOOK_KERNEL: The image version is compatible with SageMaker notebook kernels.
        m_l_framework:The machine learning framework vended in the image version.
        programming_lang:The supported programming language and its version.
        processor:Indicates CPU or GPU compatibility.    CPU: The image version is compatible with CPU.    GPU: The image version is compatible with GPU.
        horovod:Indicates Horovod compatibility.
        release_notes:The maintainer description of the image version.

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
            if attribute == "name" or attribute == "image_version_name":
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
        """
        Create a ImageVersion resource

        Parameters:
            base_image:The registry path of the container image to use as the starting point for this version. The path is an Amazon ECR URI in the following format:  &lt;acct-id&gt;.dkr.ecr.&lt;region&gt;.amazonaws.com/&lt;repo-name[:tag] or [@digest]&gt;
            client_token:A unique ID. If not specified, the Amazon Web Services CLI and Amazon Web Services SDKs, such as the SDK for Python (Boto3), add a unique value to the call.
            image_name:The ImageName of the Image to create a version of.
            aliases:A list of aliases created with the image version.
            vendor_guidance:The stability of the image version, specified by the maintainer.    NOT_PROVIDED: The maintainers did not provide a status for image version stability.    STABLE: The image version is stable.    TO_BE_ARCHIVED: The image version is set to be archived. Custom image versions that are set to be archived are automatically archived after three months.    ARCHIVED: The image version is archived. Archived image versions are not searchable and are no longer actively supported.
            job_type:Indicates SageMaker job type compatibility.    TRAINING: The image version is compatible with SageMaker training jobs.    INFERENCE: The image version is compatible with SageMaker inference jobs.    NOTEBOOK_KERNEL: The image version is compatible with SageMaker notebook kernels.
            m_l_framework:The machine learning framework vended in the image version.
            programming_lang:The supported programming language and its version.
            processor:Indicates CPU or GPU compatibility.    CPU: The image version is compatible with CPU.    GPU: The image version is compatible with GPU.
            horovod:Indicates Horovod compatibility.
            release_notes:The maintainer description of the image version.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ImageVersion resource.

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
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating image_version resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "BaseImage": base_image,
            "ClientToken": client_token,
            "ImageName": image_name,
            "Aliases": aliases,
            "VendorGuidance": vendor_guidance,
            "JobType": job_type,
            "MLFramework": m_l_framework,
            "ProgrammingLang": programming_lang,
            "Processor": processor,
            "Horovod": horovod,
            "ReleaseNotes": release_notes,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ImageVersion", operation_input_args=operation_input_args
        )

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
        """
        Get a ImageVersion resource

        Parameters:
            image_name:The name of the image.
            version:The version of the image. If not specified, the latest version is described.
            alias:The alias of the image version.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ImageVersion resource.

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
            "ImageName": image_name,
            "Version": version,
            "Alias": alias,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_image_version(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeImageVersionResponse")
        image_version = cls(**transformed_response)
        return image_version

    def refresh(self) -> Optional["ImageVersion"]:
        """
        Refresh a ImageVersion resource

        Returns:
            The ImageVersion resource.

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
            "ImageName": self.image_name,
            "Version": self.version,
            "Alias": self.alias,
        }
        client = SageMakerClient().client
        response = client.describe_image_version(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeImageVersionResponse", self)
        return self

    def update(
        self,
        image_name: str,
        alias: Optional[str] = Unassigned(),
        version: Optional[int] = Unassigned(),
        aliases_to_add: Optional[List[str]] = Unassigned(),
        aliases_to_delete: Optional[List[str]] = Unassigned(),
        vendor_guidance: Optional[str] = Unassigned(),
        job_type: Optional[str] = Unassigned(),
        m_l_framework: Optional[str] = Unassigned(),
        programming_lang: Optional[str] = Unassigned(),
        processor: Optional[str] = Unassigned(),
        horovod: Optional[bool] = Unassigned(),
        release_notes: Optional[str] = Unassigned(),
    ) -> Optional["ImageVersion"]:
        """
        Update a ImageVersion resource

        Parameters:
            image_name:The name of the image.
            alias:The alias of the image version.
            aliases_to_add:A list of aliases to add.
            aliases_to_delete:A list of aliases to delete.

        Returns:
            The ImageVersion resource.

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

        logger.debug("Updating image_version resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ImageName": image_name,
            "Alias": alias,
            "Version": version,
            "AliasesToAdd": aliases_to_add,
            "AliasesToDelete": aliases_to_delete,
            "VendorGuidance": vendor_guidance,
            "JobType": job_type,
            "MLFramework": m_l_framework,
            "ProgrammingLang": programming_lang,
            "Processor": processor,
            "Horovod": horovod,
            "ReleaseNotes": release_notes,
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
        """
        Delete a ImageVersion resource


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
            "ImageName": self.image_name,
            "Version": self.version,
            "Alias": self.alias,
        }
        client.delete_image_version(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["CREATING", "CREATED", "CREATE_FAILED", "DELETING", "DELETE_FAILED"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["ImageVersion"]:
        """
        Wait for a ImageVersion resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ImageVersion resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.image_version_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="ImageVersion", status=current_status, reason=self.failure_reason
                )

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(resouce_type="ImageVersion", status=current_status)
            print("-", end="")
            time.sleep(poll)


class InferenceComponent(Base):
    """
    Class representing resource InferenceComponent

    Attributes:
        inference_component_name:The name of the inference component.
        inference_component_arn:The Amazon Resource Name (ARN) of the inference component.
        endpoint_name:The name of the endpoint that hosts the inference component.
        endpoint_arn:The Amazon Resource Name (ARN) of the endpoint that hosts the inference component.
        creation_time:The time when the inference component was created.
        last_modified_time:The time when the inference component was last updated.
        variant_name:The name of the production variant that hosts the inference component.
        failure_reason:If the inference component status is Failed, the reason for the failure.
        specification:Details about the resources that are deployed with this inference component.
        runtime_config:Details about the runtime settings for the model that is deployed with the inference component.
        inference_component_status:The status of the inference component.

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
            if attribute == "name" or attribute == "inference_component_name":
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
        """
        Create a InferenceComponent resource

        Parameters:
            inference_component_name:A unique name to assign to the inference component.
            endpoint_name:The name of an existing endpoint where you host the inference component.
            variant_name:The name of an existing production variant where you host the inference component.
            specification:Details about the resources to deploy with this inference component, including the model, container, and compute resources.
            runtime_config:Runtime settings for a model that is deployed with an inference component.
            tags:A list of key-value pairs associated with the model. For more information, see Tagging Amazon Web Services resources in the Amazon Web Services General Reference.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceComponent resource.

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

        logger.debug("Creating inference_component resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "InferenceComponentName": inference_component_name,
            "EndpointName": endpoint_name,
            "VariantName": variant_name,
            "Specification": specification,
            "RuntimeConfig": runtime_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="InferenceComponent", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_inference_component(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            inference_component_name=inference_component_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        inference_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["InferenceComponent"]:
        """
        Get a InferenceComponent resource

        Parameters:
            inference_component_name:The name of the inference component.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceComponent resource.

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
            "InferenceComponentName": inference_component_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_inference_component(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeInferenceComponentOutput")
        inference_component = cls(**transformed_response)
        return inference_component

    def refresh(self) -> Optional["InferenceComponent"]:
        """
        Refresh a InferenceComponent resource

        Returns:
            The InferenceComponent resource.

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
            "InferenceComponentName": self.inference_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_component(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeInferenceComponentOutput", self)
        return self

    def update(
        self,
        specification: Optional[InferenceComponentSpecification] = Unassigned(),
        runtime_config: Optional[InferenceComponentRuntimeConfig] = Unassigned(),
    ) -> Optional["InferenceComponent"]:
        """
        Update a InferenceComponent resource


        Returns:
            The InferenceComponent resource.

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
        """

        logger.debug("Updating inference_component resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "InferenceComponentName": self.inference_component_name,
            "Specification": specification,
            "RuntimeConfig": runtime_config,
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
        """
        Delete a InferenceComponent resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "InferenceComponentName": self.inference_component_name,
        }
        client.delete_inference_component(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["InService", "Creating", "Updating", "Failed", "Deleting"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["InferenceComponent"]:
        """
        Wait for a InferenceComponent resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The InferenceComponent resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.inference_component_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="InferenceComponent",
                    status=current_status,
                    reason=self.failure_reason,
                )

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
        """
        Get all InferenceComponent resources

        Parameters:
            sort_by:The field by which to sort the inference components in the response. The default is CreationTime.
            sort_order:The sort order for results. The default is Descending.
            next_token:A token that you use to get the next set of results following a truncated response. If the response to the previous request was truncated, that response provides the value for this token.
            max_results:The maximum number of inference components to return in the response. This value defaults to 10.
            name_contains:Filters the results to only those inference components with a name that contains the specified string.
            creation_time_before:Filters the results to only those inference components that were created before the specified time.
            creation_time_after:Filters the results to only those inference components that were created after the specified time.
            last_modified_time_before:Filters the results to only those inference components that were updated before the specified time.
            last_modified_time_after:Filters the results to only those inference components that were updated after the specified time.
            status_equals:Filters the results to only those inference components with the specified status.
            endpoint_name_equals:An endpoint name to filter the listed inference components. The response includes only those inference components that are hosted at the specified endpoint.
            variant_name_equals:A production variant name to filter the listed inference components. The response includes only those inference components that are hosted at the specified variant.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed InferenceComponent resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "StatusEquals": status_equals,
            "EndpointNameEquals": endpoint_name_equals,
            "VariantNameEquals": variant_name_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_inference_components",
            summaries_key="InferenceComponents",
            summary_name="InferenceComponentSummary",
            resource_cls=InferenceComponent,
            list_method_kwargs=operation_input_args,
        )

    def update_runtime_configs(
        self,
        desired_runtime_config: InferenceComponentRuntimeConfig,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "InferenceComponentName": self.inference_component_name,
            "DesiredRuntimeConfig": desired_runtime_config,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling update_inference_component_runtime_config API")
        response = client.update_inference_component_runtime_config(**operation_input_args)
        logger.debug(f"Response: {response}")


class InferenceExperiment(Base):
    """
    Class representing resource InferenceExperiment

    Attributes:
        arn:The ARN of the inference experiment being described.
        name:The name of the inference experiment.
        type:The type of the inference experiment.
        status: The status of the inference experiment. The following are the possible statuses for an inference experiment:     Creating - Amazon SageMaker is creating your experiment.     Created - Amazon SageMaker has finished the creation of your experiment and will begin the experiment at the scheduled time.     Updating - When you make changes to your experiment, your experiment shows as updating.     Starting - Amazon SageMaker is beginning your experiment.     Running - Your experiment is in progress.     Stopping - Amazon SageMaker is stopping your experiment.     Completed - Your experiment has completed.     Cancelled - When you conclude your experiment early using the StopInferenceExperiment API, or if any operation fails with an unexpected error, it shows as cancelled.
        endpoint_metadata:The metadata of the endpoint on which the inference experiment ran.
        model_variants: An array of ModelVariantConfigSummary objects. There is one for each variant in the inference experiment. Each ModelVariantConfigSummary object in the array describes the infrastructure configuration for deploying the corresponding variant.
        schedule:The duration for which the inference experiment ran or will run.
        status_reason: The error message or client-specified Reason from the StopInferenceExperiment API, that explains the status of the inference experiment.
        description:The description of the inference experiment.
        creation_time:The timestamp at which you created the inference experiment.
        completion_time: The timestamp at which the inference experiment was completed.
        last_modified_time:The timestamp at which you last modified the inference experiment.
        role_arn: The ARN of the IAM role that Amazon SageMaker can assume to access model artifacts and container images, and manage Amazon SageMaker Inference endpoints for model deployment.
        data_storage_config:The Amazon S3 location and configuration for storing inference request and response data.
        shadow_mode_config: The configuration of ShadowMode inference experiment type, which shows the production variant that takes all the inference requests, and the shadow variant to which Amazon SageMaker replicates a percentage of the inference requests. For the shadow variant it also shows the percentage of requests that Amazon SageMaker replicates.
        kms_key: The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the endpoint. For more information, see CreateInferenceExperiment.

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
            if attribute == "name" or attribute == "inference_experiment_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "role_arn": {"type": "string"},
                "data_storage_config": {"kms_key": {"type": "string"}},
                "kms_key": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "InferenceExperiment", **kwargs
                ),
            )

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
        """
        Create a InferenceExperiment resource

        Parameters:
            name:The name for the inference experiment.
            type: The type of the inference experiment that you want to run. The following types of experiments are possible:     ShadowMode: You can use this type to validate a shadow variant. For more information, see Shadow tests.
            role_arn: The ARN of the IAM role that Amazon SageMaker can assume to access model artifacts and container images, and manage Amazon SageMaker Inference endpoints for model deployment.
            endpoint_name: The name of the Amazon SageMaker endpoint on which you want to run the inference experiment.
            model_variants: An array of ModelVariantConfig objects. There is one for each variant in the inference experiment. Each ModelVariantConfig object in the array describes the infrastructure configuration for the corresponding variant.
            shadow_mode_config: The configuration of ShadowMode inference experiment type. Use this field to specify a production variant which takes all the inference requests, and a shadow variant to which Amazon SageMaker replicates a percentage of the inference requests. For the shadow variant also specify the percentage of requests that Amazon SageMaker replicates.
            schedule: The duration for which you want the inference experiment to run. If you don't specify this field, the experiment automatically starts immediately upon creation and concludes after 7 days.
            description:A description for the inference experiment.
            data_storage_config: The Amazon S3 location and configuration for storing inference request and response data.   This is an optional parameter that you can use for data capture. For more information, see Capture data.
            kms_key: The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the endpoint. The KmsKey can be any of the following formats:    KMS key ID  "1234abcd-12ab-34cd-56ef-1234567890ab"    Amazon Resource Name (ARN) of a KMS key  "arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"    KMS key Alias  "alias/ExampleAlias"    Amazon Resource Name (ARN) of a KMS key Alias  "arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias"     If you use a KMS key ID or an alias of your KMS key, the Amazon SageMaker execution role must include permissions to call kms:Encrypt. If you don't provide a KMS key ID, Amazon SageMaker uses the default KMS key for Amazon S3 for your role's account. Amazon SageMaker uses server-side encryption with KMS managed keys for OutputDataConfig. If you use a bucket policy with an s3:PutObject permission that only allows objects with server-side encryption, set the condition key of s3:x-amz-server-side-encryption to "aws:kms". For more information, see KMS managed Encryption Keys in the Amazon Simple Storage Service Developer Guide.   The KMS key policy must grant permission to the IAM role that you specify in your CreateEndpoint and UpdateEndpoint requests. For more information, see Using Key Policies in Amazon Web Services KMS in the Amazon Web Services Key Management Service Developer Guide.
            tags: Array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging your Amazon Web Services Resources.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceExperiment resource.

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

        logger.debug("Creating inference_experiment resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "Name": name,
            "Type": type,
            "Schedule": schedule,
            "Description": description,
            "RoleArn": role_arn,
            "EndpointName": endpoint_name,
            "ModelVariants": model_variants,
            "DataStorageConfig": data_storage_config,
            "ShadowModeConfig": shadow_mode_config,
            "KmsKey": kms_key,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="InferenceExperiment", operation_input_args=operation_input_args
        )

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
        """
        Get a InferenceExperiment resource

        Parameters:
            name:The name of the inference experiment to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceExperiment resource.

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
            "Name": name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_inference_experiment(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeInferenceExperimentResponse")
        inference_experiment = cls(**transformed_response)
        return inference_experiment

    def refresh(self) -> Optional["InferenceExperiment"]:
        """
        Refresh a InferenceExperiment resource

        Returns:
            The InferenceExperiment resource.

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
            "Name": self.name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_experiment(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeInferenceExperimentResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        schedule: Optional[InferenceExperimentSchedule] = Unassigned(),
        description: Optional[str] = Unassigned(),
        model_variants: Optional[List[ModelVariantConfig]] = Unassigned(),
        data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned(),
        shadow_mode_config: Optional[ShadowModeConfig] = Unassigned(),
    ) -> Optional["InferenceExperiment"]:
        """
        Update a InferenceExperiment resource


        Returns:
            The InferenceExperiment resource.

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

        logger.debug("Updating inference_experiment resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "Name": self.name,
            "Schedule": schedule,
            "Description": description,
            "ModelVariants": model_variants,
            "DataStorageConfig": data_storage_config,
            "ShadowModeConfig": shadow_mode_config,
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
        """
        Delete a InferenceExperiment resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "Name": self.name,
        }
        client.delete_inference_experiment(**operation_input_args)

    def stop(self) -> None:
        """
        Stop a InferenceExperiment resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "Name": self.name,
            "ModelVariantActions": self.model_variant_actions,
            "DesiredModelVariants": self.desired_model_variants,
            "DesiredState": self.desired_state,
            "Reason": self.reason,
        }
        client.stop_inference_experiment(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Creating",
            "Created",
            "Updating",
            "Running",
            "Starting",
            "Stopping",
            "Completed",
            "Cancelled",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["InferenceExperiment"]:
        """
        Wait for a InferenceExperiment resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The InferenceExperiment resource.

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

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(
                    resouce_type="InferenceExperiment", status=current_status
                )
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
        """
        Get all InferenceExperiment resources

        Parameters:
            name_contains:Selects inference experiments whose names contain this name.
            type: Selects inference experiments of this type. For the possible types of inference experiments, see CreateInferenceExperiment.
            status_equals: Selects inference experiments which are in this status. For the possible statuses, see DescribeInferenceExperiment.
            creation_time_after:Selects inference experiments which were created after this timestamp.
            creation_time_before:Selects inference experiments which were created before this timestamp.
            last_modified_time_after:Selects inference experiments which were last modified after this timestamp.
            last_modified_time_before:Selects inference experiments which were last modified before this timestamp.
            sort_by:The column by which to sort the listed inference experiments.
            sort_order:The direction of sorting (ascending or descending).
            next_token: The response from the last list when returning a list large enough to need tokening.
            max_results:The maximum number of results to select.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed InferenceExperiment resources.

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
            "Type": type,
            "StatusEquals": status_equals,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
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
            list_method="list_inference_experiments",
            summaries_key="InferenceExperiments",
            summary_name="InferenceExperimentSummary",
            resource_cls=InferenceExperiment,
            list_method_kwargs=operation_input_args,
        )


class InferenceRecommendationsJob(Base):
    """
    Class representing resource InferenceRecommendationsJob

    Attributes:
        job_name:The name of the job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
        job_type:The job type that you provided when you initiated the job.
        job_arn:The Amazon Resource Name (ARN) of the job.
        role_arn:The Amazon Resource Name (ARN) of the Amazon Web Services Identity and Access Management (IAM) role you provided when you initiated the job.
        status:The status of the job.
        creation_time:A timestamp that shows when the job was created.
        last_modified_time:A timestamp that shows when the job was last modified.
        input_config:Returns information about the versioned model package Amazon Resource Name (ARN), the traffic pattern, and endpoint configurations you provided when you initiated the job.
        job_description:The job description that you provided when you initiated the job.
        completion_time:A timestamp that shows when the job completed.
        failure_reason:If the job fails, provides information why the job failed.
        stopping_conditions:The stopping conditions that you provided when you initiated the job.
        inference_recommendations:The recommendations made by Inference Recommender.
        endpoint_performances:The performance results from running an Inference Recommender job on an existing endpoint.

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
            if attribute == "name" or attribute == "inference_recommendations_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "role_arn": {"type": "string"},
                "input_config": {
                    "volume_kms_key_id": {"type": "string"},
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    },
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "InferenceRecommendationsJob", **kwargs
                ),
            )

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
        """
        Create a InferenceRecommendationsJob resource

        Parameters:
            job_name:A name for the recommendation job. The name must be unique within the Amazon Web Services Region and within your Amazon Web Services account. The job name is passed down to the resources created by the recommendation job. The names of resources (such as the model, endpoint configuration, endpoint, and compilation) that are prefixed with the job name are truncated at 40 characters.
            job_type:Defines the type of recommendation job. Specify Default to initiate an instance recommendation and Advanced to initiate a load test. If left unspecified, Amazon SageMaker Inference Recommender will run an instance recommendation (DEFAULT) job.
            role_arn:The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to perform tasks on your behalf.
            input_config:Provides information about the versioned model package Amazon Resource Name (ARN), the traffic pattern, and endpoint configurations.
            job_description:Description of the recommendation job.
            stopping_conditions:A set of conditions for stopping a recommendation job. If any of the conditions are met, the job is automatically stopped.
            output_config:Provides information about the output artifacts and the KMS key to use for Amazon S3 server-side encryption.
            tags:The metadata that you apply to Amazon Web Services resources to help you categorize and organize them. Each tag consists of a key and a value, both of which you define. For more information, see Tagging Amazon Web Services Resources in the Amazon Web Services General Reference.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceRecommendationsJob resource.

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

        logger.debug("Creating inference_recommendations_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "JobName": job_name,
            "JobType": job_type,
            "RoleArn": role_arn,
            "InputConfig": input_config,
            "JobDescription": job_description,
            "StoppingConditions": stopping_conditions,
            "OutputConfig": output_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="InferenceRecommendationsJob", operation_input_args=operation_input_args
        )

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
        """
        Get a InferenceRecommendationsJob resource

        Parameters:
            job_name:The name of the job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            session: Boto3 session.
            region: Region name.

        Returns:
            The InferenceRecommendationsJob resource.

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
            "JobName": job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_inference_recommendations_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeInferenceRecommendationsJobResponse")
        inference_recommendations_job = cls(**transformed_response)
        return inference_recommendations_job

    def refresh(self) -> Optional["InferenceRecommendationsJob"]:
        """
        Refresh a InferenceRecommendationsJob resource

        Returns:
            The InferenceRecommendationsJob resource.

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
            "JobName": self.job_name,
        }
        client = SageMakerClient().client
        response = client.describe_inference_recommendations_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeInferenceRecommendationsJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a InferenceRecommendationsJob resource


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
            "JobName": self.job_name,
        }
        client.stop_inference_recommendations_job(**operation_input_args)

    def wait(
        self, poll: int = 5, timeout: Optional[int] = None
    ) -> Optional["InferenceRecommendationsJob"]:
        """
        Wait for a InferenceRecommendationsJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The InferenceRecommendationsJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["COMPLETED", "FAILED", "STOPPED", "DELETED"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="InferenceRecommendationsJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

                return self

            if timeout is not None and time.time() - start_time >= timeout:
                raise TimeoutExceededError(
                    resouce_type="InferenceRecommendationsJob", status=current_status
                )
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
        """
        Get all InferenceRecommendationsJob resources

        Parameters:
            creation_time_after:A filter that returns only jobs created after the specified time (timestamp).
            creation_time_before:A filter that returns only jobs created before the specified time (timestamp).
            last_modified_time_after:A filter that returns only jobs that were last modified after the specified time (timestamp).
            last_modified_time_before:A filter that returns only jobs that were last modified before the specified time (timestamp).
            name_contains:A string in the job name. This filter returns only recommendations whose name contains the specified string.
            status_equals:A filter that retrieves only inference recommendations jobs with a specific status.
            sort_by:The parameter by which to sort the results.
            sort_order:The sort order for the results.
            next_token:If the response to a previous ListInferenceRecommendationsJobsRequest request was truncated, the response includes a NextToken. To retrieve the next set of recommendations, use the token in the next request.
            max_results:The maximum number of recommendations to return in the response.
            model_name_equals:A filter that returns only jobs that were created for this model.
            model_package_version_arn_equals:A filter that returns only jobs that were created for this versioned model package.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed InferenceRecommendationsJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "ModelNameEquals": model_name_equals,
            "ModelPackageVersionArnEquals": model_package_version_arn_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_inference_recommendations_jobs",
            summaries_key="InferenceRecommendationsJobs",
            summary_name="InferenceRecommendationsJob",
            resource_cls=InferenceRecommendationsJob,
            list_method_kwargs=operation_input_args,
        )

    def get_all_steps(
        self,
        step_type: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[InferenceRecommendationsJobStep]:

        operation_input_args = {
            "JobName": self.job_name,
            "Status": self.status,
            "StepType": step_type,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_inference_recommendations_job_steps",
            summaries_key="Steps",
            summary_name="InferenceRecommendationsJobStep",
            resource_cls=InferenceRecommendationsJobStep,
            list_method_kwargs=operation_input_args,
        )


class LabelingJob(Base):
    """
    Class representing resource LabelingJob

    Attributes:
        labeling_job_status:The processing status of the labeling job.
        label_counters:Provides a breakdown of the number of data objects labeled by humans, the number of objects labeled by machine, the number of objects than couldn't be labeled, and the total number of objects labeled.
        creation_time:The date and time that the labeling job was created.
        last_modified_time:The date and time that the labeling job was last updated.
        job_reference_code:A unique identifier for work done as part of a labeling job.
        labeling_job_name:The name assigned to the labeling job when it was created.
        labeling_job_arn:The Amazon Resource Name (ARN) of the labeling job.
        input_config:Input configuration information for the labeling job, such as the Amazon S3 location of the data objects and the location of the manifest file that describes the data objects.
        output_config:The location of the job's output data and the Amazon Web Services Key Management Service key ID for the key used to encrypt the output data, if any.
        role_arn:The Amazon Resource Name (ARN) that SageMaker assumes to perform tasks on your behalf during data labeling.
        human_task_config:Configuration information required for human workers to complete a labeling task.
        failure_reason:If the job failed, the reason that it failed.
        label_attribute_name:The attribute used as the label in the output manifest file.
        label_category_config_s3_uri:The S3 location of the JSON file that defines the categories used to label data objects. Please note the following label-category limits:   Semantic segmentation labeling jobs using automated labeling: 20 labels   Box bounding labeling jobs (all): 10 labels   The file is a JSON structure in the following format:  {    "document-version": "2018-11-28"    "labels": [    {    "label": "label 1"    },    {    "label": "label 2"    },    ...    {    "label": "label n"    }    ]   }
        stopping_conditions:A set of conditions for stopping a labeling job. If any of the conditions are met, the job is automatically stopped.
        labeling_job_algorithms_config:Configuration information for automated data labeling.
        tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
        labeling_job_output:The location of the output produced by the labeling job.

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
            if attribute == "name" or attribute == "labeling_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "input_config": {
                    "data_source": {"s3_data_source": {"manifest_s3_uri": {"type": "string"}}}
                },
                "output_config": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "role_arn": {"type": "string"},
                "human_task_config": {"ui_config": {"ui_template_s3_uri": {"type": "string"}}},
                "label_category_config_s3_uri": {"type": "string"},
                "labeling_job_algorithms_config": {
                    "labeling_job_resource_config": {
                        "volume_kms_key_id": {"type": "string"},
                        "vpc_config": {
                            "security_group_ids": {"type": "array", "items": {"type": "string"}},
                            "subnets": {"type": "array", "items": {"type": "string"}},
                        },
                    }
                },
                "labeling_job_output": {"output_dataset_s3_uri": {"type": "string"}},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "LabelingJob", **kwargs
                ),
            )

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
        """
        Create a LabelingJob resource

        Parameters:
            labeling_job_name:The name of the labeling job. This name is used to identify the job in a list of labeling jobs. Labeling job names must be unique within an Amazon Web Services account and region. LabelingJobName is not case sensitive. For example, Example-job and example-job are considered the same labeling job name by Ground Truth.
            label_attribute_name:The attribute name to use for the label in the output manifest file. This is the key for the key/value pair formed with the label that a worker assigns to the object. The LabelAttributeName must meet the following requirements.   The name can't end with "-metadata".    If you are using one of the following built-in task types, the attribute name must end with "-ref". If the task type you are using is not listed below, the attribute name must not end with "-ref".   Image semantic segmentation (SemanticSegmentation), and adjustment (AdjustmentSemanticSegmentation) and verification (VerificationSemanticSegmentation) labeling jobs for this task type.   Video frame object detection (VideoObjectDetection), and adjustment and verification (AdjustmentVideoObjectDetection) labeling jobs for this task type.   Video frame object tracking (VideoObjectTracking), and adjustment and verification (AdjustmentVideoObjectTracking) labeling jobs for this task type.   3D point cloud semantic segmentation (3DPointCloudSemanticSegmentation), and adjustment and verification (Adjustment3DPointCloudSemanticSegmentation) labeling jobs for this task type.    3D point cloud object tracking (3DPointCloudObjectTracking), and adjustment and verification (Adjustment3DPointCloudObjectTracking) labeling jobs for this task type.        If you are creating an adjustment or verification labeling job, you must use a different LabelAttributeName than the one used in the original labeling job. The original labeling job is the Ground Truth labeling job that produced the labels that you want verified or adjusted. To learn more about adjustment and verification labeling jobs, see Verify and Adjust Labels.
            input_config:Input data for the labeling job, such as the Amazon S3 location of the data objects and the location of the manifest file that describes the data objects. You must specify at least one of the following: S3DataSource or SnsDataSource.    Use SnsDataSource to specify an SNS input topic for a streaming labeling job. If you do not specify and SNS input topic ARN, Ground Truth will create a one-time labeling job that stops after all data objects in the input manifest file have been labeled.   Use S3DataSource to specify an input manifest file for both streaming and one-time labeling jobs. Adding an S3DataSource is optional if you use SnsDataSource to create a streaming labeling job.   If you use the Amazon Mechanical Turk workforce, your input data should not include confidential information, personal information or protected health information. Use ContentClassifiers to specify that your data is free of personally identifiable information and adult content.
            output_config:The location of the output data and the Amazon Web Services Key Management Service key ID for the key used to encrypt the output data, if any.
            role_arn:The Amazon Resource Number (ARN) that Amazon SageMaker assumes to perform tasks on your behalf during data labeling. You must grant this role the necessary permissions so that Amazon SageMaker can successfully complete data labeling.
            human_task_config:Configures the labeling task and how it is presented to workers; including, but not limited to price, keywords, and batch size (task count).
            label_category_config_s3_uri:The S3 URI of the file, referred to as a label category configuration file, that defines the categories used to label the data objects. For 3D point cloud and video frame task types, you can add label category attributes and frame attributes to your label category configuration file. To learn how, see Create a Labeling Category Configuration File for 3D Point Cloud Labeling Jobs.  For named entity recognition jobs, in addition to "labels", you must provide worker instructions in the label category configuration file using the "instructions" parameter: "instructions": {"shortInstruction":"&lt;h1&gt;Add header&lt;/h1&gt;&lt;p&gt;Add Instructions&lt;/p&gt;", "fullInstruction":"&lt;p&gt;Add additional instructions.&lt;/p&gt;"}. For details and an example, see Create a Named Entity Recognition Labeling Job (API) . For all other built-in task types and custom tasks, your label category configuration file must be a JSON file in the following format. Identify the labels you want to use by replacing label_1, label_2,...,label_n with your label categories.  {    "document-version": "2018-11-28",   "labels": [{"label": "label_1"},{"label": "label_2"},...{"label": "label_n"}]   }  Note the following about the label category configuration file:   For image classification and text classification (single and multi-label) you must specify at least two label categories. For all other task types, the minimum number of label categories required is one.    Each label category must be unique, you cannot specify duplicate label categories.   If you create a 3D point cloud or video frame adjustment or verification labeling job, you must include auditLabelAttributeName in the label category configuration. Use this parameter to enter the  LabelAttributeName  of the labeling job you want to adjust or verify annotations of.
            stopping_conditions:A set of conditions for stopping the labeling job. If any of the conditions are met, the job is automatically stopped. You can use these conditions to control the cost of data labeling.
            labeling_job_algorithms_config:Configures the information required to perform automated data labeling.
            tags:An array of key/value pairs. For more information, see Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The LabelingJob resource.

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

        logger.debug("Creating labeling_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "LabelingJobName": labeling_job_name,
            "LabelAttributeName": label_attribute_name,
            "InputConfig": input_config,
            "OutputConfig": output_config,
            "RoleArn": role_arn,
            "LabelCategoryConfigS3Uri": label_category_config_s3_uri,
            "StoppingConditions": stopping_conditions,
            "LabelingJobAlgorithmsConfig": labeling_job_algorithms_config,
            "HumanTaskConfig": human_task_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="LabelingJob", operation_input_args=operation_input_args
        )

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
        """
        Get a LabelingJob resource

        Parameters:
            labeling_job_name:The name of the labeling job to return information for.
            session: Boto3 session.
            region: Region name.

        Returns:
            The LabelingJob resource.

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
            "LabelingJobName": labeling_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_labeling_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeLabelingJobResponse")
        labeling_job = cls(**transformed_response)
        return labeling_job

    def refresh(self) -> Optional["LabelingJob"]:
        """
        Refresh a LabelingJob resource

        Returns:
            The LabelingJob resource.

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
            "LabelingJobName": self.labeling_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_labeling_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeLabelingJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a LabelingJob resource


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
            "LabelingJobName": self.labeling_job_name,
        }
        client.stop_labeling_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["LabelingJob"]:
        """
        Wait for a LabelingJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The LabelingJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.labeling_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="LabelingJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all LabelingJob resources

        Parameters:
            creation_time_after:A filter that returns only labeling jobs created after the specified time (timestamp).
            creation_time_before:A filter that returns only labeling jobs created before the specified time (timestamp).
            last_modified_time_after:A filter that returns only labeling jobs modified after the specified time (timestamp).
            last_modified_time_before:A filter that returns only labeling jobs modified before the specified time (timestamp).
            max_results:The maximum number of labeling jobs to return in each page of the response.
            next_token:If the result of the previous ListLabelingJobs request was truncated, the response includes a NextToken. To retrieve the next set of labeling jobs, use the token in the next request.
            name_contains:A string in the labeling job name. This filter returns only labeling jobs whose name contains the specified string.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            status_equals:A filter that retrieves only labeling jobs with a specific status.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed LabelingJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "StatusEquals": status_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_labeling_jobs",
            summaries_key="LabelingJobSummaryList",
            summary_name="LabelingJobSummary",
            resource_cls=LabelingJob,
            list_method_kwargs=operation_input_args,
        )


class LineageGroup(Base):
    """
    LineageGroup
     Class representing resource LineageGroup
    Attributes
    ---------------------
    lineage_group_name:The name of the lineage group.
    lineage_group_arn:The Amazon Resource Name (ARN) of the lineage group.
    display_name:The display name of the lineage group.
    description:The description of the lineage group.
    creation_time:The creation time of lineage group.
    created_by:
    last_modified_time:The last modified time of the lineage group.
    last_modified_by:

    """

    lineage_group_name: str
    lineage_group_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "lineage_group_name":
                return value
        raise Exception("Name attribute not found for object")

    @classmethod
    def get(
        cls,
        lineage_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["LineageGroup"]:
        operation_input_args = {
            "LineageGroupName": lineage_group_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_lineage_group(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeLineageGroupResponse")
        lineage_group = cls(**transformed_response)
        return lineage_group

    def refresh(self) -> Optional["LineageGroup"]:

        operation_input_args = {
            "LineageGroupName": self.lineage_group_name,
        }
        client = SageMakerClient().client
        response = client.describe_lineage_group(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeLineageGroupResponse", self)
        return self

    @classmethod
    def get_all(
        cls,
        created_after: Optional[datetime.datetime] = Unassigned(),
        created_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["LineageGroup"]:
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
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
            list_method="list_lineage_groups",
            summaries_key="LineageGroupSummaries",
            summary_name="LineageGroupSummary",
            resource_cls=LineageGroup,
            list_method_kwargs=operation_input_args,
        )

    def get_policy(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[GetLineageGroupPolicyResponse]:

        operation_input_args = {
            "LineageGroupName": self.lineage_group_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling get_lineage_group_policy API")
        response = client.get_lineage_group_policy(**operation_input_args)
        logger.debug(f"Response: {response}")

        transformed_response = transform(response, "GetLineageGroupPolicyResponse")
        return GetLineageGroupPolicyResponse(**transformed_response)


class Model(Base):
    """
    Class representing resource Model

    Attributes:
        model_name:Name of the SageMaker model.
        creation_time:A timestamp that shows when the model was created.
        model_arn:The Amazon Resource Name (ARN) of the model.
        primary_container:The location of the primary inference code, associated artifacts, and custom environment map that the inference code uses when it is deployed in production.
        containers:The containers in the inference pipeline.
        inference_execution_config:Specifies details of how containers in a multi-container endpoint are called.
        execution_role_arn:The Amazon Resource Name (ARN) of the IAM role that you specified for the model.
        vpc_config:A VpcConfig object that specifies the VPC that this model has access to. For more information, see Protect Endpoints by Using an Amazon Virtual Private Cloud
        enable_network_isolation:If True, no inbound or outbound network calls can be made to or from the model container.
        deployment_recommendation:A set of recommended deployment configurations for the model.

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
            if attribute == "name" or attribute == "model_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "primary_container": {
                    "model_data_source": {
                        "s3_data_source": {
                            "s3_uri": {"type": "string"},
                            "s3_data_type": {"type": "string"},
                        }
                    }
                },
                "execution_role_arn": {"type": "string"},
                "vpc_config": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "subnets": {"type": "array", "items": {"type": "string"}},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Model", **kwargs
                ),
            )

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
        """
        Create a Model resource

        Parameters:
            model_name:The name of the new model.
            primary_container:The location of the primary docker image containing inference code, associated artifacts, and custom environment map that the inference code uses when the model is deployed for predictions.
            containers:Specifies the containers in the inference pipeline.
            inference_execution_config:Specifies details of how containers in a multi-container endpoint are called.
            execution_role_arn:The Amazon Resource Name (ARN) of the IAM role that SageMaker can assume to access model artifacts and docker image for deployment on ML compute instances or for batch transform jobs. Deploying on ML compute instances is part of model hosting. For more information, see SageMaker Roles.   To be able to pass this role to SageMaker, the caller of this API must have the iam:PassRole permission.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            vpc_config:A VpcConfig object that specifies the VPC that you want your model to connect to. Control access to and from your model container by configuring the VPC. VpcConfig is used in hosting services and in batch transform. For more information, see Protect Endpoints by Using an Amazon Virtual Private Cloud and Protect Data in Batch Transform Jobs by Using an Amazon Virtual Private Cloud.
            enable_network_isolation:Isolates the model container. No inbound or outbound network calls can be made to or from the model container.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Model resource.

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

        logger.debug("Creating model resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ModelName": model_name,
            "PrimaryContainer": primary_container,
            "Containers": containers,
            "InferenceExecutionConfig": inference_execution_config,
            "ExecutionRoleArn": execution_role_arn,
            "Tags": tags,
            "VpcConfig": vpc_config,
            "EnableNetworkIsolation": enable_network_isolation,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Model", operation_input_args=operation_input_args
        )

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
        """
        Get a Model resource

        Parameters:
            model_name:The name of the model.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Model resource.

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
            "ModelName": model_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelOutput")
        model = cls(**transformed_response)
        return model

    def refresh(self) -> Optional["Model"]:
        """
        Refresh a Model resource

        Returns:
            The Model resource.

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
            "ModelName": self.model_name,
        }
        client = SageMakerClient().client
        response = client.describe_model(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelOutput", self)
        return self

    def delete(self) -> None:
        """
        Delete a Model resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "ModelName": self.model_name,
        }
        client.delete_model(**operation_input_args)

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
        """
        Get all Model resources

        Parameters:
            sort_by:Sorts the list of results. The default is CreationTime.
            sort_order:The sort order for results. The default is Descending.
            next_token:If the response to a previous ListModels request was truncated, the response includes a NextToken. To retrieve the next set of models, use the token in the next request.
            max_results:The maximum number of models to return in the response.
            name_contains:A string in the model name. This filter returns only models whose name contains the specified string.
            creation_time_before:A filter that returns only models created before the specified time (timestamp).
            creation_time_after:A filter that returns only models with a creation time greater than or equal to the specified time (timestamp).
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Model resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_models",
            summaries_key="Models",
            summary_name="ModelSummary",
            resource_cls=Model,
            list_method_kwargs=operation_input_args,
        )

    def get_all_metadata(
        self,
        search_expression: Optional[ModelMetadataSearchExpression] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[ModelMetadataSummary]:

        operation_input_args = {
            "SearchExpression": search_expression,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_model_metadata",
            summaries_key="ModelMetadataSummaries",
            summary_name="ModelMetadataSummary",
            resource_cls=ModelMetadataSummary,
            list_method_kwargs=operation_input_args,
        )


class ModelBiasJobDefinition(Base):
    """
    Class representing resource ModelBiasJobDefinition

    Attributes:
        job_definition_arn:The Amazon Resource Name (ARN) of the model bias job.
        job_definition_name:The name of the bias job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
        creation_time:The time at which the model bias job was created.
        model_bias_app_specification:Configures the model bias job to run a specified Docker container image.
        model_bias_job_input:Inputs for the model bias job.
        model_bias_job_output_config:
        job_resources:
        role_arn:The Amazon Resource Name (ARN) of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.
        model_bias_baseline_config:The baseline configuration for a model bias job.
        network_config:Networking options for a model bias job.
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
            if attribute == "name" or attribute == "model_bias_job_definition_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "model_bias_job_input": {
                    "ground_truth_s3_input": {"s3_uri": {"type": "string"}},
                    "endpoint_input": {
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                    "batch_transform_input": {
                        "data_captured_destination_s3_uri": {"type": "string"},
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                },
                "model_bias_job_output_config": {"kms_key_id": {"type": "string"}},
                "job_resources": {"cluster_config": {"volume_kms_key_id": {"type": "string"}}},
                "role_arn": {"type": "string"},
                "model_bias_baseline_config": {
                    "constraints_resource": {"s3_uri": {"type": "string"}}
                },
                "network_config": {
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelBiasJobDefinition", **kwargs
                ),
            )

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
        """
        Create a ModelBiasJobDefinition resource

        Parameters:
            job_definition_name:The name of the bias job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            model_bias_app_specification:Configures the model bias job to run a specified Docker container image.
            model_bias_job_input:Inputs for the model bias job.
            model_bias_job_output_config:
            job_resources:
            role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
            model_bias_baseline_config:The baseline configuration for a model bias job.
            network_config:Networking options for a model bias job.
            stopping_condition:
            tags:(Optional) An array of key-value pairs. For more information, see  Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelBiasJobDefinition resource.

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

        logger.debug("Creating model_bias_job_definition resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "JobDefinitionName": job_definition_name,
            "ModelBiasBaselineConfig": model_bias_baseline_config,
            "ModelBiasAppSpecification": model_bias_app_specification,
            "ModelBiasJobInput": model_bias_job_input,
            "ModelBiasJobOutputConfig": model_bias_job_output_config,
            "JobResources": job_resources,
            "NetworkConfig": network_config,
            "RoleArn": role_arn,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelBiasJobDefinition", operation_input_args=operation_input_args
        )

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
        """
        Get a ModelBiasJobDefinition resource

        Parameters:
            job_definition_name:The name of the model bias job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelBiasJobDefinition resource.

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
            "JobDefinitionName": job_definition_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_bias_job_definition(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelBiasJobDefinitionResponse")
        model_bias_job_definition = cls(**transformed_response)
        return model_bias_job_definition

    def refresh(self) -> Optional["ModelBiasJobDefinition"]:
        """
        Refresh a ModelBiasJobDefinition resource

        Returns:
            The ModelBiasJobDefinition resource.

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
            "JobDefinitionName": self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_bias_job_definition(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelBiasJobDefinitionResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a ModelBiasJobDefinition resource


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
            "JobDefinitionName": self.job_definition_name,
        }
        client.delete_model_bias_job_definition(**operation_input_args)

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
        """
        Get all ModelBiasJobDefinition resources

        Parameters:
            endpoint_name:Name of the endpoint to monitor for model bias.
            sort_by:Whether to sort results by the Name or CreationTime field. The default is CreationTime.
            sort_order:Whether to sort the results in Ascending or Descending order. The default is Descending.
            next_token:The token returned if the response is truncated. To retrieve the next set of job executions, use it in the next request.
            max_results:The maximum number of model bias jobs to return in the response. The default value is 10.
            name_contains:Filter for model bias jobs whose name contains a specified string.
            creation_time_before:A filter that returns only model bias jobs created before a specified time.
            creation_time_after:A filter that returns only model bias jobs created after a specified time.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelBiasJobDefinition resources.

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
            "EndpointName": endpoint_name,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }
        custom_key_mapping = {
            "monitoring_job_definition_name": "job_definition_name",
            "monitoring_job_definition_arn": "job_definition_arn",
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_model_bias_job_definitions",
            summaries_key="JobDefinitionSummaries",
            summary_name="MonitoringJobDefinitionSummary",
            resource_cls=ModelBiasJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args,
        )


class ModelCard(Base):
    """
    Class representing resource ModelCard

    Attributes:
        model_card_arn:The Amazon Resource Name (ARN) of the model card.
        model_card_name:The name of the model card.
        model_card_version:The version of the model card.
        content:The content of the model card.
        model_card_status:The approval status of the model card within your organization. Different organizations might have different criteria for model card review and approval.    Draft: The model card is a work in progress.    PendingReview: The model card is pending review.    Approved: The model card is approved.    Archived: The model card is archived. No more updates should be made to the model card, but it can still be exported.
        creation_time:The date and time the model card was created.
        created_by:
        security_config:The security configuration used to protect model card content.
        last_modified_time:The date and time the model card was last modified.
        last_modified_by:
        model_card_processing_status:The processing status of model card deletion. The ModelCardProcessingStatus updates throughout the different deletion steps.    DeletePending: Model card deletion request received.    DeleteInProgress: Model card deletion is in progress.    ContentDeleted: Deleted model card content.    ExportJobsDeleted: Deleted all export jobs associated with the model card.    DeleteCompleted: Successfully deleted the model card.    DeleteFailed: The model card failed to delete.

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
            if attribute == "name" or attribute == "model_card_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {"security_config": {"kms_key_id": {"type": "string"}}}
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelCard", **kwargs
                ),
            )

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
        """
        Create a ModelCard resource

        Parameters:
            model_card_name:The unique name of the model card.
            content:The content of the model card. Content must be in model card JSON schema and provided as a string.
            model_card_status:The approval status of the model card within your organization. Different organizations might have different criteria for model card review and approval.    Draft: The model card is a work in progress.    PendingReview: The model card is pending review.    Approved: The model card is approved.    Archived: The model card is archived. No more updates should be made to the model card, but it can still be exported.
            security_config:An optional Key Management Service key to encrypt, decrypt, and re-encrypt model card content for regulated workloads with highly sensitive data.
            tags:Key-value pairs used to manage metadata for model cards.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelCard resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating model_card resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ModelCardName": model_card_name,
            "SecurityConfig": security_config,
            "Content": content,
            "ModelCardStatus": model_card_status,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelCard", operation_input_args=operation_input_args
        )

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
        """
        Get a ModelCard resource

        Parameters:
            model_card_name:The name or Amazon Resource Name (ARN) of the model card to describe.
            model_card_version:The version of the model card to describe. If a version is not provided, then the latest version of the model card is described.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelCard resource.

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
            "ModelCardName": model_card_name,
            "ModelCardVersion": model_card_version,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_card(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelCardResponse")
        model_card = cls(**transformed_response)
        return model_card

    def refresh(self) -> Optional["ModelCard"]:
        """
        Refresh a ModelCard resource

        Returns:
            The ModelCard resource.

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
            "ModelCardName": self.model_card_name,
            "ModelCardVersion": self.model_card_version,
        }
        client = SageMakerClient().client
        response = client.describe_model_card(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelCardResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        content: Optional[str] = Unassigned(),
        model_card_status: Optional[str] = Unassigned(),
    ) -> Optional["ModelCard"]:
        """
        Update a ModelCard resource


        Returns:
            The ModelCard resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating model_card resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ModelCardName": self.model_card_name,
            "Content": content,
            "ModelCardStatus": model_card_status,
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
        """
        Delete a ModelCard resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "ModelCardName": self.model_card_name,
        }
        client.delete_model_card(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Draft", "PendingReview", "Approved", "Archived"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["ModelCard"]:
        """
        Wait for a ModelCard resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ModelCard resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
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
        """
        Get all ModelCard resources

        Parameters:
            creation_time_after:Only list model cards that were created after the time specified.
            creation_time_before:Only list model cards that were created before the time specified.
            max_results:The maximum number of model cards to list.
            name_contains:Only list model cards with names that contain the specified string.
            model_card_status:Only list model cards with the specified approval status.
            next_token:If the response to a previous ListModelCards request was truncated, the response includes a NextToken. To retrieve the next set of model cards, use the token in the next request.
            sort_by:Sort model cards by either name or creation time. Sorts by creation time by default.
            sort_order:Sort model cards by ascending or descending order.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelCard resources.

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
            "ModelCardStatus": model_card_status,
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
            list_method="list_model_cards",
            summaries_key="ModelCardSummaries",
            summary_name="ModelCardSummary",
            resource_cls=ModelCard,
            list_method_kwargs=operation_input_args,
        )

    def get_all_versions(
        self,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[ModelCardVersionSummary]:

        operation_input_args = {
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "ModelCardName": self.model_card_name,
            "ModelCardStatus": self.model_card_status,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_model_card_versions",
            summaries_key="ModelCardVersionSummaryList",
            summary_name="ModelCardVersionSummary",
            resource_cls=ModelCardVersionSummary,
            list_method_kwargs=operation_input_args,
        )


class ModelCardExportJob(Base):
    """
    Class representing resource ModelCardExportJob

    Attributes:
        model_card_export_job_name:The name of the model card export job to describe.
        model_card_export_job_arn:The Amazon Resource Name (ARN) of the model card export job.
        status:The completion status of the model card export job.    InProgress: The model card export job is in progress.    Completed: The model card export job is complete.    Failed: The model card export job failed. To see the reason for the failure, see the FailureReason field in the response to a DescribeModelCardExportJob call.
        model_card_name:The name or Amazon Resource Name (ARN) of the model card that the model export job exports.
        model_card_version:The version of the model card that the model export job exports.
        output_config:The export output details for the model card.
        created_at:The date and time that the model export job was created.
        last_modified_at:The date and time that the model export job was last modified.
        failure_reason:The failure reason if the model export job fails.
        export_artifacts:The exported model card artifacts.

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
            if attribute == "name" or attribute == "model_card_export_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "output_config": {"s3_output_path": {"type": "string"}},
                "export_artifacts": {"s3_export_artifacts": {"type": "string"}},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelCardExportJob", **kwargs
                ),
            )

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
        """
        Create a ModelCardExportJob resource

        Parameters:
            model_card_name:The name or Amazon Resource Name (ARN) of the model card to export.
            model_card_export_job_name:The name of the model card export job.
            output_config:The model card output configuration that specifies the Amazon S3 path for exporting.
            model_card_version:The version of the model card to export. If a version is not provided, then the latest version of the model card is exported.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelCardExportJob resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating model_card_export_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ModelCardName": model_card_name,
            "ModelCardVersion": model_card_version,
            "ModelCardExportJobName": model_card_export_job_name,
            "OutputConfig": output_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelCardExportJob", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_model_card_export_job(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            model_card_export_job_arn=response["ModelCardExportJobArn"],
            session=session,
            region=region,
        )

    @classmethod
    def get(
        cls,
        model_card_export_job_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelCardExportJob"]:
        """
        Get a ModelCardExportJob resource

        Parameters:
            model_card_export_job_arn:The Amazon Resource Name (ARN) of the model card export job to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelCardExportJob resource.

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
            "ModelCardExportJobArn": model_card_export_job_arn,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_card_export_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelCardExportJobResponse")
        model_card_export_job = cls(**transformed_response)
        return model_card_export_job

    def refresh(self) -> Optional["ModelCardExportJob"]:
        """
        Refresh a ModelCardExportJob resource

        Returns:
            The ModelCardExportJob resource.

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
            "ModelCardExportJobArn": self.model_card_export_job_arn,
        }
        client = SageMakerClient().client
        response = client.describe_model_card_export_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelCardExportJobResponse", self)
        return self

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["ModelCardExportJob"]:
        """
        Wait for a ModelCardExportJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ModelCardExportJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="ModelCardExportJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all ModelCardExportJob resources

        Parameters:
            model_card_name:List export jobs for the model card with the specified name.
            model_card_version:List export jobs for the model card with the specified version.
            creation_time_after:Only list model card export jobs that were created after the time specified.
            creation_time_before:Only list model card export jobs that were created before the time specified.
            model_card_export_job_name_contains:Only list model card export jobs with names that contain the specified string.
            status_equals:Only list model card export jobs with the specified status.
            sort_by:Sort model card export jobs by either name or creation time. Sorts by creation time by default.
            sort_order:Sort model card export jobs by ascending or descending order.
            next_token:If the response to a previous ListModelCardExportJobs request was truncated, the response includes a NextToken. To retrieve the next set of model card export jobs, use the token in the next request.
            max_results:The maximum number of model card export jobs to list.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelCardExportJob resources.

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
            "ModelCardName": model_card_name,
            "ModelCardVersion": model_card_version,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "ModelCardExportJobNameContains": model_card_export_job_name_contains,
            "StatusEquals": status_equals,
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
            list_method="list_model_card_export_jobs",
            summaries_key="ModelCardExportJobSummaries",
            summary_name="ModelCardExportJobSummary",
            resource_cls=ModelCardExportJob,
            list_method_kwargs=operation_input_args,
        )


class ModelExplainabilityJobDefinition(Base):
    """
    Class representing resource ModelExplainabilityJobDefinition

    Attributes:
        job_definition_arn:The Amazon Resource Name (ARN) of the model explainability job.
        job_definition_name:The name of the explainability job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
        creation_time:The time at which the model explainability job was created.
        model_explainability_app_specification:Configures the model explainability job to run a specified Docker container image.
        model_explainability_job_input:Inputs for the model explainability job.
        model_explainability_job_output_config:
        job_resources:
        role_arn:The Amazon Resource Name (ARN) of the IAM role that has read permission to the input data location and write permission to the output data location in Amazon S3.
        model_explainability_baseline_config:The baseline configuration for a model explainability job.
        network_config:Networking options for a model explainability job.
        stopping_condition:

    """

    job_definition_name: str
    job_definition_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned()
    model_explainability_app_specification: Optional[ModelExplainabilityAppSpecification] = (
        Unassigned()
    )
    model_explainability_job_input: Optional[ModelExplainabilityJobInput] = Unassigned()
    model_explainability_job_output_config: Optional[MonitoringOutputConfig] = Unassigned()
    job_resources: Optional[MonitoringResources] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "model_explainability_job_definition_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "model_explainability_job_input": {
                    "endpoint_input": {
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                    "batch_transform_input": {
                        "data_captured_destination_s3_uri": {"type": "string"},
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                },
                "model_explainability_job_output_config": {"kms_key_id": {"type": "string"}},
                "job_resources": {"cluster_config": {"volume_kms_key_id": {"type": "string"}}},
                "role_arn": {"type": "string"},
                "model_explainability_baseline_config": {
                    "constraints_resource": {"s3_uri": {"type": "string"}}
                },
                "network_config": {
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelExplainabilityJobDefinition", **kwargs
                ),
            )

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
        model_explainability_baseline_config: Optional[
            ModelExplainabilityBaselineConfig
        ] = Unassigned(),
        network_config: Optional[MonitoringNetworkConfig] = Unassigned(),
        stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelExplainabilityJobDefinition"]:
        """
        Create a ModelExplainabilityJobDefinition resource

        Parameters:
            job_definition_name: The name of the model explainability job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            model_explainability_app_specification:Configures the model explainability job to run a specified Docker container image.
            model_explainability_job_input:Inputs for the model explainability job.
            model_explainability_job_output_config:
            job_resources:
            role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
            model_explainability_baseline_config:The baseline configuration for a model explainability job.
            network_config:Networking options for a model explainability job.
            stopping_condition:
            tags:(Optional) An array of key-value pairs. For more information, see  Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelExplainabilityJobDefinition resource.

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

        logger.debug("Creating model_explainability_job_definition resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "JobDefinitionName": job_definition_name,
            "ModelExplainabilityBaselineConfig": model_explainability_baseline_config,
            "ModelExplainabilityAppSpecification": model_explainability_app_specification,
            "ModelExplainabilityJobInput": model_explainability_job_input,
            "ModelExplainabilityJobOutputConfig": model_explainability_job_output_config,
            "JobResources": job_resources,
            "NetworkConfig": network_config,
            "RoleArn": role_arn,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelExplainabilityJobDefinition",
            operation_input_args=operation_input_args,
        )

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
        """
        Get a ModelExplainabilityJobDefinition resource

        Parameters:
            job_definition_name:The name of the model explainability job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelExplainabilityJobDefinition resource.

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
            "JobDefinitionName": job_definition_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_explainability_job_definition(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(
            response, "DescribeModelExplainabilityJobDefinitionResponse"
        )
        model_explainability_job_definition = cls(**transformed_response)
        return model_explainability_job_definition

    def refresh(self) -> Optional["ModelExplainabilityJobDefinition"]:
        """
        Refresh a ModelExplainabilityJobDefinition resource

        Returns:
            The ModelExplainabilityJobDefinition resource.

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
            "JobDefinitionName": self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_explainability_job_definition(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelExplainabilityJobDefinitionResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a ModelExplainabilityJobDefinition resource


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
            "JobDefinitionName": self.job_definition_name,
        }
        client.delete_model_explainability_job_definition(**operation_input_args)

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
        """
        Get all ModelExplainabilityJobDefinition resources

        Parameters:
            endpoint_name:Name of the endpoint to monitor for model explainability.
            sort_by:Whether to sort results by the Name or CreationTime field. The default is CreationTime.
            sort_order:Whether to sort the results in Ascending or Descending order. The default is Descending.
            next_token:The token returned if the response is truncated. To retrieve the next set of job executions, use it in the next request.
            max_results:The maximum number of jobs to return in the response. The default value is 10.
            name_contains:Filter for model explainability jobs whose name contains a specified string.
            creation_time_before:A filter that returns only model explainability jobs created before a specified time.
            creation_time_after:A filter that returns only model explainability jobs created after a specified time.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelExplainabilityJobDefinition resources.

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
            "EndpointName": endpoint_name,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }
        custom_key_mapping = {
            "monitoring_job_definition_name": "job_definition_name",
            "monitoring_job_definition_arn": "job_definition_arn",
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_model_explainability_job_definitions",
            summaries_key="JobDefinitionSummaries",
            summary_name="MonitoringJobDefinitionSummary",
            resource_cls=ModelExplainabilityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args,
        )


class ModelPackage(Base):
    """
    Class representing resource ModelPackage

    Attributes:
        model_package_name:The name of the model package being described.
        model_package_arn:The Amazon Resource Name (ARN) of the model package.
        creation_time:A timestamp specifying when the model package was created.
        model_package_status:The current status of the model package.
        model_package_status_details:Details about the current status of the model package.
        model_package_group_name:If the model is a versioned model, the name of the model group that the versioned model belongs to.
        model_package_version:The version of the model package.
        model_package_description:A brief summary of the model package.
        inference_specification:Details about inference jobs that you can run with models based on this model package.
        source_algorithm_specification:Details about the algorithm that was used to create the model package.
        validation_specification:Configurations for one or more transform jobs that SageMaker runs to test the model package.
        certify_for_marketplace:Whether the model package is certified for listing on Amazon Web Services Marketplace.
        model_approval_status:The approval status of the model package.
        created_by:
        metadata_properties:
        model_metrics:Metrics for the model.
        last_modified_time:The last time that the model package was modified.
        last_modified_by:
        approval_description:A description provided for the model approval.
        domain:The machine learning domain of the model package you specified. Common machine learning domains include computer vision and natural language processing.
        task:The machine learning task you specified that your model package accomplishes. Common machine learning tasks include object detection and image classification.
        sample_payload_url:The Amazon Simple Storage Service (Amazon S3) path where the sample payload are stored. This path points to a single gzip compressed tar archive (.tar.gz suffix).
        customer_metadata_properties:The metadata properties associated with the model package versions.
        drift_check_baselines:Represents the drift check baselines that can be used when the model monitor is set using the model package. For more information, see the topic on Drift Detection against Previous Baselines in SageMaker Pipelines in the Amazon SageMaker Developer Guide.
        additional_inference_specifications:An array of additional Inference Specification objects. Each additional Inference Specification specifies artifacts based on this model package that can be used on inference endpoints. Generally used with SageMaker Neo to store the compiled artifacts.
        skip_model_validation:Indicates if you want to skip model validation.
        source_uri:The URI of the source for the model package.

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
    additional_inference_specifications: Optional[
        List[AdditionalInferenceSpecificationDefinition]
    ] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()
    source_uri: Optional[str] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "model_package_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "validation_specification": {"validation_role": {"type": "string"}},
                "model_metrics": {
                    "model_quality": {
                        "statistics": {"s3_uri": {"type": "string"}},
                        "constraints": {"s3_uri": {"type": "string"}},
                    },
                    "model_data_quality": {
                        "statistics": {"s3_uri": {"type": "string"}},
                        "constraints": {"s3_uri": {"type": "string"}},
                    },
                    "bias": {
                        "report": {"s3_uri": {"type": "string"}},
                        "pre_training_report": {"s3_uri": {"type": "string"}},
                        "post_training_report": {"s3_uri": {"type": "string"}},
                    },
                    "explainability": {"report": {"s3_uri": {"type": "string"}}},
                },
                "drift_check_baselines": {
                    "bias": {
                        "config_file": {"s3_uri": {"type": "string"}},
                        "pre_training_constraints": {"s3_uri": {"type": "string"}},
                        "post_training_constraints": {"s3_uri": {"type": "string"}},
                    },
                    "explainability": {
                        "constraints": {"s3_uri": {"type": "string"}},
                        "config_file": {"s3_uri": {"type": "string"}},
                    },
                    "model_quality": {
                        "statistics": {"s3_uri": {"type": "string"}},
                        "constraints": {"s3_uri": {"type": "string"}},
                    },
                    "model_data_quality": {
                        "statistics": {"s3_uri": {"type": "string"}},
                        "constraints": {"s3_uri": {"type": "string"}},
                    },
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelPackage", **kwargs
                ),
            )

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
        additional_inference_specifications: Optional[
            List[AdditionalInferenceSpecificationDefinition]
        ] = Unassigned(),
        skip_model_validation: Optional[str] = Unassigned(),
        source_uri: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackage"]:
        """
        Create a ModelPackage resource

        Parameters:
            model_package_name:The name of the model package. The name must have 1 to 63 characters. Valid characters are a-z, A-Z, 0-9, and - (hyphen). This parameter is required for unversioned models. It is not applicable to versioned models.
            model_package_group_name:The name or Amazon Resource Name (ARN) of the model package group that this model version belongs to. This parameter is required for versioned models, and does not apply to unversioned models.
            model_package_description:A description of the model package.
            inference_specification:Specifies details about inference jobs that you can run with models based on this model package, including the following information:   The Amazon ECR paths of containers that contain the inference code and model artifacts.   The instance types that the model package supports for transform jobs and real-time endpoints used for inference.   The input and output content formats that the model package supports for inference.
            validation_specification:Specifies configurations for one or more transform jobs that SageMaker runs to test the model package.
            source_algorithm_specification:Details about the algorithm that was used to create the model package.
            certify_for_marketplace:Whether to certify the model package for listing on Amazon Web Services Marketplace. This parameter is optional for unversioned models, and does not apply to versioned models.
            tags:A list of key value pairs associated with the model. For more information, see Tagging Amazon Web Services resources in the Amazon Web Services General Reference Guide. If you supply ModelPackageGroupName, your model package belongs to the model group you specify and uses the tags associated with the model group. In this case, you cannot supply a tag argument.
            model_approval_status:Whether the model is approved for deployment. This parameter is optional for versioned models, and does not apply to unversioned models. For versioned models, the value of this parameter must be set to Approved to deploy the model.
            metadata_properties:
            model_metrics:A structure that contains model metrics reports.
            client_token:A unique token that guarantees that the call to this API is idempotent.
            domain:The machine learning domain of your model package and its components. Common machine learning domains include computer vision and natural language processing.
            task:The machine learning task your model package accomplishes. Common machine learning tasks include object detection and image classification. The following tasks are supported by Inference Recommender: "IMAGE_CLASSIFICATION" | "OBJECT_DETECTION" | "TEXT_GENERATION" |"IMAGE_SEGMENTATION" | "FILL_MASK" | "CLASSIFICATION" | "REGRESSION" | "OTHER". Specify "OTHER" if none of the tasks listed fit your use case.
            sample_payload_url:The Amazon Simple Storage Service (Amazon S3) path where the sample payload is stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix). This archive can hold multiple files that are all equally used in the load test. Each file in the archive must satisfy the size constraints of the InvokeEndpoint call.
            customer_metadata_properties:The metadata properties associated with the model package versions.
            drift_check_baselines:Represents the drift check baselines that can be used when the model monitor is set using the model package. For more information, see the topic on Drift Detection against Previous Baselines in SageMaker Pipelines in the Amazon SageMaker Developer Guide.
            additional_inference_specifications:An array of additional Inference Specification objects. Each additional Inference Specification specifies artifacts based on this model package that can be used on inference endpoints. Generally used with SageMaker Neo to store the compiled artifacts.
            skip_model_validation:Indicates if you want to skip model validation.
            source_uri:The URI of the source for the model package. If you want to clone a model package, set it to the model package Amazon Resource Name (ARN). If you want to register a model, set it to the model ARN.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelPackage resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating model_package resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ModelPackageName": model_package_name,
            "ModelPackageGroupName": model_package_group_name,
            "ModelPackageDescription": model_package_description,
            "InferenceSpecification": inference_specification,
            "ValidationSpecification": validation_specification,
            "SourceAlgorithmSpecification": source_algorithm_specification,
            "CertifyForMarketplace": certify_for_marketplace,
            "Tags": tags,
            "ModelApprovalStatus": model_approval_status,
            "MetadataProperties": metadata_properties,
            "ModelMetrics": model_metrics,
            "ClientToken": client_token,
            "Domain": domain,
            "Task": task,
            "SamplePayloadUrl": sample_payload_url,
            "CustomerMetadataProperties": customer_metadata_properties,
            "DriftCheckBaselines": drift_check_baselines,
            "AdditionalInferenceSpecifications": additional_inference_specifications,
            "SkipModelValidation": skip_model_validation,
            "SourceUri": source_uri,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelPackage", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_model_package(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            model_package_name=response["ModelPackageName"], session=session, region=region
        )

    @classmethod
    def get(
        cls,
        model_package_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackage"]:
        """
        Get a ModelPackage resource

        Parameters:
            model_package_name:The name or Amazon Resource Name (ARN) of the model package to describe. When you specify a name, the name must have 1 to 63 characters. Valid characters are a-z, A-Z, 0-9, and - (hyphen).
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelPackage resource.

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
            "ModelPackageName": model_package_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_package(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelPackageOutput")
        model_package = cls(**transformed_response)
        return model_package

    def refresh(self) -> Optional["ModelPackage"]:
        """
        Refresh a ModelPackage resource

        Returns:
            The ModelPackage resource.

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
            "ModelPackageName": self.model_package_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelPackageOutput", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        model_approval_status: Optional[str] = Unassigned(),
        approval_description: Optional[str] = Unassigned(),
        customer_metadata_properties: Optional[Dict[str, str]] = Unassigned(),
        customer_metadata_properties_to_remove: Optional[List[str]] = Unassigned(),
        additional_inference_specifications_to_add: Optional[
            List[AdditionalInferenceSpecificationDefinition]
        ] = Unassigned(),
        inference_specification: Optional[InferenceSpecification] = Unassigned(),
        source_uri: Optional[str] = Unassigned(),
    ) -> Optional["ModelPackage"]:
        """
        Update a ModelPackage resource

        Parameters:
            customer_metadata_properties_to_remove:The metadata properties associated with the model package versions to remove.
            additional_inference_specifications_to_add:An array of additional Inference Specification objects to be added to the existing array additional Inference Specification. Total number of additional Inference Specifications can not exceed 15. Each additional Inference Specification specifies artifacts based on this model package that can be used on inference endpoints. Generally used with SageMaker Neo to store the compiled artifacts.

        Returns:
            The ModelPackage resource.

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

        logger.debug("Updating model_package resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ModelPackageArn": self.model_package_arn,
            "ModelApprovalStatus": model_approval_status,
            "ApprovalDescription": approval_description,
            "CustomerMetadataProperties": customer_metadata_properties,
            "CustomerMetadataPropertiesToRemove": customer_metadata_properties_to_remove,
            "AdditionalInferenceSpecificationsToAdd": additional_inference_specifications_to_add,
            "InferenceSpecification": inference_specification,
            "SourceUri": source_uri,
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
        """
        Delete a ModelPackage resource


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
            "ModelPackageName": self.model_package_name,
        }
        client.delete_model_package(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Pending", "InProgress", "Completed", "Failed", "Deleting"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["ModelPackage"]:
        """
        Wait for a ModelPackage resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ModelPackage resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.model_package_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="ModelPackage", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all ModelPackage resources

        Parameters:
            creation_time_after:A filter that returns only model packages created after the specified time (timestamp).
            creation_time_before:A filter that returns only model packages created before the specified time (timestamp).
            max_results:The maximum number of model packages to return in the response.
            name_contains:A string in the model package name. This filter returns only model packages whose name contains the specified string.
            model_approval_status:A filter that returns only the model packages with the specified approval status.
            model_package_group_name:A filter that returns only model versions that belong to the specified model group.
            model_package_type:A filter that returns only the model packages of the specified type. This can be one of the following values.    UNVERSIONED - List only unversioined models. This is the default value if no ModelPackageType is specified.    VERSIONED - List only versioned models.    BOTH - List both versioned and unversioned models.
            next_token:If the response to a previous ListModelPackages request was truncated, the response includes a NextToken. To retrieve the next set of model packages, use the token in the next request.
            sort_by:The parameter by which to sort the results. The default is CreationTime.
            sort_order:The sort order for the results. The default is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelPackage resources.

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
            "ModelApprovalStatus": model_approval_status,
            "ModelPackageGroupName": model_package_group_name,
            "ModelPackageType": model_package_type,
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
            list_method="list_model_packages",
            summaries_key="ModelPackageSummaryList",
            summary_name="ModelPackageSummary",
            resource_cls=ModelPackage,
            list_method_kwargs=operation_input_args,
        )

    def batch_get(
        self,
        model_package_arn_list: List[str],
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[BatchDescribeModelPackageOutput]:

        operation_input_args = {
            "ModelPackageArnList": model_package_arn_list,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling batch_describe_model_package API")
        response = client.batch_describe_model_package(**operation_input_args)
        logger.debug(f"Response: {response}")

        transformed_response = transform(response, "BatchDescribeModelPackageOutput")
        return BatchDescribeModelPackageOutput(**transformed_response)


class ModelPackageGroup(Base):
    """
    Class representing resource ModelPackageGroup

    Attributes:
        model_package_group_name:The name of the model group.
        model_package_group_arn:The Amazon Resource Name (ARN) of the model group.
        creation_time:The time that the model group was created.
        created_by:
        model_package_group_status:The status of the model group.
        model_package_group_description:A description of the model group.

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
            if attribute == "name" or attribute == "model_package_group_name":
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
        """
        Create a ModelPackageGroup resource

        Parameters:
            model_package_group_name:The name of the model group.
            model_package_group_description:A description for the model group.
            tags:A list of key value pairs associated with the model group. For more information, see Tagging Amazon Web Services resources in the Amazon Web Services General Reference Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelPackageGroup resource.

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

        logger.debug("Creating model_package_group resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ModelPackageGroupName": model_package_group_name,
            "ModelPackageGroupDescription": model_package_group_description,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelPackageGroup", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_model_package_group(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            model_package_group_name=model_package_group_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        model_package_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["ModelPackageGroup"]:
        """
        Get a ModelPackageGroup resource

        Parameters:
            model_package_group_name:The name of the model group to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelPackageGroup resource.

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
            "ModelPackageGroupName": model_package_group_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_package_group(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelPackageGroupOutput")
        model_package_group = cls(**transformed_response)
        return model_package_group

    def refresh(self) -> Optional["ModelPackageGroup"]:
        """
        Refresh a ModelPackageGroup resource

        Returns:
            The ModelPackageGroup resource.

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
            "ModelPackageGroupName": self.model_package_group_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_package_group(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelPackageGroupOutput", self)
        return self

    def delete(self) -> None:
        """
        Delete a ModelPackageGroup resource


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
            "ModelPackageGroupName": self.model_package_group_name,
        }
        client.delete_model_package_group(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Pending", "InProgress", "Completed", "Failed", "Deleting", "DeleteFailed"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["ModelPackageGroup"]:
        """
        Wait for a ModelPackageGroup resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ModelPackageGroup resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.model_package_group_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="ModelPackageGroup", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all ModelPackageGroup resources

        Parameters:
            creation_time_after:A filter that returns only model groups created after the specified time.
            creation_time_before:A filter that returns only model groups created before the specified time.
            max_results:The maximum number of results to return in the response.
            name_contains:A string in the model group name. This filter returns only model groups whose name contains the specified string.
            next_token:If the result of the previous ListModelPackageGroups request was truncated, the response includes a NextToken. To retrieve the next set of model groups, use the token in the next request.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelPackageGroup resources.

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
            list_method="list_model_package_groups",
            summaries_key="ModelPackageGroupSummaryList",
            summary_name="ModelPackageGroupSummary",
            resource_cls=ModelPackageGroup,
            list_method_kwargs=operation_input_args,
        )

    def get_policy(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[str]:
        """
        Perform GetModelPackageGroupPolicy on a ModelPackageGroup resource.


        """

        operation_input_args = {
            "ModelPackageGroupName": self.model_package_group_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling get_model_package_group_policy API")
        response = client.get_model_package_group_policy(**operation_input_args)
        logger.debug(f"Response: {response}")

        return list(response.values())[0]

    def delete_policy(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:
        """
        Perform DeleteModelPackageGroupPolicy on a ModelPackageGroup resource.


        """

        operation_input_args = {
            "ModelPackageGroupName": self.model_package_group_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling delete_model_package_group_policy API")
        response = client.delete_model_package_group_policy(**operation_input_args)
        logger.debug(f"Response: {response}")

    def put_policy(
        self,
        resource_policy: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "ModelPackageGroupName": self.model_package_group_name,
            "ResourcePolicy": resource_policy,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling put_model_package_group_policy API")
        response = client.put_model_package_group_policy(**operation_input_args)
        logger.debug(f"Response: {response}")


class ModelQualityJobDefinition(Base):
    """
    Class representing resource ModelQualityJobDefinition

    Attributes:
        job_definition_arn:The Amazon Resource Name (ARN) of the model quality job.
        job_definition_name:The name of the quality job definition. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
        creation_time:The time at which the model quality job was created.
        model_quality_app_specification:Configures the model quality job to run a specified Docker container image.
        model_quality_job_input:Inputs for the model quality job.
        model_quality_job_output_config:
        job_resources:
        role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
        model_quality_baseline_config:The baseline configuration for a model quality job.
        network_config:Networking options for a model quality job.
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
            if attribute == "name" or attribute == "model_quality_job_definition_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "model_quality_job_input": {
                    "ground_truth_s3_input": {"s3_uri": {"type": "string"}},
                    "endpoint_input": {
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                    "batch_transform_input": {
                        "data_captured_destination_s3_uri": {"type": "string"},
                        "s3_input_mode": {"type": "string"},
                        "s3_data_distribution_type": {"type": "string"},
                    },
                },
                "model_quality_job_output_config": {"kms_key_id": {"type": "string"}},
                "job_resources": {"cluster_config": {"volume_kms_key_id": {"type": "string"}}},
                "role_arn": {"type": "string"},
                "model_quality_baseline_config": {
                    "constraints_resource": {"s3_uri": {"type": "string"}}
                },
                "network_config": {
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ModelQualityJobDefinition", **kwargs
                ),
            )

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
        """
        Create a ModelQualityJobDefinition resource

        Parameters:
            job_definition_name:The name of the monitoring job definition.
            model_quality_app_specification:The container that runs the monitoring job.
            model_quality_job_input:A list of the inputs that are monitored. Currently endpoints are supported.
            model_quality_job_output_config:
            job_resources:
            role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
            model_quality_baseline_config:Specifies the constraints and baselines for the monitoring job.
            network_config:Specifies the network configuration for the monitoring job.
            stopping_condition:
            tags:(Optional) An array of key-value pairs. For more information, see  Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelQualityJobDefinition resource.

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

        logger.debug("Creating model_quality_job_definition resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "JobDefinitionName": job_definition_name,
            "ModelQualityBaselineConfig": model_quality_baseline_config,
            "ModelQualityAppSpecification": model_quality_app_specification,
            "ModelQualityJobInput": model_quality_job_input,
            "ModelQualityJobOutputConfig": model_quality_job_output_config,
            "JobResources": job_resources,
            "NetworkConfig": network_config,
            "RoleArn": role_arn,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ModelQualityJobDefinition", operation_input_args=operation_input_args
        )

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
        """
        Get a ModelQualityJobDefinition resource

        Parameters:
            job_definition_name:The name of the model quality job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ModelQualityJobDefinition resource.

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
            "JobDefinitionName": job_definition_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_model_quality_job_definition(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeModelQualityJobDefinitionResponse")
        model_quality_job_definition = cls(**transformed_response)
        return model_quality_job_definition

    def refresh(self) -> Optional["ModelQualityJobDefinition"]:
        """
        Refresh a ModelQualityJobDefinition resource

        Returns:
            The ModelQualityJobDefinition resource.

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
            "JobDefinitionName": self.job_definition_name,
        }
        client = SageMakerClient().client
        response = client.describe_model_quality_job_definition(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeModelQualityJobDefinitionResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a ModelQualityJobDefinition resource


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
            "JobDefinitionName": self.job_definition_name,
        }
        client.delete_model_quality_job_definition(**operation_input_args)

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
        """
        Get all ModelQualityJobDefinition resources

        Parameters:
            endpoint_name:A filter that returns only model quality monitoring job definitions that are associated with the specified endpoint.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:Whether to sort the results in Ascending or Descending order. The default is Descending.
            next_token:If the result of the previous ListModelQualityJobDefinitions request was truncated, the response includes a NextToken. To retrieve the next set of model quality monitoring job definitions, use the token in the next request.
            max_results:The maximum number of results to return in a call to ListModelQualityJobDefinitions.
            name_contains:A string in the transform job name. This filter returns only model quality monitoring job definitions whose name contains the specified string.
            creation_time_before:A filter that returns only model quality monitoring job definitions created before the specified time.
            creation_time_after:A filter that returns only model quality monitoring job definitions created after the specified time.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ModelQualityJobDefinition resources.

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
            "EndpointName": endpoint_name,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
        }
        custom_key_mapping = {
            "monitoring_job_definition_name": "job_definition_name",
            "monitoring_job_definition_arn": "job_definition_arn",
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_model_quality_job_definitions",
            summaries_key="JobDefinitionSummaries",
            summary_name="MonitoringJobDefinitionSummary",
            resource_cls=ModelQualityJobDefinition,
            custom_key_mapping=custom_key_mapping,
            list_method_kwargs=operation_input_args,
        )


class MonitoringSchedule(Base):
    """
    Class representing resource MonitoringSchedule

    Attributes:
        monitoring_schedule_arn:The Amazon Resource Name (ARN) of the monitoring schedule.
        monitoring_schedule_name:Name of the monitoring schedule.
        monitoring_schedule_status:The status of an monitoring job.
        creation_time:The time at which the monitoring job was created.
        last_modified_time:The time at which the monitoring job was last modified.
        monitoring_schedule_config:The configuration object that specifies the monitoring schedule and defines the monitoring job.
        monitoring_type:The type of the monitoring job that this schedule runs. This is one of the following values.    DATA_QUALITY - The schedule is for a data quality monitoring job.    MODEL_QUALITY - The schedule is for a model quality monitoring job.    MODEL_BIAS - The schedule is for a bias monitoring job.    MODEL_EXPLAINABILITY - The schedule is for an explainability monitoring job.
        failure_reason:A string, up to one KB in size, that contains the reason a monitoring job failed, if it failed.
        endpoint_name: The name of the endpoint for the monitoring job.
        last_monitoring_execution_summary:Describes metadata on the last execution to run, if there was one.

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
            if attribute == "name" or attribute == "monitoring_schedule_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "monitoring_schedule_config": {
                    "monitoring_job_definition": {
                        "monitoring_output_config": {"kms_key_id": {"type": "string"}},
                        "monitoring_resources": {
                            "cluster_config": {"volume_kms_key_id": {"type": "string"}}
                        },
                        "role_arn": {"type": "string"},
                        "baseline_config": {
                            "constraints_resource": {"s3_uri": {"type": "string"}},
                            "statistics_resource": {"s3_uri": {"type": "string"}},
                        },
                        "network_config": {
                            "vpc_config": {
                                "security_group_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "subnets": {"type": "array", "items": {"type": "string"}},
                            }
                        },
                    }
                }
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "MonitoringSchedule", **kwargs
                ),
            )

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
        """
        Create a MonitoringSchedule resource

        Parameters:
            monitoring_schedule_name:The name of the monitoring schedule. The name must be unique within an Amazon Web Services Region within an Amazon Web Services account.
            monitoring_schedule_config:The configuration object that specifies the monitoring schedule and defines the monitoring job.
            tags:(Optional) An array of key-value pairs. For more information, see Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The MonitoringSchedule resource.

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

        logger.debug("Creating monitoring_schedule resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "MonitoringScheduleName": monitoring_schedule_name,
            "MonitoringScheduleConfig": monitoring_schedule_config,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="MonitoringSchedule", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_monitoring_schedule(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            monitoring_schedule_name=monitoring_schedule_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        monitoring_schedule_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["MonitoringSchedule"]:
        """
        Get a MonitoringSchedule resource

        Parameters:
            monitoring_schedule_name:Name of a previously created monitoring schedule.
            session: Boto3 session.
            region: Region name.

        Returns:
            The MonitoringSchedule resource.

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
            "MonitoringScheduleName": monitoring_schedule_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_monitoring_schedule(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeMonitoringScheduleResponse")
        monitoring_schedule = cls(**transformed_response)
        return monitoring_schedule

    def refresh(self) -> Optional["MonitoringSchedule"]:
        """
        Refresh a MonitoringSchedule resource

        Returns:
            The MonitoringSchedule resource.

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
            "MonitoringScheduleName": self.monitoring_schedule_name,
        }
        client = SageMakerClient().client
        response = client.describe_monitoring_schedule(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeMonitoringScheduleResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        monitoring_schedule_config: MonitoringScheduleConfig,
    ) -> Optional["MonitoringSchedule"]:
        """
        Update a MonitoringSchedule resource


        Returns:
            The MonitoringSchedule resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating monitoring_schedule resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "MonitoringScheduleName": self.monitoring_schedule_name,
            "MonitoringScheduleConfig": monitoring_schedule_config,
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
        """
        Delete a MonitoringSchedule resource


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
            "MonitoringScheduleName": self.monitoring_schedule_name,
        }
        client.delete_monitoring_schedule(**operation_input_args)

    def stop(self) -> None:
        """
        Stop a MonitoringSchedule resource


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
            "MonitoringScheduleName": self.monitoring_schedule_name,
        }
        client.stop_monitoring_schedule(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Pending", "Failed", "Scheduled", "Stopped"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["MonitoringSchedule"]:
        """
        Wait for a MonitoringSchedule resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The MonitoringSchedule resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.monitoring_schedule_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="MonitoringSchedule",
                    status=current_status,
                    reason=self.failure_reason,
                )

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
        """
        Get all MonitoringSchedule resources

        Parameters:
            endpoint_name:Name of a specific endpoint to fetch schedules for.
            sort_by:Whether to sort the results by the Status, CreationTime, or ScheduledTime field. The default is CreationTime.
            sort_order:Whether to sort the results in Ascending or Descending order. The default is Descending.
            next_token:The token returned if the response is truncated. To retrieve the next set of job executions, use it in the next request.
            max_results:The maximum number of jobs to return in the response. The default value is 10.
            name_contains:Filter for monitoring schedules whose name contains a specified string.
            creation_time_before:A filter that returns only monitoring schedules created before a specified time.
            creation_time_after:A filter that returns only monitoring schedules created after a specified time.
            last_modified_time_before:A filter that returns only monitoring schedules modified before a specified time.
            last_modified_time_after:A filter that returns only monitoring schedules modified after a specified time.
            status_equals:A filter that returns only monitoring schedules modified before a specified time.
            monitoring_job_definition_name:Gets a list of the monitoring schedules for the specified monitoring job definition.
            monitoring_type_equals:A filter that returns only the monitoring schedules for the specified monitoring type.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed MonitoringSchedule resources.

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
            "EndpointName": endpoint_name,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "StatusEquals": status_equals,
            "MonitoringJobDefinitionName": monitoring_job_definition_name,
            "MonitoringTypeEquals": monitoring_type_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_monitoring_schedules",
            summaries_key="MonitoringScheduleSummaries",
            summary_name="MonitoringScheduleSummary",
            resource_cls=MonitoringSchedule,
            list_method_kwargs=operation_input_args,
        )


class NotebookInstance(Base):
    """
    Class representing resource NotebookInstance

    Attributes:
        notebook_instance_arn:The Amazon Resource Name (ARN) of the notebook instance.
        notebook_instance_name:The name of the SageMaker notebook instance.
        notebook_instance_status:The status of the notebook instance.
        failure_reason:If status is Failed, the reason it failed.
        url:The URL that you use to connect to the Jupyter notebook that is running in your notebook instance.
        instance_type:The type of ML compute instance running on the notebook instance.
        subnet_id:The ID of the VPC subnet.
        security_groups:The IDs of the VPC security groups.
        role_arn:The Amazon Resource Name (ARN) of the IAM role associated with the instance.
        kms_key_id:The Amazon Web Services KMS key ID SageMaker uses to encrypt data when storing it on the ML storage volume attached to the instance.
        network_interface_id:The network interface IDs that SageMaker created at the time of creating the instance.
        last_modified_time:A timestamp. Use this parameter to retrieve the time when the notebook instance was last modified.
        creation_time:A timestamp. Use this parameter to return the time when the notebook instance was created
        notebook_instance_lifecycle_config_name:Returns the name of a notebook instance lifecycle configuration. For information about notebook instance lifestyle configurations, see Step 2.1: (Optional) Customize a Notebook Instance
        direct_internet_access:Describes whether SageMaker provides internet access to the notebook instance. If this value is set to Disabled, the notebook instance does not have internet access, and cannot connect to SageMaker training and endpoint services. For more information, see Notebook Instances Are Internet-Enabled by Default.
        volume_size_in_g_b:The size, in GB, of the ML storage volume attached to the notebook instance.
        accelerator_types:A list of the Elastic Inference (EI) instance types associated with this notebook instance. Currently only one EI instance type can be associated with a notebook instance. For more information, see Using Elastic Inference in Amazon SageMaker.
        default_code_repository:The Git repository associated with the notebook instance as its default code repository. This can be either the name of a Git repository stored as a resource in your account, or the URL of a Git repository in Amazon Web Services CodeCommit or in any other Git repository. When you open a notebook instance, it opens in the directory that contains this repository. For more information, see Associating Git Repositories with SageMaker Notebook Instances.
        additional_code_repositories:An array of up to three Git repositories associated with the notebook instance. These can be either the names of Git repositories stored as resources in your account, or the URL of Git repositories in Amazon Web Services CodeCommit or in any other Git repository. These repositories are cloned at the same level as the default repository of your notebook instance. For more information, see Associating Git Repositories with SageMaker Notebook Instances.
        root_access:Whether root access is enabled or disabled for users of the notebook instance.  Lifecycle configurations need root access to be able to set up a notebook instance. Because of this, lifecycle configurations associated with a notebook instance always run with root access even if you disable root access for users.
        platform_identifier:The platform identifier of the notebook instance runtime environment.
        instance_metadata_service_configuration:Information on the IMDS configuration of the notebook instance

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
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = (
        Unassigned()
    )

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "notebook_instance_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "subnet_id": {"type": "string"},
                "security_groups": {"type": "array", "items": {"type": "string"}},
                "role_arn": {"type": "string"},
                "kms_key_id": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "NotebookInstance", **kwargs
                ),
            )

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
        instance_metadata_service_configuration: Optional[
            InstanceMetadataServiceConfiguration
        ] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstance"]:
        """
        Create a NotebookInstance resource

        Parameters:
            notebook_instance_name:The name of the new notebook instance.
            instance_type:The type of ML compute instance to launch for the notebook instance.
            role_arn: When you send any requests to Amazon Web Services resources from the notebook instance, SageMaker assumes this role to perform tasks on your behalf. You must grant this role necessary permissions so SageMaker can perform these tasks. The policy must allow the SageMaker service principal (sagemaker.amazonaws.com) permissions to assume this role. For more information, see SageMaker Roles.   To be able to pass this role to SageMaker, the caller of this API must have the iam:PassRole permission.
            subnet_id:The ID of the subnet in a VPC to which you would like to have a connectivity from your ML compute instance.
            security_group_ids:The VPC security group IDs, in the form sg-xxxxxxxx. The security groups must be for the same VPC as specified in the subnet.
            kms_key_id:The Amazon Resource Name (ARN) of a Amazon Web Services Key Management Service key that SageMaker uses to encrypt data on the storage volume attached to your notebook instance. The KMS key you provide must be enabled. For information, see Enabling and Disabling Keys in the Amazon Web Services Key Management Service Developer Guide.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            lifecycle_config_name:The name of a lifecycle configuration to associate with the notebook instance. For information about lifestyle configurations, see Step 2.1: (Optional) Customize a Notebook Instance.
            direct_internet_access:Sets whether SageMaker provides internet access to the notebook instance. If you set this to Disabled this notebook instance is able to access resources only in your VPC, and is not be able to connect to SageMaker training and endpoint services unless you configure a NAT Gateway in your VPC. For more information, see Notebook Instances Are Internet-Enabled by Default. You can set the value of this parameter to Disabled only if you set a value for the SubnetId parameter.
            volume_size_in_g_b:The size, in GB, of the ML storage volume to attach to the notebook instance. The default value is 5 GB.
            accelerator_types:A list of Elastic Inference (EI) instance types to associate with this notebook instance. Currently, only one instance type can be associated with a notebook instance. For more information, see Using Elastic Inference in Amazon SageMaker.
            default_code_repository:A Git repository to associate with the notebook instance as its default code repository. This can be either the name of a Git repository stored as a resource in your account, or the URL of a Git repository in Amazon Web Services CodeCommit or in any other Git repository. When you open a notebook instance, it opens in the directory that contains this repository. For more information, see Associating Git Repositories with SageMaker Notebook Instances.
            additional_code_repositories:An array of up to three Git repositories to associate with the notebook instance. These can be either the names of Git repositories stored as resources in your account, or the URL of Git repositories in Amazon Web Services CodeCommit or in any other Git repository. These repositories are cloned at the same level as the default repository of your notebook instance. For more information, see Associating Git Repositories with SageMaker Notebook Instances.
            root_access:Whether root access is enabled or disabled for users of the notebook instance. The default value is Enabled.  Lifecycle configurations need root access to be able to set up a notebook instance. Because of this, lifecycle configurations associated with a notebook instance always run with root access even if you disable root access for users.
            platform_identifier:The platform identifier of the notebook instance runtime environment.
            instance_metadata_service_configuration:Information on the IMDS configuration of the notebook instance
            session: Boto3 session.
            region: Region name.

        Returns:
            The NotebookInstance resource.

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

        logger.debug("Creating notebook_instance resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "NotebookInstanceName": notebook_instance_name,
            "InstanceType": instance_type,
            "SubnetId": subnet_id,
            "SecurityGroupIds": security_group_ids,
            "RoleArn": role_arn,
            "KmsKeyId": kms_key_id,
            "Tags": tags,
            "LifecycleConfigName": lifecycle_config_name,
            "DirectInternetAccess": direct_internet_access,
            "VolumeSizeInGB": volume_size_in_g_b,
            "AcceleratorTypes": accelerator_types,
            "DefaultCodeRepository": default_code_repository,
            "AdditionalCodeRepositories": additional_code_repositories,
            "RootAccess": root_access,
            "PlatformIdentifier": platform_identifier,
            "InstanceMetadataServiceConfiguration": instance_metadata_service_configuration,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="NotebookInstance", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_notebook_instance(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            notebook_instance_name=notebook_instance_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        notebook_instance_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstance"]:
        """
        Get a NotebookInstance resource

        Parameters:
            notebook_instance_name:The name of the notebook instance that you want information about.
            session: Boto3 session.
            region: Region name.

        Returns:
            The NotebookInstance resource.

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
            "NotebookInstanceName": notebook_instance_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_notebook_instance(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeNotebookInstanceOutput")
        notebook_instance = cls(**transformed_response)
        return notebook_instance

    def refresh(self) -> Optional["NotebookInstance"]:
        """
        Refresh a NotebookInstance resource

        Returns:
            The NotebookInstance resource.

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
            "NotebookInstanceName": self.notebook_instance_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeNotebookInstanceOutput", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        instance_type: Optional[str] = Unassigned(),
        role_arn: Optional[str] = Unassigned(),
        lifecycle_config_name: Optional[str] = Unassigned(),
        disassociate_lifecycle_config: Optional[bool] = Unassigned(),
        volume_size_in_g_b: Optional[int] = Unassigned(),
        default_code_repository: Optional[str] = Unassigned(),
        additional_code_repositories: Optional[List[str]] = Unassigned(),
        accelerator_types: Optional[List[str]] = Unassigned(),
        disassociate_accelerator_types: Optional[bool] = Unassigned(),
        disassociate_default_code_repository: Optional[bool] = Unassigned(),
        disassociate_additional_code_repositories: Optional[bool] = Unassigned(),
        root_access: Optional[str] = Unassigned(),
        instance_metadata_service_configuration: Optional[
            InstanceMetadataServiceConfiguration
        ] = Unassigned(),
    ) -> Optional["NotebookInstance"]:
        """
        Update a NotebookInstance resource

        Parameters:
            lifecycle_config_name:The name of a lifecycle configuration to associate with the notebook instance. For information about lifestyle configurations, see Step 2.1: (Optional) Customize a Notebook Instance.
            disassociate_lifecycle_config:Set to true to remove the notebook instance lifecycle configuration currently associated with the notebook instance. This operation is idempotent. If you specify a lifecycle configuration that is not associated with the notebook instance when you call this method, it does not throw an error.
            disassociate_accelerator_types:A list of the Elastic Inference (EI) instance types to remove from this notebook instance. This operation is idempotent. If you specify an accelerator type that is not associated with the notebook instance when you call this method, it does not throw an error.
            disassociate_default_code_repository:The name or URL of the default Git repository to remove from this notebook instance. This operation is idempotent. If you specify a Git repository that is not associated with the notebook instance when you call this method, it does not throw an error.
            disassociate_additional_code_repositories:A list of names or URLs of the default Git repositories to remove from this notebook instance. This operation is idempotent. If you specify a Git repository that is not associated with the notebook instance when you call this method, it does not throw an error.

        Returns:
            The NotebookInstance resource.

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
        """

        logger.debug("Updating notebook_instance resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "NotebookInstanceName": self.notebook_instance_name,
            "InstanceType": instance_type,
            "RoleArn": role_arn,
            "LifecycleConfigName": lifecycle_config_name,
            "DisassociateLifecycleConfig": disassociate_lifecycle_config,
            "VolumeSizeInGB": volume_size_in_g_b,
            "DefaultCodeRepository": default_code_repository,
            "AdditionalCodeRepositories": additional_code_repositories,
            "AcceleratorTypes": accelerator_types,
            "DisassociateAcceleratorTypes": disassociate_accelerator_types,
            "DisassociateDefaultCodeRepository": disassociate_default_code_repository,
            "DisassociateAdditionalCodeRepositories": disassociate_additional_code_repositories,
            "RootAccess": root_access,
            "InstanceMetadataServiceConfiguration": instance_metadata_service_configuration,
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
        """
        Delete a NotebookInstance resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "NotebookInstanceName": self.notebook_instance_name,
        }
        client.delete_notebook_instance(**operation_input_args)

    def stop(self) -> None:
        """
        Stop a NotebookInstance resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "NotebookInstanceName": self.notebook_instance_name,
        }
        client.stop_notebook_instance(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Pending", "InService", "Stopping", "Stopped", "Failed", "Deleting", "Updating"
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["NotebookInstance"]:
        """
        Wait for a NotebookInstance resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The NotebookInstance resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.notebook_instance_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="NotebookInstance",
                    status=current_status,
                    reason=self.failure_reason,
                )

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
        """
        Get all NotebookInstance resources

        Parameters:
            next_token: If the previous call to the ListNotebookInstances is truncated, the response includes a NextToken. You can use this token in your subsequent ListNotebookInstances request to fetch the next set of notebook instances.   You might specify a filter or a sort order in your request. When response is truncated, you must use the same values for the filer and sort order in the next request.
            max_results:The maximum number of notebook instances to return.
            sort_by:The field to sort results by. The default is Name.
            sort_order:The sort order for results.
            name_contains:A string in the notebook instances' name. This filter returns only notebook instances whose name contains the specified string.
            creation_time_before:A filter that returns only notebook instances that were created before the specified time (timestamp).
            creation_time_after:A filter that returns only notebook instances that were created after the specified time (timestamp).
            last_modified_time_before:A filter that returns only notebook instances that were modified before the specified time (timestamp).
            last_modified_time_after:A filter that returns only notebook instances that were modified after the specified time (timestamp).
            status_equals:A filter that returns only notebook instances with the specified status.
            notebook_instance_lifecycle_config_name_contains:A string in the name of a notebook instances lifecycle configuration associated with this notebook instance. This filter returns only notebook instances associated with a lifecycle configuration with a name that contains the specified string.
            default_code_repository_contains:A string in the name or URL of a Git repository associated with this notebook instance. This filter returns only notebook instances associated with a git repository with a name that contains the specified string.
            additional_code_repository_equals:A filter that returns only notebook instances with associated with the specified git repository.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed NotebookInstance resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
            "StatusEquals": status_equals,
            "NotebookInstanceLifecycleConfigNameContains": notebook_instance_lifecycle_config_name_contains,
            "DefaultCodeRepositoryContains": default_code_repository_contains,
            "AdditionalCodeRepositoryEquals": additional_code_repository_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_notebook_instances",
            summaries_key="NotebookInstances",
            summary_name="NotebookInstanceSummary",
            resource_cls=NotebookInstance,
            list_method_kwargs=operation_input_args,
        )


class NotebookInstanceLifecycleConfig(Base):
    """
    Class representing resource NotebookInstanceLifecycleConfig

    Attributes:
        notebook_instance_lifecycle_config_arn:The Amazon Resource Name (ARN) of the lifecycle configuration.
        notebook_instance_lifecycle_config_name:The name of the lifecycle configuration.
        on_create:The shell script that runs only once, when you create a notebook instance.
        on_start:The shell script that runs every time you start a notebook instance, including when you create the notebook instance.
        last_modified_time:A timestamp that tells when the lifecycle configuration was last modified.
        creation_time:A timestamp that tells when the lifecycle configuration was created.

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
            if attribute == "name" or attribute == "notebook_instance_lifecycle_config_name":
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
        """
        Create a NotebookInstanceLifecycleConfig resource

        Parameters:
            notebook_instance_lifecycle_config_name:The name of the lifecycle configuration.
            on_create:A shell script that runs only once, when you create a notebook instance. The shell script must be a base64-encoded string.
            on_start:A shell script that runs every time you start a notebook instance, including when you create the notebook instance. The shell script must be a base64-encoded string.
            session: Boto3 session.
            region: Region name.

        Returns:
            The NotebookInstanceLifecycleConfig resource.

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

        logger.debug("Creating notebook_instance_lifecycle_config resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "NotebookInstanceLifecycleConfigName": notebook_instance_lifecycle_config_name,
            "OnCreate": on_create,
            "OnStart": on_start,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="NotebookInstanceLifecycleConfig",
            operation_input_args=operation_input_args,
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_notebook_instance_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            notebook_instance_lifecycle_config_name=notebook_instance_lifecycle_config_name,
            session=session,
            region=region,
        )

    @classmethod
    def get(
        cls,
        notebook_instance_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["NotebookInstanceLifecycleConfig"]:
        """
        Get a NotebookInstanceLifecycleConfig resource

        Parameters:
            notebook_instance_lifecycle_config_name:The name of the lifecycle configuration to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The NotebookInstanceLifecycleConfig resource.

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
            "NotebookInstanceLifecycleConfigName": notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeNotebookInstanceLifecycleConfigOutput")
        notebook_instance_lifecycle_config = cls(**transformed_response)
        return notebook_instance_lifecycle_config

    def refresh(self) -> Optional["NotebookInstanceLifecycleConfig"]:
        """
        Refresh a NotebookInstanceLifecycleConfig resource

        Returns:
            The NotebookInstanceLifecycleConfig resource.

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
            "NotebookInstanceLifecycleConfigName": self.notebook_instance_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_notebook_instance_lifecycle_config(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeNotebookInstanceLifecycleConfigOutput", self)
        return self

    def update(
        self,
        on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
    ) -> Optional["NotebookInstanceLifecycleConfig"]:
        """
        Update a NotebookInstanceLifecycleConfig resource


        Returns:
            The NotebookInstanceLifecycleConfig resource.

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
        """

        logger.debug("Updating notebook_instance_lifecycle_config resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "NotebookInstanceLifecycleConfigName": self.notebook_instance_lifecycle_config_name,
            "OnCreate": on_create,
            "OnStart": on_start,
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
        """
        Delete a NotebookInstanceLifecycleConfig resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "NotebookInstanceLifecycleConfigName": self.notebook_instance_lifecycle_config_name,
        }
        client.delete_notebook_instance_lifecycle_config(**operation_input_args)

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
        """
        Get all NotebookInstanceLifecycleConfig resources

        Parameters:
            next_token:If the result of a ListNotebookInstanceLifecycleConfigs request was truncated, the response includes a NextToken. To get the next set of lifecycle configurations, use the token in the next request.
            max_results:The maximum number of lifecycle configurations to return in the response.
            sort_by:Sorts the list of results. The default is CreationTime.
            sort_order:The sort order for results.
            name_contains:A string in the lifecycle configuration name. This filter returns only lifecycle configurations whose name contains the specified string.
            creation_time_before:A filter that returns only lifecycle configurations that were created before the specified time (timestamp).
            creation_time_after:A filter that returns only lifecycle configurations that were created after the specified time (timestamp).
            last_modified_time_before:A filter that returns only lifecycle configurations that were modified before the specified time (timestamp).
            last_modified_time_after:A filter that returns only lifecycle configurations that were modified after the specified time (timestamp).
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed NotebookInstanceLifecycleConfig resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
            "CreationTimeBefore": creation_time_before,
            "CreationTimeAfter": creation_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "LastModifiedTimeAfter": last_modified_time_after,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_notebook_instance_lifecycle_configs",
            summaries_key="NotebookInstanceLifecycleConfigs",
            summary_name="NotebookInstanceLifecycleConfigSummary",
            resource_cls=NotebookInstanceLifecycleConfig,
            list_method_kwargs=operation_input_args,
        )


class Pipeline(Base):
    """
    Class representing resource Pipeline

    Attributes:
        pipeline_arn:The Amazon Resource Name (ARN) of the pipeline.
        pipeline_name:The name of the pipeline.
        pipeline_display_name:The display name of the pipeline.
        pipeline_definition:The JSON pipeline definition.
        pipeline_description:The description of the pipeline.
        role_arn:The Amazon Resource Name (ARN) that the pipeline uses to execute.
        pipeline_status:The status of the pipeline execution.
        creation_time:The time when the pipeline was created.
        last_modified_time:The time when the pipeline was last modified.
        last_run_time:The time when the pipeline was last run.
        created_by:
        last_modified_by:
        parallelism_configuration:Lists the parallelism configuration applied to the pipeline.

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
            if attribute == "name" or attribute == "pipeline_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {"role_arn": {"type": "string"}}
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Pipeline", **kwargs
                ),
            )

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
        """
        Create a Pipeline resource

        Parameters:
            pipeline_name:The name of the pipeline.
            client_request_token:A unique, case-sensitive identifier that you provide to ensure the idempotency of the operation. An idempotent operation completes no more than one time.
            role_arn:The Amazon Resource Name (ARN) of the role used by the pipeline to access and create resources.
            pipeline_display_name:The display name of the pipeline.
            pipeline_definition:The JSON pipeline definition of the pipeline.
            pipeline_definition_s3_location:The location of the pipeline definition stored in Amazon S3. If specified, SageMaker will retrieve the pipeline definition from this location.
            pipeline_description:A description of the pipeline.
            tags:A list of tags to apply to the created pipeline.
            parallelism_configuration:This is the configuration that controls the parallelism of the pipeline. If specified, it applies to all runs of this pipeline by default.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Pipeline resource.

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
            ResourceLimitExceeded: You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created.
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating pipeline resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "PipelineName": pipeline_name,
            "PipelineDisplayName": pipeline_display_name,
            "PipelineDefinition": pipeline_definition,
            "PipelineDefinitionS3Location": pipeline_definition_s3_location,
            "PipelineDescription": pipeline_description,
            "ClientRequestToken": client_request_token,
            "RoleArn": role_arn,
            "Tags": tags,
            "ParallelismConfiguration": parallelism_configuration,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Pipeline", operation_input_args=operation_input_args
        )

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
        """
        Get a Pipeline resource

        Parameters:
            pipeline_name:The name or Amazon Resource Name (ARN) of the pipeline to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Pipeline resource.

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
            "PipelineName": pipeline_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_pipeline(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribePipelineResponse")
        pipeline = cls(**transformed_response)
        return pipeline

    def refresh(self) -> Optional["Pipeline"]:
        """
        Refresh a Pipeline resource

        Returns:
            The Pipeline resource.

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
            "PipelineName": self.pipeline_name,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribePipelineResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        pipeline_display_name: Optional[str] = Unassigned(),
        pipeline_definition: Optional[str] = Unassigned(),
        pipeline_definition_s3_location: Optional[PipelineDefinitionS3Location] = Unassigned(),
        pipeline_description: Optional[str] = Unassigned(),
        role_arn: Optional[str] = Unassigned(),
        parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned(),
    ) -> Optional["Pipeline"]:
        """
        Update a Pipeline resource

        Parameters:
            pipeline_definition_s3_location:The location of the pipeline definition stored in Amazon S3. If specified, SageMaker will retrieve the pipeline definition from this location.

        Returns:
            The Pipeline resource.

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

        logger.debug("Updating pipeline resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "PipelineName": self.pipeline_name,
            "PipelineDisplayName": pipeline_display_name,
            "PipelineDefinition": pipeline_definition,
            "PipelineDefinitionS3Location": pipeline_definition_s3_location,
            "PipelineDescription": pipeline_description,
            "RoleArn": role_arn,
            "ParallelismConfiguration": parallelism_configuration,
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
        """
        Delete a Pipeline resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "PipelineName": self.pipeline_name,
            "ClientRequestToken": self.client_request_token,
        }
        client.delete_pipeline(**operation_input_args)

    def wait_for_status(
        self, status: Literal["Active", "Deleting"], poll: int = 5, timeout: Optional[int] = None
    ) -> Optional["Pipeline"]:
        """
        Wait for a Pipeline resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Pipeline resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
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
        """
        Get all Pipeline resources

        Parameters:
            pipeline_name_prefix:The prefix of the pipeline name.
            created_after:A filter that returns the pipelines that were created after a specified time.
            created_before:A filter that returns the pipelines that were created before a specified time.
            sort_by:The field by which to sort results. The default is CreatedTime.
            sort_order:The sort order for results.
            next_token:If the result of the previous ListPipelines request was truncated, the response includes a NextToken. To retrieve the next set of pipelines, use the token in the next request.
            max_results:The maximum number of pipelines to return in the response.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Pipeline resources.

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
            "PipelineNamePrefix": pipeline_name_prefix,
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
            list_method="list_pipelines",
            summaries_key="PipelineSummaries",
            summary_name="PipelineSummary",
            resource_cls=Pipeline,
            list_method_kwargs=operation_input_args,
        )


class PipelineExecution(Base):
    """
    Class representing resource PipelineExecution

    Attributes:
        pipeline_arn:The Amazon Resource Name (ARN) of the pipeline.
        pipeline_execution_arn:The Amazon Resource Name (ARN) of the pipeline execution.
        pipeline_execution_display_name:The display name of the pipeline execution.
        pipeline_execution_status:The status of the pipeline execution.
        pipeline_execution_description:The description of the pipeline execution.
        pipeline_experiment_config:
        failure_reason:If the execution failed, a message describing why.
        creation_time:The time when the pipeline execution was created.
        last_modified_time:The time when the pipeline execution was modified last.
        created_by:
        last_modified_by:
        parallelism_configuration:The parallelism configuration applied to the pipeline.
        selective_execution_config:The selective execution configuration applied to the pipeline run.

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
            if attribute == "name" or attribute == "pipeline_execution_name":
                return value
        raise Exception("Name attribute not found for object")

    @classmethod
    def get(
        cls,
        pipeline_execution_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["PipelineExecution"]:
        """
        Get a PipelineExecution resource

        Parameters:
            pipeline_execution_arn:The Amazon Resource Name (ARN) of the pipeline execution.
            session: Boto3 session.
            region: Region name.

        Returns:
            The PipelineExecution resource.

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
            "PipelineExecutionArn": pipeline_execution_arn,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_pipeline_execution(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribePipelineExecutionResponse")
        pipeline_execution = cls(**transformed_response)
        return pipeline_execution

    def refresh(self) -> Optional["PipelineExecution"]:
        """
        Refresh a PipelineExecution resource

        Returns:
            The PipelineExecution resource.

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
            "PipelineExecutionArn": self.pipeline_execution_arn,
        }
        client = SageMakerClient().client
        response = client.describe_pipeline_execution(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribePipelineExecutionResponse", self)
        return self

    def update(
        self,
        pipeline_execution_description: Optional[str] = Unassigned(),
        pipeline_execution_display_name: Optional[str] = Unassigned(),
        parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned(),
    ) -> Optional["PipelineExecution"]:
        """
        Update a PipelineExecution resource


        Returns:
            The PipelineExecution resource.

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

        logger.debug("Updating pipeline_execution resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
            "PipelineExecutionDescription": pipeline_execution_description,
            "PipelineExecutionDisplayName": pipeline_execution_display_name,
            "ParallelismConfiguration": parallelism_configuration,
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
        """
        Stop a PipelineExecution resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
            "ClientRequestToken": self.client_request_token,
        }
        client.stop_pipeline_execution(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Executing", "Stopping", "Stopped", "Failed", "Succeeded"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["PipelineExecution"]:
        """
        Wait for a PipelineExecution resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The PipelineExecution resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.pipeline_execution_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="PipelineExecution",
                    status=current_status,
                    reason=self.failure_reason,
                )

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
        """
        Get all PipelineExecution resources

        Parameters:
            pipeline_name:The name or Amazon Resource Name (ARN) of the pipeline.
            created_after:A filter that returns the pipeline executions that were created after a specified time.
            created_before:A filter that returns the pipeline executions that were created before a specified time.
            sort_by:The field by which to sort results. The default is CreatedTime.
            sort_order:The sort order for results.
            next_token:If the result of the previous ListPipelineExecutions request was truncated, the response includes a NextToken. To retrieve the next set of pipeline executions, use the token in the next request.
            max_results:The maximum number of pipeline executions to return in the response.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed PipelineExecution resources.

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
            "PipelineName": pipeline_name,
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
            list_method="list_pipeline_executions",
            summaries_key="PipelineExecutionSummaries",
            summary_name="PipelineExecutionSummary",
            resource_cls=PipelineExecution,
            list_method_kwargs=operation_input_args,
        )

    def get_pipeline_definition(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[DescribePipelineDefinitionForExecutionResponse]:

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling describe_pipeline_definition_for_execution API")
        response = client.describe_pipeline_definition_for_execution(**operation_input_args)
        logger.debug(f"Response: {response}")

        transformed_response = transform(response, "DescribePipelineDefinitionForExecutionResponse")
        return DescribePipelineDefinitionForExecutionResponse(**transformed_response)

    def get_all_steps(
        self,
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[PipelineExecutionStep]:

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_pipeline_execution_steps",
            summaries_key="PipelineExecutionSteps",
            summary_name="PipelineExecutionStep",
            resource_cls=PipelineExecutionStep,
            list_method_kwargs=operation_input_args,
        )

    def get_all_parameters(
        self,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[Parameter]:

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_pipeline_parameters_for_execution",
            summaries_key="PipelineParameters",
            summary_name="Parameter",
            resource_cls=Parameter,
            list_method_kwargs=operation_input_args,
        )

    def retry(
        self,
        client_request_token: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:
        """
        Perform RetryPipelineExecution on a PipelineExecution resource.

        Parameters:
            client_request_token:A unique, case-sensitive identifier that you provide to ensure the idempotency of the operation. An idempotent operation completes no more than once.

        """

        operation_input_args = {
            "PipelineExecutionArn": self.pipeline_execution_arn,
            "ClientRequestToken": client_request_token,
            "ParallelismConfiguration": self.parallelism_configuration,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling retry_pipeline_execution API")
        response = client.retry_pipeline_execution(**operation_input_args)
        logger.debug(f"Response: {response}")

    def send_execution_step_failure(
        self,
        callback_token: str,
        client_request_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "CallbackToken": callback_token,
            "FailureReason": self.failure_reason,
            "ClientRequestToken": client_request_token,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling send_pipeline_execution_step_failure API")
        response = client.send_pipeline_execution_step_failure(**operation_input_args)
        logger.debug(f"Response: {response}")

    def send_execution_step_success(
        self,
        callback_token: str,
        output_parameters: Optional[List[OutputParameter]] = Unassigned(),
        client_request_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "CallbackToken": callback_token,
            "OutputParameters": output_parameters,
            "ClientRequestToken": client_request_token,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling send_pipeline_execution_step_success API")
        response = client.send_pipeline_execution_step_success(**operation_input_args)
        logger.debug(f"Response: {response}")


class ProcessingJob(Base):
    """
    Class representing resource ProcessingJob

    Attributes:
        processing_job_name:The name of the processing job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
        processing_resources:Identifies the resources, ML compute instances, and ML storage volumes to deploy for a processing job. In distributed training, you specify more than one instance.
        app_specification:Configures the processing job to run a specified container image.
        processing_job_arn:The Amazon Resource Name (ARN) of the processing job.
        processing_job_status:Provides the status of a processing job.
        creation_time:The time at which the processing job was created.
        processing_inputs:The inputs for a processing job.
        processing_output_config:Output configuration for the processing job.
        stopping_condition:The time limit for how long the processing job is allowed to run.
        environment:The environment variables set in the Docker container.
        network_config:Networking options for a processing job.
        role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
        experiment_config:The configuration information used to create an experiment.
        exit_message:An optional string, up to one KB in size, that contains metadata from the processing container when the processing job exits.
        failure_reason:A string, up to one KB in size, that contains the reason a processing job failed, if it failed.
        processing_end_time:The time at which the processing job completed.
        processing_start_time:The time at which the processing job started.
        last_modified_time:The time at which the processing job was last modified.
        monitoring_schedule_arn:The ARN of a monitoring schedule for an endpoint associated with this processing job.
        auto_m_l_job_arn:The ARN of an AutoML job associated with this processing job.
        training_job_arn:The ARN of a training job associated with this processing job.

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
            if attribute == "name" or attribute == "processing_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "processing_resources": {
                    "cluster_config": {"volume_kms_key_id": {"type": "string"}}
                },
                "processing_output_config": {"kms_key_id": {"type": "string"}},
                "network_config": {
                    "vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                },
                "role_arn": {"type": "string"},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "ProcessingJob", **kwargs
                ),
            )

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
        """
        Create a ProcessingJob resource

        Parameters:
            processing_job_name: The name of the processing job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            processing_resources:Identifies the resources, ML compute instances, and ML storage volumes to deploy for a processing job. In distributed training, you specify more than one instance.
            app_specification:Configures the processing job to run a specified Docker container image.
            role_arn:The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.
            processing_inputs:An array of inputs configuring the data to download into the processing container.
            processing_output_config:Output configuration for the processing job.
            stopping_condition:The time limit for how long the processing job is allowed to run.
            environment:The environment variables to set in the Docker container. Up to 100 key and values entries in the map are supported.
            network_config:Networking options for a processing job, such as whether to allow inbound and outbound network calls to and from processing containers, and the VPC subnets and security groups to use for VPC-enabled processing jobs.
            tags:(Optional) An array of key-value pairs. For more information, see Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            experiment_config:
            session: Boto3 session.
            region: Region name.

        Returns:
            The ProcessingJob resource.

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
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating processing_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ProcessingInputs": processing_inputs,
            "ProcessingOutputConfig": processing_output_config,
            "ProcessingJobName": processing_job_name,
            "ProcessingResources": processing_resources,
            "StoppingCondition": stopping_condition,
            "AppSpecification": app_specification,
            "Environment": environment,
            "NetworkConfig": network_config,
            "RoleArn": role_arn,
            "Tags": tags,
            "ExperimentConfig": experiment_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="ProcessingJob", operation_input_args=operation_input_args
        )

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
        """
        Get a ProcessingJob resource

        Parameters:
            processing_job_name:The name of the processing job. The name must be unique within an Amazon Web Services Region in the Amazon Web Services account.
            session: Boto3 session.
            region: Region name.

        Returns:
            The ProcessingJob resource.

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
            "ProcessingJobName": processing_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_processing_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeProcessingJobResponse")
        processing_job = cls(**transformed_response)
        return processing_job

    def refresh(self) -> Optional["ProcessingJob"]:
        """
        Refresh a ProcessingJob resource

        Returns:
            The ProcessingJob resource.

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
            "ProcessingJobName": self.processing_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_processing_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeProcessingJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a ProcessingJob resource


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
            "ProcessingJobName": self.processing_job_name,
        }
        client.stop_processing_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["ProcessingJob"]:
        """
        Wait for a ProcessingJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The ProcessingJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.processing_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="ProcessingJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all ProcessingJob resources

        Parameters:
            creation_time_after:A filter that returns only processing jobs created after the specified time.
            creation_time_before:A filter that returns only processing jobs created after the specified time.
            last_modified_time_after:A filter that returns only processing jobs modified after the specified time.
            last_modified_time_before:A filter that returns only processing jobs modified before the specified time.
            name_contains:A string in the processing job name. This filter returns only processing jobs whose name contains the specified string.
            status_equals:A filter that retrieves only processing jobs with a specific status.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            next_token:If the result of the previous ListProcessingJobs request was truncated, the response includes a NextToken. To retrieve the next set of processing jobs, use the token in the next request.
            max_results:The maximum number of processing jobs to return in the response.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed ProcessingJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
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
            list_method="list_processing_jobs",
            summaries_key="ProcessingJobSummaries",
            summary_name="ProcessingJobSummary",
            resource_cls=ProcessingJob,
            list_method_kwargs=operation_input_args,
        )


class Project(Base):
    """
    Class representing resource Project

    Attributes:
        project_arn:The Amazon Resource Name (ARN) of the project.
        project_name:The name of the project.
        project_id:The ID of the project.
        service_catalog_provisioning_details:Information used to provision a service catalog product. For information, see What is Amazon Web Services Service Catalog.
        project_status:The status of the project.
        creation_time:The time when the project was created.
        project_description:The description of the project.
        service_catalog_provisioned_product_details:Information about a provisioned service catalog product.
        created_by:
        last_modified_time:The timestamp when project was last modified.
        last_modified_by:

    """

    project_name: str
    project_arn: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioning_details: Optional[ServiceCatalogProvisioningDetails] = Unassigned()
    service_catalog_provisioned_product_details: Optional[
        ServiceCatalogProvisionedProductDetails
    ] = Unassigned()
    project_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "project_name":
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
        """
        Create a Project resource

        Parameters:
            project_name:The name of the project.
            service_catalog_provisioning_details:The product ID and provisioning artifact ID to provision a service catalog. The provisioning artifact ID will default to the latest provisioning artifact ID of the product, if you don't provide the provisioning artifact ID. For more information, see What is Amazon Web Services Service Catalog.
            project_description:A description for the project.
            tags:An array of key-value pairs that you want to use to organize and track your Amazon Web Services resource costs. For more information, see Tagging Amazon Web Services resources in the Amazon Web Services General Reference Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Project resource.

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

        logger.debug("Creating project resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "ProjectName": project_name,
            "ProjectDescription": project_description,
            "ServiceCatalogProvisioningDetails": service_catalog_provisioning_details,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Project", operation_input_args=operation_input_args
        )

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
        """
        Get a Project resource

        Parameters:
            project_name:The name of the project to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Project resource.

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
            "ProjectName": project_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_project(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeProjectOutput")
        project = cls(**transformed_response)
        return project

    def refresh(self) -> Optional["Project"]:
        """
        Refresh a Project resource

        Returns:
            The Project resource.

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
            "ProjectName": self.project_name,
        }
        client = SageMakerClient().client
        response = client.describe_project(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeProjectOutput", self)
        return self

    def update(
        self,
        project_description: Optional[str] = Unassigned(),
        service_catalog_provisioning_update_details: Optional[
            ServiceCatalogProvisioningUpdateDetails
        ] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
    ) -> Optional["Project"]:
        """
        Update a Project resource

        Parameters:
            service_catalog_provisioning_update_details:The product ID and provisioning artifact ID to provision a service catalog. The provisioning artifact ID will default to the latest provisioning artifact ID of the product, if you don't provide the provisioning artifact ID. For more information, see What is Amazon Web Services Service Catalog.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources. In addition, the project must have tag update constraints set in order to include this parameter in the request. For more information, see Amazon Web Services Service Catalog Tag Update Constraints.

        Returns:
            The Project resource.

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

        logger.debug("Updating project resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "ProjectName": self.project_name,
            "ProjectDescription": project_description,
            "ServiceCatalogProvisioningUpdateDetails": service_catalog_provisioning_update_details,
            "Tags": tags,
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
        """
        Delete a Project resource


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
            "ProjectName": self.project_name,
        }
        client.delete_project(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Pending",
            "CreateInProgress",
            "CreateCompleted",
            "CreateFailed",
            "DeleteInProgress",
            "DeleteFailed",
            "DeleteCompleted",
            "UpdateInProgress",
            "UpdateCompleted",
            "UpdateFailed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Project"]:
        """
        Wait for a Project resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Project resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.project_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Project", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all Project resources

        Parameters:
            creation_time_after:A filter that returns the projects that were created after a specified time.
            creation_time_before:A filter that returns the projects that were created before a specified time.
            max_results:The maximum number of projects to return in the response.
            name_contains:A filter that returns the projects whose name contains a specified string.
            next_token:If the result of the previous ListProjects request was truncated, the response includes a NextToken. To retrieve the next set of projects, use the token in the next request.
            sort_by:The field by which to sort results. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Project resources.

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
            list_method="list_projects",
            summaries_key="ProjectSummaryList",
            summary_name="ProjectSummary",
            resource_cls=Project,
            list_method_kwargs=operation_input_args,
        )


class Space(Base):
    """
    Class representing resource Space

    Attributes:
        domain_id:The ID of the associated domain.
        space_arn:The space's Amazon Resource Name (ARN).
        space_name:The name of the space.
        home_efs_file_system_uid:The ID of the space's profile in the Amazon EFS volume.
        status:The status.
        last_modified_time:The last modified time.
        creation_time:The creation time.
        failure_reason:The failure reason.
        space_settings:A collection of space settings.
        ownership_settings:The collection of ownership settings for a space.
        space_sharing_settings:The collection of space sharing settings for a space.
        space_display_name:The name of the space that appears in the Amazon SageMaker Studio UI.
        url:Returns the URL of the space. If the space is created with Amazon Web Services IAM Identity Center (Successor to Amazon Web Services Single Sign-On) authentication, users can navigate to the URL after appending the respective redirect parameter for the application type to be federated through Amazon Web Services IAM Identity Center. The following application types are supported:   Studio Classic: &amp;redirect=JupyterServer    JupyterLab: &amp;redirect=JupyterLab    Code Editor, based on Code-OSS, Visual Studio Code - Open Source: &amp;redirect=CodeEditor

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
            if attribute == "name" or attribute == "space_name":
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
        """
        Create a Space resource

        Parameters:
            domain_id:The ID of the associated domain.
            space_name:The name of the space.
            tags:Tags to associated with the space. Each tag consists of a key and an optional value. Tag keys must be unique for each resource. Tags are searchable using the Search API.
            space_settings:A collection of space settings.
            ownership_settings:A collection of ownership settings.
            space_sharing_settings:A collection of space sharing settings.
            space_display_name:The name of the space that appears in the SageMaker Studio UI.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Space resource.

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

        logger.debug("Creating space resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "DomainId": domain_id,
            "SpaceName": space_name,
            "Tags": tags,
            "SpaceSettings": space_settings,
            "OwnershipSettings": ownership_settings,
            "SpaceSharingSettings": space_sharing_settings,
            "SpaceDisplayName": space_display_name,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Space", operation_input_args=operation_input_args
        )

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
        """
        Get a Space resource

        Parameters:
            domain_id:The ID of the associated domain.
            space_name:The name of the space.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Space resource.

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
            "SpaceName": space_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_space(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeSpaceResponse")
        space = cls(**transformed_response)
        return space

    def refresh(self) -> Optional["Space"]:
        """
        Refresh a Space resource

        Returns:
            The Space resource.

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
            "SpaceName": self.space_name,
        }
        client = SageMakerClient().client
        response = client.describe_space(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeSpaceResponse", self)
        return self

    def update(
        self,
        space_settings: Optional[SpaceSettings] = Unassigned(),
        space_display_name: Optional[str] = Unassigned(),
    ) -> Optional["Space"]:
        """
        Update a Space resource


        Returns:
            The Space resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating space resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "DomainId": self.domain_id,
            "SpaceName": self.space_name,
            "SpaceSettings": space_settings,
            "SpaceDisplayName": space_display_name,
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
        """
        Delete a Space resource


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
            "SpaceName": self.space_name,
        }
        client.delete_space(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Deleting",
            "Failed",
            "InService",
            "Pending",
            "Updating",
            "Update_Failed",
            "Delete_Failed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Space"]:
        """
        Wait for a Space resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Space resource.

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
                    resource_type="Space", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all Space resources

        Parameters:
            next_token:If the previous response was truncated, you will receive this token. Use it in your next request to receive the next set of results.
            max_results:The total number of items to return in the response. If the total number of items available is more than the value specified, a NextToken is provided in the response. To resume pagination, provide the NextToken value in the as part of a subsequent call. The default value is 10.
            sort_order:The sort order for the results. The default is Ascending.
            sort_by:The parameter by which to sort the results. The default is CreationTime.
            domain_id_equals:A parameter to search for the domain ID.
            space_name_contains:A parameter by which to filter the results.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Space resources.

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
            "SpaceNameContains": space_name_contains,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_spaces",
            summaries_key="Spaces",
            summary_name="SpaceDetails",
            resource_cls=Space,
            list_method_kwargs=operation_input_args,
        )


class StudioLifecycleConfig(Base):
    """
    Class representing resource StudioLifecycleConfig

    Attributes:
        studio_lifecycle_config_arn:The ARN of the Lifecycle Configuration to describe.
        studio_lifecycle_config_name:The name of the Amazon SageMaker Studio Lifecycle Configuration that is described.
        creation_time:The creation time of the Amazon SageMaker Studio Lifecycle Configuration.
        last_modified_time:This value is equivalent to CreationTime because Amazon SageMaker Studio Lifecycle Configurations are immutable.
        studio_lifecycle_config_content:The content of your Amazon SageMaker Studio Lifecycle Configuration script.
        studio_lifecycle_config_app_type:The App type that the Lifecycle Configuration is attached to.

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
            if attribute == "name" or attribute == "studio_lifecycle_config_name":
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
        """
        Create a StudioLifecycleConfig resource

        Parameters:
            studio_lifecycle_config_name:The name of the Amazon SageMaker Studio Lifecycle Configuration to create.
            studio_lifecycle_config_content:The content of your Amazon SageMaker Studio Lifecycle Configuration script. This content must be base64 encoded.
            studio_lifecycle_config_app_type:The App type that the Lifecycle Configuration is attached to.
            tags:Tags to be associated with the Lifecycle Configuration. Each tag consists of a key and an optional value. Tag keys must be unique per resource. Tags are searchable using the Search API.
            session: Boto3 session.
            region: Region name.

        Returns:
            The StudioLifecycleConfig resource.

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

        logger.debug("Creating studio_lifecycle_config resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "StudioLifecycleConfigName": studio_lifecycle_config_name,
            "StudioLifecycleConfigContent": studio_lifecycle_config_content,
            "StudioLifecycleConfigAppType": studio_lifecycle_config_app_type,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="StudioLifecycleConfig", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_studio_lifecycle_config(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            studio_lifecycle_config_name=studio_lifecycle_config_name,
            session=session,
            region=region,
        )

    @classmethod
    def get(
        cls,
        studio_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["StudioLifecycleConfig"]:
        """
        Get a StudioLifecycleConfig resource

        Parameters:
            studio_lifecycle_config_name:The name of the Amazon SageMaker Studio Lifecycle Configuration to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The StudioLifecycleConfig resource.

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
            "StudioLifecycleConfigName": studio_lifecycle_config_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_studio_lifecycle_config(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeStudioLifecycleConfigResponse")
        studio_lifecycle_config = cls(**transformed_response)
        return studio_lifecycle_config

    def refresh(self) -> Optional["StudioLifecycleConfig"]:
        """
        Refresh a StudioLifecycleConfig resource

        Returns:
            The StudioLifecycleConfig resource.

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
            "StudioLifecycleConfigName": self.studio_lifecycle_config_name,
        }
        client = SageMakerClient().client
        response = client.describe_studio_lifecycle_config(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeStudioLifecycleConfigResponse", self)
        return self

    def delete(self) -> None:
        """
        Delete a StudioLifecycleConfig resource


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
            "StudioLifecycleConfigName": self.studio_lifecycle_config_name,
        }
        client.delete_studio_lifecycle_config(**operation_input_args)

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
        """
        Get all StudioLifecycleConfig resources

        Parameters:
            max_results:The total number of items to return in the response. If the total number of items available is more than the value specified, a NextToken is provided in the response. To resume pagination, provide the NextToken value in the as part of a subsequent call. The default value is 10.
            next_token:If the previous call to ListStudioLifecycleConfigs didn't return the full set of Lifecycle Configurations, the call returns a token for getting the next set of Lifecycle Configurations.
            name_contains:A string in the Lifecycle Configuration name. This filter returns only Lifecycle Configurations whose name contains the specified string.
            app_type_equals:A parameter to search for the App Type to which the Lifecycle Configuration is attached.
            creation_time_before:A filter that returns only Lifecycle Configurations created on or before the specified time.
            creation_time_after:A filter that returns only Lifecycle Configurations created on or after the specified time.
            modified_time_before:A filter that returns only Lifecycle Configurations modified before the specified time.
            modified_time_after:A filter that returns only Lifecycle Configurations modified after the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed StudioLifecycleConfig resources.

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
        """

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "NameContains": name_contains,
            "AppTypeEquals": app_type_equals,
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
            list_method="list_studio_lifecycle_configs",
            summaries_key="StudioLifecycleConfigs",
            summary_name="StudioLifecycleConfigDetails",
            resource_cls=StudioLifecycleConfig,
            list_method_kwargs=operation_input_args,
        )


class SubscribedWorkteam(Base):
    """
    SubscribedWorkteam
     Class representing resource SubscribedWorkteam
    Attributes
    ---------------------
    subscribed_workteam:A Workteam instance that contains information about the work team.

    """

    subscribed_workteam: Optional[SubscribedWorkteam] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "subscribed_workteam_name":
                return value
        raise Exception("Name attribute not found for object")

    @classmethod
    def get(
        cls,
        workteam_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["SubscribedWorkteam"]:
        operation_input_args = {
            "WorkteamArn": workteam_arn,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_subscribed_workteam(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeSubscribedWorkteamResponse")
        subscribed_workteam = cls(**transformed_response)
        return subscribed_workteam

    def refresh(self) -> Optional["SubscribedWorkteam"]:

        operation_input_args = {
            "WorkteamArn": self.workteam_arn,
        }
        client = SageMakerClient().client
        response = client.describe_subscribed_workteam(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeSubscribedWorkteamResponse", self)
        return self

    @classmethod
    def get_all(
        cls,
        name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["SubscribedWorkteam"]:
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "NameContains": name_contains,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_subscribed_workteams",
            summaries_key="SubscribedWorkteams",
            summary_name="SubscribedWorkteam",
            resource_cls=SubscribedWorkteam,
            list_method_kwargs=operation_input_args,
        )


class TrainingJob(Base):
    """
    Class representing resource TrainingJob

    Attributes:
        training_job_name: Name of the model training job.
        training_job_arn:The Amazon Resource Name (ARN) of the training job.
        model_artifacts:Information about the Amazon S3 location that is configured for storing model artifacts.
        training_job_status:The status of the training job. SageMaker provides the following training job statuses:    InProgress - The training is in progress.    Completed - The training job has completed.    Failed - The training job has failed. To see the reason for the failure, see the FailureReason field in the response to a DescribeTrainingJobResponse call.    Stopping - The training job is stopping.    Stopped - The training job has stopped.   For more detailed information, see SecondaryStatus.
        secondary_status: Provides detailed information about the state of the training job. For detailed information on the secondary status of the training job, see StatusMessage under SecondaryStatusTransition. SageMaker provides primary statuses and secondary statuses that apply to each of them:  InProgress     Starting - Starting the training job.    Downloading - An optional stage for algorithms that support File training input mode. It indicates that data is being downloaded to the ML storage volumes.    Training - Training is in progress.    Interrupted - The job stopped because the managed spot training instances were interrupted.     Uploading - Training is complete and the model artifacts are being uploaded to the S3 location.    Completed     Completed - The training job has completed.    Failed     Failed - The training job has failed. The reason for the failure is returned in the FailureReason field of DescribeTrainingJobResponse.    Stopped     MaxRuntimeExceeded - The job stopped because it exceeded the maximum allowed runtime.    MaxWaitTimeExceeded - The job stopped because it exceeded the maximum allowed wait time.    Stopped - The training job has stopped.    Stopping     Stopping - Stopping the training job.      Valid values for SecondaryStatus are subject to change.   We no longer support the following secondary statuses:    LaunchingMLInstances     PreparingTraining     DownloadingTrainingImage
        algorithm_specification:Information about the algorithm used for training, and algorithm metadata.
        resource_config:Resources, including ML compute instances and ML storage volumes, that are configured for model training.
        stopping_condition:Specifies a limit to how long a model training job can run. It also specifies how long a managed Spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs. To stop a job, SageMaker sends the algorithm the SIGTERM signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts, so the results of training are not lost.
        creation_time:A timestamp that indicates when the training job was created.
        tuning_job_arn:The Amazon Resource Name (ARN) of the associated hyperparameter tuning job if the training job was launched by a hyperparameter tuning job.
        labeling_job_arn:The Amazon Resource Name (ARN) of the SageMaker Ground Truth labeling job that created the transform or training job.
        auto_m_l_job_arn:The Amazon Resource Name (ARN) of an AutoML job.
        failure_reason:If the training job failed, the reason it failed.
        hyper_parameters:Algorithm-specific parameters.
        role_arn:The Amazon Web Services Identity and Access Management (IAM) role configured for the training job.
        input_data_config:An array of Channel objects that describes each data input channel.
        output_data_config:The S3 path where model artifacts that you configured when creating the job are stored. SageMaker creates subfolders for model artifacts.
        warm_pool_status:The status of the warm pool associated with the training job.
        vpc_config:A VpcConfig object that specifies the VPC that this training job has access to. For more information, see Protect Training Jobs by Using an Amazon Virtual Private Cloud.
        training_start_time:Indicates the time when the training job starts on training instances. You are billed for the time interval between this time and the value of TrainingEndTime. The start time in CloudWatch Logs might be later than this time. The difference is due to the time it takes to download the training data and to the size of the training container.
        training_end_time:Indicates the time when the training job ends on training instances. You are billed for the time interval between the value of TrainingStartTime and this time. For successful jobs and stopped jobs, this is the time after model artifacts are uploaded. For failed jobs, this is the time when SageMaker detects a job failure.
        last_modified_time:A timestamp that indicates when the status of the training job was last modified.
        secondary_status_transitions:A history of all of the secondary statuses that the training job has transitioned through.
        final_metric_data_list:A collection of MetricData objects that specify the names, values, and dates and times that the training algorithm emitted to Amazon CloudWatch.
        enable_network_isolation:If you want to allow inbound or outbound network calls, except for calls between peers within a training cluster for distributed training, choose True. If you enable network isolation for training jobs that are configured to use a VPC, SageMaker downloads and uploads customer data and model artifacts through the specified VPC, but the training container does not have network access.
        enable_inter_container_traffic_encryption:To encrypt all communications between ML compute instances in distributed training, choose True. Encryption provides greater security for distributed training, but training might take longer. How long it takes depends on the amount of communication between compute instances, especially if you use a deep learning algorithms in distributed training.
        enable_managed_spot_training:A Boolean indicating whether managed spot training is enabled (True) or not (False).
        checkpoint_config:
        training_time_in_seconds:The training time in seconds.
        billable_time_in_seconds:The billable time in seconds. Billable time refers to the absolute wall-clock time. Multiply BillableTimeInSeconds by the number of instances (InstanceCount) in your training cluster to get the total compute time SageMaker bills you if you run distributed training. The formula is as follows: BillableTimeInSeconds * InstanceCount . You can calculate the savings from using managed spot training using the formula (1 - BillableTimeInSeconds / TrainingTimeInSeconds) * 100. For example, if BillableTimeInSeconds is 100 and TrainingTimeInSeconds is 500, the savings is 80%.
        debug_hook_config:
        experiment_config:
        debug_rule_configurations:Configuration information for Amazon SageMaker Debugger rules for debugging output tensors.
        tensor_board_output_config:
        debug_rule_evaluation_statuses:Evaluation status of Amazon SageMaker Debugger rules for debugging on a training job.
        profiler_config:
        profiler_rule_configurations:Configuration information for Amazon SageMaker Debugger rules for profiling system and framework metrics.
        profiler_rule_evaluation_statuses:Evaluation status of Amazon SageMaker Debugger rules for profiling on a training job.
        profiling_status:Profiling status of a training job.
        environment:The environment variables to set in the Docker container.
        retry_strategy:The number of times to retry the job when the job fails due to an InternalServerError.
        remote_debug_config:Configuration for remote debugging. To learn more about the remote debugging functionality of SageMaker, see Access a training container through Amazon Web Services Systems Manager (SSM) for remote debugging.
        infra_check_config:Contains information about the infrastructure health check configuration for the training job.

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
            if attribute == "name" or attribute == "training_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "model_artifacts": {"s3_model_artifacts": {"type": "string"}},
                "resource_config": {"volume_kms_key_id": {"type": "string"}},
                "role_arn": {"type": "string"},
                "output_data_config": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "vpc_config": {
                    "security_group_ids": {"type": "array", "items": {"type": "string"}},
                    "subnets": {"type": "array", "items": {"type": "string"}},
                },
                "checkpoint_config": {"s3_uri": {"type": "string"}},
                "debug_hook_config": {"s3_output_path": {"type": "string"}},
                "tensor_board_output_config": {"s3_output_path": {"type": "string"}},
                "profiler_config": {"s3_output_path": {"type": "string"}},
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "TrainingJob", **kwargs
                ),
            )

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
        """
        Create a TrainingJob resource

        Parameters:
            training_job_name:The name of the training job. The name must be unique within an Amazon Web Services Region in an Amazon Web Services account.
            algorithm_specification:The registry path of the Docker image that contains the training algorithm and algorithm-specific metadata, including the input mode. For more information about algorithms provided by SageMaker, see Algorithms. For information about providing your own algorithms, see Using Your Own Algorithms with Amazon SageMaker.
            role_arn:The Amazon Resource Name (ARN) of an IAM role that SageMaker can assume to perform tasks on your behalf.  During model training, SageMaker needs your permission to read input data from an S3 bucket, download a Docker image that contains training code, write model artifacts to an S3 bucket, write logs to Amazon CloudWatch Logs, and publish metrics to Amazon CloudWatch. You grant permissions for all of these tasks to an IAM role. For more information, see SageMaker Roles.   To be able to pass this role to SageMaker, the caller of this API must have the iam:PassRole permission.
            output_data_config:Specifies the path to the S3 location where you want to store model artifacts. SageMaker creates subfolders for the artifacts.
            resource_config:The resources, including the ML compute instances and ML storage volumes, to use for model training.  ML storage volumes store model artifacts and incremental states. Training algorithms might also use ML storage volumes for scratch space. If you want SageMaker to use the ML storage volume to store the training data, choose File as the TrainingInputMode in the algorithm specification. For distributed training algorithms, specify an instance count greater than 1.
            stopping_condition:Specifies a limit to how long a model training job can run. It also specifies how long a managed Spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs. To stop a job, SageMaker sends the algorithm the SIGTERM signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts, so the results of training are not lost.
            hyper_parameters:Algorithm-specific parameters that influence the quality of the model. You set hyperparameters before you start the learning process. For a list of hyperparameters for each training algorithm provided by SageMaker, see Algorithms.  You can specify a maximum of 100 hyperparameters. Each hyperparameter is a key-value pair. Each key and value is limited to 256 characters, as specified by the Length Constraint.   Do not include any security-sensitive information including account access IDs, secrets or tokens in any hyperparameter field. If the use of security-sensitive credentials are detected, SageMaker will reject your training job request and return an exception error.
            input_data_config:An array of Channel objects. Each channel is a named input source. InputDataConfig describes the input data and its location.  Algorithms can accept input data from one or more channels. For example, an algorithm might have two channels of input data, training_data and validation_data. The configuration for each channel provides the S3, EFS, or FSx location where the input data is stored. It also provides information about the stored data: the MIME type, compression method, and whether the data is wrapped in RecordIO format.  Depending on the input mode that the algorithm supports, SageMaker either copies input data files from an S3 bucket to a local directory in the Docker container, or makes it available as input streams. For example, if you specify an EFS location, input data files are available as input streams. They do not need to be downloaded. Your input must be in the same Amazon Web Services region as your training job.
            vpc_config:A VpcConfig object that specifies the VPC that you want your training job to connect to. Control access to and from your training container by configuring the VPC. For more information, see Protect Training Jobs by Using an Amazon Virtual Private Cloud.
            tags:An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see Tagging Amazon Web Services Resources.
            enable_network_isolation:Isolates the training container. No inbound or outbound network calls can be made, except for calls between peers within a training cluster for distributed training. If you enable network isolation for training jobs that are configured to use a VPC, SageMaker downloads and uploads customer data and model artifacts through the specified VPC, but the training container does not have network access.
            enable_inter_container_traffic_encryption:To encrypt all communications between ML compute instances in distributed training, choose True. Encryption provides greater security for distributed training, but training might take longer. How long it takes depends on the amount of communication between compute instances, especially if you use a deep learning algorithm in distributed training. For more information, see Protect Communications Between ML Compute Instances in a Distributed Training Job.
            enable_managed_spot_training:To train models using managed spot training, choose True. Managed spot training provides a fully managed and scalable infrastructure for training machine learning models. this option is useful when training jobs can be interrupted and when there is flexibility when the training job is run.  The complete and intermediate results of jobs are stored in an Amazon S3 bucket, and can be used as a starting point to train models incrementally. Amazon SageMaker provides metrics and logs in CloudWatch. They can be used to see when managed spot training jobs are running, interrupted, resumed, or completed.
            checkpoint_config:Contains information about the output location for managed spot training checkpoint data.
            debug_hook_config:
            debug_rule_configurations:Configuration information for Amazon SageMaker Debugger rules for debugging output tensors.
            tensor_board_output_config:
            experiment_config:
            profiler_config:
            profiler_rule_configurations:Configuration information for Amazon SageMaker Debugger rules for profiling system and framework metrics.
            environment:The environment variables to set in the Docker container.
            retry_strategy:The number of times to retry the job when the job fails due to an InternalServerError.
            remote_debug_config:Configuration for remote debugging. To learn more about the remote debugging functionality of SageMaker, see Access a training container through Amazon Web Services Systems Manager (SSM) for remote debugging.
            infra_check_config:Contains information about the infrastructure health check configuration for the training job.
            session: Boto3 session.
            region: Region name.

        Returns:
            The TrainingJob resource.

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
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating training_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "TrainingJobName": training_job_name,
            "HyperParameters": hyper_parameters,
            "AlgorithmSpecification": algorithm_specification,
            "RoleArn": role_arn,
            "InputDataConfig": input_data_config,
            "OutputDataConfig": output_data_config,
            "ResourceConfig": resource_config,
            "VpcConfig": vpc_config,
            "StoppingCondition": stopping_condition,
            "Tags": tags,
            "EnableNetworkIsolation": enable_network_isolation,
            "EnableInterContainerTrafficEncryption": enable_inter_container_traffic_encryption,
            "EnableManagedSpotTraining": enable_managed_spot_training,
            "CheckpointConfig": checkpoint_config,
            "DebugHookConfig": debug_hook_config,
            "DebugRuleConfigurations": debug_rule_configurations,
            "TensorBoardOutputConfig": tensor_board_output_config,
            "ExperimentConfig": experiment_config,
            "ProfilerConfig": profiler_config,
            "ProfilerRuleConfigurations": profiler_rule_configurations,
            "Environment": environment,
            "RetryStrategy": retry_strategy,
            "RemoteDebugConfig": remote_debug_config,
            "InfraCheckConfig": infra_check_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="TrainingJob", operation_input_args=operation_input_args
        )

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
        """
        Get a TrainingJob resource

        Parameters:
            training_job_name:The name of the training job.
            session: Boto3 session.
            region: Region name.

        Returns:
            The TrainingJob resource.

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
            "TrainingJobName": training_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_training_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeTrainingJobResponse")
        training_job = cls(**transformed_response)
        return training_job

    def refresh(self) -> Optional["TrainingJob"]:
        """
        Refresh a TrainingJob resource

        Returns:
            The TrainingJob resource.

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
            "TrainingJobName": self.training_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_training_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeTrainingJobResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        profiler_config: Optional[ProfilerConfigForUpdate] = Unassigned(),
        profiler_rule_configurations: Optional[List[ProfilerRuleConfiguration]] = Unassigned(),
        resource_config: Optional[ResourceConfigForUpdate] = Unassigned(),
        remote_debug_config: Optional[RemoteDebugConfigForUpdate] = Unassigned(),
    ) -> Optional["TrainingJob"]:
        """
        Update a TrainingJob resource


        Returns:
            The TrainingJob resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating training_job resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "TrainingJobName": self.training_job_name,
            "ProfilerConfig": profiler_config,
            "ProfilerRuleConfigurations": profiler_rule_configurations,
            "ResourceConfig": resource_config,
            "RemoteDebugConfig": remote_debug_config,
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
        """
        Stop a TrainingJob resource


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
            "TrainingJobName": self.training_job_name,
        }
        client.stop_training_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["TrainingJob"]:
        """
        Wait for a TrainingJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The TrainingJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.training_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="TrainingJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all TrainingJob resources

        Parameters:
            next_token:If the result of the previous ListTrainingJobs request was truncated, the response includes a NextToken. To retrieve the next set of training jobs, use the token in the next request.
            max_results:The maximum number of training jobs to return in the response.
            creation_time_after:A filter that returns only training jobs created after the specified time (timestamp).
            creation_time_before:A filter that returns only training jobs created before the specified time (timestamp).
            last_modified_time_after:A filter that returns only training jobs modified after the specified time (timestamp).
            last_modified_time_before:A filter that returns only training jobs modified before the specified time (timestamp).
            name_contains:A string in the training job name. This filter returns only training jobs whose name contains the specified string.
            status_equals:A filter that retrieves only training jobs with a specific status.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            warm_pool_status_equals:A filter that retrieves only training jobs with a specific warm pool status.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed TrainingJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "WarmPoolStatusEquals": warm_pool_status_equals,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_training_jobs",
            summaries_key="TrainingJobSummaries",
            summary_name="TrainingJobSummary",
            resource_cls=TrainingJob,
            list_method_kwargs=operation_input_args,
        )


class TransformJob(Base):
    """
    Class representing resource TransformJob

    Attributes:
        transform_job_name:The name of the transform job.
        transform_job_arn:The Amazon Resource Name (ARN) of the transform job.
        transform_job_status:The status of the transform job. If the transform job failed, the reason is returned in the FailureReason field.
        model_name:The name of the model used in the transform job.
        transform_input:Describes the dataset to be transformed and the Amazon S3 location where it is stored.
        transform_resources:Describes the resources, including ML instance types and ML instance count, to use for the transform job.
        creation_time:A timestamp that shows when the transform Job was created.
        failure_reason:If the transform job failed, FailureReason describes why it failed. A transform job creates a log file, which includes error messages, and stores it as an Amazon S3 object. For more information, see Log Amazon SageMaker Events with Amazon CloudWatch.
        max_concurrent_transforms:The maximum number of parallel requests on each instance node that can be launched in a transform job. The default value is 1.
        model_client_config:The timeout and maximum number of retries for processing a transform job invocation.
        max_payload_in_m_b:The maximum payload size, in MB, used in the transform job.
        batch_strategy:Specifies the number of records to include in a mini-batch for an HTTP inference request. A record  is a single unit of input data that inference can be made on. For example, a single line in a CSV file is a record.  To enable the batch strategy, you must set SplitType to Line, RecordIO, or TFRecord.
        environment:The environment variables to set in the Docker container. We support up to 16 key and values entries in the map.
        transform_output:Identifies the Amazon S3 location where you want Amazon SageMaker to save the results from the transform job.
        data_capture_config:Configuration to control how SageMaker captures inference data.
        transform_start_time:Indicates when the transform job starts on ML instances. You are billed for the time interval between this time and the value of TransformEndTime.
        transform_end_time:Indicates when the transform job has been completed, or has stopped or failed. You are billed for the time interval between this time and the value of TransformStartTime.
        labeling_job_arn:The Amazon Resource Name (ARN) of the Amazon SageMaker Ground Truth labeling job that created the transform or training job.
        auto_m_l_job_arn:The Amazon Resource Name (ARN) of the AutoML transform job.
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
            if attribute == "name" or attribute == "transform_job_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "transform_input": {
                    "data_source": {
                        "s3_data_source": {
                            "s3_data_type": {"type": "string"},
                            "s3_uri": {"type": "string"},
                        }
                    }
                },
                "transform_resources": {"volume_kms_key_id": {"type": "string"}},
                "transform_output": {
                    "s3_output_path": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
                "data_capture_config": {
                    "destination_s3_uri": {"type": "string"},
                    "kms_key_id": {"type": "string"},
                },
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "TransformJob", **kwargs
                ),
            )

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
        """
        Create a TransformJob resource

        Parameters:
            transform_job_name:The name of the transform job. The name must be unique within an Amazon Web Services Region in an Amazon Web Services account.
            model_name:The name of the model that you want to use for the transform job. ModelName must be the name of an existing Amazon SageMaker model within an Amazon Web Services Region in an Amazon Web Services account.
            transform_input:Describes the input source and the way the transform job consumes it.
            transform_output:Describes the results of the transform job.
            transform_resources:Describes the resources, including ML instance types and ML instance count, to use for the transform job.
            max_concurrent_transforms:The maximum number of parallel requests that can be sent to each instance in a transform job. If MaxConcurrentTransforms is set to 0 or left unset, Amazon SageMaker checks the optional execution-parameters to determine the settings for your chosen algorithm. If the execution-parameters endpoint is not enabled, the default value is 1. For more information on execution-parameters, see How Containers Serve Requests. For built-in algorithms, you don't need to set a value for MaxConcurrentTransforms.
            model_client_config:Configures the timeout and maximum number of retries for processing a transform job invocation.
            max_payload_in_m_b:The maximum allowed size of the payload, in MB. A payload is the data portion of a record (without metadata). The value in MaxPayloadInMB must be greater than, or equal to, the size of a single record. To estimate the size of a record in MB, divide the size of your dataset by the number of records. To ensure that the records fit within the maximum payload size, we recommend using a slightly larger value. The default value is 6 MB.  The value of MaxPayloadInMB cannot be greater than 100 MB. If you specify the MaxConcurrentTransforms parameter, the value of (MaxConcurrentTransforms * MaxPayloadInMB) also cannot exceed 100 MB. For cases where the payload might be arbitrarily large and is transmitted using HTTP chunked encoding, set the value to 0. This feature works only in supported algorithms. Currently, Amazon SageMaker built-in algorithms do not support HTTP chunked encoding.
            batch_strategy:Specifies the number of records to include in a mini-batch for an HTTP inference request. A record  is a single unit of input data that inference can be made on. For example, a single line in a CSV file is a record.  To enable the batch strategy, you must set the SplitType property to Line, RecordIO, or TFRecord. To use only one record when making an HTTP invocation request to a container, set BatchStrategy to SingleRecord and SplitType to Line. To fit as many records in a mini-batch as can fit within the MaxPayloadInMB limit, set BatchStrategy to MultiRecord and SplitType to Line.
            environment:The environment variables to set in the Docker container. We support up to 16 key and values entries in the map.
            data_capture_config:Configuration to control how SageMaker captures inference data.
            data_processing:The data structure used to specify the data to be used for inference in a batch transform job and to associate the data that is relevant to the prediction results in the output. The input filter provided allows you to exclude input data that is not needed for inference in a batch transform job. The output filter provided allows you to include input data relevant to interpreting the predictions in the output from the job. For more information, see Associate Prediction Results with their Corresponding Input Records.
            tags:(Optional) An array of key-value pairs. For more information, see Using Cost Allocation Tags in the Amazon Web Services Billing and Cost Management User Guide.
            experiment_config:
            session: Boto3 session.
            region: Region name.

        Returns:
            The TransformJob resource.

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
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating transform_job resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "TransformJobName": transform_job_name,
            "ModelName": model_name,
            "MaxConcurrentTransforms": max_concurrent_transforms,
            "ModelClientConfig": model_client_config,
            "MaxPayloadInMB": max_payload_in_m_b,
            "BatchStrategy": batch_strategy,
            "Environment": environment,
            "TransformInput": transform_input,
            "TransformOutput": transform_output,
            "DataCaptureConfig": data_capture_config,
            "TransformResources": transform_resources,
            "DataProcessing": data_processing,
            "Tags": tags,
            "ExperimentConfig": experiment_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="TransformJob", operation_input_args=operation_input_args
        )

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
        """
        Get a TransformJob resource

        Parameters:
            transform_job_name:The name of the transform job that you want to view details of.
            session: Boto3 session.
            region: Region name.

        Returns:
            The TransformJob resource.

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
            "TransformJobName": transform_job_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_transform_job(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeTransformJobResponse")
        transform_job = cls(**transformed_response)
        return transform_job

    def refresh(self) -> Optional["TransformJob"]:
        """
        Refresh a TransformJob resource

        Returns:
            The TransformJob resource.

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
            "TransformJobName": self.transform_job_name,
        }
        client = SageMakerClient().client
        response = client.describe_transform_job(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeTransformJobResponse", self)
        return self

    def stop(self) -> None:
        """
        Stop a TransformJob resource


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
            "TransformJobName": self.transform_job_name,
        }
        client.stop_transform_job(**operation_input_args)

    def wait(self, poll: int = 5, timeout: Optional[int] = None) -> Optional["TransformJob"]:
        """
        Wait for a TransformJob resource.

        Parameters:
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The TransformJob resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        terminal_states = ["Completed", "Failed", "Stopped"]
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.transform_job_status

            if current_status in terminal_states:

                if "failed" in current_status.lower():
                    raise FailedStatusError(
                        resource_type="TransformJob",
                        status=current_status,
                        reason=self.failure_reason,
                    )

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
        """
        Get all TransformJob resources

        Parameters:
            creation_time_after:A filter that returns only transform jobs created after the specified time.
            creation_time_before:A filter that returns only transform jobs created before the specified time.
            last_modified_time_after:A filter that returns only transform jobs modified after the specified time.
            last_modified_time_before:A filter that returns only transform jobs modified before the specified time.
            name_contains:A string in the transform job name. This filter returns only transform jobs whose name contains the specified string.
            status_equals:A filter that retrieves only transform jobs with a specific status.
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Descending.
            next_token:If the result of the previous ListTransformJobs request was truncated, the response includes a NextToken. To retrieve the next set of transform jobs, use the token in the next request.
            max_results:The maximum number of transform jobs to return in the response. The default value is 10.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed TransformJob resources.

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
            "LastModifiedTimeAfter": last_modified_time_after,
            "LastModifiedTimeBefore": last_modified_time_before,
            "NameContains": name_contains,
            "StatusEquals": status_equals,
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
            list_method="list_transform_jobs",
            summaries_key="TransformJobSummaries",
            summary_name="TransformJobSummary",
            resource_cls=TransformJob,
            list_method_kwargs=operation_input_args,
        )


class Trial(Base):
    """
    Class representing resource Trial

    Attributes:
        trial_name:The name of the trial.
        trial_arn:The Amazon Resource Name (ARN) of the trial.
        display_name:The name of the trial as displayed. If DisplayName isn't specified, TrialName is displayed.
        experiment_name:The name of the experiment the trial is part of.
        source:The Amazon Resource Name (ARN) of the source and, optionally, the job type.
        creation_time:When the trial was created.
        created_by:Who created the trial.
        last_modified_time:When the trial was last modified.
        last_modified_by:Who last modified the trial.
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
            if attribute == "name" or attribute == "trial_name":
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
        """
        Create a Trial resource

        Parameters:
            trial_name:The name of the trial. The name must be unique in your Amazon Web Services account and is not case-sensitive.
            experiment_name:The name of the experiment to associate the trial with.
            display_name:The name of the trial as displayed. The name doesn't need to be unique. If DisplayName isn't specified, TrialName is displayed.
            metadata_properties:
            tags:A list of tags to associate with the trial. You can use Search API to search on the tags.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Trial resource.

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
            ResourceNotFound: Resource being access is not found.
            ConfigSchemaValidationError: Raised when a configuration file does not adhere to the schema
            LocalConfigNotFoundError: Raised when a configuration file is not found in local file system
            S3ConfigNotFoundError: Raised when a configuration file is not found in S3
        """

        logger.debug("Creating trial resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "TrialName": trial_name,
            "DisplayName": display_name,
            "ExperimentName": experiment_name,
            "MetadataProperties": metadata_properties,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Trial", operation_input_args=operation_input_args
        )

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
        """
        Get a Trial resource

        Parameters:
            trial_name:The name of the trial to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Trial resource.

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
            "TrialName": trial_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_trial(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeTrialResponse")
        trial = cls(**transformed_response)
        return trial

    def refresh(self) -> Optional["Trial"]:
        """
        Refresh a Trial resource

        Returns:
            The Trial resource.

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
            "TrialName": self.trial_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeTrialResponse", self)
        return self

    def update(
        self,
        display_name: Optional[str] = Unassigned(),
    ) -> Optional["Trial"]:
        """
        Update a Trial resource


        Returns:
            The Trial resource.

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

        logger.debug("Updating trial resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "TrialName": self.trial_name,
            "DisplayName": display_name,
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
        """
        Delete a Trial resource


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
            "TrialName": self.trial_name,
        }
        client.delete_trial(**operation_input_args)

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
        """
        Get all Trial resources

        Parameters:
            experiment_name:A filter that returns only trials that are part of the specified experiment.
            trial_component_name:A filter that returns only trials that are associated with the specified trial component.
            created_after:A filter that returns only trials created after the specified time.
            created_before:A filter that returns only trials created before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            max_results:The maximum number of trials to return in the response. The default value is 10.
            next_token:If the previous call to ListTrials didn't return the full set of trials, the call returns a token for getting the next set of trials.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Trial resources.

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
            "ExperimentName": experiment_name,
            "TrialComponentName": trial_component_name,
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
            list_method="list_trials",
            summaries_key="TrialSummaries",
            summary_name="TrialSummary",
            resource_cls=Trial,
            list_method_kwargs=operation_input_args,
        )


class TrialComponent(Base):
    """
    Class representing resource TrialComponent

    Attributes:
        trial_component_name:The name of the trial component.
        trial_component_arn:The Amazon Resource Name (ARN) of the trial component.
        display_name:The name of the component as displayed. If DisplayName isn't specified, TrialComponentName is displayed.
        source:The Amazon Resource Name (ARN) of the source and, optionally, the job type.
        status:The status of the component. States include:   InProgress   Completed   Failed
        start_time:When the component started.
        end_time:When the component ended.
        creation_time:When the component was created.
        created_by:Who created the trial component.
        last_modified_time:When the component was last modified.
        last_modified_by:Who last modified the component.
        parameters:The hyperparameters of the component.
        input_artifacts:The input artifacts of the component.
        output_artifacts:The output artifacts of the component.
        metadata_properties:
        metrics:The metrics for the component.
        lineage_group_arn:The Amazon Resource Name (ARN) of the lineage group.
        sources:A list of ARNs and, if applicable, job types for multiple sources of an experiment run.

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
            if attribute == "name" or attribute == "trial_component_name":
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
        """
        Create a TrialComponent resource

        Parameters:
            trial_component_name:The name of the component. The name must be unique in your Amazon Web Services account and is not case-sensitive.
            display_name:The name of the component as displayed. The name doesn't need to be unique. If DisplayName isn't specified, TrialComponentName is displayed.
            status:The status of the component. States include:   InProgress   Completed   Failed
            start_time:When the component started.
            end_time:When the component ended.
            parameters:The hyperparameters for the component.
            input_artifacts:The input artifacts for the component. Examples of input artifacts are datasets, algorithms, hyperparameters, source code, and instance types.
            output_artifacts:The output artifacts for the component. Examples of output artifacts are metrics, snapshots, logs, and images.
            metadata_properties:
            tags:A list of tags to associate with the component. You can use Search API to search on the tags.
            session: Boto3 session.
            region: Region name.

        Returns:
            The TrialComponent resource.

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

        logger.debug("Creating trial_component resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "TrialComponentName": trial_component_name,
            "DisplayName": display_name,
            "Status": status,
            "StartTime": start_time,
            "EndTime": end_time,
            "Parameters": parameters,
            "InputArtifacts": input_artifacts,
            "OutputArtifacts": output_artifacts,
            "MetadataProperties": metadata_properties,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="TrialComponent", operation_input_args=operation_input_args
        )

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
        """
        Get a TrialComponent resource

        Parameters:
            trial_component_name:The name of the trial component to describe.
            session: Boto3 session.
            region: Region name.

        Returns:
            The TrialComponent resource.

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
            "TrialComponentName": trial_component_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_trial_component(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeTrialComponentResponse")
        trial_component = cls(**transformed_response)
        return trial_component

    def refresh(self) -> Optional["TrialComponent"]:
        """
        Refresh a TrialComponent resource

        Returns:
            The TrialComponent resource.

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
            "TrialComponentName": self.trial_component_name,
        }
        client = SageMakerClient().client
        response = client.describe_trial_component(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeTrialComponentResponse", self)
        return self

    def update(
        self,
        display_name: Optional[str] = Unassigned(),
        status: Optional[TrialComponentStatus] = Unassigned(),
        start_time: Optional[datetime.datetime] = Unassigned(),
        end_time: Optional[datetime.datetime] = Unassigned(),
        parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned(),
        parameters_to_remove: Optional[List[str]] = Unassigned(),
        input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        input_artifacts_to_remove: Optional[List[str]] = Unassigned(),
        output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned(),
        output_artifacts_to_remove: Optional[List[str]] = Unassigned(),
    ) -> Optional["TrialComponent"]:
        """
        Update a TrialComponent resource

        Parameters:
            parameters_to_remove:The hyperparameters to remove from the component.
            input_artifacts_to_remove:The input artifacts to remove from the component.
            output_artifacts_to_remove:The output artifacts to remove from the component.

        Returns:
            The TrialComponent resource.

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

        logger.debug("Updating trial_component resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "TrialComponentName": self.trial_component_name,
            "DisplayName": display_name,
            "Status": status,
            "StartTime": start_time,
            "EndTime": end_time,
            "Parameters": parameters,
            "ParametersToRemove": parameters_to_remove,
            "InputArtifacts": input_artifacts,
            "InputArtifactsToRemove": input_artifacts_to_remove,
            "OutputArtifacts": output_artifacts,
            "OutputArtifactsToRemove": output_artifacts_to_remove,
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
        """
        Delete a TrialComponent resource


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
            "TrialComponentName": self.trial_component_name,
        }
        client.delete_trial_component(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["InProgress", "Completed", "Failed", "Stopping", "Stopped"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["TrialComponent"]:
        """
        Wait for a TrialComponent resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The TrialComponent resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.status.primary_status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="TrialComponent", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all TrialComponent resources

        Parameters:
            experiment_name:A filter that returns only components that are part of the specified experiment. If you specify ExperimentName, you can't filter by SourceArn or TrialName.
            trial_name:A filter that returns only components that are part of the specified trial. If you specify TrialName, you can't filter by ExperimentName or SourceArn.
            source_arn:A filter that returns only components that have the specified source Amazon Resource Name (ARN). If you specify SourceArn, you can't filter by ExperimentName or TrialName.
            created_after:A filter that returns only components created after the specified time.
            created_before:A filter that returns only components created before the specified time.
            sort_by:The property used to sort results. The default value is CreationTime.
            sort_order:The sort order. The default value is Descending.
            max_results:The maximum number of components to return in the response. The default value is 10.
            next_token:If the previous call to ListTrialComponents didn't return the full set of components, the call returns a token for getting the next set of components.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed TrialComponent resources.

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
            "ExperimentName": experiment_name,
            "TrialName": trial_name,
            "SourceArn": source_arn,
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
            list_method="list_trial_components",
            summaries_key="TrialComponentSummaries",
            summary_name="TrialComponentSummary",
            resource_cls=TrialComponent,
            list_method_kwargs=operation_input_args,
        )

    def associate_trail(
        self,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "TrialComponentName": self.trial_component_name,
            "TrialName": trial_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling associate_trial_component API")
        response = client.associate_trial_component(**operation_input_args)
        logger.debug(f"Response: {response}")

    def disassociate_trail(
        self,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> None:

        operation_input_args = {
            "TrialComponentName": self.trial_component_name,
            "TrialName": trial_name,
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        logger.debug(f"Calling disassociate_trial_component API")
        response = client.disassociate_trial_component(**operation_input_args)
        logger.debug(f"Response: {response}")


class UserProfile(Base):
    """
    Class representing resource UserProfile

    Attributes:
        domain_id:The ID of the domain that contains the profile.
        user_profile_arn:The user profile Amazon Resource Name (ARN).
        user_profile_name:The user profile name.
        home_efs_file_system_uid:The ID of the user's profile in the Amazon Elastic File System volume.
        status:The status.
        last_modified_time:The last modified time.
        creation_time:The creation time.
        failure_reason:The failure reason.
        single_sign_on_user_identifier:The IAM Identity Center user identifier.
        single_sign_on_user_value:The IAM Identity Center user value.
        user_settings:A collection of settings.

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
            if attribute == "name" or attribute == "user_profile_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "user_settings": {
                    "execution_role": {"type": "string"},
                    "security_groups": {"type": "array", "items": {"type": "string"}},
                    "sharing_settings": {
                        "s3_output_path": {"type": "string"},
                        "s3_kms_key_id": {"type": "string"},
                    },
                    "canvas_app_settings": {
                        "time_series_forecasting_settings": {
                            "amazon_forecast_role_arn": {"type": "string"}
                        },
                        "model_register_settings": {
                            "cross_account_model_register_role_arn": {"type": "string"}
                        },
                        "workspace_settings": {
                            "s3_artifact_path": {"type": "string"},
                            "s3_kms_key_id": {"type": "string"},
                        },
                        "generative_ai_settings": {"amazon_bedrock_role_arn": {"type": "string"}},
                    },
                }
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "UserProfile", **kwargs
                ),
            )

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
        """
        Create a UserProfile resource

        Parameters:
            domain_id:The ID of the associated Domain.
            user_profile_name:A name for the UserProfile. This value is not case sensitive.
            single_sign_on_user_identifier:A specifier for the type of value specified in SingleSignOnUserValue. Currently, the only supported value is "UserName". If the Domain's AuthMode is IAM Identity Center, this field is required. If the Domain's AuthMode is not IAM Identity Center, this field cannot be specified.
            single_sign_on_user_value:The username of the associated Amazon Web Services Single Sign-On User for this UserProfile. If the Domain's AuthMode is IAM Identity Center, this field is required, and must match a valid username of a user in your directory. If the Domain's AuthMode is not IAM Identity Center, this field cannot be specified.
            tags:Each tag consists of a key and an optional value. Tag keys must be unique per resource. Tags that you specify for the User Profile are also added to all Apps that the User Profile launches.
            user_settings:A collection of settings.
            session: Boto3 session.
            region: Region name.

        Returns:
            The UserProfile resource.

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

        logger.debug("Creating user_profile resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "DomainId": domain_id,
            "UserProfileName": user_profile_name,
            "SingleSignOnUserIdentifier": single_sign_on_user_identifier,
            "SingleSignOnUserValue": single_sign_on_user_value,
            "Tags": tags,
            "UserSettings": user_settings,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="UserProfile", operation_input_args=operation_input_args
        )

        logger.debug(f"Input request: {operation_input_args}")
        # serialize the input request
        operation_input_args = cls._serialize(operation_input_args)
        logger.debug(f"Serialized input request: {operation_input_args}")

        # create the resource
        response = client.create_user_profile(**operation_input_args)
        logger.debug(f"Response: {response}")

        return cls.get(
            domain_id=domain_id, user_profile_name=user_profile_name, session=session, region=region
        )

    @classmethod
    def get(
        cls,
        domain_id: str,
        user_profile_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional["UserProfile"]:
        """
        Get a UserProfile resource

        Parameters:
            domain_id:The domain ID.
            user_profile_name:The user profile name. This value is not case sensitive.
            session: Boto3 session.
            region: Region name.

        Returns:
            The UserProfile resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "DomainId": domain_id,
            "UserProfileName": user_profile_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_user_profile(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeUserProfileResponse")
        user_profile = cls(**transformed_response)
        return user_profile

    def refresh(self) -> Optional["UserProfile"]:
        """
        Refresh a UserProfile resource

        Returns:
            The UserProfile resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        operation_input_args = {
            "DomainId": self.domain_id,
            "UserProfileName": self.user_profile_name,
        }
        client = SageMakerClient().client
        response = client.describe_user_profile(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeUserProfileResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        user_settings: Optional[UserSettings] = Unassigned(),
    ) -> Optional["UserProfile"]:
        """
        Update a UserProfile resource


        Returns:
            The UserProfile resource.

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
            ResourceNotFound: Resource being access is not found.
        """

        logger.debug("Updating user_profile resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "DomainId": self.domain_id,
            "UserProfileName": self.user_profile_name,
            "UserSettings": user_settings,
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
        """
        Delete a UserProfile resource


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
        }
        client.delete_user_profile(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal[
            "Deleting",
            "Failed",
            "InService",
            "Pending",
            "Updating",
            "Update_Failed",
            "Delete_Failed",
        ],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["UserProfile"]:
        """
        Wait for a UserProfile resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The UserProfile resource.

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
                    resource_type="UserProfile", status=current_status, reason=self.failure_reason
                )

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
        """
        Get all UserProfile resources

        Parameters:
            next_token:If the previous response was truncated, you will receive this token. Use it in your next request to receive the next set of results.
            max_results:The total number of items to return in the response. If the total number of items available is more than the value specified, a NextToken is provided in the response. To resume pagination, provide the NextToken value in the as part of a subsequent call. The default value is 10.
            sort_order:The sort order for the results. The default is Ascending.
            sort_by:The parameter by which to sort the results. The default is CreationTime.
            domain_id_equals:A parameter by which to filter the results.
            user_profile_name_contains:A parameter by which to filter the results.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed UserProfile resources.

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
            "UserProfileNameContains": user_profile_name_contains,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_user_profiles",
            summaries_key="UserProfiles",
            summary_name="UserProfileDetails",
            resource_cls=UserProfile,
            list_method_kwargs=operation_input_args,
        )


class Workforce(Base):
    """
    Class representing resource Workforce

    Attributes:
        workforce:A single private workforce, which is automatically created when you create your first private work team. You can create one private work force in each Amazon Web Services Region. By default, any workforce-related API operation used in a specific region will apply to the workforce created in that region. To learn how to create a private workforce, see Create a Private Workforce.

    """

    workforce: Optional[Workforce] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "workforce_name":
                return value
        raise Exception("Name attribute not found for object")

    def populate_inputs_decorator(create_func):
        def wrapper(*args, **kwargs):
            config_schema_for_resource = {
                "workforce": {
                    "workforce_vpc_config": {
                        "security_group_ids": {"type": "array", "items": {"type": "string"}},
                        "subnets": {"type": "array", "items": {"type": "string"}},
                    }
                }
            }
            return create_func(
                *args,
                **Base.get_updated_kwargs_with_configured_attributes(
                    config_schema_for_resource, "Workforce", **kwargs
                ),
            )

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
        """
        Create a Workforce resource

        Parameters:
            workforce_name:The name of the private workforce.
            cognito_config:Use this parameter to configure an Amazon Cognito private workforce. A single Cognito workforce is created using and corresponds to a single  Amazon Cognito user pool. Do not use OidcConfig if you specify values for CognitoConfig.
            oidc_config:Use this parameter to configure a private workforce using your own OIDC Identity Provider. Do not use CognitoConfig if you specify values for OidcConfig.
            source_ip_config:
            tags:An array of key-value pairs that contain metadata to help you categorize and organize our workforce. Each tag consists of a key and a value, both of which you define.
            workforce_vpc_config:Use this parameter to configure a workforce using VPC.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Workforce resource.

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

        logger.debug("Creating workforce resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "CognitoConfig": cognito_config,
            "OidcConfig": oidc_config,
            "SourceIpConfig": source_ip_config,
            "WorkforceName": workforce_name,
            "Tags": tags,
            "WorkforceVpcConfig": workforce_vpc_config,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Workforce", operation_input_args=operation_input_args
        )

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
        """
        Get a Workforce resource

        Parameters:
            workforce_name:The name of the private workforce whose access you want to restrict. WorkforceName is automatically set to default when a workforce is created and cannot be modified.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Workforce resource.

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
            "WorkforceName": workforce_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_workforce(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeWorkforceResponse")
        workforce = cls(**transformed_response)
        return workforce

    def refresh(self) -> Optional["Workforce"]:
        """
        Refresh a Workforce resource

        Returns:
            The Workforce resource.

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
            "WorkforceName": self.workforce_name,
        }
        client = SageMakerClient().client
        response = client.describe_workforce(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeWorkforceResponse", self)
        return self

    @populate_inputs_decorator
    def update(
        self,
        workforce_name: str,
        source_ip_config: Optional[SourceIpConfig] = Unassigned(),
        oidc_config: Optional[OidcConfig] = Unassigned(),
        workforce_vpc_config: Optional[WorkforceVpcConfigRequest] = Unassigned(),
    ) -> Optional["Workforce"]:
        """
        Update a Workforce resource

        Parameters:
            workforce_name:The name of the private workforce that you want to update. You can find your workforce name by using the ListWorkforces operation.
            source_ip_config:A list of one to ten worker IP address ranges (CIDRs) that can be used to access tasks assigned to this workforce. Maximum: Ten CIDR values
            oidc_config:Use this parameter to update your OIDC Identity Provider (IdP) configuration for a workforce made using your own IdP.
            workforce_vpc_config:Use this parameter to update your VPC configuration for a workforce.

        Returns:
            The Workforce resource.

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

        logger.debug("Updating workforce resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "WorkforceName": workforce_name,
            "SourceIpConfig": source_ip_config,
            "OidcConfig": oidc_config,
            "WorkforceVpcConfig": workforce_vpc_config,
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
        """
        Delete a Workforce resource


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

        client = SageMakerClient().client

        operation_input_args = {
            "WorkforceName": self.workforce_name,
        }
        client.delete_workforce(**operation_input_args)

    def wait_for_status(
        self,
        status: Literal["Initializing", "Updating", "Deleting", "Failed", "Active"],
        poll: int = 5,
        timeout: Optional[int] = None,
    ) -> Optional["Workforce"]:
        """
        Wait for a Workforce resource.

        Parameters:
            status: The status to wait for.
            poll: The number of seconds to wait between each poll.
            timeout: The maximum number of seconds to wait before timing out.

        Returns:
            The Workforce resource.

        Raises:
            TimeoutExceededError:  If the resource does not reach a terminal state before the timeout.
            FailedStatusError:   If the resource reaches a failed state.
            WaiterError: Raised when an error occurs while waiting.

        """
        start_time = time.time()

        while True:
            self.refresh()
            current_status = self.workforce.status

            if status == current_status:
                return self

            if "failed" in current_status.lower():
                raise FailedStatusError(
                    resource_type="Workforce", status=current_status, reason="(Unknown)"
                )

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
        """
        Get all Workforce resources

        Parameters:
            sort_by:Sort workforces using the workforce name or creation date.
            sort_order:Sort workforces in ascending or descending order.
            name_contains:A filter you can use to search for workforces using part of the workforce name.
            next_token:A token to resume pagination.
            max_results:The maximum number of workforces returned in the response.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Workforce resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_workforces",
            summaries_key="Workforces",
            summary_name="Workforce",
            resource_cls=Workforce,
            list_method_kwargs=operation_input_args,
        )


class Workteam(Base):
    """
    Class representing resource Workteam

    Attributes:
        workteam:A Workteam instance that contains information about the work team.

    """

    workteam: Optional[Workteam] = Unassigned()

    def get_name(self) -> str:
        attributes = vars(self)
        for attribute, value in attributes.items():
            if attribute == "name" or attribute == "workteam_name":
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
        """
        Create a Workteam resource

        Parameters:
            workteam_name:The name of the work team. Use this name to identify the work team.
            member_definitions:A list of MemberDefinition objects that contains objects that identify the workers that make up the work team.  Workforces can be created using Amazon Cognito or your own OIDC Identity Provider (IdP). For private workforces created using Amazon Cognito use CognitoMemberDefinition. For workforces created using your own OIDC identity provider (IdP) use OidcMemberDefinition. Do not provide input for both of these parameters in a single request. For workforces created using Amazon Cognito, private work teams correspond to Amazon Cognito user groups within the user pool used to create a workforce. All of the CognitoMemberDefinition objects that make up the member definition must have the same ClientId and UserPool values. To add a Amazon Cognito user group to an existing worker pool, see Adding groups to a User Pool. For more information about user pools, see Amazon Cognito User Pools. For workforces created using your own OIDC IdP, specify the user groups that you want to include in your private work team in OidcMemberDefinition by listing those groups in Groups.
            description:A description of the work team.
            workforce_name:The name of the workforce.
            notification_configuration:Configures notification of workers regarding available or expiring work items.
            tags:An array of key-value pairs. For more information, see Resource Tag and Using Cost Allocation Tags in the  Amazon Web Services Billing and Cost Management User Guide.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Workteam resource.

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

        logger.debug("Creating workteam resource.")
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        operation_input_args = {
            "WorkteamName": workteam_name,
            "WorkforceName": workforce_name,
            "MemberDefinitions": member_definitions,
            "Description": description,
            "NotificationConfiguration": notification_configuration,
            "Tags": tags,
        }

        operation_input_args = Base.populate_chained_attributes(
            resource_name="Workteam", operation_input_args=operation_input_args
        )

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
        """
        Get a Workteam resource

        Parameters:
            workteam_name:The name of the work team to return a description of.
            session: Boto3 session.
            region: Region name.

        Returns:
            The Workteam resource.

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
            "WorkteamName": workteam_name,
        }
        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client
        response = client.describe_workteam(**operation_input_args)

        pprint(response)

        # deserialize the response
        transformed_response = transform(response, "DescribeWorkteamResponse")
        workteam = cls(**transformed_response)
        return workteam

    def refresh(self) -> Optional["Workteam"]:
        """
        Refresh a Workteam resource

        Returns:
            The Workteam resource.

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
            "WorkteamName": self.workteam_name,
        }
        client = SageMakerClient().client
        response = client.describe_workteam(**operation_input_args)

        # deserialize response and update self
        transform(response, "DescribeWorkteamResponse", self)
        return self

    def update(
        self,
        workteam_name: str,
        member_definitions: Optional[List[MemberDefinition]] = Unassigned(),
        description: Optional[str] = Unassigned(),
        notification_configuration: Optional[NotificationConfiguration] = Unassigned(),
    ) -> Optional["Workteam"]:
        """
        Update a Workteam resource

        Parameters:
            workteam_name:The name of the work team to update.
            member_definitions:A list of MemberDefinition objects that contains objects that identify the workers that make up the work team.  Workforces can be created using Amazon Cognito or your own OIDC Identity Provider (IdP). For private workforces created using Amazon Cognito use CognitoMemberDefinition. For workforces created using your own OIDC identity provider (IdP) use OidcMemberDefinition. You should not provide input for both of these parameters in a single request. For workforces created using Amazon Cognito, private work teams correspond to Amazon Cognito user groups within the user pool used to create a workforce. All of the CognitoMemberDefinition objects that make up the member definition must have the same ClientId and UserPool values. To add a Amazon Cognito user group to an existing worker pool, see Adding groups to a User Pool. For more information about user pools, see Amazon Cognito User Pools. For workforces created using your own OIDC IdP, specify the user groups that you want to include in your private work team in OidcMemberDefinition by listing those groups in Groups. Be aware that user groups that are already in the work team must also be listed in Groups when you make this request to remain on the work team. If you do not include these user groups, they will no longer be associated with the work team you update.
            description:An updated description for the work team.
            notification_configuration:Configures SNS topic notifications for available or expiring work items

        Returns:
            The Workteam resource.

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
        """

        logger.debug("Updating workteam resource.")
        client = SageMakerClient().client

        operation_input_args = {
            "WorkteamName": workteam_name,
            "MemberDefinitions": member_definitions,
            "Description": description,
            "NotificationConfiguration": notification_configuration,
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
        """
        Delete a Workteam resource


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
        """

        client = SageMakerClient().client

        operation_input_args = {
            "WorkteamName": self.workteam_name,
        }
        client.delete_workteam(**operation_input_args)

    @classmethod
    def get_all(
        cls,
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        name_contains: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator["Workteam"]:
        """
        Get all Workteam resources

        Parameters:
            sort_by:The field to sort results by. The default is CreationTime.
            sort_order:The sort order for results. The default is Ascending.
            name_contains:A string in the work team's name. This filter returns only work teams whose name contains the specified string.
            next_token:If the result of the previous ListWorkteams request was truncated, the response includes a NextToken. To retrieve the next set of labeling jobs, use the token in the next request.
            max_results:The maximum number of work teams to return in each page of the response.
            session: Boto3 session.
            region: Region name.

        Returns:
            Iterator for listed Workteam resources.

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
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "NameContains": name_contains,
        }

        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }

        return ResourceIterator(
            client=client,
            list_method="list_workteams",
            summaries_key="Workteams",
            summary_name="Workteam",
            resource_cls=Workteam,
            list_method_kwargs=operation_input_args,
        )

    def get_all_labeling_jobs(
        self,
        workteam_arn: str,
        creation_time_after: Optional[datetime.datetime] = Unassigned(),
        creation_time_before: Optional[datetime.datetime] = Unassigned(),
        job_reference_code_contains: Optional[str] = Unassigned(),
        sort_by: Optional[str] = Unassigned(),
        sort_order: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> ResourceIterator[LabelingJob]:

        operation_input_args = {
            "WorkteamArn": workteam_arn,
            "CreationTimeAfter": creation_time_after,
            "CreationTimeBefore": creation_time_before,
            "JobReferenceCodeContains": job_reference_code_contains,
            "SortBy": sort_by,
            "SortOrder": sort_order,
        }
        operation_input_args = {
            k: v
            for k, v in operation_input_args.items()
            if v is not None and not isinstance(v, Unassigned)
        }
        logger.debug(f"Input request: {operation_input_args}")

        client = SageMakerClient(
            session=session, region_name=region, service_name="sagemaker"
        ).client

        return ResourceIterator(
            client=client,
            list_method="list_labeling_jobs_for_workteam",
            summaries_key="LabelingJobSummaryList",
            summary_name="LabelingJobForWorkteamSummary",
            resource_cls=LabelingJob,
            list_method_kwargs=operation_input_args,
        )
