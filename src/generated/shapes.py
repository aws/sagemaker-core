import datetime

from dataclasses import dataclass
from typing import Optional


class Base:
    """TBA"""
    pass


class Unassigned:
    """A custom type used to signify an undefined optional argument."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@dataclass
class ActionSource(Base):
    """TBA"""
    source_uri: str
    source_type: Optional[str] = Unassigned()
    source_id: Optional[str] = Unassigned()


@dataclass
class ActionSummary(Base):
    """TBA"""
    action_arn: Optional[str] = Unassigned()
    action_name: Optional[str] = Unassigned()
    source: Optional[ActionSource] = Unassigned()
    action_type: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class AddTagsInput(Base):
    """TBA"""
    resource_arn: str
    tags: list


@dataclass
class AddTagsOutput(Base):
    """TBA"""
    tags: Optional[list] = Unassigned()


@dataclass
class AdditionalInferenceSpecificationDefinition(Base):
    """TBA"""
    name: str
    containers: list
    description: Optional[str] = Unassigned()
    supported_transform_instance_types: Optional[list] = Unassigned()
    supported_realtime_inference_instance_types: Optional[list] = Unassigned()
    supported_content_types: Optional[list] = Unassigned()
    supported_response_m_i_m_e_types: Optional[list] = Unassigned()


@dataclass
class AdditionalS3DataSource(Base):
    """TBA"""
    s3_data_type: str
    s3_uri: str
    compression_type: Optional[str] = Unassigned()


@dataclass
class AgentVersion(Base):
    """TBA"""
    version: str
    agent_count: int


@dataclass
class Alarm(Base):
    """TBA"""
    alarm_name: Optional[str] = Unassigned()


@dataclass
class TrainingRepositoryAuthConfig(Base):
    """TBA"""
    training_repository_credentials_provider_arn: str


@dataclass
class TrainingImageConfig(Base):
    """TBA"""
    training_repository_access_mode: str
    training_repository_auth_config: Optional[TrainingRepositoryAuthConfig] = Unassigned()


@dataclass
class AlgorithmSpecification(Base):
    """TBA"""
    training_input_mode: str
    training_image: Optional[str] = Unassigned()
    algorithm_name: Optional[str] = Unassigned()
    metric_definitions: Optional[list] = Unassigned()
    enable_sage_maker_metrics_time_series: Optional[bool] = Unassigned()
    container_entrypoint: Optional[list] = Unassigned()
    container_arguments: Optional[list] = Unassigned()
    training_image_config: Optional[TrainingImageConfig] = Unassigned()


@dataclass
class AlgorithmStatusDetails(Base):
    """TBA"""
    validation_statuses: Optional[list] = Unassigned()
    image_scan_statuses: Optional[list] = Unassigned()


@dataclass
class AlgorithmStatusItem(Base):
    """TBA"""
    name: str
    status: str
    failure_reason: Optional[str] = Unassigned()


@dataclass
class AlgorithmSummary(Base):
    """TBA"""
    algorithm_name: str
    algorithm_arn: str
    creation_time: datetime.datetime
    algorithm_status: str
    algorithm_description: Optional[str] = Unassigned()


@dataclass
class OutputDataConfig(Base):
    """TBA"""
    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()


@dataclass
class ResourceConfig(Base):
    """TBA"""
    volume_size_in_g_b: int
    instance_type: Optional[str] = Unassigned()
    instance_count: Optional[int] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    keep_alive_period_in_seconds: Optional[int] = Unassigned()
    instance_groups: Optional[list] = Unassigned()


@dataclass
class StoppingCondition(Base):
    """TBA"""
    max_runtime_in_seconds: Optional[int] = Unassigned()
    max_wait_time_in_seconds: Optional[int] = Unassigned()
    max_pending_time_in_seconds: Optional[int] = Unassigned()


@dataclass
class TrainingJobDefinition(Base):
    """TBA"""
    training_input_mode: str
    input_data_config: list
    output_data_config: OutputDataConfig
    resource_config: ResourceConfig
    stopping_condition: StoppingCondition
    hyper_parameters: Optional[dict] = Unassigned()


@dataclass
class TransformS3DataSource(Base):
    """TBA"""
    s3_data_type: str
    s3_uri: str


@dataclass
class TransformDataSource(Base):
    """TBA"""
    s3_data_source: TransformS3DataSource


@dataclass
class TransformInput(Base):
    """TBA"""
    data_source: TransformDataSource
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    split_type: Optional[str] = Unassigned()


@dataclass
class TransformOutput(Base):
    """TBA"""
    s3_output_path: str
    accept: Optional[str] = Unassigned()
    assemble_with: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class TransformResources(Base):
    """TBA"""
    instance_type: str
    instance_count: int
    volume_kms_key_id: Optional[str] = Unassigned()


@dataclass
class TransformJobDefinition(Base):
    """TBA"""
    transform_input: TransformInput
    transform_output: TransformOutput
    transform_resources: TransformResources
    max_concurrent_transforms: Optional[int] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class AlgorithmValidationProfile(Base):
    """TBA"""
    profile_name: str
    training_job_definition: TrainingJobDefinition
    transform_job_definition: Optional[TransformJobDefinition] = Unassigned()


@dataclass
class AlgorithmValidationSpecification(Base):
    """TBA"""
    validation_role: str
    validation_profiles: list


@dataclass
class AnnotationConsolidationConfig(Base):
    """TBA"""
    annotation_consolidation_lambda_arn: str


@dataclass
class ResourceSpec(Base):
    """TBA"""
    sage_maker_image_arn: Optional[str] = Unassigned()
    sage_maker_image_version_arn: Optional[str] = Unassigned()
    sage_maker_image_version_alias: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    lifecycle_config_arn: Optional[str] = Unassigned()


@dataclass
class AppDetails(Base):
    """TBA"""
    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    app_type: Optional[str] = Unassigned()
    app_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    resource_spec: Optional[ResourceSpec] = Unassigned()


@dataclass
class FileSystemConfig(Base):
    """TBA"""
    mount_path: Optional[str] = Unassigned()
    default_uid: Optional[int] = Unassigned()
    default_gid: Optional[int] = Unassigned()


@dataclass
class KernelGatewayImageConfig(Base):
    """TBA"""
    kernel_specs: list
    file_system_config: Optional[FileSystemConfig] = Unassigned()


@dataclass
class ContainerConfig(Base):
    """TBA"""
    container_arguments: Optional[list] = Unassigned()
    container_entrypoint: Optional[list] = Unassigned()
    container_environment_variables: Optional[dict] = Unassigned()


@dataclass
class JupyterLabAppImageConfig(Base):
    """TBA"""
    file_system_config: Optional[FileSystemConfig] = Unassigned()
    container_config: Optional[ContainerConfig] = Unassigned()


@dataclass
class AppImageConfigDetails(Base):
    """TBA"""
    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()


@dataclass
class AppSpecification(Base):
    """TBA"""
    image_uri: str
    container_entrypoint: Optional[list] = Unassigned()
    container_arguments: Optional[list] = Unassigned()


@dataclass
class ArtifactSource(Base):
    """TBA"""
    source_uri: str
    source_types: Optional[list] = Unassigned()


@dataclass
class ArtifactSourceType(Base):
    """TBA"""
    source_id_type: str
    value: str


@dataclass
class ArtifactSummary(Base):
    """TBA"""
    artifact_arn: Optional[str] = Unassigned()
    artifact_name: Optional[str] = Unassigned()
    source: Optional[ArtifactSource] = Unassigned()
    artifact_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class IamIdentity(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()
    principal_id: Optional[str] = Unassigned()
    source_identity: Optional[str] = Unassigned()


@dataclass
class UserContext(Base):
    """TBA"""
    user_profile_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    iam_identity: Optional[IamIdentity] = Unassigned()


@dataclass
class AssociationSummary(Base):
    """TBA"""
    source_arn: Optional[str] = Unassigned()
    destination_arn: Optional[str] = Unassigned()
    source_type: Optional[str] = Unassigned()
    destination_type: Optional[str] = Unassigned()
    association_type: Optional[str] = Unassigned()
    source_name: Optional[str] = Unassigned()
    destination_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()


@dataclass
class AsyncInferenceClientConfig(Base):
    """TBA"""
    max_concurrent_invocations_per_instance: Optional[int] = Unassigned()


@dataclass
class AsyncInferenceNotificationConfig(Base):
    """TBA"""
    success_topic: Optional[str] = Unassigned()
    error_topic: Optional[str] = Unassigned()
    include_inference_response_in: Optional[list] = Unassigned()


@dataclass
class AsyncInferenceOutputConfig(Base):
    """TBA"""
    kms_key_id: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    notification_config: Optional[AsyncInferenceNotificationConfig] = Unassigned()
    s3_failure_path: Optional[str] = Unassigned()


@dataclass
class AsyncInferenceConfig(Base):
    """TBA"""
    output_config: AsyncInferenceOutputConfig
    client_config: Optional[AsyncInferenceClientConfig] = Unassigned()


@dataclass
class AthenaDatasetDefinition(Base):
    """TBA"""
    catalog: str
    database: str
    query_string: str
    output_s3_uri: str
    output_format: str
    work_group: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    output_compression: Optional[str] = Unassigned()


@dataclass
class AutoMLAlgorithmConfig(Base):
    """TBA"""
    auto_m_l_algorithms: list


@dataclass
class FinalAutoMLJobObjectiveMetric(Base):
    """TBA"""
    metric_name: str
    value: float
    type: Optional[str] = Unassigned()
    standard_metric_name: Optional[str] = Unassigned()


@dataclass
class CandidateArtifactLocations(Base):
    """TBA"""
    explainability: str
    model_insights: Optional[str] = Unassigned()
    backtest_results: Optional[str] = Unassigned()


@dataclass
class CandidateProperties(Base):
    """TBA"""
    candidate_artifact_locations: Optional[CandidateArtifactLocations] = Unassigned()
    candidate_metrics: Optional[list] = Unassigned()


@dataclass
class AutoMLCandidate(Base):
    """TBA"""
    candidate_name: str
    objective_status: str
    candidate_steps: list
    candidate_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    final_auto_m_l_job_objective_metric: Optional[FinalAutoMLJobObjectiveMetric] = Unassigned()
    inference_containers: Optional[list] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    candidate_properties: Optional[CandidateProperties] = Unassigned()
    inference_container_definitions: Optional[dict] = Unassigned()


@dataclass
class AutoMLCandidateGenerationConfig(Base):
    """TBA"""
    feature_specification_s3_uri: Optional[str] = Unassigned()
    algorithms_config: Optional[list] = Unassigned()


@dataclass
class AutoMLCandidateStep(Base):
    """TBA"""
    candidate_step_type: str
    candidate_step_arn: str
    candidate_step_name: str


@dataclass
class AutoMLS3DataSource(Base):
    """TBA"""
    s3_data_type: str
    s3_uri: str


@dataclass
class AutoMLDataSource(Base):
    """TBA"""
    s3_data_source: AutoMLS3DataSource


@dataclass
class AutoMLChannel(Base):
    """TBA"""
    target_attribute_name: str
    data_source: Optional[AutoMLDataSource] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    content_type: Optional[str] = Unassigned()
    channel_type: Optional[str] = Unassigned()
    sample_weight_attribute_name: Optional[str] = Unassigned()


@dataclass
class AutoMLContainerDefinition(Base):
    """TBA"""
    image: str
    model_data_url: str
    environment: Optional[dict] = Unassigned()


@dataclass
class AutoMLDataSplitConfig(Base):
    """TBA"""
    validation_fraction: Optional[float] = Unassigned()


@dataclass
class AutoMLJobArtifacts(Base):
    """TBA"""
    candidate_definition_notebook_location: Optional[str] = Unassigned()
    data_exploration_notebook_location: Optional[str] = Unassigned()


@dataclass
class AutoMLJobChannel(Base):
    """TBA"""
    channel_type: Optional[str] = Unassigned()
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    data_source: Optional[AutoMLDataSource] = Unassigned()


@dataclass
class AutoMLJobCompletionCriteria(Base):
    """TBA"""
    max_candidates: Optional[int] = Unassigned()
    max_runtime_per_training_job_in_seconds: Optional[int] = Unassigned()
    max_auto_m_l_job_runtime_in_seconds: Optional[int] = Unassigned()


@dataclass
class VpcConfig(Base):
    """TBA"""
    security_group_ids: list
    subnets: list


@dataclass
class AutoMLSecurityConfig(Base):
    """TBA"""
    volume_kms_key_id: Optional[str] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


@dataclass
class AutoMLJobConfig(Base):
    """TBA"""
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    security_config: Optional[AutoMLSecurityConfig] = Unassigned()
    candidate_generation_config: Optional[AutoMLCandidateGenerationConfig] = Unassigned()
    data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned()
    mode: Optional[str] = Unassigned()


@dataclass
class AutoMLJobObjective(Base):
    """TBA"""
    metric_name: str


@dataclass
class AutoMLJobStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class AutoMLJobSummary(Base):
    """TBA"""
    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[list] = Unassigned()


@dataclass
class AutoMLOutputDataConfig(Base):
    """TBA"""
    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class AutoMLPartialFailureReason(Base):
    """TBA"""
    partial_failure_message: Optional[str] = Unassigned()


@dataclass
class ImageClassificationJobConfig(Base):
    """TBA"""
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


@dataclass
class TextClassificationJobConfig(Base):
    """TBA"""
    content_column: str
    target_label_column: str
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


@dataclass
class TimeSeriesTransformations(Base):
    """TBA"""
    filling: Optional[dict] = Unassigned()
    aggregation: Optional[dict] = Unassigned()


@dataclass
class TimeSeriesConfig(Base):
    """TBA"""
    target_attribute_name: str
    timestamp_attribute_name: str
    item_identifier_attribute_name: str
    grouping_attribute_names: Optional[list] = Unassigned()


@dataclass
class TimeSeriesForecastingJobConfig(Base):
    """TBA"""
    forecast_frequency: str
    forecast_horizon: int
    time_series_config: TimeSeriesConfig
    feature_specification_s3_uri: Optional[str] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    forecast_quantiles: Optional[list] = Unassigned()
    transformations: Optional[TimeSeriesTransformations] = Unassigned()
    holiday_config: Optional[list] = Unassigned()


@dataclass
class CandidateGenerationConfig(Base):
    """TBA"""
    algorithms_config: Optional[list] = Unassigned()


@dataclass
class TabularJobConfig(Base):
    """TBA"""
    target_attribute_name: str
    candidate_generation_config: Optional[CandidateGenerationConfig] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    feature_specification_s3_uri: Optional[str] = Unassigned()
    mode: Optional[str] = Unassigned()
    generate_candidate_definitions_only: Optional[bool] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    sample_weight_attribute_name: Optional[str] = Unassigned()


@dataclass
class ModelAccessConfig(Base):
    """TBA"""
    accept_eula: bool


@dataclass
class TextGenerationJobConfig(Base):
    """TBA"""
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    base_model_name: Optional[str] = Unassigned()
    text_generation_hyper_parameters: Optional[dict] = Unassigned()
    model_access_config: Optional[ModelAccessConfig] = Unassigned()


@dataclass
class AutoMLProblemTypeConfig(Base):
    """TBA"""
    image_classification_job_config: Optional[ImageClassificationJobConfig] = Unassigned()
    text_classification_job_config: Optional[TextClassificationJobConfig] = Unassigned()
    time_series_forecasting_job_config: Optional[TimeSeriesForecastingJobConfig] = Unassigned()
    tabular_job_config: Optional[TabularJobConfig] = Unassigned()
    text_generation_job_config: Optional[TextGenerationJobConfig] = Unassigned()


@dataclass
class TabularResolvedAttributes(Base):
    """TBA"""
    problem_type: Optional[str] = Unassigned()


@dataclass
class TextGenerationResolvedAttributes(Base):
    """TBA"""
    base_model_name: Optional[str] = Unassigned()


@dataclass
class AutoMLProblemTypeResolvedAttributes(Base):
    """TBA"""
    tabular_resolved_attributes: Optional[TabularResolvedAttributes] = Unassigned()
    text_generation_resolved_attributes: Optional[TextGenerationResolvedAttributes] = Unassigned()


@dataclass
class AutoMLResolvedAttributes(Base):
    """TBA"""
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    auto_m_l_problem_type_resolved_attributes: Optional[AutoMLProblemTypeResolvedAttributes] = Unassigned()


@dataclass
class AutoParameter(Base):
    """TBA"""
    name: str
    value_hint: str


@dataclass
class AutoRollbackConfig(Base):
    """TBA"""
    alarms: Optional[list] = Unassigned()


@dataclass
class Autotune(Base):
    """TBA"""
    mode: str


@dataclass
class BatchDataCaptureConfig(Base):
    """TBA"""
    destination_s3_uri: str
    kms_key_id: Optional[str] = Unassigned()
    generate_inference_id: Optional[bool] = Unassigned()


@dataclass
class BatchDescribeModelPackageError(Base):
    """TBA"""
    error_code: str
    error_response: str


@dataclass
class BatchDescribeModelPackageInput(Base):
    """TBA"""
    model_package_arn_list: list


@dataclass
class BatchDescribeModelPackageOutput(Base):
    """TBA"""
    model_package_summaries: Optional[dict] = Unassigned()
    batch_describe_model_package_error_map: Optional[dict] = Unassigned()


@dataclass
class InferenceSpecification(Base):
    """TBA"""
    containers: list
    supported_transform_instance_types: Optional[list] = Unassigned()
    supported_realtime_inference_instance_types: Optional[list] = Unassigned()
    supported_content_types: Optional[list] = Unassigned()
    supported_response_m_i_m_e_types: Optional[list] = Unassigned()


@dataclass
class BatchDescribeModelPackageSummary(Base):
    """TBA"""
    model_package_group_name: str
    model_package_arn: str
    creation_time: datetime.datetime
    inference_specification: InferenceSpecification
    model_package_status: str
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()


@dataclass
class MonitoringCsvDatasetFormat(Base):
    """TBA"""
    header: Optional[bool] = Unassigned()


@dataclass
class MonitoringJsonDatasetFormat(Base):
    """TBA"""
    line: Optional[bool] = Unassigned()


@dataclass
class MonitoringParquetDatasetFormat(Base):
    """TBA"""


@dataclass
class MonitoringDatasetFormat(Base):
    """TBA"""
    csv: Optional[MonitoringCsvDatasetFormat] = Unassigned()
    json: Optional[MonitoringJsonDatasetFormat] = Unassigned()
    parquet: Optional[MonitoringParquetDatasetFormat] = Unassigned()


@dataclass
class BatchTransformInput(Base):
    """TBA"""
    data_captured_destination_s3_uri: str
    dataset_format: MonitoringDatasetFormat
    local_path: str
    s3_input_mode: Optional[str] = Unassigned()
    s3_data_distribution_type: Optional[str] = Unassigned()
    features_attribute: Optional[str] = Unassigned()
    inference_attribute: Optional[str] = Unassigned()
    probability_attribute: Optional[str] = Unassigned()
    probability_threshold_attribute: Optional[float] = Unassigned()
    start_time_offset: Optional[str] = Unassigned()
    end_time_offset: Optional[str] = Unassigned()
    exclude_features_attribute: Optional[str] = Unassigned()


@dataclass
class BestObjectiveNotImproving(Base):
    """TBA"""
    max_number_of_training_jobs_not_improving: Optional[int] = Unassigned()


@dataclass
class MetricsSource(Base):
    """TBA"""
    content_type: str
    s3_uri: str
    content_digest: Optional[str] = Unassigned()


@dataclass
class Bias(Base):
    """TBA"""
    report: Optional[MetricsSource] = Unassigned()
    pre_training_report: Optional[MetricsSource] = Unassigned()
    post_training_report: Optional[MetricsSource] = Unassigned()


@dataclass
class CapacitySize(Base):
    """TBA"""
    type: str
    value: int


@dataclass
class TrafficRoutingConfig(Base):
    """TBA"""
    type: str
    wait_interval_in_seconds: int
    canary_size: Optional[CapacitySize] = Unassigned()
    linear_step_size: Optional[CapacitySize] = Unassigned()


@dataclass
class BlueGreenUpdatePolicy(Base):
    """TBA"""
    traffic_routing_configuration: TrafficRoutingConfig
    termination_wait_in_seconds: Optional[int] = Unassigned()
    maximum_execution_timeout_in_seconds: Optional[int] = Unassigned()


@dataclass
class CacheHitResult(Base):
    """TBA"""
    source_pipeline_execution_arn: Optional[str] = Unassigned()


@dataclass
class CallbackStepMetadata(Base):
    """TBA"""
    callback_token: Optional[str] = Unassigned()
    sqs_queue_url: Optional[str] = Unassigned()
    output_parameters: Optional[list] = Unassigned()


@dataclass
class TimeSeriesForecastingSettings(Base):
    """TBA"""
    status: Optional[str] = Unassigned()
    amazon_forecast_role_arn: Optional[str] = Unassigned()


@dataclass
class ModelRegisterSettings(Base):
    """TBA"""
    status: Optional[str] = Unassigned()
    cross_account_model_register_role_arn: Optional[str] = Unassigned()


@dataclass
class WorkspaceSettings(Base):
    """TBA"""
    s3_artifact_path: Optional[str] = Unassigned()
    s3_kms_key_id: Optional[str] = Unassigned()


@dataclass
class DirectDeploySettings(Base):
    """TBA"""
    status: Optional[str] = Unassigned()


@dataclass
class KendraSettings(Base):
    """TBA"""
    status: Optional[str] = Unassigned()


@dataclass
class GenerativeAiSettings(Base):
    """TBA"""
    amazon_bedrock_role_arn: Optional[str] = Unassigned()


@dataclass
class CanvasAppSettings(Base):
    """TBA"""
    time_series_forecasting_settings: Optional[TimeSeriesForecastingSettings] = Unassigned()
    model_register_settings: Optional[ModelRegisterSettings] = Unassigned()
    workspace_settings: Optional[WorkspaceSettings] = Unassigned()
    identity_provider_o_auth_settings: Optional[list] = Unassigned()
    direct_deploy_settings: Optional[DirectDeploySettings] = Unassigned()
    kendra_settings: Optional[KendraSettings] = Unassigned()
    generative_ai_settings: Optional[GenerativeAiSettings] = Unassigned()


@dataclass
class CaptureContentTypeHeader(Base):
    """TBA"""
    csv_content_types: Optional[list] = Unassigned()
    json_content_types: Optional[list] = Unassigned()


@dataclass
class CaptureOption(Base):
    """TBA"""
    capture_mode: str


@dataclass
class CategoricalParameter(Base):
    """TBA"""
    name: str
    value: list


@dataclass
class CategoricalParameterRange(Base):
    """TBA"""
    name: str
    values: list


@dataclass
class CategoricalParameterRangeSpecification(Base):
    """TBA"""
    values: list


@dataclass
class S3DataSource(Base):
    """TBA"""
    s3_data_type: str
    s3_uri: str
    s3_data_distribution_type: Optional[str] = Unassigned()
    attribute_names: Optional[list] = Unassigned()
    instance_group_names: Optional[list] = Unassigned()


@dataclass
class FileSystemDataSource(Base):
    """TBA"""
    file_system_id: str
    file_system_access_mode: str
    file_system_type: str
    directory_path: str


@dataclass
class DataSource(Base):
    """TBA"""
    s3_data_source: Optional[S3DataSource] = Unassigned()
    file_system_data_source: Optional[FileSystemDataSource] = Unassigned()


@dataclass
class ShuffleConfig(Base):
    """TBA"""
    seed: int


@dataclass
class Channel(Base):
    """TBA"""
    channel_name: str
    data_source: DataSource
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    record_wrapper_type: Optional[str] = Unassigned()
    input_mode: Optional[str] = Unassigned()
    shuffle_config: Optional[ShuffleConfig] = Unassigned()


@dataclass
class ChannelSpecification(Base):
    """TBA"""
    name: str
    supported_content_types: list
    supported_input_modes: list
    description: Optional[str] = Unassigned()
    is_required: Optional[bool] = Unassigned()
    supported_compression_types: Optional[list] = Unassigned()


@dataclass
class CheckpointConfig(Base):
    """TBA"""
    s3_uri: str
    local_path: Optional[str] = Unassigned()


@dataclass
class ClarifyCheckStepMetadata(Base):
    """TBA"""
    check_type: Optional[str] = Unassigned()
    baseline_used_for_drift_check_constraints: Optional[str] = Unassigned()
    calculated_baseline_constraints: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    violation_report: Optional[str] = Unassigned()
    check_job_arn: Optional[str] = Unassigned()
    skip_check: Optional[bool] = Unassigned()
    register_new_baseline: Optional[bool] = Unassigned()


@dataclass
class ClarifyInferenceConfig(Base):
    """TBA"""
    features_attribute: Optional[str] = Unassigned()
    content_template: Optional[str] = Unassigned()
    max_record_count: Optional[int] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    probability_index: Optional[int] = Unassigned()
    label_index: Optional[int] = Unassigned()
    probability_attribute: Optional[str] = Unassigned()
    label_attribute: Optional[str] = Unassigned()
    label_headers: Optional[list] = Unassigned()
    feature_headers: Optional[list] = Unassigned()
    feature_types: Optional[list] = Unassigned()


@dataclass
class ClarifyShapBaselineConfig(Base):
    """TBA"""
    mime_type: Optional[str] = Unassigned()
    shap_baseline: Optional[str] = Unassigned()
    shap_baseline_uri: Optional[str] = Unassigned()


@dataclass
class ClarifyTextConfig(Base):
    """TBA"""
    language: str
    granularity: str


@dataclass
class ClarifyShapConfig(Base):
    """TBA"""
    shap_baseline_config: ClarifyShapBaselineConfig
    number_of_samples: Optional[int] = Unassigned()
    use_logit: Optional[bool] = Unassigned()
    seed: Optional[int] = Unassigned()
    text_config: Optional[ClarifyTextConfig] = Unassigned()


@dataclass
class ClarifyExplainerConfig(Base):
    """TBA"""
    shap_config: ClarifyShapConfig
    enable_explanations: Optional[str] = Unassigned()
    inference_config: Optional[ClarifyInferenceConfig] = Unassigned()


@dataclass
class ClusterLifeCycleConfig(Base):
    """TBA"""
    source_s3_uri: str
    on_create: str


@dataclass
class ClusterInstanceGroupDetails(Base):
    """TBA"""
    current_count: Optional[int] = Unassigned()
    target_count: Optional[int] = Unassigned()
    instance_group_name: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    life_cycle_config: Optional[ClusterLifeCycleConfig] = Unassigned()
    execution_role: Optional[str] = Unassigned()
    threads_per_core: Optional[int] = Unassigned()


@dataclass
class ClusterInstanceGroupSpecification(Base):
    """TBA"""
    instance_count: int
    instance_group_name: str
    instance_type: str
    life_cycle_config: ClusterLifeCycleConfig
    execution_role: str
    threads_per_core: Optional[int] = Unassigned()


@dataclass
class ClusterInstanceStatusDetails(Base):
    """TBA"""
    status: str
    message: Optional[str] = Unassigned()


@dataclass
class ClusterNodeDetails(Base):
    """TBA"""
    instance_group_name: Optional[str] = Unassigned()
    instance_id: Optional[str] = Unassigned()
    instance_status: Optional[ClusterInstanceStatusDetails] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    launch_time: Optional[datetime.datetime] = Unassigned()
    life_cycle_config: Optional[ClusterLifeCycleConfig] = Unassigned()
    threads_per_core: Optional[int] = Unassigned()


@dataclass
class ClusterNodeSummary(Base):
    """TBA"""
    instance_group_name: str
    instance_id: str
    instance_type: str
    launch_time: datetime.datetime
    instance_status: ClusterInstanceStatusDetails


@dataclass
class ClusterSummary(Base):
    """TBA"""
    cluster_arn: str
    cluster_name: str
    creation_time: datetime.datetime
    cluster_status: str


@dataclass
class CodeEditorAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    lifecycle_config_arns: Optional[list] = Unassigned()


@dataclass
class CodeRepository(Base):
    """TBA"""
    repository_url: str


@dataclass
class GitConfig(Base):
    """TBA"""
    repository_url: str
    branch: Optional[str] = Unassigned()
    secret_arn: Optional[str] = Unassigned()


@dataclass
class CodeRepositorySummary(Base):
    """TBA"""
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()


@dataclass
class CognitoConfig(Base):
    """TBA"""
    user_pool: str
    client_id: str


@dataclass
class CognitoMemberDefinition(Base):
    """TBA"""
    user_pool: str
    user_group: str
    client_id: str


@dataclass
class VectorConfig(Base):
    """TBA"""
    dimension: int


@dataclass
class CollectionConfig(Base):
    """TBA"""
    vector_config: Optional[VectorConfig] = Unassigned()


@dataclass
class CollectionConfiguration(Base):
    """TBA"""
    collection_name: Optional[str] = Unassigned()
    collection_parameters: Optional[dict] = Unassigned()


@dataclass
class CompilationJobSummary(Base):
    """TBA"""
    compilation_job_name: str
    compilation_job_arn: str
    creation_time: datetime.datetime
    compilation_job_status: str
    compilation_start_time: Optional[datetime.datetime] = Unassigned()
    compilation_end_time: Optional[datetime.datetime] = Unassigned()
    compilation_target_device: Optional[str] = Unassigned()
    compilation_target_platform_os: Optional[str] = Unassigned()
    compilation_target_platform_arch: Optional[str] = Unassigned()
    compilation_target_platform_accelerator: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ConditionStepMetadata(Base):
    """TBA"""
    outcome: Optional[str] = Unassigned()


@dataclass
class ConflictException(Base):
    """TBA"""
    message: Optional[str] = Unassigned()


@dataclass
class RepositoryAuthConfig(Base):
    """TBA"""
    repository_credentials_provider_arn: str


@dataclass
class ImageConfig(Base):
    """TBA"""
    repository_access_mode: str
    repository_auth_config: Optional[RepositoryAuthConfig] = Unassigned()


@dataclass
class S3ModelDataSource(Base):
    """TBA"""
    s3_uri: str
    s3_data_type: str
    compression_type: str
    model_access_config: Optional[ModelAccessConfig] = Unassigned()


@dataclass
class ModelDataSource(Base):
    """TBA"""
    s3_data_source: Optional[S3ModelDataSource] = Unassigned()


@dataclass
class MultiModelConfig(Base):
    """TBA"""
    model_cache_setting: Optional[str] = Unassigned()


@dataclass
class ContainerDefinition(Base):
    """TBA"""
    container_hostname: Optional[str] = Unassigned()
    image: Optional[str] = Unassigned()
    image_config: Optional[ImageConfig] = Unassigned()
    mode: Optional[str] = Unassigned()
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()
    environment: Optional[dict] = Unassigned()
    model_package_name: Optional[str] = Unassigned()
    inference_specification_name: Optional[str] = Unassigned()
    multi_model_config: Optional[MultiModelConfig] = Unassigned()


@dataclass
class ContextSource(Base):
    """TBA"""
    source_uri: str
    source_type: Optional[str] = Unassigned()
    source_id: Optional[str] = Unassigned()


@dataclass
class ContextSummary(Base):
    """TBA"""
    context_arn: Optional[str] = Unassigned()
    context_name: Optional[str] = Unassigned()
    source: Optional[ContextSource] = Unassigned()
    context_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ContinuousParameterRange(Base):
    """TBA"""
    name: str
    min_value: str
    max_value: str
    scaling_type: Optional[str] = Unassigned()


@dataclass
class ContinuousParameterRangeSpecification(Base):
    """TBA"""
    min_value: str
    max_value: str


@dataclass
class ConvergenceDetected(Base):
    """TBA"""
    complete_on_convergence: Optional[str] = Unassigned()


@dataclass
class MetadataProperties(Base):
    """TBA"""
    commit_id: Optional[str] = Unassigned()
    repository: Optional[str] = Unassigned()
    generated_by: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()


@dataclass
class TrainingSpecification(Base):
    """TBA"""
    training_image: str
    supported_training_instance_types: list
    training_channels: list
    training_image_digest: Optional[str] = Unassigned()
    supported_hyper_parameters: Optional[list] = Unassigned()
    supports_distributed_training: Optional[bool] = Unassigned()
    metric_definitions: Optional[list] = Unassigned()
    supported_tuning_job_objective_metrics: Optional[list] = Unassigned()
    additional_s3_data_source: Optional[AdditionalS3DataSource] = Unassigned()


@dataclass
class CreateAlgorithmInput(Base):
    """TBA"""
    algorithm_name: str
    training_specification: TrainingSpecification
    algorithm_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    validation_specification: Optional[AlgorithmValidationSpecification] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class CreateAlgorithmOutput(Base):
    """TBA"""
    algorithm_arn: str


@dataclass
class ModelDeployConfig(Base):
    """TBA"""
    auto_generate_endpoint_name: Optional[bool] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()


@dataclass
class CreateCodeRepositoryInput(Base):
    """TBA"""
    code_repository_name: str
    git_config: GitConfig
    tags: Optional[list] = Unassigned()


@dataclass
class CreateCodeRepositoryOutput(Base):
    """TBA"""
    code_repository_arn: str


@dataclass
class InputConfig(Base):
    """TBA"""
    s3_uri: str
    framework: str
    data_input_config: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()


@dataclass
class TargetPlatform(Base):
    """TBA"""
    os: str
    arch: str
    accelerator: Optional[str] = Unassigned()


@dataclass
class OutputConfig(Base):
    """TBA"""
    s3_output_location: str
    target_device: Optional[str] = Unassigned()
    target_platform: Optional[TargetPlatform] = Unassigned()
    compiler_options: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class NeoVpcConfig(Base):
    """TBA"""
    security_group_ids: list
    subnets: list


@dataclass
class MonitoringConstraintsResource(Base):
    """TBA"""
    s3_uri: Optional[str] = Unassigned()


@dataclass
class MonitoringStatisticsResource(Base):
    """TBA"""
    s3_uri: Optional[str] = Unassigned()


@dataclass
class DataQualityBaselineConfig(Base):
    """TBA"""
    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()
    statistics_resource: Optional[MonitoringStatisticsResource] = Unassigned()


@dataclass
class DataQualityAppSpecification(Base):
    """TBA"""
    image_uri: str
    container_entrypoint: Optional[list] = Unassigned()
    container_arguments: Optional[list] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class EndpointInput(Base):
    """TBA"""
    endpoint_name: str
    local_path: str
    s3_input_mode: Optional[str] = Unassigned()
    s3_data_distribution_type: Optional[str] = Unassigned()
    features_attribute: Optional[str] = Unassigned()
    inference_attribute: Optional[str] = Unassigned()
    probability_attribute: Optional[str] = Unassigned()
    probability_threshold_attribute: Optional[float] = Unassigned()
    start_time_offset: Optional[str] = Unassigned()
    end_time_offset: Optional[str] = Unassigned()
    exclude_features_attribute: Optional[str] = Unassigned()


@dataclass
class DataQualityJobInput(Base):
    """TBA"""
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class MonitoringOutputConfig(Base):
    """TBA"""
    monitoring_outputs: list
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class MonitoringClusterConfig(Base):
    """TBA"""
    instance_count: int
    instance_type: str
    volume_size_in_g_b: int
    volume_kms_key_id: Optional[str] = Unassigned()


@dataclass
class MonitoringResources(Base):
    """TBA"""
    cluster_config: MonitoringClusterConfig


@dataclass
class MonitoringNetworkConfig(Base):
    """TBA"""
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


@dataclass
class MonitoringStoppingCondition(Base):
    """TBA"""
    max_runtime_in_seconds: int


@dataclass
class EdgeOutputConfig(Base):
    """TBA"""
    s3_output_location: str
    kms_key_id: Optional[str] = Unassigned()
    preset_deployment_type: Optional[str] = Unassigned()
    preset_deployment_config: Optional[str] = Unassigned()


@dataclass
class SharingSettings(Base):
    """TBA"""
    notebook_output_option: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    s3_kms_key_id: Optional[str] = Unassigned()


@dataclass
class JupyterServerAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    lifecycle_config_arns: Optional[list] = Unassigned()
    code_repositories: Optional[list] = Unassigned()


@dataclass
class KernelGatewayAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[list] = Unassigned()
    lifecycle_config_arns: Optional[list] = Unassigned()


@dataclass
class TensorBoardAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()


@dataclass
class RStudioServerProAppSettings(Base):
    """TBA"""
    access_status: Optional[str] = Unassigned()
    user_group: Optional[str] = Unassigned()


@dataclass
class RSessionAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[list] = Unassigned()


@dataclass
class JupyterLabAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[list] = Unassigned()
    lifecycle_config_arns: Optional[list] = Unassigned()
    code_repositories: Optional[list] = Unassigned()


@dataclass
class DefaultEbsStorageSettings(Base):
    """TBA"""
    default_ebs_volume_size_in_gb: int
    maximum_ebs_volume_size_in_gb: int


@dataclass
class DefaultSpaceStorageSettings(Base):
    """TBA"""
    default_ebs_storage_settings: Optional[DefaultEbsStorageSettings] = Unassigned()


@dataclass
class CustomPosixUserConfig(Base):
    """TBA"""
    uid: int
    gid: int


@dataclass
class UserSettings(Base):
    """TBA"""
    execution_role: Optional[str] = Unassigned()
    security_groups: Optional[list] = Unassigned()
    sharing_settings: Optional[SharingSettings] = Unassigned()
    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()
    tensor_board_app_settings: Optional[TensorBoardAppSettings] = Unassigned()
    r_studio_server_pro_app_settings: Optional[RStudioServerProAppSettings] = Unassigned()
    r_session_app_settings: Optional[RSessionAppSettings] = Unassigned()
    canvas_app_settings: Optional[CanvasAppSettings] = Unassigned()
    code_editor_app_settings: Optional[CodeEditorAppSettings] = Unassigned()
    jupyter_lab_app_settings: Optional[JupyterLabAppSettings] = Unassigned()
    space_storage_settings: Optional[DefaultSpaceStorageSettings] = Unassigned()
    default_landing_uri: Optional[str] = Unassigned()
    studio_web_portal: Optional[str] = Unassigned()
    custom_posix_user_config: Optional[CustomPosixUserConfig] = Unassigned()
    custom_file_system_configs: Optional[list] = Unassigned()


@dataclass
class RStudioServerProDomainSettings(Base):
    """TBA"""
    domain_execution_role_arn: str
    r_studio_connect_url: Optional[str] = Unassigned()
    r_studio_package_manager_url: Optional[str] = Unassigned()
    default_resource_spec: Optional[ResourceSpec] = Unassigned()


@dataclass
class DockerSettings(Base):
    """TBA"""
    enable_docker_access: Optional[str] = Unassigned()
    vpc_only_trusted_accounts: Optional[list] = Unassigned()


@dataclass
class DomainSettings(Base):
    """TBA"""
    security_group_ids: Optional[list] = Unassigned()
    r_studio_server_pro_domain_settings: Optional[RStudioServerProDomainSettings] = Unassigned()
    execution_role_identity_config: Optional[str] = Unassigned()
    docker_settings: Optional[DockerSettings] = Unassigned()


@dataclass
class DefaultSpaceSettings(Base):
    """TBA"""
    execution_role: Optional[str] = Unassigned()
    security_groups: Optional[list] = Unassigned()
    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()


@dataclass
class DataCaptureConfig(Base):
    """TBA"""
    initial_sampling_percentage: int
    destination_s3_uri: str
    capture_options: list
    enable_capture: Optional[bool] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    capture_content_type_header: Optional[CaptureContentTypeHeader] = Unassigned()


@dataclass
class ExplainerConfig(Base):
    """TBA"""
    clarify_explainer_config: Optional[ClarifyExplainerConfig] = Unassigned()


@dataclass
class CreateEndpointConfigInput(Base):
    """TBA"""
    endpoint_config_name: str
    production_variants: list
    data_capture_config: Optional[DataCaptureConfig] = Unassigned()
    tags: Optional[list] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[list] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()


@dataclass
class CreateEndpointConfigOutput(Base):
    """TBA"""
    endpoint_config_arn: str


@dataclass
class RollingUpdatePolicy(Base):
    """TBA"""
    maximum_batch_size: CapacitySize
    wait_interval_in_seconds: int
    maximum_execution_timeout_in_seconds: Optional[int] = Unassigned()
    rollback_maximum_batch_size: Optional[CapacitySize] = Unassigned()


@dataclass
class DeploymentConfig(Base):
    """TBA"""
    blue_green_update_policy: Optional[BlueGreenUpdatePolicy] = Unassigned()
    rolling_update_policy: Optional[RollingUpdatePolicy] = Unassigned()
    auto_rollback_configuration: Optional[AutoRollbackConfig] = Unassigned()


@dataclass
class CreateEndpointInput(Base):
    """TBA"""
    endpoint_name: str
    endpoint_config_name: str
    deployment_config: Optional[DeploymentConfig] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class CreateEndpointOutput(Base):
    """TBA"""
    endpoint_arn: str


@dataclass
class OnlineStoreSecurityConfig(Base):
    """TBA"""
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class TtlDuration(Base):
    """TBA"""
    unit: Optional[str] = Unassigned()
    value: Optional[int] = Unassigned()


@dataclass
class OnlineStoreConfig(Base):
    """TBA"""
    security_config: Optional[OnlineStoreSecurityConfig] = Unassigned()
    enable_online_store: Optional[bool] = Unassigned()
    ttl_duration: Optional[TtlDuration] = Unassigned()
    storage_type: Optional[str] = Unassigned()


@dataclass
class S3StorageConfig(Base):
    """TBA"""
    s3_uri: str
    kms_key_id: Optional[str] = Unassigned()
    resolved_output_s3_uri: Optional[str] = Unassigned()


@dataclass
class DataCatalogConfig(Base):
    """TBA"""
    table_name: str
    catalog: str
    database: str


@dataclass
class OfflineStoreConfig(Base):
    """TBA"""
    s3_storage_config: S3StorageConfig
    disable_glue_table_creation: Optional[bool] = Unassigned()
    data_catalog_config: Optional[DataCatalogConfig] = Unassigned()
    table_format: Optional[str] = Unassigned()


@dataclass
class ThroughputConfig(Base):
    """TBA"""
    throughput_mode: str
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


@dataclass
class HumanLoopRequestSource(Base):
    """TBA"""
    aws_managed_human_loop_request_source: str


@dataclass
class HumanLoopActivationConditionsConfig(Base):
    """TBA"""
    human_loop_activation_conditions: str


@dataclass
class HumanLoopActivationConfig(Base):
    """TBA"""
    human_loop_activation_conditions_config: HumanLoopActivationConditionsConfig


@dataclass
class USD(Base):
    """TBA"""
    dollars: Optional[int] = Unassigned()
    cents: Optional[int] = Unassigned()
    tenth_fractions_of_a_cent: Optional[int] = Unassigned()


@dataclass
class PublicWorkforceTaskPrice(Base):
    """TBA"""
    amount_in_usd: Optional[USD] = Unassigned()


@dataclass
class HumanLoopConfig(Base):
    """TBA"""
    workteam_arn: str
    human_task_ui_arn: str
    task_title: str
    task_description: str
    task_count: int
    task_availability_lifetime_in_seconds: Optional[int] = Unassigned()
    task_time_limit_in_seconds: Optional[int] = Unassigned()
    task_keywords: Optional[list] = Unassigned()
    public_workforce_task_price: Optional[PublicWorkforceTaskPrice] = Unassigned()


@dataclass
class FlowDefinitionOutputConfig(Base):
    """TBA"""
    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class HubS3StorageConfig(Base):
    """TBA"""
    s3_output_path: Optional[str] = Unassigned()


@dataclass
class UiTemplate(Base):
    """TBA"""
    content: str


@dataclass
class HyperbandStrategyConfig(Base):
    """TBA"""
    min_resource: Optional[int] = Unassigned()
    max_resource: Optional[int] = Unassigned()


@dataclass
class HyperParameterTuningJobStrategyConfig(Base):
    """TBA"""
    hyperband_strategy_config: Optional[HyperbandStrategyConfig] = Unassigned()


@dataclass
class HyperParameterTuningJobObjective(Base):
    """TBA"""
    type: str
    metric_name: str


@dataclass
class ResourceLimits(Base):
    """TBA"""
    max_parallel_training_jobs: int
    max_number_of_training_jobs: Optional[int] = Unassigned()
    max_runtime_in_seconds: Optional[int] = Unassigned()


@dataclass
class ParameterRanges(Base):
    """TBA"""
    integer_parameter_ranges: Optional[list] = Unassigned()
    continuous_parameter_ranges: Optional[list] = Unassigned()
    categorical_parameter_ranges: Optional[list] = Unassigned()
    auto_parameters: Optional[list] = Unassigned()


@dataclass
class TuningJobCompletionCriteria(Base):
    """TBA"""
    target_objective_metric_value: Optional[float] = Unassigned()
    best_objective_not_improving: Optional[BestObjectiveNotImproving] = Unassigned()
    convergence_detected: Optional[ConvergenceDetected] = Unassigned()


@dataclass
class HyperParameterTuningJobConfig(Base):
    """TBA"""
    strategy: str
    resource_limits: ResourceLimits
    strategy_config: Optional[HyperParameterTuningJobStrategyConfig] = Unassigned()
    hyper_parameter_tuning_job_objective: Optional[HyperParameterTuningJobObjective] = Unassigned()
    parameter_ranges: Optional[ParameterRanges] = Unassigned()
    training_job_early_stopping_type: Optional[str] = Unassigned()
    tuning_job_completion_criteria: Optional[TuningJobCompletionCriteria] = Unassigned()
    random_seed: Optional[int] = Unassigned()


@dataclass
class HyperParameterAlgorithmSpecification(Base):
    """TBA"""
    training_input_mode: str
    training_image: Optional[str] = Unassigned()
    algorithm_name: Optional[str] = Unassigned()
    metric_definitions: Optional[list] = Unassigned()


@dataclass
class HyperParameterTuningResourceConfig(Base):
    """TBA"""
    instance_type: Optional[str] = Unassigned()
    instance_count: Optional[int] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    allocation_strategy: Optional[str] = Unassigned()
    instance_configs: Optional[list] = Unassigned()


@dataclass
class RetryStrategy(Base):
    """TBA"""
    maximum_retry_attempts: int


@dataclass
class HyperParameterTrainingJobDefinition(Base):
    """TBA"""
    algorithm_specification: HyperParameterAlgorithmSpecification
    role_arn: str
    output_data_config: OutputDataConfig
    stopping_condition: StoppingCondition
    definition_name: Optional[str] = Unassigned()
    tuning_objective: Optional[HyperParameterTuningJobObjective] = Unassigned()
    hyper_parameter_ranges: Optional[ParameterRanges] = Unassigned()
    static_hyper_parameters: Optional[dict] = Unassigned()
    input_data_config: Optional[list] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    resource_config: Optional[ResourceConfig] = Unassigned()
    hyper_parameter_tuning_resource_config: Optional[HyperParameterTuningResourceConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_managed_spot_training: Optional[bool] = Unassigned()
    checkpoint_config: Optional[CheckpointConfig] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class HyperParameterTuningJobWarmStartConfig(Base):
    """TBA"""
    parent_hyper_parameter_tuning_jobs: list
    warm_start_type: str


@dataclass
class InferenceComponentContainerSpecification(Base):
    """TBA"""
    image: Optional[str] = Unassigned()
    artifact_url: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class InferenceComponentStartupParameters(Base):
    """TBA"""
    model_data_download_timeout_in_seconds: Optional[int] = Unassigned()
    container_startup_health_check_timeout_in_seconds: Optional[int] = Unassigned()


@dataclass
class InferenceComponentComputeResourceRequirements(Base):
    """TBA"""
    min_memory_required_in_mb: int
    number_of_cpu_cores_required: Optional[float] = Unassigned()
    number_of_accelerator_devices_required: Optional[float] = Unassigned()
    max_memory_required_in_mb: Optional[int] = Unassigned()


@dataclass
class InferenceComponentSpecification(Base):
    """TBA"""
    compute_resource_requirements: InferenceComponentComputeResourceRequirements
    model_name: Optional[str] = Unassigned()
    container: Optional[InferenceComponentContainerSpecification] = Unassigned()
    startup_parameters: Optional[InferenceComponentStartupParameters] = Unassigned()


@dataclass
class InferenceComponentRuntimeConfig(Base):
    """TBA"""
    copy_count: int


@dataclass
class CreateInferenceComponentInput(Base):
    """TBA"""
    inference_component_name: str
    endpoint_name: str
    variant_name: str
    specification: InferenceComponentSpecification
    runtime_config: InferenceComponentRuntimeConfig
    tags: Optional[list] = Unassigned()


@dataclass
class CreateInferenceComponentOutput(Base):
    """TBA"""
    inference_component_arn: str


@dataclass
class InferenceExperimentSchedule(Base):
    """TBA"""
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class InferenceExperimentDataStorageConfig(Base):
    """TBA"""
    destination: str
    kms_key: Optional[str] = Unassigned()
    content_type: Optional[CaptureContentTypeHeader] = Unassigned()


@dataclass
class ShadowModeConfig(Base):
    """TBA"""
    source_model_variant_name: str
    shadow_model_variants: list


@dataclass
class Stairs(Base):
    """TBA"""
    duration_in_seconds: Optional[int] = Unassigned()
    number_of_steps: Optional[int] = Unassigned()
    users_per_step: Optional[int] = Unassigned()


@dataclass
class TrafficPattern(Base):
    """TBA"""
    traffic_type: Optional[str] = Unassigned()
    phases: Optional[list] = Unassigned()
    stairs: Optional[Stairs] = Unassigned()


@dataclass
class RecommendationJobResourceLimit(Base):
    """TBA"""
    max_number_of_tests: Optional[int] = Unassigned()
    max_parallel_of_tests: Optional[int] = Unassigned()


@dataclass
class RecommendationJobPayloadConfig(Base):
    """TBA"""
    sample_payload_url: Optional[str] = Unassigned()
    supported_content_types: Optional[list] = Unassigned()


@dataclass
class RecommendationJobContainerConfig(Base):
    """TBA"""
    domain: Optional[str] = Unassigned()
    task: Optional[str] = Unassigned()
    framework: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()
    payload_config: Optional[RecommendationJobPayloadConfig] = Unassigned()
    nearest_model_name: Optional[str] = Unassigned()
    supported_instance_types: Optional[list] = Unassigned()
    supported_endpoint_type: Optional[str] = Unassigned()
    data_input_config: Optional[str] = Unassigned()
    supported_response_m_i_m_e_types: Optional[list] = Unassigned()


@dataclass
class RecommendationJobVpcConfig(Base):
    """TBA"""
    security_group_ids: list
    subnets: list


@dataclass
class RecommendationJobInputConfig(Base):
    """TBA"""
    model_package_version_arn: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    job_duration_in_seconds: Optional[int] = Unassigned()
    traffic_pattern: Optional[TrafficPattern] = Unassigned()
    resource_limit: Optional[RecommendationJobResourceLimit] = Unassigned()
    endpoint_configurations: Optional[list] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    container_config: Optional[RecommendationJobContainerConfig] = Unassigned()
    endpoints: Optional[list] = Unassigned()
    vpc_config: Optional[RecommendationJobVpcConfig] = Unassigned()


@dataclass
class RecommendationJobStoppingConditions(Base):
    """TBA"""
    max_invocations: Optional[int] = Unassigned()
    model_latency_thresholds: Optional[list] = Unassigned()
    flat_invocations: Optional[str] = Unassigned()


@dataclass
class RecommendationJobCompiledOutputConfig(Base):
    """TBA"""
    s3_output_uri: Optional[str] = Unassigned()


@dataclass
class RecommendationJobOutputConfig(Base):
    """TBA"""
    kms_key_id: Optional[str] = Unassigned()
    compiled_output_config: Optional[RecommendationJobCompiledOutputConfig] = Unassigned()


@dataclass
class LabelingJobS3DataSource(Base):
    """TBA"""
    manifest_s3_uri: str


@dataclass
class LabelingJobSnsDataSource(Base):
    """TBA"""
    sns_topic_arn: str


@dataclass
class LabelingJobDataSource(Base):
    """TBA"""
    s3_data_source: Optional[LabelingJobS3DataSource] = Unassigned()
    sns_data_source: Optional[LabelingJobSnsDataSource] = Unassigned()


@dataclass
class LabelingJobDataAttributes(Base):
    """TBA"""
    content_classifiers: Optional[list] = Unassigned()


@dataclass
class LabelingJobInputConfig(Base):
    """TBA"""
    data_source: LabelingJobDataSource
    data_attributes: Optional[LabelingJobDataAttributes] = Unassigned()


@dataclass
class LabelingJobOutputConfig(Base):
    """TBA"""
    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()
    sns_topic_arn: Optional[str] = Unassigned()


@dataclass
class LabelingJobStoppingConditions(Base):
    """TBA"""
    max_human_labeled_object_count: Optional[int] = Unassigned()
    max_percentage_of_input_dataset_labeled: Optional[int] = Unassigned()


@dataclass
class LabelingJobResourceConfig(Base):
    """TBA"""
    volume_kms_key_id: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


@dataclass
class LabelingJobAlgorithmsConfig(Base):
    """TBA"""
    labeling_job_algorithm_specification_arn: str
    initial_active_learning_model_arn: Optional[str] = Unassigned()
    labeling_job_resource_config: Optional[LabelingJobResourceConfig] = Unassigned()


@dataclass
class UiConfig(Base):
    """TBA"""
    ui_template_s3_uri: Optional[str] = Unassigned()
    human_task_ui_arn: Optional[str] = Unassigned()


@dataclass
class HumanTaskConfig(Base):
    """TBA"""
    workteam_arn: str
    ui_config: UiConfig
    pre_human_task_lambda_arn: str
    task_title: str
    task_description: str
    number_of_human_workers_per_data_object: int
    task_time_limit_in_seconds: int
    annotation_consolidation_config: AnnotationConsolidationConfig
    task_keywords: Optional[list] = Unassigned()
    task_availability_lifetime_in_seconds: Optional[int] = Unassigned()
    max_concurrent_task_count: Optional[int] = Unassigned()
    public_workforce_task_price: Optional[PublicWorkforceTaskPrice] = Unassigned()


@dataclass
class ModelBiasBaselineConfig(Base):
    """TBA"""
    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


@dataclass
class ModelBiasAppSpecification(Base):
    """TBA"""
    image_uri: str
    config_uri: str
    environment: Optional[dict] = Unassigned()


@dataclass
class MonitoringGroundTruthS3Input(Base):
    """TBA"""
    s3_uri: Optional[str] = Unassigned()


@dataclass
class ModelBiasJobInput(Base):
    """TBA"""
    ground_truth_s3_input: MonitoringGroundTruthS3Input
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class ModelCardExportOutputConfig(Base):
    """TBA"""
    s3_output_path: str


@dataclass
class ModelCardSecurityConfig(Base):
    """TBA"""
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class ModelExplainabilityBaselineConfig(Base):
    """TBA"""
    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


@dataclass
class ModelExplainabilityAppSpecification(Base):
    """TBA"""
    image_uri: str
    config_uri: str
    environment: Optional[dict] = Unassigned()


@dataclass
class ModelExplainabilityJobInput(Base):
    """TBA"""
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class InferenceExecutionConfig(Base):
    """TBA"""
    mode: str


@dataclass
class CreateModelInput(Base):
    """TBA"""
    model_name: str
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[list] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()


@dataclass
class CreateModelOutput(Base):
    """TBA"""
    model_arn: str


@dataclass
class CreateModelPackageGroupInput(Base):
    """TBA"""
    model_package_group_name: str
    model_package_group_description: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class CreateModelPackageGroupOutput(Base):
    """TBA"""
    model_package_group_arn: str


@dataclass
class ModelPackageValidationSpecification(Base):
    """TBA"""
    validation_role: str
    validation_profiles: list


@dataclass
class SourceAlgorithmSpecification(Base):
    """TBA"""
    source_algorithms: list


@dataclass
class ModelQuality(Base):
    """TBA"""
    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


@dataclass
class ModelDataQuality(Base):
    """TBA"""
    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


@dataclass
class Explainability(Base):
    """TBA"""
    report: Optional[MetricsSource] = Unassigned()


@dataclass
class ModelMetrics(Base):
    """TBA"""
    model_quality: Optional[ModelQuality] = Unassigned()
    model_data_quality: Optional[ModelDataQuality] = Unassigned()
    bias: Optional[Bias] = Unassigned()
    explainability: Optional[Explainability] = Unassigned()


@dataclass
class FileSource(Base):
    """TBA"""
    s3_uri: str
    content_type: Optional[str] = Unassigned()
    content_digest: Optional[str] = Unassigned()


@dataclass
class DriftCheckBias(Base):
    """TBA"""
    config_file: Optional[FileSource] = Unassigned()
    pre_training_constraints: Optional[MetricsSource] = Unassigned()
    post_training_constraints: Optional[MetricsSource] = Unassigned()


@dataclass
class DriftCheckExplainability(Base):
    """TBA"""
    constraints: Optional[MetricsSource] = Unassigned()
    config_file: Optional[FileSource] = Unassigned()


@dataclass
class DriftCheckModelQuality(Base):
    """TBA"""
    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


@dataclass
class DriftCheckModelDataQuality(Base):
    """TBA"""
    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


@dataclass
class DriftCheckBaselines(Base):
    """TBA"""
    bias: Optional[DriftCheckBias] = Unassigned()
    explainability: Optional[DriftCheckExplainability] = Unassigned()
    model_quality: Optional[DriftCheckModelQuality] = Unassigned()
    model_data_quality: Optional[DriftCheckModelDataQuality] = Unassigned()


@dataclass
class CreateModelPackageInput(Base):
    """TBA"""
    model_package_name: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    validation_specification: Optional[ModelPackageValidationSpecification] = Unassigned()
    source_algorithm_specification: Optional[SourceAlgorithmSpecification] = Unassigned()
    certify_for_marketplace: Optional[bool] = Unassigned()
    tags: Optional[list] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    model_metrics: Optional[ModelMetrics] = Unassigned()
    client_token: Optional[str] = Unassigned()
    domain: Optional[str] = Unassigned()
    task: Optional[str] = Unassigned()
    sample_payload_url: Optional[str] = Unassigned()
    customer_metadata_properties: Optional[dict] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    additional_inference_specifications: Optional[list] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()
    source_uri: Optional[str] = Unassigned()


@dataclass
class CreateModelPackageOutput(Base):
    """TBA"""
    model_package_arn: str


@dataclass
class ModelQualityBaselineConfig(Base):
    """TBA"""
    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


@dataclass
class ModelQualityAppSpecification(Base):
    """TBA"""
    image_uri: str
    container_entrypoint: Optional[list] = Unassigned()
    container_arguments: Optional[list] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class ModelQualityJobInput(Base):
    """TBA"""
    ground_truth_s3_input: MonitoringGroundTruthS3Input
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class ScheduleConfig(Base):
    """TBA"""
    schedule_expression: str
    data_analysis_start_time: Optional[str] = Unassigned()
    data_analysis_end_time: Optional[str] = Unassigned()


@dataclass
class MonitoringBaselineConfig(Base):
    """TBA"""
    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()
    statistics_resource: Optional[MonitoringStatisticsResource] = Unassigned()


@dataclass
class MonitoringAppSpecification(Base):
    """TBA"""
    image_uri: str
    container_entrypoint: Optional[list] = Unassigned()
    container_arguments: Optional[list] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()


@dataclass
class NetworkConfig(Base):
    """TBA"""
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


@dataclass
class MonitoringJobDefinition(Base):
    """TBA"""
    monitoring_inputs: list
    monitoring_output_config: MonitoringOutputConfig
    monitoring_resources: MonitoringResources
    monitoring_app_specification: MonitoringAppSpecification
    role_arn: str
    baseline_config: Optional[MonitoringBaselineConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    environment: Optional[dict] = Unassigned()
    network_config: Optional[NetworkConfig] = Unassigned()


@dataclass
class MonitoringScheduleConfig(Base):
    """TBA"""
    schedule_config: Optional[ScheduleConfig] = Unassigned()
    monitoring_job_definition: Optional[MonitoringJobDefinition] = Unassigned()
    monitoring_job_definition_name: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()


@dataclass
class InstanceMetadataServiceConfiguration(Base):
    """TBA"""
    minimum_instance_metadata_service_version: str


@dataclass
class CreateNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str
    instance_type: str
    role_arn: str
    subnet_id: Optional[str] = Unassigned()
    security_group_ids: Optional[list] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()
    lifecycle_config_name: Optional[str] = Unassigned()
    direct_internet_access: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    accelerator_types: Optional[list] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[list] = Unassigned()
    root_access: Optional[str] = Unassigned()
    platform_identifier: Optional[str] = Unassigned()
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned()


@dataclass
class CreateNotebookInstanceLifecycleConfigInput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_name: str
    on_create: Optional[list] = Unassigned()
    on_start: Optional[list] = Unassigned()


@dataclass
class CreateNotebookInstanceLifecycleConfigOutput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()


@dataclass
class CreateNotebookInstanceOutput(Base):
    """TBA"""
    notebook_instance_arn: Optional[str] = Unassigned()


@dataclass
class PipelineDefinitionS3Location(Base):
    """TBA"""
    bucket: str
    object_key: str
    version_id: Optional[str] = Unassigned()


@dataclass
class ParallelismConfiguration(Base):
    """TBA"""
    max_parallel_execution_steps: int


@dataclass
class CreatePresignedNotebookInstanceUrlInput(Base):
    """TBA"""
    notebook_instance_name: str
    session_expiration_duration_in_seconds: Optional[int] = Unassigned()


@dataclass
class CreatePresignedNotebookInstanceUrlOutput(Base):
    """TBA"""
    authorized_url: Optional[str] = Unassigned()


@dataclass
class ProcessingOutputConfig(Base):
    """TBA"""
    outputs: list
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class ProcessingClusterConfig(Base):
    """TBA"""
    instance_count: int
    instance_type: str
    volume_size_in_g_b: int
    volume_kms_key_id: Optional[str] = Unassigned()


@dataclass
class ProcessingResources(Base):
    """TBA"""
    cluster_config: ProcessingClusterConfig


@dataclass
class ProcessingStoppingCondition(Base):
    """TBA"""
    max_runtime_in_seconds: int


@dataclass
class ExperimentConfig(Base):
    """TBA"""
    experiment_name: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()
    trial_component_display_name: Optional[str] = Unassigned()
    run_name: Optional[str] = Unassigned()


@dataclass
class ServiceCatalogProvisioningDetails(Base):
    """TBA"""
    product_id: str
    provisioning_artifact_id: Optional[str] = Unassigned()
    path_id: Optional[str] = Unassigned()
    provisioning_parameters: Optional[list] = Unassigned()


@dataclass
class CreateProjectInput(Base):
    """TBA"""
    project_name: str
    service_catalog_provisioning_details: ServiceCatalogProvisioningDetails
    project_description: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class CreateProjectOutput(Base):
    """TBA"""
    project_arn: str
    project_id: str


@dataclass
class SpaceCodeEditorAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()


@dataclass
class SpaceJupyterLabAppSettings(Base):
    """TBA"""
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    code_repositories: Optional[list] = Unassigned()


@dataclass
class EbsStorageSettings(Base):
    """TBA"""
    ebs_volume_size_in_gb: int


@dataclass
class SpaceStorageSettings(Base):
    """TBA"""
    ebs_storage_settings: Optional[EbsStorageSettings] = Unassigned()


@dataclass
class SpaceSettings(Base):
    """TBA"""
    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()
    code_editor_app_settings: Optional[SpaceCodeEditorAppSettings] = Unassigned()
    jupyter_lab_app_settings: Optional[SpaceJupyterLabAppSettings] = Unassigned()
    app_type: Optional[str] = Unassigned()
    space_storage_settings: Optional[SpaceStorageSettings] = Unassigned()
    custom_file_systems: Optional[list] = Unassigned()


@dataclass
class OwnershipSettings(Base):
    """TBA"""
    owner_user_profile_name: str


@dataclass
class SpaceSharingSettings(Base):
    """TBA"""
    sharing_type: str


@dataclass
class DebugHookConfig(Base):
    """TBA"""
    s3_output_path: str
    local_path: Optional[str] = Unassigned()
    hook_parameters: Optional[dict] = Unassigned()
    collection_configurations: Optional[list] = Unassigned()


@dataclass
class TensorBoardOutputConfig(Base):
    """TBA"""
    s3_output_path: str
    local_path: Optional[str] = Unassigned()


@dataclass
class ProfilerConfig(Base):
    """TBA"""
    s3_output_path: Optional[str] = Unassigned()
    profiling_interval_in_milliseconds: Optional[int] = Unassigned()
    profiling_parameters: Optional[dict] = Unassigned()
    disable_profiler: Optional[bool] = Unassigned()


@dataclass
class RemoteDebugConfig(Base):
    """TBA"""
    enable_remote_debug: Optional[bool] = Unassigned()


@dataclass
class InfraCheckConfig(Base):
    """TBA"""
    enable_infra_check: Optional[bool] = Unassigned()


@dataclass
class ModelClientConfig(Base):
    """TBA"""
    invocations_timeout_in_seconds: Optional[int] = Unassigned()
    invocations_max_retries: Optional[int] = Unassigned()


@dataclass
class DataProcessing(Base):
    """TBA"""
    input_filter: Optional[str] = Unassigned()
    output_filter: Optional[str] = Unassigned()
    join_source: Optional[str] = Unassigned()


@dataclass
class TrialComponentStatus(Base):
    """TBA"""
    primary_status: Optional[str] = Unassigned()
    message: Optional[str] = Unassigned()


@dataclass
class OidcConfig(Base):
    """TBA"""
    client_id: str
    client_secret: str
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    user_info_endpoint: str
    logout_endpoint: str
    jwks_uri: str


@dataclass
class SourceIpConfig(Base):
    """TBA"""
    cidrs: list


@dataclass
class WorkforceVpcConfigRequest(Base):
    """TBA"""
    vpc_id: Optional[str] = Unassigned()
    security_group_ids: Optional[list] = Unassigned()
    subnets: Optional[list] = Unassigned()


@dataclass
class NotificationConfiguration(Base):
    """TBA"""
    notification_topic_arn: Optional[str] = Unassigned()


@dataclass
class EFSFileSystem(Base):
    """TBA"""
    file_system_id: str


@dataclass
class CustomFileSystem(Base):
    """TBA"""
    e_f_s_file_system: Optional[EFSFileSystem] = Unassigned()


@dataclass
class EFSFileSystemConfig(Base):
    """TBA"""
    file_system_id: str
    file_system_path: Optional[str] = Unassigned()


@dataclass
class CustomFileSystemConfig(Base):
    """TBA"""
    e_f_s_file_system_config: Optional[EFSFileSystemConfig] = Unassigned()


@dataclass
class CustomImage(Base):
    """TBA"""
    image_name: str
    app_image_config_name: str
    image_version_number: Optional[int] = Unassigned()


@dataclass
class CustomizedMetricSpecification(Base):
    """TBA"""
    metric_name: Optional[str] = Unassigned()
    namespace: Optional[str] = Unassigned()
    statistic: Optional[str] = Unassigned()


@dataclass
class DataCaptureConfigSummary(Base):
    """TBA"""
    enable_capture: bool
    capture_status: str
    current_sampling_percentage: int
    destination_s3_uri: str
    kms_key_id: str


@dataclass
class RedshiftDatasetDefinition(Base):
    """TBA"""
    cluster_id: str
    database: str
    db_user: str
    query_string: str
    cluster_role_arn: str
    output_s3_uri: str
    output_format: str
    kms_key_id: Optional[str] = Unassigned()
    output_compression: Optional[str] = Unassigned()


@dataclass
class DatasetDefinition(Base):
    """TBA"""
    athena_dataset_definition: Optional[AthenaDatasetDefinition] = Unassigned()
    redshift_dataset_definition: Optional[RedshiftDatasetDefinition] = Unassigned()
    local_path: Optional[str] = Unassigned()
    data_distribution_type: Optional[str] = Unassigned()
    input_mode: Optional[str] = Unassigned()


@dataclass
class DebugRuleConfiguration(Base):
    """TBA"""
    rule_configuration_name: str
    rule_evaluator_image: str
    local_path: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    rule_parameters: Optional[dict] = Unassigned()


@dataclass
class DebugRuleEvaluationStatus(Base):
    """TBA"""
    rule_configuration_name: Optional[str] = Unassigned()
    rule_evaluation_job_arn: Optional[str] = Unassigned()
    rule_evaluation_status: Optional[str] = Unassigned()
    status_details: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DeleteAlgorithmInput(Base):
    """TBA"""
    algorithm_name: str


@dataclass
class DeleteCodeRepositoryInput(Base):
    """TBA"""
    code_repository_name: str


@dataclass
class RetentionPolicy(Base):
    """TBA"""
    home_efs_file_system: Optional[str] = Unassigned()


@dataclass
class DeleteEndpointConfigInput(Base):
    """TBA"""
    endpoint_config_name: str


@dataclass
class DeleteEndpointInput(Base):
    """TBA"""
    endpoint_name: str


@dataclass
class DeleteInferenceComponentInput(Base):
    """TBA"""
    inference_component_name: str


@dataclass
class DeleteModelInput(Base):
    """TBA"""
    model_name: str


@dataclass
class DeleteModelPackageGroupInput(Base):
    """TBA"""
    model_package_group_name: str


@dataclass
class DeleteModelPackageGroupPolicyInput(Base):
    """TBA"""
    model_package_group_name: str


@dataclass
class DeleteModelPackageInput(Base):
    """TBA"""
    model_package_name: str


@dataclass
class DeleteNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str


@dataclass
class DeleteNotebookInstanceLifecycleConfigInput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_name: str


@dataclass
class DeleteProjectInput(Base):
    """TBA"""
    project_name: str


@dataclass
class DeleteTagsInput(Base):
    """TBA"""
    resource_arn: str
    tag_keys: list


@dataclass
class DeployedImage(Base):
    """TBA"""
    specified_image: Optional[str] = Unassigned()
    resolved_image: Optional[str] = Unassigned()
    resolution_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DeploymentRecommendation(Base):
    """TBA"""
    recommendation_status: str
    real_time_inference_recommendations: Optional[list] = Unassigned()


@dataclass
class DeviceSelectionConfig(Base):
    """TBA"""
    device_subset_type: str
    percentage: Optional[int] = Unassigned()
    device_names: Optional[list] = Unassigned()
    device_name_contains: Optional[str] = Unassigned()


@dataclass
class EdgeDeploymentConfig(Base):
    """TBA"""
    failure_handling_policy: str


@dataclass
class DeploymentStage(Base):
    """TBA"""
    stage_name: str
    device_selection_config: DeviceSelectionConfig
    deployment_config: Optional[EdgeDeploymentConfig] = Unassigned()


@dataclass
class EdgeDeploymentStatus(Base):
    """TBA"""
    stage_status: str
    edge_deployment_success_in_stage: int
    edge_deployment_pending_in_stage: int
    edge_deployment_failed_in_stage: int
    edge_deployment_status_message: Optional[str] = Unassigned()
    edge_deployment_stage_start_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DeploymentStageStatusSummary(Base):
    """TBA"""
    stage_name: str
    device_selection_config: DeviceSelectionConfig
    deployment_config: EdgeDeploymentConfig
    deployment_status: EdgeDeploymentStatus


@dataclass
class DerivedInformation(Base):
    """TBA"""
    derived_data_input_config: Optional[str] = Unassigned()


@dataclass
class DescribeAlgorithmInput(Base):
    """TBA"""
    algorithm_name: str


@dataclass
class DescribeAlgorithmOutput(Base):
    """TBA"""
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


@dataclass
class ResolvedAttributes(Base):
    """TBA"""
    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


@dataclass
class ModelDeployResult(Base):
    """TBA"""
    endpoint_name: Optional[str] = Unassigned()


@dataclass
class DescribeCodeRepositoryInput(Base):
    """TBA"""
    code_repository_name: str


@dataclass
class DescribeCodeRepositoryOutput(Base):
    """TBA"""
    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()


@dataclass
class ModelArtifacts(Base):
    """TBA"""
    s3_model_artifacts: str


@dataclass
class ModelDigests(Base):
    """TBA"""
    artifact_digest: Optional[str] = Unassigned()


@dataclass
class EdgePresetDeploymentOutput(Base):
    """TBA"""
    type: str
    artifact: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    status_message: Optional[str] = Unassigned()


@dataclass
class DescribeEndpointConfigInput(Base):
    """TBA"""
    endpoint_config_name: str


@dataclass
class DescribeEndpointConfigOutput(Base):
    """TBA"""
    endpoint_config_name: str
    endpoint_config_arn: str
    production_variants: list
    creation_time: datetime.datetime
    data_capture_config: Optional[DataCaptureConfig] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[list] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()


@dataclass
class DescribeEndpointInput(Base):
    """TBA"""
    endpoint_name: str


@dataclass
class PendingDeploymentSummary(Base):
    """TBA"""
    endpoint_config_name: str
    production_variants: Optional[list] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    shadow_production_variants: Optional[list] = Unassigned()


@dataclass
class DescribeEndpointOutput(Base):
    """TBA"""
    endpoint_name: str
    endpoint_arn: str
    endpoint_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_config_name: Optional[str] = Unassigned()
    production_variants: Optional[list] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    last_deployment_config: Optional[DeploymentConfig] = Unassigned()
    async_inference_config: Optional[AsyncInferenceConfig] = Unassigned()
    pending_deployment_summary: Optional[PendingDeploymentSummary] = Unassigned()
    explainer_config: Optional[ExplainerConfig] = Unassigned()
    shadow_production_variants: Optional[list] = Unassigned()


@dataclass
class ExperimentSource(Base):
    """TBA"""
    source_arn: str
    source_type: Optional[str] = Unassigned()


@dataclass
class ThroughputConfigDescription(Base):
    """TBA"""
    throughput_mode: str
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


@dataclass
class OfflineStoreStatus(Base):
    """TBA"""
    status: str
    blocked_reason: Optional[str] = Unassigned()


@dataclass
class LastUpdateStatus(Base):
    """TBA"""
    status: str
    failure_reason: Optional[str] = Unassigned()


@dataclass
class UiTemplateInfo(Base):
    """TBA"""
    url: Optional[str] = Unassigned()
    content_sha256: Optional[str] = Unassigned()


@dataclass
class TrainingJobStatusCounters(Base):
    """TBA"""
    completed: Optional[int] = Unassigned()
    in_progress: Optional[int] = Unassigned()
    retryable_error: Optional[int] = Unassigned()
    non_retryable_error: Optional[int] = Unassigned()
    stopped: Optional[int] = Unassigned()


@dataclass
class ObjectiveStatusCounters(Base):
    """TBA"""
    succeeded: Optional[int] = Unassigned()
    pending: Optional[int] = Unassigned()
    failed: Optional[int] = Unassigned()


@dataclass
class FinalHyperParameterTuningJobObjectiveMetric(Base):
    """TBA"""
    metric_name: str
    value: float
    type: Optional[str] = Unassigned()


@dataclass
class HyperParameterTrainingJobSummary(Base):
    """TBA"""
    training_job_name: str
    training_job_arn: str
    creation_time: datetime.datetime
    training_job_status: str
    tuned_hyper_parameters: dict
    training_job_definition_name: Optional[str] = Unassigned()
    tuning_job_name: Optional[str] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    final_hyper_parameter_tuning_job_objective_metric: Optional[FinalHyperParameterTuningJobObjectiveMetric] = Unassigned()
    objective_status: Optional[str] = Unassigned()


@dataclass
class HyperParameterTuningJobCompletionDetails(Base):
    """TBA"""
    number_of_training_jobs_objective_not_improving: Optional[int] = Unassigned()
    convergence_detected_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class HyperParameterTuningJobConsumedResources(Base):
    """TBA"""
    runtime_in_seconds: Optional[int] = Unassigned()


@dataclass
class DescribeInferenceComponentInput(Base):
    """TBA"""
    inference_component_name: str


@dataclass
class InferenceComponentContainerSpecificationSummary(Base):
    """TBA"""
    deployed_image: Optional[DeployedImage] = Unassigned()
    artifact_url: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()


@dataclass
class InferenceComponentSpecificationSummary(Base):
    """TBA"""
    model_name: Optional[str] = Unassigned()
    container: Optional[InferenceComponentContainerSpecificationSummary] = Unassigned()
    startup_parameters: Optional[InferenceComponentStartupParameters] = Unassigned()
    compute_resource_requirements: Optional[InferenceComponentComputeResourceRequirements] = Unassigned()


@dataclass
class InferenceComponentRuntimeConfigSummary(Base):
    """TBA"""
    desired_copy_count: Optional[int] = Unassigned()
    current_copy_count: Optional[int] = Unassigned()


@dataclass
class DescribeInferenceComponentOutput(Base):
    """TBA"""
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


@dataclass
class EndpointMetadata(Base):
    """TBA"""
    endpoint_name: str
    endpoint_config_name: Optional[str] = Unassigned()
    endpoint_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


@dataclass
class LabelCounters(Base):
    """TBA"""
    total_labeled: Optional[int] = Unassigned()
    human_labeled: Optional[int] = Unassigned()
    machine_labeled: Optional[int] = Unassigned()
    failed_non_retryable_error: Optional[int] = Unassigned()
    unlabeled: Optional[int] = Unassigned()


@dataclass
class LabelingJobOutput(Base):
    """TBA"""
    output_dataset_s3_uri: str
    final_active_learning_model_arn: Optional[str] = Unassigned()


@dataclass
class ModelCardExportArtifacts(Base):
    """TBA"""
    s3_export_artifacts: str


@dataclass
class DescribeModelInput(Base):
    """TBA"""
    model_name: str


@dataclass
class DescribeModelOutput(Base):
    """TBA"""
    model_name: str
    creation_time: datetime.datetime
    model_arn: str
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[list] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()


@dataclass
class DescribeModelPackageGroupInput(Base):
    """TBA"""
    model_package_group_name: str


@dataclass
class DescribeModelPackageGroupOutput(Base):
    """TBA"""
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    created_by: UserContext
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()


@dataclass
class DescribeModelPackageInput(Base):
    """TBA"""
    model_package_name: str


@dataclass
class ModelPackageStatusDetails(Base):
    """TBA"""
    validation_statuses: list
    image_scan_statuses: Optional[list] = Unassigned()


@dataclass
class DescribeModelPackageOutput(Base):
    """TBA"""
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
    customer_metadata_properties: Optional[dict] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    additional_inference_specifications: Optional[list] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()
    source_uri: Optional[str] = Unassigned()


@dataclass
class MonitoringExecutionSummary(Base):
    """TBA"""
    monitoring_schedule_name: str
    scheduled_time: datetime.datetime
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    monitoring_execution_status: str
    processing_job_arn: Optional[str] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    monitoring_job_definition_name: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()


@dataclass
class DescribeNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str


@dataclass
class DescribeNotebookInstanceLifecycleConfigInput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_name: str


@dataclass
class DescribeNotebookInstanceLifecycleConfigOutput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_arn: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    on_create: Optional[list] = Unassigned()
    on_start: Optional[list] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DescribeNotebookInstanceOutput(Base):
    """TBA"""
    notebook_instance_arn: Optional[str] = Unassigned()
    notebook_instance_name: Optional[str] = Unassigned()
    notebook_instance_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    subnet_id: Optional[str] = Unassigned()
    security_groups: Optional[list] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    network_interface_id: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    direct_internet_access: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    accelerator_types: Optional[list] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[list] = Unassigned()
    root_access: Optional[str] = Unassigned()
    platform_identifier: Optional[str] = Unassigned()
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned()


@dataclass
class PipelineExperimentConfig(Base):
    """TBA"""
    experiment_name: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()


@dataclass
class SelectiveExecutionConfig(Base):
    """TBA"""
    selected_steps: list
    source_pipeline_execution_arn: Optional[str] = Unassigned()


@dataclass
class DescribeProjectInput(Base):
    """TBA"""
    project_name: str


@dataclass
class ServiceCatalogProvisionedProductDetails(Base):
    """TBA"""
    provisioned_product_id: Optional[str] = Unassigned()
    provisioned_product_status_message: Optional[str] = Unassigned()


@dataclass
class DescribeProjectOutput(Base):
    """TBA"""
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


@dataclass
class SubscribedWorkteam(Base):
    """TBA"""
    workteam_arn: str
    marketplace_title: Optional[str] = Unassigned()
    seller_name: Optional[str] = Unassigned()
    marketplace_description: Optional[str] = Unassigned()
    listing_id: Optional[str] = Unassigned()


@dataclass
class WarmPoolStatus(Base):
    """TBA"""
    status: str
    resource_retained_billable_time_in_seconds: Optional[int] = Unassigned()
    reused_by_job: Optional[str] = Unassigned()


@dataclass
class TrialComponentSource(Base):
    """TBA"""
    source_arn: str
    source_type: Optional[str] = Unassigned()


@dataclass
class TrialSource(Base):
    """TBA"""
    source_arn: str
    source_type: Optional[str] = Unassigned()


@dataclass
class OidcConfigForResponse(Base):
    """TBA"""
    client_id: Optional[str] = Unassigned()
    issuer: Optional[str] = Unassigned()
    authorization_endpoint: Optional[str] = Unassigned()
    token_endpoint: Optional[str] = Unassigned()
    user_info_endpoint: Optional[str] = Unassigned()
    logout_endpoint: Optional[str] = Unassigned()
    jwks_uri: Optional[str] = Unassigned()


@dataclass
class WorkforceVpcConfigResponse(Base):
    """TBA"""
    vpc_id: str
    security_group_ids: list
    subnets: list
    vpc_endpoint_id: Optional[str] = Unassigned()


@dataclass
class Workforce(Base):
    """TBA"""
    workforce_name: str
    workforce_arn: str
    last_updated_date: Optional[datetime.datetime] = Unassigned()
    source_ip_config: Optional[SourceIpConfig] = Unassigned()
    sub_domain: Optional[str] = Unassigned()
    cognito_config: Optional[CognitoConfig] = Unassigned()
    oidc_config: Optional[OidcConfigForResponse] = Unassigned()
    create_date: Optional[datetime.datetime] = Unassigned()
    workforce_vpc_config: Optional[WorkforceVpcConfigResponse] = Unassigned()
    status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


@dataclass
class Workteam(Base):
    """TBA"""
    workteam_name: str
    member_definitions: list
    workteam_arn: str
    description: str
    workforce_arn: Optional[str] = Unassigned()
    product_listing_ids: Optional[list] = Unassigned()
    sub_domain: Optional[str] = Unassigned()
    create_date: Optional[datetime.datetime] = Unassigned()
    last_updated_date: Optional[datetime.datetime] = Unassigned()
    notification_configuration: Optional[NotificationConfiguration] = Unassigned()


@dataclass
class ProductionVariantServerlessUpdateConfig(Base):
    """TBA"""
    max_concurrency: Optional[int] = Unassigned()
    provisioned_concurrency: Optional[int] = Unassigned()


@dataclass
class DesiredWeightAndCapacity(Base):
    """TBA"""
    variant_name: str
    desired_weight: Optional[float] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    serverless_update_config: Optional[ProductionVariantServerlessUpdateConfig] = Unassigned()


@dataclass
class Device(Base):
    """TBA"""
    device_name: str
    description: Optional[str] = Unassigned()
    iot_thing_name: Optional[str] = Unassigned()


@dataclass
class DeviceDeploymentSummary(Base):
    """TBA"""
    edge_deployment_plan_arn: str
    edge_deployment_plan_name: str
    stage_name: str
    device_name: str
    device_arn: str
    deployed_stage_name: Optional[str] = Unassigned()
    device_fleet_name: Optional[str] = Unassigned()
    device_deployment_status: Optional[str] = Unassigned()
    device_deployment_status_message: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    deployment_start_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DeviceFleetSummary(Base):
    """TBA"""
    device_fleet_arn: str
    device_fleet_name: str
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class DeviceStats(Base):
    """TBA"""
    connected_device_count: int
    registered_device_count: int


@dataclass
class DeviceSummary(Base):
    """TBA"""
    device_name: str
    device_arn: str
    description: Optional[str] = Unassigned()
    device_fleet_name: Optional[str] = Unassigned()
    iot_thing_name: Optional[str] = Unassigned()
    registration_time: Optional[datetime.datetime] = Unassigned()
    latest_heartbeat: Optional[datetime.datetime] = Unassigned()
    models: Optional[list] = Unassigned()
    agent_version: Optional[str] = Unassigned()


@dataclass
class DomainDetails(Base):
    """TBA"""
    domain_arn: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    domain_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    url: Optional[str] = Unassigned()


@dataclass
class RStudioServerProDomainSettingsForUpdate(Base):
    """TBA"""
    domain_execution_role_arn: str
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    r_studio_connect_url: Optional[str] = Unassigned()
    r_studio_package_manager_url: Optional[str] = Unassigned()


@dataclass
class DomainSettingsForUpdate(Base):
    """TBA"""
    r_studio_server_pro_domain_settings_for_update: Optional[RStudioServerProDomainSettingsForUpdate] = Unassigned()
    execution_role_identity_config: Optional[str] = Unassigned()
    security_group_ids: Optional[list] = Unassigned()
    docker_settings: Optional[DockerSettings] = Unassigned()


@dataclass
class DynamicScalingConfiguration(Base):
    """TBA"""
    min_capacity: Optional[int] = Unassigned()
    max_capacity: Optional[int] = Unassigned()
    scale_in_cooldown: Optional[int] = Unassigned()
    scale_out_cooldown: Optional[int] = Unassigned()
    scaling_policies: Optional[list] = Unassigned()


@dataclass
class EMRStepMetadata(Base):
    """TBA"""
    cluster_id: Optional[str] = Unassigned()
    step_id: Optional[str] = Unassigned()
    step_name: Optional[str] = Unassigned()
    log_file_path: Optional[str] = Unassigned()


@dataclass
class Edge(Base):
    """TBA"""
    source_arn: Optional[str] = Unassigned()
    destination_arn: Optional[str] = Unassigned()
    association_type: Optional[str] = Unassigned()


@dataclass
class EdgeDeploymentModelConfig(Base):
    """TBA"""
    model_handle: str
    edge_packaging_job_name: str


@dataclass
class EdgeDeploymentPlanSummary(Base):
    """TBA"""
    edge_deployment_plan_arn: str
    edge_deployment_plan_name: str
    device_fleet_name: str
    edge_deployment_success: int
    edge_deployment_pending: int
    edge_deployment_failed: int
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class EdgeModel(Base):
    """TBA"""
    model_name: str
    model_version: str
    latest_sample_time: Optional[datetime.datetime] = Unassigned()
    latest_inference: Optional[datetime.datetime] = Unassigned()


@dataclass
class EdgeModelStat(Base):
    """TBA"""
    model_name: str
    model_version: str
    offline_device_count: int
    connected_device_count: int
    active_device_count: int
    sampling_device_count: int


@dataclass
class EdgeModelSummary(Base):
    """TBA"""
    model_name: str
    model_version: str


@dataclass
class EdgePackagingJobSummary(Base):
    """TBA"""
    edge_packaging_job_arn: str
    edge_packaging_job_name: str
    edge_packaging_job_status: str
    compilation_job_name: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    model_version: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class Endpoint(Base):
    """TBA"""
    endpoint_name: str
    endpoint_arn: str
    endpoint_config_name: str
    endpoint_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    production_variants: Optional[list] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    monitoring_schedules: Optional[list] = Unassigned()
    tags: Optional[list] = Unassigned()
    shadow_production_variants: Optional[list] = Unassigned()


@dataclass
class EndpointConfigSummary(Base):
    """TBA"""
    endpoint_config_name: str
    endpoint_config_arn: str
    creation_time: datetime.datetime


@dataclass
class EndpointInfo(Base):
    """TBA"""
    endpoint_name: Optional[str] = Unassigned()


@dataclass
class ProductionVariantServerlessConfig(Base):
    """TBA"""
    memory_size_in_m_b: int
    max_concurrency: int
    provisioned_concurrency: Optional[int] = Unassigned()


@dataclass
class EnvironmentParameterRanges(Base):
    """TBA"""
    categorical_parameter_ranges: Optional[list] = Unassigned()


@dataclass
class EndpointInputConfiguration(Base):
    """TBA"""
    instance_type: Optional[str] = Unassigned()
    serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    inference_specification_name: Optional[str] = Unassigned()
    environment_parameter_ranges: Optional[EnvironmentParameterRanges] = Unassigned()


@dataclass
class EndpointOutputConfiguration(Base):
    """TBA"""
    endpoint_name: str
    variant_name: str
    instance_type: Optional[str] = Unassigned()
    initial_instance_count: Optional[int] = Unassigned()
    serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()


@dataclass
class InferenceMetrics(Base):
    """TBA"""
    max_invocations: int
    model_latency: int


@dataclass
class EndpointPerformance(Base):
    """TBA"""
    metrics: InferenceMetrics
    endpoint_info: EndpointInfo


@dataclass
class EndpointSummary(Base):
    """TBA"""
    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_status: str


@dataclass
class EnvironmentParameter(Base):
    """TBA"""
    key: str
    value_type: str
    value: str


@dataclass
class Experiment(Base):
    """TBA"""
    experiment_name: Optional[str] = Unassigned()
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class ExperimentSummary(Base):
    """TBA"""
    experiment_arn: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_source: Optional[ExperimentSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class FailStepMetadata(Base):
    """TBA"""
    error_message: Optional[str] = Unassigned()


@dataclass
class FeatureDefinition(Base):
    """TBA"""
    feature_name: str
    feature_type: str
    collection_type: Optional[str] = Unassigned()
    collection_config: Optional[CollectionConfig] = Unassigned()


@dataclass
class FeatureGroup(Base):
    """TBA"""
    feature_group_arn: Optional[str] = Unassigned()
    feature_group_name: Optional[str] = Unassigned()
    record_identifier_feature_name: Optional[str] = Unassigned()
    event_time_feature_name: Optional[str] = Unassigned()
    feature_definitions: Optional[list] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    online_store_config: Optional[OnlineStoreConfig] = Unassigned()
    offline_store_config: Optional[OfflineStoreConfig] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    feature_group_status: Optional[str] = Unassigned()
    offline_store_status: Optional[OfflineStoreStatus] = Unassigned()
    last_update_status: Optional[LastUpdateStatus] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class FeatureGroupSummary(Base):
    """TBA"""
    feature_group_name: str
    feature_group_arn: str
    creation_time: datetime.datetime
    feature_group_status: Optional[str] = Unassigned()
    offline_store_status: Optional[OfflineStoreStatus] = Unassigned()


@dataclass
class FeatureMetadata(Base):
    """TBA"""
    feature_group_arn: Optional[str] = Unassigned()
    feature_group_name: Optional[str] = Unassigned()
    feature_name: Optional[str] = Unassigned()
    feature_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    parameters: Optional[list] = Unassigned()


@dataclass
class FeatureParameter(Base):
    """TBA"""
    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


@dataclass
class Filter(Base):
    """TBA"""
    name: str
    operator: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


@dataclass
class FlowDefinitionSummary(Base):
    """TBA"""
    flow_definition_name: str
    flow_definition_arn: str
    flow_definition_status: str
    creation_time: datetime.datetime
    failure_reason: Optional[str] = Unassigned()


@dataclass
class GetModelPackageGroupPolicyInput(Base):
    """TBA"""
    model_package_group_name: str


@dataclass
class GetModelPackageGroupPolicyOutput(Base):
    """TBA"""
    resource_policy: str


@dataclass
class GetSagemakerServicecatalogPortfolioStatusOutput(Base):
    """TBA"""
    status: Optional[str] = Unassigned()


@dataclass
class ScalingPolicyObjective(Base):
    """TBA"""
    min_invocations_per_minute: Optional[int] = Unassigned()
    max_invocations_per_minute: Optional[int] = Unassigned()


@dataclass
class ScalingPolicyMetric(Base):
    """TBA"""
    invocations_per_instance: Optional[int] = Unassigned()
    model_latency: Optional[int] = Unassigned()


@dataclass
class PropertyNameQuery(Base):
    """TBA"""
    property_name_hint: str


@dataclass
class SuggestionQuery(Base):
    """TBA"""
    property_name_query: Optional[PropertyNameQuery] = Unassigned()


@dataclass
class GitConfigForUpdate(Base):
    """TBA"""
    secret_arn: Optional[str] = Unassigned()


@dataclass
class HolidayConfigAttributes(Base):
    """TBA"""
    country_code: Optional[str] = Unassigned()


@dataclass
class HubContentDependency(Base):
    """TBA"""
    dependency_origin_path: Optional[str] = Unassigned()
    dependency_copy_path: Optional[str] = Unassigned()


@dataclass
class HubContentInfo(Base):
    """TBA"""
    hub_content_name: str
    hub_content_arn: str
    hub_content_version: str
    hub_content_type: str
    document_schema_version: str
    hub_content_status: str
    creation_time: datetime.datetime
    hub_content_display_name: Optional[str] = Unassigned()
    hub_content_description: Optional[str] = Unassigned()
    hub_content_search_keywords: Optional[list] = Unassigned()


@dataclass
class HubInfo(Base):
    """TBA"""
    hub_name: str
    hub_arn: str
    hub_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    hub_display_name: Optional[str] = Unassigned()
    hub_description: Optional[str] = Unassigned()
    hub_search_keywords: Optional[list] = Unassigned()


@dataclass
class HumanTaskUiSummary(Base):
    """TBA"""
    human_task_ui_name: str
    human_task_ui_arn: str
    creation_time: datetime.datetime


@dataclass
class IntegerParameterRangeSpecification(Base):
    """TBA"""
    min_value: str
    max_value: str


@dataclass
class ParameterRange(Base):
    """TBA"""
    integer_parameter_range_specification: Optional[IntegerParameterRangeSpecification] = Unassigned()
    continuous_parameter_range_specification: Optional[ContinuousParameterRangeSpecification] = Unassigned()
    categorical_parameter_range_specification: Optional[CategoricalParameterRangeSpecification] = Unassigned()


@dataclass
class HyperParameterSpecification(Base):
    """TBA"""
    name: str
    type: str
    description: Optional[str] = Unassigned()
    range: Optional[ParameterRange] = Unassigned()
    is_tunable: Optional[bool] = Unassigned()
    is_required: Optional[bool] = Unassigned()
    default_value: Optional[str] = Unassigned()


@dataclass
class HyperParameterTuningInstanceConfig(Base):
    """TBA"""
    instance_type: str
    instance_count: int
    volume_size_in_g_b: int


@dataclass
class HyperParameterTuningJobSearchEntity(Base):
    """TBA"""
    hyper_parameter_tuning_job_name: Optional[str] = Unassigned()
    hyper_parameter_tuning_job_arn: Optional[str] = Unassigned()
    hyper_parameter_tuning_job_config: Optional[HyperParameterTuningJobConfig] = Unassigned()
    training_job_definition: Optional[HyperParameterTrainingJobDefinition] = Unassigned()
    training_job_definitions: Optional[list] = Unassigned()
    hyper_parameter_tuning_job_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    hyper_parameter_tuning_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    training_job_status_counters: Optional[TrainingJobStatusCounters] = Unassigned()
    objective_status_counters: Optional[ObjectiveStatusCounters] = Unassigned()
    best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    overall_best_training_job: Optional[HyperParameterTrainingJobSummary] = Unassigned()
    warm_start_config: Optional[HyperParameterTuningJobWarmStartConfig] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    tuning_job_completion_details: Optional[HyperParameterTuningJobCompletionDetails] = Unassigned()
    consumed_resources: Optional[HyperParameterTuningJobConsumedResources] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class HyperParameterTuningJobSummary(Base):
    """TBA"""
    hyper_parameter_tuning_job_name: str
    hyper_parameter_tuning_job_arn: str
    hyper_parameter_tuning_job_status: str
    strategy: str
    creation_time: datetime.datetime
    training_job_status_counters: TrainingJobStatusCounters
    objective_status_counters: ObjectiveStatusCounters
    hyper_parameter_tuning_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    resource_limits: Optional[ResourceLimits] = Unassigned()


@dataclass
class IdentityProviderOAuthSetting(Base):
    """TBA"""
    data_source_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    secret_arn: Optional[str] = Unassigned()


@dataclass
class Image(Base):
    """TBA"""
    creation_time: datetime.datetime
    image_arn: str
    image_name: str
    image_status: str
    last_modified_time: datetime.datetime
    description: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


@dataclass
class ImageVersion(Base):
    """TBA"""
    creation_time: datetime.datetime
    image_arn: str
    image_version_arn: str
    image_version_status: str
    last_modified_time: datetime.datetime
    version: int
    failure_reason: Optional[str] = Unassigned()


@dataclass
class InferenceComponentSummary(Base):
    """TBA"""
    creation_time: datetime.datetime
    inference_component_arn: str
    inference_component_name: str
    endpoint_arn: str
    endpoint_name: str
    variant_name: str
    last_modified_time: datetime.datetime
    inference_component_status: Optional[str] = Unassigned()


@dataclass
class InferenceExperimentSummary(Base):
    """TBA"""
    name: str
    type: str
    status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    schedule: Optional[InferenceExperimentSchedule] = Unassigned()
    status_reason: Optional[str] = Unassigned()
    description: Optional[str] = Unassigned()
    completion_time: Optional[datetime.datetime] = Unassigned()
    role_arn: Optional[str] = Unassigned()


@dataclass
class RecommendationMetrics(Base):
    """TBA"""
    cost_per_hour: float
    cost_per_inference: float
    max_invocations: int
    model_latency: int
    cpu_utilization: Optional[float] = Unassigned()
    memory_utilization: Optional[float] = Unassigned()
    model_setup_time: Optional[int] = Unassigned()


@dataclass
class ModelConfiguration(Base):
    """TBA"""
    inference_specification_name: Optional[str] = Unassigned()
    environment_parameters: Optional[list] = Unassigned()
    compilation_job_name: Optional[str] = Unassigned()


@dataclass
class InferenceRecommendation(Base):
    """TBA"""
    metrics: RecommendationMetrics
    endpoint_configuration: EndpointOutputConfiguration
    model_configuration: ModelConfiguration
    recommendation_id: Optional[str] = Unassigned()
    invocation_end_time: Optional[datetime.datetime] = Unassigned()
    invocation_start_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class InferenceRecommendationsJob(Base):
    """TBA"""
    job_name: str
    job_description: str
    job_type: str
    job_arn: str
    status: str
    creation_time: datetime.datetime
    role_arn: str
    last_modified_time: datetime.datetime
    completion_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    sample_payload_url: Optional[str] = Unassigned()
    model_package_version_arn: Optional[str] = Unassigned()


@dataclass
class RecommendationJobInferenceBenchmark(Base):
    """TBA"""
    model_configuration: ModelConfiguration
    metrics: Optional[RecommendationMetrics] = Unassigned()
    endpoint_metrics: Optional[InferenceMetrics] = Unassigned()
    endpoint_configuration: Optional[EndpointOutputConfiguration] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    invocation_end_time: Optional[datetime.datetime] = Unassigned()
    invocation_start_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class InferenceRecommendationsJobStep(Base):
    """TBA"""
    step_type: str
    job_name: str
    status: str
    inference_benchmark: Optional[RecommendationJobInferenceBenchmark] = Unassigned()


@dataclass
class InstanceGroup(Base):
    """TBA"""
    instance_type: str
    instance_count: int
    instance_group_name: str


@dataclass
class IntegerParameterRange(Base):
    """TBA"""
    name: str
    min_value: str
    max_value: str
    scaling_type: Optional[str] = Unassigned()


@dataclass
class KernelSpec(Base):
    """TBA"""
    name: str
    display_name: Optional[str] = Unassigned()


@dataclass
class LabelCountersForWorkteam(Base):
    """TBA"""
    human_labeled: Optional[int] = Unassigned()
    pending_human: Optional[int] = Unassigned()
    total: Optional[int] = Unassigned()


@dataclass
class LabelingJobForWorkteamSummary(Base):
    """TBA"""
    job_reference_code: str
    work_requester_account_id: str
    creation_time: datetime.datetime
    labeling_job_name: Optional[str] = Unassigned()
    label_counters: Optional[LabelCountersForWorkteam] = Unassigned()
    number_of_human_workers_per_data_object: Optional[int] = Unassigned()


@dataclass
class LabelingJobSummary(Base):
    """TBA"""
    labeling_job_name: str
    labeling_job_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    labeling_job_status: str
    label_counters: LabelCounters
    workteam_arn: str
    pre_human_task_lambda_arn: str
    annotation_consolidation_lambda_arn: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    labeling_job_output: Optional[LabelingJobOutput] = Unassigned()
    input_config: Optional[LabelingJobInputConfig] = Unassigned()


@dataclass
class LambdaStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()
    output_parameters: Optional[list] = Unassigned()


@dataclass
class LineageGroupSummary(Base):
    """TBA"""
    lineage_group_arn: Optional[str] = Unassigned()
    lineage_group_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ListAlgorithmsInput(Base):
    """TBA"""
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()


@dataclass
class ListAlgorithmsOutput(Base):
    """TBA"""
    algorithm_summary_list: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListCodeRepositoriesInput(Base):
    """TBA"""
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    last_modified_time_after: Optional[datetime.datetime] = Unassigned()
    last_modified_time_before: Optional[datetime.datetime] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()


@dataclass
class ListCodeRepositoriesOutput(Base):
    """TBA"""
    code_repository_summary_list: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListEndpointConfigsInput(Base):
    """TBA"""
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()


@dataclass
class ListEndpointConfigsOutput(Base):
    """TBA"""
    endpoint_configs: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListEndpointsInput(Base):
    """TBA"""
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    last_modified_time_before: Optional[datetime.datetime] = Unassigned()
    last_modified_time_after: Optional[datetime.datetime] = Unassigned()
    status_equals: Optional[str] = Unassigned()


@dataclass
class ListEndpointsOutput(Base):
    """TBA"""
    endpoints: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListInferenceComponentsInput(Base):
    """TBA"""
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    last_modified_time_before: Optional[datetime.datetime] = Unassigned()
    last_modified_time_after: Optional[datetime.datetime] = Unassigned()
    status_equals: Optional[str] = Unassigned()
    endpoint_name_equals: Optional[str] = Unassigned()
    variant_name_equals: Optional[str] = Unassigned()


@dataclass
class ListInferenceComponentsOutput(Base):
    """TBA"""
    inference_components: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ModelMetadataSearchExpression(Base):
    """TBA"""
    filters: Optional[list] = Unassigned()


@dataclass
class ListModelPackageGroupsInput(Base):
    """TBA"""
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()


@dataclass
class ListModelPackageGroupsOutput(Base):
    """TBA"""
    model_package_group_summary_list: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListModelPackagesInput(Base):
    """TBA"""
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    model_package_type: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()


@dataclass
class ListModelPackagesOutput(Base):
    """TBA"""
    model_package_summary_list: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListModelsInput(Base):
    """TBA"""
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()


@dataclass
class ListModelsOutput(Base):
    """TBA"""
    models: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListNotebookInstanceLifecycleConfigsInput(Base):
    """TBA"""
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    last_modified_time_before: Optional[datetime.datetime] = Unassigned()
    last_modified_time_after: Optional[datetime.datetime] = Unassigned()


@dataclass
class ListNotebookInstanceLifecycleConfigsOutput(Base):
    """TBA"""
    next_token: Optional[str] = Unassigned()
    notebook_instance_lifecycle_configs: Optional[list] = Unassigned()


@dataclass
class ListNotebookInstancesInput(Base):
    """TBA"""
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    last_modified_time_before: Optional[datetime.datetime] = Unassigned()
    last_modified_time_after: Optional[datetime.datetime] = Unassigned()
    status_equals: Optional[str] = Unassigned()
    notebook_instance_lifecycle_config_name_contains: Optional[str] = Unassigned()
    default_code_repository_contains: Optional[str] = Unassigned()
    additional_code_repository_equals: Optional[str] = Unassigned()


@dataclass
class ListNotebookInstancesOutput(Base):
    """TBA"""
    next_token: Optional[str] = Unassigned()
    notebook_instances: Optional[list] = Unassigned()


@dataclass
class ListProjectsInput(Base):
    """TBA"""
    creation_time_after: Optional[datetime.datetime] = Unassigned()
    creation_time_before: Optional[datetime.datetime] = Unassigned()
    max_results: Optional[int] = Unassigned()
    name_contains: Optional[str] = Unassigned()
    next_token: Optional[str] = Unassigned()
    sort_by: Optional[str] = Unassigned()
    sort_order: Optional[str] = Unassigned()


@dataclass
class ListProjectsOutput(Base):
    """TBA"""
    project_summary_list: list
    next_token: Optional[str] = Unassigned()


@dataclass
class ListTagsInput(Base):
    """TBA"""
    resource_arn: str
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()


@dataclass
class ListTagsOutput(Base):
    """TBA"""
    tags: Optional[list] = Unassigned()
    next_token: Optional[str] = Unassigned()


@dataclass
class OidcMemberDefinition(Base):
    """TBA"""
    groups: Optional[list] = Unassigned()


@dataclass
class MemberDefinition(Base):
    """TBA"""
    cognito_member_definition: Optional[CognitoMemberDefinition] = Unassigned()
    oidc_member_definition: Optional[OidcMemberDefinition] = Unassigned()


@dataclass
class MetricData(Base):
    """TBA"""
    metric_name: Optional[str] = Unassigned()
    value: Optional[float] = Unassigned()
    timestamp: Optional[datetime.datetime] = Unassigned()


@dataclass
class MetricDatum(Base):
    """TBA"""
    metric_name: Optional[str] = Unassigned()
    value: Optional[float] = Unassigned()
    set: Optional[str] = Unassigned()
    standard_metric_name: Optional[str] = Unassigned()


@dataclass
class MetricDefinition(Base):
    """TBA"""
    name: str
    regex: str


@dataclass
class PredefinedMetricSpecification(Base):
    """TBA"""
    predefined_metric_type: Optional[str] = Unassigned()


@dataclass
class MetricSpecification(Base):
    """TBA"""
    predefined: Optional[PredefinedMetricSpecification] = Unassigned()
    customized: Optional[CustomizedMetricSpecification] = Unassigned()


@dataclass
class Model(Base):
    """TBA"""
    model_name: Optional[str] = Unassigned()
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[list] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_arn: Optional[str] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    tags: Optional[list] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()


@dataclass
class ModelCard(Base):
    """TBA"""
    model_card_arn: Optional[str] = Unassigned()
    model_card_name: Optional[str] = Unassigned()
    model_card_version: Optional[int] = Unassigned()
    content: Optional[str] = Unassigned()
    model_card_status: Optional[str] = Unassigned()
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[list] = Unassigned()
    model_id: Optional[str] = Unassigned()
    risk_rating: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()


@dataclass
class ModelCardExportJobSummary(Base):
    """TBA"""
    model_card_export_job_name: str
    model_card_export_job_arn: str
    status: str
    model_card_name: str
    model_card_version: int
    created_at: datetime.datetime
    last_modified_at: datetime.datetime


@dataclass
class ModelCardSummary(Base):
    """TBA"""
    model_card_name: str
    model_card_arn: str
    model_card_status: str
    creation_time: datetime.datetime
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ModelCardVersionSummary(Base):
    """TBA"""
    model_card_name: str
    model_card_arn: str
    model_card_status: str
    model_card_version: int
    creation_time: datetime.datetime
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ModelDashboardEndpoint(Base):
    """TBA"""
    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_status: str


@dataclass
class ModelDashboardIndicatorAction(Base):
    """TBA"""
    enabled: Optional[bool] = Unassigned()


@dataclass
class TransformJob(Base):
    """TBA"""
    transform_job_name: Optional[str] = Unassigned()
    transform_job_arn: Optional[str] = Unassigned()
    transform_job_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    max_concurrent_transforms: Optional[int] = Unassigned()
    model_client_config: Optional[ModelClientConfig] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()
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
    tags: Optional[list] = Unassigned()


@dataclass
class ModelDashboardModelCard(Base):
    """TBA"""
    model_card_arn: Optional[str] = Unassigned()
    model_card_name: Optional[str] = Unassigned()
    model_card_version: Optional[int] = Unassigned()
    model_card_status: Optional[str] = Unassigned()
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[list] = Unassigned()
    model_id: Optional[str] = Unassigned()
    risk_rating: Optional[str] = Unassigned()


@dataclass
class ModelDashboardModel(Base):
    """TBA"""
    model: Optional[Model] = Unassigned()
    endpoints: Optional[list] = Unassigned()
    last_batch_transform_job: Optional[TransformJob] = Unassigned()
    monitoring_schedules: Optional[list] = Unassigned()
    model_card: Optional[ModelDashboardModelCard] = Unassigned()


@dataclass
class ModelDashboardMonitoringSchedule(Base):
    """TBA"""
    monitoring_schedule_arn: Optional[str] = Unassigned()
    monitoring_schedule_name: Optional[str] = Unassigned()
    monitoring_schedule_status: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_config: Optional[MonitoringScheduleConfig] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    monitoring_alert_summaries: Optional[list] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class RealTimeInferenceConfig(Base):
    """TBA"""
    instance_type: str
    instance_count: int


@dataclass
class ModelInfrastructureConfig(Base):
    """TBA"""
    infrastructure_type: str
    real_time_inference_config: RealTimeInferenceConfig


@dataclass
class ModelInput(Base):
    """TBA"""
    data_input_config: str


@dataclass
class ModelLatencyThreshold(Base):
    """TBA"""
    percentile: Optional[str] = Unassigned()
    value_in_milliseconds: Optional[int] = Unassigned()


@dataclass
class ModelMetadataFilter(Base):
    """TBA"""
    name: str
    value: str


@dataclass
class ModelMetadataSummary(Base):
    """TBA"""
    domain: str
    framework: str
    task: str
    model: str
    framework_version: str


@dataclass
class ModelPackage(Base):
    """TBA"""
    model_package_name: Optional[str] = Unassigned()
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
    additional_inference_specifications: Optional[list] = Unassigned()
    source_uri: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()
    customer_metadata_properties: Optional[dict] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()


@dataclass
class ModelPackageContainerDefinition(Base):
    """TBA"""
    image: str
    container_hostname: Optional[str] = Unassigned()
    image_digest: Optional[str] = Unassigned()
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()
    product_id: Optional[str] = Unassigned()
    environment: Optional[dict] = Unassigned()
    model_input: Optional[ModelInput] = Unassigned()
    framework: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()
    nearest_model_name: Optional[str] = Unassigned()
    additional_s3_data_source: Optional[AdditionalS3DataSource] = Unassigned()


@dataclass
class ModelPackageGroup(Base):
    """TBA"""
    model_package_group_name: Optional[str] = Unassigned()
    model_package_group_arn: Optional[str] = Unassigned()
    model_package_group_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    model_package_group_status: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class ModelPackageGroupSummary(Base):
    """TBA"""
    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()


@dataclass
class ModelPackageStatusItem(Base):
    """TBA"""
    name: str
    status: str
    failure_reason: Optional[str] = Unassigned()


@dataclass
class ModelPackageSummary(Base):
    """TBA"""
    model_package_arn: str
    creation_time: datetime.datetime
    model_package_status: str
    model_package_name: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()


@dataclass
class ModelPackageValidationProfile(Base):
    """TBA"""
    profile_name: str
    transform_job_definition: TransformJobDefinition


@dataclass
class ModelStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class ModelSummary(Base):
    """TBA"""
    model_name: str
    model_arn: str
    creation_time: datetime.datetime


@dataclass
class ModelVariantConfig(Base):
    """TBA"""
    model_name: str
    variant_name: str
    infrastructure_config: ModelInfrastructureConfig


@dataclass
class ModelVariantConfigSummary(Base):
    """TBA"""
    model_name: str
    variant_name: str
    infrastructure_config: ModelInfrastructureConfig
    status: str


@dataclass
class MonitoringAlertActions(Base):
    """TBA"""
    model_dashboard_indicator: Optional[ModelDashboardIndicatorAction] = Unassigned()


@dataclass
class MonitoringAlertHistorySummary(Base):
    """TBA"""
    monitoring_schedule_name: str
    monitoring_alert_name: str
    creation_time: datetime.datetime
    alert_status: str


@dataclass
class MonitoringAlertSummary(Base):
    """TBA"""
    monitoring_alert_name: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    alert_status: str
    datapoints_to_alert: int
    evaluation_period: int
    actions: MonitoringAlertActions


@dataclass
class MonitoringInput(Base):
    """TBA"""
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


@dataclass
class MonitoringJobDefinitionSummary(Base):
    """TBA"""
    monitoring_job_definition_name: str
    monitoring_job_definition_arn: str
    creation_time: datetime.datetime
    endpoint_name: str


@dataclass
class MonitoringS3Output(Base):
    """TBA"""
    s3_uri: str
    local_path: str
    s3_upload_mode: Optional[str] = Unassigned()


@dataclass
class MonitoringOutput(Base):
    """TBA"""
    s3_output: MonitoringS3Output


@dataclass
class MonitoringSchedule(Base):
    """TBA"""
    monitoring_schedule_arn: Optional[str] = Unassigned()
    monitoring_schedule_name: Optional[str] = Unassigned()
    monitoring_schedule_status: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_config: Optional[MonitoringScheduleConfig] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class MonitoringScheduleSummary(Base):
    """TBA"""
    monitoring_schedule_name: str
    monitoring_schedule_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    monitoring_schedule_status: str
    endpoint_name: Optional[str] = Unassigned()
    monitoring_job_definition_name: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()


@dataclass
class NestedFilters(Base):
    """TBA"""
    nested_property_name: str
    filters: list


@dataclass
class NotebookInstanceLifecycleConfigSummary(Base):
    """TBA"""
    notebook_instance_lifecycle_config_name: str
    notebook_instance_lifecycle_config_arn: str
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class NotebookInstanceLifecycleHook(Base):
    """TBA"""
    content: Optional[str] = Unassigned()


@dataclass
class NotebookInstanceSummary(Base):
    """TBA"""
    notebook_instance_name: str
    notebook_instance_arn: str
    notebook_instance_status: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[list] = Unassigned()


@dataclass
class OnlineStoreConfigUpdate(Base):
    """TBA"""
    ttl_duration: Optional[TtlDuration] = Unassigned()


@dataclass
class OutputParameter(Base):
    """TBA"""
    name: str
    value: str


@dataclass
class OwnershipSettingsSummary(Base):
    """TBA"""
    owner_user_profile_name: Optional[str] = Unassigned()


@dataclass
class Parameter(Base):
    """TBA"""
    name: str
    value: str


@dataclass
class Parent(Base):
    """TBA"""
    trial_name: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()


@dataclass
class ParentHyperParameterTuningJob(Base):
    """TBA"""
    hyper_parameter_tuning_job_name: Optional[str] = Unassigned()


@dataclass
class ProductionVariantManagedInstanceScaling(Base):
    """TBA"""
    status: Optional[str] = Unassigned()
    min_instance_count: Optional[int] = Unassigned()
    max_instance_count: Optional[int] = Unassigned()


@dataclass
class ProductionVariantRoutingConfig(Base):
    """TBA"""
    routing_strategy: str


@dataclass
class PendingProductionVariantSummary(Base):
    """TBA"""
    variant_name: str
    deployed_images: Optional[list] = Unassigned()
    current_weight: Optional[float] = Unassigned()
    desired_weight: Optional[float] = Unassigned()
    current_instance_count: Optional[int] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    accelerator_type: Optional[str] = Unassigned()
    variant_status: Optional[list] = Unassigned()
    current_serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    desired_serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = Unassigned()
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


@dataclass
class Phase(Base):
    """TBA"""
    initial_number_of_users: Optional[int] = Unassigned()
    spawn_rate: Optional[int] = Unassigned()
    duration_in_seconds: Optional[int] = Unassigned()


@dataclass
class Pipeline(Base):
    """TBA"""
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_name: Optional[str] = Unassigned()
    pipeline_display_name: Optional[str] = Unassigned()
    pipeline_description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    pipeline_status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_run_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parallelism_configuration: Optional[ParallelismConfiguration] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class PipelineExecution(Base):
    """TBA"""
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
    pipeline_parameters: Optional[list] = Unassigned()


@dataclass
class TrainingJobStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class ProcessingJobStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class TransformJobStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class TuningJobStepMetaData(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class RegisterModelStepMetadata(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()


@dataclass
class QualityCheckStepMetadata(Base):
    """TBA"""
    check_type: Optional[str] = Unassigned()
    baseline_used_for_drift_check_statistics: Optional[str] = Unassigned()
    baseline_used_for_drift_check_constraints: Optional[str] = Unassigned()
    calculated_baseline_statistics: Optional[str] = Unassigned()
    calculated_baseline_constraints: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    violation_report: Optional[str] = Unassigned()
    check_job_arn: Optional[str] = Unassigned()
    skip_check: Optional[bool] = Unassigned()
    register_new_baseline: Optional[bool] = Unassigned()


@dataclass
class PipelineExecutionStepMetadata(Base):
    """TBA"""
    training_job: Optional[TrainingJobStepMetadata] = Unassigned()
    processing_job: Optional[ProcessingJobStepMetadata] = Unassigned()
    transform_job: Optional[TransformJobStepMetadata] = Unassigned()
    tuning_job: Optional[TuningJobStepMetaData] = Unassigned()
    model: Optional[ModelStepMetadata] = Unassigned()
    register_model: Optional[RegisterModelStepMetadata] = Unassigned()
    condition: Optional[ConditionStepMetadata] = Unassigned()
    callback: Optional[CallbackStepMetadata] = Unassigned()
    # lambda: Optional[LambdaStepMetadata] = Unassigned()
    e_m_r: Optional[EMRStepMetadata] = Unassigned()
    quality_check: Optional[QualityCheckStepMetadata] = Unassigned()
    clarify_check: Optional[ClarifyCheckStepMetadata] = Unassigned()
    fail: Optional[FailStepMetadata] = Unassigned()
    auto_m_l_job: Optional[AutoMLJobStepMetadata] = Unassigned()


@dataclass
class SelectiveExecutionResult(Base):
    """TBA"""
    source_pipeline_execution_arn: Optional[str] = Unassigned()


@dataclass
class PipelineExecutionStep(Base):
    """TBA"""
    step_name: Optional[str] = Unassigned()
    step_display_name: Optional[str] = Unassigned()
    step_description: Optional[str] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    step_status: Optional[str] = Unassigned()
    cache_hit_result: Optional[CacheHitResult] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    metadata: Optional[PipelineExecutionStepMetadata] = Unassigned()
    attempt_count: Optional[int] = Unassigned()
    selective_execution_result: Optional[SelectiveExecutionResult] = Unassigned()


@dataclass
class PipelineExecutionSummary(Base):
    """TBA"""
    pipeline_execution_arn: Optional[str] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    pipeline_execution_status: Optional[str] = Unassigned()
    pipeline_execution_description: Optional[str] = Unassigned()
    pipeline_execution_display_name: Optional[str] = Unassigned()
    pipeline_execution_failure_reason: Optional[str] = Unassigned()


@dataclass
class PipelineSummary(Base):
    """TBA"""
    pipeline_arn: Optional[str] = Unassigned()
    pipeline_name: Optional[str] = Unassigned()
    pipeline_display_name: Optional[str] = Unassigned()
    pipeline_description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_execution_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ProcessingFeatureStoreOutput(Base):
    """TBA"""
    feature_group_name: str


@dataclass
class ProcessingS3Input(Base):
    """TBA"""
    s3_uri: str
    s3_data_type: str
    local_path: Optional[str] = Unassigned()
    s3_input_mode: Optional[str] = Unassigned()
    s3_data_distribution_type: Optional[str] = Unassigned()
    s3_compression_type: Optional[str] = Unassigned()


@dataclass
class ProcessingInput(Base):
    """TBA"""
    input_name: str
    app_managed: Optional[bool] = Unassigned()
    s3_input: Optional[ProcessingS3Input] = Unassigned()
    dataset_definition: Optional[DatasetDefinition] = Unassigned()


@dataclass
class ProcessingJob(Base):
    """TBA"""
    processing_inputs: Optional[list] = Unassigned()
    processing_output_config: Optional[ProcessingOutputConfig] = Unassigned()
    processing_job_name: Optional[str] = Unassigned()
    processing_resources: Optional[ProcessingResources] = Unassigned()
    stopping_condition: Optional[ProcessingStoppingCondition] = Unassigned()
    app_specification: Optional[AppSpecification] = Unassigned()
    environment: Optional[dict] = Unassigned()
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
    tags: Optional[list] = Unassigned()


@dataclass
class ProcessingJobSummary(Base):
    """TBA"""
    processing_job_name: str
    processing_job_arn: str
    creation_time: datetime.datetime
    processing_job_status: str
    processing_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    exit_message: Optional[str] = Unassigned()


@dataclass
class ProcessingS3Output(Base):
    """TBA"""
    s3_uri: str
    local_path: str
    s3_upload_mode: str


@dataclass
class ProcessingOutput(Base):
    """TBA"""
    output_name: str
    s3_output: Optional[ProcessingS3Output] = Unassigned()
    feature_store_output: Optional[ProcessingFeatureStoreOutput] = Unassigned()
    app_managed: Optional[bool] = Unassigned()


@dataclass
class ProductionVariantCoreDumpConfig(Base):
    """TBA"""
    destination_s3_uri: str
    kms_key_id: Optional[str] = Unassigned()


@dataclass
class ProductionVariant(Base):
    """TBA"""
    variant_name: str
    model_name: Optional[str] = Unassigned()
    initial_instance_count: Optional[int] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    initial_variant_weight: Optional[float] = Unassigned()
    accelerator_type: Optional[str] = Unassigned()
    core_dump_config: Optional[ProductionVariantCoreDumpConfig] = Unassigned()
    serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    model_data_download_timeout_in_seconds: Optional[int] = Unassigned()
    container_startup_health_check_timeout_in_seconds: Optional[int] = Unassigned()
    enable_s_s_m_access: Optional[bool] = Unassigned()
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = Unassigned()
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


@dataclass
class ProductionVariantStatus(Base):
    """TBA"""
    status: str
    status_message: Optional[str] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class ProductionVariantSummary(Base):
    """TBA"""
    variant_name: str
    deployed_images: Optional[list] = Unassigned()
    current_weight: Optional[float] = Unassigned()
    desired_weight: Optional[float] = Unassigned()
    current_instance_count: Optional[int] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    variant_status: Optional[list] = Unassigned()
    current_serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    desired_serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = Unassigned()
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


@dataclass
class ProfilerConfigForUpdate(Base):
    """TBA"""
    s3_output_path: Optional[str] = Unassigned()
    profiling_interval_in_milliseconds: Optional[int] = Unassigned()
    profiling_parameters: Optional[dict] = Unassigned()
    disable_profiler: Optional[bool] = Unassigned()


@dataclass
class ProfilerRuleConfiguration(Base):
    """TBA"""
    rule_configuration_name: str
    rule_evaluator_image: str
    local_path: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    rule_parameters: Optional[dict] = Unassigned()


@dataclass
class ProfilerRuleEvaluationStatus(Base):
    """TBA"""
    rule_configuration_name: Optional[str] = Unassigned()
    rule_evaluation_job_arn: Optional[str] = Unassigned()
    rule_evaluation_status: Optional[str] = Unassigned()
    status_details: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class Project(Base):
    """TBA"""
    project_arn: Optional[str] = Unassigned()
    project_name: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioning_details: Optional[ServiceCatalogProvisioningDetails] = Unassigned()
    service_catalog_provisioned_product_details: Optional[ServiceCatalogProvisionedProductDetails] = Unassigned()
    project_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    tags: Optional[list] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()


@dataclass
class ProjectSummary(Base):
    """TBA"""
    project_name: str
    project_arn: str
    project_id: str
    creation_time: datetime.datetime
    project_status: str
    project_description: Optional[str] = Unassigned()


@dataclass
class PropertyNameSuggestion(Base):
    """TBA"""
    property_name: Optional[str] = Unassigned()


@dataclass
class ProvisioningParameter(Base):
    """TBA"""
    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


@dataclass
class PutModelPackageGroupPolicyInput(Base):
    """TBA"""
    model_package_group_name: str
    resource_policy: str


@dataclass
class PutModelPackageGroupPolicyOutput(Base):
    """TBA"""
    model_package_group_arn: str


@dataclass
class QueryFilters(Base):
    """TBA"""
    types: Optional[list] = Unassigned()
    lineage_types: Optional[list] = Unassigned()
    created_before: Optional[datetime.datetime] = Unassigned()
    created_after: Optional[datetime.datetime] = Unassigned()
    modified_before: Optional[datetime.datetime] = Unassigned()
    modified_after: Optional[datetime.datetime] = Unassigned()
    properties: Optional[dict] = Unassigned()


@dataclass
class RealTimeInferenceRecommendation(Base):
    """TBA"""
    recommendation_id: str
    instance_type: str
    environment: Optional[dict] = Unassigned()


@dataclass
class RemoteDebugConfigForUpdate(Base):
    """TBA"""
    enable_remote_debug: Optional[bool] = Unassigned()


@dataclass
class RenderableTask(Base):
    """TBA"""
    input: str


@dataclass
class RenderingError(Base):
    """TBA"""
    code: str
    message: str


@dataclass
class ResourceCatalog(Base):
    """TBA"""
    resource_catalog_arn: str
    resource_catalog_name: str
    description: str
    creation_time: datetime.datetime


@dataclass
class ResourceConfigForUpdate(Base):
    """TBA"""
    keep_alive_period_in_seconds: int


@dataclass
class ResourceInUse(Base):
    """TBA"""
    message: Optional[str] = Unassigned()


@dataclass
class ResourceLimitExceeded(Base):
    """TBA"""
    message: Optional[str] = Unassigned()


@dataclass
class ResourceNotFound(Base):
    """TBA"""
    message: Optional[str] = Unassigned()


@dataclass
class TargetTrackingScalingPolicyConfiguration(Base):
    """TBA"""
    metric_specification: Optional[MetricSpecification] = Unassigned()
    target_value: Optional[float] = Unassigned()


@dataclass
class ScalingPolicy(Base):
    """TBA"""
    target_tracking: Optional[TargetTrackingScalingPolicyConfiguration] = Unassigned()


@dataclass
class SearchExpression(Base):
    """TBA"""
    filters: Optional[list] = Unassigned()
    nested_filters: Optional[list] = Unassigned()
    sub_expressions: Optional[list] = Unassigned()
    operator: Optional[str] = Unassigned()


@dataclass
class TrainingJob(Base):
    """TBA"""
    training_job_name: Optional[str] = Unassigned()
    training_job_arn: Optional[str] = Unassigned()
    tuning_job_arn: Optional[str] = Unassigned()
    labeling_job_arn: Optional[str] = Unassigned()
    auto_m_l_job_arn: Optional[str] = Unassigned()
    model_artifacts: Optional[ModelArtifacts] = Unassigned()
    training_job_status: Optional[str] = Unassigned()
    secondary_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    hyper_parameters: Optional[dict] = Unassigned()
    algorithm_specification: Optional[AlgorithmSpecification] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    input_data_config: Optional[list] = Unassigned()
    output_data_config: Optional[OutputDataConfig] = Unassigned()
    resource_config: Optional[ResourceConfig] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    stopping_condition: Optional[StoppingCondition] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    secondary_status_transitions: Optional[list] = Unassigned()
    final_metric_data_list: Optional[list] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_managed_spot_training: Optional[bool] = Unassigned()
    checkpoint_config: Optional[CheckpointConfig] = Unassigned()
    training_time_in_seconds: Optional[int] = Unassigned()
    billable_time_in_seconds: Optional[int] = Unassigned()
    debug_hook_config: Optional[DebugHookConfig] = Unassigned()
    experiment_config: Optional[ExperimentConfig] = Unassigned()
    debug_rule_configurations: Optional[list] = Unassigned()
    tensor_board_output_config: Optional[TensorBoardOutputConfig] = Unassigned()
    debug_rule_evaluation_statuses: Optional[list] = Unassigned()
    profiler_config: Optional[ProfilerConfig] = Unassigned()
    environment: Optional[dict] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class Trial(Base):
    """TBA"""
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
    tags: Optional[list] = Unassigned()
    trial_component_summaries: Optional[list] = Unassigned()


@dataclass
class TrialComponentSourceDetail(Base):
    """TBA"""
    source_arn: Optional[str] = Unassigned()
    training_job: Optional[TrainingJob] = Unassigned()
    processing_job: Optional[ProcessingJob] = Unassigned()
    transform_job: Optional[TransformJob] = Unassigned()


@dataclass
class TrialComponent(Base):
    """TBA"""
    trial_component_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    trial_component_arn: Optional[str] = Unassigned()
    source: Optional[TrialComponentSource] = Unassigned()
    status: Optional[TrialComponentStatus] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    parameters: Optional[dict] = Unassigned()
    input_artifacts: Optional[dict] = Unassigned()
    output_artifacts: Optional[dict] = Unassigned()
    metrics: Optional[list] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    source_detail: Optional[TrialComponentSourceDetail] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    tags: Optional[list] = Unassigned()
    parents: Optional[list] = Unassigned()
    run_name: Optional[str] = Unassigned()


@dataclass
class SearchRecord(Base):
    """TBA"""
    training_job: Optional[TrainingJob] = Unassigned()
    experiment: Optional[Experiment] = Unassigned()
    trial: Optional[Trial] = Unassigned()
    trial_component: Optional[TrialComponent] = Unassigned()
    endpoint: Optional[Endpoint] = Unassigned()
    model_package: Optional[ModelPackage] = Unassigned()
    model_package_group: Optional[ModelPackageGroup] = Unassigned()
    pipeline: Optional[Pipeline] = Unassigned()
    pipeline_execution: Optional[PipelineExecution] = Unassigned()
    feature_group: Optional[FeatureGroup] = Unassigned()
    feature_metadata: Optional[FeatureMetadata] = Unassigned()
    project: Optional[Project] = Unassigned()
    hyper_parameter_tuning_job: Optional[HyperParameterTuningJobSearchEntity] = Unassigned()
    model_card: Optional[ModelCard] = Unassigned()
    model: Optional[ModelDashboardModel] = Unassigned()


@dataclass
class SecondaryStatusTransition(Base):
    """TBA"""
    status: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Unassigned()
    status_message: Optional[str] = Unassigned()


@dataclass
class SelectedStep(Base):
    """TBA"""
    step_name: str


@dataclass
class ServiceCatalogProvisioningUpdateDetails(Base):
    """TBA"""
    provisioning_artifact_id: Optional[str] = Unassigned()
    provisioning_parameters: Optional[list] = Unassigned()


@dataclass
class ShadowModelVariantConfig(Base):
    """TBA"""
    shadow_model_variant_name: str
    sampling_percentage: int


@dataclass
class SourceAlgorithm(Base):
    """TBA"""
    algorithm_name: str
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()


@dataclass
class SpaceSettingsSummary(Base):
    """TBA"""
    app_type: Optional[str] = Unassigned()
    space_storage_settings: Optional[SpaceStorageSettings] = Unassigned()


@dataclass
class SpaceSharingSettingsSummary(Base):
    """TBA"""
    sharing_type: Optional[str] = Unassigned()


@dataclass
class SpaceDetails(Base):
    """TBA"""
    domain_id: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    space_settings_summary: Optional[SpaceSettingsSummary] = Unassigned()
    space_sharing_settings_summary: Optional[SpaceSharingSettingsSummary] = Unassigned()
    ownership_settings_summary: Optional[OwnershipSettingsSummary] = Unassigned()
    space_display_name: Optional[str] = Unassigned()


@dataclass
class StartNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str


@dataclass
class StopNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str


@dataclass
class StudioLifecycleConfigDetails(Base):
    """TBA"""
    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()


@dataclass
class Tag(Base):
    """TBA"""
    key: str
    value: str


@dataclass
class ThroughputConfigUpdate(Base):
    """TBA"""
    throughput_mode: Optional[str] = Unassigned()
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


@dataclass
class TrainingJobSummary(Base):
    """TBA"""
    training_job_name: str
    training_job_arn: str
    creation_time: datetime.datetime
    training_job_status: str
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    warm_pool_status: Optional[WarmPoolStatus] = Unassigned()


@dataclass
class TransformJobSummary(Base):
    """TBA"""
    transform_job_name: str
    transform_job_arn: str
    creation_time: datetime.datetime
    transform_job_status: str
    transform_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


@dataclass
class TrialComponentArtifact(Base):
    """TBA"""
    value: str
    media_type: Optional[str] = Unassigned()


@dataclass
class TrialComponentMetricSummary(Base):
    """TBA"""
    metric_name: Optional[str] = Unassigned()
    source_arn: Optional[str] = Unassigned()
    time_stamp: Optional[datetime.datetime] = Unassigned()
    max: Optional[float] = Unassigned()
    min: Optional[float] = Unassigned()
    last: Optional[float] = Unassigned()
    count: Optional[int] = Unassigned()
    avg: Optional[float] = Unassigned()
    std_dev: Optional[float] = Unassigned()


@dataclass
class TrialComponentParameterValue(Base):
    """TBA"""
    string_value: Optional[str] = Unassigned()
    number_value: Optional[float] = Unassigned()


@dataclass
class TrialComponentSimpleSummary(Base):
    """TBA"""
    trial_component_name: Optional[str] = Unassigned()
    trial_component_arn: Optional[str] = Unassigned()
    trial_component_source: Optional[TrialComponentSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()


@dataclass
class TrialComponentSummary(Base):
    """TBA"""
    trial_component_name: Optional[str] = Unassigned()
    trial_component_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    trial_component_source: Optional[TrialComponentSource] = Unassigned()
    status: Optional[TrialComponentStatus] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()


@dataclass
class TrialSummary(Base):
    """TBA"""
    trial_arn: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    trial_source: Optional[TrialSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class UpdateCodeRepositoryInput(Base):
    """TBA"""
    code_repository_name: str
    git_config: Optional[GitConfigForUpdate] = Unassigned()


@dataclass
class UpdateCodeRepositoryOutput(Base):
    """TBA"""
    code_repository_arn: str


@dataclass
class UpdateEndpointInput(Base):
    """TBA"""
    endpoint_name: str
    endpoint_config_name: str
    retain_all_variant_properties: Optional[bool] = Unassigned()
    exclude_retained_variant_properties: Optional[list] = Unassigned()
    deployment_config: Optional[DeploymentConfig] = Unassigned()
    retain_deployment_config: Optional[bool] = Unassigned()


@dataclass
class UpdateEndpointOutput(Base):
    """TBA"""
    endpoint_arn: str


@dataclass
class UpdateEndpointWeightsAndCapacitiesInput(Base):
    """TBA"""
    endpoint_name: str
    desired_weights_and_capacities: list


@dataclass
class UpdateEndpointWeightsAndCapacitiesOutput(Base):
    """TBA"""
    endpoint_arn: str


@dataclass
class UpdateInferenceComponentInput(Base):
    """TBA"""
    inference_component_name: str
    specification: Optional[InferenceComponentSpecification] = Unassigned()
    runtime_config: Optional[InferenceComponentRuntimeConfig] = Unassigned()


@dataclass
class UpdateInferenceComponentOutput(Base):
    """TBA"""
    inference_component_arn: str


@dataclass
class UpdateInferenceComponentRuntimeConfigInput(Base):
    """TBA"""
    inference_component_name: str
    desired_runtime_config: InferenceComponentRuntimeConfig


@dataclass
class UpdateInferenceComponentRuntimeConfigOutput(Base):
    """TBA"""
    inference_component_arn: str


@dataclass
class UpdateModelPackageInput(Base):
    """TBA"""
    model_package_arn: str
    model_approval_status: Optional[str] = Unassigned()
    approval_description: Optional[str] = Unassigned()
    customer_metadata_properties: Optional[dict] = Unassigned()
    customer_metadata_properties_to_remove: Optional[list] = Unassigned()
    additional_inference_specifications_to_add: Optional[list] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    source_uri: Optional[str] = Unassigned()


@dataclass
class UpdateModelPackageOutput(Base):
    """TBA"""
    model_package_arn: str


@dataclass
class UpdateNotebookInstanceInput(Base):
    """TBA"""
    notebook_instance_name: str
    instance_type: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    lifecycle_config_name: Optional[str] = Unassigned()
    disassociate_lifecycle_config: Optional[bool] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[list] = Unassigned()
    accelerator_types: Optional[list] = Unassigned()
    disassociate_accelerator_types: Optional[bool] = Unassigned()
    disassociate_default_code_repository: Optional[bool] = Unassigned()
    disassociate_additional_code_repositories: Optional[bool] = Unassigned()
    root_access: Optional[str] = Unassigned()
    instance_metadata_service_configuration: Optional[InstanceMetadataServiceConfiguration] = Unassigned()


@dataclass
class UpdateNotebookInstanceLifecycleConfigInput(Base):
    """TBA"""
    notebook_instance_lifecycle_config_name: str
    on_create: Optional[list] = Unassigned()
    on_start: Optional[list] = Unassigned()


@dataclass
class UpdateProjectInput(Base):
    """TBA"""
    project_name: str
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioning_update_details: Optional[ServiceCatalogProvisioningUpdateDetails] = Unassigned()
    tags: Optional[list] = Unassigned()


@dataclass
class UpdateProjectOutput(Base):
    """TBA"""
    project_arn: str


@dataclass
class UserProfileDetails(Base):
    """TBA"""
    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


@dataclass
class VariantProperty(Base):
    """TBA"""
    variant_property_type: str


@dataclass
class Vertex(Base):
    """TBA"""
    arn: Optional[str] = Unassigned()
    type: Optional[str] = Unassigned()
    lineage_type: Optional[str] = Unassigned()


@dataclass
class VisibilityConditions(Base):
    """TBA"""
    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()

