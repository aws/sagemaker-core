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

from enum import Enum
import shlex
from typing import Optional, List, Union, Dict, Tuple
import sagemaker
from sagemaker import image_uris, get_execution_role, Session
import sagemaker.serverless
import sagemaker.training_compiler
import sagemaker.training_compiler.config


from sagemaker_core.resources import TrainingJob
from sagemaker_core.shapes import (
    ResourceConfig,
    StoppingCondition,
    OutputDataConfig,
    TrainingImageConfig,
    AlgorithmSpecification,
    Channel,
    DataSource,
    S3DataSource,
    FileSystemDataSource,
    Base
)

from model_trainer.utils import (
    _is_valid_ecr_image, 
    _is_valid_s3_uri, 
    _is_valid_path, 
    _get_unique_name, 
    _get_base_name_from_image
)

from sagemaker_core.main.utils import logger

class TrainingRunMode(Enum):
    REMOTE = "Remote"
    LOCAL = "Local"
    
class ImageSpec():
    def __init__(
        self, 
        framework_name: str,
        version: str, 
        image_scope: Optional[str] = None, 
        instance_type: Optional[str] = None, 
        py_version: Optional[str] = None, 
        region: Optional[str] = "us-west-2",
        accelerator_type: Optional[str] = None,
        container_version: Optional[str] = None,
        distribution: Optional[dict] = None,
        base_framework_version: Optional[str] =None,
        training_compiler_config: Optional[sagemaker.training_compiler.config.TrainingCompilerConfig] = None,
        model_id: Optional[str] = None,
        model_version: Optional[str] = None,
        hub_arn: Optional[str] = None,
        tolerate_vulnerable_model: Optional[bool] = False,
        tolerate_deprecated_model: Optional[bool] = False,
        sdk_version: Optional[str] = None,
        inference_tool: Optional[str] = None,
        serverless_inference_config: Optional[sagemaker.serverless.ServerlessInferenceConfig] = None,
        config_name: Optional[str] = None,
        sagemaker_session: Optional[Session] = None,
    ):
        self.framework_name = framework_name
        self.version = version
        self.image_scope = image_scope
        self.instance_type = instance_type
        self.py_version = py_version        
        self.region = region
        self.accelerator_type = accelerator_type
        self.container_version = container_version
        self.distribution = distribution
        self.base_framework_version = base_framework_version
        self.training_compiler_config = training_compiler_config
        self.model_id = model_id
        self.model_version = model_version
        self.hub_arn = hub_arn
        self.tolerate_vulnerable_model = tolerate_vulnerable_model
        self.tolerate_deprecated_model = tolerate_deprecated_model
        self.sdk_version = sdk_version
        self.inference_tool = inference_tool
        self.serverless_inference_config = serverless_inference_config
        self.config_name = config_name
        self.sagemaker_session = sagemaker_session
        
        
    def get_image_uri(self):
        return image_uris.retrieve(
            framework=self.framework_name, 
            image_scope=self.image_scope,
            instance_type=self.instance_type,
            py_version=self.py_version,
            region=self.region, 
            version=self.version,
            accelerator_type=self.accelerator_type,
            container_version=self.container_version,
            distribution=self.distribution,
            base_framework_version=self.base_framework_version,
            training_compiler_config=self.training_compiler_config,
            model_id=self.model_id,
            model_version=self.model_version,
            hub_arn=self.hub_arn,
            tolerate_vulnerable_model=self.tolerate_vulnerable_model,
            tolerate_deprecated_model=self.tolerate_deprecated_model,
            sdk_version=self.sdk_version,
            inference_tool=self.inference_tool,
            serverless_inference_config=self.serverless_inference_config,
            config_name=self.config_name,
            sagemaker_session=self.sagemaker_session
        )

class SourceCodeConfig(Base):
    """
    SourceCodeConfig
    
    Attributes:
        commnd (str): The raw commands to execute in the training job container (eg, "python train.py <args>").
        source_dir (Optional[Union[str, S3DataSource]]): The directory containing the source code to be used in the training job container. This can be a local directory path or an S3 URI.
            References to files in the source_dir in the container should be relative to the source_dir and in the format "opt/ml/input/data/code/<path_to_file>".
    """
    command: str
    source_dir: Optional[Union[str, S3DataSource]]


