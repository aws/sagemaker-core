
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

from pydantic import BaseModel
from typing import List, Dict, Optional
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


class AppImageConfig(BaseModel):
    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()


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


class Association(BaseModel):


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


class Cluster(BaseModel):
    cluster_arn: str
    cluster_status: str
    instance_groups: List[ClusterInstanceGroupDetails]
    cluster_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    failure_message: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


class CodeRepository(BaseModel):
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()


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


class DeviceFleet(BaseModel):
    device_fleet_name: str
    device_fleet_arn: str
    output_config: EdgeOutputConfig
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    iot_role_alias: Optional[str] = Unassigned()


class Devices(BaseModel):


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


class EdgeDeploymentStage(BaseModel):


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


class HumanTaskUi(BaseModel):
    human_task_ui_arn: str
    human_task_ui_name: str
    creation_time: datetime.datetime
    ui_template: UiTemplateInfo
    human_task_ui_status: Optional[str] = Unassigned()


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


class ModelPackageGroup(BaseModel):
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    created_by: UserContext
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()


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


class NotebookInstanceLifecycleConfig(BaseModel):
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    on_create: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    on_start: Optional[List[NotebookInstanceLifecycleHook]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()


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


class PresignedDomainUrl(BaseModel):


class PresignedNotebookInstanceUrl(BaseModel):


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


class StudioLifecycleConfig(BaseModel):
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_content: Optional[str] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()


class Tags(BaseModel):


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


class Workforce(BaseModel):
    workforce: Workforce


class Workteam(BaseModel):
    workteam: Workteam


