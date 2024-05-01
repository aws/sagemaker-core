
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
import datetime
import boto3
from pprint import pprint
from pydantic import BaseModel
from typing import List, Dict, Optional
from boto3.session import Session
from utils import Unassigned
from shapes import *

from src.code_injection.codec import deserializer


class Action(BaseModel):
    action_name: Optional[str] = Unassigned()
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
    ) -> Optional[object]:
        action = cls(session, region)
    
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
        response = action.client.create_action(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return action
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        response = self.client.describe_action(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeActionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ActionName': self.action_name,
        }
        self.client.delete_action(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        action_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        action = cls(session, region)
    
        operation_input_args = {
            'ActionName': action_name,
        }
        response = action.client.describe_action(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(action, response, 'DescribeActionResponse')
        return action


class Algorithm(BaseModel):
    algorithm_name: str
    algorithm_arn: str
    creation_time: datetime.datetime
    training_specification: TrainingSpecification
    algorithm_status: str
    algorithm_status_details: AlgorithmStatusDetails
    algorithm_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned()
    product_id: Optional[str] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        algorithm = cls(session, region)
    
        operation_input_args = {
            'AlgorithmName': algorithm_name,
            'AlgorithmDescription': algorithm_description,
            'TrainingSpecification': training_specification,
            'InferenceSpecification': inference_specification,
            'ValidationSpecification': validation_specification,
            'CertifyForMarketplace': certify_for_marketplace,
            'Tags': tags,
        }
        response = algorithm.client.create_algorithm(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return algorithm
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        response = self.client.describe_algorithm(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeAlgorithmOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AlgorithmName': self.algorithm_name,
        }
        self.client.delete_algorithm(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        algorithm_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        algorithm = cls(session, region)
    
        operation_input_args = {
            'AlgorithmName': algorithm_name,
        }
        response = algorithm.client.describe_algorithm(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(algorithm, response, 'DescribeAlgorithmOutput')
        return algorithm


class App(BaseModel):
    app_arn: Optional[str] = Unassigned()
    app_type: Optional[str] = Unassigned()
    app_name: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_health_check_timestamp: Optional[datetime.datetime] = Unassigned()
    last_user_activity_timestamp: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    resource_spec: Optional[ResourceSpec] = Unassigned()
    
    @classmethod
    def create(
        cls,
        domain_id: str,
        app_type: str,
        app_name: str,
        user_profile_name: Optional[str] = Unassigned(),
        space_name: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        resource_spec: Optional[ResourceSpec] = Unassigned(),
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
            'Tags': tags,
            'ResourceSpec': resource_spec,
        }
        response = app.client.create_app(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return app
    
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
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
            'SpaceName': self.space_name,
            'AppType': self.app_type,
            'AppName': self.app_name,
        }
        self.client.delete_app(**operation_input_args)
    
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


class AppImageConfig(BaseModel):
    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        app_image_config_name: str,
        tags: Optional[List[Tag]] = Unassigned(),
        kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned(),
        jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        app_image_config = cls(session, region)
    
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
            'Tags': tags,
            'KernelGatewayImageConfig': kernel_gateway_image_config,
            'JupyterLabAppImageConfig': jupyter_lab_app_image_config,
        }
        response = app_image_config.client.create_app_image_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return app_image_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        response = self.client.describe_app_image_config(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeAppImageConfigResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'AppImageConfigName': self.app_image_config_name,
        }
        self.client.delete_app_image_config(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        app_image_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        app_image_config = cls(session, region)
    
        operation_input_args = {
            'AppImageConfigName': app_image_config_name,
        }
        response = app_image_config.client.describe_app_image_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(app_image_config, response, 'DescribeAppImageConfigResponse')
        return app_image_config


class Artifact(BaseModel):
    artifact_name: Optional[str] = Unassigned()
    artifact_arn: Optional[str] = Unassigned()
    source: Optional[ArtifactSource] = Unassigned()
    artifact_type: Optional[str] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    
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
    ) -> Optional[object]:
        artifact = cls(session, region)
    
        operation_input_args = {
            'ArtifactName': artifact_name,
            'Source': source,
            'ArtifactType': artifact_type,
            'Properties': properties,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        response = artifact.client.create_artifact(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return artifact
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
        }
        response = self.client.describe_artifact(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeArtifactResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ArtifactArn': self.artifact_arn,
            'Source': self.source,
        }
        self.client.delete_artifact(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        artifact_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        artifact = cls(session, region)
    
        operation_input_args = {
            'ArtifactArn': artifact_arn,
        }
        response = artifact.client.describe_artifact(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(artifact, response, 'DescribeArtifactResponse')
        return artifact


class AutoMLJob(BaseModel):
    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    input_data_config: List[AutoMLChannel]
    output_data_config: AutoMLOutputDataConfig
    role_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    auto_m_l_job_config: Optional[AutoMLJobConfig] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    generate_candidate_definitions_only: Optional[bool] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[ResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        auto_m_l_job = cls(session, region)
    
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
        response = auto_m_l_job.client.create_auto_m_l_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return auto_m_l_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        response = self.client.describe_auto_m_l_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeAutoMLJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        self.client.stop_auto_m_l_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        auto_m_l_job = cls(session, region)
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        response = auto_m_l_job.client.describe_auto_m_l_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(auto_m_l_job, response, 'DescribeAutoMLJobResponse')
        return auto_m_l_job


class AutoMLJobV2(BaseModel):
    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    auto_m_l_job_input_data_config: List[AutoMLJobChannel]
    output_data_config: AutoMLOutputDataConfig
    role_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    auto_m_l_problem_type_config: Optional[AutoMLProblemTypeConfig] = Unassigned()
    auto_m_l_problem_type_config_name: Optional[str] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()
    best_candidate: Optional[AutoMLCandidate] = Unassigned()
    auto_m_l_job_artifacts: Optional[AutoMLJobArtifacts] = Unassigned()
    resolved_attributes: Optional[AutoMLResolvedAttributes] = Unassigned()
    model_deploy_config: Optional[ModelDeployConfig] = Unassigned()
    model_deploy_result: Optional[ModelDeployResult] = Unassigned()
    data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned()
    security_config: Optional[AutoMLSecurityConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        auto_m_l_job_name: str,
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
    ) -> Optional[object]:
        auto_m_l_job_v2 = cls(session, region)
    
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
        response = auto_m_l_job_v2.client.create_auto_m_l_job_v2(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return auto_m_l_job_v2
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'AutoMLJobName': self.auto_m_l_job_name,
        }
        response = self.client.describe_auto_m_l_job_v2(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeAutoMLJobV2Response')
        return self
    
    @classmethod
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        auto_m_l_job_v2 = cls(session, region)
    
        operation_input_args = {
            'AutoMLJobName': auto_m_l_job_name,
        }
        response = auto_m_l_job_v2.client.describe_auto_m_l_job_v2(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(auto_m_l_job_v2, response, 'DescribeAutoMLJobV2Response')
        return auto_m_l_job_v2


class Cluster(BaseModel):
    cluster_arn: str
    cluster_status: str
    instance_groups: List[ClusterInstanceGroupDetails]
    cluster_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_message: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        cluster_name: str,
        instance_groups: List[ClusterInstanceGroupSpecification],
        vpc_config: Optional[VpcConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        cluster = cls(session, region)
    
        operation_input_args = {
            'ClusterName': cluster_name,
            'InstanceGroups': instance_groups,
            'VpcConfig': vpc_config,
            'Tags': tags,
        }
        response = cluster.client.create_cluster(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return cluster
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        response = self.client.describe_cluster(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeClusterResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ClusterName': self.cluster_name,
        }
        self.client.delete_cluster(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        cluster_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        cluster = cls(session, region)
    
        operation_input_args = {
            'ClusterName': cluster_name,
        }
        response = cluster.client.describe_cluster(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(cluster, response, 'DescribeClusterResponse')
        return cluster


class CodeRepository(BaseModel):
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        code_repository_name: str,
        git_config: GitConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        code_repository = cls(session, region)
    
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
            'GitConfig': git_config,
            'Tags': tags,
        }
        response = code_repository.client.create_code_repository(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return code_repository
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        response = self.client.describe_code_repository(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeCodeRepositoryOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'CodeRepositoryName': self.code_repository_name,
        }
        self.client.delete_code_repository(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        code_repository_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        code_repository = cls(session, region)
    
        operation_input_args = {
            'CodeRepositoryName': code_repository_name,
        }
        response = code_repository.client.describe_code_repository(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(code_repository, response, 'DescribeCodeRepositoryOutput')
        return code_repository


class CompilationJob(BaseModel):
    compilation_job_name: str
    compilation_job_arn: str
    compilation_job_status: str
    stopping_condition: StoppingCondition
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    failure_reason: str
    model_artifacts: ModelArtifacts
    role_arn: str
    input_config: InputConfig
    output_config: OutputConfig
    compilation_start_time: Optional[datetime.datetime] = Unassigned()
    compilation_end_time: Optional[datetime.datetime] = Unassigned()
    inference_image: Optional[str] = Unassigned()
    model_package_version_arn: Optional[str] = Unassigned()
    model_digests: Optional[ModelDigests] = Unassigned()
    vpc_config: Optional[NeoVpcConfig] = Unassigned()
    derived_information: Optional[DerivedInformation] = Unassigned()
    
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
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'CompilationJobName': self.compilation_job_name,
        }
        response = self.client.describe_compilation_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeCompilationJobResponse')
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
    
    @classmethod
    def get(
        cls,
        compilation_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        compilation_job = cls(session, region)
    
        operation_input_args = {
            'CompilationJobName': compilation_job_name,
        }
        response = compilation_job.client.describe_compilation_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(compilation_job, response, 'DescribeCompilationJobResponse')
        return compilation_job


class Context(BaseModel):
    context_name: Optional[str] = Unassigned()
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
    ) -> Optional[object]:
        context = cls(session, region)
    
        operation_input_args = {
            'ContextName': context_name,
            'Source': source,
            'ContextType': context_type,
            'Description': description,
            'Properties': properties,
            'Tags': tags,
        }
        response = context.client.create_context(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return context
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        response = self.client.describe_context(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeContextResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ContextName': self.context_name,
        }
        self.client.delete_context(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        context_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        context = cls(session, region)
    
        operation_input_args = {
            'ContextName': context_name,
        }
        response = context.client.describe_context(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(context, response, 'DescribeContextResponse')
        return context


class DataQualityJobDefinition(BaseModel):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    data_quality_app_specification: DataQualityAppSpecification
    data_quality_job_input: DataQualityJobInput
    data_quality_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    data_quality_baseline_config: Optional[DataQualityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        data_quality_job_definition = cls(session, region)
    
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
        response = data_quality_job_definition.client.create_data_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return data_quality_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        response = self.client.describe_data_quality_job_definition(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeDataQualityJobDefinitionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_data_quality_job_definition(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        data_quality_job_definition = cls(session, region)
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        response = data_quality_job_definition.client.describe_data_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(data_quality_job_definition, response, 'DescribeDataQualityJobDefinitionResponse')
        return data_quality_job_definition


class DeviceFleet(BaseModel):
    device_fleet_name: str
    device_fleet_arn: str
    output_config: EdgeOutputConfig
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    iot_role_alias: Optional[str] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        device_fleet = cls(session, region)
    
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
            'RoleArn': role_arn,
            'Description': description,
            'OutputConfig': output_config,
            'Tags': tags,
            'EnableIotRoleAlias': enable_iot_role_alias,
        }
        response = device_fleet.client.create_device_fleet(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return device_fleet
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        response = self.client.describe_device_fleet(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeDeviceFleetResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DeviceFleetName': self.device_fleet_name,
        }
        self.client.delete_device_fleet(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        device_fleet_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        device_fleet = cls(session, region)
    
        operation_input_args = {
            'DeviceFleetName': device_fleet_name,
        }
        response = device_fleet.client.describe_device_fleet(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(device_fleet, response, 'DescribeDeviceFleetResponse')
        return device_fleet


class Domain(BaseModel):
    domain_arn: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
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
    
    @classmethod
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
    ) -> Optional[object]:
        domain = cls(session, region)
    
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
        response = domain.client.create_domain(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return domain
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
        }
        response = self.client.describe_domain(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeDomainResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'RetentionPolicy': self.retention_policy,
        }
        self.client.delete_domain(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        domain = cls(session, region)
    
        operation_input_args = {
            'DomainId': domain_id,
        }
        response = domain.client.describe_domain(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(domain, response, 'DescribeDomainResponse')
        return domain


class EdgeDeploymentPlan(BaseModel):
    edge_deployment_plan_arn: str
    edge_deployment_plan_name: str
    model_configs: List[EdgeDeploymentModelConfig]
    device_fleet_name: str
    stages: List[DeploymentStageStatusSummary]
    edge_deployment_success: Optional[int] = Unassigned()
    edge_deployment_pending: Optional[int] = Unassigned()
    edge_deployment_failed: Optional[int] = Unassigned()
    next_token: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    
    @classmethod
    def create(
        cls,
        edge_deployment_plan_name: str,
        model_configs: List[EdgeDeploymentModelConfig],
        device_fleet_name: str,
        stages: Optional[List[DeploymentStage]] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_deployment_plan = cls(session, region)
    
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'ModelConfigs': model_configs,
            'DeviceFleetName': device_fleet_name,
            'Stages': stages,
            'Tags': tags,
        }
        response = edge_deployment_plan.client.create_edge_deployment_plan(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return edge_deployment_plan
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
            'NextToken': self.next_token,
            'MaxResults': self.max_results,
        }
        response = self.client.describe_edge_deployment_plan(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeEdgeDeploymentPlanResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EdgeDeploymentPlanName': self.edge_deployment_plan_name,
        }
        self.client.delete_edge_deployment_plan(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        edge_deployment_plan_name: str,
        next_token: Optional[str] = Unassigned(),
        max_results: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_deployment_plan = cls(session, region)
    
        operation_input_args = {
            'EdgeDeploymentPlanName': edge_deployment_plan_name,
            'NextToken': next_token,
            'MaxResults': max_results,
        }
        response = edge_deployment_plan.client.describe_edge_deployment_plan(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(edge_deployment_plan, response, 'DescribeEdgeDeploymentPlanResponse')
        return edge_deployment_plan


class EdgePackagingJob(BaseModel):
    edge_packaging_job_arn: str
    edge_packaging_job_name: str
    edge_packaging_job_status: str
    compilation_job_name: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    model_version: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    output_config: Optional[EdgeOutputConfig] = Unassigned()
    resource_key: Optional[str] = Unassigned()
    edge_packaging_job_status_message: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    model_artifact: Optional[str] = Unassigned()
    model_signature: Optional[str] = Unassigned()
    preset_deployment_output: Optional[EdgePresetDeploymentOutput] = Unassigned()
    
    @classmethod
    def create(
        cls,
        edge_packaging_job_name: str,
        compilation_job_name: str,
        model_name: str,
        model_version: str,
        role_arn: str,
        output_config: EdgeOutputConfig,
        resource_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_packaging_job = cls(session, region)
    
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
        response = edge_packaging_job.client.create_edge_packaging_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return edge_packaging_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        response = self.client.describe_edge_packaging_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeEdgePackagingJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'EdgePackagingJobName': self.edge_packaging_job_name,
        }
        self.client.stop_edge_packaging_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        edge_packaging_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_packaging_job = cls(session, region)
    
        operation_input_args = {
            'EdgePackagingJobName': edge_packaging_job_name,
        }
        response = edge_packaging_job.client.describe_edge_packaging_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(edge_packaging_job, response, 'DescribeEdgePackagingJobResponse')
        return edge_packaging_job


class Endpoint(BaseModel):
    endpoint_name: str
    endpoint_arn: str
    endpoint_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_config_name: Optional[str] = Unassigned()
    production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    last_deployment_config: Optional[DeploymentConfig] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    pending_deployment_summary: Optional[PendingDeploymentSummary] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    
    @classmethod
    def create(
        cls,
        endpoint_name: str,
        endpoint_config_name: str,
        deployment_config: Optional[DeploymentConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        endpoint = cls(session, region)
    
        operation_input_args = {
            'EndpointName': endpoint_name,
            'EndpointConfigName': endpoint_config_name,
            'DeploymentConfig': deployment_config,
            'Tags': tags,
        }
        response = endpoint.client.create_endpoint(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return endpoint
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        response = self.client.describe_endpoint(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeEndpointOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointName': self.endpoint_name,
        }
        self.client.delete_endpoint(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        endpoint_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        endpoint = cls(session, region)
    
        operation_input_args = {
            'EndpointName': endpoint_name,
        }
        response = endpoint.client.describe_endpoint(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(endpoint, response, 'DescribeEndpointOutput')
        return endpoint


class EndpointConfig(BaseModel):
    endpoint_config_name: str
    endpoint_config_arn: str
    production_variants: List[ProductionVariant]
    creation_time: datetime.datetime
    data_capture_config: Optional[DataCaptureConfig] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariant]] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        endpoint_config = cls(session, region)
    
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
        response = endpoint_config.client.create_endpoint_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return endpoint_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        response = self.client.describe_endpoint_config(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeEndpointConfigOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'EndpointConfigName': self.endpoint_config_name,
        }
        self.client.delete_endpoint_config(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        endpoint_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        endpoint_config = cls(session, region)
    
        operation_input_args = {
            'EndpointConfigName': endpoint_config_name,
        }
        response = endpoint_config.client.describe_endpoint_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(endpoint_config, response, 'DescribeEndpointConfigOutput')
        return endpoint_config


class Experiment(BaseModel):
    experiment_name: Optional[str] = Unassigned()
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    @classmethod
    def create(
        cls,
        experiment_name: str,
        display_name: Optional[str] = Unassigned(),
        description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        experiment = cls(session, region)
    
        operation_input_args = {
            'ExperimentName': experiment_name,
            'DisplayName': display_name,
            'Description': description,
            'Tags': tags,
        }
        response = experiment.client.create_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return experiment
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        response = self.client.describe_experiment(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeExperimentResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ExperimentName': self.experiment_name,
        }
        self.client.delete_experiment(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        experiment_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        experiment = cls(session, region)
    
        operation_input_args = {
            'ExperimentName': experiment_name,
        }
        response = experiment.client.describe_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(experiment, response, 'DescribeExperimentResponse')
        return experiment


class FeatureGroup(BaseModel):
    feature_group_arn: str
    feature_group_name: str
    record_identifier_feature_name: str
    event_time_feature_name: str
    feature_definitions: List[FeatureDefinition]
    creation_time: datetime.datetime
    next_token: str
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
    online_store_total_size_bytes: Optional[int] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        feature_group = cls(session, region)
    
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
        response = feature_group.client.create_feature_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return feature_group
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
            'NextToken': self.next_token,
        }
        response = self.client.describe_feature_group(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeFeatureGroupResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FeatureGroupName': self.feature_group_name,
        }
        self.client.delete_feature_group(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        feature_group_name: str,
        next_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        feature_group = cls(session, region)
    
        operation_input_args = {
            'FeatureGroupName': feature_group_name,
            'NextToken': next_token,
        }
        response = feature_group.client.describe_feature_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(feature_group, response, 'DescribeFeatureGroupResponse')
        return feature_group


class FlowDefinition(BaseModel):
    flow_definition_arn: str
    flow_definition_name: str
    flow_definition_status: str
    creation_time: datetime.datetime
    output_config: FlowDefinitionOutputConfig
    role_arn: str
    human_loop_request_source: Optional[HumanLoopRequestSource] = Unassigned()
    human_loop_activation_config: Optional[HumanLoopActivationConfig] = Unassigned()
    human_loop_config: Optional[HumanLoopConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        flow_definition = cls(session, region)
    
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
            'HumanLoopRequestSource': human_loop_request_source,
            'HumanLoopActivationConfig': human_loop_activation_config,
            'HumanLoopConfig': human_loop_config,
            'OutputConfig': output_config,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        response = flow_definition.client.create_flow_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return flow_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        response = self.client.describe_flow_definition(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeFlowDefinitionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'FlowDefinitionName': self.flow_definition_name,
        }
        self.client.delete_flow_definition(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        flow_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        flow_definition = cls(session, region)
    
        operation_input_args = {
            'FlowDefinitionName': flow_definition_name,
        }
        response = flow_definition.client.describe_flow_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(flow_definition, response, 'DescribeFlowDefinitionResponse')
        return flow_definition


class Hub(BaseModel):
    hub_name: str
    hub_arn: str
    hub_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    hub_display_name: Optional[str] = Unassigned()
    hub_description: Optional[str] = Unassigned()
    hub_search_keywords: Optional[List[str]] = Unassigned()
    s3_storage_config: Optional[HubS3StorageConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        hub = cls(session, region)
    
        operation_input_args = {
            'HubName': hub_name,
            'HubDescription': hub_description,
            'HubDisplayName': hub_display_name,
            'HubSearchKeywords': hub_search_keywords,
            'S3StorageConfig': s3_storage_config,
            'Tags': tags,
        }
        response = hub.client.create_hub(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return hub
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        response = self.client.describe_hub(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeHubResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
        }
        self.client.delete_hub(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        hub = cls(session, region)
    
        operation_input_args = {
            'HubName': hub_name,
        }
        response = hub.client.describe_hub(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(hub, response, 'DescribeHubResponse')
        return hub


class HubContent(BaseModel):
    hub_content_name: str
    hub_content_arn: str
    hub_content_version: str
    hub_content_type: str
    document_schema_version: str
    hub_name: str
    hub_arn: str
    hub_content_document: str
    hub_content_status: str
    creation_time: datetime.datetime
    hub_content_display_name: Optional[str] = Unassigned()
    hub_content_description: Optional[str] = Unassigned()
    hub_content_markdown: Optional[str] = Unassigned()
    hub_content_search_keywords: Optional[List[str]] = Unassigned()
    hub_content_dependencies: Optional[List[HubContentDependency]] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        response = self.client.describe_hub_content(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeHubContentResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HubName': self.hub_name,
            'HubContentType': self.hub_content_type,
            'HubContentName': self.hub_content_name,
            'HubContentVersion': self.hub_content_version,
        }
        self.client.delete_hub_content(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        hub_name: str,
        hub_content_type: str,
        hub_content_name: str,
        hub_content_version: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        hub_content = cls(session, region)
    
        operation_input_args = {
            'HubName': hub_name,
            'HubContentType': hub_content_type,
            'HubContentName': hub_content_name,
            'HubContentVersion': hub_content_version,
        }
        response = hub_content.client.describe_hub_content(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(hub_content, response, 'DescribeHubContentResponse')
        return hub_content


class HumanTaskUi(BaseModel):
    human_task_ui_arn: str
    human_task_ui_name: str
    creation_time: datetime.datetime
    ui_template: UiTemplateInfo
    human_task_ui_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        human_task_ui_name: str,
        ui_template: UiTemplate,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        human_task_ui = cls(session, region)
    
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
            'UiTemplate': ui_template,
            'Tags': tags,
        }
        response = human_task_ui.client.create_human_task_ui(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return human_task_ui
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        response = self.client.describe_human_task_ui(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeHumanTaskUiResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'HumanTaskUiName': self.human_task_ui_name,
        }
        self.client.delete_human_task_ui(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        human_task_ui_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        human_task_ui = cls(session, region)
    
        operation_input_args = {
            'HumanTaskUiName': human_task_ui_name,
        }
        response = human_task_ui.client.describe_human_task_ui(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(human_task_ui, response, 'DescribeHumanTaskUiResponse')
        return human_task_ui


class HyperParameterTuningJob(BaseModel):
    hyper_parameter_tuning_job_name: str
    hyper_parameter_tuning_job_arn: str
    hyper_parameter_tuning_job_config: HyperParameterTuningJobConfig
    hyper_parameter_tuning_job_status: str
    creation_time: datetime.datetime
    training_job_status_counters: TrainingJobStatusCounters
    objective_status_counters: ObjectiveStatusCounters
    training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned()
    training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = Unassigned()
    hyper_parameter_tuning_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    overall_best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned()
    autotune: Optional[Autotune] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    tuning_job_completion_details: Optional[HyperParameterTuningJobCompletionDetails] = Unassigned()
    consumed_resources: Optional[HyperParameterTuningJobConsumedResources] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        hyper_parameter_tuning_job = cls(session, region)
    
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
            'HyperParameterTuningJobConfig': hyper_parameter_tuning_job_config,
            'TrainingJobDefinition': training_job_definition,
            'TrainingJobDefinitions': training_job_definitions,
            'WarmStartConfig': warm_start_config,
            'Tags': tags,
            'Autotune': autotune,
        }
        response = hyper_parameter_tuning_job.client.create_hyper_parameter_tuning_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return hyper_parameter_tuning_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'HyperParameterTuningJobName': self.hyper_parameter_tuning_job_name,
        }
        response = self.client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeHyperParameterTuningJobResponse')
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
    
    @classmethod
    def get(
        cls,
        hyper_parameter_tuning_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        hyper_parameter_tuning_job = cls(session, region)
    
        operation_input_args = {
            'HyperParameterTuningJobName': hyper_parameter_tuning_job_name,
        }
        response = hyper_parameter_tuning_job.client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(hyper_parameter_tuning_job, response, 'DescribeHyperParameterTuningJobResponse')
        return hyper_parameter_tuning_job


class Image(BaseModel):
    creation_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    image_arn: Optional[str] = Unassigned()
    image_name: Optional[str] = Unassigned()
    image_status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        image_name: str,
        role_arn: str,
        description: Optional[str] = Unassigned(),
        display_name: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        image = cls(session, region)
    
        operation_input_args = {
            'Description': description,
            'DisplayName': display_name,
            'ImageName': image_name,
            'RoleArn': role_arn,
            'Tags': tags,
        }
        response = image.client.create_image(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return image
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        response = self.client.describe_image(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeImageResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
        }
        self.client.delete_image(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        image = cls(session, region)
    
        operation_input_args = {
            'ImageName': image_name,
        }
        response = image.client.describe_image(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(image, response, 'DescribeImageResponse')
        return image


class ImageVersion(BaseModel):
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
    
    @classmethod
    def create(
        cls,
        base_image: str,
        client_token: str,
        image_name: str,
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
    ) -> Optional[object]:
        image_version = cls(session, region)
    
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
        response = image_version.client.create_image_version(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return image_version
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        response = self.client.describe_image_version(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeImageVersionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ImageName': self.image_name,
            'Version': self.version,
            'Alias': self.alias,
        }
        self.client.delete_image_version(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        image_name: str,
        version: Optional[int] = Unassigned(),
        alias: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        image_version = cls(session, region)
    
        operation_input_args = {
            'ImageName': image_name,
            'Version': version,
            'Alias': alias,
        }
        response = image_version.client.describe_image_version(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(image_version, response, 'DescribeImageVersionResponse')
        return image_version


class InferenceComponent(BaseModel):
    inference_component_name: str
    inference_component_arn: str
    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    variant_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    specification: Optional[InferenceComponentSpecificationSummary] = Unassigned()
    runtime_config: Optional[InferenceComponentRuntimeConfigSummary] = Unassigned()
    inference_component_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        inference_component_name: str,
        endpoint_name: str,
        variant_name: str,
        specification: InferenceComponentSpecification,
        runtime_config: InferenceComponentRuntimeConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_component = cls(session, region)
    
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
            'EndpointName': endpoint_name,
            'VariantName': variant_name,
            'Specification': specification,
            'RuntimeConfig': runtime_config,
            'Tags': tags,
        }
        response = inference_component.client.create_inference_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return inference_component
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        response = self.client.describe_inference_component(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeInferenceComponentOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'InferenceComponentName': self.inference_component_name,
        }
        self.client.delete_inference_component(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        inference_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_component = cls(session, region)
    
        operation_input_args = {
            'InferenceComponentName': inference_component_name,
        }
        response = inference_component.client.describe_inference_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(inference_component, response, 'DescribeInferenceComponentOutput')
        return inference_component


class InferenceExperiment(BaseModel):
    arn: str
    name: str
    type: str
    status: str
    endpoint_metadata: EndpointMetadata
    model_variants: List[ModelVariantConfigSummary]
    schedule: Optional[InferenceExperimentSchedule] = Unassigned()
    status_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned()
    shadow_mode_config: Optional[ShadowModeConfig] = Unassigned()
    kms_key: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        name: str,
        type: str,
        role_arn: str,
        endpoint_name: str,
        model_variants: List[ModelVariantConfig],
        shadow_mode_config: ShadowModeConfig,
        schedule: Optional[InferenceExperimentSchedule] = Unassigned(),
        description: Optional[str] = Unassigned(),
        data_storage_config: Optional[InferenceExperimentDataStorageConfig] = Unassigned(),
        kms_key: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_experiment = cls(session, region)
    
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
        response = inference_experiment.client.create_inference_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return inference_experiment
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'Name': self.name,
        }
        response = self.client.describe_inference_experiment(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeInferenceExperimentResponse')
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
    
    @classmethod
    def get(
        cls,
        name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_experiment = cls(session, region)
    
        operation_input_args = {
            'Name': name,
        }
        response = inference_experiment.client.describe_inference_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(inference_experiment, response, 'DescribeInferenceExperimentResponse')
        return inference_experiment


class InferenceRecommendationsJob(BaseModel):
    job_name: str
    job_type: str
    job_arn: str
    role_arn: str
    status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    input_config: RecommendationJobInputConfig
    job_description: Optional[str] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    stopping_conditions: Optional[RecommendationJobStoppingConditions] = Unassigned()
    inference_recommendations: Optional[List[InferenceRecommendation]] = Unassigned()
    endpoint_performances: Optional[List[EndpointPerformance]] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        inference_recommendations_job = cls(session, region)
    
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
        response = inference_recommendations_job.client.create_inference_recommendations_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return inference_recommendations_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        response = self.client.describe_inference_recommendations_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeInferenceRecommendationsJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'JobName': self.job_name,
        }
        self.client.stop_inference_recommendations_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_recommendations_job = cls(session, region)
    
        operation_input_args = {
            'JobName': job_name,
        }
        response = inference_recommendations_job.client.describe_inference_recommendations_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(inference_recommendations_job, response, 'DescribeInferenceRecommendationsJobResponse')
        return inference_recommendations_job


class LabelingJob(BaseModel):
    labeling_job_status: str
    label_counters: LabelCounters
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    job_reference_code: str
    labeling_job_name: str
    labeling_job_arn: str
    input_config: LabelingJobInputConfig
    output_config: LabelingJobOutputConfig
    role_arn: str
    human_task_config: HumanTaskConfig
    failure_reason: Optional[str] = Unassigned()
    label_attribute_name: Optional[str] = Unassigned()
    label_category_config_s3_uri: Optional[str] = Unassigned()
    stopping_conditions: Optional[LabelingJobStoppingConditions] = Unassigned()
    labeling_job_algorithms_config: Optional[LabelingJobAlgorithmsConfig] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    labeling_job_output: Optional[LabelingJobOutput] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        labeling_job = cls(session, region)
    
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
        response = labeling_job.client.create_labeling_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return labeling_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        response = self.client.describe_labeling_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeLabelingJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'LabelingJobName': self.labeling_job_name,
        }
        self.client.stop_labeling_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        labeling_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        labeling_job = cls(session, region)
    
        operation_input_args = {
            'LabelingJobName': labeling_job_name,
        }
        response = labeling_job.client.describe_labeling_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(labeling_job, response, 'DescribeLabelingJobResponse')
        return labeling_job


class Model(BaseModel):
    model_name: str
    creation_time: datetime.datetime
    model_arn: str
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[List[ContainerDefinition]] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        model = cls(session, region)
    
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
        response = model.client.create_model(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        response = self.client.describe_model(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelName': self.model_name,
        }
        self.client.delete_model(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        model_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model = cls(session, region)
    
        operation_input_args = {
            'ModelName': model_name,
        }
        response = model.client.describe_model(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model, response, 'DescribeModelOutput')
        return model


class ModelBiasJobDefinition(BaseModel):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_bias_app_specification: ModelBiasAppSpecification
    model_bias_job_input: ModelBiasJobInput
    model_bias_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_bias_baseline_config: Optional[ModelBiasBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        model_bias_job_definition = cls(session, region)
    
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
        response = model_bias_job_definition.client.create_model_bias_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_bias_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        response = self.client.describe_model_bias_job_definition(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelBiasJobDefinitionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_bias_job_definition(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_bias_job_definition = cls(session, region)
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        response = model_bias_job_definition.client.describe_model_bias_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_bias_job_definition, response, 'DescribeModelBiasJobDefinitionResponse')
        return model_bias_job_definition


class ModelCard(BaseModel):
    model_card_arn: str
    model_card_name: str
    model_card_version: int
    content: str
    model_card_status: str
    creation_time: datetime.datetime
    created_by: UserContext
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    model_card_processing_status: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_card_name: str,
        content: str,
        model_card_status: str,
        security_config: Optional[ModelCardSecurityConfig] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card = cls(session, region)
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'SecurityConfig': security_config,
            'Content': content,
            'ModelCardStatus': model_card_status,
            'Tags': tags,
        }
        response = model_card.client.create_model_card(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_card
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
            'ModelCardVersion': self.model_card_version,
        }
        response = self.client.describe_model_card(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelCardResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelCardName': self.model_card_name,
        }
        self.client.delete_model_card(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        model_card_name: str,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card = cls(session, region)
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
        }
        response = model_card.client.describe_model_card(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_card, response, 'DescribeModelCardResponse')
        return model_card


class ModelCardExportJob(BaseModel):
    model_card_export_job_name: str
    model_card_export_job_arn: str
    status: str
    model_card_name: str
    model_card_version: int
    output_config: ModelCardExportOutputConfig
    created_at: datetime.datetime
    last_modified_at: datetime.datetime
    failure_reason: Optional[str] = Unassigned()
    export_artifacts: Optional[ModelCardExportArtifacts] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_card_name: str,
        model_card_export_job_name: str,
        output_config: ModelCardExportOutputConfig,
        model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card_export_job = cls(session, region)
    
        operation_input_args = {
            'ModelCardName': model_card_name,
            'ModelCardVersion': model_card_version,
            'ModelCardExportJobName': model_card_export_job_name,
            'OutputConfig': output_config,
        }
        response = model_card_export_job.client.create_model_card_export_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_card_export_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelCardExportJobArn': self.model_card_export_job_arn,
        }
        response = self.client.describe_model_card_export_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelCardExportJobResponse')
        return self
    
    @classmethod
    def get(
        cls,
        model_card_export_job_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card_export_job = cls(session, region)
    
        operation_input_args = {
            'ModelCardExportJobArn': model_card_export_job_arn,
        }
        response = model_card_export_job.client.describe_model_card_export_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_card_export_job, response, 'DescribeModelCardExportJobResponse')
        return model_card_export_job


class ModelExplainabilityJobDefinition(BaseModel):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_explainability_app_specification: ModelExplainabilityAppSpecification
    model_explainability_job_input: ModelExplainabilityJobInput
    model_explainability_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_explainability_baseline_config: Optional[ModelExplainabilityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        model_explainability_job_definition = cls(session, region)
    
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
        response = model_explainability_job_definition.client.create_model_explainability_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_explainability_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        response = self.client.describe_model_explainability_job_definition(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelExplainabilityJobDefinitionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_explainability_job_definition(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_explainability_job_definition = cls(session, region)
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        response = model_explainability_job_definition.client.describe_model_explainability_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_explainability_job_definition, response, 'DescribeModelExplainabilityJobDefinitionResponse')
        return model_explainability_job_definition


class ModelPackage(BaseModel):
    model_package_name: str
    model_package_arn: str
    creation_time: datetime.datetime
    model_package_status: str
    model_package_status_details: ModelPackageStatusDetails
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned()
    validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned()
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
    
    @classmethod
    def create(
        cls,
        model_package_name: Optional[str] = Unassigned(),
        model_package_group_name: Optional[str] = Unassigned(),
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
    ) -> Optional[object]:
        model_package = cls(session, region)
    
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
        response = model_package.client.create_model_package(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_package
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        response = self.client.describe_model_package(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelPackageOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageName': self.model_package_name,
        }
        self.client.delete_model_package(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        model_package_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_package = cls(session, region)
    
        operation_input_args = {
            'ModelPackageName': model_package_name,
        }
        response = model_package.client.describe_model_package(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_package, response, 'DescribeModelPackageOutput')
        return model_package


class ModelPackageGroup(BaseModel):
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    created_by: UserContext
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        model_package_group_name: str,
        model_package_group_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_package_group = cls(session, region)
    
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
            'ModelPackageGroupDescription': model_package_group_description,
            'Tags': tags,
        }
        response = model_package_group.client.create_model_package_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_package_group
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        response = self.client.describe_model_package_group(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelPackageGroupOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ModelPackageGroupName': self.model_package_group_name,
        }
        self.client.delete_model_package_group(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        model_package_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_package_group = cls(session, region)
    
        operation_input_args = {
            'ModelPackageGroupName': model_package_group_name,
        }
        response = model_package_group.client.describe_model_package_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_package_group, response, 'DescribeModelPackageGroupOutput')
        return model_package_group


class ModelQualityJobDefinition(BaseModel):
    job_definition_arn: str
    job_definition_name: str
    creation_time: datetime.datetime
    model_quality_app_specification: ModelQualityAppSpecification
    model_quality_job_input: ModelQualityJobInput
    model_quality_job_output_config: MonitoringOutputConfig
    job_resources: MonitoringResources
    role_arn: str
    model_quality_baseline_config: Optional[ModelQualityBaselineConfig] = Unassigned()
    network_config: Optional[MonitoringNetworkConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        model_quality_job_definition = cls(session, region)
    
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
        response = model_quality_job_definition.client.create_model_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return model_quality_job_definition
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        response = self.client.describe_model_quality_job_definition(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeModelQualityJobDefinitionResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'JobDefinitionName': self.job_definition_name,
        }
        self.client.delete_model_quality_job_definition(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_quality_job_definition = cls(session, region)
    
        operation_input_args = {
            'JobDefinitionName': job_definition_name,
        }
        response = model_quality_job_definition.client.describe_model_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(model_quality_job_definition, response, 'DescribeModelQualityJobDefinitionResponse')
        return model_quality_job_definition


class MonitoringSchedule(BaseModel):
    monitoring_schedule_arn: str
    monitoring_schedule_name: str
    monitoring_schedule_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    monitoring_schedule_config: MonitoringScheduleConfig
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = Unassigned()
    
    @classmethod
    def create(
        cls,
        monitoring_schedule_name: str,
        monitoring_schedule_config: MonitoringScheduleConfig,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        monitoring_schedule = cls(session, region)
    
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
            'MonitoringScheduleConfig': monitoring_schedule_config,
            'Tags': tags,
        }
        response = monitoring_schedule.client.create_monitoring_schedule(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return monitoring_schedule
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'MonitoringScheduleName': self.monitoring_schedule_name,
        }
        response = self.client.describe_monitoring_schedule(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeMonitoringScheduleResponse')
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
    
    @classmethod
    def get(
        cls,
        monitoring_schedule_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        monitoring_schedule = cls(session, region)
    
        operation_input_args = {
            'MonitoringScheduleName': monitoring_schedule_name,
        }
        response = monitoring_schedule.client.describe_monitoring_schedule(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(monitoring_schedule, response, 'DescribeMonitoringScheduleResponse')
        return monitoring_schedule


class NotebookInstance(BaseModel):
    notebook_instance_arn: Optional[str] = Unassigned()
    notebook_instance_name: Optional[str] = Unassigned()
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
    
    @classmethod
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
    ) -> Optional[object]:
        notebook_instance = cls(session, region)
    
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
        response = notebook_instance.client.create_notebook_instance(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return notebook_instance
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'NotebookInstanceName': self.notebook_instance_name,
        }
        response = self.client.describe_notebook_instance(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeNotebookInstanceOutput')
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
    
    @classmethod
    def get(
        cls,
        notebook_instance_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        notebook_instance = cls(session, region)
    
        operation_input_args = {
            'NotebookInstanceName': notebook_instance_name,
        }
        response = notebook_instance.client.describe_notebook_instance(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(notebook_instance, response, 'DescribeNotebookInstanceOutput')
        return notebook_instance


class NotebookInstanceLifecycleConfig(BaseModel):
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    
    @classmethod
    def create(
        cls,
        notebook_instance_lifecycle_config_name: str,
        on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        notebook_instance_lifecycle_config = cls(session, region)
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
            'OnCreate': on_create,
            'OnStart': on_start,
        }
        response = notebook_instance_lifecycle_config.client.create_notebook_instance_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return notebook_instance_lifecycle_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        response = self.client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeNotebookInstanceLifecycleConfigOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': self.notebook_instance_lifecycle_config_name,
        }
        self.client.delete_notebook_instance_lifecycle_config(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        notebook_instance_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        notebook_instance_lifecycle_config = cls(session, region)
    
        operation_input_args = {
            'NotebookInstanceLifecycleConfigName': notebook_instance_lifecycle_config_name,
        }
        response = notebook_instance_lifecycle_config.client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(notebook_instance_lifecycle_config, response, 'DescribeNotebookInstanceLifecycleConfigOutput')
        return notebook_instance_lifecycle_config


class Pipeline(BaseModel):
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_name: Optional[str] = Unassigned()
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
    
    @classmethod
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
    ) -> Optional[object]:
        pipeline = cls(session, region)
    
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
        response = pipeline.client.create_pipeline(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return pipeline
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
        }
        response = self.client.describe_pipeline(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribePipelineResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'PipelineName': self.pipeline_name,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.delete_pipeline(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        pipeline_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        pipeline = cls(session, region)
    
        operation_input_args = {
            'PipelineName': pipeline_name,
        }
        response = pipeline.client.describe_pipeline(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(pipeline, response, 'DescribePipelineResponse')
        return pipeline


class PipelineExecution(BaseModel):
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_execution_arn: Optional[str] = Unassigned()
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
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
        }
        response = self.client.describe_pipeline_execution(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribePipelineExecutionResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'PipelineExecutionArn': self.pipeline_execution_arn,
            'ClientRequestToken': self.client_request_token,
        }
        self.client.stop_pipeline_execution(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        pipeline_execution_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        pipeline_execution = cls(session, region)
    
        operation_input_args = {
            'PipelineExecutionArn': pipeline_execution_arn,
        }
        response = pipeline_execution.client.describe_pipeline_execution(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(pipeline_execution, response, 'DescribePipelineExecutionResponse')
        return pipeline_execution


class ProcessingJob(BaseModel):
    processing_job_name: str
    processing_resources: ProcessingResources
    app_specification: AppSpecification
    processing_job_arn: str
    processing_job_status: str
    creation_time: datetime.datetime
    processing_inputs: Optional[List[ProcessingInput]] = Unassigned()
    processing_output_config: Optional[ProcessingOutputConfig] = Unassigned()
    stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    network_config: Optional[NetworkConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    exit_message: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    processing_end_time: Optional[datetime.datetime] = Unassigned()
    processing_start_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    training_job_arn: Optional[str] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        processing_job = cls(session, region)
    
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
        response = processing_job.client.create_processing_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return processing_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        response = self.client.describe_processing_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeProcessingJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'ProcessingJobName': self.processing_job_name,
        }
        self.client.stop_processing_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        processing_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        processing_job = cls(session, region)
    
        operation_input_args = {
            'ProcessingJobName': processing_job_name,
        }
        response = processing_job.client.describe_processing_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(processing_job, response, 'DescribeProcessingJobResponse')
        return processing_job


class Project(BaseModel):
    project_arn: str
    project_name: str
    project_id: str
    service_catalog_provisioning_details: ServiceCatalogProvisioningDetails
    project_status: str
    creation_time: datetime.datetime
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioned_product_details: Optional[ServiceCatalogProvisionedProductDetails] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    
    @classmethod
    def create(
        cls,
        project_name: str,
        service_catalog_provisioning_details: ServiceCatalogProvisioningDetails,
        project_description: Optional[str] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        project = cls(session, region)
    
        operation_input_args = {
            'ProjectName': project_name,
            'ProjectDescription': project_description,
            'ServiceCatalogProvisioningDetails': service_catalog_provisioning_details,
            'Tags': tags,
        }
        response = project.client.create_project(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return project
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        response = self.client.describe_project(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeProjectOutput')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'ProjectName': self.project_name,
        }
        self.client.delete_project(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        project_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        project = cls(session, region)
    
        operation_input_args = {
            'ProjectName': project_name,
        }
        response = project.client.describe_project(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(project, response, 'DescribeProjectOutput')
        return project


class Space(BaseModel):
    domain_id: Optional[str] = Unassigned()
    space_arn: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
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
    ) -> Optional[object]:
        space = cls(session, region)
    
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
            'Tags': tags,
            'SpaceSettings': space_settings,
            'OwnershipSettings': ownership_settings,
            'SpaceSharingSettings': space_sharing_settings,
            'SpaceDisplayName': space_display_name,
        }
        response = space.client.create_space(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return space
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        response = self.client.describe_space(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeSpaceResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'SpaceName': self.space_name,
        }
        self.client.delete_space(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        space_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        space = cls(session, region)
    
        operation_input_args = {
            'DomainId': domain_id,
            'SpaceName': space_name,
        }
        response = space.client.describe_space(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(space, response, 'DescribeSpaceResponse')
        return space


class StudioLifecycleConfig(BaseModel):
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_content: Optional[str] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()
    
    @classmethod
    def create(
        cls,
        studio_lifecycle_config_name: str,
        studio_lifecycle_config_content: str,
        studio_lifecycle_config_app_type: str,
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        studio_lifecycle_config = cls(session, region)
    
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
            'StudioLifecycleConfigContent': studio_lifecycle_config_content,
            'StudioLifecycleConfigAppType': studio_lifecycle_config_app_type,
            'Tags': tags,
        }
        response = studio_lifecycle_config.client.create_studio_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return studio_lifecycle_config
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        response = self.client.describe_studio_lifecycle_config(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeStudioLifecycleConfigResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'StudioLifecycleConfigName': self.studio_lifecycle_config_name,
        }
        self.client.delete_studio_lifecycle_config(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        studio_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        studio_lifecycle_config = cls(session, region)
    
        operation_input_args = {
            'StudioLifecycleConfigName': studio_lifecycle_config_name,
        }
        response = studio_lifecycle_config.client.describe_studio_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(studio_lifecycle_config, response, 'DescribeStudioLifecycleConfigResponse')
        return studio_lifecycle_config


class TrainingJob(BaseModel):
    training_job_name: str
    training_job_arn: str
    model_artifacts: ModelArtifacts
    training_job_status: str
    secondary_status: str
    algorithm_specification: AlgorithmSpecification
    resource_config: ResourceConfig
    stopping_condition: StoppingCondition
    creation_time: datetime.datetime
    tuning_job_arn: Optional[str] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    hyper_parameters: Optional[Dict[str, str]] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    input_data_config: Optional[List[Channel]] = Unassigned()
    output_data_config: Optional[OutputDataConfig] = Unassigned()
    warm_pool_status: Optional[WarmPoolStatus] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
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
    
    @classmethod
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
    ) -> Optional[object]:
        training_job = cls(session, region)
    
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
        response = training_job.client.create_training_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return training_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        response = self.client.describe_training_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeTrainingJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TrainingJobName': self.training_job_name,
        }
        self.client.stop_training_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        training_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        training_job = cls(session, region)
    
        operation_input_args = {
            'TrainingJobName': training_job_name,
        }
        response = training_job.client.describe_training_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(training_job, response, 'DescribeTrainingJobResponse')
        return training_job


class TransformJob(BaseModel):
    transform_job_name: str
    transform_job_arn: str
    transform_job_status: str
    model_name: str
    transform_input: TransformInput
    transform_resources: TransformResources
    creation_time: datetime.datetime
    failure_reason: Optional[str] = Unassigned()
    max_concurrent_transforms: Optional[int] = Unassigned()
    model_client_config: Optional[ModelClientConfig] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    transform_output: Optional[TransformOutput] = Unassigned()
    data_capture_config: Optional[BatchDataCaptureConfig] = Unassigned()
    transform_start_time: Optional[datetime.datetime] = Unassigned()
    transform_end_time: Optional[datetime.datetime] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    data_processing: Optional[DataProcessing] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    
    @classmethod
    def create(
        cls,
        transform_job_name: str,
        model_name: str,
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
    ) -> Optional[object]:
        transform_job = cls(session, region)
    
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
        response = transform_job.client.create_transform_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return transform_job
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        response = self.client.describe_transform_job(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeTransformJobResponse')
        return self
    
    def stop(self) -> None:
    
        operation_input_args = {
            'TransformJobName': self.transform_job_name,
        }
        self.client.stop_transform_job(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        transform_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        transform_job = cls(session, region)
    
        operation_input_args = {
            'TransformJobName': transform_job_name,
        }
        response = transform_job.client.describe_transform_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(transform_job, response, 'DescribeTransformJobResponse')
        return transform_job


class Trial(BaseModel):
    trial_name: Optional[str] = Unassigned()
    trial_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    source: Optional[TrialSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    
    @classmethod
    def create(
        cls,
        trial_name: str,
        experiment_name: str,
        display_name: Optional[str] = Unassigned(),
        metadata_properties: Optional[MetadataProperties] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        trial = cls(session, region)
    
        operation_input_args = {
            'TrialName': trial_name,
            'DisplayName': display_name,
            'ExperimentName': experiment_name,
            'MetadataProperties': metadata_properties,
            'Tags': tags,
        }
        response = trial.client.create_trial(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return trial
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        response = self.client.describe_trial(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeTrialResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialName': self.trial_name,
        }
        self.client.delete_trial(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        trial = cls(session, region)
    
        operation_input_args = {
            'TrialName': trial_name,
        }
        response = trial.client.describe_trial(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(trial, response, 'DescribeTrialResponse')
        return trial


class TrialComponent(BaseModel):
    trial_component_name: Optional[str] = Unassigned()
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
    ) -> Optional[object]:
        trial_component = cls(session, region)
    
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
        response = trial_component.client.create_trial_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return trial_component
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        response = self.client.describe_trial_component(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeTrialComponentResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'TrialComponentName': self.trial_component_name,
        }
        self.client.delete_trial_component(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        trial_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        trial_component = cls(session, region)
    
        operation_input_args = {
            'TrialComponentName': trial_component_name,
        }
        response = trial_component.client.describe_trial_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(trial_component, response, 'DescribeTrialComponentResponse')
        return trial_component


class UserProfile(BaseModel):
    domain_id: Optional[str] = Unassigned()
    user_profile_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    home_efs_file_system_uid: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    single_sign_on_user_identifier: Optional[str] = Unassigned()
    single_sign_on_user_value: Optional[str] = Unassigned()
    user_settings: Optional[UserSettings] = Unassigned()
    
    @classmethod
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
    ) -> Optional[object]:
        user_profile = cls(session, region)
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
            'SingleSignOnUserIdentifier': single_sign_on_user_identifier,
            'SingleSignOnUserValue': single_sign_on_user_value,
            'Tags': tags,
            'UserSettings': user_settings,
        }
        response = user_profile.client.create_user_profile(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return user_profile
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        response = self.client.describe_user_profile(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeUserProfileResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'DomainId': self.domain_id,
            'UserProfileName': self.user_profile_name,
        }
        self.client.delete_user_profile(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        domain_id: str,
        user_profile_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        user_profile = cls(session, region)
    
        operation_input_args = {
            'DomainId': domain_id,
            'UserProfileName': user_profile_name,
        }
        response = user_profile.client.describe_user_profile(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(user_profile, response, 'DescribeUserProfileResponse')
        return user_profile


class Workforce(BaseModel):
    workforce: Workforce
    
    @classmethod
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
    ) -> Optional[object]:
        workforce = cls(session, region)
    
        operation_input_args = {
            'CognitoConfig': cognito_config,
            'OidcConfig': oidc_config,
            'SourceIpConfig': source_ip_config,
            'WorkforceName': workforce_name,
            'Tags': tags,
            'WorkforceVpcConfig': workforce_vpc_config,
        }
        response = workforce.client.create_workforce(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return workforce
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        response = self.client.describe_workforce(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeWorkforceResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkforceName': self.workforce_name,
        }
        self.client.delete_workforce(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        workforce_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        workforce = cls(session, region)
    
        operation_input_args = {
            'WorkforceName': workforce_name,
        }
        response = workforce.client.describe_workforce(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(workforce, response, 'DescribeWorkforceResponse')
        return workforce


class Workteam(BaseModel):
    workteam: Workteam
    
    @classmethod
    def create(
        cls,
        workteam_name: str,
        member_definitions: List[MemberDefinition],
        description: str,
        workforce_name: Optional[str] = Unassigned(),
        notification_configuration: Optional[NotificationConfiguration] = Unassigned(),
        tags: Optional[List[Tag]] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        workteam = cls(session, region)
    
        operation_input_args = {
            'WorkteamName': workteam_name,
            'WorkforceName': workforce_name,
            'MemberDefinitions': member_definitions,
            'Description': description,
            'NotificationConfiguration': notification_configuration,
            'Tags': tags,
        }
        response = workteam.client.create_workteam(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
    
        return workteam
    
    def refresh(self) -> Optional[object]:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        response = self.client.describe_workteam(**operation_input_args)
    
        # deserialize the response
        deserializer(self, response, 'DescribeWorkteamResponse')
        return self
    
    def delete(self) -> None:
    
        operation_input_args = {
            'WorkteamName': self.workteam_name,
        }
        self.client.delete_workteam(**operation_input_args)
    
    @classmethod
    def get(
        cls,
        workteam_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        workteam = cls(session, region)
    
        operation_input_args = {
            'WorkteamName': workteam_name,
        }
        response = workteam.client.describe_workteam(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        deserializer(workteam, response, 'DescribeWorkteamResponse')
        return workteam