class DistributionConfig:
    """
    DistributionConfig
    
    Attributes:
        enabled (bool): If True, enables distributed training.
        framework (str): The framework used for distributed training.
        parameters (Dict[str, str]): The parameters for distributed training.
    """

    enabled: bool
    framework: str
    parameters: Optional[Dict[str, str]]
    
    def __init__(
        self, 
        enabled: bool, 
        framework: str, 
        parameters: Optional[Dict[str, str]]
    ):
        self.enabled = enabled
        self.framework = framework
        self.parameters = parameters


class TorchDistributedConfig(DistributionConfig):
    """
    TorchDistributedConfig
    
    Attributes:
        enabled (bool): If True, enables PyTorch distributed training.
        parameters (Dict[str, str]): The parameters for distributed training.
    """
    
    def __init__(
        self, 
        enabled: bool, 
        parameters: Optional[Dict[str, str]] = None
    ):
        super().__init__(enabled, "torch", parameters)


class SMDistributedConfig(DistributionConfig):
    """
    SMDistributedConfig
    
    Attributes:
        enabled (bool): If True, enables SageMaker distributed training.
        parameters (Dict[str, str]): The parameters for distributed training.
    """
    
    def __init__(
        self, 
        enabled: bool, 
        parameters: Optional[Dict[str, str]] = None
    ):
        super().__init__(enabled, "smdistributed", parameters)
      

