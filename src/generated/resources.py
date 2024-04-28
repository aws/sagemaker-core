
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
    action_name: str


class Algorithm(BaseModel):
    algorithm_name: str


class App(BaseModel):
    domain_id: str
    app_type: str
    app_name: str
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()


class AppImageConfig(BaseModel):
    app_image_config_name: str


class Artifact(BaseModel):
    artifact_arn: str


class Association(BaseModel):


class AutoMLJob(BaseModel):
    auto_m_l_job_name: str


class AutoMLJobV2(BaseModel):
    auto_m_l_job_name: str


class Cluster(BaseModel):
    cluster_name: str


class CodeRepository(BaseModel):
    code_repository_name: str


class CompilationJob(BaseModel):
    compilation_job_name: str


class Context(BaseModel):
    context_name: str


class DataQualityJobDefinition(BaseModel):
    job_definition_name: str


class DeviceFleet(BaseModel):
    device_fleet_name: str


class Devices(BaseModel):


class Domain(BaseModel):
    domain_id: str


class EdgeDeploymentPlan(BaseModel):
    edge_deployment_plan_name: str
    next_token: Optional[str] = Unassigned()
    max_results: Optional[int] = Unassigned()


class EdgeDeploymentStage(BaseModel):


class EdgePackagingJob(BaseModel):
    edge_packaging_job_name: str


class Endpoint(BaseModel):
    endpoint_name: str


class EndpointConfig(BaseModel):
    endpoint_config_name: str


class Experiment(BaseModel):
    experiment_name: str


class FeatureGroup(BaseModel):
    feature_group_name: str
    next_token: Optional[str] = Unassigned()


class FlowDefinition(BaseModel):
    flow_definition_name: str


class Hub(BaseModel):
    hub_name: str


class HubContent(BaseModel):
    hub_name: str
    hub_content_type: str
    hub_content_name: str
    hub_content_version: Optional[str] = Unassigned()


class HumanTaskUi(BaseModel):
    human_task_ui_name: str


class HyperParameterTuningJob(BaseModel):
    hyper_parameter_tuning_job_name: str


class Image(BaseModel):
    image_name: str


class ImageVersion(BaseModel):
    image_name: str
    version: Optional[int] = Unassigned()
    alias: Optional[str] = Unassigned()


class InferenceComponent(BaseModel):
    inference_component_name: str


class InferenceExperiment(BaseModel):
    name: str


class InferenceRecommendationsJob(BaseModel):
    job_name: str


class LabelingJob(BaseModel):
    labeling_job_name: str


class Model(BaseModel):
    model_name: str


class ModelBiasJobDefinition(BaseModel):
    job_definition_name: str


class ModelCard(BaseModel):
    model_card_name: str
    model_card_version: Optional[int] = Unassigned()


class ModelCardExportJob(BaseModel):
    model_card_export_job_arn: str


class ModelExplainabilityJobDefinition(BaseModel):
    job_definition_name: str


class ModelPackage(BaseModel):
    model_package_name: str


class ModelPackageGroup(BaseModel):
    model_package_group_name: str


class ModelQualityJobDefinition(BaseModel):
    job_definition_name: str


class MonitoringSchedule(BaseModel):
    monitoring_schedule_name: str


class NotebookInstance(BaseModel):
    notebook_instance_name: str


class NotebookInstanceLifecycleConfig(BaseModel):
    notebook_instance_lifecycle_config_name: str


class Pipeline(BaseModel):
    pipeline_name: str


class PipelineExecution(BaseModel):
    pipeline_execution_arn: str


class PresignedDomainUrl(BaseModel):


class PresignedNotebookInstanceUrl(BaseModel):


class ProcessingJob(BaseModel):
    processing_job_name: str


class Project(BaseModel):
    project_name: str


class Space(BaseModel):
    domain_id: str
    space_name: str


class StudioLifecycleConfig(BaseModel):
    studio_lifecycle_config_name: str


class Tags(BaseModel):


class TrainingJob(BaseModel):
    training_job_name: str


class TransformJob(BaseModel):
    transform_job_name: str


class Trial(BaseModel):
    trial_name: str


class TrialComponent(BaseModel):
    trial_component_name: str


class UserProfile(BaseModel):
    domain_id: str
    user_profile_name: str


class Workforce(BaseModel):
    workforce_name: str


class Workteam(BaseModel):
    workteam_name: str


