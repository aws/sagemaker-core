
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
import pprint
import boto3

from pydantic import BaseModel
from typing import List, Dict, Optional
from boto3.session import Session
from utils import Unassigned
from shapes import *


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
    def get(
        cls,
        action_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        action = cls(session, region)
    
        operation_input_args = {'ActionName': 'action_name'}
        response = action.client.describe_action(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        action.action_name = response["ActionName"]
        action.action_arn = response["ActionArn"]
        action.source = response["Source"]
        action.action_type = response["ActionType"]
        action.description = response["Description"]
        action.status = response["Status"]
        action.properties = response["Properties"]
        action.creation_time = response["CreationTime"]
        action.created_by = response["CreatedBy"]
        action.last_modified_time = response["LastModifiedTime"]
        action.last_modified_by = response["LastModifiedBy"]
        action.metadata_properties = response["MetadataProperties"]
        action.lineage_group_arn = response["LineageGroupArn"]
    
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
    def get(
        cls,
        algorithm_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        algorithm = cls(session, region)
    
        operation_input_args = {'AlgorithmName': 'algorithm_name'}
        response = algorithm.client.describe_algorithm(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        algorithm.algorithm_name = response["AlgorithmName"]
        algorithm.algorithm_arn = response["AlgorithmArn"]
        algorithm.algorithm_description = response["AlgorithmDescription"]
        algorithm.creation_time = response["CreationTime"]
        algorithm.training_specification = response["TrainingSpecification"]
        algorithm.inference_specification = response["InferenceSpecification"]
        algorithm.validation_specification = response["ValidationSpecification"]
        algorithm.algorithm_status = response["AlgorithmStatus"]
        algorithm.algorithm_status_details = response["AlgorithmStatusDetails"]
        algorithm.product_id = response["ProductId"]
        algorithm.certify_for_marketplace = response["CertifyForMarketplace"]
    
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
    
        operation_input_args = {'DomainId': 'domain_id', 'UserProfileName': 'user_profile_name', 'SpaceName': 'space_name', 'AppType': 'app_type', 'AppName': 'app_name'}
        response = app.client.describe_app(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        app.app_arn = response["AppArn"]
        app.app_type = response["AppType"]
        app.app_name = response["AppName"]
        app.domain_id = response["DomainId"]
        app.user_profile_name = response["UserProfileName"]
        app.space_name = response["SpaceName"]
        app.status = response["Status"]
        app.last_health_check_timestamp = response["LastHealthCheckTimestamp"]
        app.last_user_activity_timestamp = response["LastUserActivityTimestamp"]
        app.creation_time = response["CreationTime"]
        app.failure_reason = response["FailureReason"]
        app.resource_spec = response["ResourceSpec"]
    
        return app


class AppImageConfig(BaseModel):
    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()

    
    @classmethod
    def get(
        cls,
        app_image_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        app_image_config = cls(session, region)
    
        operation_input_args = {'AppImageConfigName': 'app_image_config_name'}
        response = app_image_config.client.describe_app_image_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        app_image_config.app_image_config_arn = response["AppImageConfigArn"]
        app_image_config.app_image_config_name = response["AppImageConfigName"]
        app_image_config.creation_time = response["CreationTime"]
        app_image_config.last_modified_time = response["LastModifiedTime"]
        app_image_config.kernel_gateway_image_config = response["KernelGatewayImageConfig"]
        app_image_config.jupyter_lab_app_image_config = response["JupyterLabAppImageConfig"]
    
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
    def get(
        cls,
        artifact_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        artifact = cls(session, region)
    
        operation_input_args = {'ArtifactArn': 'artifact_arn'}
        response = artifact.client.describe_artifact(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        artifact.artifact_name = response["ArtifactName"]
        artifact.artifact_arn = response["ArtifactArn"]
        artifact.source = response["Source"]
        artifact.artifact_type = response["ArtifactType"]
        artifact.properties = response["Properties"]
        artifact.creation_time = response["CreationTime"]
        artifact.created_by = response["CreatedBy"]
        artifact.last_modified_time = response["LastModifiedTime"]
        artifact.last_modified_by = response["LastModifiedBy"]
        artifact.metadata_properties = response["MetadataProperties"]
        artifact.lineage_group_arn = response["LineageGroupArn"]
    
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
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        auto_m_l_job = cls(session, region)
    
        operation_input_args = {'AutoMLJobName': 'auto_m_l_job_name'}
        response = auto_m_l_job.client.describe_auto_m_l_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        auto_m_l_job.auto_m_l_job_name = response["AutoMLJobName"]
        auto_m_l_job.auto_m_l_job_arn = response["AutoMLJobArn"]
        auto_m_l_job.input_data_config = response["InputDataConfig"]
        auto_m_l_job.output_data_config = response["OutputDataConfig"]
        auto_m_l_job.role_arn = response["RoleArn"]
        auto_m_l_job.auto_m_l_job_objective = response["AutoMLJobObjective"]
        auto_m_l_job.problem_type = response["ProblemType"]
        auto_m_l_job.auto_m_l_job_config = response["AutoMLJobConfig"]
        auto_m_l_job.creation_time = response["CreationTime"]
        auto_m_l_job.end_time = response["EndTime"]
        auto_m_l_job.last_modified_time = response["LastModifiedTime"]
        auto_m_l_job.failure_reason = response["FailureReason"]
        auto_m_l_job.partial_failure_reasons = response["PartialFailureReasons"]
        auto_m_l_job.best_candidate = response["BestCandidate"]
        auto_m_l_job.auto_m_l_job_status = response["AutoMLJobStatus"]
        auto_m_l_job.auto_m_l_job_secondary_status = response["AutoMLJobSecondaryStatus"]
        auto_m_l_job.generate_candidate_definitions_only = response["GenerateCandidateDefinitionsOnly"]
        auto_m_l_job.auto_m_l_job_artifacts = response["AutoMLJobArtifacts"]
        auto_m_l_job.resolved_attributes = response["ResolvedAttributes"]
        auto_m_l_job.model_deploy_config = response["ModelDeployConfig"]
        auto_m_l_job.model_deploy_result = response["ModelDeployResult"]
    
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
    def get(
        cls,
        auto_m_l_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        auto_m_l_job_v2 = cls(session, region)
    
        operation_input_args = {'AutoMLJobName': 'auto_m_l_job_name'}
        response = auto_m_l_job_v2.client.describe_auto_m_l_job_v2(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        auto_m_l_job_v2.auto_m_l_job_name = response["AutoMLJobName"]
        auto_m_l_job_v2.auto_m_l_job_arn = response["AutoMLJobArn"]
        auto_m_l_job_v2.auto_m_l_job_input_data_config = response["AutoMLJobInputDataConfig"]
        auto_m_l_job_v2.output_data_config = response["OutputDataConfig"]
        auto_m_l_job_v2.role_arn = response["RoleArn"]
        auto_m_l_job_v2.auto_m_l_job_objective = response["AutoMLJobObjective"]
        auto_m_l_job_v2.auto_m_l_problem_type_config = response["AutoMLProblemTypeConfig"]
        auto_m_l_job_v2.auto_m_l_problem_type_config_name = response["AutoMLProblemTypeConfigName"]
        auto_m_l_job_v2.creation_time = response["CreationTime"]
        auto_m_l_job_v2.end_time = response["EndTime"]
        auto_m_l_job_v2.last_modified_time = response["LastModifiedTime"]
        auto_m_l_job_v2.failure_reason = response["FailureReason"]
        auto_m_l_job_v2.partial_failure_reasons = response["PartialFailureReasons"]
        auto_m_l_job_v2.best_candidate = response["BestCandidate"]
        auto_m_l_job_v2.auto_m_l_job_status = response["AutoMLJobStatus"]
        auto_m_l_job_v2.auto_m_l_job_secondary_status = response["AutoMLJobSecondaryStatus"]
        auto_m_l_job_v2.auto_m_l_job_artifacts = response["AutoMLJobArtifacts"]
        auto_m_l_job_v2.resolved_attributes = response["ResolvedAttributes"]
        auto_m_l_job_v2.model_deploy_config = response["ModelDeployConfig"]
        auto_m_l_job_v2.model_deploy_result = response["ModelDeployResult"]
        auto_m_l_job_v2.data_split_config = response["DataSplitConfig"]
        auto_m_l_job_v2.security_config = response["SecurityConfig"]
    
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
    def get(
        cls,
        cluster_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        cluster = cls(session, region)
    
        operation_input_args = {'ClusterName': 'cluster_name'}
        response = cluster.client.describe_cluster(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        cluster.cluster_arn = response["ClusterArn"]
        cluster.cluster_name = response["ClusterName"]
        cluster.cluster_status = response["ClusterStatus"]
        cluster.creation_time = response["CreationTime"]
        cluster.failure_message = response["FailureMessage"]
        cluster.instance_groups = response["InstanceGroups"]
        cluster.vpc_config = response["VpcConfig"]
    
        return cluster


class CodeRepository(BaseModel):
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()

    
    @classmethod
    def get(
        cls,
        code_repository_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        code_repository = cls(session, region)
    
        operation_input_args = {'CodeRepositoryName': 'code_repository_name'}
        response = code_repository.client.describe_code_repository(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        code_repository.code_repository_name = response["CodeRepositoryName"]
        code_repository.code_repository_arn = response["CodeRepositoryArn"]
        code_repository.creation_time = response["CreationTime"]
        code_repository.last_modified_time = response["LastModifiedTime"]
        code_repository.git_config = response["GitConfig"]
    
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
    def get(
        cls,
        compilation_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        compilation_job = cls(session, region)
    
        operation_input_args = {'CompilationJobName': 'compilation_job_name'}
        response = compilation_job.client.describe_compilation_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        compilation_job.compilation_job_name = response["CompilationJobName"]
        compilation_job.compilation_job_arn = response["CompilationJobArn"]
        compilation_job.compilation_job_status = response["CompilationJobStatus"]
        compilation_job.compilation_start_time = response["CompilationStartTime"]
        compilation_job.compilation_end_time = response["CompilationEndTime"]
        compilation_job.stopping_condition = response["StoppingCondition"]
        compilation_job.inference_image = response["InferenceImage"]
        compilation_job.model_package_version_arn = response["ModelPackageVersionArn"]
        compilation_job.creation_time = response["CreationTime"]
        compilation_job.last_modified_time = response["LastModifiedTime"]
        compilation_job.failure_reason = response["FailureReason"]
        compilation_job.model_artifacts = response["ModelArtifacts"]
        compilation_job.model_digests = response["ModelDigests"]
        compilation_job.role_arn = response["RoleArn"]
        compilation_job.input_config = response["InputConfig"]
        compilation_job.output_config = response["OutputConfig"]
        compilation_job.vpc_config = response["VpcConfig"]
        compilation_job.derived_information = response["DerivedInformation"]
    
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
    def get(
        cls,
        context_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        context = cls(session, region)
    
        operation_input_args = {'ContextName': 'context_name'}
        response = context.client.describe_context(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        context.context_name = response["ContextName"]
        context.context_arn = response["ContextArn"]
        context.source = response["Source"]
        context.context_type = response["ContextType"]
        context.description = response["Description"]
        context.properties = response["Properties"]
        context.creation_time = response["CreationTime"]
        context.created_by = response["CreatedBy"]
        context.last_modified_time = response["LastModifiedTime"]
        context.last_modified_by = response["LastModifiedBy"]
        context.lineage_group_arn = response["LineageGroupArn"]
    
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
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        data_quality_job_definition = cls(session, region)
    
        operation_input_args = {'JobDefinitionName': 'job_definition_name'}
        response = data_quality_job_definition.client.describe_data_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        data_quality_job_definition.job_definition_arn = response["JobDefinitionArn"]
        data_quality_job_definition.job_definition_name = response["JobDefinitionName"]
        data_quality_job_definition.creation_time = response["CreationTime"]
        data_quality_job_definition.data_quality_baseline_config = response["DataQualityBaselineConfig"]
        data_quality_job_definition.data_quality_app_specification = response["DataQualityAppSpecification"]
        data_quality_job_definition.data_quality_job_input = response["DataQualityJobInput"]
        data_quality_job_definition.data_quality_job_output_config = response["DataQualityJobOutputConfig"]
        data_quality_job_definition.job_resources = response["JobResources"]
        data_quality_job_definition.network_config = response["NetworkConfig"]
        data_quality_job_definition.role_arn = response["RoleArn"]
        data_quality_job_definition.stopping_condition = response["StoppingCondition"]
    
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
    def get(
        cls,
        device_fleet_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        device_fleet = cls(session, region)
    
        operation_input_args = {'DeviceFleetName': 'device_fleet_name'}
        response = device_fleet.client.describe_device_fleet(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        device_fleet.device_fleet_name = response["DeviceFleetName"]
        device_fleet.device_fleet_arn = response["DeviceFleetArn"]
        device_fleet.output_config = response["OutputConfig"]
        device_fleet.description = response["Description"]
        device_fleet.creation_time = response["CreationTime"]
        device_fleet.last_modified_time = response["LastModifiedTime"]
        device_fleet.role_arn = response["RoleArn"]
        device_fleet.iot_role_alias = response["IotRoleAlias"]
    
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
    def get(
        cls,
        domain_id: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        domain = cls(session, region)
    
        operation_input_args = {'DomainId': 'domain_id'}
        response = domain.client.describe_domain(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        domain.domain_arn = response["DomainArn"]
        domain.domain_id = response["DomainId"]
        domain.domain_name = response["DomainName"]
        domain.home_efs_file_system_id = response["HomeEfsFileSystemId"]
        domain.single_sign_on_managed_application_instance_id = response["SingleSignOnManagedApplicationInstanceId"]
        domain.single_sign_on_application_arn = response["SingleSignOnApplicationArn"]
        domain.status = response["Status"]
        domain.creation_time = response["CreationTime"]
        domain.last_modified_time = response["LastModifiedTime"]
        domain.failure_reason = response["FailureReason"]
        domain.security_group_id_for_domain_boundary = response["SecurityGroupIdForDomainBoundary"]
        domain.auth_mode = response["AuthMode"]
        domain.default_user_settings = response["DefaultUserSettings"]
        domain.domain_settings = response["DomainSettings"]
        domain.app_network_access_type = response["AppNetworkAccessType"]
        domain.home_efs_file_system_kms_key_id = response["HomeEfsFileSystemKmsKeyId"]
        domain.subnet_ids = response["SubnetIds"]
        domain.url = response["Url"]
        domain.vpc_id = response["VpcId"]
        domain.kms_key_id = response["KmsKeyId"]
        domain.app_security_group_management = response["AppSecurityGroupManagement"]
        domain.default_space_settings = response["DefaultSpaceSettings"]
    
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
    def get(
        cls,
        edge_deployment_plan_name: str,
    next_token: Optional[str] = Unassigned(),
    max_results: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_deployment_plan = cls(session, region)
    
        operation_input_args = {'EdgeDeploymentPlanName': 'edge_deployment_plan_name', 'NextToken': 'next_token', 'MaxResults': 'max_results'}
        response = edge_deployment_plan.client.describe_edge_deployment_plan(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        edge_deployment_plan.edge_deployment_plan_arn = response["EdgeDeploymentPlanArn"]
        edge_deployment_plan.edge_deployment_plan_name = response["EdgeDeploymentPlanName"]
        edge_deployment_plan.model_configs = response["ModelConfigs"]
        edge_deployment_plan.device_fleet_name = response["DeviceFleetName"]
        edge_deployment_plan.edge_deployment_success = response["EdgeDeploymentSuccess"]
        edge_deployment_plan.edge_deployment_pending = response["EdgeDeploymentPending"]
        edge_deployment_plan.edge_deployment_failed = response["EdgeDeploymentFailed"]
        edge_deployment_plan.stages = response["Stages"]
        edge_deployment_plan.next_token = response["NextToken"]
        edge_deployment_plan.creation_time = response["CreationTime"]
        edge_deployment_plan.last_modified_time = response["LastModifiedTime"]
    
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
    def get(
        cls,
        edge_packaging_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        edge_packaging_job = cls(session, region)
    
        operation_input_args = {'EdgePackagingJobName': 'edge_packaging_job_name'}
        response = edge_packaging_job.client.describe_edge_packaging_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        edge_packaging_job.edge_packaging_job_arn = response["EdgePackagingJobArn"]
        edge_packaging_job.edge_packaging_job_name = response["EdgePackagingJobName"]
        edge_packaging_job.compilation_job_name = response["CompilationJobName"]
        edge_packaging_job.model_name = response["ModelName"]
        edge_packaging_job.model_version = response["ModelVersion"]
        edge_packaging_job.role_arn = response["RoleArn"]
        edge_packaging_job.output_config = response["OutputConfig"]
        edge_packaging_job.resource_key = response["ResourceKey"]
        edge_packaging_job.edge_packaging_job_status = response["EdgePackagingJobStatus"]
        edge_packaging_job.edge_packaging_job_status_message = response["EdgePackagingJobStatusMessage"]
        edge_packaging_job.creation_time = response["CreationTime"]
        edge_packaging_job.last_modified_time = response["LastModifiedTime"]
        edge_packaging_job.model_artifact = response["ModelArtifact"]
        edge_packaging_job.model_signature = response["ModelSignature"]
        edge_packaging_job.preset_deployment_output = response["PresetDeploymentOutput"]
    
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
    def get(
        cls,
        endpoint_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        endpoint = cls(session, region)
    
        operation_input_args = {'EndpointName': 'endpoint_name'}
        response = endpoint.client.describe_endpoint(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        endpoint.endpoint_name = response["EndpointName"]
        endpoint.endpoint_arn = response["EndpointArn"]
        endpoint.endpoint_config_name = response["EndpointConfigName"]
        endpoint.production_variants = response["ProductionVariants"]
        endpoint.data_capture_config = response["DataCaptureConfig"]
        endpoint.endpoint_status = response["EndpointStatus"]
        endpoint.failure_reason = response["FailureReason"]
        endpoint.creation_time = response["CreationTime"]
        endpoint.last_modified_time = response["LastModifiedTime"]
        endpoint.last_deployment_config = response["LastDeploymentConfig"]
        endpoint.async_inference_config = response["AsyncInferenceConfig"]
        endpoint.pending_deployment_summary = response["PendingDeploymentSummary"]
        endpoint.explainer_config = response["ExplainerConfig"]
        endpoint.shadow_production_variants = response["ShadowProductionVariants"]
    
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
    def get(
        cls,
        endpoint_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        endpoint_config = cls(session, region)
    
        operation_input_args = {'EndpointConfigName': 'endpoint_config_name'}
        response = endpoint_config.client.describe_endpoint_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        endpoint_config.endpoint_config_name = response["EndpointConfigName"]
        endpoint_config.endpoint_config_arn = response["EndpointConfigArn"]
        endpoint_config.production_variants = response["ProductionVariants"]
        endpoint_config.data_capture_config = response["DataCaptureConfig"]
        endpoint_config.kms_key_id = response["KmsKeyId"]
        endpoint_config.creation_time = response["CreationTime"]
        endpoint_config.async_inference_config = response["AsyncInferenceConfig"]
        endpoint_config.explainer_config = response["ExplainerConfig"]
        endpoint_config.shadow_production_variants = response["ShadowProductionVariants"]
        endpoint_config.execution_role_arn = response["ExecutionRoleArn"]
        endpoint_config.vpc_config = response["VpcConfig"]
        endpoint_config.enable_network_isolation = response["EnableNetworkIsolation"]
    
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
    def get(
        cls,
        experiment_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        experiment = cls(session, region)
    
        operation_input_args = {'ExperimentName': 'experiment_name'}
        response = experiment.client.describe_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        experiment.experiment_name = response["ExperimentName"]
        experiment.experiment_arn = response["ExperimentArn"]
        experiment.display_name = response["DisplayName"]
        experiment.source = response["Source"]
        experiment.description = response["Description"]
        experiment.creation_time = response["CreationTime"]
        experiment.created_by = response["CreatedBy"]
        experiment.last_modified_time = response["LastModifiedTime"]
        experiment.last_modified_by = response["LastModifiedBy"]
    
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
    def get(
        cls,
        feature_group_name: str,
    next_token: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        feature_group = cls(session, region)
    
        operation_input_args = {'FeatureGroupName': 'feature_group_name', 'NextToken': 'next_token'}
        response = feature_group.client.describe_feature_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        feature_group.feature_group_arn = response["FeatureGroupArn"]
        feature_group.feature_group_name = response["FeatureGroupName"]
        feature_group.record_identifier_feature_name = response["RecordIdentifierFeatureName"]
        feature_group.event_time_feature_name = response["EventTimeFeatureName"]
        feature_group.feature_definitions = response["FeatureDefinitions"]
        feature_group.creation_time = response["CreationTime"]
        feature_group.last_modified_time = response["LastModifiedTime"]
        feature_group.online_store_config = response["OnlineStoreConfig"]
        feature_group.offline_store_config = response["OfflineStoreConfig"]
        feature_group.throughput_config = response["ThroughputConfig"]
        feature_group.role_arn = response["RoleArn"]
        feature_group.feature_group_status = response["FeatureGroupStatus"]
        feature_group.offline_store_status = response["OfflineStoreStatus"]
        feature_group.last_update_status = response["LastUpdateStatus"]
        feature_group.failure_reason = response["FailureReason"]
        feature_group.description = response["Description"]
        feature_group.next_token = response["NextToken"]
        feature_group.online_store_total_size_bytes = response["OnlineStoreTotalSizeBytes"]
    
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
    def get(
        cls,
        flow_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        flow_definition = cls(session, region)
    
        operation_input_args = {'FlowDefinitionName': 'flow_definition_name'}
        response = flow_definition.client.describe_flow_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        flow_definition.flow_definition_arn = response["FlowDefinitionArn"]
        flow_definition.flow_definition_name = response["FlowDefinitionName"]
        flow_definition.flow_definition_status = response["FlowDefinitionStatus"]
        flow_definition.creation_time = response["CreationTime"]
        flow_definition.human_loop_request_source = response["HumanLoopRequestSource"]
        flow_definition.human_loop_activation_config = response["HumanLoopActivationConfig"]
        flow_definition.human_loop_config = response["HumanLoopConfig"]
        flow_definition.output_config = response["OutputConfig"]
        flow_definition.role_arn = response["RoleArn"]
        flow_definition.failure_reason = response["FailureReason"]
    
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
    def get(
        cls,
        hub_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        hub = cls(session, region)
    
        operation_input_args = {'HubName': 'hub_name'}
        response = hub.client.describe_hub(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        hub.hub_name = response["HubName"]
        hub.hub_arn = response["HubArn"]
        hub.hub_display_name = response["HubDisplayName"]
        hub.hub_description = response["HubDescription"]
        hub.hub_search_keywords = response["HubSearchKeywords"]
        hub.s3_storage_config = response["S3StorageConfig"]
        hub.hub_status = response["HubStatus"]
        hub.failure_reason = response["FailureReason"]
        hub.creation_time = response["CreationTime"]
        hub.last_modified_time = response["LastModifiedTime"]
    
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
    
        operation_input_args = {'HubName': 'hub_name', 'HubContentType': 'hub_content_type', 'HubContentName': 'hub_content_name', 'HubContentVersion': 'hub_content_version'}
        response = hub_content.client.describe_hub_content(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        hub_content.hub_content_name = response["HubContentName"]
        hub_content.hub_content_arn = response["HubContentArn"]
        hub_content.hub_content_version = response["HubContentVersion"]
        hub_content.hub_content_type = response["HubContentType"]
        hub_content.document_schema_version = response["DocumentSchemaVersion"]
        hub_content.hub_name = response["HubName"]
        hub_content.hub_arn = response["HubArn"]
        hub_content.hub_content_display_name = response["HubContentDisplayName"]
        hub_content.hub_content_description = response["HubContentDescription"]
        hub_content.hub_content_markdown = response["HubContentMarkdown"]
        hub_content.hub_content_document = response["HubContentDocument"]
        hub_content.hub_content_search_keywords = response["HubContentSearchKeywords"]
        hub_content.hub_content_dependencies = response["HubContentDependencies"]
        hub_content.hub_content_status = response["HubContentStatus"]
        hub_content.failure_reason = response["FailureReason"]
        hub_content.creation_time = response["CreationTime"]
    
        return hub_content


class HumanTaskUi(BaseModel):
    human_task_ui_arn: str
    human_task_ui_name: str
    creation_time: datetime.datetime
    ui_template: UiTemplateInfo
    human_task_ui_status: Optional[str] = Unassigned()

    
    @classmethod
    def get(
        cls,
        human_task_ui_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        human_task_ui = cls(session, region)
    
        operation_input_args = {'HumanTaskUiName': 'human_task_ui_name'}
        response = human_task_ui.client.describe_human_task_ui(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        human_task_ui.human_task_ui_arn = response["HumanTaskUiArn"]
        human_task_ui.human_task_ui_name = response["HumanTaskUiName"]
        human_task_ui.human_task_ui_status = response["HumanTaskUiStatus"]
        human_task_ui.creation_time = response["CreationTime"]
        human_task_ui.ui_template = response["UiTemplate"]
    
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
    def get(
        cls,
        hyper_parameter_tuning_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        hyper_parameter_tuning_job = cls(session, region)
    
        operation_input_args = {'HyperParameterTuningJobName': 'hyper_parameter_tuning_job_name'}
        response = hyper_parameter_tuning_job.client.describe_hyper_parameter_tuning_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        hyper_parameter_tuning_job.hyper_parameter_tuning_job_name = response["HyperParameterTuningJobName"]
        hyper_parameter_tuning_job.hyper_parameter_tuning_job_arn = response["HyperParameterTuningJobArn"]
        hyper_parameter_tuning_job.hyper_parameter_tuning_job_config = response["HyperParameterTuningJobConfig"]
        hyper_parameter_tuning_job.training_job_definition = response["TrainingJobDefinition"]
        hyper_parameter_tuning_job.training_job_definitions = response["TrainingJobDefinitions"]
        hyper_parameter_tuning_job.hyper_parameter_tuning_job_status = response["HyperParameterTuningJobStatus"]
        hyper_parameter_tuning_job.creation_time = response["CreationTime"]
        hyper_parameter_tuning_job.hyper_parameter_tuning_end_time = response["HyperParameterTuningEndTime"]
        hyper_parameter_tuning_job.last_modified_time = response["LastModifiedTime"]
        hyper_parameter_tuning_job.training_job_status_counters = response["TrainingJobStatusCounters"]
        hyper_parameter_tuning_job.objective_status_counters = response["ObjectiveStatusCounters"]
        hyper_parameter_tuning_job.best_training_job = response["BestTrainingJob"]
        hyper_parameter_tuning_job.overall_best_training_job = response["OverallBestTrainingJob"]
        hyper_parameter_tuning_job.warm_start_config = response["WarmStartConfig"]
        hyper_parameter_tuning_job.autotune = response["Autotune"]
        hyper_parameter_tuning_job.failure_reason = response["FailureReason"]
        hyper_parameter_tuning_job.tuning_job_completion_details = response["TuningJobCompletionDetails"]
        hyper_parameter_tuning_job.consumed_resources = response["ConsumedResources"]
    
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
    def get(
        cls,
        image_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        image = cls(session, region)
    
        operation_input_args = {'ImageName': 'image_name'}
        response = image.client.describe_image(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        image.creation_time = response["CreationTime"]
        image.description = response["Description"]
        image.display_name = response["DisplayName"]
        image.failure_reason = response["FailureReason"]
        image.image_arn = response["ImageArn"]
        image.image_name = response["ImageName"]
        image.image_status = response["ImageStatus"]
        image.last_modified_time = response["LastModifiedTime"]
        image.role_arn = response["RoleArn"]
    
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
    def get(
        cls,
        image_name: str,
    version: Optional[int] = Unassigned(),
    alias: Optional[str] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        image_version = cls(session, region)
    
        operation_input_args = {'ImageName': 'image_name', 'Version': 'version', 'Alias': 'alias'}
        response = image_version.client.describe_image_version(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        image_version.base_image = response["BaseImage"]
        image_version.container_image = response["ContainerImage"]
        image_version.creation_time = response["CreationTime"]
        image_version.failure_reason = response["FailureReason"]
        image_version.image_arn = response["ImageArn"]
        image_version.image_version_arn = response["ImageVersionArn"]
        image_version.image_version_status = response["ImageVersionStatus"]
        image_version.last_modified_time = response["LastModifiedTime"]
        image_version.version = response["Version"]
        image_version.vendor_guidance = response["VendorGuidance"]
        image_version.job_type = response["JobType"]
        image_version.m_l_framework = response["MLFramework"]
        image_version.programming_lang = response["ProgrammingLang"]
        image_version.processor = response["Processor"]
        image_version.horovod = response["Horovod"]
        image_version.release_notes = response["ReleaseNotes"]
    
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
    def get(
        cls,
        inference_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_component = cls(session, region)
    
        operation_input_args = {'InferenceComponentName': 'inference_component_name'}
        response = inference_component.client.describe_inference_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        inference_component.inference_component_name = response["InferenceComponentName"]
        inference_component.inference_component_arn = response["InferenceComponentArn"]
        inference_component.endpoint_name = response["EndpointName"]
        inference_component.endpoint_arn = response["EndpointArn"]
        inference_component.variant_name = response["VariantName"]
        inference_component.failure_reason = response["FailureReason"]
        inference_component.specification = response["Specification"]
        inference_component.runtime_config = response["RuntimeConfig"]
        inference_component.creation_time = response["CreationTime"]
        inference_component.last_modified_time = response["LastModifiedTime"]
        inference_component.inference_component_status = response["InferenceComponentStatus"]
    
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
    def get(
        cls,
        name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_experiment = cls(session, region)
    
        operation_input_args = {'Name': 'name'}
        response = inference_experiment.client.describe_inference_experiment(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        inference_experiment.arn = response["Arn"]
        inference_experiment.name = response["Name"]
        inference_experiment.type = response["Type"]
        inference_experiment.schedule = response["Schedule"]
        inference_experiment.status = response["Status"]
        inference_experiment.status_reason = response["StatusReason"]
        inference_experiment.description = response["Description"]
        inference_experiment.creation_time = response["CreationTime"]
        inference_experiment.completion_time = response["CompletionTime"]
        inference_experiment.last_modified_time = response["LastModifiedTime"]
        inference_experiment.role_arn = response["RoleArn"]
        inference_experiment.endpoint_metadata = response["EndpointMetadata"]
        inference_experiment.model_variants = response["ModelVariants"]
        inference_experiment.data_storage_config = response["DataStorageConfig"]
        inference_experiment.shadow_mode_config = response["ShadowModeConfig"]
        inference_experiment.kms_key = response["KmsKey"]
    
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
    def get(
        cls,
        job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        inference_recommendations_job = cls(session, region)
    
        operation_input_args = {'JobName': 'job_name'}
        response = inference_recommendations_job.client.describe_inference_recommendations_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        inference_recommendations_job.job_name = response["JobName"]
        inference_recommendations_job.job_description = response["JobDescription"]
        inference_recommendations_job.job_type = response["JobType"]
        inference_recommendations_job.job_arn = response["JobArn"]
        inference_recommendations_job.role_arn = response["RoleArn"]
        inference_recommendations_job.status = response["Status"]
        inference_recommendations_job.creation_time = response["CreationTime"]
        inference_recommendations_job.completion_time = response["CompletionTime"]
        inference_recommendations_job.last_modified_time = response["LastModifiedTime"]
        inference_recommendations_job.failure_reason = response["FailureReason"]
        inference_recommendations_job.input_config = response["InputConfig"]
        inference_recommendations_job.stopping_conditions = response["StoppingConditions"]
        inference_recommendations_job.inference_recommendations = response["InferenceRecommendations"]
        inference_recommendations_job.endpoint_performances = response["EndpointPerformances"]
    
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
    def get(
        cls,
        labeling_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        labeling_job = cls(session, region)
    
        operation_input_args = {'LabelingJobName': 'labeling_job_name'}
        response = labeling_job.client.describe_labeling_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        labeling_job.labeling_job_status = response["LabelingJobStatus"]
        labeling_job.label_counters = response["LabelCounters"]
        labeling_job.failure_reason = response["FailureReason"]
        labeling_job.creation_time = response["CreationTime"]
        labeling_job.last_modified_time = response["LastModifiedTime"]
        labeling_job.job_reference_code = response["JobReferenceCode"]
        labeling_job.labeling_job_name = response["LabelingJobName"]
        labeling_job.labeling_job_arn = response["LabelingJobArn"]
        labeling_job.label_attribute_name = response["LabelAttributeName"]
        labeling_job.input_config = response["InputConfig"]
        labeling_job.output_config = response["OutputConfig"]
        labeling_job.role_arn = response["RoleArn"]
        labeling_job.label_category_config_s3_uri = response["LabelCategoryConfigS3Uri"]
        labeling_job.stopping_conditions = response["StoppingConditions"]
        labeling_job.labeling_job_algorithms_config = response["LabelingJobAlgorithmsConfig"]
        labeling_job.human_task_config = response["HumanTaskConfig"]
        labeling_job.tags = response["Tags"]
        labeling_job.labeling_job_output = response["LabelingJobOutput"]
    
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
    def get(
        cls,
        model_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model = cls(session, region)
    
        operation_input_args = {'ModelName': 'model_name'}
        response = model.client.describe_model(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model.model_name = response["ModelName"]
        model.primary_container = response["PrimaryContainer"]
        model.containers = response["Containers"]
        model.inference_execution_config = response["InferenceExecutionConfig"]
        model.execution_role_arn = response["ExecutionRoleArn"]
        model.vpc_config = response["VpcConfig"]
        model.creation_time = response["CreationTime"]
        model.model_arn = response["ModelArn"]
        model.enable_network_isolation = response["EnableNetworkIsolation"]
        model.deployment_recommendation = response["DeploymentRecommendation"]
    
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
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_bias_job_definition = cls(session, region)
    
        operation_input_args = {'JobDefinitionName': 'job_definition_name'}
        response = model_bias_job_definition.client.describe_model_bias_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_bias_job_definition.job_definition_arn = response["JobDefinitionArn"]
        model_bias_job_definition.job_definition_name = response["JobDefinitionName"]
        model_bias_job_definition.creation_time = response["CreationTime"]
        model_bias_job_definition.model_bias_baseline_config = response["ModelBiasBaselineConfig"]
        model_bias_job_definition.model_bias_app_specification = response["ModelBiasAppSpecification"]
        model_bias_job_definition.model_bias_job_input = response["ModelBiasJobInput"]
        model_bias_job_definition.model_bias_job_output_config = response["ModelBiasJobOutputConfig"]
        model_bias_job_definition.job_resources = response["JobResources"]
        model_bias_job_definition.network_config = response["NetworkConfig"]
        model_bias_job_definition.role_arn = response["RoleArn"]
        model_bias_job_definition.stopping_condition = response["StoppingCondition"]
    
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
    def get(
        cls,
        model_card_name: str,
    model_card_version: Optional[int] = Unassigned(),
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card = cls(session, region)
    
        operation_input_args = {'ModelCardName': 'model_card_name', 'ModelCardVersion': 'model_card_version'}
        response = model_card.client.describe_model_card(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_card.model_card_arn = response["ModelCardArn"]
        model_card.model_card_name = response["ModelCardName"]
        model_card.model_card_version = response["ModelCardVersion"]
        model_card.content = response["Content"]
        model_card.model_card_status = response["ModelCardStatus"]
        model_card.security_config = response["SecurityConfig"]
        model_card.creation_time = response["CreationTime"]
        model_card.created_by = response["CreatedBy"]
        model_card.last_modified_time = response["LastModifiedTime"]
        model_card.last_modified_by = response["LastModifiedBy"]
        model_card.model_card_processing_status = response["ModelCardProcessingStatus"]
    
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
    def get(
        cls,
        model_card_export_job_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_card_export_job = cls(session, region)
    
        operation_input_args = {'ModelCardExportJobArn': 'model_card_export_job_arn'}
        response = model_card_export_job.client.describe_model_card_export_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_card_export_job.model_card_export_job_name = response["ModelCardExportJobName"]
        model_card_export_job.model_card_export_job_arn = response["ModelCardExportJobArn"]
        model_card_export_job.status = response["Status"]
        model_card_export_job.model_card_name = response["ModelCardName"]
        model_card_export_job.model_card_version = response["ModelCardVersion"]
        model_card_export_job.output_config = response["OutputConfig"]
        model_card_export_job.created_at = response["CreatedAt"]
        model_card_export_job.last_modified_at = response["LastModifiedAt"]
        model_card_export_job.failure_reason = response["FailureReason"]
        model_card_export_job.export_artifacts = response["ExportArtifacts"]
    
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
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_explainability_job_definition = cls(session, region)
    
        operation_input_args = {'JobDefinitionName': 'job_definition_name'}
        response = model_explainability_job_definition.client.describe_model_explainability_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_explainability_job_definition.job_definition_arn = response["JobDefinitionArn"]
        model_explainability_job_definition.job_definition_name = response["JobDefinitionName"]
        model_explainability_job_definition.creation_time = response["CreationTime"]
        model_explainability_job_definition.model_explainability_baseline_config = response["ModelExplainabilityBaselineConfig"]
        model_explainability_job_definition.model_explainability_app_specification = response["ModelExplainabilityAppSpecification"]
        model_explainability_job_definition.model_explainability_job_input = response["ModelExplainabilityJobInput"]
        model_explainability_job_definition.model_explainability_job_output_config = response["ModelExplainabilityJobOutputConfig"]
        model_explainability_job_definition.job_resources = response["JobResources"]
        model_explainability_job_definition.network_config = response["NetworkConfig"]
        model_explainability_job_definition.role_arn = response["RoleArn"]
        model_explainability_job_definition.stopping_condition = response["StoppingCondition"]
    
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
    def get(
        cls,
        model_package_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_package = cls(session, region)
    
        operation_input_args = {'ModelPackageName': 'model_package_name'}
        response = model_package.client.describe_model_package(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_package.model_package_name = response["ModelPackageName"]
        model_package.model_package_group_name = response["ModelPackageGroupName"]
        model_package.model_package_version = response["ModelPackageVersion"]
        model_package.model_package_arn = response["ModelPackageArn"]
        model_package.model_package_description = response["ModelPackageDescription"]
        model_package.creation_time = response["CreationTime"]
        model_package.inference_specification = response["InferenceSpecification"]
        model_package.source_algorithm_specification = response["SourceAlgorithmSpecification"]
        model_package.validation_specification = response["ValidationSpecification"]
        model_package.model_package_status = response["ModelPackageStatus"]
        model_package.model_package_status_details = response["ModelPackageStatusDetails"]
        model_package.certify_for_marketplace = response["CertifyForMarketplace"]
        model_package.model_approval_status = response["ModelApprovalStatus"]
        model_package.created_by = response["CreatedBy"]
        model_package.metadata_properties = response["MetadataProperties"]
        model_package.model_metrics = response["ModelMetrics"]
        model_package.last_modified_time = response["LastModifiedTime"]
        model_package.last_modified_by = response["LastModifiedBy"]
        model_package.approval_description = response["ApprovalDescription"]
        model_package.domain = response["Domain"]
        model_package.task = response["Task"]
        model_package.sample_payload_url = response["SamplePayloadUrl"]
        model_package.customer_metadata_properties = response["CustomerMetadataProperties"]
        model_package.drift_check_baselines = response["DriftCheckBaselines"]
        model_package.additional_inference_specifications = response["AdditionalInferenceSpecifications"]
        model_package.skip_model_validation = response["SkipModelValidation"]
        model_package.source_uri = response["SourceUri"]
    
        return model_package


class ModelPackageGroup(BaseModel):
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    created_by: UserContext
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()

    
    @classmethod
    def get(
        cls,
        model_package_group_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_package_group = cls(session, region)
    
        operation_input_args = {'ModelPackageGroupName': 'model_package_group_name'}
        response = model_package_group.client.describe_model_package_group(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_package_group.model_package_group_name = response["ModelPackageGroupName"]
        model_package_group.model_package_group_arn = response["ModelPackageGroupArn"]
        model_package_group.model_package_group_description = response["ModelPackageGroupDescription"]
        model_package_group.creation_time = response["CreationTime"]
        model_package_group.created_by = response["CreatedBy"]
        model_package_group.model_package_group_status = response["ModelPackageGroupStatus"]
    
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
    def get(
        cls,
        job_definition_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        model_quality_job_definition = cls(session, region)
    
        operation_input_args = {'JobDefinitionName': 'job_definition_name'}
        response = model_quality_job_definition.client.describe_model_quality_job_definition(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        model_quality_job_definition.job_definition_arn = response["JobDefinitionArn"]
        model_quality_job_definition.job_definition_name = response["JobDefinitionName"]
        model_quality_job_definition.creation_time = response["CreationTime"]
        model_quality_job_definition.model_quality_baseline_config = response["ModelQualityBaselineConfig"]
        model_quality_job_definition.model_quality_app_specification = response["ModelQualityAppSpecification"]
        model_quality_job_definition.model_quality_job_input = response["ModelQualityJobInput"]
        model_quality_job_definition.model_quality_job_output_config = response["ModelQualityJobOutputConfig"]
        model_quality_job_definition.job_resources = response["JobResources"]
        model_quality_job_definition.network_config = response["NetworkConfig"]
        model_quality_job_definition.role_arn = response["RoleArn"]
        model_quality_job_definition.stopping_condition = response["StoppingCondition"]
    
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
    def get(
        cls,
        monitoring_schedule_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        monitoring_schedule = cls(session, region)
    
        operation_input_args = {'MonitoringScheduleName': 'monitoring_schedule_name'}
        response = monitoring_schedule.client.describe_monitoring_schedule(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        monitoring_schedule.monitoring_schedule_arn = response["MonitoringScheduleArn"]
        monitoring_schedule.monitoring_schedule_name = response["MonitoringScheduleName"]
        monitoring_schedule.monitoring_schedule_status = response["MonitoringScheduleStatus"]
        monitoring_schedule.monitoring_type = response["MonitoringType"]
        monitoring_schedule.failure_reason = response["FailureReason"]
        monitoring_schedule.creation_time = response["CreationTime"]
        monitoring_schedule.last_modified_time = response["LastModifiedTime"]
        monitoring_schedule.monitoring_schedule_config = response["MonitoringScheduleConfig"]
        monitoring_schedule.endpoint_name = response["EndpointName"]
        monitoring_schedule.last_monitoring_execution_summary = response["LastMonitoringExecutionSummary"]
    
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
    def get(
        cls,
        notebook_instance_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        notebook_instance = cls(session, region)
    
        operation_input_args = {'NotebookInstanceName': 'notebook_instance_name'}
        response = notebook_instance.client.describe_notebook_instance(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        notebook_instance.notebook_instance_arn = response["NotebookInstanceArn"]
        notebook_instance.notebook_instance_name = response["NotebookInstanceName"]
        notebook_instance.notebook_instance_status = response["NotebookInstanceStatus"]
        notebook_instance.failure_reason = response["FailureReason"]
        notebook_instance.url = response["Url"]
        notebook_instance.instance_type = response["InstanceType"]
        notebook_instance.subnet_id = response["SubnetId"]
        notebook_instance.security_groups = response["SecurityGroups"]
        notebook_instance.role_arn = response["RoleArn"]
        notebook_instance.kms_key_id = response["KmsKeyId"]
        notebook_instance.network_interface_id = response["NetworkInterfaceId"]
        notebook_instance.last_modified_time = response["LastModifiedTime"]
        notebook_instance.creation_time = response["CreationTime"]
        notebook_instance.notebook_instance_lifecycle_config_name = response["NotebookInstanceLifecycleConfigName"]
        notebook_instance.direct_internet_access = response["DirectInternetAccess"]
        notebook_instance.volume_size_in_g_b = response["VolumeSizeInGB"]
        notebook_instance.accelerator_types = response["AcceleratorTypes"]
        notebook_instance.default_code_repository = response["DefaultCodeRepository"]
        notebook_instance.additional_code_repositories = response["AdditionalCodeRepositories"]
        notebook_instance.root_access = response["RootAccess"]
        notebook_instance.platform_identifier = response["PlatformIdentifier"]
        notebook_instance.instance_metadata_service_configuration = response["InstanceMetadataServiceConfiguration"]
    
        return notebook_instance


class NotebookInstanceLifecycleConfig(BaseModel):
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()

    
    @classmethod
    def get(
        cls,
        notebook_instance_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        notebook_instance_lifecycle_config = cls(session, region)
    
        operation_input_args = {'NotebookInstanceLifecycleConfigName': 'notebook_instance_lifecycle_config_name'}
        response = notebook_instance_lifecycle_config.client.describe_notebook_instance_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        notebook_instance_lifecycle_config.notebook_instance_lifecycle_config_arn = response["NotebookInstanceLifecycleConfigArn"]
        notebook_instance_lifecycle_config.notebook_instance_lifecycle_config_name = response["NotebookInstanceLifecycleConfigName"]
        notebook_instance_lifecycle_config.on_create = response["OnCreate"]
        notebook_instance_lifecycle_config.on_start = response["OnStart"]
        notebook_instance_lifecycle_config.last_modified_time = response["LastModifiedTime"]
        notebook_instance_lifecycle_config.creation_time = response["CreationTime"]
    
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
    def get(
        cls,
        pipeline_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        pipeline = cls(session, region)
    
        operation_input_args = {'PipelineName': 'pipeline_name'}
        response = pipeline.client.describe_pipeline(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        pipeline.pipeline_arn = response["PipelineArn"]
        pipeline.pipeline_name = response["PipelineName"]
        pipeline.pipeline_display_name = response["PipelineDisplayName"]
        pipeline.pipeline_definition = response["PipelineDefinition"]
        pipeline.pipeline_description = response["PipelineDescription"]
        pipeline.role_arn = response["RoleArn"]
        pipeline.pipeline_status = response["PipelineStatus"]
        pipeline.creation_time = response["CreationTime"]
        pipeline.last_modified_time = response["LastModifiedTime"]
        pipeline.last_run_time = response["LastRunTime"]
        pipeline.created_by = response["CreatedBy"]
        pipeline.last_modified_by = response["LastModifiedBy"]
        pipeline.parallelism_configuration = response["ParallelismConfiguration"]
    
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

    
    @classmethod
    def get(
        cls,
        pipeline_execution_arn: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        pipeline_execution = cls(session, region)
    
        operation_input_args = {'PipelineExecutionArn': 'pipeline_execution_arn'}
        response = pipeline_execution.client.describe_pipeline_execution(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        pipeline_execution.pipeline_arn = response["PipelineArn"]
        pipeline_execution.pipeline_execution_arn = response["PipelineExecutionArn"]
        pipeline_execution.pipeline_execution_display_name = response["PipelineExecutionDisplayName"]
        pipeline_execution.pipeline_execution_status = response["PipelineExecutionStatus"]
        pipeline_execution.pipeline_execution_description = response["PipelineExecutionDescription"]
        pipeline_execution.pipeline_experiment_config = response["PipelineExperimentConfig"]
        pipeline_execution.failure_reason = response["FailureReason"]
        pipeline_execution.creation_time = response["CreationTime"]
        pipeline_execution.last_modified_time = response["LastModifiedTime"]
        pipeline_execution.created_by = response["CreatedBy"]
        pipeline_execution.last_modified_by = response["LastModifiedBy"]
        pipeline_execution.parallelism_configuration = response["ParallelismConfiguration"]
        pipeline_execution.selective_execution_config = response["SelectiveExecutionConfig"]
    
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
    def get(
        cls,
        processing_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        processing_job = cls(session, region)
    
        operation_input_args = {'ProcessingJobName': 'processing_job_name'}
        response = processing_job.client.describe_processing_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        processing_job.processing_inputs = response["ProcessingInputs"]
        processing_job.processing_output_config = response["ProcessingOutputConfig"]
        processing_job.processing_job_name = response["ProcessingJobName"]
        processing_job.processing_resources = response["ProcessingResources"]
        processing_job.stopping_condition = response["StoppingCondition"]
        processing_job.app_specification = response["AppSpecification"]
        processing_job.environment = response["Environment"]
        processing_job.network_config = response["NetworkConfig"]
        processing_job.role_arn = response["RoleArn"]
        processing_job.experiment_config = response["ExperimentConfig"]
        processing_job.processing_job_arn = response["ProcessingJobArn"]
        processing_job.processing_job_status = response["ProcessingJobStatus"]
        processing_job.exit_message = response["ExitMessage"]
        processing_job.failure_reason = response["FailureReason"]
        processing_job.processing_end_time = response["ProcessingEndTime"]
        processing_job.processing_start_time = response["ProcessingStartTime"]
        processing_job.last_modified_time = response["LastModifiedTime"]
        processing_job.creation_time = response["CreationTime"]
        processing_job.monitoring_schedule_arn = response["MonitoringScheduleArn"]
        processing_job.auto_m_l_job_arn = response["AutoMLJobArn"]
        processing_job.training_job_arn = response["TrainingJobArn"]
    
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
    def get(
        cls,
        project_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        project = cls(session, region)
    
        operation_input_args = {'ProjectName': 'project_name'}
        response = project.client.describe_project(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        project.project_arn = response["ProjectArn"]
        project.project_name = response["ProjectName"]
        project.project_id = response["ProjectId"]
        project.project_description = response["ProjectDescription"]
        project.service_catalog_provisioning_details = response["ServiceCatalogProvisioningDetails"]
        project.service_catalog_provisioned_product_details = response["ServiceCatalogProvisionedProductDetails"]
        project.project_status = response["ProjectStatus"]
        project.created_by = response["CreatedBy"]
        project.creation_time = response["CreationTime"]
        project.last_modified_time = response["LastModifiedTime"]
        project.last_modified_by = response["LastModifiedBy"]
    
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
    def get(
        cls,
        domain_id: str,
    space_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        space = cls(session, region)
    
        operation_input_args = {'DomainId': 'domain_id', 'SpaceName': 'space_name'}
        response = space.client.describe_space(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        space.domain_id = response["DomainId"]
        space.space_arn = response["SpaceArn"]
        space.space_name = response["SpaceName"]
        space.home_efs_file_system_uid = response["HomeEfsFileSystemUid"]
        space.status = response["Status"]
        space.last_modified_time = response["LastModifiedTime"]
        space.creation_time = response["CreationTime"]
        space.failure_reason = response["FailureReason"]
        space.space_settings = response["SpaceSettings"]
        space.ownership_settings = response["OwnershipSettings"]
        space.space_sharing_settings = response["SpaceSharingSettings"]
        space.space_display_name = response["SpaceDisplayName"]
        space.url = response["Url"]
    
        return space


class StudioLifecycleConfig(BaseModel):
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_content: Optional[str] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()

    
    @classmethod
    def get(
        cls,
        studio_lifecycle_config_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        studio_lifecycle_config = cls(session, region)
    
        operation_input_args = {'StudioLifecycleConfigName': 'studio_lifecycle_config_name'}
        response = studio_lifecycle_config.client.describe_studio_lifecycle_config(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        studio_lifecycle_config.studio_lifecycle_config_arn = response["StudioLifecycleConfigArn"]
        studio_lifecycle_config.studio_lifecycle_config_name = response["StudioLifecycleConfigName"]
        studio_lifecycle_config.creation_time = response["CreationTime"]
        studio_lifecycle_config.last_modified_time = response["LastModifiedTime"]
        studio_lifecycle_config.studio_lifecycle_config_content = response["StudioLifecycleConfigContent"]
        studio_lifecycle_config.studio_lifecycle_config_app_type = response["StudioLifecycleConfigAppType"]
    
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
    def get(
        cls,
        training_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        training_job = cls(session, region)
    
        operation_input_args = {'TrainingJobName': 'training_job_name'}
        response = training_job.client.describe_training_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        training_job.training_job_name = response["TrainingJobName"]
        training_job.training_job_arn = response["TrainingJobArn"]
        training_job.tuning_job_arn = response["TuningJobArn"]
        training_job.labeling_job_arn = response["LabelingJobArn"]
        training_job.auto_m_l_job_arn = response["AutoMLJobArn"]
        training_job.model_artifacts = response["ModelArtifacts"]
        training_job.training_job_status = response["TrainingJobStatus"]
        training_job.secondary_status = response["SecondaryStatus"]
        training_job.failure_reason = response["FailureReason"]
        training_job.hyper_parameters = response["HyperParameters"]
        training_job.algorithm_specification = response["AlgorithmSpecification"]
        training_job.role_arn = response["RoleArn"]
        training_job.input_data_config = response["InputDataConfig"]
        training_job.output_data_config = response["OutputDataConfig"]
        training_job.resource_config = response["ResourceConfig"]
        training_job.warm_pool_status = response["WarmPoolStatus"]
        training_job.vpc_config = response["VpcConfig"]
        training_job.stopping_condition = response["StoppingCondition"]
        training_job.creation_time = response["CreationTime"]
        training_job.training_start_time = response["TrainingStartTime"]
        training_job.training_end_time = response["TrainingEndTime"]
        training_job.last_modified_time = response["LastModifiedTime"]
        training_job.secondary_status_transitions = response["SecondaryStatusTransitions"]
        training_job.final_metric_data_list = response["FinalMetricDataList"]
        training_job.enable_network_isolation = response["EnableNetworkIsolation"]
        training_job.enable_inter_container_traffic_encryption = response["EnableInterContainerTrafficEncryption"]
        training_job.enable_managed_spot_training = response["EnableManagedSpotTraining"]
        training_job.checkpoint_config = response["CheckpointConfig"]
        training_job.training_time_in_seconds = response["TrainingTimeInSeconds"]
        training_job.billable_time_in_seconds = response["BillableTimeInSeconds"]
        training_job.debug_hook_config = response["DebugHookConfig"]
        training_job.experiment_config = response["ExperimentConfig"]
        training_job.debug_rule_configurations = response["DebugRuleConfigurations"]
        training_job.tensor_board_output_config = response["TensorBoardOutputConfig"]
        training_job.debug_rule_evaluation_statuses = response["DebugRuleEvaluationStatuses"]
        training_job.profiler_config = response["ProfilerConfig"]
        training_job.profiler_rule_configurations = response["ProfilerRuleConfigurations"]
        training_job.profiler_rule_evaluation_statuses = response["ProfilerRuleEvaluationStatuses"]
        training_job.profiling_status = response["ProfilingStatus"]
        training_job.environment = response["Environment"]
        training_job.retry_strategy = response["RetryStrategy"]
        training_job.remote_debug_config = response["RemoteDebugConfig"]
        training_job.infra_check_config = response["InfraCheckConfig"]
    
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
    def get(
        cls,
        transform_job_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        transform_job = cls(session, region)
    
        operation_input_args = {'TransformJobName': 'transform_job_name'}
        response = transform_job.client.describe_transform_job(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        transform_job.transform_job_name = response["TransformJobName"]
        transform_job.transform_job_arn = response["TransformJobArn"]
        transform_job.transform_job_status = response["TransformJobStatus"]
        transform_job.failure_reason = response["FailureReason"]
        transform_job.model_name = response["ModelName"]
        transform_job.max_concurrent_transforms = response["MaxConcurrentTransforms"]
        transform_job.model_client_config = response["ModelClientConfig"]
        transform_job.max_payload_in_m_b = response["MaxPayloadInMB"]
        transform_job.batch_strategy = response["BatchStrategy"]
        transform_job.environment = response["Environment"]
        transform_job.transform_input = response["TransformInput"]
        transform_job.transform_output = response["TransformOutput"]
        transform_job.data_capture_config = response["DataCaptureConfig"]
        transform_job.transform_resources = response["TransformResources"]
        transform_job.creation_time = response["CreationTime"]
        transform_job.transform_start_time = response["TransformStartTime"]
        transform_job.transform_end_time = response["TransformEndTime"]
        transform_job.labeling_job_arn = response["LabelingJobArn"]
        transform_job.auto_m_l_job_arn = response["AutoMLJobArn"]
        transform_job.data_processing = response["DataProcessing"]
        transform_job.experiment_config = response["ExperimentConfig"]
    
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
    def get(
        cls,
        trial_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        trial = cls(session, region)
    
        operation_input_args = {'TrialName': 'trial_name'}
        response = trial.client.describe_trial(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        trial.trial_name = response["TrialName"]
        trial.trial_arn = response["TrialArn"]
        trial.display_name = response["DisplayName"]
        trial.experiment_name = response["ExperimentName"]
        trial.source = response["Source"]
        trial.creation_time = response["CreationTime"]
        trial.created_by = response["CreatedBy"]
        trial.last_modified_time = response["LastModifiedTime"]
        trial.last_modified_by = response["LastModifiedBy"]
        trial.metadata_properties = response["MetadataProperties"]
    
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
    def get(
        cls,
        trial_component_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        trial_component = cls(session, region)
    
        operation_input_args = {'TrialComponentName': 'trial_component_name'}
        response = trial_component.client.describe_trial_component(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        trial_component.trial_component_name = response["TrialComponentName"]
        trial_component.trial_component_arn = response["TrialComponentArn"]
        trial_component.display_name = response["DisplayName"]
        trial_component.source = response["Source"]
        trial_component.status = response["Status"]
        trial_component.start_time = response["StartTime"]
        trial_component.end_time = response["EndTime"]
        trial_component.creation_time = response["CreationTime"]
        trial_component.created_by = response["CreatedBy"]
        trial_component.last_modified_time = response["LastModifiedTime"]
        trial_component.last_modified_by = response["LastModifiedBy"]
        trial_component.parameters = response["Parameters"]
        trial_component.input_artifacts = response["InputArtifacts"]
        trial_component.output_artifacts = response["OutputArtifacts"]
        trial_component.metadata_properties = response["MetadataProperties"]
        trial_component.metrics = response["Metrics"]
        trial_component.lineage_group_arn = response["LineageGroupArn"]
        trial_component.sources = response["Sources"]
    
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
    def get(
        cls,
        domain_id: str,
    user_profile_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        user_profile = cls(session, region)
    
        operation_input_args = {'DomainId': 'domain_id', 'UserProfileName': 'user_profile_name'}
        response = user_profile.client.describe_user_profile(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        user_profile.domain_id = response["DomainId"]
        user_profile.user_profile_arn = response["UserProfileArn"]
        user_profile.user_profile_name = response["UserProfileName"]
        user_profile.home_efs_file_system_uid = response["HomeEfsFileSystemUid"]
        user_profile.status = response["Status"]
        user_profile.last_modified_time = response["LastModifiedTime"]
        user_profile.creation_time = response["CreationTime"]
        user_profile.failure_reason = response["FailureReason"]
        user_profile.single_sign_on_user_identifier = response["SingleSignOnUserIdentifier"]
        user_profile.single_sign_on_user_value = response["SingleSignOnUserValue"]
        user_profile.user_settings = response["UserSettings"]
    
        return user_profile


class Workforce(BaseModel):
    workforce: Workforce

    
    @classmethod
    def get(
        cls,
        workforce_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        workforce = cls(session, region)
    
        operation_input_args = {'WorkforceName': 'workforce_name'}
        response = workforce.client.describe_workforce(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        workforce.workforce = response["Workforce"]
    
        return workforce


class Workteam(BaseModel):
    workteam: Workteam

    
    @classmethod
    def get(
        cls,
        workteam_name: str,
        session: Optional[Session] = None,
        region: Optional[str] = None,
    ) -> Optional[object]:
        workteam = cls(session, region)
    
        operation_input_args = {'WorkteamName': 'workteam_name'}
        response = workteam.client.describe_workteam(**operation_input_args)
    
        pprint(response)
    
        # deserialize the response
        workteam.workteam = response["Workteam"]
    
        return workteam