class ModelTrainer:
    @staticmethod
    def _default_resource_config() -> ResourceConfig:
        x = ResourceConfig(
            volume_size_in_gb=30,
            instance_count=1,
        )
        return x
    
    @staticmethod
    def _default_stopping_condition() -> StoppingCondition:
        x = StoppingCondition(
            max_runtime_in_seconds=86400
        )
        return x
    
    @staticmethod
    def _default_output_data_config(session: Session, base_name: str) -> OutputDataConfig:
        x = OutputDataConfig(
            s3_output_path=f"s3://{session.default_bucket()}/{base_name}/output/",
            compression_type="NONE"
        )
        return x

    def __init__(
        self,
        training_image: Optional[Union[str | ImageSpec]] = None,
        training_input_mode: Optional[str] = None,
        algorithm_name: Optional[str] = None,
        source_code_config: Optional[SourceCodeConfig] = None,
        environment: Optional[Dict[str, str]] = None,
        hyper_parameters: Optional[Dict[str, str]] = None,
        distribution: Optional[DistributionConfig] = None,
        resource_config: Optional[ResourceConfig] = None,
        stopping_condition: Optional[StoppingCondition] = None,
        output_data_config: Optional[OutputDataConfig] = None,
        base_name: Optional[str] = None,
        role: Optional[str] = None,
        session: Optional[Session] = None,
    ):
        self.session = session if session else Session()
        self.role = role
        if not self.role:
            role = get_execution_role()
            logger.info(f"Role was not provided. Using default role: {role}")
            self.role = role
        
        if not training_image and not algorithm_name:
            raise ValueError("Either training_image or algorithm_name must be provided")
        if training_image and algorithm_name:
            raise ValueError("Only one of training_image or algorithm_name should be provided")
        

        self.training_image = None
        if isinstance(training_image, str):
            self.training_image = training_image
            if not _is_valid_ecr_image(training_image):
                raise ValueError(
                    "The training_image string must be in the format of 'account_id.dkr.ecr.region.amazonaws.com/repository[:tag]'"
                )
        elif isinstance(training_image, ImageSpec):
            self.training_image = training_image.get_image_uri()

        
        self.algorithm_name = algorithm_name
        self.base_name = base_name or _get_base_name_from_image(self.training_image) or algorithm_name
        
        self.resource_config = resource_config
        if not self.resource_config:
            self.resource_config = self._default_resource_config()
            logger.info(f"Resource Config was not provided. Using default: {self.resource_config.__dict__}")
        
        self.stopping_condition = stopping_condition
        if not self.stopping_condition:
            self.stopping_condition = self._default_stopping_condition()
            logger.info(f"Stopping Condition was not provided. Using default: {self.stopping_condition.__dict__}")

        self.output_data_config = output_data_config
        if not self.output_data_config:
            self.output_data_config = self._default_output_data_config(
                session=self.session, 
                base_name=self.base_name
            )
            logger.info(f"Output Data Config was not provided. Using default: {self.output_data_config.__dict__}")
        
        self.training_input_mode = training_input_mode or "File"
        self.environment = environment
        self.hyper_parameters = hyper_parameters
        self.distribution = distribution
        self.source_code_config = source_code_config
        
    def get_entrypoint_and_arguments(self, source_code_config: SourceCodeConfig) -> Tuple[List[str], List[str]]:
        commands = source_code_config.command.strip()
        
        # remove any extra spaces greater than 1
        commands = " ".join(commands.split())
        
        container_entrypoint = shlex.split(commands)[0]
        container_entrypoint = [container_entrypoint]
        container_arguments = shlex.split(commands)[1:]
        
        return container_entrypoint, container_arguments
        

    def run(
            self,
            inputs: Union[Dict[str, str], Dict[str, S3DataSource], Dict[str, FileSystemDataSource]],
            source_code_config: Optional[SourceCodeConfig] = None,
            hyper_parameters: Optional[Dict[str, str]] = None,
            environment: Optional[Dict[str, str]] = None,
            training_run_mode: Optional[TrainingRunMode] = TrainingRunMode.REMOTE,
            wait: bool = True,
            logs: bool = True,
    ) -> TrainingJob:
        """Run a TrainingJob using AWS SageMaker

        Args:
            inputs (Union[Dict[str, str], Dict[str, S3DataSource], Dict[str, FileSystemDataSource]]): 
                A dictionary of input data sources. The key is the channel name and the value is an S3 path, S3DataSource object, or FileSystemDataSource object.,
            source_code_config (Optional[SourceCodeConfig]):
                The container script configuration. This includes the commands to execute in the training job container entry point and the source directory containing the source code to be used in the training job container.
                If source_dir is provided, it will set as the "code" input channel in the training job.
                References to files in the source_dir within the training container should be relative to the source_dir and in the format "opt/ml/input/data/code/<relative_path_to_file>".
            hyper_parameters (Optional[Dict[str, str]]): 
                A dictionary of hyperparameters that will be passed to the training job container.
            environment (Optional[Dict[str, str]]): 
                A dictionary of environment variables that will be passed to the training job container.
            training_run_mode (Optional[TrainingRunMode]):
                The run mode for the training job. Defaults to TrainingRunMode.REMOTE.
            wait (bool, optional):
                Parameter to determine whether to wait until the training job to completes. Defaults to True.
            logs (bool, optional):
                Parameter to determine whether to print training logs while waiting for training job to complete. Defaults to True.

        Raises:
            ValueError: If the inputs dictionary contains invalid S3 paths.

        Returns:
            TrainingJob: A TrainingJob object that represents the training job.
        """
        
        if training_run_mode == TrainingRunMode.LOCAL:
            logger.warning("Local training is not supported yet. Running training remotely.")
    
        create_input_args = {
            "training_job_name": _get_unique_name(self.base_name),
            "role_arn": self.role,
            "output_data_config": self.output_data_config,
            "resource_config": self.resource_config,
            "stopping_condition": self.stopping_condition
        }
    
        source_code_input_channel = None
        container_entrypoint = None
        container_arguments = None
        source_code_config = source_code_config or self.source_code_config
        if source_code_config:
            source_code_input_channel = self._get_container_source_code_channel(source_code_config)
            container_entrypoint, container_arguments = self.get_entrypoint_and_arguments(source_code_config)
        
        input_data_configs = self._get_input_data_config(inputs)
        
        if source_code_input_channel:
            input_data_configs.append(source_code_input_channel)
        

        create_input_args["algorithm_specification"] = AlgorithmSpecification(
            training_image=self.training_image,
            algorithm_name=self.algorithm_name,
            training_input_mode=self.training_input_mode,
            container_arguments=container_arguments,
            container_entrypoint=container_entrypoint
        )
        create_input_args["input_data_config"] = input_data_configs
        create_input_args["hyper_parameters"] = hyper_parameters or self.hyper_parameters
        
        default_env = {}
        for input_config in input_data_configs:
            default_env[f"SM_CHANNEL_{input_config.channel_name.upper()}"] = f"/opt/ml/input/data/{input_config.channel_name}"
        
        if create_input_args["hyper_parameters"]:
            for hyper_parameter, value in create_input_args["hyper_parameters"].items():
                default_env[f"SM_HP_{hyper_parameter.upper()}"] = value
        default_env["SM_MODEL_DIR"] = "/opt/ml/model"
        
        if environment:
            default_env.update(environment)
        elif self.environment:
            default_env.update(self.environment)
        
        create_input_args["environment"] = default_env
        create_input_args["enable_network_isolation"] = False
        create_input_args["enable_inter_container_traffic_encryption"] = False
        create_input_args["enable_managed_spot_training"] = False

        training_job = TrainingJob.create(**create_input_args)
        
        if wait:
            training_job.wait(logs=logs)
        if logs and not wait:
            logger.warning("Logs are only available when wait=True. Set wait=True to see logs.")
            
        return training_job
    
    
    def _get_input_data_config(self, inputs: Dict[str, str]) -> List[Channel]:
        input_data_configs = []
        for input_name, input_source in inputs.items():
            if isinstance(input_source, S3DataSource):
                input_data_configs.append(
                    Channel(
                        channel_name=input_name,
                        data_source=DataSource(
                            s3_data_source=input_source
                        ),
                        input_mode="File"
                    )
                )
            elif isinstance(input_source, FileSystemDataSource):
                input_data_configs.append(
                    Channel(
                        channel_name=input_name,
                        data_source=DataSource(
                            file_system_data_source=input_source
                        )
                    )
                )
            elif isinstance(input_source, str) and _is_valid_s3_uri(input_source):
                if not _is_valid_s3_uri(input_source):
                    raise ValueError(f"Invalid S3 path for input [{input_name}: {input_source}]")
                input_data_configs.append(
                    Channel(
                        channel_name=input_name,
                        data_source=DataSource(
                            s3_data_source=S3DataSource(
                                s3_data_type="S3Prefix",
                                s3_uri=input_source
                            )
                        ),
                        input_mode="File"
                    )
                )
            elif isinstance(input_source, str) and _is_valid_path(input_source):
                source_code_s3_uri = self.session.upload_data(
                    path=input_source,
                    bucket=self.session.default_bucket(),
                    key_prefix=f"{self.base_name}/input/{input_name}"
                )                
                input_data_configs.append(
                    Channel(
                        channel_name=input_name,
                        data_source=DataSource(
                            s3_data_source=S3DataSource(
                                s3_data_type="S3Prefix",
                                s3_uri=source_code_s3_uri
                            )
                        ),
                        input_mode="File"
                    )
                )
            else:
                if not _is_valid_s3_uri(input_source):
                    raise ValueError(f"Invalid S3 directory uri path: {input_source}")
                if not _is_valid_path(input_source):
                    raise ValueError(f"Invalid local directory path: {input_source}")
                raise ValueError(f"Invalid input source: {input_source}")
                
        return input_data_configs

    
    def _get_container_source_code_channel(self, source_code_config: SourceCodeConfig) -> Channel:
        source_code_input_channel = None
        if isinstance(source_code_config.source_dir, S3DataSource):
            source_code_input_channel = Channel(
                channel_name="code",
                data_source=DataSource(
                    s3_data_source=source_code_config.source_dir
                ),
                input_mode="File"
            )
        if isinstance(source_code_config.source_dir, str) and  _is_valid_s3_uri(source_code_config.source_dir, path_type="Directory"):
            source_code_input_channel = Channel(
                channel_name="code",
                data_source=DataSource(
                    s3_data_source=S3DataSource(
                        s3_data_type="S3Prefix",
                        s3_uri=source_code_config.source_dir,
                        s3_data_distribution_type="FullyReplicated"
                    )
                ),
                input_mode="File"
            )
        elif isinstance(source_code_config.source_dir, str) and _is_valid_path(source_code_config.source_dir, path_type="Directory"):
            
            source_code_s3_uri = self.session.upload_data(
                path=source_code_config.source_dir,
                bucket=self.session.default_bucket(),
                key_prefix=f"{self.base_name}/input/code"
            )
            source_code_input_channel = Channel(
                channel_name="code",
                data_source=DataSource(
                    s3_data_source=S3DataSource(
                        s3_data_type="S3Prefix",
                        s3_uri=source_code_s3_uri,
                        s3_data_distribution_type="FullyReplicated"
                    )
                ),
                input_mode="File"
            )
        else:
            if not _is_valid_s3_uri(source_code_config.source_dir, path_type="Directory"):
                raise ValueError(f"Invalid S3 directory uri path: {source_code_config.source_dir}")
            if not _is_valid_path(source_code_config.source_dir, path_type="Directory"):
                raise ValueError(f"Invalid local directory path: {source_code_config.source_dir}")

            raise ValueError(f"Invalid source_dir: {source_code_config.source_dir}")
            
        return source_code_input_channel
