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
from typing import List, Dict, Optional, Any


class Base(BaseModel):
    def serialize(self):
        result = {}
        for attr, value in self.__dict__.items():
            if isinstance(value, Unassigned):
                continue

            components = attr.split("_")
            pascal_attr = "".join(x.title() for x in components[0:])
            if isinstance(value, List):
                result[pascal_attr] = self._serialize_list(value)
            elif isinstance(value, Dict):
                result[pascal_attr] = self._serialize_dict(value)
            elif hasattr(value, "serialize"):
                result[pascal_attr] = value.serialize()
            else:
                result[pascal_attr] = value
        return result

    def _serialize_list(self, value: List):
        return [v.serialize() if hasattr(v, "serialize") else v for v in value]

    def _serialize_dict(self, value: Dict):
        return {
            k: v.serialize() if hasattr(v, "serialize") else v for k, v in value.items()
        }


class Unassigned:
    """A custom type used to signify an undefined optional argument."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class ActionSource(Base):
    """
    ActionSource
         <p>A structure describing the source of an action.</p>

        Attributes
       ----------------------
       source_uri: 	 <p>The URI of the source.</p>
       source_type: 	 <p>The type of the source.</p>
       source_id: 	 <p>The ID of the source.</p>
    """

    source_uri: str
    source_type: Optional[str] = Unassigned()
    source_id: Optional[str] = Unassigned()


class ActionSummary(Base):
    """
    ActionSummary
         <p>Lists the properties of an <i>action</i>. An action represents an action or activity. Some examples are a workflow step and a model deployment. Generally, an action involves at least one input artifact or output artifact.</p>

        Attributes
       ----------------------
       action_arn: 	 <p>The Amazon Resource Name (ARN) of the action.</p>
       action_name: 	 <p>The name of the action.</p>
       source: 	 <p>The source of the action.</p>
       action_type: 	 <p>The type of the action.</p>
       status: 	 <p>The status of the action.</p>
       creation_time: 	 <p>When the action was created.</p>
       last_modified_time: 	 <p>When the action was last modified.</p>
    """

    action_arn: Optional[str] = Unassigned()
    action_name: Optional[str] = Unassigned()
    source: Optional[ActionSource] = Unassigned()
    action_type: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class Tag(Base):
    """
    Tag
         <p>A tag object that consists of a key and an optional value, used to manage metadata for SageMaker Amazon Web Services resources.</p> <p>You can add tags to notebook instances, training jobs, hyperparameter tuning jobs, batch transform jobs, models, labeling jobs, work teams, endpoint configurations, and endpoints. For more information on adding tags to SageMaker resources, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AddTags.html">AddTags</a>.</p> <p>For more information on adding metadata to your Amazon Web Services resources with tagging, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a>. For advice on best practices for managing Amazon Web Services resources with tagging, see <a href="https://d1.awsstatic.com/whitepapers/aws-tagging-best-practices.pdf">Tagging Best Practices: Implement an Effective Amazon Web Services Resource Tagging Strategy</a>.</p>

        Attributes
       ----------------------
       key: 	 <p>The tag key. Tag keys must be unique per resource.</p>
       value: 	 <p>The tag value.</p>
    """

    key: str
    value: str


class ModelAccessConfig(Base):
    """
    ModelAccessConfig
         <p>The access configuration file to control access to the ML model. You can explicitly accept the model end-user license agreement (EULA) within the <code>ModelAccessConfig</code>.</p> <ul> <li> <p>If you are a Jumpstart user, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-foundation-models-choose.html#jumpstart-foundation-models-choose-eula">End-user license agreements</a> section for more details on accepting the EULA.</p> </li> <li> <p>If you are an AutoML user, see the <i>Optional Parameters</i> section of <i>Create an AutoML job to fine-tune text generation models using the API</i> for details on <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-create-experiment-finetune-llms.html#autopilot-llms-finetuning-api-optional-params">How to set the EULA acceptance when fine-tuning a model using the AutoML API</a>.</p> </li> </ul>

        Attributes
       ----------------------
       accept_eula: 	 <p>Specifies agreement to the model end-user license agreement (EULA). The <code>AcceptEula</code> value must be explicitly defined as <code>True</code> in order to accept the EULA that this model requires. You are responsible for reviewing and complying with any applicable license terms and making sure they are acceptable for your use case before downloading or using a model.</p>
    """

    accept_eula: bool


class S3ModelDataSource(Base):
    """
    S3ModelDataSource
         <p>Specifies the S3 location of ML model data to deploy.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>Specifies the S3 path of ML model data to deploy.</p>
       s3_data_type: 	 <p>Specifies the type of ML model data to deploy.</p> <p>If you choose <code>S3Prefix</code>, <code>S3Uri</code> identifies a key name prefix. SageMaker uses all objects that match the specified key name prefix as part of the ML model data to deploy. A valid key name prefix identified by <code>S3Uri</code> always ends with a forward slash (/).</p> <p>If you choose <code>S3Object</code>, <code>S3Uri</code> identifies an object that is the ML model data to deploy.</p>
       compression_type: 	 <p>Specifies how the ML model data is prepared.</p> <p>If you choose <code>Gzip</code> and choose <code>S3Object</code> as the value of <code>S3DataType</code>, <code>S3Uri</code> identifies an object that is a gzip-compressed TAR archive. SageMaker will attempt to decompress and untar the object during model deployment.</p> <p>If you choose <code>None</code> and chooose <code>S3Object</code> as the value of <code>S3DataType</code>, <code>S3Uri</code> identifies an object that represents an uncompressed ML model to deploy.</p> <p>If you choose None and choose <code>S3Prefix</code> as the value of <code>S3DataType</code>, <code>S3Uri</code> identifies a key name prefix, under which all objects represents the uncompressed ML model to deploy.</p> <p>If you choose None, then SageMaker will follow rules below when creating model data files under /opt/ml/model directory for use by your inference code:</p> <ul> <li> <p>If you choose <code>S3Object</code> as the value of <code>S3DataType</code>, then SageMaker will split the key of the S3 object referenced by <code>S3Uri</code> by slash (/), and use the last part as the filename of the file holding the content of the S3 object.</p> </li> <li> <p>If you choose <code>S3Prefix</code> as the value of <code>S3DataType</code>, then for each S3 object under the key name pefix referenced by <code>S3Uri</code>, SageMaker will trim its key by the prefix, and use the remainder as the path (relative to <code>/opt/ml/model</code>) of the file holding the content of the S3 object. SageMaker will split the remainder by slash (/), using intermediate parts as directory names and the last part as filename of the file holding the content of the S3 object.</p> </li> <li> <p>Do not use any of the following as file names or directory names:</p> <ul> <li> <p>An empty or blank string</p> </li> <li> <p>A string which contains null bytes</p> </li> <li> <p>A string longer than 255 bytes</p> </li> <li> <p>A single dot (<code>.</code>)</p> </li> <li> <p>A double dot (<code>..</code>)</p> </li> </ul> </li> <li> <p>Ambiguous file names will result in model deployment failure. For example, if your uncompressed ML model consists of two S3 objects <code>s3://mybucket/model/weights</code> and <code>s3://mybucket/model/weights/part1</code> and you specify <code>s3://mybucket/model/</code> as the value of <code>S3Uri</code> and <code>S3Prefix</code> as the value of <code>S3DataType</code>, then it will result in name clash between <code>/opt/ml/model/weights</code> (a regular file) and <code>/opt/ml/model/weights/</code> (a directory).</p> </li> <li> <p>Do not organize the model artifacts in <a href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-folders.html">S3 console using folders</a>. When you create a folder in S3 console, S3 creates a 0-byte object with a key set to the folder name you provide. They key of the 0-byte object ends with a slash (/) which violates SageMaker restrictions on model artifact file names, leading to model deployment failure. </p> </li> </ul>
       model_access_config: 	 <p>Specifies the access configuration file for the ML model. You can explicitly accept the model end-user license agreement (EULA) within the <code>ModelAccessConfig</code>. You are responsible for reviewing and complying with any applicable license terms and making sure they are acceptable for your use case before downloading or using a model.</p>
    """

    s3_uri: str
    s3_data_type: str
    compression_type: str
    model_access_config: Optional[ModelAccessConfig] = Unassigned()


class ModelDataSource(Base):
    """
    ModelDataSource
         <p>Specifies the location of ML model data to deploy. If specified, you must specify one and only one of the available data sources.</p>

        Attributes
       ----------------------
       s3_data_source: 	 <p>Specifies the S3 location of ML model data to deploy.</p>
    """

    s3_data_source: Optional[S3ModelDataSource] = Unassigned()


class ModelInput(Base):
    """
    ModelInput
         <p>Input object for the model.</p>

        Attributes
       ----------------------
       data_input_config: 	 <p>The input configuration object for the model.</p>
    """

    data_input_config: str


class AdditionalS3DataSource(Base):
    """
    AdditionalS3DataSource
         <p>A data source used for training or inference that is in addition to the input dataset or model data.</p>

        Attributes
       ----------------------
       s3_data_type: 	 <p>The data type of the additional data source that you specify for use in inference or training. </p>
       s3_uri: 	 <p>The uniform resource identifier (URI) used to identify an additional data source used in inference or training.</p>
       compression_type: 	 <p>The type of compression used for an additional data source used in inference or training. Specify <code>None</code> if your additional data source is not compressed.</p>
    """

    s3_data_type: str
    s3_uri: str
    compression_type: Optional[str] = Unassigned()


class ModelPackageContainerDefinition(Base):
    """
    ModelPackageContainerDefinition
         <p>Describes the Docker container for the model package.</p>

        Attributes
       ----------------------
       container_hostname: 	 <p>The DNS host name for the Docker container.</p>
       image: 	 <p>The Amazon EC2 Container Registry (Amazon ECR) path where inference code is stored.</p> <p>If you are using your own custom algorithm instead of an algorithm provided by SageMaker, the inference code must meet SageMaker requirements. SageMaker supports both <code>registry/repository[:tag]</code> and <code>registry/repository[@digest]</code> image path formats. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html">Using Your Own Algorithms with Amazon SageMaker</a>.</p>
       image_digest: 	 <p>An MD5 hash of the training algorithm that identifies the Docker image used for training.</p>
       model_data_url: 	 <p>The Amazon S3 path where the model artifacts, which result from model training, are stored. This path must point to a single <code>gzip</code> compressed tar archive (<code>.tar.gz</code> suffix).</p> <note> <p>The model artifacts must be in an S3 bucket that is in the same region as the model package.</p> </note>
       model_data_source: 	 <p>Specifies the location of ML model data to deploy during endpoint creation.</p>
       product_id: 	 <p>The Amazon Web Services Marketplace product ID of the model package.</p>
       environment: 	 <p>The environment variables to set in the Docker container. Each key and value in the <code>Environment</code> string to string map can have length of up to 1024. We support up to 16 entries in the map.</p>
       model_input: 	 <p>A structure with Model Input details.</p>
       framework: 	 <p>The machine learning framework of the model package container image.</p>
       framework_version: 	 <p>The framework version of the Model Package Container Image.</p>
       nearest_model_name: 	 <p>The name of a pre-trained machine learning benchmarked by Amazon SageMaker Inference Recommender model that matches your model. You can find a list of benchmarked models by calling <code>ListModelMetadata</code>.</p>
       additional_s3_data_source: 	 <p>The additional data source that is used during inference in the Docker container for your model package.</p>
    """

    image: str
    container_hostname: Optional[str] = Unassigned()
    image_digest: Optional[str] = Unassigned()
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()
    product_id: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    model_input: Optional[ModelInput] = Unassigned()
    framework: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()
    nearest_model_name: Optional[str] = Unassigned()
    additional_s3_data_source: Optional[AdditionalS3DataSource] = Unassigned()


class AdditionalInferenceSpecificationDefinition(Base):
    """
    AdditionalInferenceSpecificationDefinition
         <p>A structure of additional Inference Specification. Additional Inference Specification specifies details about inference jobs that can be run with models based on this model package</p>

        Attributes
       ----------------------
       name: 	 <p>A unique name to identify the additional inference specification. The name must be unique within the list of your additional inference specifications for a particular model package.</p>
       description: 	 <p>A description of the additional Inference specification</p>
       containers: 	 <p>The Amazon ECR registry path of the Docker image that contains the inference code.</p>
       supported_transform_instance_types: 	 <p>A list of the instance types on which a transformation job can be run or on which an endpoint can be deployed.</p>
       supported_realtime_inference_instance_types: 	 <p>A list of the instance types that are used to generate inferences in real-time.</p>
       supported_content_types: 	 <p>The supported MIME types for the input data.</p>
       supported_response_m_i_m_e_types: 	 <p>The supported MIME types for the output data.</p>
    """

    name: str
    containers: List[ModelPackageContainerDefinition]
    description: Optional[str] = Unassigned()
    supported_transform_instance_types: Optional[List[str]] = Unassigned()
    supported_realtime_inference_instance_types: Optional[List[str]] = Unassigned()
    supported_content_types: Optional[List[str]] = Unassigned()
    supported_response_m_i_m_e_types: Optional[List[str]] = Unassigned()


class AgentVersion(Base):
    """
    AgentVersion
         <p>Edge Manager agent version.</p>

        Attributes
       ----------------------
       version: 	 <p>Version of the agent.</p>
       agent_count: 	 <p>The number of Edge Manager agents.</p>
    """

    version: str
    agent_count: int


class Alarm(Base):
    """
    Alarm
         <p>An Amazon CloudWatch alarm configured to monitor metrics on an endpoint.</p>

        Attributes
       ----------------------
       alarm_name: 	 <p>The name of a CloudWatch alarm in your account.</p>
    """

    alarm_name: Optional[str] = Unassigned()


class MetricDefinition(Base):
    """
    MetricDefinition
         <p>Specifies a metric that the training algorithm writes to <code>stderr</code> or <code>stdout</code>. You can view these logs to understand how your training job performs and check for any errors encountered during training. SageMaker hyperparameter tuning captures all defined metrics. Specify one of the defined metrics to use as an objective metric using the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTrainingJobDefinition.html#sagemaker-Type-HyperParameterTrainingJobDefinition-TuningObjective">TuningObjective</a> parameter in the <code>HyperParameterTrainingJobDefinition</code> API to evaluate job performance during hyperparameter tuning.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the metric.</p>
       regex: 	 <p>A regular expression that searches the output of a training job and gets the value of the metric. For more information about using regular expressions to define metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-metrics-variables.html">Defining metrics and environment variables</a>.</p>
    """

    name: str
    regex: str


class TrainingRepositoryAuthConfig(Base):
    """
    TrainingRepositoryAuthConfig
         <p>An object containing authentication information for a private Docker registry.</p>

        Attributes
       ----------------------
       training_repository_credentials_provider_arn: 	 <p>The Amazon Resource Name (ARN) of an Amazon Web Services Lambda function used to give SageMaker access credentials to your private Docker registry.</p>
    """

    training_repository_credentials_provider_arn: str


class TrainingImageConfig(Base):
    """
    TrainingImageConfig
         <p>The configuration to use an image from a private Docker registry for a training job.</p>

        Attributes
       ----------------------
       training_repository_access_mode: 	 <p>The method that your training job will use to gain access to the images in your private Docker registry. For access to an image in a private Docker registry, set to <code>Vpc</code>.</p>
       training_repository_auth_config: 	 <p>An object containing authentication information for a private Docker registry containing your training images.</p>
    """

    training_repository_access_mode: str
    training_repository_auth_config: Optional[TrainingRepositoryAuthConfig] = (
        Unassigned()
    )


class AlgorithmSpecification(Base):
    """
    AlgorithmSpecification
         <p>Specifies the training algorithm to use in a <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html">CreateTrainingJob</a> request.</p> <p>For more information about algorithms provided by SageMaker, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html">Algorithms</a>. For information about using your own algorithms, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html">Using Your Own Algorithms with Amazon SageMaker</a>. </p>

        Attributes
       ----------------------
       training_image: 	 <p>The registry path of the Docker image that contains the training algorithm. For information about docker registry paths for SageMaker built-in algorithms, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-algo-docker-registry-paths.html">Docker Registry Paths and Example Code</a> in the <i>Amazon SageMaker developer guide</i>. SageMaker supports both <code>registry/repository[:tag]</code> and <code>registry/repository[@digest]</code> image path formats. For more information about using your custom training container, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html">Using Your Own Algorithms with Amazon SageMaker</a>.</p> <note> <p>You must specify either the algorithm name to the <code>AlgorithmName</code> parameter or the image URI of the algorithm container to the <code>TrainingImage</code> parameter.</p> <p>For more information, see the note in the <code>AlgorithmName</code> parameter description.</p> </note>
       algorithm_name: 	 <p>The name of the algorithm resource to use for the training job. This must be an algorithm resource that you created or subscribe to on Amazon Web Services Marketplace.</p> <note> <p>You must specify either the algorithm name to the <code>AlgorithmName</code> parameter or the image URI of the algorithm container to the <code>TrainingImage</code> parameter.</p> <p>Note that the <code>AlgorithmName</code> parameter is mutually exclusive with the <code>TrainingImage</code> parameter. If you specify a value for the <code>AlgorithmName</code> parameter, you can't specify a value for <code>TrainingImage</code>, and vice versa.</p> <p>If you specify values for both parameters, the training job might break; if you don't specify any value for both parameters, the training job might raise a <code>null</code> error.</p> </note>
       training_input_mode
       metric_definitions: 	 <p>A list of metric definition objects. Each object specifies the metric name and regular expressions used to parse algorithm logs. SageMaker publishes each metric to Amazon CloudWatch.</p>
       enable_sage_maker_metrics_time_series: 	 <p>To generate and save time-series metrics during training, set to <code>true</code>. The default is <code>false</code> and time-series metrics aren't generated except in the following cases:</p> <ul> <li> <p>You use one of the SageMaker built-in algorithms</p> </li> <li> <p>You use one of the following <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/pre-built-containers-frameworks-deep-learning.html">Prebuilt SageMaker Docker Images</a>:</p> <ul> <li> <p>Tensorflow (version &gt;= 1.15)</p> </li> <li> <p>MXNet (version &gt;= 1.6)</p> </li> <li> <p>PyTorch (version &gt;= 1.3)</p> </li> </ul> </li> <li> <p>You specify at least one <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_MetricDefinition.html">MetricDefinition</a> </p> </li> </ul>
       container_entrypoint: 	 <p>The <a href="https://docs.docker.com/engine/reference/builder/">entrypoint script for a Docker container</a> used to run a training job. This script takes precedence over the default train processing instructions. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo-dockerfile.html">How Amazon SageMaker Runs Your Training Image</a> for more information.</p>
       container_arguments: 	 <p>The arguments for a container used to run a training job. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-training-algo-dockerfile.html">How Amazon SageMaker Runs Your Training Image</a> for additional information.</p>
       training_image_config: 	 <p>The configuration to use an image from a private Docker registry for a training job.</p>
    """

    training_input_mode: str
    training_image: Optional[str] = Unassigned()
    algorithm_name: Optional[str] = Unassigned()
    metric_definitions: Optional[List[MetricDefinition]] = Unassigned()
    enable_sage_maker_metrics_time_series: Optional[bool] = Unassigned()
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_arguments: Optional[List[str]] = Unassigned()
    training_image_config: Optional[TrainingImageConfig] = Unassigned()


class AlgorithmStatusItem(Base):
    """
    AlgorithmStatusItem
         <p>Represents the overall status of an algorithm.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the algorithm for which the overall status is being reported.</p>
       status: 	 <p>The current status.</p>
       failure_reason: 	 <p>if the overall status is <code>Failed</code>, the reason for the failure.</p>
    """

    name: str
    status: str
    failure_reason: Optional[str] = Unassigned()


class AlgorithmStatusDetails(Base):
    """
    AlgorithmStatusDetails
         <p>Specifies the validation and image scan statuses of the algorithm.</p>

        Attributes
       ----------------------
       validation_statuses: 	 <p>The status of algorithm validation.</p>
       image_scan_statuses: 	 <p>The status of the scan of the algorithm's Docker image container.</p>
    """

    validation_statuses: Optional[List[AlgorithmStatusItem]] = Unassigned()
    image_scan_statuses: Optional[List[AlgorithmStatusItem]] = Unassigned()


class AlgorithmSummary(Base):
    """
    AlgorithmSummary
         <p>Provides summary information about an algorithm.</p>

        Attributes
       ----------------------
       algorithm_name: 	 <p>The name of the algorithm that is described by the summary.</p>
       algorithm_arn: 	 <p>The Amazon Resource Name (ARN) of the algorithm.</p>
       algorithm_description: 	 <p>A brief description of the algorithm.</p>
       creation_time: 	 <p>A timestamp that shows when the algorithm was created.</p>
       algorithm_status: 	 <p>The overall status of the algorithm.</p>
    """

    algorithm_name: str
    algorithm_arn: str
    creation_time: datetime.datetime
    algorithm_status: str
    algorithm_description: Optional[str] = Unassigned()


class S3DataSource(Base):
    """
    S3DataSource
         <p>Describes the S3 data source.</p> <p>Your input bucket must be in the same Amazon Web Services region as your training job.</p>

        Attributes
       ----------------------
       s3_data_type: 	 <p>If you choose <code>S3Prefix</code>, <code>S3Uri</code> identifies a key name prefix. SageMaker uses all objects that match the specified key name prefix for model training. </p> <p>If you choose <code>ManifestFile</code>, <code>S3Uri</code> identifies an object that is a manifest file containing a list of object keys that you want SageMaker to use for model training. </p> <p>If you choose <code>AugmentedManifestFile</code>, S3Uri identifies an object that is an augmented manifest file in JSON lines format. This file contains the data you want to use for model training. <code>AugmentedManifestFile</code> can only be used if the Channel's input mode is <code>Pipe</code>.</p>
       s3_uri: 	 <p>Depending on the value specified for the <code>S3DataType</code>, identifies either a key name prefix or a manifest. For example: </p> <ul> <li> <p> A key name prefix might look like this: <code>s3://bucketname/exampleprefix/</code> </p> </li> <li> <p> A manifest might look like this: <code>s3://bucketname/example.manifest</code> </p> <p> A manifest is an S3 object which is a JSON file consisting of an array of elements. The first element is a prefix which is followed by one or more suffixes. SageMaker appends the suffix elements to the prefix to get a full set of <code>S3Uri</code>. Note that the prefix must be a valid non-empty <code>S3Uri</code> that precludes users from specifying a manifest whose individual <code>S3Uri</code> is sourced from different S3 buckets.</p> <p> The following code example shows a valid manifest format: </p> <p> <code>[ {"prefix": "s3://customer_bucket/some/prefix/"},</code> </p> <p> <code> "relative/path/to/custdata-1",</code> </p> <p> <code> "relative/path/custdata-2",</code> </p> <p> <code> ...</code> </p> <p> <code> "relative/path/custdata-N"</code> </p> <p> <code>]</code> </p> <p> This JSON is equivalent to the following <code>S3Uri</code> list:</p> <p> <code>s3://customer_bucket/some/prefix/relative/path/to/custdata-1</code> </p> <p> <code>s3://customer_bucket/some/prefix/relative/path/custdata-2</code> </p> <p> <code>...</code> </p> <p> <code>s3://customer_bucket/some/prefix/relative/path/custdata-N</code> </p> <p>The complete set of <code>S3Uri</code> in this manifest is the input data for the channel for this data source. The object that each <code>S3Uri</code> points to must be readable by the IAM role that SageMaker uses to perform tasks on your behalf. </p> </li> </ul> <p>Your input bucket must be located in same Amazon Web Services region as your training job.</p>
       s3_data_distribution_type: 	 <p>If you want SageMaker to replicate the entire dataset on each ML compute instance that is launched for model training, specify <code>FullyReplicated</code>. </p> <p>If you want SageMaker to replicate a subset of data on each ML compute instance that is launched for model training, specify <code>ShardedByS3Key</code>. If there are <i>n</i> ML compute instances launched for a training job, each instance gets approximately 1/<i>n</i> of the number of S3 objects. In this case, model training on each machine uses only the subset of training data. </p> <p>Don't choose more ML compute instances for training than available S3 objects. If you do, some nodes won't get any data and you will pay for nodes that aren't getting any training data. This applies in both File and Pipe modes. Keep this in mind when developing algorithms. </p> <p>In distributed training, where you use multiple ML compute EC2 instances, you might choose <code>ShardedByS3Key</code>. If the algorithm requires copying training data to the ML storage volume (when <code>TrainingInputMode</code> is set to <code>File</code>), this copies 1/<i>n</i> of the number of objects. </p>
       attribute_names: 	 <p>A list of one or more attribute names to use that are found in a specified augmented manifest file.</p>
       instance_group_names: 	 <p>A list of names of instance groups that get data from the S3 data source.</p>
    """

    s3_data_type: str
    s3_uri: str
    s3_data_distribution_type: Optional[str] = Unassigned()
    attribute_names: Optional[List[str]] = Unassigned()
    instance_group_names: Optional[List[str]] = Unassigned()


class FileSystemDataSource(Base):
    """
    FileSystemDataSource
         <p>Specifies a file system data source for a channel.</p>

        Attributes
       ----------------------
       file_system_id: 	 <p>The file system id.</p>
       file_system_access_mode: 	 <p>The access mode of the mount of the directory associated with the channel. A directory can be mounted either in <code>ro</code> (read-only) or <code>rw</code> (read-write) mode.</p>
       file_system_type: 	 <p>The file system type. </p>
       directory_path: 	 <p>The full path to the directory to associate with the channel.</p>
    """

    file_system_id: str
    file_system_access_mode: str
    file_system_type: str
    directory_path: str


class DataSource(Base):
    """
    DataSource
         <p>Describes the location of the channel data.</p>

        Attributes
       ----------------------
       s3_data_source: 	 <p>The S3 location of the data source that is associated with a channel.</p>
       file_system_data_source: 	 <p>The file system that is associated with a channel.</p>
    """

    s3_data_source: Optional[S3DataSource] = Unassigned()
    file_system_data_source: Optional[FileSystemDataSource] = Unassigned()


class ShuffleConfig(Base):
    """
    ShuffleConfig
         <p>A configuration for a shuffle option for input data in a channel. If you use <code>S3Prefix</code> for <code>S3DataType</code>, the results of the S3 key prefix matches are shuffled. If you use <code>ManifestFile</code>, the order of the S3 object references in the <code>ManifestFile</code> is shuffled. If you use <code>AugmentedManifestFile</code>, the order of the JSON lines in the <code>AugmentedManifestFile</code> is shuffled. The shuffling order is determined using the <code>Seed</code> value.</p> <p>For Pipe input mode, when <code>ShuffleConfig</code> is specified shuffling is done at the start of every epoch. With large datasets, this ensures that the order of the training data is different for each epoch, and it helps reduce bias and possible overfitting. In a multi-node training job when <code>ShuffleConfig</code> is combined with <code>S3DataDistributionType</code> of <code>ShardedByS3Key</code>, the data is shuffled across nodes so that the content sent to a particular node on the first epoch might be sent to a different node on the second epoch.</p>

        Attributes
       ----------------------
       seed: 	 <p>Determines the shuffling order in <code>ShuffleConfig</code> value.</p>
    """

    seed: int


class Channel(Base):
    """
    Channel
         <p>A channel is a named input source that training algorithms can consume. </p>

        Attributes
       ----------------------
       channel_name: 	 <p>The name of the channel. </p>
       data_source: 	 <p>The location of the channel data.</p>
       content_type: 	 <p>The MIME type of the data.</p>
       compression_type: 	 <p>If training data is compressed, the compression type. The default value is <code>None</code>. <code>CompressionType</code> is used only in Pipe input mode. In File mode, leave this field unset or set it to None.</p>
       record_wrapper_type: 	 <p/> <p>Specify RecordIO as the value when input data is in raw format but the training algorithm requires the RecordIO format. In this case, SageMaker wraps each individual S3 object in a RecordIO record. If the input data is already in RecordIO format, you don't need to set this attribute. For more information, see <a href="https://mxnet.apache.org/api/architecture/note_data_loading#data-format">Create a Dataset Using RecordIO</a>. </p> <p>In File mode, leave this field unset or set it to None.</p>
       input_mode: 	 <p>(Optional) The input mode to use for the data channel in a training job. If you don't set a value for <code>InputMode</code>, SageMaker uses the value set for <code>TrainingInputMode</code>. Use this parameter to override the <code>TrainingInputMode</code> setting in a <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AlgorithmSpecification.html">AlgorithmSpecification</a> request when you have a channel that needs a different input mode from the training job's general setting. To download the data from Amazon Simple Storage Service (Amazon S3) to the provisioned ML storage volume, and mount the directory to a Docker volume, use <code>File</code> input mode. To stream data directly from Amazon S3 to the container, choose <code>Pipe</code> input mode.</p> <p>To use a model for incremental training, choose <code>File</code> input model.</p>
       shuffle_config: 	 <p>A configuration for a shuffle option for input data in a channel. If you use <code>S3Prefix</code> for <code>S3DataType</code>, this shuffles the results of the S3 key prefix matches. If you use <code>ManifestFile</code>, the order of the S3 object references in the <code>ManifestFile</code> is shuffled. If you use <code>AugmentedManifestFile</code>, the order of the JSON lines in the <code>AugmentedManifestFile</code> is shuffled. The shuffling order is determined using the <code>Seed</code> value.</p> <p>For Pipe input mode, shuffling is done at the start of every epoch. With large datasets this ensures that the order of the training data is different for each epoch, it helps reduce bias and possible overfitting. In a multi-node training job when ShuffleConfig is combined with <code>S3DataDistributionType</code> of <code>ShardedByS3Key</code>, the data is shuffled across nodes so that the content sent to a particular node on the first epoch might be sent to a different node on the second epoch.</p>
    """

    channel_name: str
    data_source: DataSource
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    record_wrapper_type: Optional[str] = Unassigned()
    input_mode: Optional[str] = Unassigned()
    shuffle_config: Optional[ShuffleConfig] = Unassigned()


class OutputDataConfig(Base):
    """
    OutputDataConfig
         <p>Provides information about how to store model training results (model artifacts).</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that SageMaker uses to encrypt the model artifacts at rest using Amazon S3 server-side encryption. The <code>KmsKeyId</code> can be any of the following formats: </p> <ul> <li> <p>// KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// KMS Key Alias</p> <p> <code>"alias/ExampleAlias"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key Alias</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias"</code> </p> </li> </ul> <p>If you use a KMS key ID or an alias of your KMS key, the SageMaker execution role must include permissions to call <code>kms:Encrypt</code>. If you don't provide a KMS key ID, SageMaker uses the default KMS key for Amazon S3 for your role's account. For more information, see <a href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html">KMS-Managed Encryption Keys</a> in the <i>Amazon Simple Storage Service Developer Guide</i>. If the output data is stored in Amazon S3 Express One Zone, it is encrypted with server-side encryption with Amazon S3 managed keys (SSE-S3). KMS key is not supported for Amazon S3 Express One Zone</p> <p>The KMS key policy must grant permission to the IAM role that you specify in your <code>CreateTrainingJob</code>, <code>CreateTransformJob</code>, or <code>CreateHyperParameterTuningJob</code> requests. For more information, see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html">Using Key Policies in Amazon Web Services KMS</a> in the <i>Amazon Web Services Key Management Service Developer Guide</i>.</p>
       s3_output_path: 	 <p>Identifies the S3 path where you want SageMaker to store the model artifacts. For example, <code>s3://bucket-name/key-name-prefix</code>. </p>
       compression_type: 	 <p>The model output compression type. Select <code>None</code> to output an uncompressed model, recommended for large model outputs. Defaults to gzip.</p>
    """

    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()


class InstanceGroup(Base):
    """
    InstanceGroup
         <p>Defines an instance group for heterogeneous cluster training. When requesting a training job using the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html">CreateTrainingJob</a> API, you can configure multiple instance groups .</p>

        Attributes
       ----------------------
       instance_type: 	 <p>Specifies the instance type of the instance group.</p>
       instance_count: 	 <p>Specifies the number of instances of the instance group.</p>
       instance_group_name: 	 <p>Specifies the name of the instance group.</p>
    """

    instance_type: str
    instance_count: int
    instance_group_name: str


class ResourceConfig(Base):
    """
    ResourceConfig
         <p>Describes the resources, including machine learning (ML) compute instances and ML storage volumes, to use for model training. </p>

        Attributes
       ----------------------
       instance_type: 	 <p>The ML compute instance type. </p> <note> <p>SageMaker Training on Amazon Elastic Compute Cloud (EC2) P4de instances is in preview release starting December 9th, 2022. </p> <p> <a href="http://aws.amazon.com/ec2/instance-types/p4/">Amazon EC2 P4de instances</a> (currently in preview) are powered by 8 NVIDIA A100 GPUs with 80GB high-performance HBM2e GPU memory, which accelerate the speed of training ML models that need to be trained on large datasets of high-resolution data. In this preview release, Amazon SageMaker supports ML training jobs on P4de instances (<code>ml.p4de.24xlarge</code>) to reduce model training time. The <code>ml.p4de.24xlarge</code> instances are available in the following Amazon Web Services Regions. </p> <ul> <li> <p>US East (N. Virginia) (us-east-1)</p> </li> <li> <p>US West (Oregon) (us-west-2)</p> </li> </ul> <p>To request quota limit increase and start using P4de instances, contact the SageMaker Training service team through your account team.</p> </note>
       instance_count: 	 <p>The number of ML compute instances to use. For distributed training, provide a value greater than 1. </p>
       volume_size_in_g_b: 	 <p>The size of the ML storage volume that you want to provision. </p> <p>ML storage volumes store model artifacts and incremental states. Training algorithms might also use the ML storage volume for scratch space. If you want to store the training data in the ML storage volume, choose <code>File</code> as the <code>TrainingInputMode</code> in the algorithm specification. </p> <p>When using an ML instance with <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html#nvme-ssd-volumes">NVMe SSD volumes</a>, SageMaker doesn't provision Amazon EBS General Purpose SSD (gp2) storage. Available storage is fixed to the NVMe-type instance's storage capacity. SageMaker configures storage paths for training datasets, checkpoints, model artifacts, and outputs to use the entire capacity of the instance storage. For example, ML instance families with the NVMe-type instance storage include <code>ml.p4d</code>, <code>ml.g4dn</code>, and <code>ml.g5</code>. </p> <p>When using an ML instance with the EBS-only storage option and without instance storage, you must define the size of EBS volume through <code>VolumeSizeInGB</code> in the <code>ResourceConfig</code> API. For example, ML instance families that use EBS volumes include <code>ml.c5</code> and <code>ml.p2</code>. </p> <p>To look up instance types and their instance storage types and volumes, see <a href="http://aws.amazon.com/ec2/instance-types/">Amazon EC2 Instance Types</a>.</p> <p>To find the default local paths defined by the SageMaker training platform, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-train-storage.html">Amazon SageMaker Training Storage Folders for Training Datasets, Checkpoints, Model Artifacts, and Outputs</a>.</p>
       volume_kms_key_id: 	 <p>The Amazon Web Services KMS key that SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s) that run the training job.</p> <note> <p>Certain Nitro-based instances include local storage, dependent on the instance type. Local storage volumes are encrypted using a hardware module on the instance. You can't request a <code>VolumeKmsKeyId</code> when using an instance type with local storage.</p> <p>For a list of instance types that support local instance storage, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html#instance-store-volumes">Instance Store Volumes</a>.</p> <p>For more information about local instance storage encryption, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html">SSD Instance Store Volumes</a>.</p> </note> <p>The <code>VolumeKmsKeyId</code> can be in any of the following formats:</p> <ul> <li> <p>// KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> </ul>
       keep_alive_period_in_seconds: 	 <p>The duration of time in seconds to retain configured resources in a warm pool for subsequent training jobs.</p>
       instance_groups: 	 <p>The configuration of a heterogeneous cluster in JSON format.</p>
    """

    volume_size_in_g_b: int
    instance_type: Optional[str] = Unassigned()
    instance_count: Optional[int] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    keep_alive_period_in_seconds: Optional[int] = Unassigned()
    instance_groups: Optional[List[InstanceGroup]] = Unassigned()


class StoppingCondition(Base):
    """
    StoppingCondition
         <p>Specifies a limit to how long a model training job or model compilation job can run. It also specifies how long a managed spot training job has to complete. When the job reaches the time limit, SageMaker ends the training or compilation job. Use this API to cap model training costs.</p> <p>To stop a training job, SageMaker sends the algorithm the <code>SIGTERM</code> signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts, so the results of training are not lost. </p> <p>The training algorithms provided by SageMaker automatically save the intermediate results of a model training job when possible. This attempt to save artifacts is only a best effort case as model might not be in a state from which it can be saved. For example, if training has just started, the model might not be ready to save. When saved, this intermediate data is a valid model artifact. You can use it to create a model with <code>CreateModel</code>.</p> <note> <p>The Neural Topic Model (NTM) currently does not support saving intermediate model artifacts. When training NTMs, make sure that the maximum runtime is sufficient for the training job to complete.</p> </note>

        Attributes
       ----------------------
       max_runtime_in_seconds: 	 <p>The maximum length of time, in seconds, that a training or compilation job can run before it is stopped.</p> <p>For compilation jobs, if the job does not complete during this time, a <code>TimeOut</code> error is generated. We recommend starting with 900 seconds and increasing as necessary based on your model.</p> <p>For all other jobs, if the job does not complete during this time, SageMaker ends the job. When <code>RetryStrategy</code> is specified in the job request, <code>MaxRuntimeInSeconds</code> specifies the maximum time for all of the attempts in total, not each individual attempt. The default value is 1 day. The maximum value is 28 days.</p> <p>The maximum time that a <code>TrainingJob</code> can run in total, including any time spent publishing metrics or archiving and uploading models after it has been stopped, is 30 days.</p>
       max_wait_time_in_seconds: 	 <p>The maximum length of time, in seconds, that a managed Spot training job has to complete. It is the amount of time spent waiting for Spot capacity plus the amount of time the job can run. It must be equal to or greater than <code>MaxRuntimeInSeconds</code>. If the job does not complete during this time, SageMaker ends the job.</p> <p>When <code>RetryStrategy</code> is specified in the job request, <code>MaxWaitTimeInSeconds</code> specifies the maximum time for all of the attempts in total, not each individual attempt.</p>
       max_pending_time_in_seconds: 	 <p>The maximum length of time, in seconds, that a training or compilation job can be pending before it is stopped.</p>
    """

    max_runtime_in_seconds: Optional[int] = Unassigned()
    max_wait_time_in_seconds: Optional[int] = Unassigned()
    max_pending_time_in_seconds: Optional[int] = Unassigned()


class TrainingJobDefinition(Base):
    """
    TrainingJobDefinition
         <p>Defines the input needed to run a training job using the algorithm.</p>

        Attributes
       ----------------------
       training_input_mode
       hyper_parameters: 	 <p>The hyperparameters used for the training job.</p>
       input_data_config: 	 <p>An array of <code>Channel</code> objects, each of which specifies an input source.</p>
       output_data_config: 	 <p>the path to the S3 bucket where you want to store model artifacts. SageMaker creates subfolders for the artifacts.</p>
       resource_config: 	 <p>The resources, including the ML compute instances and ML storage volumes, to use for model training.</p>
       stopping_condition: 	 <p>Specifies a limit to how long a model training job can run. It also specifies how long a managed Spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs.</p> <p>To stop a job, SageMaker sends the algorithm the SIGTERM signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts.</p>
    """

    training_input_mode: str
    input_data_config: List[Channel]
    output_data_config: OutputDataConfig
    resource_config: ResourceConfig
    stopping_condition: StoppingCondition
    hyper_parameters: Optional[Dict[str, str]] = Unassigned()


class TransformS3DataSource(Base):
    """
    TransformS3DataSource
         <p>Describes the S3 data source.</p>

        Attributes
       ----------------------
       s3_data_type: 	 <p>If you choose <code>S3Prefix</code>, <code>S3Uri</code> identifies a key name prefix. Amazon SageMaker uses all objects with the specified key name prefix for batch transform. </p> <p>If you choose <code>ManifestFile</code>, <code>S3Uri</code> identifies an object that is a manifest file containing a list of object keys that you want Amazon SageMaker to use for batch transform. </p> <p>The following values are compatible: <code>ManifestFile</code>, <code>S3Prefix</code> </p> <p>The following value is not compatible: <code>AugmentedManifestFile</code> </p>
       s3_uri: 	 <p>Depending on the value specified for the <code>S3DataType</code>, identifies either a key name prefix or a manifest. For example:</p> <ul> <li> <p> A key name prefix might look like this: <code>s3://bucketname/exampleprefix/</code>. </p> </li> <li> <p> A manifest might look like this: <code>s3://bucketname/example.manifest</code> </p> <p> The manifest is an S3 object which is a JSON file with the following format: </p> <p> <code>[ {"prefix": "s3://customer_bucket/some/prefix/"},</code> </p> <p> <code>"relative/path/to/custdata-1",</code> </p> <p> <code>"relative/path/custdata-2",</code> </p> <p> <code>...</code> </p> <p> <code>"relative/path/custdata-N"</code> </p> <p> <code>]</code> </p> <p> The preceding JSON matches the following <code>S3Uris</code>: </p> <p> <code>s3://customer_bucket/some/prefix/relative/path/to/custdata-1</code> </p> <p> <code>s3://customer_bucket/some/prefix/relative/path/custdata-2</code> </p> <p> <code>...</code> </p> <p> <code>s3://customer_bucket/some/prefix/relative/path/custdata-N</code> </p> <p> The complete set of <code>S3Uris</code> in this manifest constitutes the input data for the channel for this datasource. The object that each <code>S3Uris</code> points to must be readable by the IAM role that Amazon SageMaker uses to perform tasks on your behalf.</p> </li> </ul>
    """

    s3_data_type: str
    s3_uri: str


class TransformDataSource(Base):
    """
    TransformDataSource
         <p>Describes the location of the channel data.</p>

        Attributes
       ----------------------
       s3_data_source: 	 <p>The S3 location of the data source that is associated with a channel.</p>
    """

    s3_data_source: TransformS3DataSource


class TransformInput(Base):
    """
    TransformInput
         <p>Describes the input source of a transform job and the way the transform job consumes it.</p>

        Attributes
       ----------------------
       data_source: 	 <p>Describes the location of the channel data, which is, the S3 location of the input data that the model can consume.</p>
       content_type: 	 <p>The multipurpose internet mail extension (MIME) type of the data. Amazon SageMaker uses the MIME type with each http call to transfer data to the transform job.</p>
       compression_type: 	 <p>If your transform data is compressed, specify the compression type. Amazon SageMaker automatically decompresses the data for the transform job accordingly. The default value is <code>None</code>.</p>
       split_type: 	 <p>The method to use to split the transform job's data files into smaller batches. Splitting is necessary when the total size of each object is too large to fit in a single request. You can also use data splitting to improve performance by processing multiple concurrent mini-batches. The default value for <code>SplitType</code> is <code>None</code>, which indicates that input data files are not split, and request payloads contain the entire contents of an input object. Set the value of this parameter to <code>Line</code> to split records on a newline character boundary. <code>SplitType</code> also supports a number of record-oriented binary data formats. Currently, the supported record formats are:</p> <ul> <li> <p>RecordIO</p> </li> <li> <p>TFRecord</p> </li> </ul> <p>When splitting is enabled, the size of a mini-batch depends on the values of the <code>BatchStrategy</code> and <code>MaxPayloadInMB</code> parameters. When the value of <code>BatchStrategy</code> is <code>MultiRecord</code>, Amazon SageMaker sends the maximum number of records in each request, up to the <code>MaxPayloadInMB</code> limit. If the value of <code>BatchStrategy</code> is <code>SingleRecord</code>, Amazon SageMaker sends individual records in each request.</p> <note> <p>Some data formats represent a record as a binary payload wrapped with extra padding bytes. When splitting is applied to a binary data format, padding is removed if the value of <code>BatchStrategy</code> is set to <code>SingleRecord</code>. Padding is not removed if the value of <code>BatchStrategy</code> is set to <code>MultiRecord</code>.</p> <p>For more information about <code>RecordIO</code>, see <a href="https://mxnet.apache.org/api/faq/recordio">Create a Dataset Using RecordIO</a> in the MXNet documentation. For more information about <code>TFRecord</code>, see <a href="https://www.tensorflow.org/guide/data#consuming_tfrecord_data">Consuming TFRecord data</a> in the TensorFlow documentation.</p> </note>
    """

    data_source: TransformDataSource
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    split_type: Optional[str] = Unassigned()


class TransformOutput(Base):
    """
    TransformOutput
         <p>Describes the results of a transform job.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>The Amazon S3 path where you want Amazon SageMaker to store the results of the transform job. For example, <code>s3://bucket-name/key-name-prefix</code>.</p> <p>For every S3 object used as input for the transform job, batch transform stores the transformed data with an .<code>out</code> suffix in a corresponding subfolder in the location in the output prefix. For example, for the input data stored at <code>s3://bucket-name/input-name-prefix/dataset01/data.csv</code>, batch transform stores the transformed data at <code>s3://bucket-name/output-name-prefix/input-name-prefix/data.csv.out</code>. Batch transform doesn't upload partially processed objects. For an input S3 object that contains multiple records, it creates an .<code>out</code> file only if the transform job succeeds on the entire file. When the input contains multiple S3 objects, the batch transform job processes the listed S3 objects and uploads only the output for successfully processed objects. If any object fails in the transform job batch transform marks the job as failed to prompt investigation.</p>
       accept: 	 <p>The MIME type used to specify the output data. Amazon SageMaker uses the MIME type with each http call to transfer data from the transform job.</p>
       assemble_with: 	 <p>Defines how to assemble the results of the transform job as a single S3 object. Choose a format that is most convenient to you. To concatenate the results in binary format, specify <code>None</code>. To add a newline character at the end of every transformed record, specify <code>Line</code>.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt the model artifacts at rest using Amazon S3 server-side encryption. The <code>KmsKeyId</code> can be any of the following formats: </p> <ul> <li> <p>Key ID: <code>1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Key ARN: <code>arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Alias name: <code>alias/ExampleAlias</code> </p> </li> <li> <p>Alias name ARN: <code>arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias</code> </p> </li> </ul> <p>If you don't provide a KMS key ID, Amazon SageMaker uses the default KMS key for Amazon S3 for your role's account. For more information, see <a href="https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html">KMS-Managed Encryption Keys</a> in the <i>Amazon Simple Storage Service Developer Guide.</i> </p> <p>The KMS key policy must grant permission to the IAM role that you specify in your <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateModel.html">CreateModel</a> request. For more information, see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html">Using Key Policies in Amazon Web Services KMS</a> in the <i>Amazon Web Services Key Management Service Developer Guide</i>.</p>
    """

    s3_output_path: str
    accept: Optional[str] = Unassigned()
    assemble_with: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()


class TransformResources(Base):
    """
    TransformResources
         <p>Describes the resources, including ML instance types and ML instance count, to use for transform job.</p>

        Attributes
       ----------------------
       instance_type: 	 <p>The ML compute instance type for the transform job. If you are using built-in algorithms to transform moderately sized datasets, we recommend using ml.m4.xlarge or <code>ml.m5.large</code>instance types.</p>
       instance_count: 	 <p>The number of ML compute instances to use in the transform job. The default value is <code>1</code>, and the maximum is <code>100</code>. For distributed transform jobs, specify a value greater than <code>1</code>.</p>
       volume_kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt model data on the storage volume attached to the ML compute instance(s) that run the batch transform job.</p> <note> <p>Certain Nitro-based instances include local storage, dependent on the instance type. Local storage volumes are encrypted using a hardware module on the instance. You can't request a <code>VolumeKmsKeyId</code> when using an instance type with local storage.</p> <p>For a list of instance types that support local instance storage, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html#instance-store-volumes">Instance Store Volumes</a>.</p> <p>For more information about local instance storage encryption, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html">SSD Instance Store Volumes</a>.</p> </note> <p> The <code>VolumeKmsKeyId</code> can be any of the following formats:</p> <ul> <li> <p>Key ID: <code>1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Key ARN: <code>arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Alias name: <code>alias/ExampleAlias</code> </p> </li> <li> <p>Alias name ARN: <code>arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias</code> </p> </li> </ul>
    """

    instance_type: str
    instance_count: int
    volume_kms_key_id: Optional[str] = Unassigned()


class TransformJobDefinition(Base):
    """
    TransformJobDefinition
         <p>Defines the input needed to run a transform job using the inference specification specified in the algorithm.</p>

        Attributes
       ----------------------
       max_concurrent_transforms: 	 <p>The maximum number of parallel requests that can be sent to each instance in a transform job. The default value is 1.</p>
       max_payload_in_m_b: 	 <p>The maximum payload size allowed, in MB. A payload is the data portion of a record (without metadata).</p>
       batch_strategy: 	 <p>A string that determines the number of records included in a single mini-batch.</p> <p> <code>SingleRecord</code> means only one record is used per mini-batch. <code>MultiRecord</code> means a mini-batch is set to contain as many records that can fit within the <code>MaxPayloadInMB</code> limit.</p>
       environment: 	 <p>The environment variables to set in the Docker container. We support up to 16 key and values entries in the map.</p>
       transform_input: 	 <p>A description of the input source and the way the transform job consumes it.</p>
       transform_output: 	 <p>Identifies the Amazon S3 location where you want Amazon SageMaker to save the results from the transform job.</p>
       transform_resources: 	 <p>Identifies the ML compute instances for the transform job.</p>
    """

    transform_input: TransformInput
    transform_output: TransformOutput
    transform_resources: TransformResources
    max_concurrent_transforms: Optional[int] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    batch_strategy: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class AlgorithmValidationProfile(Base):
    """
    AlgorithmValidationProfile
         <p>Defines a training job and a batch transform job that SageMaker runs to validate your algorithm.</p> <p>The data provided in the validation profile is made available to your buyers on Amazon Web Services Marketplace.</p>

        Attributes
       ----------------------
       profile_name: 	 <p>The name of the profile for the algorithm. The name must have 1 to 63 characters. Valid characters are a-z, A-Z, 0-9, and - (hyphen).</p>
       training_job_definition: 	 <p>The <code>TrainingJobDefinition</code> object that describes the training job that SageMaker runs to validate your algorithm.</p>
       transform_job_definition: 	 <p>The <code>TransformJobDefinition</code> object that describes the transform job that SageMaker runs to validate your algorithm.</p>
    """

    profile_name: str
    training_job_definition: TrainingJobDefinition
    transform_job_definition: Optional[TransformJobDefinition] = Unassigned()


class AlgorithmValidationSpecification(Base):
    """
    AlgorithmValidationSpecification
         <p>Specifies configurations for one or more training jobs that SageMaker runs to test the algorithm.</p>

        Attributes
       ----------------------
       validation_role: 	 <p>The IAM roles that SageMaker uses to run the training jobs.</p>
       validation_profiles: 	 <p>An array of <code>AlgorithmValidationProfile</code> objects, each of which specifies a training job and batch transform job that SageMaker runs to validate your algorithm.</p>
    """

    validation_role: str
    validation_profiles: List[AlgorithmValidationProfile]


class AnnotationConsolidationConfig(Base):
    """
    AnnotationConsolidationConfig
         <p>Configures how labels are consolidated across human workers and processes output data. </p>

        Attributes
       ----------------------
       annotation_consolidation_lambda_arn: 	 <p>The Amazon Resource Name (ARN) of a Lambda function implements the logic for <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-annotation-consolidation.html">annotation consolidation</a> and to process output data.</p> <p>This parameter is required for all labeling jobs. For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-task-types.html">built-in task types</a>, use one of the following Amazon SageMaker Ground Truth Lambda function ARNs for <code>AnnotationConsolidationLambdaArn</code>. For custom labeling workflows, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-custom-templates-step3.html#sms-custom-templates-step3-postlambda">Post-annotation Lambda</a>. </p> <p> <b>Bounding box</b> - Finds the most similar boxes from different workers based on the Jaccard index of the boxes.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-BoundingBox</code> </p> </li> </ul> <p> <b>Image classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of an image based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-ImageMultiClass</code> </p> </li> </ul> <p> <b>Multi-label image classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true classes of an image based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-ImageMultiClassMultiLabel</code> </p> </li> </ul> <p> <b>Semantic segmentation</b> - Treats each pixel in an image as a multi-class classification and treats pixel annotations from workers as "votes" for the correct label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-SemanticSegmentation</code> </p> </li> </ul> <p> <b>Text classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of text based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-TextMultiClass</code> </p> </li> </ul> <p> <b>Multi-label text classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true classes of text based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-TextMultiClassMultiLabel</code> </p> </li> </ul> <p> <b>Named entity recognition</b> - Groups similar selections and calculates aggregate boundaries, resolving to most-assigned label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-NamedEntityRecognition</code> </p> </li> </ul> <p> <b>Video Classification</b> - Use this task type when you need workers to classify videos using predefined labels that you specify. Workers are shown videos and are asked to choose one label for each video.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-VideoMultiClass</code> </p> </li> </ul> <p> <b>Video Frame Object Detection</b> - Use this task type to have workers identify and locate objects in a sequence of video frames (images extracted from a video) using bounding boxes. For example, you can use this task to ask workers to identify and localize various objects in a series of video frames, such as cars, bikes, and pedestrians.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-VideoObjectDetection</code> </p> </li> </ul> <p> <b>Video Frame Object Tracking</b> - Use this task type to have workers track the movement of objects in a sequence of video frames (images extracted from a video) using bounding boxes. For example, you can use this task to ask workers to track the movement of objects, such as cars, bikes, and pedestrians. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-VideoObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Object Detection</b> - Use this task type when you want workers to classify objects in a 3D point cloud by drawing 3D cuboids around objects. For example, you can use this task type to ask workers to identify different types of objects in a point cloud, such as cars, bikes, and pedestrians.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-3DPointCloudObjectDetection</code> </p> </li> </ul> <p> <b>3D Point Cloud Object Tracking</b> - Use this task type when you want workers to draw 3D cuboids around objects that appear in a sequence of 3D point cloud frames. For example, you can use this task type to ask workers to track the movement of vehicles across multiple point cloud frames. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-3DPointCloudObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Semantic Segmentation</b> - Use this task type when you want workers to create a point-level semantic segmentation masks by painting objects in a 3D point cloud using different colors where each color is assigned to one of the classes you specify.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> </ul> <p> <b>Use the following ARNs for Label Verification and Adjustment Jobs</b> </p> <p>Use label verification and adjustment jobs to review and adjust labels. To learn more, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-verification-data.html">Verify and Adjust Labels </a>.</p> <p> <b>Semantic Segmentation Adjustment</b> - Treats each pixel in an image as a multi-class classification and treats pixel adjusted annotations from workers as "votes" for the correct label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-AdjustmentSemanticSegmentation</code> </p> </li> </ul> <p> <b>Semantic Segmentation Verification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of verification judgment for semantic segmentation labels based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-VerificationSemanticSegmentation</code> </p> </li> </ul> <p> <b>Bounding Box Adjustment</b> - Finds the most similar boxes from different workers based on the Jaccard index of the adjusted annotations.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-AdjustmentBoundingBox</code> </p> </li> </ul> <p> <b>Bounding Box Verification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of verification judgement for bounding box labels based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-VerificationBoundingBox</code> </p> </li> </ul> <p> <b>Video Frame Object Detection Adjustment</b> - Use this task type when you want workers to adjust bounding boxes that workers have added to video frames to classify and localize objects in a sequence of video frames.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-AdjustmentVideoObjectDetection</code> </p> </li> </ul> <p> <b>Video Frame Object Tracking Adjustment</b> - Use this task type when you want workers to adjust bounding boxes that workers have added to video frames to track object movement across a sequence of video frames.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-AdjustmentVideoObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Object Detection Adjustment</b> - Use this task type when you want workers to adjust 3D cuboids around objects in a 3D point cloud. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-Adjustment3DPointCloudObjectDetection</code> </p> </li> </ul> <p> <b>3D Point Cloud Object Tracking Adjustment</b> - Use this task type when you want workers to adjust 3D cuboids around objects that appear in a sequence of 3D point cloud frames.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-Adjustment3DPointCloudObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Semantic Segmentation Adjustment</b> - Use this task type when you want workers to adjust a point-level semantic segmentation masks using a paint tool.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:ACS-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> </ul>
    """

    annotation_consolidation_lambda_arn: str


class ResourceSpec(Base):
    """
    ResourceSpec
         <p>Specifies the ARN's of a SageMaker image and SageMaker image version, and the instance type that the version runs on.</p>

        Attributes
       ----------------------
       sage_maker_image_arn: 	 <p>The ARN of the SageMaker image that the image version belongs to.</p>
       sage_maker_image_version_arn: 	 <p>The ARN of the image version created on the instance.</p>
       sage_maker_image_version_alias: 	 <p>The SageMakerImageVersionAlias of the image to launch with. This value is in SemVer 2.0.0 versioning format.</p>
       instance_type: 	 <p>The instance type that the image version runs on.</p> <note> <p> <b>JupyterServer apps</b> only support the <code>system</code> value.</p> <p>For <b>KernelGateway apps</b>, the <code>system</code> value is translated to <code>ml.t3.medium</code>. KernelGateway apps also support all other values for available instance types.</p> </note>
       lifecycle_config_arn: 	 <p> The Amazon Resource Name (ARN) of the Lifecycle Configuration attached to the Resource.</p>
    """

    sage_maker_image_arn: Optional[str] = Unassigned()
    sage_maker_image_version_arn: Optional[str] = Unassigned()
    sage_maker_image_version_alias: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    lifecycle_config_arn: Optional[str] = Unassigned()


class AppDetails(Base):
    """
    AppDetails
         <p>Details about an Amazon SageMaker app.</p>

        Attributes
       ----------------------
       domain_id: 	 <p>The domain ID.</p>
       user_profile_name: 	 <p>The user profile name.</p>
       space_name: 	 <p>The name of the space.</p>
       app_type: 	 <p>The type of app.</p>
       app_name: 	 <p>The name of the app.</p>
       status: 	 <p>The status.</p>
       creation_time: 	 <p>The creation time.</p>
       resource_spec
    """

    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    app_type: Optional[str] = Unassigned()
    app_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    resource_spec: Optional[ResourceSpec] = Unassigned()


class KernelSpec(Base):
    """
    KernelSpec
         <p>The specification of a Jupyter kernel.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the Jupyter kernel in the image. This value is case sensitive.</p>
       display_name: 	 <p>The display name of the kernel.</p>
    """

    name: str
    display_name: Optional[str] = Unassigned()


class FileSystemConfig(Base):
    """
    FileSystemConfig
         <p>The Amazon Elastic File System storage configuration for a SageMaker image.</p>

        Attributes
       ----------------------
       mount_path: 	 <p>The path within the image to mount the user's EFS home directory. The directory should be empty. If not specified, defaults to <i>/home/sagemaker-user</i>.</p>
       default_uid: 	 <p>The default POSIX user ID (UID). If not specified, defaults to <code>1000</code>.</p>
       default_gid: 	 <p>The default POSIX group ID (GID). If not specified, defaults to <code>100</code>.</p>
    """

    mount_path: Optional[str] = Unassigned()
    default_uid: Optional[int] = Unassigned()
    default_gid: Optional[int] = Unassigned()


class KernelGatewayImageConfig(Base):
    """
    KernelGatewayImageConfig
         <p>The configuration for the file system and kernels in a SageMaker image running as a KernelGateway app.</p>

        Attributes
       ----------------------
       kernel_specs: 	 <p>The specification of the Jupyter kernels in the image.</p>
       file_system_config: 	 <p>The Amazon Elastic File System storage configuration for a SageMaker image.</p>
    """

    kernel_specs: List[KernelSpec]
    file_system_config: Optional[FileSystemConfig] = Unassigned()


class ContainerConfig(Base):
    """
    ContainerConfig
         <p>The configuration used to run the application image container.</p>

        Attributes
       ----------------------
       container_arguments: 	 <p>The arguments for the container when you're running the application.</p>
       container_entrypoint: 	 <p>The entrypoint used to run the application in the container.</p>
       container_environment_variables: 	 <p>The environment variables to set in the container</p>
    """

    container_arguments: Optional[List[str]] = Unassigned()
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_environment_variables: Optional[Dict[str, str]] = Unassigned()


class JupyterLabAppImageConfig(Base):
    """
    JupyterLabAppImageConfig
         <p>The configuration for the file system and kernels in a SageMaker image running as a JupyterLab app. The <code>FileSystemConfig</code> object is not supported.</p>

        Attributes
       ----------------------
       file_system_config
       container_config
    """

    file_system_config: Optional[FileSystemConfig] = Unassigned()
    container_config: Optional[ContainerConfig] = Unassigned()


class AppImageConfigDetails(Base):
    """
    AppImageConfigDetails
         <p>The configuration for running a SageMaker image as a KernelGateway app.</p>

        Attributes
       ----------------------
       app_image_config_arn: 	 <p>The ARN of the AppImageConfig.</p>
       app_image_config_name: 	 <p>The name of the AppImageConfig. Must be unique to your account.</p>
       creation_time: 	 <p>When the AppImageConfig was created.</p>
       last_modified_time: 	 <p>When the AppImageConfig was last modified.</p>
       kernel_gateway_image_config: 	 <p>The configuration for the file system and kernels in the SageMaker image.</p>
       jupyter_lab_app_image_config: 	 <p>The configuration for the file system and the runtime, such as the environment variables and entry point.</p>
    """

    app_image_config_arn: Optional[str] = Unassigned()
    app_image_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    kernel_gateway_image_config: Optional[KernelGatewayImageConfig] = Unassigned()
    jupyter_lab_app_image_config: Optional[JupyterLabAppImageConfig] = Unassigned()


class AppSpecification(Base):
    """
    AppSpecification
         <p>Configuration to run a processing job in a specified container image.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The container image to be run by the processing job.</p>
       container_entrypoint: 	 <p>The entrypoint for a container used to run a processing job.</p>
       container_arguments: 	 <p>The arguments for a container used to run a processing job.</p>
    """

    image_uri: str
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_arguments: Optional[List[str]] = Unassigned()


class ArtifactSourceType(Base):
    """
    ArtifactSourceType
         <p>The ID and ID type of an artifact source.</p>

        Attributes
       ----------------------
       source_id_type: 	 <p>The type of ID.</p>
       value: 	 <p>The ID.</p>
    """

    source_id_type: str
    value: str


class ArtifactSource(Base):
    """
    ArtifactSource
         <p>A structure describing the source of an artifact.</p>

        Attributes
       ----------------------
       source_uri: 	 <p>The URI of the source.</p>
       source_types: 	 <p>A list of source types.</p>
    """

    source_uri: str
    source_types: Optional[List[ArtifactSourceType]] = Unassigned()


class ArtifactSummary(Base):
    """
    ArtifactSummary
         <p>Lists a summary of the properties of an artifact. An artifact represents a URI addressable object or data. Some examples are a dataset and a model.</p>

        Attributes
       ----------------------
       artifact_arn: 	 <p>The Amazon Resource Name (ARN) of the artifact.</p>
       artifact_name: 	 <p>The name of the artifact.</p>
       source: 	 <p>The source of the artifact.</p>
       artifact_type: 	 <p>The type of the artifact.</p>
       creation_time: 	 <p>When the artifact was created.</p>
       last_modified_time: 	 <p>When the artifact was last modified.</p>
    """

    artifact_arn: Optional[str] = Unassigned()
    artifact_name: Optional[str] = Unassigned()
    source: Optional[ArtifactSource] = Unassigned()
    artifact_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class IamIdentity(Base):
    """
    IamIdentity
         <p>The IAM Identity details associated with the user. These details are associated with model package groups, model packages and project entities only.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the IAM identity.</p>
       principal_id: 	 <p>The ID of the principal that assumes the IAM identity.</p>
       source_identity: 	 <p>The person or application which assumes the IAM identity.</p>
    """

    arn: Optional[str] = Unassigned()
    principal_id: Optional[str] = Unassigned()
    source_identity: Optional[str] = Unassigned()


class UserContext(Base):
    """
    UserContext
         <p>Information about the user who created or modified an experiment, trial, trial component, lineage group, project, or model card.</p>

        Attributes
       ----------------------
       user_profile_arn: 	 <p>The Amazon Resource Name (ARN) of the user's profile.</p>
       user_profile_name: 	 <p>The name of the user's profile.</p>
       domain_id: 	 <p>The domain associated with the user.</p>
       iam_identity: 	 <p>The IAM Identity details associated with the user. These details are associated with model package groups, model packages, and project entities only.</p>
    """

    user_profile_arn: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    iam_identity: Optional[IamIdentity] = Unassigned()


class AssociationSummary(Base):
    """
    AssociationSummary
         <p>Lists a summary of the properties of an association. An association is an entity that links other lineage or experiment entities. An example would be an association between a training job and a model.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The ARN of the source.</p>
       destination_arn: 	 <p>The Amazon Resource Name (ARN) of the destination.</p>
       source_type: 	 <p>The source type.</p>
       destination_type: 	 <p>The destination type.</p>
       association_type: 	 <p>The type of the association.</p>
       source_name: 	 <p>The name of the source.</p>
       destination_name: 	 <p>The name of the destination.</p>
       creation_time: 	 <p>When the association was created.</p>
       created_by
    """

    source_arn: Optional[str] = Unassigned()
    destination_arn: Optional[str] = Unassigned()
    source_type: Optional[str] = Unassigned()
    destination_type: Optional[str] = Unassigned()
    association_type: Optional[str] = Unassigned()
    source_name: Optional[str] = Unassigned()
    destination_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()


class AsyncInferenceClientConfig(Base):
    """
    AsyncInferenceClientConfig
         <p>Configures the behavior of the client used by SageMaker to interact with the model container during asynchronous inference.</p>

        Attributes
       ----------------------
       max_concurrent_invocations_per_instance: 	 <p>The maximum number of concurrent requests sent by the SageMaker client to the model container. If no value is provided, SageMaker chooses an optimal value.</p>
    """

    max_concurrent_invocations_per_instance: Optional[int] = Unassigned()


class AsyncInferenceNotificationConfig(Base):
    """
    AsyncInferenceNotificationConfig
         <p>Specifies the configuration for notifications of inference results for asynchronous inference.</p>

        Attributes
       ----------------------
       success_topic: 	 <p>Amazon SNS topic to post a notification to when inference completes successfully. If no topic is provided, no notification is sent on success.</p>
       error_topic: 	 <p>Amazon SNS topic to post a notification to when inference fails. If no topic is provided, no notification is sent on failure.</p>
       include_inference_response_in: 	 <p>The Amazon SNS topics where you want the inference response to be included.</p> <note> <p>The inference response is included only if the response size is less than or equal to 128 KB.</p> </note>
    """

    success_topic: Optional[str] = Unassigned()
    error_topic: Optional[str] = Unassigned()
    include_inference_response_in: Optional[List[str]] = Unassigned()


class AsyncInferenceOutputConfig(Base):
    """
    AsyncInferenceOutputConfig
         <p>Specifies the configuration for asynchronous inference invocation outputs.</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that SageMaker uses to encrypt the asynchronous inference output in Amazon S3.</p> <p/>
       s3_output_path: 	 <p>The Amazon S3 location to upload inference responses to.</p>
       notification_config: 	 <p>Specifies the configuration for notifications of inference results for asynchronous inference.</p>
       s3_failure_path: 	 <p>The Amazon S3 location to upload failure inference responses to.</p>
    """

    kms_key_id: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    notification_config: Optional[AsyncInferenceNotificationConfig] = Unassigned()
    s3_failure_path: Optional[str] = Unassigned()


class AsyncInferenceConfig(Base):
    """
    AsyncInferenceConfig
         <p>Specifies configuration for how an endpoint performs asynchronous inference.</p>

        Attributes
       ----------------------
       client_config: 	 <p>Configures the behavior of the client used by SageMaker to interact with the model container during asynchronous inference.</p>
       output_config: 	 <p>Specifies the configuration for asynchronous inference invocation outputs.</p>
    """

    output_config: AsyncInferenceOutputConfig
    client_config: Optional[AsyncInferenceClientConfig] = Unassigned()


class AthenaDatasetDefinition(Base):
    """
    AthenaDatasetDefinition
         <p>Configuration for Athena Dataset Definition input.</p>

        Attributes
       ----------------------
       catalog
       database
       query_string
       work_group
       output_s3_uri: 	 <p>The location in Amazon S3 where Athena query results are stored.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data generated from an Athena query execution.</p>
       output_format
       output_compression
    """

    catalog: str
    database: str
    query_string: str
    output_s3_uri: str
    output_format: str
    work_group: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    output_compression: Optional[str] = Unassigned()


class AutoMLAlgorithmConfig(Base):
    """
    AutoMLAlgorithmConfig
         <p>The collection of algorithms run on a dataset for training the model candidates of an Autopilot job.</p>

        Attributes
       ----------------------
       auto_m_l_algorithms: 	 <p>The selection of algorithms run on a dataset to train the model candidates of an Autopilot job. </p> <note> <p>Selected algorithms must belong to the list corresponding to the training mode set in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLJobConfig.html#sagemaker-Type-AutoMLJobConfig-Mode">AutoMLJobConfig.Mode</a> (<code>ENSEMBLING</code> or <code>HYPERPARAMETER_TUNING</code>). Choose a minimum of 1 algorithm. </p> </note> <ul> <li> <p>In <code>ENSEMBLING</code> mode:</p> <ul> <li> <p>"catboost"</p> </li> <li> <p>"extra-trees"</p> </li> <li> <p>"fastai"</p> </li> <li> <p>"lightgbm"</p> </li> <li> <p>"linear-learner"</p> </li> <li> <p>"nn-torch"</p> </li> <li> <p>"randomforest"</p> </li> <li> <p>"xgboost"</p> </li> </ul> </li> <li> <p>In <code>HYPERPARAMETER_TUNING</code> mode:</p> <ul> <li> <p>"linear-learner"</p> </li> <li> <p>"mlp"</p> </li> <li> <p>"xgboost"</p> </li> </ul> </li> </ul>
    """

    auto_m_l_algorithms: List[str]


class FinalAutoMLJobObjectiveMetric(Base):
    """
    FinalAutoMLJobObjectiveMetric
         <p>The best candidate result from an AutoML training job.</p>

        Attributes
       ----------------------
       type: 	 <p>The type of metric with the best result.</p>
       metric_name: 	 <p>The name of the metric with the best result. For a description of the possible objective metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLJobObjective.html">AutoMLJobObjective$MetricName</a>.</p>
       value: 	 <p>The value of the metric with the best result.</p>
       standard_metric_name: 	 <p>The name of the standard metric. For a description of the standard metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-metrics-validation.html#autopilot-metrics">Autopilot candidate metrics</a>.</p>
    """

    metric_name: str
    value: float
    type: Optional[str] = Unassigned()
    standard_metric_name: Optional[str] = Unassigned()


class AutoMLCandidateStep(Base):
    """
    AutoMLCandidateStep
         <p>Information about the steps for a candidate and what step it is working on.</p>

        Attributes
       ----------------------
       candidate_step_type: 	 <p>Whether the candidate is at the transform, training, or processing step.</p>
       candidate_step_arn: 	 <p>The ARN for the candidate's step.</p>
       candidate_step_name: 	 <p>The name for the candidate's step.</p>
    """

    candidate_step_type: str
    candidate_step_arn: str
    candidate_step_name: str


class AutoMLContainerDefinition(Base):
    """
    AutoMLContainerDefinition
         <p>A list of container definitions that describe the different containers that make up an AutoML candidate. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ContainerDefinition.html"> ContainerDefinition</a>.</p>

        Attributes
       ----------------------
       image: 	 <p>The Amazon Elastic Container Registry (Amazon ECR) path of the container. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ContainerDefinition.html"> ContainerDefinition</a>.</p>
       model_data_url: 	 <p>The location of the model artifacts. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ContainerDefinition.html"> ContainerDefinition</a>.</p>
       environment: 	 <p>The environment variables to set in the container. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ContainerDefinition.html"> ContainerDefinition</a>.</p>
    """

    image: str
    model_data_url: str
    environment: Optional[Dict[str, str]] = Unassigned()


class CandidateArtifactLocations(Base):
    """
    CandidateArtifactLocations
         <p>The location of artifacts for an AutoML candidate job.</p>

        Attributes
       ----------------------
       explainability: 	 <p>The Amazon S3 prefix to the explainability artifacts generated for the AutoML candidate.</p>
       model_insights: 	 <p>The Amazon S3 prefix to the model insight artifacts generated for the AutoML candidate.</p>
       backtest_results: 	 <p>The Amazon S3 prefix to the accuracy metrics and the inference results observed over the testing window. Available only for the time-series forecasting problem type.</p>
    """

    explainability: str
    model_insights: Optional[str] = Unassigned()
    backtest_results: Optional[str] = Unassigned()


class MetricDatum(Base):
    """
    MetricDatum
         <p>Information about the metric for a candidate produced by an AutoML job.</p>

        Attributes
       ----------------------
       metric_name: 	 <p>The name of the metric.</p>
       value: 	 <p>The value of the metric.</p>
       set: 	 <p>The dataset split from which the AutoML job produced the metric.</p>
       standard_metric_name: 	 <p>The name of the standard metric. </p> <note> <p>For definitions of the standard metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-metrics"> <code>Autopilot candidate metrics</code> </a>.</p> </note>
    """

    metric_name: Optional[str] = Unassigned()
    value: Optional[float] = Unassigned()
    set: Optional[str] = Unassigned()
    standard_metric_name: Optional[str] = Unassigned()


class CandidateProperties(Base):
    """
    CandidateProperties
         <p>The properties of an AutoML candidate job.</p>

        Attributes
       ----------------------
       candidate_artifact_locations: 	 <p>The Amazon S3 prefix to the artifacts generated for an AutoML candidate.</p>
       candidate_metrics: 	 <p>Information about the candidate metrics for an AutoML job.</p>
    """

    candidate_artifact_locations: Optional[CandidateArtifactLocations] = Unassigned()
    candidate_metrics: Optional[List[MetricDatum]] = Unassigned()


class AutoMLCandidate(Base):
    """
    AutoMLCandidate
         <p>Information about a candidate produced by an AutoML training job, including its status, steps, and other properties.</p>

        Attributes
       ----------------------
       candidate_name: 	 <p>The name of the candidate.</p>
       final_auto_m_l_job_objective_metric
       objective_status: 	 <p>The objective's status.</p>
       candidate_steps: 	 <p>Information about the candidate's steps.</p>
       candidate_status: 	 <p>The candidate's status.</p>
       inference_containers: 	 <p>Information about the recommended inference container definitions.</p>
       creation_time: 	 <p>The creation time.</p>
       end_time: 	 <p>The end time.</p>
       last_modified_time: 	 <p>The last modified time.</p>
       failure_reason: 	 <p>The failure reason.</p>
       candidate_properties: 	 <p>The properties of an AutoML candidate job.</p>
       inference_container_definitions: 	 <p>The mapping of all supported processing unit (CPU, GPU, etc...) to inference container definitions for the candidate. This field is populated for the AutoML jobs V2 (for example, for jobs created by calling <code>CreateAutoMLJobV2</code>) related to image or text classification problem types only.</p>
    """

    candidate_name: str
    objective_status: str
    candidate_steps: List[AutoMLCandidateStep]
    candidate_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    final_auto_m_l_job_objective_metric: Optional[FinalAutoMLJobObjectiveMetric] = (
        Unassigned()
    )
    inference_containers: Optional[List[AutoMLContainerDefinition]] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    candidate_properties: Optional[CandidateProperties] = Unassigned()
    inference_container_definitions: Optional[
        Dict[str, List[AutoMLContainerDefinition]]
    ] = Unassigned()


class AutoMLCandidateGenerationConfig(Base):
    """
    AutoMLCandidateGenerationConfig
         <p>Stores the configuration information for how a candidate is generated (optional).</p>

        Attributes
       ----------------------
       feature_specification_s3_uri: 	 <p>A URL to the Amazon S3 data source containing selected features from the input data source to run an Autopilot job. You can input <code>FeatureAttributeNames</code> (optional) in JSON format as shown below: </p> <p> <code>{ "FeatureAttributeNames":["col1", "col2", ...] }</code>.</p> <p>You can also specify the data type of the feature (optional) in the format shown below:</p> <p> <code>{ "FeatureDataTypes":{"col1":"numeric", "col2":"categorical" ... } }</code> </p> <note> <p>These column keys may not include the target column.</p> </note> <p>In ensembling mode, Autopilot only supports the following data types: <code>numeric</code>, <code>categorical</code>, <code>text</code>, and <code>datetime</code>. In HPO mode, Autopilot can support <code>numeric</code>, <code>categorical</code>, <code>text</code>, <code>datetime</code>, and <code>sequence</code>.</p> <p>If only <code>FeatureDataTypes</code> is provided, the column keys (<code>col1</code>, <code>col2</code>,..) should be a subset of the column names in the input data. </p> <p>If both <code>FeatureDataTypes</code> and <code>FeatureAttributeNames</code> are provided, then the column keys should be a subset of the column names provided in <code>FeatureAttributeNames</code>. </p> <p>The key name <code>FeatureAttributeNames</code> is fixed. The values listed in <code>["col1", "col2", ...]</code> are case sensitive and should be a list of strings containing unique values that are a subset of the column names in the input data. The list of columns provided must not include the target column.</p>
       algorithms_config: 	 <p>Stores the configuration information for the selection of algorithms used to train the model candidates.</p> <p>The list of available algorithms to choose from depends on the training mode set in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLJobConfig.html"> <code>AutoMLJobConfig.Mode</code> </a>.</p> <ul> <li> <p> <code>AlgorithmsConfig</code> should not be set in <code>AUTO</code> training mode.</p> </li> <li> <p>When <code>AlgorithmsConfig</code> is provided, one <code>AutoMLAlgorithms</code> attribute must be set and one only.</p> <p>If the list of algorithms provided as values for <code>AutoMLAlgorithms</code> is empty, <code>AutoMLCandidateGenerationConfig</code> uses the full set of algorithms for the given training mode.</p> </li> <li> <p>When <code>AlgorithmsConfig</code> is not provided, <code>AutoMLCandidateGenerationConfig</code> uses the full set of algorithms for the given training mode.</p> </li> </ul> <p>For the list of all algorithms per training mode, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLAlgorithmConfig.html"> AutoMLAlgorithmConfig</a>.</p> <p>For more information on each algorithm, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Algorithm support</a> section in Autopilot developer guide.</p>
    """

    feature_specification_s3_uri: Optional[str] = Unassigned()
    algorithms_config: Optional[List[AutoMLAlgorithmConfig]] = Unassigned()


class AutoMLS3DataSource(Base):
    """
    AutoMLS3DataSource
         <p>Describes the Amazon S3 data source.</p>

        Attributes
       ----------------------
       s3_data_type: 	 <p>The data type. </p> <ul> <li> <p>If you choose <code>S3Prefix</code>, <code>S3Uri</code> identifies a key name prefix. SageMaker uses all objects that match the specified key name prefix for model training.</p> <p>The <code>S3Prefix</code> should have the following format:</p> <p> <code>s3://DOC-EXAMPLE-BUCKET/DOC-EXAMPLE-FOLDER-OR-FILE</code> </p> </li> <li> <p>If you choose <code>ManifestFile</code>, <code>S3Uri</code> identifies an object that is a manifest file containing a list of object keys that you want SageMaker to use for model training.</p> <p>A <code>ManifestFile</code> should have the format shown below:</p> <p> <code>[ {"prefix": "s3://DOC-EXAMPLE-BUCKET/DOC-EXAMPLE-FOLDER/DOC-EXAMPLE-PREFIX/"}, </code> </p> <p> <code>"DOC-EXAMPLE-RELATIVE-PATH/DOC-EXAMPLE-FOLDER/DATA-1",</code> </p> <p> <code>"DOC-EXAMPLE-RELATIVE-PATH/DOC-EXAMPLE-FOLDER/DATA-2",</code> </p> <p> <code>... "DOC-EXAMPLE-RELATIVE-PATH/DOC-EXAMPLE-FOLDER/DATA-N" ]</code> </p> </li> <li> <p>If you choose <code>AugmentedManifestFile</code>, <code>S3Uri</code> identifies an object that is an augmented manifest file in JSON lines format. This file contains the data you want to use for model training. <code>AugmentedManifestFile</code> is available for V2 API jobs only (for example, for jobs created by calling <code>CreateAutoMLJobV2</code>).</p> <p>Here is a minimal, single-record example of an <code>AugmentedManifestFile</code>:</p> <p> <code>{"source-ref": "s3://DOC-EXAMPLE-BUCKET/DOC-EXAMPLE-FOLDER/cats/cat.jpg",</code> </p> <p> <code>"label-metadata": {"class-name": "cat"</code> }</p> <p>For more information on <code>AugmentedManifestFile</code>, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/augmented-manifest.html">Provide Dataset Metadata to Training Jobs with an Augmented Manifest File</a>.</p> </li> </ul>
       s3_uri: 	 <p>The URL to the Amazon S3 data source. The Uri refers to the Amazon S3 prefix or ManifestFile depending on the data type.</p>
    """

    s3_data_type: str
    s3_uri: str


class AutoMLDataSource(Base):
    """
    AutoMLDataSource
         <p>The data source for the Autopilot job.</p>

        Attributes
       ----------------------
       s3_data_source: 	 <p>The Amazon S3 location of the input data.</p>
    """

    s3_data_source: AutoMLS3DataSource


class AutoMLChannel(Base):
    """
    AutoMLChannel
         <p>A channel is a named input source that training algorithms can consume. The validation dataset size is limited to less than 2 GB. The training dataset size must be less than 100 GB. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Channel.html"> Channel</a>.</p> <note> <p>A validation dataset must contain the same headers as the training dataset.</p> </note> <p/>

        Attributes
       ----------------------
       data_source: 	 <p>The data source for an AutoML channel.</p>
       compression_type: 	 <p>You can use <code>Gzip</code> or <code>None</code>. The default value is <code>None</code>.</p>
       target_attribute_name: 	 <p>The name of the target variable in supervised learning, usually represented by 'y'.</p>
       content_type: 	 <p>The content type of the data from the input source. You can use <code>text/csv;header=present</code> or <code>x-application/vnd.amazon+parquet</code>. The default value is <code>text/csv;header=present</code>.</p>
       channel_type: 	 <p>The channel type (optional) is an <code>enum</code> string. The default value is <code>training</code>. Channels for training and validation must share the same <code>ContentType</code> and <code>TargetAttributeName</code>. For information on specifying training and validation channel types, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-datasets-problem-types.html#autopilot-data-sources-training-or-validation">How to specify training and validation datasets</a>.</p>
       sample_weight_attribute_name: 	 <p>If specified, this column name indicates which column of the dataset should be treated as sample weights for use by the objective metric during the training, evaluation, and the selection of the best model. This column is not considered as a predictive feature. For more information on Autopilot metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-metrics-validation.html">Metrics and validation</a>.</p> <p>Sample weights should be numeric, non-negative, with larger values indicating which rows are more important than others. Data points that have invalid or no weight value are excluded.</p> <p>Support for sample weights is available in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLAlgorithmConfig.html">Ensembling</a> mode only.</p>
    """

    target_attribute_name: str
    data_source: Optional[AutoMLDataSource] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    content_type: Optional[str] = Unassigned()
    channel_type: Optional[str] = Unassigned()
    sample_weight_attribute_name: Optional[str] = Unassigned()


class AutoMLDataSplitConfig(Base):
    """
    AutoMLDataSplitConfig
         <p>This structure specifies how to split the data into train and validation datasets.</p> <p>The validation and training datasets must contain the same headers. For jobs created by calling <code>CreateAutoMLJob</code>, the validation dataset must be less than 2 GB in size.</p>

        Attributes
       ----------------------
       validation_fraction: 	 <p>The validation fraction (optional) is a float that specifies the portion of the training dataset to be used for validation. The default value is 0.2, and values must be greater than 0 and less than 1. We recommend setting this value to be less than 0.5.</p>
    """

    validation_fraction: Optional[float] = Unassigned()


class AutoMLJobArtifacts(Base):
    """
    AutoMLJobArtifacts
         <p>The artifacts that are generated during an AutoML job.</p>

        Attributes
       ----------------------
       candidate_definition_notebook_location: 	 <p>The URL of the notebook location.</p>
       data_exploration_notebook_location: 	 <p>The URL of the notebook location.</p>
    """

    candidate_definition_notebook_location: Optional[str] = Unassigned()
    data_exploration_notebook_location: Optional[str] = Unassigned()


class AutoMLJobChannel(Base):
    """
    AutoMLJobChannel
         <p>A channel is a named input source that training algorithms can consume. This channel is used for AutoML jobs V2 (jobs created by calling <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateAutoMLJobV2.html">CreateAutoMLJobV2</a>).</p>

        Attributes
       ----------------------
       channel_type: 	 <p>The type of channel. Defines whether the data are used for training or validation. The default value is <code>training</code>. Channels for <code>training</code> and <code>validation</code> must share the same <code>ContentType</code> </p> <note> <p>The type of channel defaults to <code>training</code> for the time-series forecasting problem type.</p> </note>
       content_type: 	 <p>The content type of the data from the input source. The following are the allowed content types for different problems:</p> <ul> <li> <p>For tabular problem types: <code>text/csv;header=present</code> or <code>x-application/vnd.amazon+parquet</code>. The default value is <code>text/csv;header=present</code>.</p> </li> <li> <p>For image classification: <code>image/png</code>, <code>image/jpeg</code>, or <code>image/*</code>. The default value is <code>image/*</code>.</p> </li> <li> <p>For text classification: <code>text/csv;header=present</code> or <code>x-application/vnd.amazon+parquet</code>. The default value is <code>text/csv;header=present</code>.</p> </li> <li> <p>For time-series forecasting: <code>text/csv;header=present</code> or <code>x-application/vnd.amazon+parquet</code>. The default value is <code>text/csv;header=present</code>.</p> </li> <li> <p>For text generation (LLMs fine-tuning): <code>text/csv;header=present</code> or <code>x-application/vnd.amazon+parquet</code>. The default value is <code>text/csv;header=present</code>.</p> </li> </ul>
       compression_type: 	 <p>The allowed compression types depend on the input format and problem type. We allow the compression type <code>Gzip</code> for <code>S3Prefix</code> inputs on tabular data only. For all other inputs, the compression type should be <code>None</code>. If no compression type is provided, we default to <code>None</code>.</p>
       data_source: 	 <p>The data source for an AutoML channel (Required).</p>
    """

    channel_type: Optional[str] = Unassigned()
    content_type: Optional[str] = Unassigned()
    compression_type: Optional[str] = Unassigned()
    data_source: Optional[AutoMLDataSource] = Unassigned()


class AutoMLJobCompletionCriteria(Base):
    """
    AutoMLJobCompletionCriteria
         <p>How long a job is allowed to run, or how many candidates a job is allowed to generate.</p>

        Attributes
       ----------------------
       max_candidates: 	 <p>The maximum number of times a training job is allowed to run.</p> <p>For text and image classification, time-series forecasting, as well as text generation (LLMs fine-tuning) problem types, the supported value is 1. For tabular problem types, the maximum value is 750.</p>
       max_runtime_per_training_job_in_seconds: 	 <p>The maximum time, in seconds, that each training job executed inside hyperparameter tuning is allowed to run as part of a hyperparameter tuning job. For more information, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_StoppingCondition.html">StoppingCondition</a> used by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateHyperParameterTuningJob.html">CreateHyperParameterTuningJob</a> action.</p> <p>For job V2s (jobs created by calling <code>CreateAutoMLJobV2</code>), this field controls the runtime of the job candidate.</p> <p>For <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TextClassificationJobConfig.html">TextGenerationJobConfig</a> problem types, the maximum time defaults to 72 hours (259200 seconds).</p>
       max_auto_m_l_job_runtime_in_seconds: 	 <p>The maximum runtime, in seconds, an AutoML job has to complete.</p> <p>If an AutoML job exceeds the maximum runtime, the job is stopped automatically and its processing is ended gracefully. The AutoML job identifies the best model whose training was completed and marks it as the best-performing model. Any unfinished steps of the job, such as automatic one-click Autopilot model deployment, are not completed.</p>
    """

    max_candidates: Optional[int] = Unassigned()
    max_runtime_per_training_job_in_seconds: Optional[int] = Unassigned()
    max_auto_m_l_job_runtime_in_seconds: Optional[int] = Unassigned()


class VpcConfig(Base):
    """
    VpcConfig
         <p>Specifies an Amazon Virtual Private Cloud (VPC) that your SageMaker jobs, hosted models, and compute resources have access to. You can control access to and from your resources by configuring a VPC. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/infrastructure-give-access.html">Give SageMaker Access to Resources in your Amazon VPC</a>. </p>

        Attributes
       ----------------------
       security_group_ids: 	 <p>The VPC security group IDs, in the form <code>sg-xxxxxxxx</code>. Specify the security groups for the VPC that is specified in the <code>Subnets</code> field.</p>
       subnets: 	 <p>The ID of the subnets in the VPC to which you want to connect your training job or model. For information about the availability of specific instance types, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/instance-types-az.html">Supported Instance Types and Availability Zones</a>.</p>
    """

    security_group_ids: List[str]
    subnets: List[str]


class AutoMLSecurityConfig(Base):
    """
    AutoMLSecurityConfig
         <p>Security options.</p>

        Attributes
       ----------------------
       volume_kms_key_id: 	 <p>The key used to encrypt stored data.</p>
       enable_inter_container_traffic_encryption: 	 <p>Whether to use traffic encryption between the container layers.</p>
       vpc_config: 	 <p>The VPC configuration.</p>
    """

    volume_kms_key_id: Optional[str] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


class AutoMLJobConfig(Base):
    """
    AutoMLJobConfig
         <p>A collection of settings used for an AutoML job.</p>

        Attributes
       ----------------------
       completion_criteria: 	 <p>How long an AutoML job is allowed to run, or how many candidates a job is allowed to generate.</p>
       security_config: 	 <p>The security configuration for traffic encryption or Amazon VPC settings.</p>
       candidate_generation_config: 	 <p>The configuration for generating a candidate for an AutoML job (optional). </p>
       data_split_config: 	 <p>The configuration for splitting the input training dataset.</p> <p>Type: AutoMLDataSplitConfig</p>
       mode: 	 <p>The method that Autopilot uses to train the data. You can either specify the mode manually or let Autopilot choose for you based on the dataset size by selecting <code>AUTO</code>. In <code>AUTO</code> mode, Autopilot chooses <code>ENSEMBLING</code> for datasets smaller than 100 MB, and <code>HYPERPARAMETER_TUNING</code> for larger ones.</p> <p>The <code>ENSEMBLING</code> mode uses a multi-stack ensemble model to predict classification and regression tasks directly from your dataset. This machine learning mode combines several base models to produce an optimal predictive model. It then uses a stacking ensemble method to combine predictions from contributing members. A multi-stack ensemble model can provide better performance over a single model by combining the predictive capabilities of multiple models. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Autopilot algorithm support</a> for a list of algorithms supported by <code>ENSEMBLING</code> mode.</p> <p>The <code>HYPERPARAMETER_TUNING</code> (HPO) mode uses the best hyperparameters to train the best version of a model. HPO automatically selects an algorithm for the type of problem you want to solve. Then HPO finds the best hyperparameters according to your objective metric. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Autopilot algorithm support</a> for a list of algorithms supported by <code>HYPERPARAMETER_TUNING</code> mode.</p>
    """

    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    security_config: Optional[AutoMLSecurityConfig] = Unassigned()
    candidate_generation_config: Optional[AutoMLCandidateGenerationConfig] = (
        Unassigned()
    )
    data_split_config: Optional[AutoMLDataSplitConfig] = Unassigned()
    mode: Optional[str] = Unassigned()


class AutoMLJobObjective(Base):
    """
    AutoMLJobObjective
         <p>Specifies a metric to minimize or maximize as the objective of an AutoML job.</p>

        Attributes
       ----------------------
       metric_name: 	 <p>The name of the objective metric used to measure the predictive quality of a machine learning system. During training, the model's parameters are updated iteratively to optimize its performance based on the feedback provided by the objective metric when evaluating the model on the validation dataset.</p> <p>The list of available metrics supported by Autopilot and the default metric applied when you do not specify a metric name explicitly depend on the problem type.</p> <ul> <li> <p>For tabular problem types:</p> <ul> <li> <p>List of available metrics: </p> <ul> <li> <p> Regression: <code>MAE</code>, <code>MSE</code>, <code>R2</code>, <code>RMSE</code> </p> </li> <li> <p> Binary classification: <code>Accuracy</code>, <code>AUC</code>, <code>BalancedAccuracy</code>, <code>F1</code>, <code>Precision</code>, <code>Recall</code> </p> </li> <li> <p> Multiclass classification: <code>Accuracy</code>, <code>BalancedAccuracy</code>, <code>F1macro</code>, <code>PrecisionMacro</code>, <code>RecallMacro</code> </p> </li> </ul> <p>For a description of each metric, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-metrics-validation.html#autopilot-metrics">Autopilot metrics for classification and regression</a>.</p> </li> <li> <p>Default objective metrics:</p> <ul> <li> <p>Regression: <code>MSE</code>.</p> </li> <li> <p>Binary classification: <code>F1</code>.</p> </li> <li> <p>Multiclass classification: <code>Accuracy</code>.</p> </li> </ul> </li> </ul> </li> <li> <p>For image or text classification problem types:</p> <ul> <li> <p>List of available metrics: <code>Accuracy</code> </p> <p>For a description of each metric, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/text-classification-data-format-and-metric.html">Autopilot metrics for text and image classification</a>.</p> </li> <li> <p>Default objective metrics: <code>Accuracy</code> </p> </li> </ul> </li> <li> <p>For time-series forecasting problem types:</p> <ul> <li> <p>List of available metrics: <code>RMSE</code>, <code>wQL</code>, <code>Average wQL</code>, <code>MASE</code>, <code>MAPE</code>, <code>WAPE</code> </p> <p>For a description of each metric, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/timeseries-objective-metric.html">Autopilot metrics for time-series forecasting</a>.</p> </li> <li> <p>Default objective metrics: <code>AverageWeightedQuantileLoss</code> </p> </li> </ul> </li> <li> <p>For text generation problem types (LLMs fine-tuning): Fine-tuning language models in Autopilot does not require setting the <code>AutoMLJobObjective</code> field. Autopilot fine-tunes LLMs without requiring multiple candidates to be trained and evaluated. Instead, using your dataset, Autopilot directly fine-tunes your target model to enhance a default objective metric, the cross-entropy loss. After fine-tuning a language model, you can evaluate the quality of its generated text using different metrics. For a list of the available metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-llms-finetuning-metrics.html">Metrics for fine-tuning LLMs in Autopilot</a>.</p> </li> </ul>
    """

    metric_name: str


class AutoMLJobStepMetadata(Base):
    """
    AutoMLJobStepMetadata
         <p>Metadata for an AutoML job step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the AutoML job.</p>
    """

    arn: Optional[str] = Unassigned()


class AutoMLPartialFailureReason(Base):
    """
    AutoMLPartialFailureReason
         <p>The reason for a partial failure of an AutoML job.</p>

        Attributes
       ----------------------
       partial_failure_message: 	 <p>The message containing the reason for a partial failure of an AutoML job.</p>
    """

    partial_failure_message: Optional[str] = Unassigned()


class AutoMLJobSummary(Base):
    """
    AutoMLJobSummary
         <p>Provides a summary about an AutoML job.</p>

        Attributes
       ----------------------
       auto_m_l_job_name: 	 <p>The name of the AutoML job you are requesting.</p>
       auto_m_l_job_arn: 	 <p>The ARN of the AutoML job.</p>
       auto_m_l_job_status: 	 <p>The status of the AutoML job.</p>
       auto_m_l_job_secondary_status: 	 <p>The secondary status of the AutoML job.</p>
       creation_time: 	 <p>When the AutoML job was created.</p>
       end_time: 	 <p>The end time of an AutoML job.</p>
       last_modified_time: 	 <p>When the AutoML job was last modified.</p>
       failure_reason: 	 <p>The failure reason of an AutoML job.</p>
       partial_failure_reasons: 	 <p>The list of reasons for partial failures within an AutoML job.</p>
    """

    auto_m_l_job_name: str
    auto_m_l_job_arn: str
    auto_m_l_job_status: str
    auto_m_l_job_secondary_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    partial_failure_reasons: Optional[List[AutoMLPartialFailureReason]] = Unassigned()


class AutoMLOutputDataConfig(Base):
    """
    AutoMLOutputDataConfig
         <p>The output data configuration.</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>The Key Management Service encryption key ID.</p>
       s3_output_path: 	 <p>The Amazon S3 output path. Must be 128 characters or less.</p>
    """

    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()


class ImageClassificationJobConfig(Base):
    """
    ImageClassificationJobConfig
         <p>The collection of settings used by an AutoML job V2 for the image classification problem type.</p>

        Attributes
       ----------------------
       completion_criteria: 	 <p>How long a job is allowed to run, or how many candidates a job is allowed to generate.</p>
    """

    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


class TextClassificationJobConfig(Base):
    """
    TextClassificationJobConfig
         <p>The collection of settings used by an AutoML job V2 for the text classification problem type.</p>

        Attributes
       ----------------------
       completion_criteria: 	 <p>How long a job is allowed to run, or how many candidates a job is allowed to generate.</p>
       content_column: 	 <p>The name of the column used to provide the sentences to be classified. It should not be the same as the target column.</p>
       target_label_column: 	 <p>The name of the column used to provide the class labels. It should not be same as the content column.</p>
    """

    content_column: str
    target_label_column: str
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


class TimeSeriesTransformations(Base):
    """
    TimeSeriesTransformations
         <p>Transformations allowed on the dataset. Supported transformations are <code>Filling</code> and <code>Aggregation</code>. <code>Filling</code> specifies how to add values to missing values in the dataset. <code>Aggregation</code> defines how to aggregate data that does not align with forecast frequency.</p>

        Attributes
       ----------------------
       filling: 	 <p>A key value pair defining the filling method for a column, where the key is the column name and the value is an object which defines the filling logic. You can specify multiple filling methods for a single column.</p> <p>The supported filling methods and their corresponding options are:</p> <ul> <li> <p> <code>frontfill</code>: <code>none</code> (Supported only for target column)</p> </li> <li> <p> <code>middlefill</code>: <code>zero</code>, <code>value</code>, <code>median</code>, <code>mean</code>, <code>min</code>, <code>max</code> </p> </li> <li> <p> <code>backfill</code>: <code>zero</code>, <code>value</code>, <code>median</code>, <code>mean</code>, <code>min</code>, <code>max</code> </p> </li> <li> <p> <code>futurefill</code>: <code>zero</code>, <code>value</code>, <code>median</code>, <code>mean</code>, <code>min</code>, <code>max</code> </p> </li> </ul> <p>To set a filling method to a specific value, set the fill parameter to the chosen filling method value (for example <code>"backfill" : "value"</code>), and define the filling value in an additional parameter prefixed with "_value". For example, to set <code>backfill</code> to a value of <code>2</code>, you must include two parameters: <code>"backfill": "value"</code> and <code>"backfill_value":"2"</code>.</p>
       aggregation: 	 <p>A key value pair defining the aggregation method for a column, where the key is the column name and the value is the aggregation method.</p> <p>The supported aggregation methods are <code>sum</code> (default), <code>avg</code>, <code>first</code>, <code>min</code>, <code>max</code>.</p> <note> <p>Aggregation is only supported for the target column.</p> </note>
    """

    filling: Optional[Dict[str, Dict[str, str]]] = Unassigned()
    aggregation: Optional[Dict[str, str]] = Unassigned()


class TimeSeriesConfig(Base):
    """
    TimeSeriesConfig
         <p>The collection of components that defines the time-series.</p>

        Attributes
       ----------------------
       target_attribute_name: 	 <p>The name of the column representing the target variable that you want to predict for each item in your dataset. The data type of the target variable must be numerical.</p>
       timestamp_attribute_name: 	 <p>The name of the column indicating a point in time at which the target value of a given item is recorded.</p>
       item_identifier_attribute_name: 	 <p>The name of the column that represents the set of item identifiers for which you want to predict the target value.</p>
       grouping_attribute_names: 	 <p>A set of columns names that can be grouped with the item identifier column to create a composite key for which a target value is predicted.</p>
    """

    target_attribute_name: str
    timestamp_attribute_name: str
    item_identifier_attribute_name: str
    grouping_attribute_names: Optional[List[str]] = Unassigned()


class HolidayConfigAttributes(Base):
    """
    HolidayConfigAttributes
         <p>Stores the holiday featurization attributes applicable to each item of time-series datasets during the training of a forecasting model. This allows the model to identify patterns associated with specific holidays.</p>

        Attributes
       ----------------------
       country_code: 	 <p>The country code for the holiday calendar.</p> <p>For the list of public holiday calendars supported by AutoML job V2, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-timeseries-forecasting-holiday-calendars.html#holiday-country-codes">Country Codes</a>. Use the country code corresponding to the country of your choice.</p>
    """

    country_code: Optional[str] = Unassigned()


class TimeSeriesForecastingJobConfig(Base):
    """
    TimeSeriesForecastingJobConfig
         <p>The collection of settings used by an AutoML job V2 for the time-series forecasting problem type.</p>

        Attributes
       ----------------------
       feature_specification_s3_uri: 	 <p>A URL to the Amazon S3 data source containing additional selected features that complement the target, itemID, timestamp, and grouped columns set in <code>TimeSeriesConfig</code>. When not provided, the AutoML job V2 includes all the columns from the original dataset that are not already declared in <code>TimeSeriesConfig</code>. If provided, the AutoML job V2 only considers these additional columns as a complement to the ones declared in <code>TimeSeriesConfig</code>.</p> <p>You can input <code>FeatureAttributeNames</code> (optional) in JSON format as shown below: </p> <p> <code>{ "FeatureAttributeNames":["col1", "col2", ...] }</code>.</p> <p>You can also specify the data type of the feature (optional) in the format shown below:</p> <p> <code>{ "FeatureDataTypes":{"col1":"numeric", "col2":"categorical" ... } }</code> </p> <p>Autopilot supports the following data types: <code>numeric</code>, <code>categorical</code>, <code>text</code>, and <code>datetime</code>.</p> <note> <p>These column keys must not include any column set in <code>TimeSeriesConfig</code>.</p> </note>
       completion_criteria
       forecast_frequency: 	 <p>The frequency of predictions in a forecast.</p> <p>Valid intervals are an integer followed by Y (Year), M (Month), W (Week), D (Day), H (Hour), and min (Minute). For example, <code>1D</code> indicates every day and <code>15min</code> indicates every 15 minutes. The value of a frequency must not overlap with the next larger frequency. For example, you must use a frequency of <code>1H</code> instead of <code>60min</code>.</p> <p>The valid values for each frequency are the following:</p> <ul> <li> <p>Minute - 1-59</p> </li> <li> <p>Hour - 1-23</p> </li> <li> <p>Day - 1-6</p> </li> <li> <p>Week - 1-4</p> </li> <li> <p>Month - 1-11</p> </li> <li> <p>Year - 1</p> </li> </ul>
       forecast_horizon: 	 <p>The number of time-steps that the model predicts. The forecast horizon is also called the prediction length. The maximum forecast horizon is the lesser of 500 time-steps or 1/4 of the time-steps in the dataset.</p>
       forecast_quantiles: 	 <p>The quantiles used to train the model for forecasts at a specified quantile. You can specify quantiles from <code>0.01</code> (p1) to <code>0.99</code> (p99), by increments of 0.01 or higher. Up to five forecast quantiles can be specified. When <code>ForecastQuantiles</code> is not provided, the AutoML job uses the quantiles p10, p50, and p90 as default.</p>
       transformations: 	 <p>The transformations modifying specific attributes of the time-series, such as filling strategies for missing values.</p>
       time_series_config: 	 <p>The collection of components that defines the time-series.</p>
       holiday_config: 	 <p>The collection of holiday featurization attributes used to incorporate national holiday information into your forecasting model.</p>
    """

    forecast_frequency: str
    forecast_horizon: int
    time_series_config: TimeSeriesConfig
    feature_specification_s3_uri: Optional[str] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    forecast_quantiles: Optional[List[str]] = Unassigned()
    transformations: Optional[TimeSeriesTransformations] = Unassigned()
    holiday_config: Optional[List[HolidayConfigAttributes]] = Unassigned()


class CandidateGenerationConfig(Base):
    """
    CandidateGenerationConfig
         <p>Stores the configuration information for how model candidates are generated using an AutoML job V2.</p>

        Attributes
       ----------------------
       algorithms_config: 	 <p>Stores the configuration information for the selection of algorithms used to train model candidates on tabular data.</p> <p>The list of available algorithms to choose from depends on the training mode set in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TabularJobConfig.html"> <code>TabularJobConfig.Mode</code> </a>.</p> <ul> <li> <p> <code>AlgorithmsConfig</code> should not be set in <code>AUTO</code> training mode.</p> </li> <li> <p>When <code>AlgorithmsConfig</code> is provided, one <code>AutoMLAlgorithms</code> attribute must be set and one only.</p> <p>If the list of algorithms provided as values for <code>AutoMLAlgorithms</code> is empty, <code>CandidateGenerationConfig</code> uses the full set of algorithms for the given training mode.</p> </li> <li> <p>When <code>AlgorithmsConfig</code> is not provided, <code>CandidateGenerationConfig</code> uses the full set of algorithms for the given training mode.</p> </li> </ul> <p>For the list of all algorithms per problem type and training mode, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLAlgorithmConfig.html"> AutoMLAlgorithmConfig</a>.</p> <p>For more information on each algorithm, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Algorithm support</a> section in Autopilot developer guide.</p>
    """

    algorithms_config: Optional[List[AutoMLAlgorithmConfig]] = Unassigned()


class TabularJobConfig(Base):
    """
    TabularJobConfig
         <p>The collection of settings used by an AutoML job V2 for the tabular problem type.</p>

        Attributes
       ----------------------
       candidate_generation_config: 	 <p>The configuration information of how model candidates are generated.</p>
       completion_criteria
       feature_specification_s3_uri: 	 <p>A URL to the Amazon S3 data source containing selected features from the input data source to run an Autopilot job V2. You can input <code>FeatureAttributeNames</code> (optional) in JSON format as shown below: </p> <p> <code>{ "FeatureAttributeNames":["col1", "col2", ...] }</code>.</p> <p>You can also specify the data type of the feature (optional) in the format shown below:</p> <p> <code>{ "FeatureDataTypes":{"col1":"numeric", "col2":"categorical" ... } }</code> </p> <note> <p>These column keys may not include the target column.</p> </note> <p>In ensembling mode, Autopilot only supports the following data types: <code>numeric</code>, <code>categorical</code>, <code>text</code>, and <code>datetime</code>. In HPO mode, Autopilot can support <code>numeric</code>, <code>categorical</code>, <code>text</code>, <code>datetime</code>, and <code>sequence</code>.</p> <p>If only <code>FeatureDataTypes</code> is provided, the column keys (<code>col1</code>, <code>col2</code>,..) should be a subset of the column names in the input data. </p> <p>If both <code>FeatureDataTypes</code> and <code>FeatureAttributeNames</code> are provided, then the column keys should be a subset of the column names provided in <code>FeatureAttributeNames</code>. </p> <p>The key name <code>FeatureAttributeNames</code> is fixed. The values listed in <code>["col1", "col2", ...]</code> are case sensitive and should be a list of strings containing unique values that are a subset of the column names in the input data. The list of columns provided must not include the target column.</p>
       mode: 	 <p>The method that Autopilot uses to train the data. You can either specify the mode manually or let Autopilot choose for you based on the dataset size by selecting <code>AUTO</code>. In <code>AUTO</code> mode, Autopilot chooses <code>ENSEMBLING</code> for datasets smaller than 100 MB, and <code>HYPERPARAMETER_TUNING</code> for larger ones.</p> <p>The <code>ENSEMBLING</code> mode uses a multi-stack ensemble model to predict classification and regression tasks directly from your dataset. This machine learning mode combines several base models to produce an optimal predictive model. It then uses a stacking ensemble method to combine predictions from contributing members. A multi-stack ensemble model can provide better performance over a single model by combining the predictive capabilities of multiple models. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Autopilot algorithm support</a> for a list of algorithms supported by <code>ENSEMBLING</code> mode.</p> <p>The <code>HYPERPARAMETER_TUNING</code> (HPO) mode uses the best hyperparameters to train the best version of a model. HPO automatically selects an algorithm for the type of problem you want to solve. Then HPO finds the best hyperparameters according to your objective metric. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-model-support-validation.html#autopilot-algorithm-support">Autopilot algorithm support</a> for a list of algorithms supported by <code>HYPERPARAMETER_TUNING</code> mode.</p>
       generate_candidate_definitions_only: 	 <p>Generates possible candidates without training the models. A model candidate is a combination of data preprocessors, algorithms, and algorithm parameter settings.</p>
       problem_type: 	 <p>The type of supervised learning problem available for the model candidates of the AutoML job V2. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-datasets-problem-types.html#autopilot-problem-types"> SageMaker Autopilot problem types</a>.</p> <note> <p>You must either specify the type of supervised learning problem in <code>ProblemType</code> and provide the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateAutoMLJobV2.html#sagemaker-CreateAutoMLJobV2-request-AutoMLJobObjective">AutoMLJobObjective</a> metric, or none at all.</p> </note>
       target_attribute_name: 	 <p>The name of the target variable in supervised learning, usually represented by 'y'.</p>
       sample_weight_attribute_name: 	 <p>If specified, this column name indicates which column of the dataset should be treated as sample weights for use by the objective metric during the training, evaluation, and the selection of the best model. This column is not considered as a predictive feature. For more information on Autopilot metrics, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-metrics-validation.html">Metrics and validation</a>.</p> <p>Sample weights should be numeric, non-negative, with larger values indicating which rows are more important than others. Data points that have invalid or no weight value are excluded.</p> <p>Support for sample weights is available in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_AutoMLAlgorithmConfig.html">Ensembling</a> mode only.</p>
    """

    target_attribute_name: str
    candidate_generation_config: Optional[CandidateGenerationConfig] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    feature_specification_s3_uri: Optional[str] = Unassigned()
    mode: Optional[str] = Unassigned()
    generate_candidate_definitions_only: Optional[bool] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    sample_weight_attribute_name: Optional[str] = Unassigned()


class TextGenerationJobConfig(Base):
    """
    TextGenerationJobConfig
         <p>The collection of settings used by an AutoML job V2 for the text generation problem type.</p> <note> <p>The text generation models that support fine-tuning in Autopilot are currently accessible exclusively in regions supported by Canvas. Refer to the documentation of Canvas for the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/canvas.html">full list of its supported Regions</a>.</p> </note>

        Attributes
       ----------------------
       completion_criteria: 	 <p>How long a fine-tuning job is allowed to run. For <code>TextGenerationJobConfig</code> problem types, the <code>MaxRuntimePerTrainingJobInSeconds</code> attribute of <code>AutoMLJobCompletionCriteria</code> defaults to 72h (259200s).</p>
       base_model_name: 	 <p>The name of the base model to fine-tune. Autopilot supports fine-tuning a variety of large language models. For information on the list of supported models, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-llms-finetuning-models.html#autopilot-llms-finetuning-supported-llms">Text generation models supporting fine-tuning in Autopilot</a>. If no <code>BaseModelName</code> is provided, the default model used is <b>Falcon7BInstruct</b>. </p>
       text_generation_hyper_parameters: 	 <p>The hyperparameters used to configure and optimize the learning process of the base model. You can set any combination of the following hyperparameters for all base models. For more information on each supported hyperparameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-llms-finetuning-set-hyperparameters.html">Optimize the learning process of your text generation models with hyperparameters</a>.</p> <ul> <li> <p> <code>"epochCount"</code>: The number of times the model goes through the entire training dataset. Its value should be a string containing an integer value within the range of "1" to "10".</p> </li> <li> <p> <code>"batchSize"</code>: The number of data samples used in each iteration of training. Its value should be a string containing an integer value within the range of "1" to "64".</p> </li> <li> <p> <code>"learningRate"</code>: The step size at which a model's parameters are updated during training. Its value should be a string containing a floating-point value within the range of "0" to "1".</p> </li> <li> <p> <code>"learningRateWarmupSteps"</code>: The number of training steps during which the learning rate gradually increases before reaching its target or maximum value. Its value should be a string containing an integer value within the range of "0" to "250".</p> </li> </ul> <p>Here is an example where all four hyperparameters are configured.</p> <p> <code>{ "epochCount":"5", "learningRate":"0.5", "batchSize": "32", "learningRateWarmupSteps": "10" }</code> </p>
       model_access_config
    """

    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    base_model_name: Optional[str] = Unassigned()
    text_generation_hyper_parameters: Optional[Dict[str, str]] = Unassigned()
    model_access_config: Optional[ModelAccessConfig] = Unassigned()


class AutoMLProblemTypeConfig(Base):
    """
    AutoMLProblemTypeConfig
         <p>A collection of settings specific to the problem type used to configure an AutoML job V2. There must be one and only one config of the following type.</p>

        Attributes
       ----------------------
       image_classification_job_config: 	 <p>Settings used to configure an AutoML job V2 for the image classification problem type.</p>
       text_classification_job_config: 	 <p>Settings used to configure an AutoML job V2 for the text classification problem type.</p>
       time_series_forecasting_job_config: 	 <p>Settings used to configure an AutoML job V2 for the time-series forecasting problem type.</p>
       tabular_job_config: 	 <p>Settings used to configure an AutoML job V2 for the tabular problem type (regression, classification).</p>
       text_generation_job_config: 	 <p>Settings used to configure an AutoML job V2 for the text generation (LLMs fine-tuning) problem type.</p> <note> <p>The text generation models that support fine-tuning in Autopilot are currently accessible exclusively in regions supported by Canvas. Refer to the documentation of Canvas for the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/canvas.html">full list of its supported Regions</a>.</p> </note>
    """

    image_classification_job_config: Optional[ImageClassificationJobConfig] = (
        Unassigned()
    )
    text_classification_job_config: Optional[TextClassificationJobConfig] = Unassigned()
    time_series_forecasting_job_config: Optional[TimeSeriesForecastingJobConfig] = (
        Unassigned()
    )
    tabular_job_config: Optional[TabularJobConfig] = Unassigned()
    text_generation_job_config: Optional[TextGenerationJobConfig] = Unassigned()


class TabularResolvedAttributes(Base):
    """
    TabularResolvedAttributes
         <p>The resolved attributes specific to the tabular problem type.</p>

        Attributes
       ----------------------
       problem_type: 	 <p>The type of supervised learning problem available for the model candidates of the AutoML job V2 (Binary Classification, Multiclass Classification, Regression). For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-datasets-problem-types.html#autopilot-problem-types"> SageMaker Autopilot problem types</a>.</p>
    """

    problem_type: Optional[str] = Unassigned()


class TextGenerationResolvedAttributes(Base):
    """
    TextGenerationResolvedAttributes
         <p>The resolved attributes specific to the text generation problem type.</p>

        Attributes
       ----------------------
       base_model_name: 	 <p>The name of the base model to fine-tune.</p>
    """

    base_model_name: Optional[str] = Unassigned()


class AutoMLProblemTypeResolvedAttributes(Base):
    """
    AutoMLProblemTypeResolvedAttributes
         <p>Stores resolved attributes specific to the problem type of an AutoML job V2.</p>

        Attributes
       ----------------------
       tabular_resolved_attributes: 	 <p>The resolved attributes for the tabular problem type.</p>
       text_generation_resolved_attributes: 	 <p>The resolved attributes for the text generation problem type.</p>
    """

    tabular_resolved_attributes: Optional[TabularResolvedAttributes] = Unassigned()
    text_generation_resolved_attributes: Optional[TextGenerationResolvedAttributes] = (
        Unassigned()
    )


class AutoMLResolvedAttributes(Base):
    """
    AutoMLResolvedAttributes
         <p>The resolved attributes used to configure an AutoML job V2.</p>

        Attributes
       ----------------------
       auto_m_l_job_objective
       completion_criteria
       auto_m_l_problem_type_resolved_attributes: 	 <p>Defines the resolved attributes specific to a problem type.</p>
    """

    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()
    auto_m_l_problem_type_resolved_attributes: Optional[
        AutoMLProblemTypeResolvedAttributes
    ] = Unassigned()


class AutoParameter(Base):
    """
    AutoParameter
         <p>The name and an example value of the hyperparameter that you want to use in Autotune. If Automatic model tuning (AMT) determines that your hyperparameter is eligible for Autotune, an optimal hyperparameter range is selected for you.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the hyperparameter to optimize using Autotune.</p>
       value_hint: 	 <p>An example value of the hyperparameter to optimize using Autotune.</p>
    """

    name: str
    value_hint: str


class AutoRollbackConfig(Base):
    """
    AutoRollbackConfig
         <p>Automatic rollback configuration for handling endpoint deployment failures and recovery.</p>

        Attributes
       ----------------------
       alarms: 	 <p>List of CloudWatch alarms in your account that are configured to monitor metrics on an endpoint. If any alarms are tripped during a deployment, SageMaker rolls back the deployment.</p>
    """

    alarms: Optional[List[Alarm]] = Unassigned()


class Autotune(Base):
    """
    Autotune
         <p>A flag to indicate if you want to use Autotune to automatically find optimal values for the following fields:</p> <ul> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobConfig.html#sagemaker-Type-HyperParameterTuningJobConfig-ParameterRanges">ParameterRanges</a>: The names and ranges of parameters that a hyperparameter tuning job can optimize.</p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ResourceLimits.html">ResourceLimits</a>: The maximum resources that can be used for a training job. These resources include the maximum number of training jobs, the maximum runtime of a tuning job, and the maximum number of training jobs to run at the same time.</p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobConfig.html#sagemaker-Type-HyperParameterTuningJobConfig-TrainingJobEarlyStoppingType">TrainingJobEarlyStoppingType</a>: A flag that specifies whether or not to use early stopping for training jobs launched by a hyperparameter tuning job.</p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTrainingJobDefinition.html#sagemaker-Type-HyperParameterTrainingJobDefinition-RetryStrategy">RetryStrategy</a>: The number of times to retry a training job.</p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobConfig.html">Strategy</a>: Specifies how hyperparameter tuning chooses the combinations of hyperparameter values to use for the training jobs that it launches.</p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ConvergenceDetected.html">ConvergenceDetected</a>: A flag to indicate that Automatic model tuning (AMT) has detected model convergence.</p> </li> </ul>

        Attributes
       ----------------------
       mode: 	 <p>Set <code>Mode</code> to <code>Enabled</code> if you want to use Autotune.</p>
    """

    mode: str


class BatchDataCaptureConfig(Base):
    """
    BatchDataCaptureConfig
         <p>Configuration to control how SageMaker captures inference data for batch transform jobs.</p>

        Attributes
       ----------------------
       destination_s3_uri: 	 <p>The Amazon S3 location being used to capture the data.</p>
       kms_key_id: 	 <p>The Amazon Resource Name (ARN) of a Amazon Web Services Key Management Service key that SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the batch transform job.</p> <p>The KmsKeyId can be any of the following formats: </p> <ul> <li> <p>Key ID: <code>1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Key ARN: <code>arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Alias name: <code>alias/ExampleAlias</code> </p> </li> <li> <p>Alias name ARN: <code>arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias</code> </p> </li> </ul>
       generate_inference_id: 	 <p>Flag that indicates whether to append inference id to the output.</p>
    """

    destination_s3_uri: str
    kms_key_id: Optional[str] = Unassigned()
    generate_inference_id: Optional[bool] = Unassigned()


class BatchDescribeModelPackageError(Base):
    """
    BatchDescribeModelPackageError
         <p>The error code and error description associated with the resource.</p>

        Attributes
       ----------------------
       error_code: 	 <p/>
       error_response: 	 <p/>
    """

    error_code: str
    error_response: str


class InferenceSpecification(Base):
    """
    InferenceSpecification
         <p>Defines how to perform inference generation after a training job is run.</p>

        Attributes
       ----------------------
       containers: 	 <p>The Amazon ECR registry path of the Docker image that contains the inference code.</p>
       supported_transform_instance_types: 	 <p>A list of the instance types on which a transformation job can be run or on which an endpoint can be deployed.</p> <p>This parameter is required for unversioned models, and optional for versioned models.</p>
       supported_realtime_inference_instance_types: 	 <p>A list of the instance types that are used to generate inferences in real-time.</p> <p>This parameter is required for unversioned models, and optional for versioned models.</p>
       supported_content_types: 	 <p>The supported MIME types for the input data.</p>
       supported_response_m_i_m_e_types: 	 <p>The supported MIME types for the output data.</p>
    """

    containers: List[ModelPackageContainerDefinition]
    supported_transform_instance_types: Optional[List[str]] = Unassigned()
    supported_realtime_inference_instance_types: Optional[List[str]] = Unassigned()
    supported_content_types: Optional[List[str]] = Unassigned()
    supported_response_m_i_m_e_types: Optional[List[str]] = Unassigned()


class BatchDescribeModelPackageSummary(Base):
    """
    BatchDescribeModelPackageSummary
         <p>Provides summary information about the model package.</p>

        Attributes
       ----------------------
       model_package_group_name: 	 <p>The group name for the model package</p>
       model_package_version: 	 <p>The version number of a versioned model.</p>
       model_package_arn: 	 <p>The Amazon Resource Name (ARN) of the model package.</p>
       model_package_description: 	 <p>The description of the model package.</p>
       creation_time: 	 <p>The creation time of the mortgage package summary.</p>
       inference_specification
       model_package_status: 	 <p>The status of the mortgage package.</p>
       model_approval_status: 	 <p>The approval status of the model.</p>
    """

    model_package_group_name: str
    model_package_arn: str
    creation_time: datetime.datetime
    inference_specification: InferenceSpecification
    model_package_status: str
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()


class MonitoringCsvDatasetFormat(Base):
    """
    MonitoringCsvDatasetFormat
         <p>Represents the CSV dataset format used when running a monitoring job.</p>

        Attributes
       ----------------------
       header: 	 <p>Indicates if the CSV data has a header.</p>
    """

    header: Optional[bool] = Unassigned()


class MonitoringJsonDatasetFormat(Base):
    """
    MonitoringJsonDatasetFormat
         <p>Represents the JSON dataset format used when running a monitoring job.</p>

        Attributes
       ----------------------
       line: 	 <p>Indicates if the file should be read as a JSON object per line. </p>
    """

    line: Optional[bool] = Unassigned()


class MonitoringParquetDatasetFormat(Base):
    """
    MonitoringParquetDatasetFormat
         <p>Represents the Parquet dataset format used when running a monitoring job.</p>

        Attributes
       ----------------------
    """


class MonitoringDatasetFormat(Base):
    """
    MonitoringDatasetFormat
         <p>Represents the dataset format used when running a monitoring job.</p>

        Attributes
       ----------------------
       csv: 	 <p>The CSV dataset used in the monitoring job.</p>
       json: 	 <p>The JSON dataset used in the monitoring job</p>
       parquet: 	 <p>The Parquet dataset used in the monitoring job</p>
    """

    csv: Optional[MonitoringCsvDatasetFormat] = Unassigned()
    json: Optional[MonitoringJsonDatasetFormat] = Unassigned()
    parquet: Optional[MonitoringParquetDatasetFormat] = Unassigned()


class BatchTransformInput(Base):
    """
    BatchTransformInput
         <p>Input object for the batch transform job.</p>

        Attributes
       ----------------------
       data_captured_destination_s3_uri: 	 <p>The Amazon S3 location being used to capture the data.</p>
       dataset_format: 	 <p>The dataset format for your batch transform job.</p>
       local_path: 	 <p>Path to the filesystem where the batch transform data is available to the container.</p>
       s3_input_mode: 	 <p>Whether the <code>Pipe</code> or <code>File</code> is used as the input mode for transferring data for the monitoring job. <code>Pipe</code> mode is recommended for large datasets. <code>File</code> mode is useful for small files that fit in memory. Defaults to <code>File</code>.</p>
       s3_data_distribution_type: 	 <p>Whether input data distributed in Amazon S3 is fully replicated or sharded by an S3 key. Defaults to <code>FullyReplicated</code> </p>
       features_attribute: 	 <p>The attributes of the input data that are the input features.</p>
       inference_attribute: 	 <p>The attribute of the input data that represents the ground truth label.</p>
       probability_attribute: 	 <p>In a classification problem, the attribute that represents the class probability.</p>
       probability_threshold_attribute: 	 <p>The threshold for the class probability to be evaluated as a positive result.</p>
       start_time_offset: 	 <p>If specified, monitoring jobs substract this time from the start time. For information about using offsets for scheduling monitoring jobs, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality-schedule.html">Schedule Model Quality Monitoring Jobs</a>.</p>
       end_time_offset: 	 <p>If specified, monitoring jobs subtract this time from the end time. For information about using offsets for scheduling monitoring jobs, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality-schedule.html">Schedule Model Quality Monitoring Jobs</a>.</p>
       exclude_features_attribute: 	 <p>The attributes of the input data to exclude from the analysis.</p>
    """

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


class BestObjectiveNotImproving(Base):
    """
    BestObjectiveNotImproving
         <p>A structure that keeps track of which training jobs launched by your hyperparameter tuning job are not improving model performance as evaluated against an objective function.</p>

        Attributes
       ----------------------
       max_number_of_training_jobs_not_improving: 	 <p>The number of training jobs that have failed to improve model performance by 1% or greater over prior training jobs as evaluated against an objective function.</p>
    """

    max_number_of_training_jobs_not_improving: Optional[int] = Unassigned()


class MetricsSource(Base):
    """
    MetricsSource
         <p>Details about the metrics source.</p>

        Attributes
       ----------------------
       content_type: 	 <p>The metric source content type.</p>
       content_digest: 	 <p>The hash key used for the metrics source.</p>
       s3_uri: 	 <p>The S3 URI for the metrics source.</p>
    """

    content_type: str
    s3_uri: str
    content_digest: Optional[str] = Unassigned()


class Bias(Base):
    """
    Bias
         <p>Contains bias metrics for a model.</p>

        Attributes
       ----------------------
       report: 	 <p>The bias report for a model</p>
       pre_training_report: 	 <p>The pre-training bias report for a model.</p>
       post_training_report: 	 <p>The post-training bias report for a model.</p>
    """

    report: Optional[MetricsSource] = Unassigned()
    pre_training_report: Optional[MetricsSource] = Unassigned()
    post_training_report: Optional[MetricsSource] = Unassigned()


class CapacitySize(Base):
    """
    CapacitySize
         <p>Specifies the type and size of the endpoint capacity to activate for a blue/green deployment, a rolling deployment, or a rollback strategy. You can specify your batches as either instance count or the overall percentage or your fleet.</p> <p>For a rollback strategy, if you don't specify the fields in this object, or if you set the <code>Value</code> to 100%, then SageMaker uses a blue/green rollback strategy and rolls all traffic back to the blue fleet.</p>

        Attributes
       ----------------------
       type: 	 <p>Specifies the endpoint capacity type.</p> <ul> <li> <p> <code>INSTANCE_COUNT</code>: The endpoint activates based on the number of instances.</p> </li> <li> <p> <code>CAPACITY_PERCENT</code>: The endpoint activates based on the specified percentage of capacity.</p> </li> </ul>
       value: 	 <p>Defines the capacity size, either as a number of instances or a capacity percentage.</p>
    """

    type: str
    value: int


class TrafficRoutingConfig(Base):
    """
    TrafficRoutingConfig
         <p>Defines the traffic routing strategy during an endpoint deployment to shift traffic from the old fleet to the new fleet.</p>

        Attributes
       ----------------------
       type: 	 <p>Traffic routing strategy type.</p> <ul> <li> <p> <code>ALL_AT_ONCE</code>: Endpoint traffic shifts to the new fleet in a single step. </p> </li> <li> <p> <code>CANARY</code>: Endpoint traffic shifts to the new fleet in two steps. The first step is the canary, which is a small portion of the traffic. The second step is the remainder of the traffic. </p> </li> <li> <p> <code>LINEAR</code>: Endpoint traffic shifts to the new fleet in n steps of a configurable size. </p> </li> </ul>
       wait_interval_in_seconds: 	 <p>The waiting time (in seconds) between incremental steps to turn on traffic on the new endpoint fleet.</p>
       canary_size: 	 <p>Batch size for the first step to turn on traffic on the new endpoint fleet. <code>Value</code> must be less than or equal to 50% of the variant's total instance count.</p>
       linear_step_size: 	 <p>Batch size for each step to turn on traffic on the new endpoint fleet. <code>Value</code> must be 10-50% of the variant's total instance count.</p>
    """

    type: str
    wait_interval_in_seconds: int
    canary_size: Optional[CapacitySize] = Unassigned()
    linear_step_size: Optional[CapacitySize] = Unassigned()


class BlueGreenUpdatePolicy(Base):
    """
    BlueGreenUpdatePolicy
         <p>Update policy for a blue/green deployment. If this update policy is specified, SageMaker creates a new fleet during the deployment while maintaining the old fleet. SageMaker flips traffic to the new fleet according to the specified traffic routing configuration. Only one update policy should be used in the deployment configuration. If no update policy is specified, SageMaker uses a blue/green deployment strategy with all at once traffic shifting by default.</p>

        Attributes
       ----------------------
       traffic_routing_configuration: 	 <p>Defines the traffic routing strategy to shift traffic from the old fleet to the new fleet during an endpoint deployment.</p>
       termination_wait_in_seconds: 	 <p>Additional waiting time in seconds after the completion of an endpoint deployment before terminating the old endpoint fleet. Default is 0.</p>
       maximum_execution_timeout_in_seconds: 	 <p>Maximum execution timeout for the deployment. Note that the timeout value should be larger than the total waiting time specified in <code>TerminationWaitInSeconds</code> and <code>WaitIntervalInSeconds</code>.</p>
    """

    traffic_routing_configuration: TrafficRoutingConfig
    termination_wait_in_seconds: Optional[int] = Unassigned()
    maximum_execution_timeout_in_seconds: Optional[int] = Unassigned()


class CacheHitResult(Base):
    """
    CacheHitResult
         <p>Details on the cache hit of a pipeline execution step.</p>

        Attributes
       ----------------------
       source_pipeline_execution_arn: 	 <p>The Amazon Resource Name (ARN) of the pipeline execution.</p>
    """

    source_pipeline_execution_arn: Optional[str] = Unassigned()


class OutputParameter(Base):
    """
    OutputParameter
         <p>An output parameter of a pipeline step.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the output parameter.</p>
       value: 	 <p>The value of the output parameter.</p>
    """

    name: str
    value: str


class CallbackStepMetadata(Base):
    """
    CallbackStepMetadata
         <p>Metadata about a callback step.</p>

        Attributes
       ----------------------
       callback_token: 	 <p>The pipeline generated token from the Amazon SQS queue.</p>
       sqs_queue_url: 	 <p>The URL of the Amazon Simple Queue Service (Amazon SQS) queue used by the callback step.</p>
       output_parameters: 	 <p>A list of the output parameters of the callback step.</p>
    """

    callback_token: Optional[str] = Unassigned()
    sqs_queue_url: Optional[str] = Unassigned()
    output_parameters: Optional[List[OutputParameter]] = Unassigned()


class TimeSeriesForecastingSettings(Base):
    """
    TimeSeriesForecastingSettings
         <p>Time series forecast settings for the SageMaker Canvas application.</p>

        Attributes
       ----------------------
       status: 	 <p>Describes whether time series forecasting is enabled or disabled in the Canvas application.</p>
       amazon_forecast_role_arn: 	 <p>The IAM role that Canvas passes to Amazon Forecast for time series forecasting. By default, Canvas uses the execution role specified in the <code>UserProfile</code> that launches the Canvas application. If an execution role is not specified in the <code>UserProfile</code>, Canvas uses the execution role specified in the Domain that owns the <code>UserProfile</code>. To allow time series forecasting, this IAM role should have the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/security-iam-awsmanpol-canvas.html#security-iam-awsmanpol-AmazonSageMakerCanvasForecastAccess"> AmazonSageMakerCanvasForecastAccess</a> policy attached and <code>forecast.amazonaws.com</code> added in the trust relationship as a service principal.</p>
    """

    status: Optional[str] = Unassigned()
    amazon_forecast_role_arn: Optional[str] = Unassigned()


class ModelRegisterSettings(Base):
    """
    ModelRegisterSettings
         <p>The model registry settings for the SageMaker Canvas application.</p>

        Attributes
       ----------------------
       status: 	 <p>Describes whether the integration to the model registry is enabled or disabled in the Canvas application.</p>
       cross_account_model_register_role_arn: 	 <p>The Amazon Resource Name (ARN) of the SageMaker model registry account. Required only to register model versions created by a different SageMaker Canvas Amazon Web Services account than the Amazon Web Services account in which SageMaker model registry is set up.</p>
    """

    status: Optional[str] = Unassigned()
    cross_account_model_register_role_arn: Optional[str] = Unassigned()


class WorkspaceSettings(Base):
    """
    WorkspaceSettings
         <p>The workspace settings for the SageMaker Canvas application.</p>

        Attributes
       ----------------------
       s3_artifact_path: 	 <p>The Amazon S3 bucket used to store artifacts generated by Canvas. Updating the Amazon S3 location impacts existing configuration settings, and Canvas users no longer have access to their artifacts. Canvas users must log out and log back in to apply the new location.</p>
       s3_kms_key_id: 	 <p>The Amazon Web Services Key Management Service (KMS) encryption key ID that is used to encrypt artifacts generated by Canvas in the Amazon S3 bucket.</p>
    """

    s3_artifact_path: Optional[str] = Unassigned()
    s3_kms_key_id: Optional[str] = Unassigned()


class IdentityProviderOAuthSetting(Base):
    """
    IdentityProviderOAuthSetting
         <p>The Amazon SageMaker Canvas application setting where you configure OAuth for connecting to an external data source, such as Snowflake.</p>

        Attributes
       ----------------------
       data_source_name: 	 <p>The name of the data source that you're connecting to. Canvas currently supports OAuth for Snowflake and Salesforce Data Cloud.</p>
       status: 	 <p>Describes whether OAuth for a data source is enabled or disabled in the Canvas application.</p>
       secret_arn: 	 <p>The ARN of an Amazon Web Services Secrets Manager secret that stores the credentials from your identity provider, such as the client ID and secret, authorization URL, and token URL. </p>
    """

    data_source_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    secret_arn: Optional[str] = Unassigned()


class DirectDeploySettings(Base):
    """
    DirectDeploySettings
         <p>The model deployment settings for the SageMaker Canvas application.</p> <note> <p>In order to enable model deployment for Canvas, the SageMaker Domain's or user profile's Amazon Web Services IAM execution role must have the <code>AmazonSageMakerCanvasDirectDeployAccess</code> policy attached. You can also turn on model deployment permissions through the SageMaker Domain's or user profile's settings in the SageMaker console.</p> </note>

        Attributes
       ----------------------
       status: 	 <p>Describes whether model deployment permissions are enabled or disabled in the Canvas application.</p>
    """

    status: Optional[str] = Unassigned()


class KendraSettings(Base):
    """
    KendraSettings
         <p>The Amazon SageMaker Canvas application setting where you configure document querying.</p>

        Attributes
       ----------------------
       status: 	 <p>Describes whether the document querying feature is enabled or disabled in the Canvas application.</p>
    """

    status: Optional[str] = Unassigned()


class GenerativeAiSettings(Base):
    """
    GenerativeAiSettings
         <p>The generative AI settings for the SageMaker Canvas application.</p> <p>Configure these settings for Canvas users starting chats with generative AI foundation models. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/canvas-fm-chat.html"> Use generative AI with foundation models</a>.</p>

        Attributes
       ----------------------
       amazon_bedrock_role_arn: 	 <p>The ARN of an Amazon Web Services IAM role that allows fine-tuning of large language models (LLMs) in Amazon Bedrock. The IAM role should have Amazon S3 read and write permissions, as well as a trust relationship that establishes <code>bedrock.amazonaws.com</code> as a service principal.</p>
    """

    amazon_bedrock_role_arn: Optional[str] = Unassigned()


class CanvasAppSettings(Base):
    """
    CanvasAppSettings
         <p>The SageMaker Canvas application settings.</p>

        Attributes
       ----------------------
       time_series_forecasting_settings: 	 <p>Time series forecast settings for the SageMaker Canvas application.</p>
       model_register_settings: 	 <p>The model registry settings for the SageMaker Canvas application.</p>
       workspace_settings: 	 <p>The workspace settings for the SageMaker Canvas application.</p>
       identity_provider_o_auth_settings: 	 <p>The settings for connecting to an external data source with OAuth.</p>
       direct_deploy_settings: 	 <p>The model deployment settings for the SageMaker Canvas application.</p>
       kendra_settings: 	 <p>The settings for document querying.</p>
       generative_ai_settings: 	 <p>The generative AI settings for the SageMaker Canvas application.</p>
    """

    time_series_forecasting_settings: Optional[TimeSeriesForecastingSettings] = (
        Unassigned()
    )
    model_register_settings: Optional[ModelRegisterSettings] = Unassigned()
    workspace_settings: Optional[WorkspaceSettings] = Unassigned()
    identity_provider_o_auth_settings: Optional[List[IdentityProviderOAuthSetting]] = (
        Unassigned()
    )
    direct_deploy_settings: Optional[DirectDeploySettings] = Unassigned()
    kendra_settings: Optional[KendraSettings] = Unassigned()
    generative_ai_settings: Optional[GenerativeAiSettings] = Unassigned()


class CaptureContentTypeHeader(Base):
    """
    CaptureContentTypeHeader
         <p>Configuration specifying how to treat different headers. If no headers are specified Amazon SageMaker will by default base64 encode when capturing the data.</p>

        Attributes
       ----------------------
       csv_content_types: 	 <p>The list of all content type headers that Amazon SageMaker will treat as CSV and capture accordingly.</p>
       json_content_types: 	 <p>The list of all content type headers that SageMaker will treat as JSON and capture accordingly.</p>
    """

    csv_content_types: Optional[List[str]] = Unassigned()
    json_content_types: Optional[List[str]] = Unassigned()


class CaptureOption(Base):
    """
    CaptureOption
         <p>Specifies data Model Monitor will capture.</p>

        Attributes
       ----------------------
       capture_mode: 	 <p>Specify the boundary of data to capture.</p>
    """

    capture_mode: str


class CategoricalParameter(Base):
    """
    CategoricalParameter
         <p>Environment parameters you want to benchmark your load test against.</p>

        Attributes
       ----------------------
       name: 	 <p>The Name of the environment variable.</p>
       value: 	 <p>The list of values you can pass.</p>
    """

    name: str
    value: List[str]


class CategoricalParameterRange(Base):
    """
    CategoricalParameterRange
         <p>A list of categorical hyperparameters to tune.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the categorical hyperparameter to tune.</p>
       values: 	 <p>A list of the categories for the hyperparameter.</p>
    """

    name: str
    values: List[str]


class CategoricalParameterRangeSpecification(Base):
    """
    CategoricalParameterRangeSpecification
         <p>Defines the possible values for a categorical hyperparameter.</p>

        Attributes
       ----------------------
       values: 	 <p>The allowed categories for the hyperparameter.</p>
    """

    values: List[str]


class ChannelSpecification(Base):
    """
    ChannelSpecification
         <p>Defines a named input source, called a channel, to be used by an algorithm.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the channel.</p>
       description: 	 <p>A brief description of the channel.</p>
       is_required: 	 <p>Indicates whether the channel is required by the algorithm.</p>
       supported_content_types: 	 <p>The supported MIME types for the data.</p>
       supported_compression_types: 	 <p>The allowed compression types, if data compression is used.</p>
       supported_input_modes: 	 <p>The allowed input mode, either FILE or PIPE.</p> <p>In FILE mode, Amazon SageMaker copies the data from the input source onto the local Amazon Elastic Block Store (Amazon EBS) volumes before starting your training algorithm. This is the most commonly used input mode.</p> <p>In PIPE mode, Amazon SageMaker streams input data from the source directly to your algorithm without using the EBS volume.</p>
    """

    name: str
    supported_content_types: List[str]
    supported_input_modes: List[str]
    description: Optional[str] = Unassigned()
    is_required: Optional[bool] = Unassigned()
    supported_compression_types: Optional[List[str]] = Unassigned()


class CheckpointConfig(Base):
    """
    CheckpointConfig
         <p>Contains information about the output location for managed spot training checkpoint data. </p>

        Attributes
       ----------------------
       s3_uri: 	 <p>Identifies the S3 path where you want SageMaker to store checkpoints. For example, <code>s3://bucket-name/key-name-prefix</code>.</p>
       local_path: 	 <p>(Optional) The local directory where checkpoints are written. The default directory is <code>/opt/ml/checkpoints/</code>. </p>
    """

    s3_uri: str
    local_path: Optional[str] = Unassigned()


class ClarifyCheckStepMetadata(Base):
    """
    ClarifyCheckStepMetadata
         <p>The container for the metadata for the ClarifyCheck step. For more information, see the topic on <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/build-and-manage-steps.html#step-type-clarify-check">ClarifyCheck step</a> in the <i>Amazon SageMaker Developer Guide</i>. </p>

        Attributes
       ----------------------
       check_type: 	 <p>The type of the Clarify Check step</p>
       baseline_used_for_drift_check_constraints: 	 <p>The Amazon S3 URI of baseline constraints file to be used for the drift check.</p>
       calculated_baseline_constraints: 	 <p>The Amazon S3 URI of the newly calculated baseline constraints file.</p>
       model_package_group_name: 	 <p>The model package group name.</p>
       violation_report: 	 <p>The Amazon S3 URI of the violation report if violations are detected.</p>
       check_job_arn: 	 <p>The Amazon Resource Name (ARN) of the check processing job that was run by this step's execution.</p>
       skip_check: 	 <p>This flag indicates if the drift check against the previous baseline will be skipped or not. If it is set to <code>False</code>, the previous baseline of the configured check type must be available.</p>
       register_new_baseline: 	 <p>This flag indicates if a newly calculated baseline can be accessed through step properties <code>BaselineUsedForDriftCheckConstraints</code> and <code>BaselineUsedForDriftCheckStatistics</code>. If it is set to <code>False</code>, the previous baseline of the configured check type must also be available. These can be accessed through the <code>BaselineUsedForDriftCheckConstraints</code> property. </p>
    """

    check_type: Optional[str] = Unassigned()
    baseline_used_for_drift_check_constraints: Optional[str] = Unassigned()
    calculated_baseline_constraints: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    violation_report: Optional[str] = Unassigned()
    check_job_arn: Optional[str] = Unassigned()
    skip_check: Optional[bool] = Unassigned()
    register_new_baseline: Optional[bool] = Unassigned()


class ClarifyInferenceConfig(Base):
    """
    ClarifyInferenceConfig
         <p>The inference configuration parameter for the model container.</p>

        Attributes
       ----------------------
       features_attribute: 	 <p>Provides the JMESPath expression to extract the features from a model container input in JSON Lines format. For example, if <code>FeaturesAttribute</code> is the JMESPath expression <code>'myfeatures'</code>, it extracts a list of features <code>[1,2,3]</code> from request data <code>'{"myfeatures":[1,2,3]}'</code>.</p>
       content_template: 	 <p>A template string used to format a JSON record into an acceptable model container input. For example, a <code>ContentTemplate</code> string <code>'{"myfeatures":$features}'</code> will format a list of features <code>[1,2,3]</code> into the record string <code>'{"myfeatures":[1,2,3]}'</code>. Required only when the model container input is in JSON Lines format.</p>
       max_record_count: 	 <p>The maximum number of records in a request that the model container can process when querying the model container for the predictions of a <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-create-endpoint.html#clarify-online-explainability-create-endpoint-synthetic">synthetic dataset</a>. A record is a unit of input data that inference can be made on, for example, a single line in CSV data. If <code>MaxRecordCount</code> is <code>1</code>, the model container expects one record per request. A value of 2 or greater means that the model expects batch requests, which can reduce overhead and speed up the inferencing process. If this parameter is not provided, the explainer will tune the record count per request according to the model container's capacity at runtime.</p>
       max_payload_in_m_b: 	 <p>The maximum payload size (MB) allowed of a request from the explainer to the model container. Defaults to <code>6</code> MB.</p>
       probability_index: 	 <p>A zero-based index used to extract a probability value (score) or list from model container output in CSV format. If this value is not provided, the entire model container output will be treated as a probability value (score) or list.</p> <p> <b>Example for a single class model:</b> If the model container output consists of a string-formatted prediction label followed by its probability: <code>'1,0.6'</code>, set <code>ProbabilityIndex</code> to <code>1</code> to select the probability value <code>0.6</code>.</p> <p> <b>Example for a multiclass model:</b> If the model container output consists of a string-formatted prediction label followed by its probability: <code>'"[\'cat\',\'dog\',\'fish\']","[0.1,0.6,0.3]"'</code>, set <code>ProbabilityIndex</code> to <code>1</code> to select the probability values <code>[0.1,0.6,0.3]</code>.</p>
       label_index: 	 <p>A zero-based index used to extract a label header or list of label headers from model container output in CSV format.</p> <p> <b>Example for a multiclass model:</b> If the model container output consists of label headers followed by probabilities: <code>'"[\'cat\',\'dog\',\'fish\']","[0.1,0.6,0.3]"'</code>, set <code>LabelIndex</code> to <code>0</code> to select the label headers <code>['cat','dog','fish']</code>.</p>
       probability_attribute: 	 <p>A JMESPath expression used to extract the probability (or score) from the model container output if the model container is in JSON Lines format.</p> <p> <b>Example</b>: If the model container output of a single request is <code>'{"predicted_label":1,"probability":0.6}'</code>, then set <code>ProbabilityAttribute</code> to <code>'probability'</code>.</p>
       label_attribute: 	 <p>A JMESPath expression used to locate the list of label headers in the model container output.</p> <p> <b>Example</b>: If the model container output of a batch request is <code>'{"labels":["cat","dog","fish"],"probability":[0.6,0.3,0.1]}'</code>, then set <code>LabelAttribute</code> to <code>'labels'</code> to extract the list of label headers <code>["cat","dog","fish"]</code> </p>
       label_headers: 	 <p>For multiclass classification problems, the label headers are the names of the classes. Otherwise, the label header is the name of the predicted label. These are used to help readability for the output of the <code>InvokeEndpoint</code> API. See the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-invoke-endpoint.html#clarify-online-explainability-response">response</a> section under <b>Invoke the endpoint</b> in the Developer Guide for more information. If there are no label headers in the model container output, provide them manually using this parameter.</p>
       feature_headers: 	 <p>The names of the features. If provided, these are included in the endpoint response payload to help readability of the <code>InvokeEndpoint</code> output. See the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-invoke-endpoint.html#clarify-online-explainability-response">Response</a> section under <b>Invoke the endpoint</b> in the Developer Guide for more information.</p>
       feature_types: 	 <p>A list of data types of the features (optional). Applicable only to NLP explainability. If provided, <code>FeatureTypes</code> must have at least one <code>'text'</code> string (for example, <code>['text']</code>). If <code>FeatureTypes</code> is not provided, the explainer infers the feature types based on the baseline data. The feature types are included in the endpoint response payload. For additional information see the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-invoke-endpoint.html#clarify-online-explainability-response">response</a> section under <b>Invoke the endpoint</b> in the Developer Guide for more information.</p>
    """

    features_attribute: Optional[str] = Unassigned()
    content_template: Optional[str] = Unassigned()
    max_record_count: Optional[int] = Unassigned()
    max_payload_in_m_b: Optional[int] = Unassigned()
    probability_index: Optional[int] = Unassigned()
    label_index: Optional[int] = Unassigned()
    probability_attribute: Optional[str] = Unassigned()
    label_attribute: Optional[str] = Unassigned()
    label_headers: Optional[List[str]] = Unassigned()
    feature_headers: Optional[List[str]] = Unassigned()
    feature_types: Optional[List[str]] = Unassigned()


class ClarifyShapBaselineConfig(Base):
    """
    ClarifyShapBaselineConfig
         <p>The configuration for the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-feature-attribute-shap-baselines.html">SHAP baseline</a> (also called the background or reference dataset) of the Kernal SHAP algorithm.</p> <note> <ul> <li> <p>The number of records in the baseline data determines the size of the synthetic dataset, which has an impact on latency of explainability requests. For more information, see the <b>Synthetic data</b> of <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-create-endpoint.html">Configure and create an endpoint</a>.</p> </li> <li> <p> <code>ShapBaseline</code> and <code>ShapBaselineUri</code> are mutually exclusive parameters. One or the either is required to configure a SHAP baseline. </p> </li> </ul> </note>

        Attributes
       ----------------------
       mime_type: 	 <p>The MIME type of the baseline data. Choose from <code>'text/csv'</code> or <code>'application/jsonlines'</code>. Defaults to <code>'text/csv'</code>.</p>
       shap_baseline: 	 <p>The inline SHAP baseline data in string format. <code>ShapBaseline</code> can have one or multiple records to be used as the baseline dataset. The format of the SHAP baseline file should be the same format as the training dataset. For example, if the training dataset is in CSV format and each record contains four features, and all features are numerical, then the format of the baseline data should also share these characteristics. For natural language processing (NLP) of text columns, the baseline value should be the value used to replace the unit of text specified by the <code>Granularity</code> of the <code>TextConfig</code> parameter. The size limit for <code>ShapBasline</code> is 4 KB. Use the <code>ShapBaselineUri</code> parameter if you want to provide more than 4 KB of baseline data.</p>
       shap_baseline_uri: 	 <p>The uniform resource identifier (URI) of the S3 bucket where the SHAP baseline file is stored. The format of the SHAP baseline file should be the same format as the format of the training dataset. For example, if the training dataset is in CSV format, and each record in the training dataset has four features, and all features are numerical, then the baseline file should also have this same format. Each record should contain only the features. If you are using a virtual private cloud (VPC), the <code>ShapBaselineUri</code> should be accessible to the VPC. For more information about setting up endpoints with Amazon Virtual Private Cloud, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/infrastructure-give-access.html">Give SageMaker access to Resources in your Amazon Virtual Private Cloud</a>.</p>
    """

    mime_type: Optional[str] = Unassigned()
    shap_baseline: Optional[str] = Unassigned()
    shap_baseline_uri: Optional[str] = Unassigned()


class ClarifyTextConfig(Base):
    """
    ClarifyTextConfig
         <p>A parameter used to configure the SageMaker Clarify explainer to treat text features as text so that explanations are provided for individual units of text. Required only for natural language processing (NLP) explainability. </p>

        Attributes
       ----------------------
       language: 	 <p>Specifies the language of the text features in <a href=" https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes">ISO 639-1</a> or <a href="https://en.wikipedia.org/wiki/ISO_639-3">ISO 639-3</a> code of a supported language. </p> <note> <p>For a mix of multiple languages, use code <code>'xx'</code>.</p> </note>
       granularity: 	 <p>The unit of granularity for the analysis of text features. For example, if the unit is <code>'token'</code>, then each token (like a word in English) of the text is treated as a feature. SHAP values are computed for each unit/feature.</p>
    """

    language: str
    granularity: str


class ClarifyShapConfig(Base):
    """
    ClarifyShapConfig
         <p>The configuration for SHAP analysis using SageMaker Clarify Explainer.</p>

        Attributes
       ----------------------
       shap_baseline_config: 	 <p>The configuration for the SHAP baseline of the Kernal SHAP algorithm.</p>
       number_of_samples: 	 <p>The number of samples to be used for analysis by the Kernal SHAP algorithm. </p> <note> <p>The number of samples determines the size of the synthetic dataset, which has an impact on latency of explainability requests. For more information, see the <b>Synthetic data</b> of <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-create-endpoint.html">Configure and create an endpoint</a>.</p> </note>
       use_logit: 	 <p>A Boolean toggle to indicate if you want to use the logit function (true) or log-odds units (false) for model predictions. Defaults to false.</p>
       seed: 	 <p>The starting value used to initialize the random number generator in the explainer. Provide a value for this parameter to obtain a deterministic SHAP result.</p>
       text_config: 	 <p>A parameter that indicates if text features are treated as text and explanations are provided for individual units of text. Required for natural language processing (NLP) explainability only.</p>
    """

    shap_baseline_config: ClarifyShapBaselineConfig
    number_of_samples: Optional[int] = Unassigned()
    use_logit: Optional[bool] = Unassigned()
    seed: Optional[int] = Unassigned()
    text_config: Optional[ClarifyTextConfig] = Unassigned()


class ClarifyExplainerConfig(Base):
    """
    ClarifyExplainerConfig
         <p>The configuration parameters for the SageMaker Clarify explainer.</p>

        Attributes
       ----------------------
       enable_explanations: 	 <p>A JMESPath boolean expression used to filter which records to explain. Explanations are activated by default. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-online-explainability-create-endpoint.html#clarify-online-explainability-create-endpoint-enable"> <code>EnableExplanations</code> </a>for additional information.</p>
       inference_config: 	 <p>The inference configuration parameter for the model container.</p>
       shap_config: 	 <p>The configuration for SHAP analysis.</p>
    """

    shap_config: ClarifyShapConfig
    enable_explanations: Optional[str] = Unassigned()
    inference_config: Optional[ClarifyInferenceConfig] = Unassigned()


class ClusterLifeCycleConfig(Base):
    """
    ClusterLifeCycleConfig
         <p>The LifeCycle configuration for a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       source_s3_uri: 	 <p>An Amazon S3 bucket path where your LifeCycle scripts are stored.</p>
       on_create: 	 <p>The directory of the LifeCycle script under <code>SourceS3Uri</code>. This LifeCycle script runs during cluster creation.</p>
    """

    source_s3_uri: str
    on_create: str


class ClusterInstanceGroupDetails(Base):
    """
    ClusterInstanceGroupDetails
         <p>Details of an instance group in a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       current_count: 	 <p>The number of instances that are currently in the instance group of a SageMaker HyperPod cluster.</p>
       target_count: 	 <p>The number of instances you specified to add to the instance group of a SageMaker HyperPod cluster.</p>
       instance_group_name: 	 <p>The name of the instance group of a SageMaker HyperPod cluster.</p>
       instance_type: 	 <p>The instance type of the instance group of a SageMaker HyperPod cluster.</p>
       life_cycle_config: 	 <p>Details of LifeCycle configuration for the instance group.</p>
       execution_role: 	 <p>The execution role for the instance group to assume.</p>
       threads_per_core: 	 <p>The number you specified to <code>TreadsPerCore</code> in <code>CreateCluster</code> for enabling or disabling multithreading. For instance types that support multithreading, you can specify 1 for disabling multithreading and 2 for enabling multithreading. For more information, see the reference table of <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html">CPU cores and threads per CPU core per instance type</a> in the <i>Amazon Elastic Compute Cloud User Guide</i>.</p>
    """

    current_count: Optional[int] = Unassigned()
    target_count: Optional[int] = Unassigned()
    instance_group_name: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    life_cycle_config: Optional[ClusterLifeCycleConfig] = Unassigned()
    execution_role: Optional[str] = Unassigned()
    threads_per_core: Optional[int] = Unassigned()


class ClusterInstanceGroupSpecification(Base):
    """
    ClusterInstanceGroupSpecification
         <p>The specifications of an instance group that you need to define.</p>

        Attributes
       ----------------------
       instance_count: 	 <p>Specifies the number of instances to add to the instance group of a SageMaker HyperPod cluster.</p>
       instance_group_name: 	 <p>Specifies the name of the instance group.</p>
       instance_type: 	 <p>Specifies the instance type of the instance group.</p>
       life_cycle_config: 	 <p>Specifies the LifeCycle configuration for the instance group.</p>
       execution_role: 	 <p>Specifies an IAM execution role to be assumed by the instance group.</p>
       threads_per_core: 	 <p>Specifies the value for <b>Threads per core</b>. For instance types that support multithreading, you can specify <code>1</code> for disabling multithreading and <code>2</code> for enabling multithreading. For instance types that doesn't support multithreading, specify <code>1</code>. For more information, see the reference table of <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/cpu-options-supported-instances-values.html">CPU cores and threads per CPU core per instance type</a> in the <i>Amazon Elastic Compute Cloud User Guide</i>.</p>
    """

    instance_count: int
    instance_group_name: str
    instance_type: str
    life_cycle_config: ClusterLifeCycleConfig
    execution_role: str
    threads_per_core: Optional[int] = Unassigned()


class ClusterInstanceStatusDetails(Base):
    """
    ClusterInstanceStatusDetails
         <p>Details of an instance in a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       status: 	 <p>The status of an instance in a SageMaker HyperPod cluster.</p>
       message: 	 <p>The message from an instance in a SageMaker HyperPod cluster.</p>
    """

    status: str
    message: Optional[str] = Unassigned()


class ClusterNodeDetails(Base):
    """
    ClusterNodeDetails
         <p>Details of an instance (also called a <i>node</i> interchangeably) in a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       instance_group_name: 	 <p>The instance group name in which the instance is.</p>
       instance_id: 	 <p>The ID of the instance.</p>
       instance_status: 	 <p>The status of the instance.</p>
       instance_type: 	 <p>The type of the instance.</p>
       launch_time: 	 <p>The time when the instance is launched.</p>
       life_cycle_config: 	 <p>The LifeCycle configuration applied to the instance.</p>
       threads_per_core: 	 <p>The number of threads per CPU core you specified under <code>CreateCluster</code>.</p>
    """

    instance_group_name: Optional[str] = Unassigned()
    instance_id: Optional[str] = Unassigned()
    instance_status: Optional[ClusterInstanceStatusDetails] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    launch_time: Optional[datetime.datetime] = Unassigned()
    life_cycle_config: Optional[ClusterLifeCycleConfig] = Unassigned()
    threads_per_core: Optional[int] = Unassigned()


class ClusterNodeSummary(Base):
    """
    ClusterNodeSummary
         <p>Lists a summary of the properties of an instance (also called a <i>node</i> interchangeably) of a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       instance_group_name: 	 <p>The name of the instance group in which the instance is.</p>
       instance_id: 	 <p>The ID of the instance.</p>
       instance_type: 	 <p>The type of the instance.</p>
       launch_time: 	 <p>The time when the instance is launched.</p>
       instance_status: 	 <p>The status of the instance.</p>
    """

    instance_group_name: str
    instance_id: str
    instance_type: str
    launch_time: datetime.datetime
    instance_status: ClusterInstanceStatusDetails


class ClusterSummary(Base):
    """
    ClusterSummary
         <p>Lists a summary of the properties of a SageMaker HyperPod cluster.</p>

        Attributes
       ----------------------
       cluster_arn: 	 <p>The Amazon Resource Name (ARN) of the SageMaker HyperPod cluster.</p>
       cluster_name: 	 <p>The name of the SageMaker HyperPod cluster.</p>
       creation_time: 	 <p>The time when the SageMaker HyperPod cluster is created.</p>
       cluster_status: 	 <p>The status of the SageMaker HyperPod cluster.</p>
    """

    cluster_arn: str
    cluster_name: str
    creation_time: datetime.datetime
    cluster_status: str


class CodeEditorAppSettings(Base):
    """
    CodeEditorAppSettings
         <p>The Code Editor application settings.</p> <p>For more information about Code Editor, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/code-editor.html">Get started with Code Editor in Amazon SageMaker</a>.</p>

        Attributes
       ----------------------
       default_resource_spec
       lifecycle_config_arns: 	 <p>The Amazon Resource Name (ARN) of the Code Editor application lifecycle configuration.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    lifecycle_config_arns: Optional[List[str]] = Unassigned()


class CodeRepository(Base):
    """
    CodeRepository
         <p>A Git repository that SageMaker automatically displays to users for cloning in the JupyterServer application.</p>

        Attributes
       ----------------------
       repository_url: 	 <p>The URL of the Git repository.</p>
    """

    repository_url: str


class GitConfig(Base):
    """
    GitConfig
         <p>Specifies configuration details for a Git repository in your Amazon Web Services account.</p>

        Attributes
       ----------------------
       repository_url: 	 <p>The URL where the Git repository is located.</p>
       branch: 	 <p>The default branch for the Git repository.</p>
       secret_arn: 	 <p>The Amazon Resource Name (ARN) of the Amazon Web Services Secrets Manager secret that contains the credentials used to access the git repository. The secret must have a staging label of <code>AWSCURRENT</code> and must be in the following format:</p> <p> <code>{"username": <i>UserName</i>, "password": <i>Password</i>}</code> </p>
    """

    repository_url: str
    branch: Optional[str] = Unassigned()
    secret_arn: Optional[str] = Unassigned()


class CodeRepositorySummary(Base):
    """
    CodeRepositorySummary
         <p>Specifies summary information about a Git repository.</p>

        Attributes
       ----------------------
       code_repository_name: 	 <p>The name of the Git repository.</p>
       code_repository_arn: 	 <p>The Amazon Resource Name (ARN) of the Git repository.</p>
       creation_time: 	 <p>The date and time that the Git repository was created.</p>
       last_modified_time: 	 <p>The date and time that the Git repository was last modified.</p>
       git_config: 	 <p>Configuration details for the Git repository, including the URL where it is located and the ARN of the Amazon Web Services Secrets Manager secret that contains the credentials used to access the repository.</p>
    """

    code_repository_name: str
    code_repository_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    git_config: Optional[GitConfig] = Unassigned()


class CognitoConfig(Base):
    """
    CognitoConfig
         <p>Use this parameter to configure your Amazon Cognito workforce. A single Cognito workforce is created using and corresponds to a single <a href="https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html"> Amazon Cognito user pool</a>.</p>

        Attributes
       ----------------------
       user_pool: 	 <p>A <a href="https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html"> user pool</a> is a user directory in Amazon Cognito. With a user pool, your users can sign in to your web or mobile app through Amazon Cognito. Your users can also sign in through social identity providers like Google, Facebook, Amazon, or Apple, and through SAML identity providers.</p>
       client_id: 	 <p>The client ID for your Amazon Cognito user pool.</p>
    """

    user_pool: str
    client_id: str


class CognitoMemberDefinition(Base):
    """
    CognitoMemberDefinition
         <p>Identifies a Amazon Cognito user group. A user group can be used in on or more work teams.</p>

        Attributes
       ----------------------
       user_pool: 	 <p>An identifier for a user pool. The user pool must be in the same region as the service that you are calling.</p>
       user_group: 	 <p>An identifier for a user group.</p>
       client_id: 	 <p>An identifier for an application client. You must create the app client ID using Amazon Cognito.</p>
    """

    user_pool: str
    user_group: str
    client_id: str


class VectorConfig(Base):
    """
    VectorConfig
         <p>Configuration for your vector collection type.</p>

        Attributes
       ----------------------
       dimension: 	 <p>The number of elements in your vector.</p>
    """

    dimension: int


class CollectionConfig(Base):
    """
    CollectionConfig
         <p>Configuration for your collection.</p>

        Attributes
       ----------------------
       vector_config: 	 <p>Configuration for your vector collection type.</p> <ul> <li> <p> <code>Dimension</code>: The number of elements in your vector.</p> </li> </ul>
    """

    vector_config: Optional[VectorConfig] = Unassigned()


class CollectionConfiguration(Base):
    """
    CollectionConfiguration
         <p>Configuration information for the Amazon SageMaker Debugger output tensor collections.</p>

        Attributes
       ----------------------
       collection_name: 	 <p>The name of the tensor collection. The name must be unique relative to other rule configuration names.</p>
       collection_parameters: 	 <p>Parameter values for the tensor collection. The allowed parameters are <code>"name"</code>, <code>"include_regex"</code>, <code>"reduction_config"</code>, <code>"save_config"</code>, <code>"tensor_names"</code>, and <code>"save_histogram"</code>.</p>
    """

    collection_name: Optional[str] = Unassigned()
    collection_parameters: Optional[Dict[str, str]] = Unassigned()


class CompilationJobSummary(Base):
    """
    CompilationJobSummary
         <p>A summary of a model compilation job.</p>

        Attributes
       ----------------------
       compilation_job_name: 	 <p>The name of the model compilation job that you want a summary for.</p>
       compilation_job_arn: 	 <p>The Amazon Resource Name (ARN) of the model compilation job.</p>
       creation_time: 	 <p>The time when the model compilation job was created.</p>
       compilation_start_time: 	 <p>The time when the model compilation job started.</p>
       compilation_end_time: 	 <p>The time when the model compilation job completed.</p>
       compilation_target_device: 	 <p>The type of device that the model will run on after the compilation job has completed.</p>
       compilation_target_platform_os: 	 <p>The type of OS that the model will run on after the compilation job has completed.</p>
       compilation_target_platform_arch: 	 <p>The type of architecture that the model will run on after the compilation job has completed.</p>
       compilation_target_platform_accelerator: 	 <p>The type of accelerator that the model will run on after the compilation job has completed.</p>
       last_modified_time: 	 <p>The time when the model compilation job was last modified.</p>
       compilation_job_status: 	 <p>The status of the model compilation job.</p>
    """

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


class ConditionStepMetadata(Base):
    """
    ConditionStepMetadata
         <p>Metadata for a Condition step.</p>

        Attributes
       ----------------------
       outcome: 	 <p>The outcome of the Condition step evaluation.</p>
    """

    outcome: Optional[str] = Unassigned()


class ConflictException(Base):
    """
    ConflictException
         <p>There was a conflict when you attempted to modify a SageMaker entity such as an <code>Experiment</code> or <code>Artifact</code>.</p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class RepositoryAuthConfig(Base):
    """
    RepositoryAuthConfig
         <p>Specifies an authentication configuration for the private docker registry where your model image is hosted. Specify a value for this property only if you specified <code>Vpc</code> as the value for the <code>RepositoryAccessMode</code> field of the <code>ImageConfig</code> object that you passed to a call to <code>CreateModel</code> and the private Docker registry where the model image is hosted requires authentication.</p>

        Attributes
       ----------------------
       repository_credentials_provider_arn: 	 <p>The Amazon Resource Name (ARN) of an Amazon Web Services Lambda function that provides credentials to authenticate to the private Docker registry where your model image is hosted. For information about how to create an Amazon Web Services Lambda function, see <a href="https://docs.aws.amazon.com/lambda/latest/dg/getting-started-create-function.html">Create a Lambda function with the console</a> in the <i>Amazon Web Services Lambda Developer Guide</i>.</p>
    """

    repository_credentials_provider_arn: str


class ImageConfig(Base):
    """
    ImageConfig
         <p>Specifies whether the model container is in Amazon ECR or a private Docker registry accessible from your Amazon Virtual Private Cloud (VPC).</p>

        Attributes
       ----------------------
       repository_access_mode: 	 <p>Set this to one of the following values:</p> <ul> <li> <p> <code>Platform</code> - The model image is hosted in Amazon ECR.</p> </li> <li> <p> <code>Vpc</code> - The model image is hosted in a private Docker registry in your VPC.</p> </li> </ul>
       repository_auth_config: 	 <p>(Optional) Specifies an authentication configuration for the private docker registry where your model image is hosted. Specify a value for this property only if you specified <code>Vpc</code> as the value for the <code>RepositoryAccessMode</code> field, and the private Docker registry where the model image is hosted requires authentication.</p>
    """

    repository_access_mode: str
    repository_auth_config: Optional[RepositoryAuthConfig] = Unassigned()


class MultiModelConfig(Base):
    """
    MultiModelConfig
         <p>Specifies additional configuration for hosting multi-model endpoints.</p>

        Attributes
       ----------------------
       model_cache_setting: 	 <p>Whether to cache models for a multi-model endpoint. By default, multi-model endpoints cache models so that a model does not have to be loaded into memory each time it is invoked. Some use cases do not benefit from model caching. For example, if an endpoint hosts a large number of models that are each invoked infrequently, the endpoint might perform better if you disable model caching. To disable model caching, set the value of this parameter to <code>Disabled</code>.</p>
    """

    model_cache_setting: Optional[str] = Unassigned()


class ContainerDefinition(Base):
    """
    ContainerDefinition
         <p>Describes the container, as part of model definition.</p>

        Attributes
       ----------------------
       container_hostname: 	 <p>This parameter is ignored for models that contain only a <code>PrimaryContainer</code>.</p> <p>When a <code>ContainerDefinition</code> is part of an inference pipeline, the value of the parameter uniquely identifies the container for the purposes of logging and metrics. For information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/inference-pipeline-logs-metrics.html">Use Logs and Metrics to Monitor an Inference Pipeline</a>. If you don't specify a value for this parameter for a <code>ContainerDefinition</code> that is part of an inference pipeline, a unique name is automatically assigned based on the position of the <code>ContainerDefinition</code> in the pipeline. If you specify a value for the <code>ContainerHostName</code> for any <code>ContainerDefinition</code> that is part of an inference pipeline, you must specify a value for the <code>ContainerHostName</code> parameter of every <code>ContainerDefinition</code> in that pipeline.</p>
       image: 	 <p>The path where inference code is stored. This can be either in Amazon EC2 Container Registry or in a Docker registry that is accessible from the same VPC that you configure for your endpoint. If you are using your own custom algorithm instead of an algorithm provided by SageMaker, the inference code must meet SageMaker requirements. SageMaker supports both <code>registry/repository[:tag]</code> and <code>registry/repository[@digest]</code> image path formats. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html">Using Your Own Algorithms with Amazon SageMaker</a>. </p> <note> <p>The model artifacts in an Amazon S3 bucket and the Docker image for inference container in Amazon EC2 Container Registry must be in the same region as the model or endpoint you are creating.</p> </note>
       image_config: 	 <p>Specifies whether the model container is in Amazon ECR or a private Docker registry accessible from your Amazon Virtual Private Cloud (VPC). For information about storing containers in a private Docker registry, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-containers-inference-private.html">Use a Private Docker Registry for Real-Time Inference Containers</a>. </p> <note> <p>The model artifacts in an Amazon S3 bucket and the Docker image for inference container in Amazon EC2 Container Registry must be in the same region as the model or endpoint you are creating.</p> </note>
       mode: 	 <p>Whether the container hosts a single model or multiple models.</p>
       model_data_url: 	 <p>The S3 path where the model artifacts, which result from model training, are stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix). The S3 path is required for SageMaker built-in algorithms, but not if you use your own algorithms. For more information on built-in algorithms, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-algo-docker-registry-paths.html">Common Parameters</a>. </p> <note> <p>The model artifacts must be in an S3 bucket that is in the same region as the model or endpoint you are creating.</p> </note> <p>If you provide a value for this parameter, SageMaker uses Amazon Web Services Security Token Service to download model artifacts from the S3 path you provide. Amazon Web Services STS is activated in your Amazon Web Services account by default. If you previously deactivated Amazon Web Services STS for a region, you need to reactivate Amazon Web Services STS for that region. For more information, see <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_enable-regions.html">Activating and Deactivating Amazon Web Services STS in an Amazon Web Services Region</a> in the <i>Amazon Web Services Identity and Access Management User Guide</i>.</p> <important> <p>If you use a built-in algorithm to create a model, SageMaker requires that you provide a S3 path to the model artifacts in <code>ModelDataUrl</code>.</p> </important>
       model_data_source: 	 <p>Specifies the location of ML model data to deploy.</p> <note> <p>Currently you cannot use <code>ModelDataSource</code> in conjunction with SageMaker batch transform, SageMaker serverless endpoints, SageMaker multi-model endpoints, and SageMaker Marketplace.</p> </note>
       environment: 	 <p>The environment variables to set in the Docker container.</p> <p>The maximum length of each key and value in the <code>Environment</code> map is 1024 bytes. The maximum length of all keys and values in the map, combined, is 32 KB. If you pass multiple containers to a <code>CreateModel</code> request, then the maximum length of all of their maps, combined, is also 32 KB.</p>
       model_package_name: 	 <p>The name or Amazon Resource Name (ARN) of the model package to use to create the model.</p>
       inference_specification_name: 	 <p>The inference specification name in the model package version.</p>
       multi_model_config: 	 <p>Specifies additional configuration for multi-model endpoints.</p>
    """

    container_hostname: Optional[str] = Unassigned()
    image: Optional[str] = Unassigned()
    image_config: Optional[ImageConfig] = Unassigned()
    mode: Optional[str] = Unassigned()
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    model_package_name: Optional[str] = Unassigned()
    inference_specification_name: Optional[str] = Unassigned()
    multi_model_config: Optional[MultiModelConfig] = Unassigned()


class ContextSource(Base):
    """
    ContextSource
         <p>A structure describing the source of a context.</p>

        Attributes
       ----------------------
       source_uri: 	 <p>The URI of the source.</p>
       source_type: 	 <p>The type of the source.</p>
       source_id: 	 <p>The ID of the source.</p>
    """

    source_uri: str
    source_type: Optional[str] = Unassigned()
    source_id: Optional[str] = Unassigned()


class ContextSummary(Base):
    """
    ContextSummary
         <p>Lists a summary of the properties of a context. A context provides a logical grouping of other entities.</p>

        Attributes
       ----------------------
       context_arn: 	 <p>The Amazon Resource Name (ARN) of the context.</p>
       context_name: 	 <p>The name of the context.</p>
       source: 	 <p>The source of the context.</p>
       context_type: 	 <p>The type of the context.</p>
       creation_time: 	 <p>When the context was created.</p>
       last_modified_time: 	 <p>When the context was last modified.</p>
    """

    context_arn: Optional[str] = Unassigned()
    context_name: Optional[str] = Unassigned()
    source: Optional[ContextSource] = Unassigned()
    context_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class ContinuousParameterRange(Base):
    """
    ContinuousParameterRange
         <p>A list of continuous hyperparameters to tune.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the continuous hyperparameter to tune.</p>
       min_value: 	 <p>The minimum value for the hyperparameter. The tuning job uses floating-point values between this value and <code>MaxValue</code>for tuning.</p>
       max_value: 	 <p>The maximum value for the hyperparameter. The tuning job uses floating-point values between <code>MinValue</code> value and this value for tuning.</p>
       scaling_type: 	 <p>The scale that hyperparameter tuning uses to search the hyperparameter range. For information about choosing a hyperparameter scale, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-ranges.html#scaling-type">Hyperparameter Scaling</a>. One of the following values:</p> <dl> <dt>Auto</dt> <dd> <p>SageMaker hyperparameter tuning chooses the best scale for the hyperparameter.</p> </dd> <dt>Linear</dt> <dd> <p>Hyperparameter tuning searches the values in the hyperparameter range by using a linear scale.</p> </dd> <dt>Logarithmic</dt> <dd> <p>Hyperparameter tuning searches the values in the hyperparameter range by using a logarithmic scale.</p> <p>Logarithmic scaling works only for ranges that have only values greater than 0.</p> </dd> <dt>ReverseLogarithmic</dt> <dd> <p>Hyperparameter tuning searches the values in the hyperparameter range by using a reverse logarithmic scale.</p> <p>Reverse logarithmic scaling works only for ranges that are entirely within the range 0&lt;=x&lt;1.0.</p> </dd> </dl>
    """

    name: str
    min_value: str
    max_value: str
    scaling_type: Optional[str] = Unassigned()


class ContinuousParameterRangeSpecification(Base):
    """
    ContinuousParameterRangeSpecification
         <p>Defines the possible values for a continuous hyperparameter.</p>

        Attributes
       ----------------------
       min_value: 	 <p>The minimum floating-point value allowed.</p>
       max_value: 	 <p>The maximum floating-point value allowed.</p>
    """

    min_value: str
    max_value: str


class ConvergenceDetected(Base):
    """
    ConvergenceDetected
         <p>A flag to indicating that automatic model tuning (AMT) has detected model convergence, defined as a lack of significant improvement (1% or less) against an objective metric.</p>

        Attributes
       ----------------------
       complete_on_convergence: 	 <p>A flag to stop a tuning job once AMT has detected that the job has converged.</p>
    """

    complete_on_convergence: Optional[str] = Unassigned()


class MetadataProperties(Base):
    """
    MetadataProperties
         <p>Metadata properties of the tracking entity, trial, or trial component.</p>

        Attributes
       ----------------------
       commit_id: 	 <p>The commit ID.</p>
       repository: 	 <p>The repository.</p>
       generated_by: 	 <p>The entity this entity was generated by.</p>
       project_id: 	 <p>The project ID.</p>
    """

    commit_id: Optional[str] = Unassigned()
    repository: Optional[str] = Unassigned()
    generated_by: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()


class IntegerParameterRangeSpecification(Base):
    """
    IntegerParameterRangeSpecification
         <p>Defines the possible values for an integer hyperparameter.</p>

        Attributes
       ----------------------
       min_value: 	 <p>The minimum integer value allowed.</p>
       max_value: 	 <p>The maximum integer value allowed.</p>
    """

    min_value: str
    max_value: str


class ParameterRange(Base):
    """
    ParameterRange
         <p>Defines the possible values for categorical, continuous, and integer hyperparameters to be used by an algorithm.</p>

        Attributes
       ----------------------
       integer_parameter_range_specification: 	 <p>A <code>IntegerParameterRangeSpecification</code> object that defines the possible values for an integer hyperparameter.</p>
       continuous_parameter_range_specification: 	 <p>A <code>ContinuousParameterRangeSpecification</code> object that defines the possible values for a continuous hyperparameter.</p>
       categorical_parameter_range_specification: 	 <p>A <code>CategoricalParameterRangeSpecification</code> object that defines the possible values for a categorical hyperparameter.</p>
    """

    integer_parameter_range_specification: Optional[
        IntegerParameterRangeSpecification
    ] = Unassigned()
    continuous_parameter_range_specification: Optional[
        ContinuousParameterRangeSpecification
    ] = Unassigned()
    categorical_parameter_range_specification: Optional[
        CategoricalParameterRangeSpecification
    ] = Unassigned()


class HyperParameterSpecification(Base):
    """
    HyperParameterSpecification
         <p>Defines a hyperparameter to be used by an algorithm.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of this hyperparameter. The name must be unique.</p>
       description: 	 <p>A brief description of the hyperparameter.</p>
       type: 	 <p>The type of this hyperparameter. The valid types are <code>Integer</code>, <code>Continuous</code>, <code>Categorical</code>, and <code>FreeText</code>.</p>
       range: 	 <p>The allowed range for this hyperparameter.</p>
       is_tunable: 	 <p>Indicates whether this hyperparameter is tunable in a hyperparameter tuning job.</p>
       is_required: 	 <p>Indicates whether this hyperparameter is required.</p>
       default_value: 	 <p>The default value for this hyperparameter. If a default value is specified, a hyperparameter cannot be required.</p>
    """

    name: str
    type: str
    description: Optional[str] = Unassigned()
    range: Optional[ParameterRange] = Unassigned()
    is_tunable: Optional[bool] = Unassigned()
    is_required: Optional[bool] = Unassigned()
    default_value: Optional[str] = Unassigned()


class HyperParameterTuningJobObjective(Base):
    """
    HyperParameterTuningJobObjective
         <p>Defines the objective metric for a hyperparameter tuning job. Hyperparameter tuning uses the value of this metric to evaluate the training jobs it launches, and returns the training job that results in either the highest or lowest value for this metric, depending on the value you specify for the <code>Type</code> parameter. If you want to define a custom objective metric, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-metrics-variables.html">Define metrics and environment variables</a>.</p>

        Attributes
       ----------------------
       type: 	 <p>Whether to minimize or maximize the objective metric.</p>
       metric_name: 	 <p>The name of the metric to use for the objective metric.</p>
    """

    type: str
    metric_name: str


class TrainingSpecification(Base):
    """
    TrainingSpecification
         <p>Defines how the algorithm is used for a training job.</p>

        Attributes
       ----------------------
       training_image: 	 <p>The Amazon ECR registry path of the Docker image that contains the training algorithm.</p>
       training_image_digest: 	 <p>An MD5 hash of the training algorithm that identifies the Docker image used for training.</p>
       supported_hyper_parameters: 	 <p>A list of the <code>HyperParameterSpecification</code> objects, that define the supported hyperparameters. This is required if the algorithm supports automatic model tuning.&gt;</p>
       supported_training_instance_types: 	 <p>A list of the instance types that this algorithm can use for training.</p>
       supports_distributed_training: 	 <p>Indicates whether the algorithm supports distributed training. If set to false, buyers can't request more than one instance during training.</p>
       metric_definitions: 	 <p>A list of <code>MetricDefinition</code> objects, which are used for parsing metrics generated by the algorithm.</p>
       training_channels: 	 <p>A list of <code>ChannelSpecification</code> objects, which specify the input sources to be used by the algorithm.</p>
       supported_tuning_job_objective_metrics: 	 <p>A list of the metrics that the algorithm emits that can be used as the objective metric in a hyperparameter tuning job.</p>
       additional_s3_data_source: 	 <p>The additional data source used during the training job.</p>
    """

    training_image: str
    supported_training_instance_types: List[str]
    training_channels: List[ChannelSpecification]
    training_image_digest: Optional[str] = Unassigned()
    supported_hyper_parameters: Optional[List[HyperParameterSpecification]] = (
        Unassigned()
    )
    supports_distributed_training: Optional[bool] = Unassigned()
    metric_definitions: Optional[List[MetricDefinition]] = Unassigned()
    supported_tuning_job_objective_metrics: Optional[
        List[HyperParameterTuningJobObjective]
    ] = Unassigned()
    additional_s3_data_source: Optional[AdditionalS3DataSource] = Unassigned()


class ModelDeployConfig(Base):
    """
    ModelDeployConfig
         <p>Specifies how to generate the endpoint name for an automatic one-click Autopilot model deployment.</p>

        Attributes
       ----------------------
       auto_generate_endpoint_name: 	 <p>Set to <code>True</code> to automatically generate an endpoint name for a one-click Autopilot model deployment; set to <code>False</code> otherwise. The default value is <code>False</code>.</p> <note> <p>If you set <code>AutoGenerateEndpointName</code> to <code>True</code>, do not specify the <code>EndpointName</code>; otherwise a 400 error is thrown.</p> </note>
       endpoint_name: 	 <p>Specifies the endpoint name to use for a one-click Autopilot model deployment if the endpoint name is not generated automatically.</p> <note> <p>Specify the <code>EndpointName</code> if and only if you set <code>AutoGenerateEndpointName</code> to <code>False</code>; otherwise a 400 error is thrown.</p> </note>
    """

    auto_generate_endpoint_name: Optional[bool] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()


class InputConfig(Base):
    """
    InputConfig
         <p>Contains information about the location of input model artifacts, the name and shape of the expected data inputs, and the framework in which the model was trained.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The S3 path where the model artifacts, which result from model training, are stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix).</p>
       data_input_config: 	 <p>Specifies the name and shape of the expected data inputs for your trained model with a JSON dictionary form. The data inputs are <code>Framework</code> specific. </p> <ul> <li> <p> <code>TensorFlow</code>: You must specify the name and shape (NHWC format) of the expected data inputs using a dictionary format for your trained model. The dictionary formats required for the console and CLI are different.</p> <ul> <li> <p>Examples for one input:</p> <ul> <li> <p>If using the console, <code>{"input":[1,1024,1024,3]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"input\":[1,1024,1024,3]}</code> </p> </li> </ul> </li> <li> <p>Examples for two inputs:</p> <ul> <li> <p>If using the console, <code>{"data1": [1,28,28,1], "data2":[1,28,28,1]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"data1\": [1,28,28,1], \"data2\":[1,28,28,1]}</code> </p> </li> </ul> </li> </ul> </li> <li> <p> <code>KERAS</code>: You must specify the name and shape (NCHW format) of expected data inputs using a dictionary format for your trained model. Note that while Keras model artifacts should be uploaded in NHWC (channel-last) format, <code>DataInputConfig</code> should be specified in NCHW (channel-first) format. The dictionary formats required for the console and CLI are different.</p> <ul> <li> <p>Examples for one input:</p> <ul> <li> <p>If using the console, <code>{"input_1":[1,3,224,224]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"input_1\":[1,3,224,224]}</code> </p> </li> </ul> </li> <li> <p>Examples for two inputs:</p> <ul> <li> <p>If using the console, <code>{"input_1": [1,3,224,224], "input_2":[1,3,224,224]} </code> </p> </li> <li> <p>If using the CLI, <code>{\"input_1\": [1,3,224,224], \"input_2\":[1,3,224,224]}</code> </p> </li> </ul> </li> </ul> </li> <li> <p> <code>MXNET/ONNX/DARKNET</code>: You must specify the name and shape (NCHW format) of the expected data inputs in order using a dictionary format for your trained model. The dictionary formats required for the console and CLI are different.</p> <ul> <li> <p>Examples for one input:</p> <ul> <li> <p>If using the console, <code>{"data":[1,3,1024,1024]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"data\":[1,3,1024,1024]}</code> </p> </li> </ul> </li> <li> <p>Examples for two inputs:</p> <ul> <li> <p>If using the console, <code>{"var1": [1,1,28,28], "var2":[1,1,28,28]} </code> </p> </li> <li> <p>If using the CLI, <code>{\"var1\": [1,1,28,28], \"var2\":[1,1,28,28]}</code> </p> </li> </ul> </li> </ul> </li> <li> <p> <code>PyTorch</code>: You can either specify the name and shape (NCHW format) of expected data inputs in order using a dictionary format for your trained model or you can specify the shape only using a list format. The dictionary formats required for the console and CLI are different. The list formats for the console and CLI are the same.</p> <ul> <li> <p>Examples for one input in dictionary format:</p> <ul> <li> <p>If using the console, <code>{"input0":[1,3,224,224]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"input0\":[1,3,224,224]}</code> </p> </li> </ul> </li> <li> <p>Example for one input in list format: <code>[[1,3,224,224]]</code> </p> </li> <li> <p>Examples for two inputs in dictionary format:</p> <ul> <li> <p>If using the console, <code>{"input0":[1,3,224,224], "input1":[1,3,224,224]}</code> </p> </li> <li> <p>If using the CLI, <code>{\"input0\":[1,3,224,224], \"input1\":[1,3,224,224]} </code> </p> </li> </ul> </li> <li> <p>Example for two inputs in list format: <code>[[1,3,224,224], [1,3,224,224]]</code> </p> </li> </ul> </li> <li> <p> <code>XGBOOST</code>: input data name and shape are not needed.</p> </li> </ul> <p> <code>DataInputConfig</code> supports the following parameters for <code>CoreML</code> <code>TargetDevice</code> (ML Model format):</p> <ul> <li> <p> <code>shape</code>: Input shape, for example <code>{"input_1": {"shape": [1,224,224,3]}}</code>. In addition to static input shapes, CoreML converter supports Flexible input shapes:</p> <ul> <li> <p>Range Dimension. You can use the Range Dimension feature if you know the input shape will be within some specific interval in that dimension, for example: <code>{"input_1": {"shape": ["1..10", 224, 224, 3]}}</code> </p> </li> <li> <p>Enumerated shapes. Sometimes, the models are trained to work only on a select set of inputs. You can enumerate all supported input shapes, for example: <code>{"input_1": {"shape": [[1, 224, 224, 3], [1, 160, 160, 3]]}}</code> </p> </li> </ul> </li> <li> <p> <code>default_shape</code>: Default input shape. You can set a default shape during conversion for both Range Dimension and Enumerated Shapes. For example <code>{"input_1": {"shape": ["1..10", 224, 224, 3], "default_shape": [1, 224, 224, 3]}}</code> </p> </li> <li> <p> <code>type</code>: Input type. Allowed values: <code>Image</code> and <code>Tensor</code>. By default, the converter generates an ML Model with inputs of type Tensor (MultiArray). User can set input type to be Image. Image input type requires additional input parameters such as <code>bias</code> and <code>scale</code>.</p> </li> <li> <p> <code>bias</code>: If the input type is an Image, you need to provide the bias vector.</p> </li> <li> <p> <code>scale</code>: If the input type is an Image, you need to provide a scale factor.</p> </li> </ul> <p>CoreML <code>ClassifierConfig</code> parameters can be specified using <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputConfig.html">OutputConfig</a> <code>CompilerOptions</code>. CoreML converter supports Tensorflow and PyTorch models. CoreML conversion examples:</p> <ul> <li> <p>Tensor type input:</p> <ul> <li> <p> <code>"DataInputConfig": {"input_1": {"shape": [[1,224,224,3], [1,160,160,3]], "default_shape": [1,224,224,3]}}</code> </p> </li> </ul> </li> <li> <p>Tensor type input without input name (PyTorch):</p> <ul> <li> <p> <code>"DataInputConfig": [{"shape": [[1,3,224,224], [1,3,160,160]], "default_shape": [1,3,224,224]}]</code> </p> </li> </ul> </li> <li> <p>Image type input:</p> <ul> <li> <p> <code>"DataInputConfig": {"input_1": {"shape": [[1,224,224,3], [1,160,160,3]], "default_shape": [1,224,224,3], "type": "Image", "bias": [-1,-1,-1], "scale": 0.007843137255}}</code> </p> </li> <li> <p> <code>"CompilerOptions": {"class_labels": "imagenet_labels_1000.txt"}</code> </p> </li> </ul> </li> <li> <p>Image type input without input name (PyTorch):</p> <ul> <li> <p> <code>"DataInputConfig": [{"shape": [[1,3,224,224], [1,3,160,160]], "default_shape": [1,3,224,224], "type": "Image", "bias": [-1,-1,-1], "scale": 0.007843137255}]</code> </p> </li> <li> <p> <code>"CompilerOptions": {"class_labels": "imagenet_labels_1000.txt"}</code> </p> </li> </ul> </li> </ul> <p>Depending on the model format, <code>DataInputConfig</code> requires the following parameters for <code>ml_eia2</code> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputConfig.html#sagemaker-Type-OutputConfig-TargetDevice">OutputConfig:TargetDevice</a>.</p> <ul> <li> <p>For TensorFlow models saved in the SavedModel format, specify the input names from <code>signature_def_key</code> and the input model shapes for <code>DataInputConfig</code>. Specify the <code>signature_def_key</code> in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputConfig.html#sagemaker-Type-OutputConfig-CompilerOptions"> <code>OutputConfig:CompilerOptions</code> </a> if the model does not use TensorFlow's default signature def key. For example:</p> <ul> <li> <p> <code>"DataInputConfig": {"inputs": [1, 224, 224, 3]}</code> </p> </li> <li> <p> <code>"CompilerOptions": {"signature_def_key": "serving_custom"}</code> </p> </li> </ul> </li> <li> <p>For TensorFlow models saved as a frozen graph, specify the input tensor names and shapes in <code>DataInputConfig</code> and the output tensor names for <code>output_names</code> in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputConfig.html#sagemaker-Type-OutputConfig-CompilerOptions"> <code>OutputConfig:CompilerOptions</code> </a>. For example:</p> <ul> <li> <p> <code>"DataInputConfig": {"input_tensor:0": [1, 224, 224, 3]}</code> </p> </li> <li> <p> <code>"CompilerOptions": {"output_names": ["output_tensor:0"]}</code> </p> </li> </ul> </li> </ul>
       framework: 	 <p>Identifies the framework in which the model was trained. For example: TENSORFLOW.</p>
       framework_version: 	 <p>Specifies the framework version to use. This API field is only supported for the MXNet, PyTorch, TensorFlow and TensorFlow Lite frameworks.</p> <p>For information about framework versions supported for cloud targets and edge devices, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/neo-supported-cloud.html">Cloud Supported Instance Types and Frameworks</a> and <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/neo-supported-devices-edge-frameworks.html">Edge Supported Frameworks</a>.</p>
    """

    s3_uri: str
    framework: str
    data_input_config: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()


class TargetPlatform(Base):
    """
    TargetPlatform
         <p>Contains information about a target platform that you want your model to run on, such as OS, architecture, and accelerators. It is an alternative of <code>TargetDevice</code>.</p>

        Attributes
       ----------------------
       os: 	 <p>Specifies a target platform OS.</p> <ul> <li> <p> <code>LINUX</code>: Linux-based operating systems.</p> </li> <li> <p> <code>ANDROID</code>: Android operating systems. Android API level can be specified using the <code>ANDROID_PLATFORM</code> compiler option. For example, <code>"CompilerOptions": {'ANDROID_PLATFORM': 28}</code> </p> </li> </ul>
       arch: 	 <p>Specifies a target platform architecture.</p> <ul> <li> <p> <code>X86_64</code>: 64-bit version of the x86 instruction set.</p> </li> <li> <p> <code>X86</code>: 32-bit version of the x86 instruction set.</p> </li> <li> <p> <code>ARM64</code>: ARMv8 64-bit CPU.</p> </li> <li> <p> <code>ARM_EABIHF</code>: ARMv7 32-bit, Hard Float.</p> </li> <li> <p> <code>ARM_EABI</code>: ARMv7 32-bit, Soft Float. Used by Android 32-bit ARM platform.</p> </li> </ul>
       accelerator: 	 <p>Specifies a target platform accelerator (optional).</p> <ul> <li> <p> <code>NVIDIA</code>: Nvidia graphics processing unit. It also requires <code>gpu-code</code>, <code>trt-ver</code>, <code>cuda-ver</code> compiler options</p> </li> <li> <p> <code>MALI</code>: ARM Mali graphics processor</p> </li> <li> <p> <code>INTEL_GRAPHICS</code>: Integrated Intel graphics</p> </li> </ul>
    """

    os: str
    arch: str
    accelerator: Optional[str] = Unassigned()


class OutputConfig(Base):
    """
    OutputConfig
         <p>Contains information about the output location for the compiled model and the target device that the model runs on. <code>TargetDevice</code> and <code>TargetPlatform</code> are mutually exclusive, so you need to choose one between the two to specify your target device or platform. If you cannot find your device you want to use from the <code>TargetDevice</code> list, use <code>TargetPlatform</code> to describe the platform of your edge device and <code>CompilerOptions</code> if there are specific settings that are required or recommended to use for particular TargetPlatform.</p>

        Attributes
       ----------------------
       s3_output_location: 	 <p>Identifies the S3 bucket where you want Amazon SageMaker to store the model artifacts. For example, <code>s3://bucket-name/key-name-prefix</code>.</p>
       target_device: 	 <p>Identifies the target device or the machine learning instance that you want to run your model on after the compilation has completed. Alternatively, you can specify OS, architecture, and accelerator using <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TargetPlatform.html">TargetPlatform</a> fields. It can be used instead of <code>TargetPlatform</code>.</p> <note> <p>Currently <code>ml_trn1</code> is available only in US East (N. Virginia) Region, and <code>ml_inf2</code> is available only in US East (Ohio) Region.</p> </note>
       target_platform: 	 <p>Contains information about a target platform that you want your model to run on, such as OS, architecture, and accelerators. It is an alternative of <code>TargetDevice</code>.</p> <p>The following examples show how to configure the <code>TargetPlatform</code> and <code>CompilerOptions</code> JSON strings for popular target platforms: </p> <ul> <li> <p>Raspberry Pi 3 Model B+</p> <p> <code>"TargetPlatform": {"Os": "LINUX", "Arch": "ARM_EABIHF"},</code> </p> <p> <code> "CompilerOptions": {'mattr': ['+neon']}</code> </p> </li> <li> <p>Jetson TX2</p> <p> <code>"TargetPlatform": {"Os": "LINUX", "Arch": "ARM64", "Accelerator": "NVIDIA"},</code> </p> <p> <code> "CompilerOptions": {'gpu-code': 'sm_62', 'trt-ver': '6.0.1', 'cuda-ver': '10.0'}</code> </p> </li> <li> <p>EC2 m5.2xlarge instance OS</p> <p> <code>"TargetPlatform": {"Os": "LINUX", "Arch": "X86_64", "Accelerator": "NVIDIA"},</code> </p> <p> <code> "CompilerOptions": {'mcpu': 'skylake-avx512'}</code> </p> </li> <li> <p>RK3399</p> <p> <code>"TargetPlatform": {"Os": "LINUX", "Arch": "ARM64", "Accelerator": "MALI"}</code> </p> </li> <li> <p>ARMv7 phone (CPU)</p> <p> <code>"TargetPlatform": {"Os": "ANDROID", "Arch": "ARM_EABI"},</code> </p> <p> <code> "CompilerOptions": {'ANDROID_PLATFORM': 25, 'mattr': ['+neon']}</code> </p> </li> <li> <p>ARMv8 phone (CPU)</p> <p> <code>"TargetPlatform": {"Os": "ANDROID", "Arch": "ARM64"},</code> </p> <p> <code> "CompilerOptions": {'ANDROID_PLATFORM': 29}</code> </p> </li> </ul>
       compiler_options: 	 <p>Specifies additional parameters for compiler options in JSON format. The compiler options are <code>TargetPlatform</code> specific. It is required for NVIDIA accelerators and highly recommended for CPU compilations. For any other cases, it is optional to specify <code>CompilerOptions.</code> </p> <ul> <li> <p> <code>DTYPE</code>: Specifies the data type for the input. When compiling for <code>ml_*</code> (except for <code>ml_inf</code>) instances using PyTorch framework, provide the data type (dtype) of the model's input. <code>"float32"</code> is used if <code>"DTYPE"</code> is not specified. Options for data type are:</p> <ul> <li> <p>float32: Use either <code>"float"</code> or <code>"float32"</code>.</p> </li> <li> <p>int64: Use either <code>"int64"</code> or <code>"long"</code>.</p> </li> </ul> <p> For example, <code>{"dtype" : "float32"}</code>.</p> </li> <li> <p> <code>CPU</code>: Compilation for CPU supports the following compiler options.</p> <ul> <li> <p> <code>mcpu</code>: CPU micro-architecture. For example, <code>{'mcpu': 'skylake-avx512'}</code> </p> </li> <li> <p> <code>mattr</code>: CPU flags. For example, <code>{'mattr': ['+neon', '+vfpv4']}</code> </p> </li> </ul> </li> <li> <p> <code>ARM</code>: Details of ARM CPU compilations.</p> <ul> <li> <p> <code>NEON</code>: NEON is an implementation of the Advanced SIMD extension used in ARMv7 processors.</p> <p>For example, add <code>{'mattr': ['+neon']}</code> to the compiler options if compiling for ARM 32-bit platform with the NEON support.</p> </li> </ul> </li> <li> <p> <code>NVIDIA</code>: Compilation for NVIDIA GPU supports the following compiler options.</p> <ul> <li> <p> <code>gpu_code</code>: Specifies the targeted architecture.</p> </li> <li> <p> <code>trt-ver</code>: Specifies the TensorRT versions in x.y.z. format.</p> </li> <li> <p> <code>cuda-ver</code>: Specifies the CUDA version in x.y format.</p> </li> </ul> <p>For example, <code>{'gpu-code': 'sm_72', 'trt-ver': '6.0.1', 'cuda-ver': '10.1'}</code> </p> </li> <li> <p> <code>ANDROID</code>: Compilation for the Android OS supports the following compiler options:</p> <ul> <li> <p> <code>ANDROID_PLATFORM</code>: Specifies the Android API levels. Available levels range from 21 to 29. For example, <code>{'ANDROID_PLATFORM': 28}</code>.</p> </li> <li> <p> <code>mattr</code>: Add <code>{'mattr': ['+neon']}</code> to compiler options if compiling for ARM 32-bit platform with NEON support.</p> </li> </ul> </li> <li> <p> <code>INFERENTIA</code>: Compilation for target ml_inf1 uses compiler options passed in as a JSON string. For example, <code>"CompilerOptions": "\"--verbose 1 --num-neuroncores 2 -O2\""</code>. </p> <p>For information about supported compiler options, see <a href="https://awsdocs-neuron.readthedocs-hosted.com/en/latest/compiler/neuronx-cc/api-reference-guide/neuron-compiler-cli-reference-guide.html"> Neuron Compiler CLI Reference Guide</a>. </p> </li> <li> <p> <code>CoreML</code>: Compilation for the CoreML <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OutputConfig.html">OutputConfig</a> <code>TargetDevice</code> supports the following compiler options:</p> <ul> <li> <p> <code>class_labels</code>: Specifies the classification labels file name inside input tar.gz file. For example, <code>{"class_labels": "imagenet_labels_1000.txt"}</code>. Labels inside the txt file should be separated by newlines.</p> </li> </ul> </li> <li> <p> <code>EIA</code>: Compilation for the Elastic Inference Accelerator supports the following compiler options:</p> <ul> <li> <p> <code>precision_mode</code>: Specifies the precision of compiled artifacts. Supported values are <code>"FP16"</code> and <code>"FP32"</code>. Default is <code>"FP32"</code>.</p> </li> <li> <p> <code>signature_def_key</code>: Specifies the signature to use for models in SavedModel format. Defaults is TensorFlow's default signature def key.</p> </li> <li> <p> <code>output_names</code>: Specifies a list of output tensor names for models in FrozenGraph format. Set at most one API field, either: <code>signature_def_key</code> or <code>output_names</code>.</p> </li> </ul> <p>For example: <code>{"precision_mode": "FP32", "output_names": ["output:0"]}</code> </p> </li> </ul>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service key (Amazon Web Services KMS) that Amazon SageMaker uses to encrypt your output models with Amazon S3 server-side encryption after compilation job. If you don't provide a KMS key ID, Amazon SageMaker uses the default KMS key for Amazon S3 for your role's account. For more information, see <a href="https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html">KMS-Managed Encryption Keys</a> in the <i>Amazon Simple Storage Service Developer Guide.</i> </p> <p>The KmsKeyId can be any of the following formats: </p> <ul> <li> <p>Key ID: <code>1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Key ARN: <code>arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Alias name: <code>alias/ExampleAlias</code> </p> </li> <li> <p>Alias name ARN: <code>arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias</code> </p> </li> </ul>
    """

    s3_output_location: str
    target_device: Optional[str] = Unassigned()
    target_platform: Optional[TargetPlatform] = Unassigned()
    compiler_options: Optional[str] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()


class NeoVpcConfig(Base):
    """
    NeoVpcConfig
         <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> configuration object that specifies the VPC that you want the compilation jobs to connect to. For more information on controlling access to your Amazon S3 buckets used for compilation job, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/neo-vpc.html">Give Amazon SageMaker Compilation Jobs Access to Resources in Your Amazon VPC</a>.</p>

        Attributes
       ----------------------
       security_group_ids: 	 <p>The VPC security group IDs. IDs have the form of <code>sg-xxxxxxxx</code>. Specify the security groups for the VPC that is specified in the <code>Subnets</code> field.</p>
       subnets: 	 <p>The ID of the subnets in the VPC that you want to connect the compilation job to for accessing the model in Amazon S3.</p>
    """

    security_group_ids: List[str]
    subnets: List[str]


class MonitoringConstraintsResource(Base):
    """
    MonitoringConstraintsResource
         <p>The constraints resource for a monitoring job.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The Amazon S3 URI for the constraints resource.</p>
    """

    s3_uri: Optional[str] = Unassigned()


class MonitoringStatisticsResource(Base):
    """
    MonitoringStatisticsResource
         <p>The statistics resource for a monitoring job.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The Amazon S3 URI for the statistics resource.</p>
    """

    s3_uri: Optional[str] = Unassigned()


class DataQualityBaselineConfig(Base):
    """
    DataQualityBaselineConfig
         <p>Configuration for monitoring constraints and monitoring statistics. These baseline resources are compared against the results of the current job from the series of jobs scheduled to collect data periodically.</p>

        Attributes
       ----------------------
       baselining_job_name: 	 <p>The name of the job that performs baselining for the data quality monitoring job.</p>
       constraints_resource
       statistics_resource
    """

    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()
    statistics_resource: Optional[MonitoringStatisticsResource] = Unassigned()


class DataQualityAppSpecification(Base):
    """
    DataQualityAppSpecification
         <p>Information about the container that a data quality monitoring job runs.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The container image that the data quality monitoring job runs.</p>
       container_entrypoint: 	 <p>The entrypoint for a container used to run a monitoring job.</p>
       container_arguments: 	 <p>The arguments to send to the container that the monitoring job runs.</p>
       record_preprocessor_source_uri: 	 <p>An Amazon S3 URI to a script that is called per row prior to running analysis. It can base64 decode the payload and convert it into a flattened JSON so that the built-in container can use the converted data. Applicable only for the built-in (first party) containers.</p>
       post_analytics_processor_source_uri: 	 <p>An Amazon S3 URI to a script that is called after analysis has been performed. Applicable only for the built-in (first party) containers.</p>
       environment: 	 <p>Sets the environment variables in the container that the monitoring job runs.</p>
    """

    image_uri: str
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_arguments: Optional[List[str]] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class EndpointInput(Base):
    """
    EndpointInput
         <p>Input object for the endpoint</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>An endpoint in customer's account which has enabled <code>DataCaptureConfig</code> enabled.</p>
       local_path: 	 <p>Path to the filesystem where the endpoint data is available to the container.</p>
       s3_input_mode: 	 <p>Whether the <code>Pipe</code> or <code>File</code> is used as the input mode for transferring data for the monitoring job. <code>Pipe</code> mode is recommended for large datasets. <code>File</code> mode is useful for small files that fit in memory. Defaults to <code>File</code>.</p>
       s3_data_distribution_type: 	 <p>Whether input data distributed in Amazon S3 is fully replicated or sharded by an Amazon S3 key. Defaults to <code>FullyReplicated</code> </p>
       features_attribute: 	 <p>The attributes of the input data that are the input features.</p>
       inference_attribute: 	 <p>The attribute of the input data that represents the ground truth label.</p>
       probability_attribute: 	 <p>In a classification problem, the attribute that represents the class probability.</p>
       probability_threshold_attribute: 	 <p>The threshold for the class probability to be evaluated as a positive result.</p>
       start_time_offset: 	 <p>If specified, monitoring jobs substract this time from the start time. For information about using offsets for scheduling monitoring jobs, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality-schedule.html">Schedule Model Quality Monitoring Jobs</a>.</p>
       end_time_offset: 	 <p>If specified, monitoring jobs substract this time from the end time. For information about using offsets for scheduling monitoring jobs, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor-model-quality-schedule.html">Schedule Model Quality Monitoring Jobs</a>.</p>
       exclude_features_attribute: 	 <p>The attributes of the input data to exclude from the analysis.</p>
    """

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


class DataQualityJobInput(Base):
    """
    DataQualityJobInput
         <p>The input for the data quality monitoring job. Currently endpoints are supported for input.</p>

        Attributes
       ----------------------
       endpoint_input
       batch_transform_input: 	 <p>Input object for the batch transform job.</p>
    """

    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class MonitoringS3Output(Base):
    """
    MonitoringS3Output
         <p>Information about where and how you want to store the results of a monitoring job.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>A URI that identifies the Amazon S3 storage location where Amazon SageMaker saves the results of a monitoring job.</p>
       local_path: 	 <p>The local path to the Amazon S3 storage location where Amazon SageMaker saves the results of a monitoring job. LocalPath is an absolute path for the output data.</p>
       s3_upload_mode: 	 <p>Whether to upload the results of the monitoring job continuously or after the job completes.</p>
    """

    s3_uri: str
    local_path: str
    s3_upload_mode: Optional[str] = Unassigned()


class MonitoringOutput(Base):
    """
    MonitoringOutput
         <p>The output object for a monitoring job.</p>

        Attributes
       ----------------------
       s3_output: 	 <p>The Amazon S3 storage location where the results of a monitoring job are saved.</p>
    """

    s3_output: MonitoringS3Output


class MonitoringOutputConfig(Base):
    """
    MonitoringOutputConfig
         <p>The output configuration for monitoring jobs.</p>

        Attributes
       ----------------------
       monitoring_outputs: 	 <p>Monitoring outputs for monitoring jobs. This is where the output of the periodic monitoring jobs is uploaded.</p>
       kms_key_id: 	 <p>The Key Management Service (KMS) key that Amazon SageMaker uses to encrypt the model artifacts at rest using Amazon S3 server-side encryption.</p>
    """

    monitoring_outputs: List[MonitoringOutput]
    kms_key_id: Optional[str] = Unassigned()


class MonitoringClusterConfig(Base):
    """
    MonitoringClusterConfig
         <p>Configuration for the cluster used to run model monitoring jobs.</p>

        Attributes
       ----------------------
       instance_count: 	 <p>The number of ML compute instances to use in the model monitoring job. For distributed processing jobs, specify a value greater than 1. The default value is 1.</p>
       instance_type: 	 <p>The ML compute instance type for the processing job.</p>
       volume_size_in_g_b: 	 <p>The size of the ML storage volume, in gigabytes, that you want to provision. You must specify sufficient ML storage for your scenario.</p>
       volume_kms_key_id: 	 <p>The Key Management Service (KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s) that run the model monitoring job.</p>
    """

    instance_count: int
    instance_type: str
    volume_size_in_g_b: int
    volume_kms_key_id: Optional[str] = Unassigned()


class MonitoringResources(Base):
    """
    MonitoringResources
         <p>Identifies the resources to deploy for a monitoring job.</p>

        Attributes
       ----------------------
       cluster_config: 	 <p>The configuration for the cluster resources used to run the processing job.</p>
    """

    cluster_config: MonitoringClusterConfig


class MonitoringNetworkConfig(Base):
    """
    MonitoringNetworkConfig
         <p>The networking configuration for the monitoring job.</p>

        Attributes
       ----------------------
       enable_inter_container_traffic_encryption: 	 <p>Whether to encrypt all communications between the instances used for the monitoring jobs. Choose <code>True</code> to encrypt communications. Encryption provides greater security for distributed jobs, but the processing might take longer.</p>
       enable_network_isolation: 	 <p>Whether to allow inbound and outbound network calls to and from the containers used for the monitoring job.</p>
       vpc_config
    """

    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


class MonitoringStoppingCondition(Base):
    """
    MonitoringStoppingCondition
         <p>A time limit for how long the monitoring job is allowed to run before stopping.</p>

        Attributes
       ----------------------
       max_runtime_in_seconds: 	 <p>The maximum runtime allowed in seconds.</p> <note> <p>The <code>MaxRuntimeInSeconds</code> cannot exceed the frequency of the job. For data quality and model explainability, this can be up to 3600 seconds for an hourly schedule. For model bias and model quality hourly schedules, this can be up to 1800 seconds.</p> </note>
    """

    max_runtime_in_seconds: int


class EdgeOutputConfig(Base):
    """
    EdgeOutputConfig
         <p>The output configuration.</p>

        Attributes
       ----------------------
       s3_output_location: 	 <p>The Amazon Simple Storage (S3) bucker URI.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume after compilation job. If you don't provide a KMS key ID, Amazon SageMaker uses the default KMS key for Amazon S3 for your role's account.</p>
       preset_deployment_type: 	 <p>The deployment type SageMaker Edge Manager will create. Currently only supports Amazon Web Services IoT Greengrass Version 2 components.</p>
       preset_deployment_config: 	 <p>The configuration used to create deployment artifacts. Specify configuration options with a JSON string. The available configuration options for each type are:</p> <ul> <li> <p> <code>ComponentName</code> (optional) - Name of the GreenGrass V2 component. If not specified, the default name generated consists of "SagemakerEdgeManager" and the name of your SageMaker Edge Manager packaging job.</p> </li> <li> <p> <code>ComponentDescription</code> (optional) - Description of the component.</p> </li> <li> <p> <code>ComponentVersion</code> (optional) - The version of the component.</p> <note> <p>Amazon Web Services IoT Greengrass uses semantic versions for components. Semantic versions follow a<i> major.minor.patch</i> number system. For example, version 1.0.0 represents the first major release for a component. For more information, see the <a href="https://semver.org/">semantic version specification</a>.</p> </note> </li> <li> <p> <code>PlatformOS</code> (optional) - The name of the operating system for the platform. Supported platforms include Windows and Linux.</p> </li> <li> <p> <code>PlatformArchitecture</code> (optional) - The processor architecture for the platform. </p> <p>Supported architectures Windows include: Windows32_x86, Windows64_x64.</p> <p>Supported architectures for Linux include: Linux x86_64, Linux ARMV8.</p> </li> </ul>
    """

    s3_output_location: str
    kms_key_id: Optional[str] = Unassigned()
    preset_deployment_type: Optional[str] = Unassigned()
    preset_deployment_config: Optional[str] = Unassigned()


class SharingSettings(Base):
    """
    SharingSettings
         <p>Specifies options for sharing Amazon SageMaker Studio notebooks. These settings are specified as part of <code>DefaultUserSettings</code> when the <code>CreateDomain</code> API is called, and as part of <code>UserSettings</code> when the <code>CreateUserProfile</code> API is called. When <code>SharingSettings</code> is not specified, notebook sharing isn't allowed.</p>

        Attributes
       ----------------------
       notebook_output_option: 	 <p>Whether to include the notebook cell output when sharing the notebook. The default is <code>Disabled</code>.</p>
       s3_output_path: 	 <p>When <code>NotebookOutputOption</code> is <code>Allowed</code>, the Amazon S3 bucket used to store the shared notebook snapshots.</p>
       s3_kms_key_id: 	 <p>When <code>NotebookOutputOption</code> is <code>Allowed</code>, the Amazon Web Services Key Management Service (KMS) encryption key ID used to encrypt the notebook cell output in the Amazon S3 bucket.</p>
    """

    notebook_output_option: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    s3_kms_key_id: Optional[str] = Unassigned()


class JupyterServerAppSettings(Base):
    """
    JupyterServerAppSettings
         <p>The JupyterServer app settings.</p>

        Attributes
       ----------------------
       default_resource_spec: 	 <p>The default instance type and the Amazon Resource Name (ARN) of the default SageMaker image used by the JupyterServer app. If you use the <code>LifecycleConfigArns</code> parameter, then this parameter is also required.</p>
       lifecycle_config_arns: 	 <p> The Amazon Resource Name (ARN) of the Lifecycle Configurations attached to the JupyterServerApp. If you use this parameter, the <code>DefaultResourceSpec</code> parameter is also required.</p> <note> <p>To remove a Lifecycle Config, you must set <code>LifecycleConfigArns</code> to an empty list.</p> </note>
       code_repositories: 	 <p>A list of Git repositories that SageMaker automatically displays to users for cloning in the JupyterServer application.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    lifecycle_config_arns: Optional[List[str]] = Unassigned()
    code_repositories: Optional[List[CodeRepository]] = Unassigned()


class CustomImage(Base):
    """
    CustomImage
         <p>A custom SageMaker image. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/studio-byoi.html">Bring your own SageMaker image</a>.</p>

        Attributes
       ----------------------
       image_name: 	 <p>The name of the CustomImage. Must be unique to your account.</p>
       image_version_number: 	 <p>The version number of the CustomImage.</p>
       app_image_config_name: 	 <p>The name of the AppImageConfig.</p>
    """

    image_name: str
    app_image_config_name: str
    image_version_number: Optional[int] = Unassigned()


class KernelGatewayAppSettings(Base):
    """
    KernelGatewayAppSettings
         <p>The KernelGateway app settings.</p>

        Attributes
       ----------------------
       default_resource_spec: 	 <p>The default instance type and the Amazon Resource Name (ARN) of the default SageMaker image used by the KernelGateway app.</p> <note> <p>The Amazon SageMaker Studio UI does not use the default instance type value set here. The default instance type set here is used when Apps are created using the CLI or CloudFormation and the instance type parameter value is not passed.</p> </note>
       custom_images: 	 <p>A list of custom SageMaker images that are configured to run as a KernelGateway app.</p>
       lifecycle_config_arns: 	 <p> The Amazon Resource Name (ARN) of the Lifecycle Configurations attached to the the user profile or domain.</p> <note> <p>To remove a Lifecycle Config, you must set <code>LifecycleConfigArns</code> to an empty list.</p> </note>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[List[CustomImage]] = Unassigned()
    lifecycle_config_arns: Optional[List[str]] = Unassigned()


class TensorBoardAppSettings(Base):
    """
    TensorBoardAppSettings
         <p>The TensorBoard app settings.</p>

        Attributes
       ----------------------
       default_resource_spec: 	 <p>The default instance type and the Amazon Resource Name (ARN) of the SageMaker image created on the instance.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()


class RStudioServerProAppSettings(Base):
    """
    RStudioServerProAppSettings
         <p>A collection of settings that configure user interaction with the <code>RStudioServerPro</code> app.</p>

        Attributes
       ----------------------
       access_status: 	 <p>Indicates whether the current user has access to the <code>RStudioServerPro</code> app.</p>
       user_group: 	 <p>The level of permissions that the user has within the <code>RStudioServerPro</code> app. This value defaults to `User`. The `Admin` value allows the user access to the RStudio Administrative Dashboard.</p>
    """

    access_status: Optional[str] = Unassigned()
    user_group: Optional[str] = Unassigned()


class RSessionAppSettings(Base):
    """
    RSessionAppSettings
         <p>A collection of settings that apply to an <code>RSessionGateway</code> app.</p>

        Attributes
       ----------------------
       default_resource_spec
       custom_images: 	 <p>A list of custom SageMaker images that are configured to run as a RSession app.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[List[CustomImage]] = Unassigned()


class JupyterLabAppSettings(Base):
    """
    JupyterLabAppSettings
         <p>The settings for the JupyterLab application.</p>

        Attributes
       ----------------------
       default_resource_spec
       custom_images: 	 <p>A list of custom SageMaker images that are configured to run as a JupyterLab app.</p>
       lifecycle_config_arns: 	 <p>The Amazon Resource Name (ARN) of the lifecycle configurations attached to the user profile or domain. To remove a lifecycle config, you must set <code>LifecycleConfigArns</code> to an empty list.</p>
       code_repositories: 	 <p>A list of Git repositories that SageMaker automatically displays to users for cloning in the JupyterLab application.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    custom_images: Optional[List[CustomImage]] = Unassigned()
    lifecycle_config_arns: Optional[List[str]] = Unassigned()
    code_repositories: Optional[List[CodeRepository]] = Unassigned()


class DefaultEbsStorageSettings(Base):
    """
    DefaultEbsStorageSettings
         <p>A collection of default EBS storage settings that applies to private spaces created within a domain or user profile.</p>

        Attributes
       ----------------------
       default_ebs_volume_size_in_gb: 	 <p>The default size of the EBS storage volume for a private space.</p>
       maximum_ebs_volume_size_in_gb: 	 <p>The maximum size of the EBS storage volume for a private space.</p>
    """

    default_ebs_volume_size_in_gb: int
    maximum_ebs_volume_size_in_gb: int


class DefaultSpaceStorageSettings(Base):
    """
    DefaultSpaceStorageSettings
         <p>The default storage settings for a private space.</p>

        Attributes
       ----------------------
       default_ebs_storage_settings: 	 <p>The default EBS storage settings for a private space.</p>
    """

    default_ebs_storage_settings: Optional[DefaultEbsStorageSettings] = Unassigned()


class CustomPosixUserConfig(Base):
    """
    CustomPosixUserConfig
         <p>Details about the POSIX identity that is used for file system operations.</p>

        Attributes
       ----------------------
       uid: 	 <p>The POSIX user ID.</p>
       gid: 	 <p>The POSIX group ID.</p>
    """

    uid: int
    gid: int


class EFSFileSystemConfig(Base):
    """
    EFSFileSystemConfig
         <p>The settings for assigning a custom Amazon EFS file system to a user profile or space for an Amazon SageMaker Domain.</p>

        Attributes
       ----------------------
       file_system_id: 	 <p>The ID of your Amazon EFS file system.</p>
       file_system_path: 	 <p>The path to the file system directory that is accessible in Amazon SageMaker Studio. Permitted users can access only this directory and below.</p>
    """

    file_system_id: str
    file_system_path: Optional[str] = Unassigned()


class CustomFileSystemConfig(Base):
    """
    CustomFileSystemConfig
         <p>The settings for assigning a custom file system to a user profile or space for an Amazon SageMaker Domain. Permitted users can access this file system in Amazon SageMaker Studio.</p>

        Attributes
       ----------------------
       e_f_s_file_system_config: 	 <p>The settings for a custom Amazon EFS file system.</p>
    """

    e_f_s_file_system_config: Optional[EFSFileSystemConfig] = Unassigned()


class UserSettings(Base):
    """
    UserSettings
         <p>A collection of settings that apply to users in a domain. These settings are specified when the <code>CreateUserProfile</code> API is called, and as <code>DefaultUserSettings</code> when the <code>CreateDomain</code> API is called.</p> <p> <code>SecurityGroups</code> is aggregated when specified in both calls. For all other settings in <code>UserSettings</code>, the values specified in <code>CreateUserProfile</code> take precedence over those specified in <code>CreateDomain</code>.</p>

        Attributes
       ----------------------
       execution_role: 	 <p>The execution role for the user.</p>
       security_groups: 	 <p>The security groups for the Amazon Virtual Private Cloud (VPC) that the domain uses for communication.</p> <p>Optional when the <code>CreateDomain.AppNetworkAccessType</code> parameter is set to <code>PublicInternetOnly</code>.</p> <p>Required when the <code>CreateDomain.AppNetworkAccessType</code> parameter is set to <code>VpcOnly</code>, unless specified as part of the <code>DefaultUserSettings</code> for the domain.</p> <p>Amazon SageMaker adds a security group to allow NFS traffic from Amazon SageMaker Studio. Therefore, the number of security groups that you can specify is one less than the maximum number shown.</p>
       sharing_settings: 	 <p>Specifies options for sharing Amazon SageMaker Studio notebooks.</p>
       jupyter_server_app_settings: 	 <p>The Jupyter server's app settings.</p>
       kernel_gateway_app_settings: 	 <p>The kernel gateway app settings.</p>
       tensor_board_app_settings: 	 <p>The TensorBoard app settings.</p>
       r_studio_server_pro_app_settings: 	 <p>A collection of settings that configure user interaction with the <code>RStudioServerPro</code> app.</p>
       r_session_app_settings: 	 <p>A collection of settings that configure the <code>RSessionGateway</code> app.</p>
       canvas_app_settings: 	 <p>The Canvas app settings.</p>
       code_editor_app_settings: 	 <p>The Code Editor application settings.</p>
       jupyter_lab_app_settings: 	 <p>The settings for the JupyterLab application.</p>
       space_storage_settings: 	 <p>The storage settings for a private space.</p>
       default_landing_uri: 	 <p>The default experience that the user is directed to when accessing the domain. The supported values are:</p> <ul> <li> <p> <code>studio::</code>: Indicates that Studio is the default experience. This value can only be passed if <code>StudioWebPortal</code> is set to <code>ENABLED</code>.</p> </li> <li> <p> <code>app:JupyterServer:</code>: Indicates that Studio Classic is the default experience.</p> </li> </ul>
       studio_web_portal: 	 <p>Whether the user can access Studio. If this value is set to <code>DISABLED</code>, the user cannot access Studio, even if that is the default experience for the domain.</p>
       custom_posix_user_config: 	 <p>Details about the POSIX identity that is used for file system operations.</p>
       custom_file_system_configs: 	 <p>The settings for assigning a custom file system to a user profile. Permitted users can access this file system in Amazon SageMaker Studio.</p>
    """

    execution_role: Optional[str] = Unassigned()
    security_groups: Optional[List[str]] = Unassigned()
    sharing_settings: Optional[SharingSettings] = Unassigned()
    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()
    tensor_board_app_settings: Optional[TensorBoardAppSettings] = Unassigned()
    r_studio_server_pro_app_settings: Optional[RStudioServerProAppSettings] = (
        Unassigned()
    )
    r_session_app_settings: Optional[RSessionAppSettings] = Unassigned()
    canvas_app_settings: Optional[CanvasAppSettings] = Unassigned()
    code_editor_app_settings: Optional[CodeEditorAppSettings] = Unassigned()
    jupyter_lab_app_settings: Optional[JupyterLabAppSettings] = Unassigned()
    space_storage_settings: Optional[DefaultSpaceStorageSettings] = Unassigned()
    default_landing_uri: Optional[str] = Unassigned()
    studio_web_portal: Optional[str] = Unassigned()
    custom_posix_user_config: Optional[CustomPosixUserConfig] = Unassigned()
    custom_file_system_configs: Optional[List[CustomFileSystemConfig]] = Unassigned()


class RStudioServerProDomainSettings(Base):
    """
    RStudioServerProDomainSettings
         <p>A collection of settings that configure the <code>RStudioServerPro</code> Domain-level app.</p>

        Attributes
       ----------------------
       domain_execution_role_arn: 	 <p>The ARN of the execution role for the <code>RStudioServerPro</code> Domain-level app.</p>
       r_studio_connect_url: 	 <p>A URL pointing to an RStudio Connect server.</p>
       r_studio_package_manager_url: 	 <p>A URL pointing to an RStudio Package Manager server.</p>
       default_resource_spec
    """

    domain_execution_role_arn: str
    r_studio_connect_url: Optional[str] = Unassigned()
    r_studio_package_manager_url: Optional[str] = Unassigned()
    default_resource_spec: Optional[ResourceSpec] = Unassigned()


class DockerSettings(Base):
    """
    DockerSettings
         <p>A collection of settings that configure the domain's Docker interaction.</p>

        Attributes
       ----------------------
       enable_docker_access: 	 <p>Indicates whether the domain can access Docker.</p>
       vpc_only_trusted_accounts: 	 <p>The list of Amazon Web Services accounts that are trusted when the domain is created in VPC-only mode.</p>
    """

    enable_docker_access: Optional[str] = Unassigned()
    vpc_only_trusted_accounts: Optional[List[str]] = Unassigned()


class DomainSettings(Base):
    """
    DomainSettings
         <p>A collection of settings that apply to the <code>SageMaker Domain</code>. These settings are specified through the <code>CreateDomain</code> API call.</p>

        Attributes
       ----------------------
       security_group_ids: 	 <p>The security groups for the Amazon Virtual Private Cloud that the <code>Domain</code> uses for communication between Domain-level apps and user apps.</p>
       r_studio_server_pro_domain_settings: 	 <p>A collection of settings that configure the <code>RStudioServerPro</code> Domain-level app.</p>
       execution_role_identity_config: 	 <p>The configuration for attaching a SageMaker user profile name to the execution role as a <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_monitor.html">sts:SourceIdentity key</a>.</p>
       docker_settings: 	 <p>A collection of settings that configure the domain's Docker interaction.</p>
    """

    security_group_ids: Optional[List[str]] = Unassigned()
    r_studio_server_pro_domain_settings: Optional[RStudioServerProDomainSettings] = (
        Unassigned()
    )
    execution_role_identity_config: Optional[str] = Unassigned()
    docker_settings: Optional[DockerSettings] = Unassigned()


class DefaultSpaceSettings(Base):
    """
    DefaultSpaceSettings
         <p>A collection of settings that apply to spaces created in the domain.</p>

        Attributes
       ----------------------
       execution_role: 	 <p>The ARN of the execution role for the space.</p>
       security_groups: 	 <p>The security group IDs for the Amazon VPC that the space uses for communication.</p>
       jupyter_server_app_settings
       kernel_gateway_app_settings
    """

    execution_role: Optional[str] = Unassigned()
    security_groups: Optional[List[str]] = Unassigned()
    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()


class EdgeDeploymentModelConfig(Base):
    """
    EdgeDeploymentModelConfig
         <p>Contains information about the configuration of a model in a deployment.</p>

        Attributes
       ----------------------
       model_handle: 	 <p>The name the device application uses to reference this model.</p>
       edge_packaging_job_name: 	 <p>The edge packaging job associated with this deployment.</p>
    """

    model_handle: str
    edge_packaging_job_name: str


class DeviceSelectionConfig(Base):
    """
    DeviceSelectionConfig
         <p>Contains information about the configurations of selected devices.</p>

        Attributes
       ----------------------
       device_subset_type: 	 <p>Type of device subsets to deploy to the current stage.</p>
       percentage: 	 <p>Percentage of devices in the fleet to deploy to the current stage.</p>
       device_names: 	 <p>List of devices chosen to deploy.</p>
       device_name_contains: 	 <p>A filter to select devices with names containing this name.</p>
    """

    device_subset_type: str
    percentage: Optional[int] = Unassigned()
    device_names: Optional[List[str]] = Unassigned()
    device_name_contains: Optional[str] = Unassigned()


class EdgeDeploymentConfig(Base):
    """
    EdgeDeploymentConfig
         <p>Contains information about the configuration of a deployment.</p>

        Attributes
       ----------------------
       failure_handling_policy: 	 <p>Toggle that determines whether to rollback to previous configuration if the current deployment fails. By default this is turned on. You may turn this off if you want to investigate the errors yourself.</p>
    """

    failure_handling_policy: str


class DeploymentStage(Base):
    """
    DeploymentStage
         <p>Contains information about a stage in an edge deployment plan.</p>

        Attributes
       ----------------------
       stage_name: 	 <p>The name of the stage.</p>
       device_selection_config: 	 <p>Configuration of the devices in the stage.</p>
       deployment_config: 	 <p>Configuration of the deployment details.</p>
    """

    stage_name: str
    device_selection_config: DeviceSelectionConfig
    deployment_config: Optional[EdgeDeploymentConfig] = Unassigned()


class ProductionVariantCoreDumpConfig(Base):
    """
    ProductionVariantCoreDumpConfig
         <p>Specifies configuration for a core dump from the model container when the process crashes.</p>

        Attributes
       ----------------------
       destination_s3_uri: 	 <p>The Amazon S3 bucket to send the core dump to.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that SageMaker uses to encrypt the core dump data at rest using Amazon S3 server-side encryption. The <code>KmsKeyId</code> can be any of the following formats: </p> <ul> <li> <p>// KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// KMS Key Alias</p> <p> <code>"alias/ExampleAlias"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key Alias</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias"</code> </p> </li> </ul> <p>If you use a KMS key ID or an alias of your KMS key, the SageMaker execution role must include permissions to call <code>kms:Encrypt</code>. If you don't provide a KMS key ID, SageMaker uses the default KMS key for Amazon S3 for your role's account. SageMaker uses server-side encryption with KMS-managed keys for <code>OutputDataConfig</code>. If you use a bucket policy with an <code>s3:PutObject</code> permission that only allows objects with server-side encryption, set the condition key of <code>s3:x-amz-server-side-encryption</code> to <code>"aws:kms"</code>. For more information, see <a href="https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html">KMS-Managed Encryption Keys</a> in the <i>Amazon Simple Storage Service Developer Guide.</i> </p> <p>The KMS key policy must grant permission to the IAM role that you specify in your <code>CreateEndpoint</code> and <code>UpdateEndpoint</code> requests. For more information, see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html">Using Key Policies in Amazon Web Services KMS</a> in the <i>Amazon Web Services Key Management Service Developer Guide</i>.</p>
    """

    destination_s3_uri: str
    kms_key_id: Optional[str] = Unassigned()


class ProductionVariantServerlessConfig(Base):
    """
    ProductionVariantServerlessConfig
         <p>Specifies the serverless configuration for an endpoint variant.</p>

        Attributes
       ----------------------
       memory_size_in_m_b: 	 <p>The memory size of your serverless endpoint. Valid values are in 1 GB increments: 1024 MB, 2048 MB, 3072 MB, 4096 MB, 5120 MB, or 6144 MB.</p>
       max_concurrency: 	 <p>The maximum number of concurrent invocations your serverless endpoint can process.</p>
       provisioned_concurrency: 	 <p>The amount of provisioned concurrency to allocate for the serverless endpoint. Should be less than or equal to <code>MaxConcurrency</code>.</p> <note> <p>This field is not supported for serverless endpoint recommendations for Inference Recommender jobs. For more information about creating an Inference Recommender job, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateInferenceRecommendationsJob.html">CreateInferenceRecommendationsJobs</a>.</p> </note>
    """

    memory_size_in_m_b: int
    max_concurrency: int
    provisioned_concurrency: Optional[int] = Unassigned()


class ProductionVariantManagedInstanceScaling(Base):
    """
    ProductionVariantManagedInstanceScaling
         <p>Settings that control the range in the number of instances that the endpoint provisions as it scales up or down to accommodate traffic. </p>

        Attributes
       ----------------------
       status: 	 <p>Indicates whether managed instance scaling is enabled.</p>
       min_instance_count: 	 <p>The minimum number of instances that the endpoint must retain when it scales down to accommodate a decrease in traffic.</p>
       max_instance_count: 	 <p>The maximum number of instances that the endpoint can provision when it scales up to accommodate an increase in traffic.</p>
    """

    status: Optional[str] = Unassigned()
    min_instance_count: Optional[int] = Unassigned()
    max_instance_count: Optional[int] = Unassigned()


class ProductionVariantRoutingConfig(Base):
    """
    ProductionVariantRoutingConfig
         <p>Settings that control how the endpoint routes incoming traffic to the instances that the endpoint hosts.</p>

        Attributes
       ----------------------
       routing_strategy: 	 <p>Sets how the endpoint routes incoming traffic:</p> <ul> <li> <p> <code>LEAST_OUTSTANDING_REQUESTS</code>: The endpoint routes requests to the specific instances that have more capacity to process them.</p> </li> <li> <p> <code>RANDOM</code>: The endpoint routes each request to a randomly chosen instance.</p> </li> </ul>
    """

    routing_strategy: str


class ProductionVariant(Base):
    """
    ProductionVariant
         <p> Identifies a model that you want to host and the resources chosen to deploy for hosting it. If you are deploying multiple models, tell SageMaker how to distribute traffic among the models by specifying variant weights. For more information on production variants, check <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-ab-testing.html"> Production variants</a>. </p>

        Attributes
       ----------------------
       variant_name: 	 <p>The name of the production variant.</p>
       model_name: 	 <p>The name of the model that you want to host. This is the name that you specified when creating the model.</p>
       initial_instance_count: 	 <p>Number of instances to launch initially.</p>
       instance_type: 	 <p>The ML compute instance type.</p>
       initial_variant_weight: 	 <p>Determines initial traffic distribution among all of the models that you specify in the endpoint configuration. The traffic to a production variant is determined by the ratio of the <code>VariantWeight</code> to the sum of all <code>VariantWeight</code> values across all ProductionVariants. If unspecified, it defaults to 1.0. </p>
       accelerator_type: 	 <p>The size of the Elastic Inference (EI) instance to use for the production variant. EI instances provide on-demand GPU computing for inference. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/ei.html">Using Elastic Inference in Amazon SageMaker</a>.</p>
       core_dump_config: 	 <p>Specifies configuration for a core dump from the model container when the process crashes.</p>
       serverless_config: 	 <p>The serverless configuration for an endpoint. Specifies a serverless endpoint configuration instead of an instance-based endpoint configuration.</p>
       volume_size_in_g_b: 	 <p>The size, in GB, of the ML storage volume attached to individual inference instance associated with the production variant. Currently only Amazon EBS gp2 storage volumes are supported.</p>
       model_data_download_timeout_in_seconds: 	 <p>The timeout value, in seconds, to download and extract the model that you want to host from Amazon S3 to the individual inference instance associated with this production variant.</p>
       container_startup_health_check_timeout_in_seconds: 	 <p>The timeout value, in seconds, for your inference container to pass health check by SageMaker Hosting. For more information about health check, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html#your-algorithms-inference-algo-ping-requests">How Your Container Should Respond to Health Check (Ping) Requests</a>.</p>
       enable_s_s_m_access: 	 <p> You can use this parameter to turn on native Amazon Web Services Systems Manager (SSM) access for a production variant behind an endpoint. By default, SSM access is disabled for all production variants behind an endpoint. You can turn on or turn off SSM access for a production variant behind an existing endpoint by creating a new endpoint configuration and calling <code>UpdateEndpoint</code>. </p>
       managed_instance_scaling: 	 <p>Settings that control the range in the number of instances that the endpoint provisions as it scales up or down to accommodate traffic. </p>
       routing_config: 	 <p>Settings that control how the endpoint routes incoming traffic to the instances that the endpoint hosts.</p>
    """

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
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = (
        Unassigned()
    )
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


class DataCaptureConfig(Base):
    """
    DataCaptureConfig
         <p>Configuration to control how SageMaker captures inference data.</p>

        Attributes
       ----------------------
       enable_capture: 	 <p>Whether data capture should be enabled or disabled (defaults to enabled).</p>
       initial_sampling_percentage: 	 <p>The percentage of requests SageMaker will capture. A lower value is recommended for Endpoints with high traffic.</p>
       destination_s3_uri: 	 <p>The Amazon S3 location used to capture the data.</p>
       kms_key_id: 	 <p>The Amazon Resource Name (ARN) of an Key Management Service key that SageMaker uses to encrypt the captured data at rest using Amazon S3 server-side encryption.</p> <p>The KmsKeyId can be any of the following formats: </p> <ul> <li> <p>Key ID: <code>1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Key ARN: <code>arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab</code> </p> </li> <li> <p>Alias name: <code>alias/ExampleAlias</code> </p> </li> <li> <p>Alias name ARN: <code>arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias</code> </p> </li> </ul>
       capture_options: 	 <p>Specifies data Model Monitor will capture. You can configure whether to collect only input, only output, or both</p>
       capture_content_type_header: 	 <p>Configuration specifying how to treat different headers. If no headers are specified SageMaker will by default base64 encode when capturing the data.</p>
    """

    initial_sampling_percentage: int
    destination_s3_uri: str
    capture_options: List[CaptureOption]
    enable_capture: Optional[bool] = Unassigned()
    kms_key_id: Optional[str] = Unassigned()
    capture_content_type_header: Optional[CaptureContentTypeHeader] = Unassigned()


class ExplainerConfig(Base):
    """
    ExplainerConfig
         <p>A parameter to activate explainers.</p>

        Attributes
       ----------------------
       clarify_explainer_config: 	 <p>A member of <code>ExplainerConfig</code> that contains configuration parameters for the SageMaker Clarify explainer.</p>
    """

    clarify_explainer_config: Optional[ClarifyExplainerConfig] = Unassigned()


class RollingUpdatePolicy(Base):
    """
    RollingUpdatePolicy
         <p>Specifies a rolling deployment strategy for updating a SageMaker endpoint.</p>

        Attributes
       ----------------------
       maximum_batch_size: 	 <p>Batch size for each rolling step to provision capacity and turn on traffic on the new endpoint fleet, and terminate capacity on the old endpoint fleet. Value must be between 5% to 50% of the variant's total instance count.</p>
       wait_interval_in_seconds: 	 <p>The length of the baking period, during which SageMaker monitors alarms for each batch on the new fleet.</p>
       maximum_execution_timeout_in_seconds: 	 <p>The time limit for the total deployment. Exceeding this limit causes a timeout.</p>
       rollback_maximum_batch_size: 	 <p>Batch size for rollback to the old endpoint fleet. Each rolling step to provision capacity and turn on traffic on the old endpoint fleet, and terminate capacity on the new endpoint fleet. If this field is absent, the default value will be set to 100% of total capacity which means to bring up the whole capacity of the old fleet at once during rollback.</p>
    """

    maximum_batch_size: CapacitySize
    wait_interval_in_seconds: int
    maximum_execution_timeout_in_seconds: Optional[int] = Unassigned()
    rollback_maximum_batch_size: Optional[CapacitySize] = Unassigned()


class DeploymentConfig(Base):
    """
    DeploymentConfig
         <p>The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations.</p>

        Attributes
       ----------------------
       blue_green_update_policy: 	 <p>Update policy for a blue/green deployment. If this update policy is specified, SageMaker creates a new fleet during the deployment while maintaining the old fleet. SageMaker flips traffic to the new fleet according to the specified traffic routing configuration. Only one update policy should be used in the deployment configuration. If no update policy is specified, SageMaker uses a blue/green deployment strategy with all at once traffic shifting by default.</p>
       rolling_update_policy: 	 <p>Specifies a rolling deployment strategy for updating a SageMaker endpoint.</p>
       auto_rollback_configuration: 	 <p>Automatic rollback configuration for handling endpoint deployment failures and recovery.</p>
    """

    blue_green_update_policy: Optional[BlueGreenUpdatePolicy] = Unassigned()
    rolling_update_policy: Optional[RollingUpdatePolicy] = Unassigned()
    auto_rollback_configuration: Optional[AutoRollbackConfig] = Unassigned()


class FeatureDefinition(Base):
    """
    FeatureDefinition
         <p>A list of features. You must include <code>FeatureName</code> and <code>FeatureType</code>. Valid feature <code>FeatureType</code>s are <code>Integral</code>, <code>Fractional</code> and <code>String</code>. </p>

        Attributes
       ----------------------
       feature_name: 	 <p>The name of a feature. The type must be a string. <code>FeatureName</code> cannot be any of the following: <code>is_deleted</code>, <code>write_time</code>, <code>api_invocation_time</code>.</p> <p>The name:</p> <ul> <li> <p>Must start and end with an alphanumeric character.</p> </li> <li> <p>Can only include alphanumeric characters, underscores, and hyphens. Spaces are not allowed.</p> </li> </ul>
       feature_type: 	 <p>The value type of a feature. Valid values are Integral, Fractional, or String.</p>
       collection_type: 	 <p>A grouping of elements where each element within the collection must have the same feature type (<code>String</code>, <code>Integral</code>, or <code>Fractional</code>).</p> <ul> <li> <p> <code>List</code>: An ordered collection of elements.</p> </li> <li> <p> <code>Set</code>: An unordered collection of unique elements.</p> </li> <li> <p> <code>Vector</code>: A specialized list that represents a fixed-size array of elements. The vector dimension is determined by you. Must have elements with fractional feature types. </p> </li> </ul>
       collection_config: 	 <p>Configuration for your collection.</p>
    """

    feature_name: str
    feature_type: str
    collection_type: Optional[str] = Unassigned()
    collection_config: Optional[CollectionConfig] = Unassigned()


class OnlineStoreSecurityConfig(Base):
    """
    OnlineStoreSecurityConfig
         <p>The security configuration for <code>OnlineStore</code>.</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (KMS) key ARN that SageMaker Feature Store uses to encrypt the Amazon S3 objects at rest using Amazon S3 server-side encryption.</p> <p>The caller (either user or IAM role) of <code>CreateFeatureGroup</code> must have below permissions to the <code>OnlineStore</code> <code>KmsKeyId</code>:</p> <ul> <li> <p> <code>"kms:Encrypt"</code> </p> </li> <li> <p> <code>"kms:Decrypt"</code> </p> </li> <li> <p> <code>"kms:DescribeKey"</code> </p> </li> <li> <p> <code>"kms:CreateGrant"</code> </p> </li> <li> <p> <code>"kms:RetireGrant"</code> </p> </li> <li> <p> <code>"kms:ReEncryptFrom"</code> </p> </li> <li> <p> <code>"kms:ReEncryptTo"</code> </p> </li> <li> <p> <code>"kms:GenerateDataKey"</code> </p> </li> <li> <p> <code>"kms:ListAliases"</code> </p> </li> <li> <p> <code>"kms:ListGrants"</code> </p> </li> <li> <p> <code>"kms:RevokeGrant"</code> </p> </li> </ul> <p>The caller (either user or IAM role) to all DataPlane operations (<code>PutRecord</code>, <code>GetRecord</code>, <code>DeleteRecord</code>) must have the following permissions to the <code>KmsKeyId</code>:</p> <ul> <li> <p> <code>"kms:Decrypt"</code> </p> </li> </ul>
    """

    kms_key_id: Optional[str] = Unassigned()


class TtlDuration(Base):
    """
    TtlDuration
         <p>Time to live duration, where the record is hard deleted after the expiration time is reached; <code>ExpiresAt</code> = <code>EventTime</code> + <code>TtlDuration</code>. For information on HardDelete, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_feature_store_DeleteRecord.html">DeleteRecord</a> API in the Amazon SageMaker API Reference guide.</p>

        Attributes
       ----------------------
       unit: 	 <p> <code>TtlDuration</code> time unit.</p>
       value: 	 <p> <code>TtlDuration</code> time value.</p>
    """

    unit: Optional[str] = Unassigned()
    value: Optional[int] = Unassigned()


class OnlineStoreConfig(Base):
    """
    OnlineStoreConfig
         <p>Use this to specify the Amazon Web Services Key Management Service (KMS) Key ID, or <code>KMSKeyId</code>, for at rest data encryption. You can turn <code>OnlineStore</code> on or off by specifying the <code>EnableOnlineStore</code> flag at General Assembly.</p> <p>The default value is <code>False</code>.</p>

        Attributes
       ----------------------
       security_config: 	 <p>Use to specify KMS Key ID (<code>KMSKeyId</code>) for at-rest encryption of your <code>OnlineStore</code>.</p>
       enable_online_store: 	 <p>Turn <code>OnlineStore</code> off by specifying <code>False</code> for the <code>EnableOnlineStore</code> flag. Turn <code>OnlineStore</code> on by specifying <code>True</code> for the <code>EnableOnlineStore</code> flag. </p> <p>The default value is <code>False</code>.</p>
       ttl_duration: 	 <p>Time to live duration, where the record is hard deleted after the expiration time is reached; <code>ExpiresAt</code> = <code>EventTime</code> + <code>TtlDuration</code>. For information on HardDelete, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_feature_store_DeleteRecord.html">DeleteRecord</a> API in the Amazon SageMaker API Reference guide.</p>
       storage_type: 	 <p>Option for different tiers of low latency storage for real-time data retrieval.</p> <ul> <li> <p> <code>Standard</code>: A managed low latency data store for feature groups.</p> </li> <li> <p> <code>InMemory</code>: A managed data store for feature groups that supports very low latency retrieval. </p> </li> </ul>
    """

    security_config: Optional[OnlineStoreSecurityConfig] = Unassigned()
    enable_online_store: Optional[bool] = Unassigned()
    ttl_duration: Optional[TtlDuration] = Unassigned()
    storage_type: Optional[str] = Unassigned()


class S3StorageConfig(Base):
    """
    S3StorageConfig
         <p>The Amazon Simple Storage (Amazon S3) location and security configuration for <code>OfflineStore</code>.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The S3 URI, or location in Amazon S3, of <code>OfflineStore</code>.</p> <p>S3 URIs have a format similar to the following: <code>s3://example-bucket/prefix/</code>.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (KMS) key ARN of the key used to encrypt any objects written into the <code>OfflineStore</code> S3 location.</p> <p>The IAM <code>roleARN</code> that is passed as a parameter to <code>CreateFeatureGroup</code> must have below permissions to the <code>KmsKeyId</code>:</p> <ul> <li> <p> <code>"kms:GenerateDataKey"</code> </p> </li> </ul>
       resolved_output_s3_uri: 	 <p>The S3 path where offline records are written.</p>
    """

    s3_uri: str
    kms_key_id: Optional[str] = Unassigned()
    resolved_output_s3_uri: Optional[str] = Unassigned()


class DataCatalogConfig(Base):
    """
    DataCatalogConfig
         <p>The meta data of the Glue table which serves as data catalog for the <code>OfflineStore</code>. </p>

        Attributes
       ----------------------
       table_name: 	 <p>The name of the Glue table.</p>
       catalog: 	 <p>The name of the Glue table catalog.</p>
       database: 	 <p>The name of the Glue table database.</p>
    """

    table_name: str
    catalog: str
    database: str


class OfflineStoreConfig(Base):
    """
    OfflineStoreConfig
         <p>The configuration of an <code>OfflineStore</code>.</p> <p>Provide an <code>OfflineStoreConfig</code> in a request to <code>CreateFeatureGroup</code> to create an <code>OfflineStore</code>.</p> <p>To encrypt an <code>OfflineStore</code> using at rest data encryption, specify Amazon Web Services Key Management Service (KMS) key ID, or <code>KMSKeyId</code>, in <code>S3StorageConfig</code>.</p>

        Attributes
       ----------------------
       s3_storage_config: 	 <p>The Amazon Simple Storage (Amazon S3) location of <code>OfflineStore</code>.</p>
       disable_glue_table_creation: 	 <p>Set to <code>True</code> to disable the automatic creation of an Amazon Web Services Glue table when configuring an <code>OfflineStore</code>. If set to <code>False</code>, Feature Store will name the <code>OfflineStore</code> Glue table following <a href="https://docs.aws.amazon.com/athena/latest/ug/tables-databases-columns-names.html">Athena's naming recommendations</a>.</p> <p>The default value is <code>False</code>.</p>
       data_catalog_config: 	 <p>The meta data of the Glue table that is autogenerated when an <code>OfflineStore</code> is created. </p>
       table_format: 	 <p>Format for the offline store table. Supported formats are Glue (Default) and <a href="https://iceberg.apache.org/">Apache Iceberg</a>.</p>
    """

    s3_storage_config: S3StorageConfig
    disable_glue_table_creation: Optional[bool] = Unassigned()
    data_catalog_config: Optional[DataCatalogConfig] = Unassigned()
    table_format: Optional[str] = Unassigned()


class ThroughputConfig(Base):
    """
    ThroughputConfig
         <p>Used to set feature group throughput configuration. There are two modes: <code>ON_DEMAND</code> and <code>PROVISIONED</code>. With on-demand mode, you are charged for data reads and writes that your application performs on your feature group. You do not need to specify read and write throughput because Feature Store accommodates your workloads as they ramp up and down. You can switch a feature group to on-demand only once in a 24 hour period. With provisioned throughput mode, you specify the read and write capacity per second that you expect your application to require, and you are billed based on those limits. Exceeding provisioned throughput will result in your requests being throttled. </p> <p>Note: <code>PROVISIONED</code> throughput mode is supported only for feature groups that are offline-only, or use the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OnlineStoreConfig.html#sagemaker-Type-OnlineStoreConfig-StorageType"> <code>Standard</code> </a> tier online store. </p>

        Attributes
       ----------------------
       throughput_mode: 	 <p>The mode used for your feature group throughput: <code>ON_DEMAND</code> or <code>PROVISIONED</code>. </p>
       provisioned_read_capacity_units: 	 <p> For provisioned feature groups with online store enabled, this indicates the read throughput you are billed for and can consume without throttling. </p> <p>This field is not applicable for on-demand feature groups. </p>
       provisioned_write_capacity_units: 	 <p> For provisioned feature groups, this indicates the write throughput you are billed for and can consume without throttling. </p> <p>This field is not applicable for on-demand feature groups. </p>
    """

    throughput_mode: str
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


class HumanLoopRequestSource(Base):
    """
    HumanLoopRequestSource
         <p>Container for configuring the source of human task requests.</p>

        Attributes
       ----------------------
       aws_managed_human_loop_request_source: 	 <p>Specifies whether Amazon Rekognition or Amazon Textract are used as the integration source. The default field settings and JSON parsing rules are different based on the integration source. Valid values:</p>
    """

    aws_managed_human_loop_request_source: str


class HumanLoopActivationConditionsConfig(Base):
    """
    HumanLoopActivationConditionsConfig
         <p>Defines under what conditions SageMaker creates a human loop. Used within <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateFlowDefinition.html">CreateFlowDefinition</a>. See <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HumanLoopActivationConditionsConfig.html">HumanLoopActivationConditionsConfig</a> for the required format of activation conditions.</p>

        Attributes
       ----------------------
       human_loop_activation_conditions: 	 <p>JSON expressing use-case specific conditions declaratively. If any condition is matched, atomic tasks are created against the configured work team. The set of conditions is different for Rekognition and Textract. For more information about how to structure the JSON, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-human-fallback-conditions-json-schema.html">JSON Schema for Human Loop Activation Conditions in Amazon Augmented AI</a> in the <i>Amazon SageMaker Developer Guide</i>.</p>
    """

    human_loop_activation_conditions: str


class HumanLoopActivationConfig(Base):
    """
    HumanLoopActivationConfig
         <p>Provides information about how and under what conditions SageMaker creates a human loop. If <code>HumanLoopActivationConfig</code> is not given, then all requests go to humans.</p>

        Attributes
       ----------------------
       human_loop_activation_conditions_config: 	 <p>Container structure for defining under what conditions SageMaker creates a human loop.</p>
    """

    human_loop_activation_conditions_config: HumanLoopActivationConditionsConfig


class USD(Base):
    """
    USD
         <p>Represents an amount of money in United States dollars.</p>

        Attributes
       ----------------------
       dollars: 	 <p>The whole number of dollars in the amount.</p>
       cents: 	 <p>The fractional portion, in cents, of the amount. </p>
       tenth_fractions_of_a_cent: 	 <p>Fractions of a cent, in tenths.</p>
    """

    dollars: Optional[int] = Unassigned()
    cents: Optional[int] = Unassigned()
    tenth_fractions_of_a_cent: Optional[int] = Unassigned()


class PublicWorkforceTaskPrice(Base):
    """
    PublicWorkforceTaskPrice
         <p>Defines the amount of money paid to an Amazon Mechanical Turk worker for each task performed. </p> <p>Use one of the following prices for bounding box tasks. Prices are in US dollars and should be based on the complexity of the task; the longer it takes in your initial testing, the more you should offer.</p> <ul> <li> <p>0.036</p> </li> <li> <p>0.048</p> </li> <li> <p>0.060</p> </li> <li> <p>0.072</p> </li> <li> <p>0.120</p> </li> <li> <p>0.240</p> </li> <li> <p>0.360</p> </li> <li> <p>0.480</p> </li> <li> <p>0.600</p> </li> <li> <p>0.720</p> </li> <li> <p>0.840</p> </li> <li> <p>0.960</p> </li> <li> <p>1.080</p> </li> <li> <p>1.200</p> </li> </ul> <p>Use one of the following prices for image classification, text classification, and custom tasks. Prices are in US dollars.</p> <ul> <li> <p>0.012</p> </li> <li> <p>0.024</p> </li> <li> <p>0.036</p> </li> <li> <p>0.048</p> </li> <li> <p>0.060</p> </li> <li> <p>0.072</p> </li> <li> <p>0.120</p> </li> <li> <p>0.240</p> </li> <li> <p>0.360</p> </li> <li> <p>0.480</p> </li> <li> <p>0.600</p> </li> <li> <p>0.720</p> </li> <li> <p>0.840</p> </li> <li> <p>0.960</p> </li> <li> <p>1.080</p> </li> <li> <p>1.200</p> </li> </ul> <p>Use one of the following prices for semantic segmentation tasks. Prices are in US dollars.</p> <ul> <li> <p>0.840</p> </li> <li> <p>0.960</p> </li> <li> <p>1.080</p> </li> <li> <p>1.200</p> </li> </ul> <p>Use one of the following prices for Textract AnalyzeDocument Important Form Key Amazon Augmented AI review tasks. Prices are in US dollars.</p> <ul> <li> <p>2.400 </p> </li> <li> <p>2.280 </p> </li> <li> <p>2.160 </p> </li> <li> <p>2.040 </p> </li> <li> <p>1.920 </p> </li> <li> <p>1.800 </p> </li> <li> <p>1.680 </p> </li> <li> <p>1.560 </p> </li> <li> <p>1.440 </p> </li> <li> <p>1.320 </p> </li> <li> <p>1.200 </p> </li> <li> <p>1.080 </p> </li> <li> <p>0.960 </p> </li> <li> <p>0.840 </p> </li> <li> <p>0.720 </p> </li> <li> <p>0.600 </p> </li> <li> <p>0.480 </p> </li> <li> <p>0.360 </p> </li> <li> <p>0.240 </p> </li> <li> <p>0.120 </p> </li> <li> <p>0.072 </p> </li> <li> <p>0.060 </p> </li> <li> <p>0.048 </p> </li> <li> <p>0.036 </p> </li> <li> <p>0.024 </p> </li> <li> <p>0.012 </p> </li> </ul> <p>Use one of the following prices for Rekognition DetectModerationLabels Amazon Augmented AI review tasks. Prices are in US dollars.</p> <ul> <li> <p>1.200 </p> </li> <li> <p>1.080 </p> </li> <li> <p>0.960 </p> </li> <li> <p>0.840 </p> </li> <li> <p>0.720 </p> </li> <li> <p>0.600 </p> </li> <li> <p>0.480 </p> </li> <li> <p>0.360 </p> </li> <li> <p>0.240 </p> </li> <li> <p>0.120 </p> </li> <li> <p>0.072 </p> </li> <li> <p>0.060 </p> </li> <li> <p>0.048 </p> </li> <li> <p>0.036 </p> </li> <li> <p>0.024 </p> </li> <li> <p>0.012 </p> </li> </ul> <p>Use one of the following prices for Amazon Augmented AI custom human review tasks. Prices are in US dollars.</p> <ul> <li> <p>1.200 </p> </li> <li> <p>1.080 </p> </li> <li> <p>0.960 </p> </li> <li> <p>0.840 </p> </li> <li> <p>0.720 </p> </li> <li> <p>0.600 </p> </li> <li> <p>0.480 </p> </li> <li> <p>0.360 </p> </li> <li> <p>0.240 </p> </li> <li> <p>0.120 </p> </li> <li> <p>0.072 </p> </li> <li> <p>0.060 </p> </li> <li> <p>0.048 </p> </li> <li> <p>0.036 </p> </li> <li> <p>0.024 </p> </li> <li> <p>0.012 </p> </li> </ul>

        Attributes
       ----------------------
       amount_in_usd: 	 <p>Defines the amount of money paid to an Amazon Mechanical Turk worker in United States dollars.</p>
    """

    amount_in_usd: Optional[USD] = Unassigned()


class HumanLoopConfig(Base):
    """
    HumanLoopConfig
         <p>Describes the work to be performed by human workers.</p>

        Attributes
       ----------------------
       workteam_arn: 	 <p>Amazon Resource Name (ARN) of a team of workers. To learn more about the types of workforces and work teams you can create and use with Amazon A2I, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-management.html">Create and Manage Workforces</a>.</p>
       human_task_ui_arn: 	 <p>The Amazon Resource Name (ARN) of the human task user interface.</p> <p>You can use standard HTML and Crowd HTML Elements to create a custom worker task template. You use this template to create a human task UI.</p> <p>To learn how to create a custom HTML template, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-custom-templates.html">Create Custom Worker Task Template</a>.</p> <p>To learn how to create a human task UI, which is a worker task template that can be used in a flow definition, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-worker-template-console.html">Create and Delete a Worker Task Templates</a>.</p>
       task_title: 	 <p>A title for the human worker task.</p>
       task_description: 	 <p>A description for the human worker task.</p>
       task_count: 	 <p>The number of distinct workers who will perform the same task on each object. For example, if <code>TaskCount</code> is set to <code>3</code> for an image classification labeling job, three workers will classify each input image. Increasing <code>TaskCount</code> can improve label accuracy.</p>
       task_availability_lifetime_in_seconds: 	 <p>The length of time that a task remains available for review by human workers.</p>
       task_time_limit_in_seconds: 	 <p>The amount of time that a worker has to complete a task. The default value is 3,600 seconds (1 hour).</p>
       task_keywords: 	 <p>Keywords used to describe the task so that workers can discover the task.</p>
       public_workforce_task_price
    """

    workteam_arn: str
    human_task_ui_arn: str
    task_title: str
    task_description: str
    task_count: int
    task_availability_lifetime_in_seconds: Optional[int] = Unassigned()
    task_time_limit_in_seconds: Optional[int] = Unassigned()
    task_keywords: Optional[List[str]] = Unassigned()
    public_workforce_task_price: Optional[PublicWorkforceTaskPrice] = Unassigned()


class FlowDefinitionOutputConfig(Base):
    """
    FlowDefinitionOutputConfig
         <p>Contains information about where human output will be stored.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>The Amazon S3 path where the object containing human output will be made available.</p> <p>To learn more about the format of Amazon A2I output data, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-output-data.html">Amazon A2I Output Data</a>.</p>
       kms_key_id: 	 <p>The Amazon Key Management Service (KMS) key ID for server-side encryption.</p>
    """

    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()


class HubS3StorageConfig(Base):
    """
    HubS3StorageConfig
         <p>The Amazon S3 storage configuration of a hub.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>The Amazon S3 bucket prefix for hosting hub content.</p>
    """

    s3_output_path: Optional[str] = Unassigned()


class UiTemplate(Base):
    """
    UiTemplate
         <p>The Liquid template for the worker user interface.</p>

        Attributes
       ----------------------
       content: 	 <p>The content of the Liquid template for the worker user interface.</p>
    """

    content: str


class HyperbandStrategyConfig(Base):
    """
    HyperbandStrategyConfig
         <p>The configuration for <code>Hyperband</code>, a multi-fidelity based hyperparameter tuning strategy. <code>Hyperband</code> uses the final and intermediate results of a training job to dynamically allocate resources to utilized hyperparameter configurations while automatically stopping under-performing configurations. This parameter should be provided only if <code>Hyperband</code> is selected as the <code>StrategyConfig</code> under the <code>HyperParameterTuningJobConfig</code> API.</p>

        Attributes
       ----------------------
       min_resource: 	 <p>The minimum number of resources (such as epochs) that can be used by a training job launched by a hyperparameter tuning job. If the value for <code>MinResource</code> has not been reached, the training job is not stopped by <code>Hyperband</code>.</p>
       max_resource: 	 <p>The maximum number of resources (such as epochs) that can be used by a training job launched by a hyperparameter tuning job. Once a job reaches the <code>MaxResource</code> value, it is stopped. If a value for <code>MaxResource</code> is not provided, and <code>Hyperband</code> is selected as the hyperparameter tuning strategy, <code>HyperbandTraining</code> attempts to infer <code>MaxResource</code> from the following keys (if present) in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTrainingJobDefinition.html#sagemaker-Type-HyperParameterTrainingJobDefinition-StaticHyperParameters">StaticsHyperParameters</a>:</p> <ul> <li> <p> <code>epochs</code> </p> </li> <li> <p> <code>numepochs</code> </p> </li> <li> <p> <code>n-epochs</code> </p> </li> <li> <p> <code>n_epochs</code> </p> </li> <li> <p> <code>num_epochs</code> </p> </li> </ul> <p>If <code>HyperbandStrategyConfig</code> is unable to infer a value for <code>MaxResource</code>, it generates a validation error. The maximum value is 20,000 epochs. All metrics that correspond to an objective metric are used to derive <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-early-stopping.html">early stopping decisions</a>. For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/distributed-training.html">distributed</a> training jobs, ensure that duplicate metrics are not printed in the logs across the individual nodes in a training job. If multiple nodes are publishing duplicate or incorrect metrics, training jobs may make an incorrect stopping decision and stop the job prematurely. </p>
    """

    min_resource: Optional[int] = Unassigned()
    max_resource: Optional[int] = Unassigned()


class HyperParameterTuningJobStrategyConfig(Base):
    """
    HyperParameterTuningJobStrategyConfig
         <p>The configuration for a training job launched by a hyperparameter tuning job. Choose <code>Bayesian</code> for Bayesian optimization, and <code>Random</code> for random search optimization. For more advanced use cases, use <code>Hyperband</code>, which evaluates objective metrics for training jobs after every epoch. For more information about strategies, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-how-it-works.html">How Hyperparameter Tuning Works</a>.</p>

        Attributes
       ----------------------
       hyperband_strategy_config: 	 <p>The configuration for the object that specifies the <code>Hyperband</code> strategy. This parameter is only supported for the <code>Hyperband</code> selection for <code>Strategy</code> within the <code>HyperParameterTuningJobConfig</code> API.</p>
    """

    hyperband_strategy_config: Optional[HyperbandStrategyConfig] = Unassigned()


class ResourceLimits(Base):
    """
    ResourceLimits
         <p>Specifies the maximum number of training jobs and parallel training jobs that a hyperparameter tuning job can launch.</p>

        Attributes
       ----------------------
       max_number_of_training_jobs: 	 <p>The maximum number of training jobs that a hyperparameter tuning job can launch.</p>
       max_parallel_training_jobs: 	 <p>The maximum number of concurrent training jobs that a hyperparameter tuning job can launch.</p>
       max_runtime_in_seconds: 	 <p>The maximum time in seconds that a hyperparameter tuning job can run.</p>
    """

    max_parallel_training_jobs: int
    max_number_of_training_jobs: Optional[int] = Unassigned()
    max_runtime_in_seconds: Optional[int] = Unassigned()


class IntegerParameterRange(Base):
    """
    IntegerParameterRange
         <p>For a hyperparameter of the integer type, specifies the range that a hyperparameter tuning job searches.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the hyperparameter to search.</p>
       min_value: 	 <p>The minimum value of the hyperparameter to search.</p>
       max_value: 	 <p>The maximum value of the hyperparameter to search.</p>
       scaling_type: 	 <p>The scale that hyperparameter tuning uses to search the hyperparameter range. For information about choosing a hyperparameter scale, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-ranges.html#scaling-type">Hyperparameter Scaling</a>. One of the following values:</p> <dl> <dt>Auto</dt> <dd> <p>SageMaker hyperparameter tuning chooses the best scale for the hyperparameter.</p> </dd> <dt>Linear</dt> <dd> <p>Hyperparameter tuning searches the values in the hyperparameter range by using a linear scale.</p> </dd> <dt>Logarithmic</dt> <dd> <p>Hyperparameter tuning searches the values in the hyperparameter range by using a logarithmic scale.</p> <p>Logarithmic scaling works only for ranges that have only values greater than 0.</p> </dd> </dl>
    """

    name: str
    min_value: str
    max_value: str
    scaling_type: Optional[str] = Unassigned()


class ParameterRanges(Base):
    """
    ParameterRanges
         <p>Specifies ranges of integer, continuous, and categorical hyperparameters that a hyperparameter tuning job searches. The hyperparameter tuning job launches training jobs with hyperparameter values within these ranges to find the combination of values that result in the training job with the best performance as measured by the objective metric of the hyperparameter tuning job.</p> <note> <p>The maximum number of items specified for <code>Array Members</code> refers to the maximum number of hyperparameters for each range and also the maximum for the hyperparameter tuning job itself. That is, the sum of the number of hyperparameters for all the ranges can't exceed the maximum number specified.</p> </note>

        Attributes
       ----------------------
       integer_parameter_ranges: 	 <p>The array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_IntegerParameterRange.html">IntegerParameterRange</a> objects that specify ranges of integer hyperparameters that a hyperparameter tuning job searches.</p>
       continuous_parameter_ranges: 	 <p>The array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ContinuousParameterRange.html">ContinuousParameterRange</a> objects that specify ranges of continuous hyperparameters that a hyperparameter tuning job searches.</p>
       categorical_parameter_ranges: 	 <p>The array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CategoricalParameterRange.html">CategoricalParameterRange</a> objects that specify ranges of categorical hyperparameters that a hyperparameter tuning job searches.</p>
       auto_parameters: 	 <p>A list containing hyperparameter names and example values to be used by Autotune to determine optimal ranges for your tuning job.</p>
    """

    integer_parameter_ranges: Optional[List[IntegerParameterRange]] = Unassigned()
    continuous_parameter_ranges: Optional[List[ContinuousParameterRange]] = Unassigned()
    categorical_parameter_ranges: Optional[List[CategoricalParameterRange]] = (
        Unassigned()
    )
    auto_parameters: Optional[List[AutoParameter]] = Unassigned()


class TuningJobCompletionCriteria(Base):
    """
    TuningJobCompletionCriteria
         <p>The job completion criteria.</p>

        Attributes
       ----------------------
       target_objective_metric_value: 	 <p>The value of the objective metric.</p>
       best_objective_not_improving: 	 <p>A flag to stop your hyperparameter tuning job if model performance fails to improve as evaluated against an objective function.</p>
       convergence_detected: 	 <p>A flag to top your hyperparameter tuning job if automatic model tuning (AMT) has detected that your model has converged as evaluated against your objective function.</p>
    """

    target_objective_metric_value: Optional[float] = Unassigned()
    best_objective_not_improving: Optional[BestObjectiveNotImproving] = Unassigned()
    convergence_detected: Optional[ConvergenceDetected] = Unassigned()


class HyperParameterTuningJobConfig(Base):
    """
    HyperParameterTuningJobConfig
         <p>Configures a hyperparameter tuning job.</p>

        Attributes
       ----------------------
       strategy: 	 <p>Specifies how hyperparameter tuning chooses the combinations of hyperparameter values to use for the training job it launches. For information about search strategies, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-how-it-works.html">How Hyperparameter Tuning Works</a>.</p>
       strategy_config: 	 <p>The configuration for the <code>Hyperband</code> optimization strategy. This parameter should be provided only if <code>Hyperband</code> is selected as the strategy for <code>HyperParameterTuningJobConfig</code>.</p>
       hyper_parameter_tuning_job_objective: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobObjective.html">HyperParameterTuningJobObjective</a> specifies the objective metric used to evaluate the performance of training jobs launched by this tuning job.</p>
       resource_limits: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ResourceLimits.html">ResourceLimits</a> object that specifies the maximum number of training and parallel training jobs that can be used for this hyperparameter tuning job.</p>
       parameter_ranges: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ParameterRanges.html">ParameterRanges</a> object that specifies the ranges of hyperparameters that this tuning job searches over to find the optimal configuration for the highest model performance against your chosen objective metric. </p>
       training_job_early_stopping_type: 	 <p>Specifies whether to use early stopping for training jobs launched by the hyperparameter tuning job. Because the <code>Hyperband</code> strategy has its own advanced internal early stopping mechanism, <code>TrainingJobEarlyStoppingType</code> must be <code>OFF</code> to use <code>Hyperband</code>. This parameter can take on one of the following values (the default value is <code>OFF</code>):</p> <dl> <dt>OFF</dt> <dd> <p>Training jobs launched by the hyperparameter tuning job do not use early stopping.</p> </dd> <dt>AUTO</dt> <dd> <p>SageMaker stops training jobs launched by the hyperparameter tuning job when they are unlikely to perform better than previously completed training jobs. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-early-stopping.html">Stop Training Jobs Early</a>.</p> </dd> </dl>
       tuning_job_completion_criteria: 	 <p>The tuning job's completion criteria.</p>
       random_seed: 	 <p>A value used to initialize a pseudo-random number generator. Setting a random seed and using the same seed later for the same tuning job will allow hyperparameter optimization to find more a consistent hyperparameter configuration between the two runs.</p>
    """

    strategy: str
    resource_limits: ResourceLimits
    strategy_config: Optional[HyperParameterTuningJobStrategyConfig] = Unassigned()
    hyper_parameter_tuning_job_objective: Optional[HyperParameterTuningJobObjective] = (
        Unassigned()
    )
    parameter_ranges: Optional[ParameterRanges] = Unassigned()
    training_job_early_stopping_type: Optional[str] = Unassigned()
    tuning_job_completion_criteria: Optional[TuningJobCompletionCriteria] = Unassigned()
    random_seed: Optional[int] = Unassigned()


class HyperParameterAlgorithmSpecification(Base):
    """
    HyperParameterAlgorithmSpecification
         <p>Specifies which training algorithm to use for training jobs that a hyperparameter tuning job launches and the metrics to monitor.</p>

        Attributes
       ----------------------
       training_image: 	 <p> The registry path of the Docker image that contains the training algorithm. For information about Docker registry paths for built-in algorithms, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-algo-docker-registry-paths.html">Algorithms Provided by Amazon SageMaker: Common Parameters</a>. SageMaker supports both <code>registry/repository[:tag]</code> and <code>registry/repository[@digest]</code> image path formats. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms.html">Using Your Own Algorithms with Amazon SageMaker</a>.</p>
       training_input_mode
       algorithm_name: 	 <p>The name of the resource algorithm to use for the hyperparameter tuning job. If you specify a value for this parameter, do not specify a value for <code>TrainingImage</code>.</p>
       metric_definitions: 	 <p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_MetricDefinition.html">MetricDefinition</a> objects that specify the metrics that the algorithm emits.</p>
    """

    training_input_mode: str
    training_image: Optional[str] = Unassigned()
    algorithm_name: Optional[str] = Unassigned()
    metric_definitions: Optional[List[MetricDefinition]] = Unassigned()


class HyperParameterTuningInstanceConfig(Base):
    """
    HyperParameterTuningInstanceConfig
         <p>The configuration for hyperparameter tuning resources for use in training jobs launched by the tuning job. These resources include compute instances and storage volumes. Specify one or more compute instance configurations and allocation strategies to select resources (optional).</p>

        Attributes
       ----------------------
       instance_type: 	 <p>The instance type used for processing of hyperparameter optimization jobs. Choose from general purpose (no GPUs) instance types: ml.m5.xlarge, ml.m5.2xlarge, and ml.m5.4xlarge or compute optimized (no GPUs) instance types: ml.c5.xlarge and ml.c5.2xlarge. For more information about instance types, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-instance-types.html">instance type descriptions</a>.</p>
       instance_count: 	 <p>The number of instances of the type specified by <code>InstanceType</code>. Choose an instance count larger than 1 for distributed training algorithms. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/data-parallel-use-api.html">Step 2: Launch a SageMaker Distributed Training Job Using the SageMaker Python SDK</a> for more information.</p>
       volume_size_in_g_b: 	 <p>The volume size in GB of the data to be processed for hyperparameter optimization (optional).</p>
    """

    instance_type: str
    instance_count: int
    volume_size_in_g_b: int


class HyperParameterTuningResourceConfig(Base):
    """
    HyperParameterTuningResourceConfig
         <p>The configuration of resources, including compute instances and storage volumes for use in training jobs launched by hyperparameter tuning jobs. <code>HyperParameterTuningResourceConfig</code> is similar to <code>ResourceConfig</code>, but has the additional <code>InstanceConfigs</code> and <code>AllocationStrategy</code> fields to allow for flexible instance management. Specify one or more instance types, count, and the allocation strategy for instance selection.</p> <note> <p> <code>HyperParameterTuningResourceConfig</code> supports the capabilities of <code>ResourceConfig</code> with the exception of <code>KeepAlivePeriodInSeconds</code>. Hyperparameter tuning jobs use warm pools by default, which reuse clusters between training jobs.</p> </note>

        Attributes
       ----------------------
       instance_type: 	 <p>The instance type used to run hyperparameter optimization tuning jobs. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-available-instance-types.html"> descriptions of instance types</a> for more information.</p>
       instance_count: 	 <p>The number of compute instances of type <code>InstanceType</code> to use. For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/data-parallel-use-api.html">distributed training</a>, select a value greater than 1.</p>
       volume_size_in_g_b: 	 <p>The volume size in GB for the storage volume to be used in processing hyperparameter optimization jobs (optional). These volumes store model artifacts, incremental states and optionally, scratch space for training algorithms. Do not provide a value for this parameter if a value for <code>InstanceConfigs</code> is also specified.</p> <p>Some instance types have a fixed total local storage size. If you select one of these instances for training, <code>VolumeSizeInGB</code> cannot be greater than this total size. For a list of instance types with local instance storage and their sizes, see <a href="http://aws.amazon.com/releasenotes/host-instance-storage-volumes-table/">instance store volumes</a>.</p> <note> <p>SageMaker supports only the <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html">General Purpose SSD (gp2)</a> storage volume type.</p> </note>
       volume_kms_key_id: 	 <p>A key used by Amazon Web Services Key Management Service to encrypt data on the storage volume attached to the compute instances used to run the training job. You can use either of the following formats to specify a key.</p> <p>KMS Key ID:</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> <p>Amazon Resource Name (ARN) of a KMS key:</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> <p>Some instances use local storage, which use a <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html">hardware module to encrypt</a> storage volumes. If you choose one of these instance types, you cannot request a <code>VolumeKmsKeyId</code>. For a list of instance types that use local storage, see <a href="http://aws.amazon.com/releasenotes/host-instance-storage-volumes-table/">instance store volumes</a>. For more information about Amazon Web Services Key Management Service, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-security-kms-permissions.html">KMS encryption</a> for more information.</p>
       allocation_strategy: 	 <p>The strategy that determines the order of preference for resources specified in <code>InstanceConfigs</code> used in hyperparameter optimization.</p>
       instance_configs: 	 <p>A list containing the configuration(s) for one or more resources for processing hyperparameter jobs. These resources include compute instances and storage volumes to use in model training jobs launched by hyperparameter tuning jobs. The <code>AllocationStrategy</code> controls the order in which multiple configurations provided in <code>InstanceConfigs</code> are used.</p> <note> <p>If you only want to use a single instance configuration inside the <code>HyperParameterTuningResourceConfig</code> API, do not provide a value for <code>InstanceConfigs</code>. Instead, use <code>InstanceType</code>, <code>VolumeSizeInGB</code> and <code>InstanceCount</code>. If you use <code>InstanceConfigs</code>, do not provide values for <code>InstanceType</code>, <code>VolumeSizeInGB</code> or <code>InstanceCount</code>.</p> </note>
    """

    instance_type: Optional[str] = Unassigned()
    instance_count: Optional[int] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    allocation_strategy: Optional[str] = Unassigned()
    instance_configs: Optional[List[HyperParameterTuningInstanceConfig]] = Unassigned()


class RetryStrategy(Base):
    """
    RetryStrategy
         <p>The retry strategy to use when a training job fails due to an <code>InternalServerError</code>. <code>RetryStrategy</code> is specified as part of the <code>CreateTrainingJob</code> and <code>CreateHyperParameterTuningJob</code> requests. You can add the <code>StoppingCondition</code> parameter to the request to limit the training time for the complete job.</p>

        Attributes
       ----------------------
       maximum_retry_attempts: 	 <p>The number of times to retry the job. When the job is retried, it's <code>SecondaryStatus</code> is changed to <code>STARTING</code>.</p>
    """

    maximum_retry_attempts: int


class HyperParameterTrainingJobDefinition(Base):
    """
    HyperParameterTrainingJobDefinition
         <p>Defines the training jobs launched by a hyperparameter tuning job.</p>

        Attributes
       ----------------------
       definition_name: 	 <p>The job definition name.</p>
       tuning_objective
       hyper_parameter_ranges
       static_hyper_parameters: 	 <p>Specifies the values of hyperparameters that do not change for the tuning job.</p>
       algorithm_specification: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterAlgorithmSpecification.html">HyperParameterAlgorithmSpecification</a> object that specifies the resource algorithm to use for the training jobs that the tuning job launches.</p>
       role_arn: 	 <p>The Amazon Resource Name (ARN) of the IAM role associated with the training jobs that the tuning job launches.</p>
       input_data_config: 	 <p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Channel.html">Channel</a> objects that specify the input for the training jobs that the tuning job launches.</p>
       vpc_config: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> object that specifies the VPC that you want the training jobs that this hyperparameter tuning job launches to connect to. Control access to and from your training container by configuring the VPC. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-vpc.html">Protect Training Jobs by Using an Amazon Virtual Private Cloud</a>.</p>
       output_data_config: 	 <p>Specifies the path to the Amazon S3 bucket where you store model artifacts from the training jobs that the tuning job launches.</p>
       resource_config: 	 <p>The resources, including the compute instances and storage volumes, to use for the training jobs that the tuning job launches.</p> <p>Storage volumes store model artifacts and incremental states. Training algorithms might also use storage volumes for scratch space. If you want SageMaker to use the storage volume to store the training data, choose <code>File</code> as the <code>TrainingInputMode</code> in the algorithm specification. For distributed training algorithms, specify an instance count greater than 1.</p> <note> <p>If you want to use hyperparameter optimization with instance type flexibility, use <code>HyperParameterTuningResourceConfig</code> instead.</p> </note>
       hyper_parameter_tuning_resource_config: 	 <p>The configuration for the hyperparameter tuning resources, including the compute instances and storage volumes, used for training jobs launched by the tuning job. By default, storage volumes hold model artifacts and incremental states. Choose <code>File</code> for <code>TrainingInputMode</code> in the <code>AlgorithmSpecification</code> parameter to additionally store training data in the storage volume (optional).</p>
       stopping_condition: 	 <p>Specifies a limit to how long a model hyperparameter training job can run. It also specifies how long a managed spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs.</p>
       enable_network_isolation: 	 <p>Isolates the training container. No inbound or outbound network calls can be made, except for calls between peers within a training cluster for distributed training. If network isolation is used for training jobs that are configured to use a VPC, SageMaker downloads and uploads customer data and model artifacts through the specified VPC, but the training container does not have network access.</p>
       enable_inter_container_traffic_encryption: 	 <p>To encrypt all communications between ML compute instances in distributed training, choose <code>True</code>. Encryption provides greater security for distributed training, but training might take longer. How long it takes depends on the amount of communication between compute instances, especially if you use a deep learning algorithm in distributed training.</p>
       enable_managed_spot_training: 	 <p>A Boolean indicating whether managed spot training is enabled (<code>True</code>) or not (<code>False</code>).</p>
       checkpoint_config
       retry_strategy: 	 <p>The number of times to retry the job when the job fails due to an <code>InternalServerError</code>.</p>
       environment: 	 <p>An environment variable that you can pass into the SageMaker <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html">CreateTrainingJob</a> API. You can use an existing <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-Environment">environment variable from the training container</a> or use your own. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-metrics-variables.html">Define metrics and variables</a> for more information.</p> <note> <p>The maximum number of items specified for <code>Map Entries</code> refers to the maximum number of environment variables for each <code>TrainingJobDefinition</code> and also the maximum for the hyperparameter tuning job itself. That is, the sum of the number of environment variables for all the training job definitions can't exceed the maximum number specified.</p> </note>
    """

    algorithm_specification: HyperParameterAlgorithmSpecification
    role_arn: str
    output_data_config: OutputDataConfig
    stopping_condition: StoppingCondition
    definition_name: Optional[str] = Unassigned()
    tuning_objective: Optional[HyperParameterTuningJobObjective] = Unassigned()
    hyper_parameter_ranges: Optional[ParameterRanges] = Unassigned()
    static_hyper_parameters: Optional[Dict[str, str]] = Unassigned()
    input_data_config: Optional[List[Channel]] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    resource_config: Optional[ResourceConfig] = Unassigned()
    hyper_parameter_tuning_resource_config: Optional[
        HyperParameterTuningResourceConfig
    ] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_managed_spot_training: Optional[bool] = Unassigned()
    checkpoint_config: Optional[CheckpointConfig] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class ParentHyperParameterTuningJob(Base):
    """
    ParentHyperParameterTuningJob
         <p>A previously completed or stopped hyperparameter tuning job to be used as a starting point for a new hyperparameter tuning job.</p>

        Attributes
       ----------------------
       hyper_parameter_tuning_job_name: 	 <p>The name of the hyperparameter tuning job to be used as a starting point for a new hyperparameter tuning job.</p>
    """

    hyper_parameter_tuning_job_name: Optional[str] = Unassigned()


class HyperParameterTuningJobWarmStartConfig(Base):
    """
    HyperParameterTuningJobWarmStartConfig
         <p>Specifies the configuration for a hyperparameter tuning job that uses one or more previous hyperparameter tuning jobs as a starting point. The results of previous tuning jobs are used to inform which combinations of hyperparameters to search over in the new tuning job.</p> <p>All training jobs launched by the new hyperparameter tuning job are evaluated by using the objective metric, and the training job that performs the best is compared to the best training jobs from the parent tuning jobs. From these, the training job that performs the best as measured by the objective metric is returned as the overall best training job.</p> <note> <p>All training jobs launched by parent hyperparameter tuning jobs and the new hyperparameter tuning jobs count against the limit of training jobs for the tuning job.</p> </note>

        Attributes
       ----------------------
       parent_hyper_parameter_tuning_jobs: 	 <p>An array of hyperparameter tuning jobs that are used as the starting point for the new hyperparameter tuning job. For more information about warm starting a hyperparameter tuning job, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-warm-start.html">Using a Previous Hyperparameter Tuning Job as a Starting Point</a>.</p> <p>Hyperparameter tuning jobs created before October 1, 2018 cannot be used as parent jobs for warm start tuning jobs.</p>
       warm_start_type: 	 <p>Specifies one of the following:</p> <dl> <dt>IDENTICAL_DATA_AND_ALGORITHM</dt> <dd> <p>The new hyperparameter tuning job uses the same input data and training image as the parent tuning jobs. You can change the hyperparameter ranges to search and the maximum number of training jobs that the hyperparameter tuning job launches. You cannot use a new version of the training algorithm, unless the changes in the new version do not affect the algorithm itself. For example, changes that improve logging or adding support for a different data format are allowed. You can also change hyperparameters from tunable to static, and from static to tunable, but the total number of static plus tunable hyperparameters must remain the same as it is in all parent jobs. The objective metric for the new tuning job must be the same as for all parent jobs.</p> </dd> <dt>TRANSFER_LEARNING</dt> <dd> <p>The new hyperparameter tuning job can include input data, hyperparameter ranges, maximum number of concurrent training jobs, and maximum number of training jobs that are different than those of its parent hyperparameter tuning jobs. The training image can also be a different version from the version used in the parent hyperparameter tuning job. You can also change hyperparameters from tunable to static, and from static to tunable, but the total number of static plus tunable hyperparameters must remain the same as it is in all parent jobs. The objective metric for the new tuning job must be the same as for all parent jobs.</p> </dd> </dl>
    """

    parent_hyper_parameter_tuning_jobs: List[ParentHyperParameterTuningJob]
    warm_start_type: str


class InferenceComponentContainerSpecification(Base):
    """
    InferenceComponentContainerSpecification
         <p>Defines a container that provides the runtime environment for a model that you deploy with an inference component.</p>

        Attributes
       ----------------------
       image: 	 <p>The Amazon Elastic Container Registry (Amazon ECR) path where the Docker image for the model is stored.</p>
       artifact_url: 	 <p>The Amazon S3 path where the model artifacts, which result from model training, are stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix).</p>
       environment: 	 <p>The environment variables to set in the Docker container. Each key and value in the Environment string-to-string map can have length of up to 1024. We support up to 16 entries in the map.</p>
    """

    image: Optional[str] = Unassigned()
    artifact_url: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class InferenceComponentStartupParameters(Base):
    """
    InferenceComponentStartupParameters
         <p>Settings that take effect while the model container starts up.</p>

        Attributes
       ----------------------
       model_data_download_timeout_in_seconds: 	 <p>The timeout value, in seconds, to download and extract the model that you want to host from Amazon S3 to the individual inference instance associated with this inference component.</p>
       container_startup_health_check_timeout_in_seconds: 	 <p>The timeout value, in seconds, for your inference container to pass health check by Amazon S3 Hosting. For more information about health check, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html#your-algorithms-inference-algo-ping-requests">How Your Container Should Respond to Health Check (Ping) Requests</a>.</p>
    """

    model_data_download_timeout_in_seconds: Optional[int] = Unassigned()
    container_startup_health_check_timeout_in_seconds: Optional[int] = Unassigned()


class InferenceComponentComputeResourceRequirements(Base):
    """
    InferenceComponentComputeResourceRequirements
         <p>Defines the compute resources to allocate to run a model that you assign to an inference component. These resources include CPU cores, accelerators, and memory.</p>

        Attributes
       ----------------------
       number_of_cpu_cores_required: 	 <p>The number of CPU cores to allocate to run a model that you assign to an inference component.</p>
       number_of_accelerator_devices_required: 	 <p>The number of accelerators to allocate to run a model that you assign to an inference component. Accelerators include GPUs and Amazon Web Services Inferentia.</p>
       min_memory_required_in_mb: 	 <p>The minimum MB of memory to allocate to run a model that you assign to an inference component.</p>
       max_memory_required_in_mb: 	 <p>The maximum MB of memory to allocate to run a model that you assign to an inference component.</p>
    """

    min_memory_required_in_mb: int
    number_of_cpu_cores_required: Optional[float] = Unassigned()
    number_of_accelerator_devices_required: Optional[float] = Unassigned()
    max_memory_required_in_mb: Optional[int] = Unassigned()


class InferenceComponentSpecification(Base):
    """
    InferenceComponentSpecification
         <p>Details about the resources to deploy with this inference component, including the model, container, and compute resources.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of an existing SageMaker model object in your account that you want to deploy with the inference component.</p>
       container: 	 <p>Defines a container that provides the runtime environment for a model that you deploy with an inference component.</p>
       startup_parameters: 	 <p>Settings that take effect while the model container starts up.</p>
       compute_resource_requirements: 	 <p>The compute resources allocated to run the model assigned to the inference component.</p>
    """

    compute_resource_requirements: InferenceComponentComputeResourceRequirements
    model_name: Optional[str] = Unassigned()
    container: Optional[InferenceComponentContainerSpecification] = Unassigned()
    startup_parameters: Optional[InferenceComponentStartupParameters] = Unassigned()


class InferenceComponentRuntimeConfig(Base):
    """
    InferenceComponentRuntimeConfig
         <p>Runtime settings for a model that is deployed with an inference component.</p>

        Attributes
       ----------------------
       copy_count: 	 <p>The number of runtime copies of the model container to deploy with the inference component. Each copy can serve inference requests.</p>
    """

    copy_count: int


class InferenceExperimentSchedule(Base):
    """
    InferenceExperimentSchedule
         <p>The start and end times of an inference experiment.</p> <p>The maximum duration that you can set for an inference experiment is 30 days.</p>

        Attributes
       ----------------------
       start_time: 	 <p>The timestamp at which the inference experiment started or will start.</p>
       end_time: 	 <p>The timestamp at which the inference experiment ended or will end.</p>
    """

    start_time: Optional[datetime.datetime] = Unassigned()
    end_time: Optional[datetime.datetime] = Unassigned()


class RealTimeInferenceConfig(Base):
    """
    RealTimeInferenceConfig
         <p>The infrastructure configuration for deploying the model to a real-time inference endpoint.</p>

        Attributes
       ----------------------
       instance_type: 	 <p>The instance type the model is deployed to.</p>
       instance_count: 	 <p>The number of instances of the type specified by <code>InstanceType</code>.</p>
    """

    instance_type: str
    instance_count: int


class ModelInfrastructureConfig(Base):
    """
    ModelInfrastructureConfig
         <p>The configuration for the infrastructure that the model will be deployed to.</p>

        Attributes
       ----------------------
       infrastructure_type: 	 <p>The inference option to which to deploy your model. Possible values are the following:</p> <ul> <li> <p> <code>RealTime</code>: Deploy to real-time inference.</p> </li> </ul>
       real_time_inference_config: 	 <p>The infrastructure configuration for deploying the model to real-time inference.</p>
    """

    infrastructure_type: str
    real_time_inference_config: RealTimeInferenceConfig


class ModelVariantConfig(Base):
    """
    ModelVariantConfig
         <p>Contains information about the deployment options of a model.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the Amazon SageMaker Model entity.</p>
       variant_name: 	 <p>The name of the variant.</p>
       infrastructure_config: 	 <p>The configuration for the infrastructure that the model will be deployed to.</p>
    """

    model_name: str
    variant_name: str
    infrastructure_config: ModelInfrastructureConfig


class InferenceExperimentDataStorageConfig(Base):
    """
    InferenceExperimentDataStorageConfig
         <p>The Amazon S3 location and configuration for storing inference request and response data.</p>

        Attributes
       ----------------------
       destination: 	 <p>The Amazon S3 bucket where the inference request and response data is stored. </p>
       kms_key: 	 <p> The Amazon Web Services Key Management Service key that Amazon SageMaker uses to encrypt captured data at rest using Amazon S3 server-side encryption. </p>
       content_type
    """

    destination: str
    kms_key: Optional[str] = Unassigned()
    content_type: Optional[CaptureContentTypeHeader] = Unassigned()


class ShadowModelVariantConfig(Base):
    """
    ShadowModelVariantConfig
         <p>The name and sampling percentage of a shadow variant.</p>

        Attributes
       ----------------------
       shadow_model_variant_name: 	 <p>The name of the shadow variant.</p>
       sampling_percentage: 	 <p> The percentage of inference requests that Amazon SageMaker replicates from the production variant to the shadow variant. </p>
    """

    shadow_model_variant_name: str
    sampling_percentage: int


class ShadowModeConfig(Base):
    """
    ShadowModeConfig
         <p> The configuration of <code>ShadowMode</code> inference experiment type, which specifies a production variant to take all the inference requests, and a shadow variant to which Amazon SageMaker replicates a percentage of the inference requests. For the shadow variant it also specifies the percentage of requests that Amazon SageMaker replicates. </p>

        Attributes
       ----------------------
       source_model_variant_name: 	 <p> The name of the production variant, which takes all the inference requests. </p>
       shadow_model_variants: 	 <p>List of shadow variant configurations.</p>
    """

    source_model_variant_name: str
    shadow_model_variants: List[ShadowModelVariantConfig]


class Phase(Base):
    """
    Phase
         <p>Defines the traffic pattern.</p>

        Attributes
       ----------------------
       initial_number_of_users: 	 <p>Specifies how many concurrent users to start with. The value should be between 1 and 3.</p>
       spawn_rate: 	 <p>Specified how many new users to spawn in a minute.</p>
       duration_in_seconds: 	 <p>Specifies how long a traffic phase should be. For custom load tests, the value should be between 120 and 3600. This value should not exceed <code>JobDurationInSeconds</code>.</p>
    """

    initial_number_of_users: Optional[int] = Unassigned()
    spawn_rate: Optional[int] = Unassigned()
    duration_in_seconds: Optional[int] = Unassigned()


class Stairs(Base):
    """
    Stairs
         <p>Defines the stairs traffic pattern for an Inference Recommender load test. This pattern type consists of multiple steps where the number of users increases at each step.</p> <p>Specify either the stairs or phases traffic pattern.</p>

        Attributes
       ----------------------
       duration_in_seconds: 	 <p>Defines how long each traffic step should be.</p>
       number_of_steps: 	 <p>Specifies how many steps to perform during traffic.</p>
       users_per_step: 	 <p>Specifies how many new users to spawn in each step.</p>
    """

    duration_in_seconds: Optional[int] = Unassigned()
    number_of_steps: Optional[int] = Unassigned()
    users_per_step: Optional[int] = Unassigned()


class TrafficPattern(Base):
    """
    TrafficPattern
         <p>Defines the traffic pattern of the load test.</p>

        Attributes
       ----------------------
       traffic_type: 	 <p>Defines the traffic patterns. Choose either <code>PHASES</code> or <code>STAIRS</code>.</p>
       phases: 	 <p>Defines the phases traffic specification.</p>
       stairs: 	 <p>Defines the stairs traffic pattern.</p>
    """

    traffic_type: Optional[str] = Unassigned()
    phases: Optional[List[Phase]] = Unassigned()
    stairs: Optional[Stairs] = Unassigned()


class RecommendationJobResourceLimit(Base):
    """
    RecommendationJobResourceLimit
         <p>Specifies the maximum number of jobs that can run in parallel and the maximum number of jobs that can run.</p>

        Attributes
       ----------------------
       max_number_of_tests: 	 <p>Defines the maximum number of load tests.</p>
       max_parallel_of_tests: 	 <p>Defines the maximum number of parallel load tests.</p>
    """

    max_number_of_tests: Optional[int] = Unassigned()
    max_parallel_of_tests: Optional[int] = Unassigned()


class EnvironmentParameterRanges(Base):
    """
    EnvironmentParameterRanges
         <p>Specifies the range of environment parameters</p>

        Attributes
       ----------------------
       categorical_parameter_ranges: 	 <p>Specified a list of parameters for each category.</p>
    """

    categorical_parameter_ranges: Optional[List[CategoricalParameter]] = Unassigned()


class EndpointInputConfiguration(Base):
    """
    EndpointInputConfiguration
         <p>The endpoint configuration for the load test.</p>

        Attributes
       ----------------------
       instance_type: 	 <p>The instance types to use for the load test.</p>
       serverless_config
       inference_specification_name: 	 <p>The inference specification name in the model package version.</p>
       environment_parameter_ranges: 	 <p> The parameter you want to benchmark against.</p>
    """

    instance_type: Optional[str] = Unassigned()
    serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()
    inference_specification_name: Optional[str] = Unassigned()
    environment_parameter_ranges: Optional[EnvironmentParameterRanges] = Unassigned()


class RecommendationJobPayloadConfig(Base):
    """
    RecommendationJobPayloadConfig
         <p>The configuration for the payload for a recommendation job.</p>

        Attributes
       ----------------------
       sample_payload_url: 	 <p>The Amazon Simple Storage Service (Amazon S3) path where the sample payload is stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix).</p>
       supported_content_types: 	 <p>The supported MIME types for the input data.</p>
    """

    sample_payload_url: Optional[str] = Unassigned()
    supported_content_types: Optional[List[str]] = Unassigned()


class RecommendationJobContainerConfig(Base):
    """
    RecommendationJobContainerConfig
         <p>Specifies mandatory fields for running an Inference Recommender job directly in the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateInferenceRecommendationsJob.html">CreateInferenceRecommendationsJob</a> API. The fields specified in <code>ContainerConfig</code> override the corresponding fields in the model package. Use <code>ContainerConfig</code> if you want to specify these fields for the recommendation job but don't want to edit them in your model package.</p>

        Attributes
       ----------------------
       domain: 	 <p>The machine learning domain of the model and its components.</p> <p>Valid Values: <code>COMPUTER_VISION | NATURAL_LANGUAGE_PROCESSING | MACHINE_LEARNING</code> </p>
       task: 	 <p>The machine learning task that the model accomplishes.</p> <p>Valid Values: <code>IMAGE_CLASSIFICATION | OBJECT_DETECTION | TEXT_GENERATION | IMAGE_SEGMENTATION | FILL_MASK | CLASSIFICATION | REGRESSION | OTHER</code> </p>
       framework: 	 <p>The machine learning framework of the container image.</p> <p>Valid Values: <code>TENSORFLOW | PYTORCH | XGBOOST | SAGEMAKER-SCIKIT-LEARN</code> </p>
       framework_version: 	 <p>The framework version of the container image.</p>
       payload_config: 	 <p>Specifies the <code>SamplePayloadUrl</code> and all other sample payload-related fields.</p>
       nearest_model_name: 	 <p>The name of a pre-trained machine learning model benchmarked by Amazon SageMaker Inference Recommender that matches your model.</p> <p>Valid Values: <code>efficientnetb7 | unet | xgboost | faster-rcnn-resnet101 | nasnetlarge | vgg16 | inception-v3 | mask-rcnn | sagemaker-scikit-learn | densenet201-gluon | resnet18v2-gluon | xception | densenet201 | yolov4 | resnet152 | bert-base-cased | xceptionV1-keras | resnet50 | retinanet</code> </p>
       supported_instance_types: 	 <p>A list of the instance types that are used to generate inferences in real-time.</p>
       supported_endpoint_type: 	 <p>The endpoint type to receive recommendations for. By default this is null, and the results of the inference recommendation job return a combined list of both real-time and serverless benchmarks. By specifying a value for this field, you can receive a longer list of benchmarks for the desired endpoint type.</p>
       data_input_config: 	 <p>Specifies the name and shape of the expected data inputs for your trained model with a JSON dictionary form. This field is used for optimizing your model using SageMaker Neo. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_InputConfig.html#sagemaker-Type-InputConfig-DataInputConfig">DataInputConfig</a>.</p>
       supported_response_m_i_m_e_types: 	 <p>The supported MIME types for the output data.</p>
    """

    domain: Optional[str] = Unassigned()
    task: Optional[str] = Unassigned()
    framework: Optional[str] = Unassigned()
    framework_version: Optional[str] = Unassigned()
    payload_config: Optional[RecommendationJobPayloadConfig] = Unassigned()
    nearest_model_name: Optional[str] = Unassigned()
    supported_instance_types: Optional[List[str]] = Unassigned()
    supported_endpoint_type: Optional[str] = Unassigned()
    data_input_config: Optional[str] = Unassigned()
    supported_response_m_i_m_e_types: Optional[List[str]] = Unassigned()


class EndpointInfo(Base):
    """
    EndpointInfo
         <p>Details about a customer endpoint that was compared in an Inference Recommender job.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of a customer's endpoint.</p>
    """

    endpoint_name: Optional[str] = Unassigned()


class RecommendationJobVpcConfig(Base):
    """
    RecommendationJobVpcConfig
         <p>Inference Recommender provisions SageMaker endpoints with access to VPC in the inference recommendation job.</p>

        Attributes
       ----------------------
       security_group_ids: 	 <p>The VPC security group IDs. IDs have the form of <code>sg-xxxxxxxx</code>. Specify the security groups for the VPC that is specified in the <code>Subnets</code> field.</p>
       subnets: 	 <p>The ID of the subnets in the VPC to which you want to connect your model.</p>
    """

    security_group_ids: List[str]
    subnets: List[str]


class RecommendationJobInputConfig(Base):
    """
    RecommendationJobInputConfig
         <p>The input configuration of the recommendation job.</p>

        Attributes
       ----------------------
       model_package_version_arn: 	 <p>The Amazon Resource Name (ARN) of a versioned model package.</p>
       model_name: 	 <p>The name of the created model.</p>
       job_duration_in_seconds: 	 <p>Specifies the maximum duration of the job, in seconds. The maximum value is 18,000 seconds.</p>
       traffic_pattern: 	 <p>Specifies the traffic pattern of the job.</p>
       resource_limit: 	 <p>Defines the resource limit of the job.</p>
       endpoint_configurations: 	 <p>Specifies the endpoint configuration to use for a job.</p>
       volume_kms_key_id: 	 <p>The Amazon Resource Name (ARN) of a Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance that hosts the endpoint. This key will be passed to SageMaker Hosting for endpoint creation. </p> <p>The SageMaker execution role must have <code>kms:CreateGrant</code> permission in order to encrypt data on the storage volume of the endpoints created for inference recommendation. The inference recommendation job will fail asynchronously during endpoint configuration creation if the role passed does not have <code>kms:CreateGrant</code> permission.</p> <p>The <code>KmsKeyId</code> can be any of the following formats:</p> <ul> <li> <p>// KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:&lt;region&gt;:&lt;account&gt;:key/&lt;key-id-12ab-34cd-56ef-1234567890ab&gt;"</code> </p> </li> <li> <p>// KMS Key Alias</p> <p> <code>"alias/ExampleAlias"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key Alias</p> <p> <code>"arn:aws:kms:&lt;region&gt;:&lt;account&gt;:alias/&lt;ExampleAlias&gt;"</code> </p> </li> </ul> <p>For more information about key identifiers, see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#key-id-key-id">Key identifiers (KeyID)</a> in the Amazon Web Services Key Management Service (Amazon Web Services KMS) documentation.</p>
       container_config: 	 <p>Specifies mandatory fields for running an Inference Recommender job. The fields specified in <code>ContainerConfig</code> override the corresponding fields in the model package.</p>
       endpoints: 	 <p>Existing customer endpoints on which to run an Inference Recommender job.</p>
       vpc_config: 	 <p>Inference Recommender provisions SageMaker endpoints with access to VPC in the inference recommendation job.</p>
    """

    model_package_version_arn: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    job_duration_in_seconds: Optional[int] = Unassigned()
    traffic_pattern: Optional[TrafficPattern] = Unassigned()
    resource_limit: Optional[RecommendationJobResourceLimit] = Unassigned()
    endpoint_configurations: Optional[List[EndpointInputConfiguration]] = Unassigned()
    volume_kms_key_id: Optional[str] = Unassigned()
    container_config: Optional[RecommendationJobContainerConfig] = Unassigned()
    endpoints: Optional[List[EndpointInfo]] = Unassigned()
    vpc_config: Optional[RecommendationJobVpcConfig] = Unassigned()


class ModelLatencyThreshold(Base):
    """
    ModelLatencyThreshold
         <p>The model latency threshold.</p>

        Attributes
       ----------------------
       percentile: 	 <p>The model latency percentile threshold. Acceptable values are <code>P95</code> and <code>P99</code>. For custom load tests, specify the value as <code>P95</code>.</p>
       value_in_milliseconds: 	 <p>The model latency percentile value in milliseconds.</p>
    """

    percentile: Optional[str] = Unassigned()
    value_in_milliseconds: Optional[int] = Unassigned()


class RecommendationJobStoppingConditions(Base):
    """
    RecommendationJobStoppingConditions
         <p>Specifies conditions for stopping a job. When a job reaches a stopping condition limit, SageMaker ends the job.</p>

        Attributes
       ----------------------
       max_invocations: 	 <p>The maximum number of requests per minute expected for the endpoint.</p>
       model_latency_thresholds: 	 <p>The interval of time taken by a model to respond as viewed from SageMaker. The interval includes the local communication time taken to send the request and to fetch the response from the container of a model and the time taken to complete the inference in the container.</p>
       flat_invocations: 	 <p>Stops a load test when the number of invocations (TPS) peaks and flattens, which means that the instance has reached capacity. The default value is <code>Stop</code>. If you want the load test to continue after invocations have flattened, set the value to <code>Continue</code>.</p>
    """

    max_invocations: Optional[int] = Unassigned()
    model_latency_thresholds: Optional[List[ModelLatencyThreshold]] = Unassigned()
    flat_invocations: Optional[str] = Unassigned()


class RecommendationJobCompiledOutputConfig(Base):
    """
    RecommendationJobCompiledOutputConfig
         <p>Provides information about the output configuration for the compiled model.</p>

        Attributes
       ----------------------
       s3_output_uri: 	 <p>Identifies the Amazon S3 bucket where you want SageMaker to store the compiled model artifacts.</p>
    """

    s3_output_uri: Optional[str] = Unassigned()


class RecommendationJobOutputConfig(Base):
    """
    RecommendationJobOutputConfig
         <p>Provides information about the output configuration for the compiled model.</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>The Amazon Resource Name (ARN) of a Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt your output artifacts with Amazon S3 server-side encryption. The SageMaker execution role must have <code>kms:GenerateDataKey</code> permission.</p> <p>The <code>KmsKeyId</code> can be any of the following formats:</p> <ul> <li> <p>// KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:&lt;region&gt;:&lt;account&gt;:key/&lt;key-id-12ab-34cd-56ef-1234567890ab&gt;"</code> </p> </li> <li> <p>// KMS Key Alias</p> <p> <code>"alias/ExampleAlias"</code> </p> </li> <li> <p>// Amazon Resource Name (ARN) of a KMS Key Alias</p> <p> <code>"arn:aws:kms:&lt;region&gt;:&lt;account&gt;:alias/&lt;ExampleAlias&gt;"</code> </p> </li> </ul> <p>For more information about key identifiers, see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#key-id-key-id">Key identifiers (KeyID)</a> in the Amazon Web Services Key Management Service (Amazon Web Services KMS) documentation.</p>
       compiled_output_config: 	 <p>Provides information about the output configuration for the compiled model.</p>
    """

    kms_key_id: Optional[str] = Unassigned()
    compiled_output_config: Optional[RecommendationJobCompiledOutputConfig] = (
        Unassigned()
    )


class LabelingJobS3DataSource(Base):
    """
    LabelingJobS3DataSource
         <p>The Amazon S3 location of the input data objects.</p>

        Attributes
       ----------------------
       manifest_s3_uri: 	 <p>The Amazon S3 location of the manifest file that describes the input data objects. </p> <p>The input manifest file referenced in <code>ManifestS3Uri</code> must contain one of the following keys: <code>source-ref</code> or <code>source</code>. The value of the keys are interpreted as follows:</p> <ul> <li> <p> <code>source-ref</code>: The source of the object is the Amazon S3 object specified in the value. Use this value when the object is a binary object, such as an image.</p> </li> <li> <p> <code>source</code>: The source of the object is the value. Use this value when the object is a text value.</p> </li> </ul> <p>If you are a new user of Ground Truth, it is recommended you review <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-input-data-input-manifest.html">Use an Input Manifest File </a> in the Amazon SageMaker Developer Guide to learn how to create an input manifest file.</p>
    """

    manifest_s3_uri: str


class LabelingJobSnsDataSource(Base):
    """
    LabelingJobSnsDataSource
         <p>An Amazon SNS data source used for streaming labeling jobs.</p>

        Attributes
       ----------------------
       sns_topic_arn: 	 <p>The Amazon SNS input topic Amazon Resource Name (ARN). Specify the ARN of the input topic you will use to send new data objects to a streaming labeling job.</p>
    """

    sns_topic_arn: str


class LabelingJobDataSource(Base):
    """
    LabelingJobDataSource
         <p>Provides information about the location of input data.</p> <p>You must specify at least one of the following: <code>S3DataSource</code> or <code>SnsDataSource</code>.</p> <p>Use <code>SnsDataSource</code> to specify an SNS input topic for a streaming labeling job. If you do not specify and SNS input topic ARN, Ground Truth will create a one-time labeling job.</p> <p>Use <code>S3DataSource</code> to specify an input manifest file for both streaming and one-time labeling jobs. Adding an <code>S3DataSource</code> is optional if you use <code>SnsDataSource</code> to create a streaming labeling job.</p>

        Attributes
       ----------------------
       s3_data_source: 	 <p>The Amazon S3 location of the input data objects.</p>
       sns_data_source: 	 <p>An Amazon SNS data source used for streaming labeling jobs. To learn more, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-streaming-labeling-job.html#sms-streaming-how-it-works-send-data">Send Data to a Streaming Labeling Job</a>. </p>
    """

    s3_data_source: Optional[LabelingJobS3DataSource] = Unassigned()
    sns_data_source: Optional[LabelingJobSnsDataSource] = Unassigned()


class LabelingJobDataAttributes(Base):
    """
    LabelingJobDataAttributes
         <p>Attributes of the data specified by the customer. Use these to describe the data to be labeled.</p>

        Attributes
       ----------------------
       content_classifiers: 	 <p>Declares that your content is free of personally identifiable information or adult content. SageMaker may restrict the Amazon Mechanical Turk workers that can view your task based on this information.</p>
    """

    content_classifiers: Optional[List[str]] = Unassigned()


class LabelingJobInputConfig(Base):
    """
    LabelingJobInputConfig
         <p>Input configuration information for a labeling job.</p>

        Attributes
       ----------------------
       data_source: 	 <p>The location of the input data.</p>
       data_attributes: 	 <p>Attributes of the data specified by the customer.</p>
    """

    data_source: LabelingJobDataSource
    data_attributes: Optional[LabelingJobDataAttributes] = Unassigned()


class LabelingJobOutputConfig(Base):
    """
    LabelingJobOutputConfig
         <p>Output configuration information for a labeling job.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>The Amazon S3 location to write output data.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service ID of the key used to encrypt the output data, if any.</p> <p>If you provide your own KMS key ID, you must add the required permissions to your KMS key described in <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-security-permission.html#sms-security-kms-permissions">Encrypt Output Data and Storage Volume with Amazon Web Services KMS</a>.</p> <p>If you don't provide a KMS key ID, Amazon SageMaker uses the default Amazon Web Services KMS key for Amazon S3 for your role's account to encrypt your output data.</p> <p>If you use a bucket policy with an <code>s3:PutObject</code> permission that only allows objects with server-side encryption, set the condition key of <code>s3:x-amz-server-side-encryption</code> to <code>"aws:kms"</code>. For more information, see <a href="https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingKMSEncryption.html">KMS-Managed Encryption Keys</a> in the <i>Amazon Simple Storage Service Developer Guide.</i> </p>
       sns_topic_arn: 	 <p>An Amazon Simple Notification Service (Amazon SNS) output topic ARN. Provide a <code>SnsTopicArn</code> if you want to do real time chaining to another streaming job and receive an Amazon SNS notifications each time a data object is submitted by a worker.</p> <p>If you provide an <code>SnsTopicArn</code> in <code>OutputConfig</code>, when workers complete labeling tasks, Ground Truth will send labeling task output data to the SNS output topic you specify here. </p> <p>To learn more, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-streaming-labeling-job.html#sms-streaming-how-it-works-output-data">Receive Output Data from a Streaming Labeling Job</a>. </p>
    """

    s3_output_path: str
    kms_key_id: Optional[str] = Unassigned()
    sns_topic_arn: Optional[str] = Unassigned()


class LabelingJobStoppingConditions(Base):
    """
    LabelingJobStoppingConditions
         <p>A set of conditions for stopping a labeling job. If any of the conditions are met, the job is automatically stopped. You can use these conditions to control the cost of data labeling.</p> <note> <p>Labeling jobs fail after 30 days with an appropriate client error message.</p> </note>

        Attributes
       ----------------------
       max_human_labeled_object_count: 	 <p>The maximum number of objects that can be labeled by human workers.</p>
       max_percentage_of_input_dataset_labeled: 	 <p>The maximum number of input data objects that should be labeled.</p>
    """

    max_human_labeled_object_count: Optional[int] = Unassigned()
    max_percentage_of_input_dataset_labeled: Optional[int] = Unassigned()


class LabelingJobResourceConfig(Base):
    """
    LabelingJobResourceConfig
         <p>Configure encryption on the storage volume attached to the ML compute instance used to run automated data labeling model training and inference. </p>

        Attributes
       ----------------------
       volume_kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s) that run the training and inference jobs used for automated data labeling. </p> <p>You can only specify a <code>VolumeKmsKeyId</code> when you create a labeling job with automated data labeling enabled using the API operation <code>CreateLabelingJob</code>. You cannot specify an Amazon Web Services KMS key to encrypt the storage volume used for automated data labeling model training and inference when you create a labeling job using the console. To learn more, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-security.html">Output Data and Storage Volume Encryption</a>.</p> <p>The <code>VolumeKmsKeyId</code> can be any of the following formats:</p> <ul> <li> <p>KMS Key ID</p> <p> <code>"1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> <li> <p>Amazon Resource Name (ARN) of a KMS Key</p> <p> <code>"arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"</code> </p> </li> </ul>
       vpc_config
    """

    volume_kms_key_id: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


class LabelingJobAlgorithmsConfig(Base):
    """
    LabelingJobAlgorithmsConfig
         <p>Provides configuration information for auto-labeling of your data objects. A <code>LabelingJobAlgorithmsConfig</code> object must be supplied in order to use auto-labeling.</p>

        Attributes
       ----------------------
       labeling_job_algorithm_specification_arn: 	 <p>Specifies the Amazon Resource Name (ARN) of the algorithm used for auto-labeling. You must select one of the following ARNs:</p> <ul> <li> <p> <i>Image classification</i> </p> <p> <code>arn:aws:sagemaker:<i>region</i>:027400017018:labeling-job-algorithm-specification/image-classification</code> </p> </li> <li> <p> <i>Text classification</i> </p> <p> <code>arn:aws:sagemaker:<i>region</i>:027400017018:labeling-job-algorithm-specification/text-classification</code> </p> </li> <li> <p> <i>Object detection</i> </p> <p> <code>arn:aws:sagemaker:<i>region</i>:027400017018:labeling-job-algorithm-specification/object-detection</code> </p> </li> <li> <p> <i>Semantic Segmentation</i> </p> <p> <code>arn:aws:sagemaker:<i>region</i>:027400017018:labeling-job-algorithm-specification/semantic-segmentation</code> </p> </li> </ul>
       initial_active_learning_model_arn: 	 <p>At the end of an auto-label job Ground Truth sends the Amazon Resource Name (ARN) of the final model used for auto-labeling. You can use this model as the starting point for subsequent similar jobs by providing the ARN of the model here. </p>
       labeling_job_resource_config: 	 <p>Provides configuration information for a labeling job.</p>
    """

    labeling_job_algorithm_specification_arn: str
    initial_active_learning_model_arn: Optional[str] = Unassigned()
    labeling_job_resource_config: Optional[LabelingJobResourceConfig] = Unassigned()


class UiConfig(Base):
    """
    UiConfig
         <p>Provided configuration information for the worker UI for a labeling job. Provide either <code>HumanTaskUiArn</code> or <code>UiTemplateS3Uri</code>.</p> <p>For named entity recognition, 3D point cloud and video frame labeling jobs, use <code>HumanTaskUiArn</code>.</p> <p>For all other Ground Truth built-in task types and custom task types, use <code>UiTemplateS3Uri</code> to specify the location of a worker task template in Amazon S3.</p>

        Attributes
       ----------------------
       ui_template_s3_uri: 	 <p>The Amazon S3 bucket location of the UI template, or worker task template. This is the template used to render the worker UI and tools for labeling job tasks. For more information about the contents of a UI template, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-custom-templates-step2.html"> Creating Your Custom Labeling Task Template</a>.</p>
       human_task_ui_arn: 	 <p>The ARN of the worker task template used to render the worker UI and tools for labeling job tasks.</p> <p>Use this parameter when you are creating a labeling job for named entity recognition, 3D point cloud and video frame labeling jobs. Use your labeling job task type to select one of the following ARNs and use it with this parameter when you create a labeling job. Replace <code>aws-region</code> with the Amazon Web Services Region you are creating your labeling job in. For example, replace <code>aws-region</code> with <code>us-west-1</code> if you create a labeling job in US West (N. California).</p> <p> <b>Named Entity Recognition</b> </p> <p>Use the following <code>HumanTaskUiArn</code> for named entity recognition labeling jobs:</p> <p> <code>arn:aws:sagemaker:aws-region:394669845002:human-task-ui/NamedEntityRecognition</code> </p> <p> <b>3D Point Cloud HumanTaskUiArns</b> </p> <p>Use this <code>HumanTaskUiArn</code> for 3D point cloud object detection and 3D point cloud object detection adjustment labeling jobs. </p> <ul> <li> <p> <code>arn:aws:sagemaker:aws-region:394669845002:human-task-ui/PointCloudObjectDetection</code> </p> </li> </ul> <p> Use this <code>HumanTaskUiArn</code> for 3D point cloud object tracking and 3D point cloud object tracking adjustment labeling jobs. </p> <ul> <li> <p> <code>arn:aws:sagemaker:aws-region:394669845002:human-task-ui/PointCloudObjectTracking</code> </p> </li> </ul> <p> Use this <code>HumanTaskUiArn</code> for 3D point cloud semantic segmentation and 3D point cloud semantic segmentation adjustment labeling jobs.</p> <ul> <li> <p> <code>arn:aws:sagemaker:aws-region:394669845002:human-task-ui/PointCloudSemanticSegmentation</code> </p> </li> </ul> <p> <b>Video Frame HumanTaskUiArns</b> </p> <p>Use this <code>HumanTaskUiArn</code> for video frame object detection and video frame object detection adjustment labeling jobs. </p> <ul> <li> <p> <code>arn:aws:sagemaker:region:394669845002:human-task-ui/VideoObjectDetection</code> </p> </li> </ul> <p> Use this <code>HumanTaskUiArn</code> for video frame object tracking and video frame object tracking adjustment labeling jobs. </p> <ul> <li> <p> <code>arn:aws:sagemaker:aws-region:394669845002:human-task-ui/VideoObjectTracking</code> </p> </li> </ul>
    """

    ui_template_s3_uri: Optional[str] = Unassigned()
    human_task_ui_arn: Optional[str] = Unassigned()


class HumanTaskConfig(Base):
    """
    HumanTaskConfig
         <p>Information required for human workers to complete a labeling task.</p>

        Attributes
       ----------------------
       workteam_arn: 	 <p>The Amazon Resource Name (ARN) of the work team assigned to complete the tasks.</p>
       ui_config: 	 <p>Information about the user interface that workers use to complete the labeling task.</p>
       pre_human_task_lambda_arn: 	 <p>The Amazon Resource Name (ARN) of a Lambda function that is run before a data object is sent to a human worker. Use this function to provide input to a custom labeling job.</p> <p>For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-task-types.html">built-in task types</a>, use one of the following Amazon SageMaker Ground Truth Lambda function ARNs for <code>PreHumanTaskLambdaArn</code>. For custom labeling workflows, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-custom-templates-step3.html#sms-custom-templates-step3-prelambda">Pre-annotation Lambda</a>. </p> <p> <b>Bounding box</b> - Finds the most similar boxes from different workers based on the Jaccard index of the boxes.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-BoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-BoundingBox</code> </p> </li> </ul> <p> <b>Image classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of an image based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-ImageMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-ImageMultiClass</code> </p> </li> </ul> <p> <b>Multi-label image classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true classes of an image based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-ImageMultiClassMultiLabel</code> </p> </li> </ul> <p> <b>Semantic segmentation</b> - Treats each pixel in an image as a multi-class classification and treats pixel annotations from workers as "votes" for the correct label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-SemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-SemanticSegmentation</code> </p> </li> </ul> <p> <b>Text classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of text based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-TextMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-TextMultiClass</code> </p> </li> </ul> <p> <b>Multi-label text classification</b> - Uses a variant of the Expectation Maximization approach to estimate the true classes of text based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-TextMultiClassMultiLabel</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-TextMultiClassMultiLabel</code> </p> </li> </ul> <p> <b>Named entity recognition</b> - Groups similar selections and calculates aggregate boundaries, resolving to most-assigned label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-NamedEntityRecognition</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-NamedEntityRecognition</code> </p> </li> </ul> <p> <b>Video Classification</b> - Use this task type when you need workers to classify videos using predefined labels that you specify. Workers are shown videos and are asked to choose one label for each video.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-VideoMultiClass</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-VideoMultiClass</code> </p> </li> </ul> <p> <b>Video Frame Object Detection</b> - Use this task type to have workers identify and locate objects in a sequence of video frames (images extracted from a video) using bounding boxes. For example, you can use this task to ask workers to identify and localize various objects in a series of video frames, such as cars, bikes, and pedestrians.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-VideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-VideoObjectDetection</code> </p> </li> </ul> <p> <b>Video Frame Object Tracking</b> - Use this task type to have workers track the movement of objects in a sequence of video frames (images extracted from a video) using bounding boxes. For example, you can use this task to ask workers to track the movement of objects, such as cars, bikes, and pedestrians. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-VideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-VideoObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Modalities</b> </p> <p>Use the following pre-annotation lambdas for 3D point cloud labeling modality tasks. See <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-point-cloud-task-types.html">3D Point Cloud Task types </a> to learn more. </p> <p> <b>3D Point Cloud Object Detection</b> - Use this task type when you want workers to classify objects in a 3D point cloud by drawing 3D cuboids around objects. For example, you can use this task type to ask workers to identify different types of objects in a point cloud, such as cars, bikes, and pedestrians.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-3DPointCloudObjectDetection</code> </p> </li> </ul> <p> <b>3D Point Cloud Object Tracking</b> - Use this task type when you want workers to draw 3D cuboids around objects that appear in a sequence of 3D point cloud frames. For example, you can use this task type to ask workers to track the movement of vehicles across multiple point cloud frames. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-3DPointCloudObjectTracking</code> </p> </li> </ul> <p> <b>3D Point Cloud Semantic Segmentation</b> - Use this task type when you want workers to create a point-level semantic segmentation masks by painting objects in a 3D point cloud using different colors where each color is assigned to one of the classes you specify.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-3DPointCloudSemanticSegmentation</code> </p> </li> </ul> <p> <b>Use the following ARNs for Label Verification and Adjustment Jobs</b> </p> <p>Use label verification and adjustment jobs to review and adjust labels. To learn more, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-verification-data.html">Verify and Adjust Labels </a>.</p> <p> <b>Bounding box verification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of verification judgement for bounding box labels based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-VerificationBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-VerificationBoundingBox</code> </p> </li> </ul> <p> <b>Bounding box adjustment</b> - Finds the most similar boxes from different workers based on the Jaccard index of the adjusted annotations.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-AdjustmentBoundingBox</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-AdjustmentBoundingBox</code> </p> </li> </ul> <p> <b>Semantic segmentation verification</b> - Uses a variant of the Expectation Maximization approach to estimate the true class of verification judgment for semantic segmentation labels based on annotations from individual workers.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-VerificationSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-VerificationSemanticSegmentation</code> </p> </li> </ul> <p> <b>Semantic segmentation adjustment</b> - Treats each pixel in an image as a multi-class classification and treats pixel adjusted annotations from workers as "votes" for the correct label.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-AdjustmentSemanticSegmentation</code> </p> </li> </ul> <p> <b>Video Frame Object Detection Adjustment</b> - Use this task type when you want workers to adjust bounding boxes that workers have added to video frames to classify and localize objects in a sequence of video frames.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-AdjustmentVideoObjectDetection</code> </p> </li> </ul> <p> <b>Video Frame Object Tracking Adjustment</b> - Use this task type when you want workers to adjust bounding boxes that workers have added to video frames to track object movement across a sequence of video frames.</p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-AdjustmentVideoObjectTracking</code> </p> </li> </ul> <p> <b>3D point cloud object detection adjustment</b> - Adjust 3D cuboids in a point cloud frame. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-Adjustment3DPointCloudObjectDetection</code> </p> </li> </ul> <p> <b>3D point cloud object tracking adjustment</b> - Adjust 3D cuboids across a sequence of point cloud frames. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-Adjustment3DPointCloudObjectTracking</code> </p> </li> </ul> <p> <b>3D point cloud semantic segmentation adjustment</b> - Adjust semantic segmentation masks in a 3D point cloud. </p> <ul> <li> <p> <code>arn:aws:lambda:us-east-1:432418664414:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-east-2:266458841044:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:us-west-2:081040173940:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-1:568282634449:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-1:477331159723:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-2:454466003867:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-south-1:565803892007:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-central-1:203001061592:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-northeast-2:845288260483:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:eu-west-2:487402164563:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ap-southeast-1:377565633583:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> <li> <p> <code>arn:aws:lambda:ca-central-1:918755190332:function:PRE-Adjustment3DPointCloudSemanticSegmentation</code> </p> </li> </ul>
       task_keywords: 	 <p>Keywords used to describe the task so that workers on Amazon Mechanical Turk can discover the task.</p>
       task_title: 	 <p>A title for the task for your human workers.</p>
       task_description: 	 <p>A description of the task for your human workers.</p>
       number_of_human_workers_per_data_object: 	 <p>The number of human workers that will label an object. </p>
       task_time_limit_in_seconds: 	 <p>The amount of time that a worker has to complete a task. </p> <p>If you create a custom labeling job, the maximum value for this parameter is 8 hours (28,800 seconds).</p> <p>If you create a labeling job using a <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-task-types.html">built-in task type</a> the maximum for this parameter depends on the task type you use:</p> <ul> <li> <p>For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-label-images.html">image</a> and <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-label-text.html">text</a> labeling jobs, the maximum is 8 hours (28,800 seconds).</p> </li> <li> <p>For <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-point-cloud.html">3D point cloud</a> and <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-video.html">video frame</a> labeling jobs, the maximum is 30 days (2952,000 seconds) for non-AL mode. For most users, the maximum is also 30 days.</p> </li> </ul>
       task_availability_lifetime_in_seconds: 	 <p>The length of time that a task remains available for labeling by human workers. The default and maximum values for this parameter depend on the type of workforce you use.</p> <ul> <li> <p>If you choose the Amazon Mechanical Turk workforce, the maximum is 12 hours (43,200 seconds). The default is 6 hours (21,600 seconds).</p> </li> <li> <p>If you choose a private or vendor workforce, the default value is 30 days (2592,000 seconds) for non-AL mode. For most users, the maximum is also 30 days.</p> </li> </ul>
       max_concurrent_task_count: 	 <p>Defines the maximum number of data objects that can be labeled by human workers at the same time. Also referred to as batch size. Each object may have more than one worker at one time. The default value is 1000 objects. To increase the maximum value to 5000 objects, contact Amazon Web Services Support.</p>
       annotation_consolidation_config: 	 <p>Configures how labels are consolidated across human workers.</p>
       public_workforce_task_price: 	 <p>The price that you pay for each task performed by an Amazon Mechanical Turk worker.</p>
    """

    workteam_arn: str
    ui_config: UiConfig
    pre_human_task_lambda_arn: str
    task_title: str
    task_description: str
    number_of_human_workers_per_data_object: int
    task_time_limit_in_seconds: int
    annotation_consolidation_config: AnnotationConsolidationConfig
    task_keywords: Optional[List[str]] = Unassigned()
    task_availability_lifetime_in_seconds: Optional[int] = Unassigned()
    max_concurrent_task_count: Optional[int] = Unassigned()
    public_workforce_task_price: Optional[PublicWorkforceTaskPrice] = Unassigned()


class ModelBiasBaselineConfig(Base):
    """
    ModelBiasBaselineConfig
         <p>The configuration for a baseline model bias job.</p>

        Attributes
       ----------------------
       baselining_job_name: 	 <p>The name of the baseline model bias job.</p>
       constraints_resource
    """

    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


class ModelBiasAppSpecification(Base):
    """
    ModelBiasAppSpecification
         <p>Docker container image configuration object for the model bias job.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The container image to be run by the model bias job.</p>
       config_uri: 	 <p>JSON formatted S3 file that defines bias parameters. For more information on this JSON configuration file, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-config-json-monitor-bias-parameters.html">Configure bias parameters</a>.</p>
       environment: 	 <p>Sets the environment variables in the Docker container.</p>
    """

    image_uri: str
    config_uri: str
    environment: Optional[Dict[str, str]] = Unassigned()


class MonitoringGroundTruthS3Input(Base):
    """
    MonitoringGroundTruthS3Input
         <p>The ground truth labels for the dataset used for the monitoring job.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The address of the Amazon S3 location of the ground truth labels.</p>
    """

    s3_uri: Optional[str] = Unassigned()


class ModelBiasJobInput(Base):
    """
    ModelBiasJobInput
         <p>Inputs for the model bias job.</p>

        Attributes
       ----------------------
       endpoint_input
       batch_transform_input: 	 <p>Input object for the batch transform job.</p>
       ground_truth_s3_input: 	 <p>Location of ground truth labels to use in model bias job.</p>
    """

    ground_truth_s3_input: MonitoringGroundTruthS3Input
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class ModelCardExportOutputConfig(Base):
    """
    ModelCardExportOutputConfig
         <p>Configure the export output details for an Amazon SageMaker Model Card.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>The Amazon S3 output path to export your model card PDF.</p>
    """

    s3_output_path: str


class ModelCardSecurityConfig(Base):
    """
    ModelCardSecurityConfig
         <p>Configure the security settings to protect model card data.</p>

        Attributes
       ----------------------
       kms_key_id: 	 <p>A Key Management Service <a href="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#key-id-key-id">key ID</a> to use for encrypting a model card.</p>
    """

    kms_key_id: Optional[str] = Unassigned()


class ModelExplainabilityBaselineConfig(Base):
    """
    ModelExplainabilityBaselineConfig
         <p>The configuration for a baseline model explainability job.</p>

        Attributes
       ----------------------
       baselining_job_name: 	 <p>The name of the baseline model explainability job.</p>
       constraints_resource
    """

    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


class ModelExplainabilityAppSpecification(Base):
    """
    ModelExplainabilityAppSpecification
         <p>Docker container image configuration object for the model explainability job.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The container image to be run by the model explainability job.</p>
       config_uri: 	 <p>JSON formatted Amazon S3 file that defines explainability parameters. For more information on this JSON configuration file, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/clarify-config-json-monitor-model-explainability-parameters.html">Configure model explainability parameters</a>.</p>
       environment: 	 <p>Sets the environment variables in the Docker container.</p>
    """

    image_uri: str
    config_uri: str
    environment: Optional[Dict[str, str]] = Unassigned()


class ModelExplainabilityJobInput(Base):
    """
    ModelExplainabilityJobInput
         <p>Inputs for the model explainability job.</p>

        Attributes
       ----------------------
       endpoint_input
       batch_transform_input: 	 <p>Input object for the batch transform job.</p>
    """

    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class InferenceExecutionConfig(Base):
    """
    InferenceExecutionConfig
         <p>Specifies details about how containers in a multi-container endpoint are run.</p>

        Attributes
       ----------------------
       mode: 	 <p>How containers in a multi-container are run. The following values are valid.</p> <ul> <li> <p> <code>SERIAL</code> - Containers run as a serial pipeline.</p> </li> <li> <p> <code>DIRECT</code> - Only the individual container that you specify is run.</p> </li> </ul>
    """

    mode: str


class ModelPackageValidationProfile(Base):
    """
    ModelPackageValidationProfile
         <p>Contains data, such as the inputs and targeted instance types that are used in the process of validating the model package.</p> <p>The data provided in the validation profile is made available to your buyers on Amazon Web Services Marketplace.</p>

        Attributes
       ----------------------
       profile_name: 	 <p>The name of the profile for the model package.</p>
       transform_job_definition: 	 <p>The <code>TransformJobDefinition</code> object that describes the transform job used for the validation of the model package.</p>
    """

    profile_name: str
    transform_job_definition: TransformJobDefinition


class ModelPackageValidationSpecification(Base):
    """
    ModelPackageValidationSpecification
         <p>Specifies batch transform jobs that SageMaker runs to validate your model package.</p>

        Attributes
       ----------------------
       validation_role: 	 <p>The IAM roles to be used for the validation of the model package.</p>
       validation_profiles: 	 <p>An array of <code>ModelPackageValidationProfile</code> objects, each of which specifies a batch transform job that SageMaker runs to validate your model package.</p>
    """

    validation_role: str
    validation_profiles: List[ModelPackageValidationProfile]


class SourceAlgorithm(Base):
    """
    SourceAlgorithm
         <p>Specifies an algorithm that was used to create the model package. The algorithm must be either an algorithm resource in your SageMaker account or an algorithm in Amazon Web Services Marketplace that you are subscribed to.</p>

        Attributes
       ----------------------
       model_data_url: 	 <p>The Amazon S3 path where the model artifacts, which result from model training, are stored. This path must point to a single <code>gzip</code> compressed tar archive (<code>.tar.gz</code> suffix).</p> <note> <p>The model artifacts must be in an S3 bucket that is in the same Amazon Web Services region as the algorithm.</p> </note>
       model_data_source: 	 <p>Specifies the location of ML model data to deploy during endpoint creation.</p>
       algorithm_name: 	 <p>The name of an algorithm that was used to create the model package. The algorithm must be either an algorithm resource in your SageMaker account or an algorithm in Amazon Web Services Marketplace that you are subscribed to.</p>
    """

    algorithm_name: str
    model_data_url: Optional[str] = Unassigned()
    model_data_source: Optional[ModelDataSource] = Unassigned()


class SourceAlgorithmSpecification(Base):
    """
    SourceAlgorithmSpecification
         <p>A list of algorithms that were used to create a model package.</p>

        Attributes
       ----------------------
       source_algorithms: 	 <p>A list of the algorithms that were used to create a model package.</p>
    """

    source_algorithms: List[SourceAlgorithm]


class ModelQuality(Base):
    """
    ModelQuality
         <p>Model quality statistics and constraints.</p>

        Attributes
       ----------------------
       statistics: 	 <p>Model quality statistics.</p>
       constraints: 	 <p>Model quality constraints.</p>
    """

    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


class ModelDataQuality(Base):
    """
    ModelDataQuality
         <p>Data quality constraints and statistics for a model.</p>

        Attributes
       ----------------------
       statistics: 	 <p>Data quality statistics for a model.</p>
       constraints: 	 <p>Data quality constraints for a model.</p>
    """

    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


class Explainability(Base):
    """
    Explainability
         <p>Contains explainability metrics for a model.</p>

        Attributes
       ----------------------
       report: 	 <p>The explainability report for a model.</p>
    """

    report: Optional[MetricsSource] = Unassigned()


class ModelMetrics(Base):
    """
    ModelMetrics
         <p>Contains metrics captured from a model.</p>

        Attributes
       ----------------------
       model_quality: 	 <p>Metrics that measure the quality of a model.</p>
       model_data_quality: 	 <p>Metrics that measure the quality of the input data for a model.</p>
       bias: 	 <p>Metrics that measure bias in a model.</p>
       explainability: 	 <p>Metrics that help explain a model.</p>
    """

    model_quality: Optional[ModelQuality] = Unassigned()
    model_data_quality: Optional[ModelDataQuality] = Unassigned()
    bias: Optional[Bias] = Unassigned()
    explainability: Optional[Explainability] = Unassigned()


class FileSource(Base):
    """
    FileSource
         <p>Contains details regarding the file source.</p>

        Attributes
       ----------------------
       content_type: 	 <p>The type of content stored in the file source.</p>
       content_digest: 	 <p>The digest of the file source.</p>
       s3_uri: 	 <p>The Amazon S3 URI for the file source.</p>
    """

    s3_uri: str
    content_type: Optional[str] = Unassigned()
    content_digest: Optional[str] = Unassigned()


class DriftCheckBias(Base):
    """
    DriftCheckBias
         <p>Represents the drift check bias baselines that can be used when the model monitor is set using the model package.</p>

        Attributes
       ----------------------
       config_file: 	 <p>The bias config file for a model.</p>
       pre_training_constraints: 	 <p>The pre-training constraints.</p>
       post_training_constraints: 	 <p>The post-training constraints.</p>
    """

    config_file: Optional[FileSource] = Unassigned()
    pre_training_constraints: Optional[MetricsSource] = Unassigned()
    post_training_constraints: Optional[MetricsSource] = Unassigned()


class DriftCheckExplainability(Base):
    """
    DriftCheckExplainability
         <p>Represents the drift check explainability baselines that can be used when the model monitor is set using the model package. </p>

        Attributes
       ----------------------
       constraints: 	 <p>The drift check explainability constraints.</p>
       config_file: 	 <p>The explainability config file for the model.</p>
    """

    constraints: Optional[MetricsSource] = Unassigned()
    config_file: Optional[FileSource] = Unassigned()


class DriftCheckModelQuality(Base):
    """
    DriftCheckModelQuality
         <p>Represents the drift check model quality baselines that can be used when the model monitor is set using the model package. </p>

        Attributes
       ----------------------
       statistics: 	 <p>The drift check model quality statistics.</p>
       constraints: 	 <p>The drift check model quality constraints.</p>
    """

    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


class DriftCheckModelDataQuality(Base):
    """
    DriftCheckModelDataQuality
         <p>Represents the drift check data quality baselines that can be used when the model monitor is set using the model package. </p>

        Attributes
       ----------------------
       statistics: 	 <p>The drift check model data quality statistics.</p>
       constraints: 	 <p>The drift check model data quality constraints.</p>
    """

    statistics: Optional[MetricsSource] = Unassigned()
    constraints: Optional[MetricsSource] = Unassigned()


class DriftCheckBaselines(Base):
    """
    DriftCheckBaselines
         <p>Represents the drift check baselines that can be used when the model monitor is set using the model package. </p>

        Attributes
       ----------------------
       bias: 	 <p>Represents the drift check bias baselines that can be used when the model monitor is set using the model package. </p>
       explainability: 	 <p>Represents the drift check explainability baselines that can be used when the model monitor is set using the model package. </p>
       model_quality: 	 <p>Represents the drift check model quality baselines that can be used when the model monitor is set using the model package.</p>
       model_data_quality: 	 <p>Represents the drift check model data quality baselines that can be used when the model monitor is set using the model package.</p>
    """

    bias: Optional[DriftCheckBias] = Unassigned()
    explainability: Optional[DriftCheckExplainability] = Unassigned()
    model_quality: Optional[DriftCheckModelQuality] = Unassigned()
    model_data_quality: Optional[DriftCheckModelDataQuality] = Unassigned()


class ModelQualityBaselineConfig(Base):
    """
    ModelQualityBaselineConfig
         <p>Configuration for monitoring constraints and monitoring statistics. These baseline resources are compared against the results of the current job from the series of jobs scheduled to collect data periodically.</p>

        Attributes
       ----------------------
       baselining_job_name: 	 <p>The name of the job that performs baselining for the monitoring job.</p>
       constraints_resource
    """

    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()


class ModelQualityAppSpecification(Base):
    """
    ModelQualityAppSpecification
         <p>Container image configuration object for the monitoring job.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The address of the container image that the monitoring job runs.</p>
       container_entrypoint: 	 <p>Specifies the entrypoint for a container that the monitoring job runs.</p>
       container_arguments: 	 <p>An array of arguments for the container used to run the monitoring job.</p>
       record_preprocessor_source_uri: 	 <p>An Amazon S3 URI to a script that is called per row prior to running analysis. It can base64 decode the payload and convert it into a flattened JSON so that the built-in container can use the converted data. Applicable only for the built-in (first party) containers.</p>
       post_analytics_processor_source_uri: 	 <p>An Amazon S3 URI to a script that is called after analysis has been performed. Applicable only for the built-in (first party) containers.</p>
       problem_type: 	 <p>The machine learning problem type of the model that the monitoring job monitors.</p>
       environment: 	 <p>Sets the environment variables in the container that the monitoring job runs.</p>
    """

    image_uri: str
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_arguments: Optional[List[str]] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class ModelQualityJobInput(Base):
    """
    ModelQualityJobInput
         <p>The input for the model quality monitoring job. Currently endpoints are supported for input for model quality monitoring jobs.</p>

        Attributes
       ----------------------
       endpoint_input
       batch_transform_input: 	 <p>Input object for the batch transform job.</p>
       ground_truth_s3_input: 	 <p>The ground truth label provided for the model.</p>
    """

    ground_truth_s3_input: MonitoringGroundTruthS3Input
    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class ScheduleConfig(Base):
    """
    ScheduleConfig
         <p>Configuration details about the monitoring schedule.</p>

        Attributes
       ----------------------
       schedule_expression: 	 <p>A cron expression that describes details about the monitoring schedule.</p> <p>The supported cron expressions are:</p> <ul> <li> <p>If you want to set the job to start every hour, use the following:</p> <p> <code>Hourly: cron(0 * ? * * *)</code> </p> </li> <li> <p>If you want to start the job daily:</p> <p> <code>cron(0 [00-23] ? * * *)</code> </p> </li> <li> <p>If you want to run the job one time, immediately, use the following keyword:</p> <p> <code>NOW</code> </p> </li> </ul> <p>For example, the following are valid cron expressions:</p> <ul> <li> <p>Daily at noon UTC: <code>cron(0 12 ? * * *)</code> </p> </li> <li> <p>Daily at midnight UTC: <code>cron(0 0 ? * * *)</code> </p> </li> </ul> <p>To support running every 6, 12 hours, the following are also supported:</p> <p> <code>cron(0 [00-23]/[01-24] ? * * *)</code> </p> <p>For example, the following are valid cron expressions:</p> <ul> <li> <p>Every 12 hours, starting at 5pm UTC: <code>cron(0 17/12 ? * * *)</code> </p> </li> <li> <p>Every two hours starting at midnight: <code>cron(0 0/2 ? * * *)</code> </p> </li> </ul> <note> <ul> <li> <p>Even though the cron expression is set to start at 5PM UTC, note that there could be a delay of 0-20 minutes from the actual requested time to run the execution. </p> </li> <li> <p>We recommend that if you would like a daily schedule, you do not provide this parameter. Amazon SageMaker will pick a time for running every day.</p> </li> </ul> </note> <p>You can also specify the keyword <code>NOW</code> to run the monitoring job immediately, one time, without recurring.</p>
       data_analysis_start_time: 	 <p>Sets the start time for a monitoring job window. Express this time as an offset to the times that you schedule your monitoring jobs to run. You schedule monitoring jobs with the <code>ScheduleExpression</code> parameter. Specify this offset in ISO 8601 duration format. For example, if you want to monitor the five hours of data in your dataset that precede the start of each monitoring job, you would specify: <code>"-PT5H"</code>.</p> <p>The start time that you specify must not precede the end time that you specify by more than 24 hours. You specify the end time with the <code>DataAnalysisEndTime</code> parameter.</p> <p>If you set <code>ScheduleExpression</code> to <code>NOW</code>, this parameter is required.</p>
       data_analysis_end_time: 	 <p>Sets the end time for a monitoring job window. Express this time as an offset to the times that you schedule your monitoring jobs to run. You schedule monitoring jobs with the <code>ScheduleExpression</code> parameter. Specify this offset in ISO 8601 duration format. For example, if you want to end the window one hour before the start of each monitoring job, you would specify: <code>"-PT1H"</code>.</p> <p>The end time that you specify must not follow the start time that you specify by more than 24 hours. You specify the start time with the <code>DataAnalysisStartTime</code> parameter.</p> <p>If you set <code>ScheduleExpression</code> to <code>NOW</code>, this parameter is required.</p>
    """

    schedule_expression: str
    data_analysis_start_time: Optional[str] = Unassigned()
    data_analysis_end_time: Optional[str] = Unassigned()


class MonitoringBaselineConfig(Base):
    """
    MonitoringBaselineConfig
         <p>Configuration for monitoring constraints and monitoring statistics. These baseline resources are compared against the results of the current job from the series of jobs scheduled to collect data periodically.</p>

        Attributes
       ----------------------
       baselining_job_name: 	 <p>The name of the job that performs baselining for the monitoring job.</p>
       constraints_resource: 	 <p>The baseline constraint file in Amazon S3 that the current monitoring job should validated against.</p>
       statistics_resource: 	 <p>The baseline statistics file in Amazon S3 that the current monitoring job should be validated against.</p>
    """

    baselining_job_name: Optional[str] = Unassigned()
    constraints_resource: Optional[MonitoringConstraintsResource] = Unassigned()
    statistics_resource: Optional[MonitoringStatisticsResource] = Unassigned()


class MonitoringInput(Base):
    """
    MonitoringInput
         <p>The inputs for a monitoring job.</p>

        Attributes
       ----------------------
       endpoint_input: 	 <p>The endpoint for a monitoring job.</p>
       batch_transform_input: 	 <p>Input object for the batch transform job.</p>
    """

    endpoint_input: Optional[EndpointInput] = Unassigned()
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class MonitoringAppSpecification(Base):
    """
    MonitoringAppSpecification
         <p>Container image configuration object for the monitoring job.</p>

        Attributes
       ----------------------
       image_uri: 	 <p>The container image to be run by the monitoring job.</p>
       container_entrypoint: 	 <p>Specifies the entrypoint for a container used to run the monitoring job.</p>
       container_arguments: 	 <p>An array of arguments for the container used to run the monitoring job.</p>
       record_preprocessor_source_uri: 	 <p>An Amazon S3 URI to a script that is called per row prior to running analysis. It can base64 decode the payload and convert it into a flattened JSON so that the built-in container can use the converted data. Applicable only for the built-in (first party) containers.</p>
       post_analytics_processor_source_uri: 	 <p>An Amazon S3 URI to a script that is called after analysis has been performed. Applicable only for the built-in (first party) containers.</p>
    """

    image_uri: str
    container_entrypoint: Optional[List[str]] = Unassigned()
    container_arguments: Optional[List[str]] = Unassigned()
    record_preprocessor_source_uri: Optional[str] = Unassigned()
    post_analytics_processor_source_uri: Optional[str] = Unassigned()


class NetworkConfig(Base):
    """
    NetworkConfig
         <p>Networking options for a job, such as network traffic encryption between containers, whether to allow inbound and outbound network calls to and from containers, and the VPC subnets and security groups to use for VPC-enabled jobs.</p>

        Attributes
       ----------------------
       enable_inter_container_traffic_encryption: 	 <p>Whether to encrypt all communications between distributed processing jobs. Choose <code>True</code> to encrypt communications. Encryption provides greater security for distributed processing jobs, but the processing might take longer.</p>
       enable_network_isolation: 	 <p>Whether to allow inbound and outbound network calls to and from the containers used for the processing job.</p>
       vpc_config
    """

    enable_inter_container_traffic_encryption: Optional[bool] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()


class MonitoringJobDefinition(Base):
    """
    MonitoringJobDefinition
         <p>Defines the monitoring job.</p>

        Attributes
       ----------------------
       baseline_config: 	 <p>Baseline configuration used to validate that the data conforms to the specified constraints and statistics</p>
       monitoring_inputs: 	 <p>The array of inputs for the monitoring job. Currently we support monitoring an Amazon SageMaker Endpoint.</p>
       monitoring_output_config: 	 <p>The array of outputs from the monitoring job to be uploaded to Amazon S3.</p>
       monitoring_resources: 	 <p>Identifies the resources, ML compute instances, and ML storage volumes to deploy for a monitoring job. In distributed processing, you specify more than one instance.</p>
       monitoring_app_specification: 	 <p>Configures the monitoring job to run a specified Docker container image.</p>
       stopping_condition: 	 <p>Specifies a time limit for how long the monitoring job is allowed to run.</p>
       environment: 	 <p>Sets the environment variables in the Docker container.</p>
       network_config: 	 <p>Specifies networking options for an monitoring job.</p>
       role_arn: 	 <p>The Amazon Resource Name (ARN) of an IAM role that Amazon SageMaker can assume to perform tasks on your behalf.</p>
    """

    monitoring_inputs: List[MonitoringInput]
    monitoring_output_config: MonitoringOutputConfig
    monitoring_resources: MonitoringResources
    monitoring_app_specification: MonitoringAppSpecification
    role_arn: str
    baseline_config: Optional[MonitoringBaselineConfig] = Unassigned()
    stopping_condition: Optional[MonitoringStoppingCondition] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    network_config: Optional[NetworkConfig] = Unassigned()


class MonitoringScheduleConfig(Base):
    """
    MonitoringScheduleConfig
         <p>Configures the monitoring schedule and defines the monitoring job.</p>

        Attributes
       ----------------------
       schedule_config: 	 <p>Configures the monitoring schedule.</p>
       monitoring_job_definition: 	 <p>Defines the monitoring job.</p>
       monitoring_job_definition_name: 	 <p>The name of the monitoring job definition to schedule.</p>
       monitoring_type: 	 <p>The type of the monitoring job definition to schedule.</p>
    """

    schedule_config: Optional[ScheduleConfig] = Unassigned()
    monitoring_job_definition: Optional[MonitoringJobDefinition] = Unassigned()
    monitoring_job_definition_name: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()


class InstanceMetadataServiceConfiguration(Base):
    """
    InstanceMetadataServiceConfiguration
         <p>Information on the IMDS configuration of the notebook instance</p>

        Attributes
       ----------------------
       minimum_instance_metadata_service_version: 	 <p>Indicates the minimum IMDS version that the notebook instance supports. When passed as part of <code>CreateNotebookInstance</code>, if no value is selected, then it defaults to IMDSv1. This means that both IMDSv1 and IMDSv2 are supported. If passed as part of <code>UpdateNotebookInstance</code>, there is no default.</p>
    """

    minimum_instance_metadata_service_version: str


class NotebookInstanceLifecycleHook(Base):
    """
    NotebookInstanceLifecycleHook
         <p>Contains the notebook instance lifecycle configuration script.</p> <p>Each lifecycle configuration script has a limit of 16384 characters.</p> <p>The value of the <code>$PATH</code> environment variable that is available to both scripts is <code>/sbin:bin:/usr/sbin:/usr/bin</code>.</p> <p>View Amazon CloudWatch Logs for notebook instance lifecycle configurations in log group <code>/aws/sagemaker/NotebookInstances</code> in log stream <code>[notebook-instance-name]/[LifecycleConfigHook]</code>.</p> <p>Lifecycle configuration scripts cannot run for longer than 5 minutes. If a script runs for longer than 5 minutes, it fails and the notebook instance is not created or started.</p> <p>For information about notebook instance lifestyle configurations, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-lifecycle-config.html">Step 2.1: (Optional) Customize a Notebook Instance</a>.</p>

        Attributes
       ----------------------
       content: 	 <p>A base64-encoded string that contains a shell script for a notebook instance lifecycle configuration.</p>
    """

    content: Optional[str] = Unassigned()


class PipelineDefinitionS3Location(Base):
    """
    PipelineDefinitionS3Location
         <p>The location of the pipeline definition stored in Amazon S3.</p>

        Attributes
       ----------------------
       bucket: 	 <p>Name of the S3 bucket.</p>
       object_key: 	 <p>The object key (or key name) uniquely identifies the object in an S3 bucket. </p>
       version_id: 	 <p>Version Id of the pipeline definition file. If not specified, Amazon SageMaker will retrieve the latest version.</p>
    """

    bucket: str
    object_key: str
    version_id: Optional[str] = Unassigned()


class ParallelismConfiguration(Base):
    """
    ParallelismConfiguration
         <p>Configuration that controls the parallelism of the pipeline. By default, the parallelism configuration specified applies to all executions of the pipeline unless overridden.</p>

        Attributes
       ----------------------
       max_parallel_execution_steps: 	 <p>The max number of steps that can be executed in parallel. </p>
    """

    max_parallel_execution_steps: int


class ProcessingS3Input(Base):
    """
    ProcessingS3Input
         <p>Configuration for downloading input data from Amazon S3 into the processing container.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>The URI of the Amazon S3 prefix Amazon SageMaker downloads data required to run a processing job.</p>
       local_path: 	 <p>The local path in your container where you want Amazon SageMaker to write input data to. <code>LocalPath</code> is an absolute path to the input data and must begin with <code>/opt/ml/processing/</code>. <code>LocalPath</code> is a required parameter when <code>AppManaged</code> is <code>False</code> (default).</p>
       s3_data_type: 	 <p>Whether you use an <code>S3Prefix</code> or a <code>ManifestFile</code> for the data type. If you choose <code>S3Prefix</code>, <code>S3Uri</code> identifies a key name prefix. Amazon SageMaker uses all objects with the specified key name prefix for the processing job. If you choose <code>ManifestFile</code>, <code>S3Uri</code> identifies an object that is a manifest file containing a list of object keys that you want Amazon SageMaker to use for the processing job.</p>
       s3_input_mode: 	 <p>Whether to use <code>File</code> or <code>Pipe</code> input mode. In File mode, Amazon SageMaker copies the data from the input source onto the local ML storage volume before starting your processing container. This is the most commonly used input mode. In <code>Pipe</code> mode, Amazon SageMaker streams input data from the source directly to your processing container into named pipes without using the ML storage volume.</p>
       s3_data_distribution_type: 	 <p>Whether to distribute the data from Amazon S3 to all processing instances with <code>FullyReplicated</code>, or whether the data from Amazon S3 is shared by Amazon S3 key, downloading one shard of data to each processing instance.</p>
       s3_compression_type: 	 <p>Whether to GZIP-decompress the data in Amazon S3 as it is streamed into the processing container. <code>Gzip</code> can only be used when <code>Pipe</code> mode is specified as the <code>S3InputMode</code>. In <code>Pipe</code> mode, Amazon SageMaker streams input data from the source directly to your container without using the EBS volume.</p>
    """

    s3_uri: str
    s3_data_type: str
    local_path: Optional[str] = Unassigned()
    s3_input_mode: Optional[str] = Unassigned()
    s3_data_distribution_type: Optional[str] = Unassigned()
    s3_compression_type: Optional[str] = Unassigned()


class RedshiftDatasetDefinition(Base):
    """
    RedshiftDatasetDefinition
         <p>Configuration for Redshift Dataset Definition input.</p>

        Attributes
       ----------------------
       cluster_id
       database
       db_user
       query_string
       cluster_role_arn: 	 <p>The IAM role attached to your Redshift cluster that Amazon SageMaker uses to generate datasets.</p>
       output_s3_uri: 	 <p>The location in Amazon S3 where the Redshift query results are stored.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data from a Redshift execution.</p>
       output_format
       output_compression
    """

    cluster_id: str
    database: str
    db_user: str
    query_string: str
    cluster_role_arn: str
    output_s3_uri: str
    output_format: str
    kms_key_id: Optional[str] = Unassigned()
    output_compression: Optional[str] = Unassigned()


class DatasetDefinition(Base):
    """
    DatasetDefinition
         <p>Configuration for Dataset Definition inputs. The Dataset Definition input must specify exactly one of either <code>AthenaDatasetDefinition</code> or <code>RedshiftDatasetDefinition</code> types.</p>

        Attributes
       ----------------------
       athena_dataset_definition
       redshift_dataset_definition
       local_path: 	 <p>The local path where you want Amazon SageMaker to download the Dataset Definition inputs to run a processing job. <code>LocalPath</code> is an absolute path to the input data. This is a required parameter when <code>AppManaged</code> is <code>False</code> (default).</p>
       data_distribution_type: 	 <p>Whether the generated dataset is <code>FullyReplicated</code> or <code>ShardedByS3Key</code> (default).</p>
       input_mode: 	 <p>Whether to use <code>File</code> or <code>Pipe</code> input mode. In <code>File</code> (default) mode, Amazon SageMaker copies the data from the input source onto the local Amazon Elastic Block Store (Amazon EBS) volumes before starting your training algorithm. This is the most commonly used input mode. In <code>Pipe</code> mode, Amazon SageMaker streams input data from the source directly to your algorithm without using the EBS volume.</p>
    """

    athena_dataset_definition: Optional[AthenaDatasetDefinition] = Unassigned()
    redshift_dataset_definition: Optional[RedshiftDatasetDefinition] = Unassigned()
    local_path: Optional[str] = Unassigned()
    data_distribution_type: Optional[str] = Unassigned()
    input_mode: Optional[str] = Unassigned()


class ProcessingInput(Base):
    """
    ProcessingInput
         <p>The inputs for a processing job. The processing input must specify exactly one of either <code>S3Input</code> or <code>DatasetDefinition</code> types.</p>

        Attributes
       ----------------------
       input_name: 	 <p>The name for the processing job input.</p>
       app_managed: 	 <p>When <code>True</code>, input operations such as data download are managed natively by the processing job application. When <code>False</code> (default), input operations are managed by Amazon SageMaker.</p>
       s3_input: 	 <p>Configuration for downloading input data from Amazon S3 into the processing container.</p>
       dataset_definition: 	 <p>Configuration for a Dataset Definition input. </p>
    """

    input_name: str
    app_managed: Optional[bool] = Unassigned()
    s3_input: Optional[ProcessingS3Input] = Unassigned()
    dataset_definition: Optional[DatasetDefinition] = Unassigned()


class ProcessingS3Output(Base):
    """
    ProcessingS3Output
         <p>Configuration for uploading output data to Amazon S3 from the processing container.</p>

        Attributes
       ----------------------
       s3_uri: 	 <p>A URI that identifies the Amazon S3 bucket where you want Amazon SageMaker to save the results of a processing job.</p>
       local_path: 	 <p>The local path of a directory where you want Amazon SageMaker to upload its contents to Amazon S3. <code>LocalPath</code> is an absolute path to a directory containing output files. This directory will be created by the platform and exist when your container's entrypoint is invoked.</p>
       s3_upload_mode: 	 <p>Whether to upload the results of the processing job continuously or after the job completes.</p>
    """

    s3_uri: str
    local_path: str
    s3_upload_mode: str


class ProcessingFeatureStoreOutput(Base):
    """
    ProcessingFeatureStoreOutput
         <p>Configuration for processing job outputs in Amazon SageMaker Feature Store.</p>

        Attributes
       ----------------------
       feature_group_name: 	 <p>The name of the Amazon SageMaker FeatureGroup to use as the destination for processing job output. Note that your processing script is responsible for putting records into your Feature Store.</p>
    """

    feature_group_name: str


class ProcessingOutput(Base):
    """
    ProcessingOutput
         <p>Describes the results of a processing job. The processing output must specify exactly one of either <code>S3Output</code> or <code>FeatureStoreOutput</code> types.</p>

        Attributes
       ----------------------
       output_name: 	 <p>The name for the processing job output.</p>
       s3_output: 	 <p>Configuration for processing job outputs in Amazon S3.</p>
       feature_store_output: 	 <p>Configuration for processing job outputs in Amazon SageMaker Feature Store. This processing output type is only supported when <code>AppManaged</code> is specified. </p>
       app_managed: 	 <p>When <code>True</code>, output operations such as data upload are managed natively by the processing job application. When <code>False</code> (default), output operations are managed by Amazon SageMaker.</p>
    """

    output_name: str
    s3_output: Optional[ProcessingS3Output] = Unassigned()
    feature_store_output: Optional[ProcessingFeatureStoreOutput] = Unassigned()
    app_managed: Optional[bool] = Unassigned()


class ProcessingOutputConfig(Base):
    """
    ProcessingOutputConfig
         <p>Configuration for uploading output from the processing container.</p>

        Attributes
       ----------------------
       outputs: 	 <p>An array of outputs configuring the data to upload from the processing container.</p>
       kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt the processing job output. <code>KmsKeyId</code> can be an ID of a KMS key, ARN of a KMS key, alias of a KMS key, or alias of a KMS key. The <code>KmsKeyId</code> is applied to all outputs.</p>
    """

    outputs: List[ProcessingOutput]
    kms_key_id: Optional[str] = Unassigned()


class ProcessingClusterConfig(Base):
    """
    ProcessingClusterConfig
         <p>Configuration for the cluster used to run a processing job.</p>

        Attributes
       ----------------------
       instance_count: 	 <p>The number of ML compute instances to use in the processing job. For distributed processing jobs, specify a value greater than 1. The default value is 1.</p>
       instance_type: 	 <p>The ML compute instance type for the processing job.</p>
       volume_size_in_g_b: 	 <p>The size of the ML storage volume in gigabytes that you want to provision. You must specify sufficient ML storage for your scenario.</p> <note> <p>Certain Nitro-based instances include local storage with a fixed total size, dependent on the instance type. When using these instances for processing, Amazon SageMaker mounts the local instance storage instead of Amazon EBS gp2 storage. You can't request a <code>VolumeSizeInGB</code> greater than the total size of the local instance storage.</p> <p>For a list of instance types that support local instance storage, including the total size per instance type, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html#instance-store-volumes">Instance Store Volumes</a>.</p> </note>
       volume_kms_key_id: 	 <p>The Amazon Web Services Key Management Service (Amazon Web Services KMS) key that Amazon SageMaker uses to encrypt data on the storage volume attached to the ML compute instance(s) that run the processing job. </p> <note> <p>Certain Nitro-based instances include local storage, dependent on the instance type. Local storage volumes are encrypted using a hardware module on the instance. You can't request a <code>VolumeKmsKeyId</code> when using an instance type with local storage.</p> <p>For a list of instance types that support local instance storage, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/InstanceStorage.html#instance-store-volumes">Instance Store Volumes</a>.</p> <p>For more information about local instance storage encryption, see <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html">SSD Instance Store Volumes</a>.</p> </note>
    """

    instance_count: int
    instance_type: str
    volume_size_in_g_b: int
    volume_kms_key_id: Optional[str] = Unassigned()


class ProcessingResources(Base):
    """
    ProcessingResources
         <p>Identifies the resources, ML compute instances, and ML storage volumes to deploy for a processing job. In distributed training, you specify more than one instance.</p>

        Attributes
       ----------------------
       cluster_config: 	 <p>The configuration for the resources in a cluster used to run the processing job.</p>
    """

    cluster_config: ProcessingClusterConfig


class ProcessingStoppingCondition(Base):
    """
    ProcessingStoppingCondition
         <p>Configures conditions under which the processing job should be stopped, such as how long the processing job has been running. After the condition is met, the processing job is stopped.</p>

        Attributes
       ----------------------
       max_runtime_in_seconds: 	 <p>Specifies the maximum runtime in seconds.</p>
    """

    max_runtime_in_seconds: int


class ExperimentConfig(Base):
    """
    ExperimentConfig
         <p>Associates a SageMaker job as a trial component with an experiment and trial. Specified when you call the following APIs:</p> <ul> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateProcessingJob.html">CreateProcessingJob</a> </p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html">CreateTrainingJob</a> </p> </li> <li> <p> <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTransformJob.html">CreateTransformJob</a> </p> </li> </ul>

        Attributes
       ----------------------
       experiment_name: 	 <p>The name of an existing experiment to associate with the trial component.</p>
       trial_name: 	 <p>The name of an existing trial to associate the trial component with. If not specified, a new trial is created.</p>
       trial_component_display_name: 	 <p>The display name for the trial component. If this key isn't specified, the display name is the trial component name.</p>
       run_name: 	 <p>The name of the experiment run to associate with the trial component.</p>
    """

    experiment_name: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()
    trial_component_display_name: Optional[str] = Unassigned()
    run_name: Optional[str] = Unassigned()


class ProvisioningParameter(Base):
    """
    ProvisioningParameter
         <p>A key value pair used when you provision a project as a service catalog product. For information, see <a href="https://docs.aws.amazon.com/servicecatalog/latest/adminguide/introduction.html">What is Amazon Web Services Service Catalog</a>.</p>

        Attributes
       ----------------------
       key: 	 <p>The key that identifies a provisioning parameter.</p>
       value: 	 <p>The value of the provisioning parameter.</p>
    """

    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


class ServiceCatalogProvisioningDetails(Base):
    """
    ServiceCatalogProvisioningDetails
         <p>Details that you specify to provision a service catalog product. For information about service catalog, see <a href="https://docs.aws.amazon.com/servicecatalog/latest/adminguide/introduction.html">What is Amazon Web Services Service Catalog</a>.</p>

        Attributes
       ----------------------
       product_id: 	 <p>The ID of the product to provision.</p>
       provisioning_artifact_id: 	 <p>The ID of the provisioning artifact.</p>
       path_id: 	 <p>The path identifier of the product. This value is optional if the product has a default path, and required if the product has more than one path. </p>
       provisioning_parameters: 	 <p>A list of key value pairs that you specify when you provision a product.</p>
    """

    product_id: str
    provisioning_artifact_id: Optional[str] = Unassigned()
    path_id: Optional[str] = Unassigned()
    provisioning_parameters: Optional[List[ProvisioningParameter]] = Unassigned()


class SpaceCodeEditorAppSettings(Base):
    """
    SpaceCodeEditorAppSettings
         <p>The application settings for a Code Editor space.</p>

        Attributes
       ----------------------
       default_resource_spec
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()


class SpaceJupyterLabAppSettings(Base):
    """
    SpaceJupyterLabAppSettings
         <p>The settings for the JupyterLab application within a space.</p>

        Attributes
       ----------------------
       default_resource_spec
       code_repositories: 	 <p>A list of Git repositories that SageMaker automatically displays to users for cloning in the JupyterLab application.</p>
    """

    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    code_repositories: Optional[List[CodeRepository]] = Unassigned()


class EbsStorageSettings(Base):
    """
    EbsStorageSettings
         <p>A collection of EBS storage settings that applies to private spaces.</p>

        Attributes
       ----------------------
       ebs_volume_size_in_gb: 	 <p>The size of an EBS storage volume for a private space.</p>
    """

    ebs_volume_size_in_gb: int


class SpaceStorageSettings(Base):
    """
    SpaceStorageSettings
         <p>The storage settings for a private space.</p>

        Attributes
       ----------------------
       ebs_storage_settings: 	 <p>A collection of EBS storage settings for a private space.</p>
    """

    ebs_storage_settings: Optional[EbsStorageSettings] = Unassigned()


class EFSFileSystem(Base):
    """
    EFSFileSystem
         <p>A file system, created by you in Amazon EFS, that you assign to a user profile or space for an Amazon SageMaker Domain. Permitted users can access this file system in Amazon SageMaker Studio.</p>

        Attributes
       ----------------------
       file_system_id: 	 <p>The ID of your Amazon EFS file system.</p>
    """

    file_system_id: str


class CustomFileSystem(Base):
    """
    CustomFileSystem
         <p>A file system, created by you, that you assign to a user profile or space for an Amazon SageMaker Domain. Permitted users can access this file system in Amazon SageMaker Studio.</p>

        Attributes
       ----------------------
       e_f_s_file_system: 	 <p>A custom file system in Amazon EFS.</p>
    """

    e_f_s_file_system: Optional[EFSFileSystem] = Unassigned()


class SpaceSettings(Base):
    """
    SpaceSettings
         <p>A collection of space settings.</p>

        Attributes
       ----------------------
       jupyter_server_app_settings
       kernel_gateway_app_settings
       code_editor_app_settings: 	 <p>The Code Editor application settings.</p>
       jupyter_lab_app_settings: 	 <p>The settings for the JupyterLab application.</p>
       app_type: 	 <p>The type of app created within the space.</p>
       space_storage_settings: 	 <p>The storage settings for a private space.</p>
       custom_file_systems: 	 <p>A file system, created by you, that you assign to a space for an Amazon SageMaker Domain. Permitted users can access this file system in Amazon SageMaker Studio.</p>
    """

    jupyter_server_app_settings: Optional[JupyterServerAppSettings] = Unassigned()
    kernel_gateway_app_settings: Optional[KernelGatewayAppSettings] = Unassigned()
    code_editor_app_settings: Optional[SpaceCodeEditorAppSettings] = Unassigned()
    jupyter_lab_app_settings: Optional[SpaceJupyterLabAppSettings] = Unassigned()
    app_type: Optional[str] = Unassigned()
    space_storage_settings: Optional[SpaceStorageSettings] = Unassigned()
    custom_file_systems: Optional[List[CustomFileSystem]] = Unassigned()


class OwnershipSettings(Base):
    """
    OwnershipSettings
         <p>The collection of ownership settings for a space.</p>

        Attributes
       ----------------------
       owner_user_profile_name: 	 <p>The user profile who is the owner of the private space.</p>
    """

    owner_user_profile_name: str


class SpaceSharingSettings(Base):
    """
    SpaceSharingSettings
         <p>A collection of space sharing settings.</p>

        Attributes
       ----------------------
       sharing_type: 	 <p>Specifies the sharing type of the space.</p>
    """

    sharing_type: str


class DebugHookConfig(Base):
    """
    DebugHookConfig
         <p>Configuration information for the Amazon SageMaker Debugger hook parameters, metric and tensor collections, and storage paths. To learn more about how to configure the <code>DebugHookConfig</code> parameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/debugger-createtrainingjob-api.html">Use the SageMaker and Debugger Configuration API Operations to Create, Update, and Debug Your Training Job</a>.</p>

        Attributes
       ----------------------
       local_path: 	 <p>Path to local storage location for metrics and tensors. Defaults to <code>/opt/ml/output/tensors/</code>.</p>
       s3_output_path: 	 <p>Path to Amazon S3 storage location for metrics and tensors.</p>
       hook_parameters: 	 <p>Configuration information for the Amazon SageMaker Debugger hook parameters.</p>
       collection_configurations: 	 <p>Configuration information for Amazon SageMaker Debugger tensor collections. To learn more about how to configure the <code>CollectionConfiguration</code> parameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/debugger-createtrainingjob-api.html">Use the SageMaker and Debugger Configuration API Operations to Create, Update, and Debug Your Training Job</a>. </p>
    """

    s3_output_path: str
    local_path: Optional[str] = Unassigned()
    hook_parameters: Optional[Dict[str, str]] = Unassigned()
    collection_configurations: Optional[List[CollectionConfiguration]] = Unassigned()


class DebugRuleConfiguration(Base):
    """
    DebugRuleConfiguration
         <p>Configuration information for SageMaker Debugger rules for debugging. To learn more about how to configure the <code>DebugRuleConfiguration</code> parameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/debugger-createtrainingjob-api.html">Use the SageMaker and Debugger Configuration API Operations to Create, Update, and Debug Your Training Job</a>.</p>

        Attributes
       ----------------------
       rule_configuration_name: 	 <p>The name of the rule configuration. It must be unique relative to other rule configuration names.</p>
       local_path: 	 <p>Path to local storage location for output of rules. Defaults to <code>/opt/ml/processing/output/rule/</code>.</p>
       s3_output_path: 	 <p>Path to Amazon S3 storage location for rules.</p>
       rule_evaluator_image: 	 <p>The Amazon Elastic Container (ECR) Image for the managed rule evaluation.</p>
       instance_type: 	 <p>The instance type to deploy a custom rule for debugging a training job.</p>
       volume_size_in_g_b: 	 <p>The size, in GB, of the ML storage volume attached to the processing instance.</p>
       rule_parameters: 	 <p>Runtime configuration for rule container.</p>
    """

    rule_configuration_name: str
    rule_evaluator_image: str
    local_path: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    rule_parameters: Optional[Dict[str, str]] = Unassigned()


class TensorBoardOutputConfig(Base):
    """
    TensorBoardOutputConfig
         <p>Configuration of storage locations for the Amazon SageMaker Debugger TensorBoard output data.</p>

        Attributes
       ----------------------
       local_path: 	 <p>Path to local storage location for tensorBoard output. Defaults to <code>/opt/ml/output/tensorboard</code>.</p>
       s3_output_path: 	 <p>Path to Amazon S3 storage location for TensorBoard output.</p>
    """

    s3_output_path: str
    local_path: Optional[str] = Unassigned()


class ProfilerConfig(Base):
    """
    ProfilerConfig
         <p>Configuration information for Amazon SageMaker Debugger system monitoring, framework profiling, and storage paths.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>Path to Amazon S3 storage location for system and framework metrics.</p>
       profiling_interval_in_milliseconds: 	 <p>A time interval for capturing system metrics in milliseconds. Available values are 100, 200, 500, 1000 (1 second), 5000 (5 seconds), and 60000 (1 minute) milliseconds. The default value is 500 milliseconds.</p>
       profiling_parameters: 	 <p>Configuration information for capturing framework metrics. Available key strings for different profiling options are <code>DetailedProfilingConfig</code>, <code>PythonProfilingConfig</code>, and <code>DataLoaderProfilingConfig</code>. The following codes are configuration structures for the <code>ProfilingParameters</code> parameter. To learn more about how to configure the <code>ProfilingParameters</code> parameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/debugger-createtrainingjob-api.html">Use the SageMaker and Debugger Configuration API Operations to Create, Update, and Debug Your Training Job</a>. </p>
       disable_profiler: 	 <p>Configuration to turn off Amazon SageMaker Debugger's system monitoring and profiling functionality. To turn it off, set to <code>True</code>.</p>
    """

    s3_output_path: Optional[str] = Unassigned()
    profiling_interval_in_milliseconds: Optional[int] = Unassigned()
    profiling_parameters: Optional[Dict[str, str]] = Unassigned()
    disable_profiler: Optional[bool] = Unassigned()


class ProfilerRuleConfiguration(Base):
    """
    ProfilerRuleConfiguration
         <p>Configuration information for profiling rules.</p>

        Attributes
       ----------------------
       rule_configuration_name: 	 <p>The name of the rule configuration. It must be unique relative to other rule configuration names.</p>
       local_path: 	 <p>Path to local storage location for output of rules. Defaults to <code>/opt/ml/processing/output/rule/</code>. </p>
       s3_output_path: 	 <p>Path to Amazon S3 storage location for rules.</p>
       rule_evaluator_image: 	 <p>The Amazon Elastic Container Registry Image for the managed rule evaluation.</p>
       instance_type: 	 <p>The instance type to deploy a custom rule for profiling a training job.</p>
       volume_size_in_g_b: 	 <p>The size, in GB, of the ML storage volume attached to the processing instance.</p>
       rule_parameters: 	 <p>Runtime configuration for rule container.</p>
    """

    rule_configuration_name: str
    rule_evaluator_image: str
    local_path: Optional[str] = Unassigned()
    s3_output_path: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    volume_size_in_g_b: Optional[int] = Unassigned()
    rule_parameters: Optional[Dict[str, str]] = Unassigned()


class RemoteDebugConfig(Base):
    """
    RemoteDebugConfig
         <p>Configuration for remote debugging for the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html">CreateTrainingJob</a> API. To learn more about the remote debugging functionality of SageMaker, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-remote-debugging.html">Access a training container through Amazon Web Services Systems Manager (SSM) for remote debugging</a>.</p>

        Attributes
       ----------------------
       enable_remote_debug: 	 <p>If set to True, enables remote debugging.</p>
    """

    enable_remote_debug: Optional[bool] = Unassigned()


class InfraCheckConfig(Base):
    """
    InfraCheckConfig
         <p>Configuration information for the infrastructure health check of a training job. A SageMaker-provided health check tests the health of instance hardware and cluster network connectivity.</p>

        Attributes
       ----------------------
       enable_infra_check: 	 <p>Enables an infrastructure health check.</p>
    """

    enable_infra_check: Optional[bool] = Unassigned()


class ModelClientConfig(Base):
    """
    ModelClientConfig
         <p>Configures the timeout and maximum number of retries for processing a transform job invocation.</p>

        Attributes
       ----------------------
       invocations_timeout_in_seconds: 	 <p>The timeout value in seconds for an invocation request. The default value is 600.</p>
       invocations_max_retries: 	 <p>The maximum number of retries when invocation requests are failing. The default value is 3.</p>
    """

    invocations_timeout_in_seconds: Optional[int] = Unassigned()
    invocations_max_retries: Optional[int] = Unassigned()


class DataProcessing(Base):
    """
    DataProcessing
         <p>The data structure used to specify the data to be used for inference in a batch transform job and to associate the data that is relevant to the prediction results in the output. The input filter provided allows you to exclude input data that is not needed for inference in a batch transform job. The output filter provided allows you to include input data relevant to interpreting the predictions in the output from the job. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform-data-processing.html">Associate Prediction Results with their Corresponding Input Records</a>.</p>

        Attributes
       ----------------------
       input_filter: 	 <p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform-data-processing.html#data-processing-operators">JSONPath</a> expression used to select a portion of the input data to pass to the algorithm. Use the <code>InputFilter</code> parameter to exclude fields, such as an ID column, from the input. If you want SageMaker to pass the entire input dataset to the algorithm, accept the default value <code>$</code>.</p> <p>Examples: <code>"$"</code>, <code>"$[1:]"</code>, <code>"$.features"</code> </p>
       output_filter: 	 <p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform-data-processing.html#data-processing-operators">JSONPath</a> expression used to select a portion of the joined dataset to save in the output file for a batch transform job. If you want SageMaker to store the entire input dataset in the output file, leave the default value, <code>$</code>. If you specify indexes that aren't within the dimension size of the joined dataset, you get an error.</p> <p>Examples: <code>"$"</code>, <code>"$[0,5:]"</code>, <code>"$['id','SageMakerOutput']"</code> </p>
       join_source: 	 <p>Specifies the source of the data to join with the transformed data. The valid values are <code>None</code> and <code>Input</code>. The default value is <code>None</code>, which specifies not to join the input with the transformed data. If you want the batch transform job to join the original input data with the transformed data, set <code>JoinSource</code> to <code>Input</code>. You can specify <code>OutputFilter</code> as an additional filter to select a portion of the joined dataset and store it in the output file.</p> <p>For JSON or JSONLines objects, such as a JSON array, SageMaker adds the transformed data to the input JSON object in an attribute called <code>SageMakerOutput</code>. The joined result for JSON must be a key-value pair object. If the input is not a key-value pair object, SageMaker creates a new JSON file. In the new JSON file, and the input data is stored under the <code>SageMakerInput</code> key and the results are stored in <code>SageMakerOutput</code>.</p> <p>For CSV data, SageMaker takes each row as a JSON array and joins the transformed data with the input by appending each transformed row to the end of the input. The joined data has the original input data followed by the transformed data and the output is a CSV file.</p> <p>For information on how joining in applied, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform-data-processing.html#batch-transform-data-processing-workflow">Workflow for Associating Inferences with Input Records</a>.</p>
    """

    input_filter: Optional[str] = Unassigned()
    output_filter: Optional[str] = Unassigned()
    join_source: Optional[str] = Unassigned()


class TrialComponentStatus(Base):
    """
    TrialComponentStatus
         <p>The status of the trial component.</p>

        Attributes
       ----------------------
       primary_status: 	 <p>The status of the trial component.</p>
       message: 	 <p>If the component failed, a message describing why.</p>
    """

    primary_status: Optional[str] = Unassigned()
    message: Optional[str] = Unassigned()


class TrialComponentParameterValue(Base):
    """
    TrialComponentParameterValue
         <p>The value of a hyperparameter. Only one of <code>NumberValue</code> or <code>StringValue</code> can be specified.</p> <p>This object is specified in the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrialComponent.html">CreateTrialComponent</a> request.</p>

        Attributes
       ----------------------
       string_value: 	 <p>The string value of a categorical hyperparameter. If you specify a value for this parameter, you can't specify the <code>NumberValue</code> parameter.</p>
       number_value: 	 <p>The numeric value of a numeric hyperparameter. If you specify a value for this parameter, you can't specify the <code>StringValue</code> parameter.</p>
    """

    string_value: Optional[str] = Unassigned()
    number_value: Optional[float] = Unassigned()


class TrialComponentArtifact(Base):
    """
    TrialComponentArtifact
         <p>Represents an input or output artifact of a trial component. You specify <code>TrialComponentArtifact</code> as part of the <code>InputArtifacts</code> and <code>OutputArtifacts</code> parameters in the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrialComponent.html">CreateTrialComponent</a> request.</p> <p>Examples of input artifacts are datasets, algorithms, hyperparameters, source code, and instance types. Examples of output artifacts are metrics, snapshots, logs, and images.</p>

        Attributes
       ----------------------
       media_type: 	 <p>The media type of the artifact, which indicates the type of data in the artifact file. The media type consists of a <i>type</i> and a <i>subtype</i> concatenated with a slash (/) character, for example, text/csv, image/jpeg, and s3/uri. The type specifies the category of the media. The subtype specifies the kind of data.</p>
       value: 	 <p>The location of the artifact.</p>
    """

    value: str
    media_type: Optional[str] = Unassigned()


class OidcConfig(Base):
    """
    OidcConfig
         <p>Use this parameter to configure your OIDC Identity Provider (IdP).</p>

        Attributes
       ----------------------
       client_id: 	 <p>The OIDC IdP client ID used to configure your private workforce.</p>
       client_secret: 	 <p>The OIDC IdP client secret used to configure your private workforce.</p>
       issuer: 	 <p>The OIDC IdP issuer used to configure your private workforce.</p>
       authorization_endpoint: 	 <p>The OIDC IdP authorization endpoint used to configure your private workforce.</p>
       token_endpoint: 	 <p>The OIDC IdP token endpoint used to configure your private workforce.</p>
       user_info_endpoint: 	 <p>The OIDC IdP user information endpoint used to configure your private workforce.</p>
       logout_endpoint: 	 <p>The OIDC IdP logout endpoint used to configure your private workforce.</p>
       jwks_uri: 	 <p>The OIDC IdP JSON Web Key Set (Jwks) URI used to configure your private workforce.</p>
    """

    client_id: str
    client_secret: str
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    user_info_endpoint: str
    logout_endpoint: str
    jwks_uri: str


class SourceIpConfig(Base):
    """
    SourceIpConfig
         <p>A list of IP address ranges (<a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html">CIDRs</a>). Used to create an allow list of IP addresses for a private workforce. Workers will only be able to login to their worker portal from an IP address within this range. By default, a workforce isn't restricted to specific IP addresses.</p>

        Attributes
       ----------------------
       cidrs: 	 <p>A list of one to ten <a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html">Classless Inter-Domain Routing</a> (CIDR) values.</p> <p>Maximum: Ten CIDR values</p> <note> <p>The following Length Constraints apply to individual CIDR values in the CIDR value list.</p> </note>
    """

    cidrs: List[str]


class WorkforceVpcConfigRequest(Base):
    """
    WorkforceVpcConfigRequest
         <p>The VPC object you use to create or update a workforce.</p>

        Attributes
       ----------------------
       vpc_id: 	 <p>The ID of the VPC that the workforce uses for communication.</p>
       security_group_ids: 	 <p>The VPC security group IDs, in the form sg-xxxxxxxx. The security groups must be for the same VPC as specified in the subnet.</p>
       subnets: 	 <p>The ID of the subnets in the VPC that you want to connect.</p>
    """

    vpc_id: Optional[str] = Unassigned()
    security_group_ids: Optional[List[str]] = Unassigned()
    subnets: Optional[List[str]] = Unassigned()


class OidcMemberDefinition(Base):
    """
    OidcMemberDefinition
         <p>A list of user groups that exist in your OIDC Identity Provider (IdP). One to ten groups can be used to create a single private work team. When you add a user group to the list of <code>Groups</code>, you can add that user group to one or more private work teams. If you add a user group to a private work team, all workers in that user group are added to the work team.</p>

        Attributes
       ----------------------
       groups: 	 <p>A list of comma seperated strings that identifies user groups in your OIDC IdP. Each user group is made up of a group of private workers.</p>
    """

    groups: Optional[List[str]] = Unassigned()


class MemberDefinition(Base):
    """
    MemberDefinition
         <p>Defines an Amazon Cognito or your own OIDC IdP user group that is part of a work team.</p>

        Attributes
       ----------------------
       cognito_member_definition: 	 <p>The Amazon Cognito user group that is part of the work team.</p>
       oidc_member_definition: 	 <p>A list user groups that exist in your OIDC Identity Provider (IdP). One to ten groups can be used to create a single private work team. When you add a user group to the list of <code>Groups</code>, you can add that user group to one or more private work teams. If you add a user group to a private work team, all workers in that user group are added to the work team.</p>
    """

    cognito_member_definition: Optional[CognitoMemberDefinition] = Unassigned()
    oidc_member_definition: Optional[OidcMemberDefinition] = Unassigned()


class NotificationConfiguration(Base):
    """
    NotificationConfiguration
         <p>Configures Amazon SNS notifications of available or expiring work items for work teams.</p>

        Attributes
       ----------------------
       notification_topic_arn: 	 <p>The ARN for the Amazon SNS topic to which notifications should be published.</p>
    """

    notification_topic_arn: Optional[str] = Unassigned()


class CustomizedMetricSpecification(Base):
    """
    CustomizedMetricSpecification
         <p>A customized metric.</p>

        Attributes
       ----------------------
       metric_name: 	 <p>The name of the customized metric.</p>
       namespace: 	 <p>The namespace of the customized metric.</p>
       statistic: 	 <p>The statistic of the customized metric.</p>
    """

    metric_name: Optional[str] = Unassigned()
    namespace: Optional[str] = Unassigned()
    statistic: Optional[str] = Unassigned()


class DataCaptureConfigSummary(Base):
    """
    DataCaptureConfigSummary
         <p>The currently active data capture configuration used by your Endpoint.</p>

        Attributes
       ----------------------
       enable_capture: 	 <p>Whether data capture is enabled or disabled.</p>
       capture_status: 	 <p>Whether data capture is currently functional.</p>
       current_sampling_percentage: 	 <p>The percentage of requests being captured by your Endpoint.</p>
       destination_s3_uri: 	 <p>The Amazon S3 location being used to capture the data.</p>
       kms_key_id: 	 <p>The KMS key being used to encrypt the data in Amazon S3.</p>
    """

    enable_capture: bool
    capture_status: str
    current_sampling_percentage: int
    destination_s3_uri: str
    kms_key_id: str


class DebugRuleEvaluationStatus(Base):
    """
    DebugRuleEvaluationStatus
         <p>Information about the status of the rule evaluation.</p>

        Attributes
       ----------------------
       rule_configuration_name: 	 <p>The name of the rule configuration.</p>
       rule_evaluation_job_arn: 	 <p>The Amazon Resource Name (ARN) of the rule evaluation job.</p>
       rule_evaluation_status: 	 <p>Status of the rule evaluation.</p>
       status_details: 	 <p>Details from the rule evaluation.</p>
       last_modified_time: 	 <p>Timestamp when the rule evaluation status was last modified.</p>
    """

    rule_configuration_name: Optional[str] = Unassigned()
    rule_evaluation_job_arn: Optional[str] = Unassigned()
    rule_evaluation_status: Optional[str] = Unassigned()
    status_details: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class RetentionPolicy(Base):
    """
    RetentionPolicy
         <p>The retention policy for data stored on an Amazon Elastic File System volume.</p>

        Attributes
       ----------------------
       home_efs_file_system: 	 <p>The default is <code>Retain</code>, which specifies to keep the data stored on the Amazon EFS volume.</p> <p>Specify <code>Delete</code> to delete the data stored on the Amazon EFS volume.</p>
    """

    home_efs_file_system: Optional[str] = Unassigned()


class DeployedImage(Base):
    """
    DeployedImage
         <p>Gets the Amazon EC2 Container Registry path of the docker image of the model that is hosted in this <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ProductionVariant.html">ProductionVariant</a>.</p> <p>If you used the <code>registry/repository[:tag]</code> form to specify the image path of the primary container when you created the model hosted in this <code>ProductionVariant</code>, the path resolves to a path of the form <code>registry/repository[@digest]</code>. A digest is a hash value that identifies a specific version of an image. For information about Amazon ECR paths, see <a href="https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-pull-ecr-image.html">Pulling an Image</a> in the <i>Amazon ECR User Guide</i>.</p>

        Attributes
       ----------------------
       specified_image: 	 <p>The image path you specified when you created the model.</p>
       resolved_image: 	 <p>The specific digest path of the image hosted in this <code>ProductionVariant</code>.</p>
       resolution_time: 	 <p>The date and time when the image path for the model resolved to the <code>ResolvedImage</code> </p>
    """

    specified_image: Optional[str] = Unassigned()
    resolved_image: Optional[str] = Unassigned()
    resolution_time: Optional[datetime.datetime] = Unassigned()


class RealTimeInferenceRecommendation(Base):
    """
    RealTimeInferenceRecommendation
         <p>The recommended configuration to use for Real-Time Inference.</p>

        Attributes
       ----------------------
       recommendation_id: 	 <p>The recommendation ID which uniquely identifies each recommendation.</p>
       instance_type: 	 <p>The recommended instance type for Real-Time Inference.</p>
       environment: 	 <p>The recommended environment variables to set in the model container for Real-Time Inference.</p>
    """

    recommendation_id: str
    instance_type: str
    environment: Optional[Dict[str, str]] = Unassigned()


class DeploymentRecommendation(Base):
    """
    DeploymentRecommendation
         <p>A set of recommended deployment configurations for the model. To get more advanced recommendations, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateInferenceRecommendationsJob.html">CreateInferenceRecommendationsJob</a> to create an inference recommendation job.</p>

        Attributes
       ----------------------
       recommendation_status: 	 <p>Status of the deployment recommendation. The status <code>NOT_APPLICABLE</code> means that SageMaker is unable to provide a default recommendation for the model using the information provided. If the deployment status is <code>IN_PROGRESS</code>, retry your API call after a few seconds to get a <code>COMPLETED</code> deployment recommendation.</p>
       real_time_inference_recommendations: 	 <p>A list of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_RealTimeInferenceRecommendation.html">RealTimeInferenceRecommendation</a> items.</p>
    """

    recommendation_status: str
    real_time_inference_recommendations: Optional[
        List[RealTimeInferenceRecommendation]
    ] = Unassigned()


class EdgeDeploymentStatus(Base):
    """
    EdgeDeploymentStatus
         <p>Contains information summarizing the deployment stage results.</p>

        Attributes
       ----------------------
       stage_status: 	 <p>The general status of the current stage.</p>
       edge_deployment_success_in_stage: 	 <p>The number of edge devices with the successful deployment in the current stage.</p>
       edge_deployment_pending_in_stage: 	 <p>The number of edge devices yet to pick up the deployment in current stage, or in progress.</p>
       edge_deployment_failed_in_stage: 	 <p>The number of edge devices that failed the deployment in current stage.</p>
       edge_deployment_status_message: 	 <p>A detailed message about deployment status in current stage.</p>
       edge_deployment_stage_start_time: 	 <p>The time when the deployment API started.</p>
    """

    stage_status: str
    edge_deployment_success_in_stage: int
    edge_deployment_pending_in_stage: int
    edge_deployment_failed_in_stage: int
    edge_deployment_status_message: Optional[str] = Unassigned()
    edge_deployment_stage_start_time: Optional[datetime.datetime] = Unassigned()


class DeploymentStageStatusSummary(Base):
    """
    DeploymentStageStatusSummary
         <p>Contains information summarizing the deployment stage results.</p>

        Attributes
       ----------------------
       stage_name: 	 <p>The name of the stage.</p>
       device_selection_config: 	 <p>Configuration of the devices in the stage.</p>
       deployment_config: 	 <p>Configuration of the deployment details.</p>
       deployment_status: 	 <p>General status of the current state.</p>
    """

    stage_name: str
    device_selection_config: DeviceSelectionConfig
    deployment_config: EdgeDeploymentConfig
    deployment_status: EdgeDeploymentStatus


class DerivedInformation(Base):
    """
    DerivedInformation
         <p>Information that SageMaker Neo automatically derived about the model.</p>

        Attributes
       ----------------------
       derived_data_input_config: 	 <p>The data input configuration that SageMaker Neo automatically derived for the model. When SageMaker Neo derives this information, you don't need to specify the data input configuration when you create a compilation job.</p>
    """

    derived_data_input_config: Optional[str] = Unassigned()


class ResolvedAttributes(Base):
    """
    ResolvedAttributes
         <p>The resolved attributes.</p>

        Attributes
       ----------------------
       auto_m_l_job_objective
       problem_type: 	 <p>The problem type.</p>
       completion_criteria
    """

    auto_m_l_job_objective: Optional[AutoMLJobObjective] = Unassigned()
    problem_type: Optional[str] = Unassigned()
    completion_criteria: Optional[AutoMLJobCompletionCriteria] = Unassigned()


class ModelDeployResult(Base):
    """
    ModelDeployResult
         <p>Provides information about the endpoint of the model deployment.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of the endpoint to which the model has been deployed.</p> <note> <p>If model deployment fails, this field is omitted from the response.</p> </note>
    """

    endpoint_name: Optional[str] = Unassigned()


class ModelArtifacts(Base):
    """
    ModelArtifacts
         <p>Provides information about the location that is configured for storing model artifacts. </p> <p>Model artifacts are outputs that result from training a model. They typically consist of trained parameters, a model definition that describes how to compute inferences, and other metadata. A SageMaker container stores your trained model artifacts in the <code>/opt/ml/model</code> directory. After training has completed, by default, these artifacts are uploaded to your Amazon S3 bucket as compressed files.</p>

        Attributes
       ----------------------
       s3_model_artifacts: 	 <p>The path of the S3 object that contains the model artifacts. For example, <code>s3://bucket-name/keynameprefix/model.tar.gz</code>.</p>
    """

    s3_model_artifacts: str


class ModelDigests(Base):
    """
    ModelDigests
         <p>Provides information to verify the integrity of stored model artifacts. </p>

        Attributes
       ----------------------
       artifact_digest: 	 <p>Provides a hash value that uniquely identifies the stored model artifacts.</p>
    """

    artifact_digest: Optional[str] = Unassigned()


class EdgeModel(Base):
    """
    EdgeModel
         <p>The model on the edge device.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the model.</p>
       model_version: 	 <p>The model version.</p>
       latest_sample_time: 	 <p>The timestamp of the last data sample taken.</p>
       latest_inference: 	 <p>The timestamp of the last inference that was made.</p>
    """

    model_name: str
    model_version: str
    latest_sample_time: Optional[datetime.datetime] = Unassigned()
    latest_inference: Optional[datetime.datetime] = Unassigned()


class EdgePresetDeploymentOutput(Base):
    """
    EdgePresetDeploymentOutput
         <p>The output of a SageMaker Edge Manager deployable resource.</p>

        Attributes
       ----------------------
       type: 	 <p>The deployment type created by SageMaker Edge Manager. Currently only supports Amazon Web Services IoT Greengrass Version 2 components.</p>
       artifact: 	 <p>The Amazon Resource Name (ARN) of the generated deployable resource.</p>
       status: 	 <p>The status of the deployable resource.</p>
       status_message: 	 <p>Returns a message describing the status of the deployed resource.</p>
    """

    type: str
    artifact: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    status_message: Optional[str] = Unassigned()


class ProductionVariantStatus(Base):
    """
    ProductionVariantStatus
         <p>Describes the status of the production variant.</p>

        Attributes
       ----------------------
       status: 	 <p>The endpoint variant status which describes the current deployment stage status or operational status.</p> <ul> <li> <p> <code>Creating</code>: Creating inference resources for the production variant.</p> </li> <li> <p> <code>Deleting</code>: Terminating inference resources for the production variant.</p> </li> <li> <p> <code>Updating</code>: Updating capacity for the production variant.</p> </li> <li> <p> <code>ActivatingTraffic</code>: Turning on traffic for the production variant.</p> </li> <li> <p> <code>Baking</code>: Waiting period to monitor the CloudWatch alarms in the automatic rollback configuration.</p> </li> </ul>
       status_message: 	 <p>A message that describes the status of the production variant.</p>
       start_time: 	 <p>The start time of the current status change.</p>
    """

    status: str
    status_message: Optional[str] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()


class ProductionVariantSummary(Base):
    """
    ProductionVariantSummary
         <p>Describes weight and capacities for a production variant associated with an endpoint. If you sent a request to the <code>UpdateEndpointWeightsAndCapacities</code> API and the endpoint status is <code>Updating</code>, you get different desired and current values. </p>

        Attributes
       ----------------------
       variant_name: 	 <p>The name of the variant.</p>
       deployed_images: 	 <p>An array of <code>DeployedImage</code> objects that specify the Amazon EC2 Container Registry paths of the inference images deployed on instances of this <code>ProductionVariant</code>.</p>
       current_weight: 	 <p>The weight associated with the variant.</p>
       desired_weight: 	 <p>The requested weight, as specified in the <code>UpdateEndpointWeightsAndCapacities</code> request. </p>
       current_instance_count: 	 <p>The number of instances associated with the variant.</p>
       desired_instance_count: 	 <p>The number of instances requested in the <code>UpdateEndpointWeightsAndCapacities</code> request. </p>
       variant_status: 	 <p>The endpoint variant status which describes the current deployment stage status or operational status.</p>
       current_serverless_config: 	 <p>The serverless configuration for the endpoint.</p>
       desired_serverless_config: 	 <p>The serverless configuration requested for the endpoint update.</p>
       managed_instance_scaling: 	 <p>Settings that control the range in the number of instances that the endpoint provisions as it scales up or down to accommodate traffic. </p>
       routing_config: 	 <p>Settings that control how the endpoint routes incoming traffic to the instances that the endpoint hosts.</p>
    """

    variant_name: str
    deployed_images: Optional[List[DeployedImage]] = Unassigned()
    current_weight: Optional[float] = Unassigned()
    desired_weight: Optional[float] = Unassigned()
    current_instance_count: Optional[int] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    variant_status: Optional[List[ProductionVariantStatus]] = Unassigned()
    current_serverless_config: Optional[ProductionVariantServerlessConfig] = (
        Unassigned()
    )
    desired_serverless_config: Optional[ProductionVariantServerlessConfig] = (
        Unassigned()
    )
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = (
        Unassigned()
    )
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


class PendingProductionVariantSummary(Base):
    """
    PendingProductionVariantSummary
         <p>The production variant summary for a deployment when an endpoint is creating or updating with the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpoint.html">CreateEndpoint</a> or <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html">UpdateEndpoint</a> operations. Describes the <code>VariantStatus </code>, weight and capacity for a production variant associated with an endpoint. </p>

        Attributes
       ----------------------
       variant_name: 	 <p>The name of the variant.</p>
       deployed_images: 	 <p>An array of <code>DeployedImage</code> objects that specify the Amazon EC2 Container Registry paths of the inference images deployed on instances of this <code>ProductionVariant</code>.</p>
       current_weight: 	 <p>The weight associated with the variant.</p>
       desired_weight: 	 <p>The requested weight for the variant in this deployment, as specified in the endpoint configuration for the endpoint. The value is taken from the request to the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html">CreateEndpointConfig</a> operation.</p>
       current_instance_count: 	 <p>The number of instances associated with the variant.</p>
       desired_instance_count: 	 <p>The number of instances requested in this deployment, as specified in the endpoint configuration for the endpoint. The value is taken from the request to the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html">CreateEndpointConfig</a> operation.</p>
       instance_type: 	 <p>The type of instances associated with the variant.</p>
       accelerator_type: 	 <p>The size of the Elastic Inference (EI) instance to use for the production variant. EI instances provide on-demand GPU computing for inference. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/ei.html">Using Elastic Inference in Amazon SageMaker</a>.</p>
       variant_status: 	 <p>The endpoint variant status which describes the current deployment stage status or operational status.</p>
       current_serverless_config: 	 <p>The serverless configuration for the endpoint.</p>
       desired_serverless_config: 	 <p>The serverless configuration requested for this deployment, as specified in the endpoint configuration for the endpoint.</p>
       managed_instance_scaling: 	 <p>Settings that control the range in the number of instances that the endpoint provisions as it scales up or down to accommodate traffic. </p>
       routing_config: 	 <p>Settings that control how the endpoint routes incoming traffic to the instances that the endpoint hosts.</p>
    """

    variant_name: str
    deployed_images: Optional[List[DeployedImage]] = Unassigned()
    current_weight: Optional[float] = Unassigned()
    desired_weight: Optional[float] = Unassigned()
    current_instance_count: Optional[int] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    accelerator_type: Optional[str] = Unassigned()
    variant_status: Optional[List[ProductionVariantStatus]] = Unassigned()
    current_serverless_config: Optional[ProductionVariantServerlessConfig] = (
        Unassigned()
    )
    desired_serverless_config: Optional[ProductionVariantServerlessConfig] = (
        Unassigned()
    )
    managed_instance_scaling: Optional[ProductionVariantManagedInstanceScaling] = (
        Unassigned()
    )
    routing_config: Optional[ProductionVariantRoutingConfig] = Unassigned()


class PendingDeploymentSummary(Base):
    """
    PendingDeploymentSummary
         <p>The summary of an in-progress deployment when an endpoint is creating or updating with a new endpoint configuration.</p>

        Attributes
       ----------------------
       endpoint_config_name: 	 <p>The name of the endpoint configuration used in the deployment. </p>
       production_variants: 	 <p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_PendingProductionVariantSummary.html">PendingProductionVariantSummary</a> objects, one for each model hosted behind this endpoint for the in-progress deployment.</p>
       start_time: 	 <p>The start time of the deployment.</p>
       shadow_production_variants: 	 <p>An array of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_PendingProductionVariantSummary.html">PendingProductionVariantSummary</a> objects, one for each model hosted behind this endpoint in shadow mode with production traffic replicated from the model specified on <code>ProductionVariants</code> for the in-progress deployment.</p>
    """

    endpoint_config_name: str
    production_variants: Optional[List[PendingProductionVariantSummary]] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    shadow_production_variants: Optional[List[PendingProductionVariantSummary]] = (
        Unassigned()
    )


class ExperimentSource(Base):
    """
    ExperimentSource
         <p>The source of the experiment.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The Amazon Resource Name (ARN) of the source.</p>
       source_type: 	 <p>The source type.</p>
    """

    source_arn: str
    source_type: Optional[str] = Unassigned()


class ThroughputConfigDescription(Base):
    """
    ThroughputConfigDescription
         <p>Active throughput configuration of the feature group. There are two modes: <code>ON_DEMAND</code> and <code>PROVISIONED</code>. With on-demand mode, you are charged for data reads and writes that your application performs on your feature group. You do not need to specify read and write throughput because Feature Store accommodates your workloads as they ramp up and down. You can switch a feature group to on-demand only once in a 24 hour period. With provisioned throughput mode, you specify the read and write capacity per second that you expect your application to require, and you are billed based on those limits. Exceeding provisioned throughput will result in your requests being throttled. </p> <p>Note: <code>PROVISIONED</code> throughput mode is supported only for feature groups that are offline-only, or use the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_OnlineStoreConfig.html#sagemaker-Type-OnlineStoreConfig-StorageType"> <code>Standard</code> </a> tier online store. </p>

        Attributes
       ----------------------
       throughput_mode: 	 <p>The mode used for your feature group throughput: <code>ON_DEMAND</code> or <code>PROVISIONED</code>. </p>
       provisioned_read_capacity_units: 	 <p> For provisioned feature groups with online store enabled, this indicates the read throughput you are billed for and can consume without throttling. </p> <p>This field is not applicable for on-demand feature groups. </p>
       provisioned_write_capacity_units: 	 <p> For provisioned feature groups, this indicates the write throughput you are billed for and can consume without throttling. </p> <p>This field is not applicable for on-demand feature groups. </p>
    """

    throughput_mode: str
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


class OfflineStoreStatus(Base):
    """
    OfflineStoreStatus
         <p>The status of <code>OfflineStore</code>.</p>

        Attributes
       ----------------------
       status: 	 <p>An <code>OfflineStore</code> status.</p>
       blocked_reason: 	 <p>The justification for why the OfflineStoreStatus is Blocked (if applicable).</p>
    """

    status: str
    blocked_reason: Optional[str] = Unassigned()


class LastUpdateStatus(Base):
    """
    LastUpdateStatus
         <p>A value that indicates whether the update was successful.</p>

        Attributes
       ----------------------
       status: 	 <p>A value that indicates whether the update was made successful.</p>
       failure_reason: 	 <p>If the update wasn't successful, indicates the reason why it failed.</p>
    """

    status: str
    failure_reason: Optional[str] = Unassigned()


class FeatureParameter(Base):
    """
    FeatureParameter
         <p>A key-value pair that you specify to describe the feature.</p>

        Attributes
       ----------------------
       key: 	 <p>A key that must contain a value to describe the feature.</p>
       value: 	 <p>The value that belongs to a key.</p>
    """

    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


class HubContentDependency(Base):
    """
    HubContentDependency
         <p>Any dependencies related to hub content, such as scripts, model artifacts, datasets, or notebooks.</p>

        Attributes
       ----------------------
       dependency_origin_path: 	 <p>The hub content dependency origin path.</p>
       dependency_copy_path: 	 <p>The hub content dependency copy path.</p>
    """

    dependency_origin_path: Optional[str] = Unassigned()
    dependency_copy_path: Optional[str] = Unassigned()


class UiTemplateInfo(Base):
    """
    UiTemplateInfo
         <p>Container for user interface template information.</p>

        Attributes
       ----------------------
       url: 	 <p>The URL for the user interface template.</p>
       content_sha256: 	 <p>The SHA-256 digest of the contents of the template.</p>
    """

    url: Optional[str] = Unassigned()
    content_sha256: Optional[str] = Unassigned()


class TrainingJobStatusCounters(Base):
    """
    TrainingJobStatusCounters
         <p>The numbers of training jobs launched by a hyperparameter tuning job, categorized by status.</p>

        Attributes
       ----------------------
       completed: 	 <p>The number of completed training jobs launched by the hyperparameter tuning job.</p>
       in_progress: 	 <p>The number of in-progress training jobs launched by a hyperparameter tuning job.</p>
       retryable_error: 	 <p>The number of training jobs that failed, but can be retried. A failed training job can be retried only if it failed because an internal service error occurred.</p>
       non_retryable_error: 	 <p>The number of training jobs that failed and can't be retried. A failed training job can't be retried if it failed because a client error occurred.</p>
       stopped: 	 <p>The number of training jobs launched by a hyperparameter tuning job that were manually stopped.</p>
    """

    completed: Optional[int] = Unassigned()
    in_progress: Optional[int] = Unassigned()
    retryable_error: Optional[int] = Unassigned()
    non_retryable_error: Optional[int] = Unassigned()
    stopped: Optional[int] = Unassigned()


class ObjectiveStatusCounters(Base):
    """
    ObjectiveStatusCounters
         <p>Specifies the number of training jobs that this hyperparameter tuning job launched, categorized by the status of their objective metric. The objective metric status shows whether the final objective metric for the training job has been evaluated by the tuning job and used in the hyperparameter tuning process.</p>

        Attributes
       ----------------------
       succeeded: 	 <p>The number of training jobs whose final objective metric was evaluated by the hyperparameter tuning job and used in the hyperparameter tuning process.</p>
       pending: 	 <p>The number of training jobs that are in progress and pending evaluation of their final objective metric.</p>
       failed: 	 <p>The number of training jobs whose final objective metric was not evaluated and used in the hyperparameter tuning process. This typically occurs when the training job failed or did not emit an objective metric.</p>
    """

    succeeded: Optional[int] = Unassigned()
    pending: Optional[int] = Unassigned()
    failed: Optional[int] = Unassigned()


class FinalHyperParameterTuningJobObjectiveMetric(Base):
    """
    FinalHyperParameterTuningJobObjectiveMetric
         <p>Shows the latest objective metric emitted by a training job that was launched by a hyperparameter tuning job. You define the objective metric in the <code>HyperParameterTuningJobObjective</code> parameter of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_HyperParameterTuningJobConfig.html">HyperParameterTuningJobConfig</a>.</p>

        Attributes
       ----------------------
       type: 	 <p>Select if you want to minimize or maximize the objective metric during hyperparameter tuning. </p>
       metric_name: 	 <p>The name of the objective metric. For SageMaker built-in algorithms, metrics are defined per algorithm. See the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/xgboost-tuning.html">metrics for XGBoost</a> as an example. You can also use a custom algorithm for training and define your own metrics. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning-define-metrics-variables.html">Define metrics and environment variables</a>.</p>
       value: 	 <p>The value of the objective metric.</p>
    """

    metric_name: str
    value: float
    type: Optional[str] = Unassigned()


class HyperParameterTrainingJobSummary(Base):
    """
    HyperParameterTrainingJobSummary
         <p>The container for the summary information about a training job.</p>

        Attributes
       ----------------------
       training_job_definition_name: 	 <p>The training job definition name.</p>
       training_job_name: 	 <p>The name of the training job.</p>
       training_job_arn: 	 <p>The Amazon Resource Name (ARN) of the training job.</p>
       tuning_job_name: 	 <p>The HyperParameter tuning job that launched the training job.</p>
       creation_time: 	 <p>The date and time that the training job was created.</p>
       training_start_time: 	 <p>The date and time that the training job started.</p>
       training_end_time: 	 <p>Specifies the time when the training job ends on training instances. You are billed for the time interval between the value of <code>TrainingStartTime</code> and this time. For successful jobs and stopped jobs, this is the time after model artifacts are uploaded. For failed jobs, this is the time when SageMaker detects a job failure.</p>
       training_job_status: 	 <p>The status of the training job.</p>
       tuned_hyper_parameters: 	 <p>A list of the hyperparameters for which you specified ranges to search.</p>
       failure_reason: 	 <p>The reason that the training job failed. </p>
       final_hyper_parameter_tuning_job_objective_metric: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_FinalHyperParameterTuningJobObjectiveMetric.html">FinalHyperParameterTuningJobObjectiveMetric</a> object that specifies the value of the objective metric of the tuning job that launched this training job.</p>
       objective_status: 	 <p>The status of the objective metric for the training job:</p> <ul> <li> <p>Succeeded: The final objective metric for the training job was evaluated by the hyperparameter tuning job and used in the hyperparameter tuning process.</p> </li> </ul> <ul> <li> <p>Pending: The training job is in progress and evaluation of its final objective metric is pending.</p> </li> </ul> <ul> <li> <p>Failed: The final objective metric for the training job was not evaluated, and was not used in the hyperparameter tuning process. This typically occurs when the training job failed or did not emit an objective metric.</p> </li> </ul>
    """

    training_job_name: str
    training_job_arn: str
    creation_time: datetime.datetime
    training_job_status: str
    tuned_hyper_parameters: Dict[str, str]
    training_job_definition_name: Optional[str] = Unassigned()
    tuning_job_name: Optional[str] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    final_hyper_parameter_tuning_job_objective_metric: Optional[
        FinalHyperParameterTuningJobObjectiveMetric
    ] = Unassigned()
    objective_status: Optional[str] = Unassigned()


class HyperParameterTuningJobCompletionDetails(Base):
    """
    HyperParameterTuningJobCompletionDetails
         <p>A structure that contains runtime information about both current and completed hyperparameter tuning jobs.</p>

        Attributes
       ----------------------
       number_of_training_jobs_objective_not_improving: 	 <p>The number of training jobs launched by a tuning job that are not improving (1% or less) as measured by model performance evaluated against an objective function.</p>
       convergence_detected_time: 	 <p>The time in timestamp format that AMT detected model convergence, as defined by a lack of significant improvement over time based on criteria developed over a wide range of diverse benchmarking tests.</p>
    """

    number_of_training_jobs_objective_not_improving: Optional[int] = Unassigned()
    convergence_detected_time: Optional[datetime.datetime] = Unassigned()


class HyperParameterTuningJobConsumedResources(Base):
    """
    HyperParameterTuningJobConsumedResources
         <p>The total resources consumed by your hyperparameter tuning job.</p>

        Attributes
       ----------------------
       runtime_in_seconds: 	 <p>The wall clock runtime in seconds used by your hyperparameter tuning job.</p>
    """

    runtime_in_seconds: Optional[int] = Unassigned()


class InferenceComponentContainerSpecificationSummary(Base):
    """
    InferenceComponentContainerSpecificationSummary
         <p>Details about the resources that are deployed with this inference component.</p>

        Attributes
       ----------------------
       deployed_image
       artifact_url: 	 <p>The Amazon S3 path where the model artifacts are stored.</p>
       environment: 	 <p>The environment variables to set in the Docker container.</p>
    """

    deployed_image: Optional[DeployedImage] = Unassigned()
    artifact_url: Optional[str] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()


class InferenceComponentSpecificationSummary(Base):
    """
    InferenceComponentSpecificationSummary
         <p>Details about the resources that are deployed with this inference component.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the SageMaker model object that is deployed with the inference component.</p>
       container: 	 <p>Details about the container that provides the runtime environment for the model that is deployed with the inference component.</p>
       startup_parameters: 	 <p>Settings that take effect while the model container starts up.</p>
       compute_resource_requirements: 	 <p>The compute resources allocated to run the model assigned to the inference component.</p>
    """

    model_name: Optional[str] = Unassigned()
    container: Optional[InferenceComponentContainerSpecificationSummary] = Unassigned()
    startup_parameters: Optional[InferenceComponentStartupParameters] = Unassigned()
    compute_resource_requirements: Optional[
        InferenceComponentComputeResourceRequirements
    ] = Unassigned()


class InferenceComponentRuntimeConfigSummary(Base):
    """
    InferenceComponentRuntimeConfigSummary
         <p>Details about the runtime settings for the model that is deployed with the inference component.</p>

        Attributes
       ----------------------
       desired_copy_count: 	 <p>The number of runtime copies of the model container that you requested to deploy with the inference component.</p>
       current_copy_count: 	 <p>The number of runtime copies of the model container that are currently deployed.</p>
    """

    desired_copy_count: Optional[int] = Unassigned()
    current_copy_count: Optional[int] = Unassigned()


class EndpointMetadata(Base):
    """
    EndpointMetadata
         <p>The metadata of the endpoint.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of the endpoint.</p>
       endpoint_config_name: 	 <p>The name of the endpoint configuration.</p>
       endpoint_status: 	 <p> The status of the endpoint. For possible values of the status of an endpoint, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_EndpointSummary.html">EndpointSummary</a>. </p>
       failure_reason: 	 <p> If the status of the endpoint is <code>Failed</code>, or the status is <code>InService</code> but update operation fails, this provides the reason why it failed. </p>
    """

    endpoint_name: str
    endpoint_config_name: Optional[str] = Unassigned()
    endpoint_status: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


class ModelVariantConfigSummary(Base):
    """
    ModelVariantConfigSummary
         <p>Summary of the deployment configuration of a model.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the Amazon SageMaker Model entity.</p>
       variant_name: 	 <p>The name of the variant.</p>
       infrastructure_config: 	 <p>The configuration of the infrastructure that the model has been deployed to.</p>
       status: 	 <p>The status of deployment for the model variant on the hosted inference endpoint.</p> <ul> <li> <p> <code>Creating</code> - Amazon SageMaker is preparing the model variant on the hosted inference endpoint. </p> </li> <li> <p> <code>InService</code> - The model variant is running on the hosted inference endpoint. </p> </li> <li> <p> <code>Updating</code> - Amazon SageMaker is updating the model variant on the hosted inference endpoint. </p> </li> <li> <p> <code>Deleting</code> - Amazon SageMaker is deleting the model variant on the hosted inference endpoint. </p> </li> <li> <p> <code>Deleted</code> - The model variant has been deleted on the hosted inference endpoint. This can only happen after stopping the experiment. </p> </li> </ul>
    """

    model_name: str
    variant_name: str
    infrastructure_config: ModelInfrastructureConfig
    status: str


class RecommendationMetrics(Base):
    """
    RecommendationMetrics
         <p>The metrics of recommendations.</p>

        Attributes
       ----------------------
       cost_per_hour: 	 <p>Defines the cost per hour for the instance. </p>
       cost_per_inference: 	 <p>Defines the cost per inference for the instance .</p>
       max_invocations: 	 <p>The expected maximum number of requests per minute for the instance.</p>
       model_latency: 	 <p>The expected model latency at maximum invocation per minute for the instance.</p>
       cpu_utilization: 	 <p>The expected CPU utilization at maximum invocations per minute for the instance.</p> <p> <code>NaN</code> indicates that the value is not available.</p>
       memory_utilization: 	 <p>The expected memory utilization at maximum invocations per minute for the instance.</p> <p> <code>NaN</code> indicates that the value is not available.</p>
       model_setup_time: 	 <p>The time it takes to launch new compute resources for a serverless endpoint. The time can vary depending on the model size, how long it takes to download the model, and the start-up time of the container.</p> <p> <code>NaN</code> indicates that the value is not available.</p>
    """

    cost_per_hour: float
    cost_per_inference: float
    max_invocations: int
    model_latency: int
    cpu_utilization: Optional[float] = Unassigned()
    memory_utilization: Optional[float] = Unassigned()
    model_setup_time: Optional[int] = Unassigned()


class EndpointOutputConfiguration(Base):
    """
    EndpointOutputConfiguration
         <p>The endpoint configuration made by Inference Recommender during a recommendation job.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of the endpoint made during a recommendation job.</p>
       variant_name: 	 <p>The name of the production variant (deployed model) made during a recommendation job.</p>
       instance_type: 	 <p>The instance type recommended by Amazon SageMaker Inference Recommender.</p>
       initial_instance_count: 	 <p>The number of instances recommended to launch initially.</p>
       serverless_config
    """

    endpoint_name: str
    variant_name: str
    instance_type: Optional[str] = Unassigned()
    initial_instance_count: Optional[int] = Unassigned()
    serverless_config: Optional[ProductionVariantServerlessConfig] = Unassigned()


class EnvironmentParameter(Base):
    """
    EnvironmentParameter
         <p>A list of environment parameters suggested by the Amazon SageMaker Inference Recommender.</p>

        Attributes
       ----------------------
       key: 	 <p>The environment key suggested by the Amazon SageMaker Inference Recommender.</p>
       value_type: 	 <p>The value type suggested by the Amazon SageMaker Inference Recommender.</p>
       value: 	 <p>The value suggested by the Amazon SageMaker Inference Recommender.</p>
    """

    key: str
    value_type: str
    value: str


class ModelConfiguration(Base):
    """
    ModelConfiguration
         <p>Defines the model configuration. Includes the specification name and environment parameters.</p>

        Attributes
       ----------------------
       inference_specification_name: 	 <p>The inference specification name in the model package version.</p>
       environment_parameters: 	 <p>Defines the environment parameters that includes key, value types, and values.</p>
       compilation_job_name: 	 <p>The name of the compilation job used to create the recommended model artifacts.</p>
    """

    inference_specification_name: Optional[str] = Unassigned()
    environment_parameters: Optional[List[EnvironmentParameter]] = Unassigned()
    compilation_job_name: Optional[str] = Unassigned()


class InferenceRecommendation(Base):
    """
    InferenceRecommendation
         <p>A list of recommendations made by Amazon SageMaker Inference Recommender.</p>

        Attributes
       ----------------------
       recommendation_id: 	 <p>The recommendation ID which uniquely identifies each recommendation.</p>
       metrics: 	 <p>The metrics used to decide what recommendation to make.</p>
       endpoint_configuration: 	 <p>Defines the endpoint configuration parameters.</p>
       model_configuration: 	 <p>Defines the model configuration.</p>
       invocation_end_time: 	 <p>A timestamp that shows when the benchmark completed.</p>
       invocation_start_time: 	 <p>A timestamp that shows when the benchmark started.</p>
    """

    metrics: RecommendationMetrics
    endpoint_configuration: EndpointOutputConfiguration
    model_configuration: ModelConfiguration
    recommendation_id: Optional[str] = Unassigned()
    invocation_end_time: Optional[datetime.datetime] = Unassigned()
    invocation_start_time: Optional[datetime.datetime] = Unassigned()


class InferenceMetrics(Base):
    """
    InferenceMetrics
         <p>The metrics for an existing endpoint compared in an Inference Recommender job.</p>

        Attributes
       ----------------------
       max_invocations: 	 <p>The expected maximum number of requests per minute for the instance.</p>
       model_latency: 	 <p>The expected model latency at maximum invocations per minute for the instance.</p>
    """

    max_invocations: int
    model_latency: int


class EndpointPerformance(Base):
    """
    EndpointPerformance
         <p>The performance results from running an Inference Recommender job on an existing endpoint.</p>

        Attributes
       ----------------------
       metrics: 	 <p>The metrics for an existing endpoint.</p>
       endpoint_info
    """

    metrics: InferenceMetrics
    endpoint_info: EndpointInfo


class LabelCounters(Base):
    """
    LabelCounters
         <p>Provides a breakdown of the number of objects labeled.</p>

        Attributes
       ----------------------
       total_labeled: 	 <p>The total number of objects labeled.</p>
       human_labeled: 	 <p>The total number of objects labeled by a human worker.</p>
       machine_labeled: 	 <p>The total number of objects labeled by automated data labeling.</p>
       failed_non_retryable_error: 	 <p>The total number of objects that could not be labeled due to an error.</p>
       unlabeled: 	 <p>The total number of objects not yet labeled.</p>
    """

    total_labeled: Optional[int] = Unassigned()
    human_labeled: Optional[int] = Unassigned()
    machine_labeled: Optional[int] = Unassigned()
    failed_non_retryable_error: Optional[int] = Unassigned()
    unlabeled: Optional[int] = Unassigned()


class LabelingJobOutput(Base):
    """
    LabelingJobOutput
         <p>Specifies the location of the output produced by the labeling job. </p>

        Attributes
       ----------------------
       output_dataset_s3_uri: 	 <p>The Amazon S3 bucket location of the manifest file for labeled data. </p>
       final_active_learning_model_arn: 	 <p>The Amazon Resource Name (ARN) for the most recent SageMaker model trained as part of automated data labeling. </p>
    """

    output_dataset_s3_uri: str
    final_active_learning_model_arn: Optional[str] = Unassigned()


class ModelCardExportArtifacts(Base):
    """
    ModelCardExportArtifacts
         <p>The artifacts of the model card export job.</p>

        Attributes
       ----------------------
       s3_export_artifacts: 	 <p>The Amazon S3 URI of the exported model artifacts.</p>
    """

    s3_export_artifacts: str


class ModelPackageStatusItem(Base):
    """
    ModelPackageStatusItem
         <p>Represents the overall status of a model package.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the model package for which the overall status is being reported.</p>
       status: 	 <p>The current status.</p>
       failure_reason: 	 <p>if the overall status is <code>Failed</code>, the reason for the failure.</p>
    """

    name: str
    status: str
    failure_reason: Optional[str] = Unassigned()


class ModelPackageStatusDetails(Base):
    """
    ModelPackageStatusDetails
         <p>Specifies the validation and image scan statuses of the model package.</p>

        Attributes
       ----------------------
       validation_statuses: 	 <p>The validation status of the model package.</p>
       image_scan_statuses: 	 <p>The status of the scan of the Docker image container for the model package.</p>
    """

    validation_statuses: List[ModelPackageStatusItem]
    image_scan_statuses: Optional[List[ModelPackageStatusItem]] = Unassigned()


class MonitoringExecutionSummary(Base):
    """
    MonitoringExecutionSummary
         <p>Summary of information about the last monitoring job to run.</p>

        Attributes
       ----------------------
       monitoring_schedule_name: 	 <p>The name of the monitoring schedule.</p>
       scheduled_time: 	 <p>The time the monitoring job was scheduled.</p>
       creation_time: 	 <p>The time at which the monitoring job was created.</p>
       last_modified_time: 	 <p>A timestamp that indicates the last time the monitoring job was modified.</p>
       monitoring_execution_status: 	 <p>The status of the monitoring job.</p>
       processing_job_arn: 	 <p>The Amazon Resource Name (ARN) of the monitoring job.</p>
       endpoint_name: 	 <p>The name of the endpoint used to run the monitoring job.</p>
       failure_reason: 	 <p>Contains the reason a monitoring job failed, if it failed.</p>
       monitoring_job_definition_name: 	 <p>The name of the monitoring job.</p>
       monitoring_type: 	 <p>The type of the monitoring job.</p>
    """

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


class PipelineExperimentConfig(Base):
    """
    PipelineExperimentConfig
         <p>Specifies the names of the experiment and trial created by a pipeline.</p>

        Attributes
       ----------------------
       experiment_name: 	 <p>The name of the experiment.</p>
       trial_name: 	 <p>The name of the trial.</p>
    """

    experiment_name: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()


class SelectedStep(Base):
    """
    SelectedStep
         <p>A step selected to run in selective execution mode.</p>

        Attributes
       ----------------------
       step_name: 	 <p>The name of the pipeline step.</p>
    """

    step_name: str


class SelectiveExecutionConfig(Base):
    """
    SelectiveExecutionConfig
         <p>The selective execution configuration applied to the pipeline run.</p>

        Attributes
       ----------------------
       source_pipeline_execution_arn: 	 <p>The ARN from a reference execution of the current pipeline. Used to copy input collaterals needed for the selected steps to run. The execution status of the pipeline can be either <code>Failed</code> or <code>Success</code>.</p> <p>This field is required if the steps you specify for <code>SelectedSteps</code> depend on output collaterals from any non-specified pipeline steps. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-selective-ex.html">Selective Execution for Pipeline Steps</a>.</p>
       selected_steps: 	 <p>A list of pipeline steps to run. All step(s) in all path(s) between two selected steps should be included.</p>
    """

    selected_steps: List[SelectedStep]
    source_pipeline_execution_arn: Optional[str] = Unassigned()


class ServiceCatalogProvisionedProductDetails(Base):
    """
    ServiceCatalogProvisionedProductDetails
         <p>Details of a provisioned service catalog product. For information about service catalog, see <a href="https://docs.aws.amazon.com/servicecatalog/latest/adminguide/introduction.html">What is Amazon Web Services Service Catalog</a>.</p>

        Attributes
       ----------------------
       provisioned_product_id: 	 <p>The ID of the provisioned product.</p>
       provisioned_product_status_message: 	 <p>The current status of the product.</p> <ul> <li> <p> <code>AVAILABLE</code> - Stable state, ready to perform any operation. The most recent operation succeeded and completed.</p> </li> <li> <p> <code>UNDER_CHANGE</code> - Transitive state. Operations performed might not have valid results. Wait for an AVAILABLE status before performing operations.</p> </li> <li> <p> <code>TAINTED</code> - Stable state, ready to perform any operation. The stack has completed the requested operation but is not exactly what was requested. For example, a request to update to a new version failed and the stack rolled back to the current version.</p> </li> <li> <p> <code>ERROR</code> - An unexpected error occurred. The provisioned product exists but the stack is not running. For example, CloudFormation received a parameter value that was not valid and could not launch the stack.</p> </li> <li> <p> <code>PLAN_IN_PROGRESS</code> - Transitive state. The plan operations were performed to provision a new product, but resources have not yet been created. After reviewing the list of resources to be created, execute the plan. Wait for an AVAILABLE status before performing operations.</p> </li> </ul>
    """

    provisioned_product_id: Optional[str] = Unassigned()
    provisioned_product_status_message: Optional[str] = Unassigned()


class SubscribedWorkteam(Base):
    """
    SubscribedWorkteam
         <p>Describes a work team of a vendor that does the a labelling job.</p>

        Attributes
       ----------------------
       workteam_arn: 	 <p>The Amazon Resource Name (ARN) of the vendor that you have subscribed.</p>
       marketplace_title: 	 <p>The title of the service provided by the vendor in the Amazon Marketplace.</p>
       seller_name: 	 <p>The name of the vendor in the Amazon Marketplace.</p>
       marketplace_description: 	 <p>The description of the vendor from the Amazon Marketplace.</p>
       listing_id: 	 <p>Marketplace product listing ID.</p>
    """

    workteam_arn: str
    marketplace_title: Optional[str] = Unassigned()
    seller_name: Optional[str] = Unassigned()
    marketplace_description: Optional[str] = Unassigned()
    listing_id: Optional[str] = Unassigned()


class WarmPoolStatus(Base):
    """
    WarmPoolStatus
         <p>Status and billing information about the warm pool.</p>

        Attributes
       ----------------------
       status: 	 <p>The status of the warm pool.</p> <ul> <li> <p> <code>InUse</code>: The warm pool is in use for the training job.</p> </li> <li> <p> <code>Available</code>: The warm pool is available to reuse for a matching training job.</p> </li> <li> <p> <code>Reused</code>: The warm pool moved to a matching training job for reuse.</p> </li> <li> <p> <code>Terminated</code>: The warm pool is no longer available. Warm pools are unavailable if they are terminated by a user, terminated for a patch update, or terminated for exceeding the specified <code>KeepAlivePeriodInSeconds</code>.</p> </li> </ul>
       resource_retained_billable_time_in_seconds: 	 <p>The billable time in seconds used by the warm pool. Billable time refers to the absolute wall-clock time.</p> <p>Multiply <code>ResourceRetainedBillableTimeInSeconds</code> by the number of instances (<code>InstanceCount</code>) in your training cluster to get the total compute time SageMaker bills you if you run warm pool training. The formula is as follows: <code>ResourceRetainedBillableTimeInSeconds * InstanceCount</code>.</p>
       reused_by_job: 	 <p>The name of the matching training job that reused the warm pool.</p>
    """

    status: str
    resource_retained_billable_time_in_seconds: Optional[int] = Unassigned()
    reused_by_job: Optional[str] = Unassigned()


class SecondaryStatusTransition(Base):
    """
    SecondaryStatusTransition
         <p>An array element of <code>SecondaryStatusTransitions</code> for <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrainingJob.html">DescribeTrainingJob</a>. It provides additional details about a status that the training job has transitioned through. A training job can be in one of several states, for example, starting, downloading, training, or uploading. Within each state, there are a number of intermediate states. For example, within the starting state, SageMaker could be starting the training job or launching the ML instances. These transitional states are referred to as the job's secondary status. </p> <p/>

        Attributes
       ----------------------
       status: 	 <p>Contains a secondary status information from a training job.</p> <p>Status might be one of the following secondary statuses:</p> <dl> <dt>InProgress</dt> <dd> <ul> <li> <p> <code>Starting</code> - Starting the training job.</p> </li> <li> <p> <code>Downloading</code> - An optional stage for algorithms that support <code>File</code> training input mode. It indicates that data is being downloaded to the ML storage volumes.</p> </li> <li> <p> <code>Training</code> - Training is in progress.</p> </li> <li> <p> <code>Uploading</code> - Training is complete and the model artifacts are being uploaded to the S3 location.</p> </li> </ul> </dd> <dt>Completed</dt> <dd> <ul> <li> <p> <code>Completed</code> - The training job has completed.</p> </li> </ul> </dd> <dt>Failed</dt> <dd> <ul> <li> <p> <code>Failed</code> - The training job has failed. The reason for the failure is returned in the <code>FailureReason</code> field of <code>DescribeTrainingJobResponse</code>.</p> </li> </ul> </dd> <dt>Stopped</dt> <dd> <ul> <li> <p> <code>MaxRuntimeExceeded</code> - The job stopped because it exceeded the maximum allowed runtime.</p> </li> <li> <p> <code>Stopped</code> - The training job has stopped.</p> </li> </ul> </dd> <dt>Stopping</dt> <dd> <ul> <li> <p> <code>Stopping</code> - Stopping the training job.</p> </li> </ul> </dd> </dl> <p>We no longer support the following secondary statuses:</p> <ul> <li> <p> <code>LaunchingMLInstances</code> </p> </li> <li> <p> <code>PreparingTrainingStack</code> </p> </li> <li> <p> <code>DownloadingTrainingImage</code> </p> </li> </ul>
       start_time: 	 <p>A timestamp that shows when the training job transitioned to the current secondary status state.</p>
       end_time: 	 <p>A timestamp that shows when the training job transitioned out of this secondary status state into another secondary status state or when the training job has ended.</p>
       status_message: 	 <p>A detailed description of the progress within a secondary status. </p> <p>SageMaker provides secondary statuses and status messages that apply to each of them:</p> <dl> <dt>Starting</dt> <dd> <ul> <li> <p>Starting the training job.</p> </li> <li> <p>Launching requested ML instances.</p> </li> <li> <p>Insufficient capacity error from EC2 while launching instances, retrying!</p> </li> <li> <p>Launched instance was unhealthy, replacing it!</p> </li> <li> <p>Preparing the instances for training.</p> </li> </ul> </dd> <dt>Training</dt> <dd> <ul> <li> <p>Training image download completed. Training in progress.</p> </li> </ul> </dd> </dl> <important> <p>Status messages are subject to change. Therefore, we recommend not including them in code that programmatically initiates actions. For examples, don't use status messages in if statements.</p> </important> <p>To have an overview of your training job's progress, view <code>TrainingJobStatus</code> and <code>SecondaryStatus</code> in <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrainingJob.html">DescribeTrainingJob</a>, and <code>StatusMessage</code> together. For example, at the start of a training job, you might see the following:</p> <ul> <li> <p> <code>TrainingJobStatus</code> - InProgress</p> </li> <li> <p> <code>SecondaryStatus</code> - Training</p> </li> <li> <p> <code>StatusMessage</code> - Downloading the training image</p> </li> </ul>
    """

    status: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = Unassigned()
    status_message: Optional[str] = Unassigned()


class MetricData(Base):
    """
    MetricData
         <p>The name, value, and date and time of a metric that was emitted to Amazon CloudWatch.</p>

        Attributes
       ----------------------
       metric_name: 	 <p>The name of the metric.</p>
       value: 	 <p>The value of the metric.</p>
       timestamp: 	 <p>The date and time that the algorithm emitted the metric.</p>
    """

    metric_name: Optional[str] = Unassigned()
    value: Optional[float] = Unassigned()
    timestamp: Optional[datetime.datetime] = Unassigned()


class ProfilerRuleEvaluationStatus(Base):
    """
    ProfilerRuleEvaluationStatus
         <p>Information about the status of the rule evaluation.</p>

        Attributes
       ----------------------
       rule_configuration_name: 	 <p>The name of the rule configuration.</p>
       rule_evaluation_job_arn: 	 <p>The Amazon Resource Name (ARN) of the rule evaluation job.</p>
       rule_evaluation_status: 	 <p>Status of the rule evaluation.</p>
       status_details: 	 <p>Details from the rule evaluation.</p>
       last_modified_time: 	 <p>Timestamp when the rule evaluation status was last modified.</p>
    """

    rule_configuration_name: Optional[str] = Unassigned()
    rule_evaluation_job_arn: Optional[str] = Unassigned()
    rule_evaluation_status: Optional[str] = Unassigned()
    status_details: Optional[str] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class TrialComponentSource(Base):
    """
    TrialComponentSource
         <p>The Amazon Resource Name (ARN) and job type of the source of a trial component.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The source Amazon Resource Name (ARN).</p>
       source_type: 	 <p>The source job type.</p>
    """

    source_arn: str
    source_type: Optional[str] = Unassigned()


class TrialComponentMetricSummary(Base):
    """
    TrialComponentMetricSummary
         <p>A summary of the metrics of a trial component.</p>

        Attributes
       ----------------------
       metric_name: 	 <p>The name of the metric.</p>
       source_arn: 	 <p>The Amazon Resource Name (ARN) of the source.</p>
       time_stamp: 	 <p>When the metric was last updated.</p>
       max: 	 <p>The maximum value of the metric.</p>
       min: 	 <p>The minimum value of the metric.</p>
       last: 	 <p>The most recent value of the metric.</p>
       count: 	 <p>The number of samples used to generate the metric.</p>
       avg: 	 <p>The average value of the metric.</p>
       std_dev: 	 <p>The standard deviation of the metric.</p>
    """

    metric_name: Optional[str] = Unassigned()
    source_arn: Optional[str] = Unassigned()
    time_stamp: Optional[datetime.datetime] = Unassigned()
    max: Optional[float] = Unassigned()
    min: Optional[float] = Unassigned()
    last: Optional[float] = Unassigned()
    count: Optional[int] = Unassigned()
    avg: Optional[float] = Unassigned()
    std_dev: Optional[float] = Unassigned()


class TrialSource(Base):
    """
    TrialSource
         <p>The source of the trial.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The Amazon Resource Name (ARN) of the source.</p>
       source_type: 	 <p>The source job type.</p>
    """

    source_arn: str
    source_type: Optional[str] = Unassigned()


class OidcConfigForResponse(Base):
    """
    OidcConfigForResponse
         <p>Your OIDC IdP workforce configuration.</p>

        Attributes
       ----------------------
       client_id: 	 <p>The OIDC IdP client ID used to configure your private workforce.</p>
       issuer: 	 <p>The OIDC IdP issuer used to configure your private workforce.</p>
       authorization_endpoint: 	 <p>The OIDC IdP authorization endpoint used to configure your private workforce.</p>
       token_endpoint: 	 <p>The OIDC IdP token endpoint used to configure your private workforce.</p>
       user_info_endpoint: 	 <p>The OIDC IdP user information endpoint used to configure your private workforce.</p>
       logout_endpoint: 	 <p>The OIDC IdP logout endpoint used to configure your private workforce.</p>
       jwks_uri: 	 <p>The OIDC IdP JSON Web Key Set (Jwks) URI used to configure your private workforce.</p>
    """

    client_id: Optional[str] = Unassigned()
    issuer: Optional[str] = Unassigned()
    authorization_endpoint: Optional[str] = Unassigned()
    token_endpoint: Optional[str] = Unassigned()
    user_info_endpoint: Optional[str] = Unassigned()
    logout_endpoint: Optional[str] = Unassigned()
    jwks_uri: Optional[str] = Unassigned()


class WorkforceVpcConfigResponse(Base):
    """
    WorkforceVpcConfigResponse
         <p>A VpcConfig object that specifies the VPC that you want your workforce to connect to.</p>

        Attributes
       ----------------------
       vpc_id: 	 <p>The ID of the VPC that the workforce uses for communication.</p>
       security_group_ids: 	 <p>The VPC security group IDs, in the form sg-xxxxxxxx. The security groups must be for the same VPC as specified in the subnet.</p>
       subnets: 	 <p>The ID of the subnets in the VPC that you want to connect.</p>
       vpc_endpoint_id: 	 <p>The IDs for the VPC service endpoints of your VPC workforce when it is created and updated.</p>
    """

    vpc_id: str
    security_group_ids: List[str]
    subnets: List[str]
    vpc_endpoint_id: Optional[str] = Unassigned()


class Workforce(Base):
    """
    Workforce
         <p>A single private workforce, which is automatically created when you create your first private work team. You can create one private work force in each Amazon Web Services Region. By default, any workforce-related API operation used in a specific region will apply to the workforce created in that region. To learn how to create a private workforce, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-workforce-create-private.html">Create a Private Workforce</a>.</p>

        Attributes
       ----------------------
       workforce_name: 	 <p>The name of the private workforce.</p>
       workforce_arn: 	 <p>The Amazon Resource Name (ARN) of the private workforce.</p>
       last_updated_date: 	 <p>The most recent date that <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateWorkforce.html">UpdateWorkforce</a> was used to successfully add one or more IP address ranges (<a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html">CIDRs</a>) to a private workforce's allow list.</p>
       source_ip_config: 	 <p>A list of one to ten IP address ranges (<a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html">CIDRs</a>) to be added to the workforce allow list. By default, a workforce isn't restricted to specific IP addresses.</p>
       sub_domain: 	 <p>The subdomain for your OIDC Identity Provider.</p>
       cognito_config: 	 <p>The configuration of an Amazon Cognito workforce. A single Cognito workforce is created using and corresponds to a single <a href="https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html"> Amazon Cognito user pool</a>.</p>
       oidc_config: 	 <p>The configuration of an OIDC Identity Provider (IdP) private workforce.</p>
       create_date: 	 <p>The date that the workforce is created.</p>
       workforce_vpc_config: 	 <p>The configuration of a VPC workforce.</p>
       status: 	 <p>The status of your workforce.</p>
       failure_reason: 	 <p>The reason your workforce failed.</p>
    """

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


class Workteam(Base):
    """
    Workteam
         <p>Provides details about a labeling work team.</p>

        Attributes
       ----------------------
       workteam_name: 	 <p>The name of the work team.</p>
       member_definitions: 	 <p>A list of <code>MemberDefinition</code> objects that contains objects that identify the workers that make up the work team. </p> <p>Workforces can be created using Amazon Cognito or your own OIDC Identity Provider (IdP). For private workforces created using Amazon Cognito use <code>CognitoMemberDefinition</code>. For workforces created using your own OIDC identity provider (IdP) use <code>OidcMemberDefinition</code>.</p>
       workteam_arn: 	 <p>The Amazon Resource Name (ARN) that identifies the work team.</p>
       workforce_arn: 	 <p>The Amazon Resource Name (ARN) of the workforce.</p>
       product_listing_ids: 	 <p>The Amazon Marketplace identifier for a vendor's work team.</p>
       description: 	 <p>A description of the work team.</p>
       sub_domain: 	 <p>The URI of the labeling job's user interface. Workers open this URI to start labeling your data objects.</p>
       create_date: 	 <p>The date and time that the work team was created (timestamp).</p>
       last_updated_date: 	 <p>The date and time that the work team was last updated (timestamp).</p>
       notification_configuration: 	 <p>Configures SNS notifications of available or expiring work items for work teams.</p>
    """

    workteam_name: str
    member_definitions: List[MemberDefinition]
    workteam_arn: str
    description: str
    workforce_arn: Optional[str] = Unassigned()
    product_listing_ids: Optional[List[str]] = Unassigned()
    sub_domain: Optional[str] = Unassigned()
    create_date: Optional[datetime.datetime] = Unassigned()
    last_updated_date: Optional[datetime.datetime] = Unassigned()
    notification_configuration: Optional[NotificationConfiguration] = Unassigned()


class ProductionVariantServerlessUpdateConfig(Base):
    """
    ProductionVariantServerlessUpdateConfig
         <p>Specifies the serverless update concurrency configuration for an endpoint variant.</p>

        Attributes
       ----------------------
       max_concurrency: 	 <p>The updated maximum number of concurrent invocations your serverless endpoint can process.</p>
       provisioned_concurrency: 	 <p>The updated amount of provisioned concurrency to allocate for the serverless endpoint. Should be less than or equal to <code>MaxConcurrency</code>.</p>
    """

    max_concurrency: Optional[int] = Unassigned()
    provisioned_concurrency: Optional[int] = Unassigned()


class DesiredWeightAndCapacity(Base):
    """
    DesiredWeightAndCapacity
         <p>Specifies weight and capacity values for a production variant.</p>

        Attributes
       ----------------------
       variant_name: 	 <p>The name of the variant to update.</p>
       desired_weight: 	 <p>The variant's weight.</p>
       desired_instance_count: 	 <p>The variant's capacity.</p>
       serverless_update_config: 	 <p>Specifies the serverless update concurrency configuration for an endpoint variant.</p>
    """

    variant_name: str
    desired_weight: Optional[float] = Unassigned()
    desired_instance_count: Optional[int] = Unassigned()
    serverless_update_config: Optional[ProductionVariantServerlessUpdateConfig] = (
        Unassigned()
    )


class Device(Base):
    """
    Device
         <p>Information of a particular device.</p>

        Attributes
       ----------------------
       device_name: 	 <p>The name of the device.</p>
       description: 	 <p>Description of the device.</p>
       iot_thing_name: 	 <p>Amazon Web Services Internet of Things (IoT) object name.</p>
    """

    device_name: str
    description: Optional[str] = Unassigned()
    iot_thing_name: Optional[str] = Unassigned()


class DeviceDeploymentSummary(Base):
    """
    DeviceDeploymentSummary
         <p>Contains information summarizing device details and deployment status.</p>

        Attributes
       ----------------------
       edge_deployment_plan_arn: 	 <p>The ARN of the edge deployment plan.</p>
       edge_deployment_plan_name: 	 <p>The name of the edge deployment plan.</p>
       stage_name: 	 <p>The name of the stage in the edge deployment plan.</p>
       deployed_stage_name: 	 <p>The name of the deployed stage.</p>
       device_fleet_name: 	 <p>The name of the fleet to which the device belongs to.</p>
       device_name: 	 <p>The name of the device.</p>
       device_arn: 	 <p>The ARN of the device.</p>
       device_deployment_status: 	 <p>The deployment status of the device.</p>
       device_deployment_status_message: 	 <p>The detailed error message for the deployoment status result.</p>
       description: 	 <p>The description of the device.</p>
       deployment_start_time: 	 <p>The time when the deployment on the device started.</p>
    """

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


class DeviceFleetSummary(Base):
    """
    DeviceFleetSummary
         <p>Summary of the device fleet.</p>

        Attributes
       ----------------------
       device_fleet_arn: 	 <p>Amazon Resource Name (ARN) of the device fleet.</p>
       device_fleet_name: 	 <p>Name of the device fleet.</p>
       creation_time: 	 <p>Timestamp of when the device fleet was created.</p>
       last_modified_time: 	 <p>Timestamp of when the device fleet was last updated.</p>
    """

    device_fleet_arn: str
    device_fleet_name: str
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class DeviceStats(Base):
    """
    DeviceStats
         <p>Status of devices.</p>

        Attributes
       ----------------------
       connected_device_count: 	 <p>The number of devices connected with a heartbeat.</p>
       registered_device_count: 	 <p>The number of registered devices.</p>
    """

    connected_device_count: int
    registered_device_count: int


class EdgeModelSummary(Base):
    """
    EdgeModelSummary
         <p>Summary of model on edge device.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the model.</p>
       model_version: 	 <p>The version model.</p>
    """

    model_name: str
    model_version: str


class DeviceSummary(Base):
    """
    DeviceSummary
         <p>Summary of the device.</p>

        Attributes
       ----------------------
       device_name: 	 <p>The unique identifier of the device.</p>
       device_arn: 	 <p>Amazon Resource Name (ARN) of the device.</p>
       description: 	 <p>A description of the device.</p>
       device_fleet_name: 	 <p>The name of the fleet the device belongs to.</p>
       iot_thing_name: 	 <p>The Amazon Web Services Internet of Things (IoT) object thing name associated with the device..</p>
       registration_time: 	 <p>The timestamp of the last registration or de-reregistration.</p>
       latest_heartbeat: 	 <p>The last heartbeat received from the device.</p>
       models: 	 <p>Models on the device.</p>
       agent_version: 	 <p>Edge Manager agent version.</p>
    """

    device_name: str
    device_arn: str
    description: Optional[str] = Unassigned()
    device_fleet_name: Optional[str] = Unassigned()
    iot_thing_name: Optional[str] = Unassigned()
    registration_time: Optional[datetime.datetime] = Unassigned()
    latest_heartbeat: Optional[datetime.datetime] = Unassigned()
    models: Optional[List[EdgeModelSummary]] = Unassigned()
    agent_version: Optional[str] = Unassigned()


class DomainDetails(Base):
    """
    DomainDetails
         <p>The domain's details.</p>

        Attributes
       ----------------------
       domain_arn: 	 <p>The domain's Amazon Resource Name (ARN).</p>
       domain_id: 	 <p>The domain ID.</p>
       domain_name: 	 <p>The domain name.</p>
       status: 	 <p>The status.</p>
       creation_time: 	 <p>The creation time.</p>
       last_modified_time: 	 <p>The last modified time.</p>
       url: 	 <p>The domain's URL.</p>
    """

    domain_arn: Optional[str] = Unassigned()
    domain_id: Optional[str] = Unassigned()
    domain_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    url: Optional[str] = Unassigned()


class RStudioServerProDomainSettingsForUpdate(Base):
    """
    RStudioServerProDomainSettingsForUpdate
         <p>A collection of settings that update the current configuration for the <code>RStudioServerPro</code> Domain-level app.</p>

        Attributes
       ----------------------
       domain_execution_role_arn: 	 <p>The execution role for the <code>RStudioServerPro</code> Domain-level app.</p>
       default_resource_spec
       r_studio_connect_url: 	 <p>A URL pointing to an RStudio Connect server.</p>
       r_studio_package_manager_url: 	 <p>A URL pointing to an RStudio Package Manager server.</p>
    """

    domain_execution_role_arn: str
    default_resource_spec: Optional[ResourceSpec] = Unassigned()
    r_studio_connect_url: Optional[str] = Unassigned()
    r_studio_package_manager_url: Optional[str] = Unassigned()


class DomainSettingsForUpdate(Base):
    """
    DomainSettingsForUpdate
         <p>A collection of <code>Domain</code> configuration settings to update.</p>

        Attributes
       ----------------------
       r_studio_server_pro_domain_settings_for_update: 	 <p>A collection of <code>RStudioServerPro</code> Domain-level app settings to update. A single <code>RStudioServerPro</code> application is created for a domain.</p>
       execution_role_identity_config: 	 <p>The configuration for attaching a SageMaker user profile name to the execution role as a <a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_control-access_monitor.html">sts:SourceIdentity key</a>. This configuration can only be modified if there are no apps in the <code>InService</code> or <code>Pending</code> state.</p>
       security_group_ids: 	 <p>The security groups for the Amazon Virtual Private Cloud that the <code>Domain</code> uses for communication between Domain-level apps and user apps.</p>
       docker_settings: 	 <p>A collection of settings that configure the domain's Docker interaction.</p>
    """

    r_studio_server_pro_domain_settings_for_update: Optional[
        RStudioServerProDomainSettingsForUpdate
    ] = Unassigned()
    execution_role_identity_config: Optional[str] = Unassigned()
    security_group_ids: Optional[List[str]] = Unassigned()
    docker_settings: Optional[DockerSettings] = Unassigned()


class PredefinedMetricSpecification(Base):
    """
    PredefinedMetricSpecification
         <p>A specification for a predefined metric.</p>

        Attributes
       ----------------------
       predefined_metric_type: 	 <p>The metric type. You can only apply SageMaker metric types to SageMaker endpoints.</p>
    """

    predefined_metric_type: Optional[str] = Unassigned()


class MetricSpecification(Base):
    """
    MetricSpecification
         <p>An object containing information about a metric.</p>

        Attributes
       ----------------------
       predefined: 	 <p>Information about a predefined metric.</p>
       customized: 	 <p>Information about a customized metric.</p>
    """

    predefined: Optional[PredefinedMetricSpecification] = Unassigned()
    customized: Optional[CustomizedMetricSpecification] = Unassigned()


class TargetTrackingScalingPolicyConfiguration(Base):
    """
    TargetTrackingScalingPolicyConfiguration
         <p>A target tracking scaling policy. Includes support for predefined or customized metrics.</p> <p>When using the <a href="https://docs.aws.amazon.com/autoscaling/application/APIReference/API_PutScalingPolicy.html">PutScalingPolicy</a> API, this parameter is required when you are creating a policy with the policy type <code>TargetTrackingScaling</code>.</p>

        Attributes
       ----------------------
       metric_specification: 	 <p>An object containing information about a metric.</p>
       target_value: 	 <p>The recommended target value to specify for the metric when creating a scaling policy.</p>
    """

    metric_specification: Optional[MetricSpecification] = Unassigned()
    target_value: Optional[float] = Unassigned()


class ScalingPolicy(Base):
    """
    ScalingPolicy
         <p>An object containing a recommended scaling policy.</p>

        Attributes
       ----------------------
       target_tracking: 	 <p>A target tracking scaling policy. Includes support for predefined or customized metrics.</p>
    """

    target_tracking: Optional[TargetTrackingScalingPolicyConfiguration] = Unassigned()


class DynamicScalingConfiguration(Base):
    """
    DynamicScalingConfiguration
         <p>An object with the recommended values for you to specify when creating an autoscaling policy.</p>

        Attributes
       ----------------------
       min_capacity: 	 <p>The recommended minimum capacity to specify for your autoscaling policy.</p>
       max_capacity: 	 <p>The recommended maximum capacity to specify for your autoscaling policy.</p>
       scale_in_cooldown: 	 <p>The recommended scale in cooldown time for your autoscaling policy.</p>
       scale_out_cooldown: 	 <p>The recommended scale out cooldown time for your autoscaling policy.</p>
       scaling_policies: 	 <p>An object of the scaling policies for each metric.</p>
    """

    min_capacity: Optional[int] = Unassigned()
    max_capacity: Optional[int] = Unassigned()
    scale_in_cooldown: Optional[int] = Unassigned()
    scale_out_cooldown: Optional[int] = Unassigned()
    scaling_policies: Optional[List[ScalingPolicy]] = Unassigned()


class EMRStepMetadata(Base):
    """
    EMRStepMetadata
         <p>The configurations and outcomes of an Amazon EMR step execution.</p>

        Attributes
       ----------------------
       cluster_id: 	 <p>The identifier of the EMR cluster.</p>
       step_id: 	 <p>The identifier of the EMR cluster step.</p>
       step_name: 	 <p>The name of the EMR cluster step.</p>
       log_file_path: 	 <p>The path to the log file where the cluster step's failure root cause is recorded.</p>
    """

    cluster_id: Optional[str] = Unassigned()
    step_id: Optional[str] = Unassigned()
    step_name: Optional[str] = Unassigned()
    log_file_path: Optional[str] = Unassigned()


class Edge(Base):
    """
    Edge
         <p>A directed edge connecting two lineage entities.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The Amazon Resource Name (ARN) of the source lineage entity of the directed edge.</p>
       destination_arn: 	 <p>The Amazon Resource Name (ARN) of the destination lineage entity of the directed edge.</p>
       association_type: 	 <p>The type of the Association(Edge) between the source and destination. For example <code>ContributedTo</code>, <code>Produced</code>, or <code>DerivedFrom</code>.</p>
    """

    source_arn: Optional[str] = Unassigned()
    destination_arn: Optional[str] = Unassigned()
    association_type: Optional[str] = Unassigned()


class EdgeDeploymentPlanSummary(Base):
    """
    EdgeDeploymentPlanSummary
         <p>Contains information summarizing an edge deployment plan.</p>

        Attributes
       ----------------------
       edge_deployment_plan_arn: 	 <p>The ARN of the edge deployment plan.</p>
       edge_deployment_plan_name: 	 <p>The name of the edge deployment plan.</p>
       device_fleet_name: 	 <p>The name of the device fleet used for the deployment. </p>
       edge_deployment_success: 	 <p>The number of edge devices with the successful deployment.</p>
       edge_deployment_pending: 	 <p>The number of edge devices yet to pick up the deployment, or in progress.</p>
       edge_deployment_failed: 	 <p>The number of edge devices that failed the deployment.</p>
       creation_time: 	 <p>The time when the edge deployment plan was created.</p>
       last_modified_time: 	 <p>The time when the edge deployment plan was last updated.</p>
    """

    edge_deployment_plan_arn: str
    edge_deployment_plan_name: str
    device_fleet_name: str
    edge_deployment_success: int
    edge_deployment_pending: int
    edge_deployment_failed: int
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class EdgeModelStat(Base):
    """
    EdgeModelStat
         <p>Status of edge devices with this model.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the model.</p>
       model_version: 	 <p>The model version.</p>
       offline_device_count: 	 <p>The number of devices that have this model version and do not have a heart beat.</p>
       connected_device_count: 	 <p>The number of devices that have this model version and have a heart beat. </p>
       active_device_count: 	 <p>The number of devices that have this model version, a heart beat, and are currently running.</p>
       sampling_device_count: 	 <p>The number of devices with this model version and are producing sample data.</p>
    """

    model_name: str
    model_version: str
    offline_device_count: int
    connected_device_count: int
    active_device_count: int
    sampling_device_count: int


class EdgePackagingJobSummary(Base):
    """
    EdgePackagingJobSummary
         <p>Summary of edge packaging job.</p>

        Attributes
       ----------------------
       edge_packaging_job_arn: 	 <p>The Amazon Resource Name (ARN) of the edge packaging job.</p>
       edge_packaging_job_name: 	 <p>The name of the edge packaging job.</p>
       edge_packaging_job_status: 	 <p>The status of the edge packaging job.</p>
       compilation_job_name: 	 <p>The name of the SageMaker Neo compilation job.</p>
       model_name: 	 <p>The name of the model.</p>
       model_version: 	 <p>The version of the model.</p>
       creation_time: 	 <p>The timestamp of when the job was created.</p>
       last_modified_time: 	 <p>The timestamp of when the edge packaging job was last updated.</p>
    """

    edge_packaging_job_arn: str
    edge_packaging_job_name: str
    edge_packaging_job_status: str
    compilation_job_name: Optional[str] = Unassigned()
    model_name: Optional[str] = Unassigned()
    model_version: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class MonitoringSchedule(Base):
    """
    MonitoringSchedule
         <p>A schedule for a model monitoring job. For information about model monitor, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html">Amazon SageMaker Model Monitor</a>.</p>

        Attributes
       ----------------------
       monitoring_schedule_arn: 	 <p>The Amazon Resource Name (ARN) of the monitoring schedule.</p>
       monitoring_schedule_name: 	 <p>The name of the monitoring schedule.</p>
       monitoring_schedule_status: 	 <p>The status of the monitoring schedule. This can be one of the following values.</p> <ul> <li> <p> <code>PENDING</code> - The schedule is pending being created.</p> </li> <li> <p> <code>FAILED</code> - The schedule failed.</p> </li> <li> <p> <code>SCHEDULED</code> - The schedule was successfully created.</p> </li> <li> <p> <code>STOPPED</code> - The schedule was stopped.</p> </li> </ul>
       monitoring_type: 	 <p>The type of the monitoring job definition to schedule.</p>
       failure_reason: 	 <p>If the monitoring schedule failed, the reason it failed.</p>
       creation_time: 	 <p>The time that the monitoring schedule was created.</p>
       last_modified_time: 	 <p>The last time the monitoring schedule was changed.</p>
       monitoring_schedule_config
       endpoint_name: 	 <p>The endpoint that hosts the model being monitored.</p>
       last_monitoring_execution_summary
       tags: 	 <p>A list of the tags associated with the monitoring schedlue. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a> in the <i>Amazon Web Services General Reference Guide</i>.</p>
    """

    monitoring_schedule_arn: Optional[str] = Unassigned()
    monitoring_schedule_name: Optional[str] = Unassigned()
    monitoring_schedule_status: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_config: Optional[MonitoringScheduleConfig] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = (
        Unassigned()
    )
    tags: Optional[List[Tag]] = Unassigned()


class Endpoint(Base):
    """
    Endpoint
         <p>A hosted endpoint for real-time inference.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of the endpoint.</p>
       endpoint_arn: 	 <p>The Amazon Resource Name (ARN) of the endpoint.</p>
       endpoint_config_name: 	 <p>The endpoint configuration associated with the endpoint.</p>
       production_variants: 	 <p>A list of the production variants hosted on the endpoint. Each production variant is a model.</p>
       data_capture_config
       endpoint_status: 	 <p>The status of the endpoint.</p>
       failure_reason: 	 <p>If the endpoint failed, the reason it failed.</p>
       creation_time: 	 <p>The time that the endpoint was created.</p>
       last_modified_time: 	 <p>The last time the endpoint was modified.</p>
       monitoring_schedules: 	 <p>A list of monitoring schedules for the endpoint. For information about model monitoring, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html">Amazon SageMaker Model Monitor</a>.</p>
       tags: 	 <p>A list of the tags associated with the endpoint. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a> in the <i>Amazon Web Services General Reference Guide</i>.</p>
       shadow_production_variants: 	 <p>A list of the shadow variants hosted on the endpoint. Each shadow variant is a model in shadow mode with production traffic replicated from the production variant.</p>
    """

    endpoint_name: str
    endpoint_arn: str
    endpoint_config_name: str
    endpoint_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()
    data_capture_config: Optional[DataCaptureConfigSummary] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    monitoring_schedules: Optional[List[MonitoringSchedule]] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    shadow_production_variants: Optional[List[ProductionVariantSummary]] = Unassigned()


class EndpointConfigSummary(Base):
    """
    EndpointConfigSummary
         <p>Provides summary information for an endpoint configuration.</p>

        Attributes
       ----------------------
       endpoint_config_name: 	 <p>The name of the endpoint configuration.</p>
       endpoint_config_arn: 	 <p>The Amazon Resource Name (ARN) of the endpoint configuration.</p>
       creation_time: 	 <p>A timestamp that shows when the endpoint configuration was created.</p>
    """

    endpoint_config_name: str
    endpoint_config_arn: str
    creation_time: datetime.datetime


class EndpointSummary(Base):
    """
    EndpointSummary
         <p>Provides summary information for an endpoint.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The name of the endpoint.</p>
       endpoint_arn: 	 <p>The Amazon Resource Name (ARN) of the endpoint.</p>
       creation_time: 	 <p>A timestamp that shows when the endpoint was created.</p>
       last_modified_time: 	 <p>A timestamp that shows when the endpoint was last modified.</p>
       endpoint_status: 	 <p>The status of the endpoint.</p> <ul> <li> <p> <code>OutOfService</code>: Endpoint is not available to take incoming requests.</p> </li> <li> <p> <code>Creating</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpoint.html">CreateEndpoint</a> is executing.</p> </li> <li> <p> <code>Updating</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html">UpdateEndpoint</a> or <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> is executing.</p> </li> <li> <p> <code>SystemUpdating</code>: Endpoint is undergoing maintenance and cannot be updated or deleted or re-scaled until it has completed. This maintenance operation does not change any customer-specified values such as VPC config, KMS encryption, model, instance type, or instance count.</p> </li> <li> <p> <code>RollingBack</code>: Endpoint fails to scale up or down or change its variant weight and is in the process of rolling back to its previous configuration. Once the rollback completes, endpoint returns to an <code>InService</code> status. This transitional status only applies to an endpoint that has autoscaling enabled and is undergoing variant weight or capacity changes as part of an <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> call or when the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpointWeightsAndCapacities.html">UpdateEndpointWeightsAndCapacities</a> operation is called explicitly.</p> </li> <li> <p> <code>InService</code>: Endpoint is available to process incoming requests.</p> </li> <li> <p> <code>Deleting</code>: <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DeleteEndpoint.html">DeleteEndpoint</a> is executing.</p> </li> <li> <p> <code>Failed</code>: Endpoint could not be created, updated, or re-scaled. Use <code>DescribeEndpointOutput$FailureReason</code> for information about the failure. <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DeleteEndpoint.html">DeleteEndpoint</a> is the only operation that can be performed on a failed endpoint.</p> </li> </ul> <p>To get a list of endpoints with a specified status, use the <code>StatusEquals</code> filter with a call to <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ListEndpoints.html">ListEndpoints</a>.</p>
    """

    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_status: str


class Experiment(Base):
    """
    Experiment
         <p>The properties of an experiment as returned by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p>

        Attributes
       ----------------------
       experiment_name: 	 <p>The name of the experiment.</p>
       experiment_arn: 	 <p>The Amazon Resource Name (ARN) of the experiment.</p>
       display_name: 	 <p>The name of the experiment as displayed. If <code>DisplayName</code> isn't specified, <code>ExperimentName</code> is displayed.</p>
       source
       description: 	 <p>The description of the experiment.</p>
       creation_time: 	 <p>When the experiment was created.</p>
       created_by: 	 <p>Who created the experiment.</p>
       last_modified_time: 	 <p>When the experiment was last modified.</p>
       last_modified_by
       tags: 	 <p>The list of tags that are associated with the experiment. You can use <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API to search on the tags.</p>
    """

    experiment_name: Optional[str] = Unassigned()
    experiment_arn: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    source: Optional[ExperimentSource] = Unassigned()
    description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()


class ExperimentSummary(Base):
    """
    ExperimentSummary
         <p>A summary of the properties of an experiment. To get the complete set of properties, call the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeExperiment.html">DescribeExperiment</a> API and provide the <code>ExperimentName</code>.</p>

        Attributes
       ----------------------
       experiment_arn: 	 <p>The Amazon Resource Name (ARN) of the experiment.</p>
       experiment_name: 	 <p>The name of the experiment.</p>
       display_name: 	 <p>The name of the experiment as displayed. If <code>DisplayName</code> isn't specified, <code>ExperimentName</code> is displayed.</p>
       experiment_source
       creation_time: 	 <p>When the experiment was created.</p>
       last_modified_time: 	 <p>When the experiment was last modified.</p>
    """

    experiment_arn: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    experiment_source: Optional[ExperimentSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class FailStepMetadata(Base):
    """
    FailStepMetadata
         <p>The container for the metadata for Fail step.</p>

        Attributes
       ----------------------
       error_message: 	 <p>A message that you define and then is processed and rendered by the Fail step when the error occurs.</p>
    """

    error_message: Optional[str] = Unassigned()


class FeatureGroup(Base):
    """
    FeatureGroup
         <p>Amazon SageMaker Feature Store stores features in a collection called Feature Group. A Feature Group can be visualized as a table which has rows, with a unique identifier for each row where each column in the table is a feature. In principle, a Feature Group is composed of features and values per features.</p>

        Attributes
       ----------------------
       feature_group_arn: 	 <p>The Amazon Resource Name (ARN) of a <code>FeatureGroup</code>.</p>
       feature_group_name: 	 <p>The name of the <code>FeatureGroup</code>.</p>
       record_identifier_feature_name: 	 <p>The name of the <code>Feature</code> whose value uniquely identifies a <code>Record</code> defined in the <code>FeatureGroup</code> <code>FeatureDefinitions</code>.</p>
       event_time_feature_name: 	 <p>The name of the feature that stores the <code>EventTime</code> of a Record in a <code>FeatureGroup</code>.</p> <p>A <code>EventTime</code> is point in time when a new event occurs that corresponds to the creation or update of a <code>Record</code> in <code>FeatureGroup</code>. All <code>Records</code> in the <code>FeatureGroup</code> must have a corresponding <code>EventTime</code>.</p>
       feature_definitions: 	 <p>A list of <code>Feature</code>s. Each <code>Feature</code> must include a <code>FeatureName</code> and a <code>FeatureType</code>. </p> <p>Valid <code>FeatureType</code>s are <code>Integral</code>, <code>Fractional</code> and <code>String</code>. </p> <p> <code>FeatureName</code>s cannot be any of the following: <code>is_deleted</code>, <code>write_time</code>, <code>api_invocation_time</code>.</p> <p>You can create up to 2,500 <code>FeatureDefinition</code>s per <code>FeatureGroup</code>.</p>
       creation_time: 	 <p>The time a <code>FeatureGroup</code> was created.</p>
       last_modified_time: 	 <p>A timestamp indicating the last time you updated the feature group.</p>
       online_store_config
       offline_store_config
       role_arn: 	 <p>The Amazon Resource Name (ARN) of the IAM execution role used to create the feature group.</p>
       feature_group_status: 	 <p>A <code>FeatureGroup</code> status.</p>
       offline_store_status
       last_update_status: 	 <p>A value that indicates whether the feature group was updated successfully.</p>
       failure_reason: 	 <p>The reason that the <code>FeatureGroup</code> failed to be replicated in the <code>OfflineStore</code>. This is failure may be due to a failure to create a <code>FeatureGroup</code> in or delete a <code>FeatureGroup</code> from the <code>OfflineStore</code>.</p>
       description: 	 <p>A free form description of a <code>FeatureGroup</code>.</p>
       tags: 	 <p>Tags used to define a <code>FeatureGroup</code>.</p>
    """

    feature_group_arn: Optional[str] = Unassigned()
    feature_group_name: Optional[str] = Unassigned()
    record_identifier_feature_name: Optional[str] = Unassigned()
    event_time_feature_name: Optional[str] = Unassigned()
    feature_definitions: Optional[List[FeatureDefinition]] = Unassigned()
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
    tags: Optional[List[Tag]] = Unassigned()


class FeatureGroupSummary(Base):
    """
    FeatureGroupSummary
         <p>The name, ARN, <code>CreationTime</code>, <code>FeatureGroup</code> values, <code>LastUpdatedTime</code> and <code>EnableOnlineStorage</code> status of a <code>FeatureGroup</code>.</p>

        Attributes
       ----------------------
       feature_group_name: 	 <p>The name of <code>FeatureGroup</code>.</p>
       feature_group_arn: 	 <p>Unique identifier for the <code>FeatureGroup</code>.</p>
       creation_time: 	 <p>A timestamp indicating the time of creation time of the <code>FeatureGroup</code>.</p>
       feature_group_status: 	 <p>The status of a FeatureGroup. The status can be any of the following: <code>Creating</code>, <code>Created</code>, <code>CreateFail</code>, <code>Deleting</code> or <code>DetailFail</code>. </p>
       offline_store_status: 	 <p>Notifies you if replicating data into the <code>OfflineStore</code> has failed. Returns either: <code>Active</code> or <code>Blocked</code>.</p>
    """

    feature_group_name: str
    feature_group_arn: str
    creation_time: datetime.datetime
    feature_group_status: Optional[str] = Unassigned()
    offline_store_status: Optional[OfflineStoreStatus] = Unassigned()


class FeatureMetadata(Base):
    """
    FeatureMetadata
         <p>The metadata for a feature. It can either be metadata that you specify, or metadata that is updated automatically.</p>

        Attributes
       ----------------------
       feature_group_arn: 	 <p>The Amazon Resource Number (ARN) of the feature group.</p>
       feature_group_name: 	 <p>The name of the feature group containing the feature.</p>
       feature_name: 	 <p>The name of feature.</p>
       feature_type: 	 <p>The data type of the feature.</p>
       creation_time: 	 <p>A timestamp indicating when the feature was created.</p>
       last_modified_time: 	 <p>A timestamp indicating when the feature was last modified.</p>
       description: 	 <p>An optional description that you specify to better describe the feature.</p>
       parameters: 	 <p>Optional key-value pairs that you specify to better describe the feature.</p>
    """

    feature_group_arn: Optional[str] = Unassigned()
    feature_group_name: Optional[str] = Unassigned()
    feature_name: Optional[str] = Unassigned()
    feature_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    description: Optional[str] = Unassigned()
    parameters: Optional[List[FeatureParameter]] = Unassigned()


class Filter(Base):
    """
    Filter
         <p>A conditional statement for a search expression that includes a resource property, a Boolean operator, and a value. Resources that match the statement are returned in the results from the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p> <p>If you specify a <code>Value</code>, but not an <code>Operator</code>, SageMaker uses the equals operator.</p> <p>In search, there are several property types:</p> <dl> <dt>Metrics</dt> <dd> <p>To define a metric filter, enter a value using the form <code>"Metrics.&lt;name&gt;"</code>, where <code>&lt;name&gt;</code> is a metric name. For example, the following filter searches for training jobs with an <code>"accuracy"</code> metric greater than <code>"0.9"</code>:</p> <p> <code>{</code> </p> <p> <code>"Name": "Metrics.accuracy",</code> </p> <p> <code>"Operator": "GreaterThan",</code> </p> <p> <code>"Value": "0.9"</code> </p> <p> <code>}</code> </p> </dd> <dt>HyperParameters</dt> <dd> <p>To define a hyperparameter filter, enter a value with the form <code>"HyperParameters.&lt;name&gt;"</code>. Decimal hyperparameter values are treated as a decimal in a comparison if the specified <code>Value</code> is also a decimal value. If the specified <code>Value</code> is an integer, the decimal hyperparameter values are treated as integers. For example, the following filter is satisfied by training jobs with a <code>"learning_rate"</code> hyperparameter that is less than <code>"0.5"</code>:</p> <p> <code> {</code> </p> <p> <code> "Name": "HyperParameters.learning_rate",</code> </p> <p> <code> "Operator": "LessThan",</code> </p> <p> <code> "Value": "0.5"</code> </p> <p> <code> }</code> </p> </dd> <dt>Tags</dt> <dd> <p>To define a tag filter, enter a value with the form <code>Tags.&lt;key&gt;</code>.</p> </dd> </dl>

        Attributes
       ----------------------
       name: 	 <p>A resource property name. For example, <code>TrainingJobName</code>. For valid property names, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_SearchRecord.html">SearchRecord</a>. You must specify a valid property for the resource.</p>
       operator: 	 <p>A Boolean binary operator that is used to evaluate the filter. The operator field contains one of the following values:</p> <dl> <dt>Equals</dt> <dd> <p>The value of <code>Name</code> equals <code>Value</code>.</p> </dd> <dt>NotEquals</dt> <dd> <p>The value of <code>Name</code> doesn't equal <code>Value</code>.</p> </dd> <dt>Exists</dt> <dd> <p>The <code>Name</code> property exists.</p> </dd> <dt>NotExists</dt> <dd> <p>The <code>Name</code> property does not exist.</p> </dd> <dt>GreaterThan</dt> <dd> <p>The value of <code>Name</code> is greater than <code>Value</code>. Not supported for text properties.</p> </dd> <dt>GreaterThanOrEqualTo</dt> <dd> <p>The value of <code>Name</code> is greater than or equal to <code>Value</code>. Not supported for text properties.</p> </dd> <dt>LessThan</dt> <dd> <p>The value of <code>Name</code> is less than <code>Value</code>. Not supported for text properties.</p> </dd> <dt>LessThanOrEqualTo</dt> <dd> <p>The value of <code>Name</code> is less than or equal to <code>Value</code>. Not supported for text properties.</p> </dd> <dt>In</dt> <dd> <p>The value of <code>Name</code> is one of the comma delimited strings in <code>Value</code>. Only supported for text properties.</p> </dd> <dt>Contains</dt> <dd> <p>The value of <code>Name</code> contains the string <code>Value</code>. Only supported for text properties.</p> <p>A <code>SearchExpression</code> can include the <code>Contains</code> operator multiple times when the value of <code>Name</code> is one of the following:</p> <ul> <li> <p> <code>Experiment.DisplayName</code> </p> </li> <li> <p> <code>Experiment.ExperimentName</code> </p> </li> <li> <p> <code>Experiment.Tags</code> </p> </li> <li> <p> <code>Trial.DisplayName</code> </p> </li> <li> <p> <code>Trial.TrialName</code> </p> </li> <li> <p> <code>Trial.Tags</code> </p> </li> <li> <p> <code>TrialComponent.DisplayName</code> </p> </li> <li> <p> <code>TrialComponent.TrialComponentName</code> </p> </li> <li> <p> <code>TrialComponent.Tags</code> </p> </li> <li> <p> <code>TrialComponent.InputArtifacts</code> </p> </li> <li> <p> <code>TrialComponent.OutputArtifacts</code> </p> </li> </ul> <p>A <code>SearchExpression</code> can include only one <code>Contains</code> operator for all other values of <code>Name</code>. In these cases, if you include multiple <code>Contains</code> operators in the <code>SearchExpression</code>, the result is the following error message: "<code>'CONTAINS' operator usage limit of 1 exceeded.</code>"</p> </dd> </dl>
       value: 	 <p>A value used with <code>Name</code> and <code>Operator</code> to determine which resources satisfy the filter's condition. For numerical properties, <code>Value</code> must be an integer or floating-point decimal. For timestamp properties, <code>Value</code> must be an ISO 8601 date-time string of the following format: <code>YYYY-mm-dd'T'HH:MM:SS</code>.</p>
    """

    name: str
    operator: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


class FlowDefinitionSummary(Base):
    """
    FlowDefinitionSummary
         <p>Contains summary information about the flow definition.</p>

        Attributes
       ----------------------
       flow_definition_name: 	 <p>The name of the flow definition.</p>
       flow_definition_arn: 	 <p>The Amazon Resource Name (ARN) of the flow definition.</p>
       flow_definition_status: 	 <p>The status of the flow definition. Valid values:</p>
       creation_time: 	 <p>The timestamp when SageMaker created the flow definition.</p>
       failure_reason: 	 <p>The reason why the flow definition creation failed. A failure reason is returned only when the flow definition status is <code>Failed</code>.</p>
    """

    flow_definition_name: str
    flow_definition_arn: str
    flow_definition_status: str
    creation_time: datetime.datetime
    failure_reason: Optional[str] = Unassigned()


class ScalingPolicyObjective(Base):
    """
    ScalingPolicyObjective
         <p>An object where you specify the anticipated traffic pattern for an endpoint.</p>

        Attributes
       ----------------------
       min_invocations_per_minute: 	 <p>The minimum number of expected requests to your endpoint per minute.</p>
       max_invocations_per_minute: 	 <p>The maximum number of expected requests to your endpoint per minute.</p>
    """

    min_invocations_per_minute: Optional[int] = Unassigned()
    max_invocations_per_minute: Optional[int] = Unassigned()


class ScalingPolicyMetric(Base):
    """
    ScalingPolicyMetric
         <p>The metric for a scaling policy.</p>

        Attributes
       ----------------------
       invocations_per_instance: 	 <p>The number of invocations sent to a model, normalized by <code>InstanceCount</code> in each ProductionVariant. <code>1/numberOfInstances</code> is sent as the value on each request, where <code>numberOfInstances</code> is the number of active instances for the ProductionVariant behind the endpoint at the time of the request.</p>
       model_latency: 	 <p>The interval of time taken by a model to respond as viewed from SageMaker. This interval includes the local communication times taken to send the request and to fetch the response from the container of a model and the time taken to complete the inference in the container.</p>
    """

    invocations_per_instance: Optional[int] = Unassigned()
    model_latency: Optional[int] = Unassigned()


class PropertyNameQuery(Base):
    """
    PropertyNameQuery
         <p>Part of the <code>SuggestionQuery</code> type. Specifies a hint for retrieving property names that begin with the specified text.</p>

        Attributes
       ----------------------
       property_name_hint: 	 <p>Text that begins a property's name.</p>
    """

    property_name_hint: str


class SuggestionQuery(Base):
    """
    SuggestionQuery
         <p>Specified in the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_GetSearchSuggestions.html">GetSearchSuggestions</a> request. Limits the property names that are included in the response.</p>

        Attributes
       ----------------------
       property_name_query: 	 <p>Defines a property name hint. Only property names that begin with the specified hint are included in the response.</p>
    """

    property_name_query: Optional[PropertyNameQuery] = Unassigned()


class PropertyNameSuggestion(Base):
    """
    PropertyNameSuggestion
         <p>A property name returned from a <code>GetSearchSuggestions</code> call that specifies a value in the <code>PropertyNameQuery</code> field.</p>

        Attributes
       ----------------------
       property_name: 	 <p>A suggested property name based on what you entered in the search textbox in the SageMaker console.</p>
    """

    property_name: Optional[str] = Unassigned()


class GitConfigForUpdate(Base):
    """
    GitConfigForUpdate
         <p>Specifies configuration details for a Git repository when the repository is updated.</p>

        Attributes
       ----------------------
       secret_arn: 	 <p>The Amazon Resource Name (ARN) of the Amazon Web Services Secrets Manager secret that contains the credentials used to access the git repository. The secret must have a staging label of <code>AWSCURRENT</code> and must be in the following format:</p> <p> <code>{"username": <i>UserName</i>, "password": <i>Password</i>}</code> </p>
    """

    secret_arn: Optional[str] = Unassigned()


class HubContentInfo(Base):
    """
    HubContentInfo
         <p>Information about hub content.</p>

        Attributes
       ----------------------
       hub_content_name: 	 <p>The name of the hub content.</p>
       hub_content_arn: 	 <p>The Amazon Resource Name (ARN) of the hub content.</p>
       hub_content_version: 	 <p>The version of the hub content.</p>
       hub_content_type: 	 <p>The type of hub content.</p>
       document_schema_version: 	 <p>The version of the hub content document schema.</p>
       hub_content_display_name: 	 <p>The display name of the hub content.</p>
       hub_content_description: 	 <p>A description of the hub content.</p>
       hub_content_search_keywords: 	 <p>The searchable keywords for the hub content.</p>
       hub_content_status: 	 <p>The status of the hub content.</p>
       creation_time: 	 <p>The date and time that the hub content was created.</p>
    """

    hub_content_name: str
    hub_content_arn: str
    hub_content_version: str
    hub_content_type: str
    document_schema_version: str
    hub_content_status: str
    creation_time: datetime.datetime
    hub_content_display_name: Optional[str] = Unassigned()
    hub_content_description: Optional[str] = Unassigned()
    hub_content_search_keywords: Optional[List[str]] = Unassigned()


class HubInfo(Base):
    """
    HubInfo
         <p>Information about a hub.</p>

        Attributes
       ----------------------
       hub_name: 	 <p>The name of the hub.</p>
       hub_arn: 	 <p>The Amazon Resource Name (ARN) of the hub.</p>
       hub_display_name: 	 <p>The display name of the hub.</p>
       hub_description: 	 <p>A description of the hub.</p>
       hub_search_keywords: 	 <p>The searchable keywords for the hub.</p>
       hub_status: 	 <p>The status of the hub.</p>
       creation_time: 	 <p>The date and time that the hub was created.</p>
       last_modified_time: 	 <p>The date and time that the hub was last modified.</p>
    """

    hub_name: str
    hub_arn: str
    hub_status: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    hub_display_name: Optional[str] = Unassigned()
    hub_description: Optional[str] = Unassigned()
    hub_search_keywords: Optional[List[str]] = Unassigned()


class HumanTaskUiSummary(Base):
    """
    HumanTaskUiSummary
         <p>Container for human task user interface information.</p>

        Attributes
       ----------------------
       human_task_ui_name: 	 <p>The name of the human task user interface.</p>
       human_task_ui_arn: 	 <p>The Amazon Resource Name (ARN) of the human task user interface.</p>
       creation_time: 	 <p>A timestamp when SageMaker created the human task user interface.</p>
    """

    human_task_ui_name: str
    human_task_ui_arn: str
    creation_time: datetime.datetime


class HyperParameterTuningJobSearchEntity(Base):
    """
    HyperParameterTuningJobSearchEntity
         <p>An entity returned by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_SearchRecord.html">SearchRecord</a> API containing the properties of a hyperparameter tuning job.</p>

        Attributes
       ----------------------
       hyper_parameter_tuning_job_name: 	 <p>The name of a hyperparameter tuning job.</p>
       hyper_parameter_tuning_job_arn: 	 <p>The Amazon Resource Name (ARN) of a hyperparameter tuning job.</p>
       hyper_parameter_tuning_job_config
       training_job_definition
       training_job_definitions: 	 <p>The job definitions included in a hyperparameter tuning job.</p>
       hyper_parameter_tuning_job_status: 	 <p>The status of a hyperparameter tuning job.</p>
       creation_time: 	 <p>The time that a hyperparameter tuning job was created.</p>
       hyper_parameter_tuning_end_time: 	 <p>The time that a hyperparameter tuning job ended.</p>
       last_modified_time: 	 <p>The time that a hyperparameter tuning job was last modified.</p>
       training_job_status_counters
       objective_status_counters
       best_training_job
       overall_best_training_job
       warm_start_config
       failure_reason: 	 <p>The error that was created when a hyperparameter tuning job failed.</p>
       tuning_job_completion_details: 	 <p>Information about either a current or completed hyperparameter tuning job.</p>
       consumed_resources: 	 <p>The total amount of resources consumed by a hyperparameter tuning job.</p>
       tags: 	 <p>The tags associated with a hyperparameter tuning job. For more information see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a>.</p>
    """

    hyper_parameter_tuning_job_name: Optional[str] = Unassigned()
    hyper_parameter_tuning_job_arn: Optional[str] = Unassigned()
    hyper_parameter_tuning_job_config: Optional[HyperParameterTuningJobConfig] = (
        Unassigned()
    )
    training_job_definition: Optional[HyperParameterTrainingJobDefinition] = (
        Unassigned()
    )
    training_job_definitions: Optional[List[HyperParameterTrainingJobDefinition]] = (
        Unassigned()
    )
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
    tuning_job_completion_details: Optional[
        HyperParameterTuningJobCompletionDetails
    ] = Unassigned()
    consumed_resources: Optional[HyperParameterTuningJobConsumedResources] = (
        Unassigned()
    )
    tags: Optional[List[Tag]] = Unassigned()


class HyperParameterTuningJobSummary(Base):
    """
    HyperParameterTuningJobSummary
         <p>Provides summary information about a hyperparameter tuning job.</p>

        Attributes
       ----------------------
       hyper_parameter_tuning_job_name: 	 <p>The name of the tuning job.</p>
       hyper_parameter_tuning_job_arn: 	 <p>The Amazon Resource Name (ARN) of the tuning job.</p>
       hyper_parameter_tuning_job_status: 	 <p>The status of the tuning job.</p>
       strategy: 	 <p>Specifies the search strategy hyperparameter tuning uses to choose which hyperparameters to evaluate at each iteration.</p>
       creation_time: 	 <p>The date and time that the tuning job was created.</p>
       hyper_parameter_tuning_end_time: 	 <p>The date and time that the tuning job ended.</p>
       last_modified_time: 	 <p>The date and time that the tuning job was modified.</p>
       training_job_status_counters: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_TrainingJobStatusCounters.html">TrainingJobStatusCounters</a> object that specifies the numbers of training jobs, categorized by status, that this tuning job launched.</p>
       objective_status_counters: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ObjectiveStatusCounters.html">ObjectiveStatusCounters</a> object that specifies the numbers of training jobs, categorized by objective metric status, that this tuning job launched.</p>
       resource_limits: 	 <p>The <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ResourceLimits.html">ResourceLimits</a> object that specifies the maximum number of training jobs and parallel training jobs allowed for this tuning job.</p>
    """

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


class Image(Base):
    """
    Image
         <p>A SageMaker image. A SageMaker image represents a set of container images that are derived from a common base container image. Each of these container images is represented by a SageMaker <code>ImageVersion</code>.</p>

        Attributes
       ----------------------
       creation_time: 	 <p>When the image was created.</p>
       description: 	 <p>The description of the image.</p>
       display_name: 	 <p>The name of the image as displayed.</p>
       failure_reason: 	 <p>When a create, update, or delete operation fails, the reason for the failure.</p>
       image_arn: 	 <p>The ARN of the image.</p>
       image_name: 	 <p>The name of the image.</p>
       image_status: 	 <p>The status of the image.</p>
       last_modified_time: 	 <p>When the image was last modified.</p>
    """

    creation_time: datetime.datetime
    image_arn: str
    image_name: str
    image_status: str
    last_modified_time: datetime.datetime
    description: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


class ImageVersion(Base):
    """
    ImageVersion
         <p>A version of a SageMaker <code>Image</code>. A version represents an existing container image.</p>

        Attributes
       ----------------------
       creation_time: 	 <p>When the version was created.</p>
       failure_reason: 	 <p>When a create or delete operation fails, the reason for the failure.</p>
       image_arn: 	 <p>The ARN of the image the version is based on.</p>
       image_version_arn: 	 <p>The ARN of the version.</p>
       image_version_status: 	 <p>The status of the version.</p>
       last_modified_time: 	 <p>When the version was last modified.</p>
       version: 	 <p>The version number.</p>
    """

    creation_time: datetime.datetime
    image_arn: str
    image_version_arn: str
    image_version_status: str
    last_modified_time: datetime.datetime
    version: int
    failure_reason: Optional[str] = Unassigned()


class InferenceComponentSummary(Base):
    """
    InferenceComponentSummary
         <p>A summary of the properties of an inference component.</p>

        Attributes
       ----------------------
       creation_time: 	 <p>The time when the inference component was created.</p>
       inference_component_arn: 	 <p>The Amazon Resource Name (ARN) of the inference component.</p>
       inference_component_name: 	 <p>The name of the inference component.</p>
       endpoint_arn: 	 <p>The Amazon Resource Name (ARN) of the endpoint that hosts the inference component.</p>
       endpoint_name: 	 <p>The name of the endpoint that hosts the inference component.</p>
       variant_name: 	 <p>The name of the production variant that hosts the inference component.</p>
       inference_component_status: 	 <p>The status of the inference component.</p>
       last_modified_time: 	 <p>The time when the inference component was last updated.</p>
    """

    creation_time: datetime.datetime
    inference_component_arn: str
    inference_component_name: str
    endpoint_arn: str
    endpoint_name: str
    variant_name: str
    last_modified_time: datetime.datetime
    inference_component_status: Optional[str] = Unassigned()


class InferenceExperimentSummary(Base):
    """
    InferenceExperimentSummary
         <p>Lists a summary of properties of an inference experiment.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the inference experiment.</p>
       type: 	 <p>The type of the inference experiment.</p>
       schedule: 	 <p>The duration for which the inference experiment ran or will run.</p> <p>The maximum duration that you can set for an inference experiment is 30 days.</p>
       status: 	 <p>The status of the inference experiment.</p>
       status_reason: 	 <p>The error message for the inference experiment status result.</p>
       description: 	 <p>The description of the inference experiment.</p>
       creation_time: 	 <p>The timestamp at which the inference experiment was created.</p>
       completion_time: 	 <p>The timestamp at which the inference experiment was completed.</p>
       last_modified_time: 	 <p>The timestamp when you last modified the inference experiment.</p>
       role_arn: 	 <p> The ARN of the IAM role that Amazon SageMaker can assume to access model artifacts and container images, and manage Amazon SageMaker Inference endpoints for model deployment. </p>
    """

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


class InferenceRecommendationsJob(Base):
    """
    InferenceRecommendationsJob
         <p>A structure that contains a list of recommendation jobs.</p>

        Attributes
       ----------------------
       job_name: 	 <p>The name of the job.</p>
       job_description: 	 <p>The job description.</p>
       job_type: 	 <p>The recommendation job type.</p>
       job_arn: 	 <p>The Amazon Resource Name (ARN) of the recommendation job.</p>
       status: 	 <p>The status of the job.</p>
       creation_time: 	 <p>A timestamp that shows when the job was created.</p>
       completion_time: 	 <p>A timestamp that shows when the job completed.</p>
       role_arn: 	 <p>The Amazon Resource Name (ARN) of an IAM role that enables Amazon SageMaker to perform tasks on your behalf.</p>
       last_modified_time: 	 <p>A timestamp that shows when the job was last modified.</p>
       failure_reason: 	 <p>If the job fails, provides information why the job failed.</p>
       model_name: 	 <p>The name of the created model.</p>
       sample_payload_url: 	 <p>The Amazon Simple Storage Service (Amazon S3) path where the sample payload is stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix).</p>
       model_package_version_arn: 	 <p>The Amazon Resource Name (ARN) of a versioned model package.</p>
    """

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


class RecommendationJobInferenceBenchmark(Base):
    """
    RecommendationJobInferenceBenchmark
         <p>The details for a specific benchmark from an Inference Recommender job.</p>

        Attributes
       ----------------------
       metrics
       endpoint_metrics
       endpoint_configuration
       model_configuration
       failure_reason: 	 <p>The reason why a benchmark failed.</p>
       invocation_end_time: 	 <p>A timestamp that shows when the benchmark completed.</p>
       invocation_start_time: 	 <p>A timestamp that shows when the benchmark started.</p>
    """

    model_configuration: ModelConfiguration
    metrics: Optional[RecommendationMetrics] = Unassigned()
    endpoint_metrics: Optional[InferenceMetrics] = Unassigned()
    endpoint_configuration: Optional[EndpointOutputConfiguration] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    invocation_end_time: Optional[datetime.datetime] = Unassigned()
    invocation_start_time: Optional[datetime.datetime] = Unassigned()


class InferenceRecommendationsJobStep(Base):
    """
    InferenceRecommendationsJobStep
         <p>A returned array object for the <code>Steps</code> response field in the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ListInferenceRecommendationsJobSteps.html">ListInferenceRecommendationsJobSteps</a> API command.</p>

        Attributes
       ----------------------
       step_type: 	 <p>The type of the subtask.</p> <p> <code>BENCHMARK</code>: Evaluate the performance of your model on different instance types.</p>
       job_name: 	 <p>The name of the Inference Recommender job.</p>
       status: 	 <p>The current status of the benchmark.</p>
       inference_benchmark: 	 <p>The details for a specific benchmark.</p>
    """

    step_type: str
    job_name: str
    status: str
    inference_benchmark: Optional[RecommendationJobInferenceBenchmark] = Unassigned()


class LabelCountersForWorkteam(Base):
    """
    LabelCountersForWorkteam
         <p>Provides counts for human-labeled tasks in the labeling job.</p>

        Attributes
       ----------------------
       human_labeled: 	 <p>The total number of data objects labeled by a human worker.</p>
       pending_human: 	 <p>The total number of data objects that need to be labeled by a human worker.</p>
       total: 	 <p>The total number of tasks in the labeling job.</p>
    """

    human_labeled: Optional[int] = Unassigned()
    pending_human: Optional[int] = Unassigned()
    total: Optional[int] = Unassigned()


class LabelingJobForWorkteamSummary(Base):
    """
    LabelingJobForWorkteamSummary
         <p>Provides summary information for a work team.</p>

        Attributes
       ----------------------
       labeling_job_name: 	 <p>The name of the labeling job that the work team is assigned to.</p>
       job_reference_code: 	 <p>A unique identifier for a labeling job. You can use this to refer to a specific labeling job.</p>
       work_requester_account_id: 	 <p>The Amazon Web Services account ID of the account used to start the labeling job.</p>
       creation_time: 	 <p>The date and time that the labeling job was created.</p>
       label_counters: 	 <p>Provides information about the progress of a labeling job.</p>
       number_of_human_workers_per_data_object: 	 <p>The configured number of workers per data object.</p>
    """

    job_reference_code: str
    work_requester_account_id: str
    creation_time: datetime.datetime
    labeling_job_name: Optional[str] = Unassigned()
    label_counters: Optional[LabelCountersForWorkteam] = Unassigned()
    number_of_human_workers_per_data_object: Optional[int] = Unassigned()


class LabelingJobSummary(Base):
    """
    LabelingJobSummary
         <p>Provides summary information about a labeling job.</p>

        Attributes
       ----------------------
       labeling_job_name: 	 <p>The name of the labeling job.</p>
       labeling_job_arn: 	 <p>The Amazon Resource Name (ARN) assigned to the labeling job when it was created.</p>
       creation_time: 	 <p>The date and time that the job was created (timestamp).</p>
       last_modified_time: 	 <p>The date and time that the job was last modified (timestamp).</p>
       labeling_job_status: 	 <p>The current status of the labeling job. </p>
       label_counters: 	 <p>Counts showing the progress of the labeling job.</p>
       workteam_arn: 	 <p>The Amazon Resource Name (ARN) of the work team assigned to the job.</p>
       pre_human_task_lambda_arn: 	 <p>The Amazon Resource Name (ARN) of a Lambda function. The function is run before each data object is sent to a worker.</p>
       annotation_consolidation_lambda_arn: 	 <p>The Amazon Resource Name (ARN) of the Lambda function used to consolidate the annotations from individual workers into a label for a data object. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sms-annotation-consolidation.html">Annotation Consolidation</a>.</p>
       failure_reason: 	 <p>If the <code>LabelingJobStatus</code> field is <code>Failed</code>, this field contains a description of the error.</p>
       labeling_job_output: 	 <p>The location of the output produced by the labeling job.</p>
       input_config: 	 <p>Input configuration for the labeling job.</p>
    """

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


class LambdaStepMetadata(Base):
    """
    LambdaStepMetadata
         <p>Metadata for a Lambda step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the Lambda function that was run by this step execution.</p>
       output_parameters: 	 <p>A list of the output parameters of the Lambda step.</p>
    """

    arn: Optional[str] = Unassigned()
    output_parameters: Optional[List[OutputParameter]] = Unassigned()


class LineageGroupSummary(Base):
    """
    LineageGroupSummary
         <p>Lists a summary of the properties of a lineage group. A lineage group provides a group of shareable lineage entity resources.</p>

        Attributes
       ----------------------
       lineage_group_arn: 	 <p>The Amazon Resource Name (ARN) of the lineage group resource.</p>
       lineage_group_name: 	 <p>The name or Amazon Resource Name (ARN) of the lineage group.</p>
       display_name: 	 <p>The display name of the lineage group summary.</p>
       creation_time: 	 <p>The creation time of the lineage group summary.</p>
       last_modified_time: 	 <p>The last modified time of the lineage group summary.</p>
    """

    lineage_group_arn: Optional[str] = Unassigned()
    lineage_group_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class MonitoringJobDefinitionSummary(Base):
    """
    MonitoringJobDefinitionSummary
         <p>Summary information about a monitoring job.</p>

        Attributes
       ----------------------
       monitoring_job_definition_name: 	 <p>The name of the monitoring job.</p>
       monitoring_job_definition_arn: 	 <p>The Amazon Resource Name (ARN) of the monitoring job.</p>
       creation_time: 	 <p>The time that the monitoring job was created.</p>
       endpoint_name: 	 <p>The name of the endpoint that the job monitors.</p>
    """

    monitoring_job_definition_name: str
    monitoring_job_definition_arn: str
    creation_time: datetime.datetime
    endpoint_name: str


class ModelCardExportJobSummary(Base):
    """
    ModelCardExportJobSummary
         <p>The summary of the Amazon SageMaker Model Card export job.</p>

        Attributes
       ----------------------
       model_card_export_job_name: 	 <p>The name of the model card export job.</p>
       model_card_export_job_arn: 	 <p>The Amazon Resource Name (ARN) of the model card export job.</p>
       status: 	 <p>The completion status of the model card export job.</p>
       model_card_name: 	 <p>The name of the model card that the export job exports.</p>
       model_card_version: 	 <p>The version of the model card that the export job exports.</p>
       created_at: 	 <p>The date and time that the model card export job was created.</p>
       last_modified_at: 	 <p>The date and time that the model card export job was last modified..</p>
    """

    model_card_export_job_name: str
    model_card_export_job_arn: str
    status: str
    model_card_name: str
    model_card_version: int
    created_at: datetime.datetime
    last_modified_at: datetime.datetime


class ModelCardVersionSummary(Base):
    """
    ModelCardVersionSummary
         <p>A summary of a specific version of the model card.</p>

        Attributes
       ----------------------
       model_card_name: 	 <p>The name of the model card.</p>
       model_card_arn: 	 <p>The Amazon Resource Name (ARN) of the model card.</p>
       model_card_status: 	 <p>The approval status of the model card version within your organization. Different organizations might have different criteria for model card review and approval.</p> <ul> <li> <p> <code>Draft</code>: The model card is a work in progress.</p> </li> <li> <p> <code>PendingReview</code>: The model card is pending review.</p> </li> <li> <p> <code>Approved</code>: The model card is approved.</p> </li> <li> <p> <code>Archived</code>: The model card is archived. No more updates should be made to the model card, but it can still be exported.</p> </li> </ul>
       model_card_version: 	 <p>A version of the model card.</p>
       creation_time: 	 <p>The date and time that the model card version was created.</p>
       last_modified_time: 	 <p>The time date and time that the model card version was last modified.</p>
    """

    model_card_name: str
    model_card_arn: str
    model_card_status: str
    model_card_version: int
    creation_time: datetime.datetime
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class ModelCardSummary(Base):
    """
    ModelCardSummary
         <p>A summary of the model card.</p>

        Attributes
       ----------------------
       model_card_name: 	 <p>The name of the model card.</p>
       model_card_arn: 	 <p>The Amazon Resource Name (ARN) of the model card.</p>
       model_card_status: 	 <p>The approval status of the model card within your organization. Different organizations might have different criteria for model card review and approval.</p> <ul> <li> <p> <code>Draft</code>: The model card is a work in progress.</p> </li> <li> <p> <code>PendingReview</code>: The model card is pending review.</p> </li> <li> <p> <code>Approved</code>: The model card is approved.</p> </li> <li> <p> <code>Archived</code>: The model card is archived. No more updates should be made to the model card, but it can still be exported.</p> </li> </ul>
       creation_time: 	 <p>The date and time that the model card was created.</p>
       last_modified_time: 	 <p>The date and time that the model card was last modified.</p>
    """

    model_card_name: str
    model_card_arn: str
    model_card_status: str
    creation_time: datetime.datetime
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class ModelMetadataFilter(Base):
    """
    ModelMetadataFilter
         <p>Part of the search expression. You can specify the name and value (domain, task, framework, framework version, task, and model).</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the of the model to filter by.</p>
       value: 	 <p>The value to filter the model metadata.</p>
    """

    name: str
    value: str


class ModelMetadataSearchExpression(Base):
    """
    ModelMetadataSearchExpression
         <p>One or more filters that searches for the specified resource or resources in a search. All resource objects that satisfy the expression's condition are included in the search results</p>

        Attributes
       ----------------------
       filters: 	 <p>A list of filter objects.</p>
    """

    filters: Optional[List[ModelMetadataFilter]] = Unassigned()


class ModelMetadataSummary(Base):
    """
    ModelMetadataSummary
         <p>A summary of the model metadata.</p>

        Attributes
       ----------------------
       domain: 	 <p>The machine learning domain of the model.</p>
       framework: 	 <p>The machine learning framework of the model.</p>
       task: 	 <p>The machine learning task of the model.</p>
       model: 	 <p>The name of the model.</p>
       framework_version: 	 <p>The framework version of the model.</p>
    """

    domain: str
    framework: str
    task: str
    model: str
    framework_version: str


class ModelPackageGroupSummary(Base):
    """
    ModelPackageGroupSummary
         <p>Summary information about a model group.</p>

        Attributes
       ----------------------
       model_package_group_name: 	 <p>The name of the model group.</p>
       model_package_group_arn: 	 <p>The Amazon Resource Name (ARN) of the model group.</p>
       model_package_group_description: 	 <p>A description of the model group.</p>
       creation_time: 	 <p>The time that the model group was created.</p>
       model_package_group_status: 	 <p>The status of the model group.</p>
    """

    model_package_group_name: str
    model_package_group_arn: str
    creation_time: datetime.datetime
    model_package_group_status: str
    model_package_group_description: Optional[str] = Unassigned()


class ModelPackageSummary(Base):
    """
    ModelPackageSummary
         <p>Provides summary information about a model package.</p>

        Attributes
       ----------------------
       model_package_name: 	 <p>The name of the model package.</p>
       model_package_group_name: 	 <p>If the model package is a versioned model, the model group that the versioned model belongs to.</p>
       model_package_version: 	 <p>If the model package is a versioned model, the version of the model.</p>
       model_package_arn: 	 <p>The Amazon Resource Name (ARN) of the model package.</p>
       model_package_description: 	 <p>A brief description of the model package.</p>
       creation_time: 	 <p>A timestamp that shows when the model package was created.</p>
       model_package_status: 	 <p>The overall status of the model package.</p>
       model_approval_status: 	 <p>The approval status of the model. This can be one of the following values.</p> <ul> <li> <p> <code>APPROVED</code> - The model is approved</p> </li> <li> <p> <code>REJECTED</code> - The model is rejected.</p> </li> <li> <p> <code>PENDING_MANUAL_APPROVAL</code> - The model is waiting for manual approval.</p> </li> </ul>
    """

    model_package_arn: str
    creation_time: datetime.datetime
    model_package_status: str
    model_package_name: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    model_approval_status: Optional[str] = Unassigned()


class ModelSummary(Base):
    """
    ModelSummary
         <p>Provides summary information about a model.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the model that you want a summary for.</p>
       model_arn: 	 <p>The Amazon Resource Name (ARN) of the model.</p>
       creation_time: 	 <p>A timestamp that indicates when the model was created.</p>
    """

    model_name: str
    model_arn: str
    creation_time: datetime.datetime


class MonitoringAlertHistorySummary(Base):
    """
    MonitoringAlertHistorySummary
         <p>Provides summary information of an alert's history.</p>

        Attributes
       ----------------------
       monitoring_schedule_name: 	 <p>The name of a monitoring schedule.</p>
       monitoring_alert_name: 	 <p>The name of a monitoring alert.</p>
       creation_time: 	 <p>A timestamp that indicates when the first alert transition occurred in an alert history. An alert transition can be from status <code>InAlert</code> to <code>OK</code>, or from <code>OK</code> to <code>InAlert</code>.</p>
       alert_status: 	 <p>The current alert status of an alert.</p>
    """

    monitoring_schedule_name: str
    monitoring_alert_name: str
    creation_time: datetime.datetime
    alert_status: str


class ModelDashboardIndicatorAction(Base):
    """
    ModelDashboardIndicatorAction
         <p>An alert action taken to light up an icon on the Amazon SageMaker Model Dashboard when an alert goes into <code>InAlert</code> status.</p>

        Attributes
       ----------------------
       enabled: 	 <p>Indicates whether the alert action is turned on.</p>
    """

    enabled: Optional[bool] = Unassigned()


class MonitoringAlertActions(Base):
    """
    MonitoringAlertActions
         <p>A list of alert actions taken in response to an alert going into <code>InAlert</code> status.</p>

        Attributes
       ----------------------
       model_dashboard_indicator: 	 <p>An alert action taken to light up an icon on the Model Dashboard when an alert goes into <code>InAlert</code> status.</p>
    """

    model_dashboard_indicator: Optional[ModelDashboardIndicatorAction] = Unassigned()


class MonitoringAlertSummary(Base):
    """
    MonitoringAlertSummary
         <p>Provides summary information about a monitor alert.</p>

        Attributes
       ----------------------
       monitoring_alert_name: 	 <p>The name of a monitoring alert.</p>
       creation_time: 	 <p>A timestamp that indicates when a monitor alert was created.</p>
       last_modified_time: 	 <p>A timestamp that indicates when a monitor alert was last updated.</p>
       alert_status: 	 <p>The current status of an alert.</p>
       datapoints_to_alert: 	 <p>Within <code>EvaluationPeriod</code>, how many execution failures will raise an alert.</p>
       evaluation_period: 	 <p>The number of most recent monitoring executions to consider when evaluating alert status.</p>
       actions: 	 <p>A list of alert actions taken in response to an alert going into <code>InAlert</code> status.</p>
    """

    monitoring_alert_name: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    alert_status: str
    datapoints_to_alert: int
    evaluation_period: int
    actions: MonitoringAlertActions


class MonitoringScheduleSummary(Base):
    """
    MonitoringScheduleSummary
         <p>Summarizes the monitoring schedule.</p>

        Attributes
       ----------------------
       monitoring_schedule_name: 	 <p>The name of the monitoring schedule.</p>
       monitoring_schedule_arn: 	 <p>The Amazon Resource Name (ARN) of the monitoring schedule.</p>
       creation_time: 	 <p>The creation time of the monitoring schedule.</p>
       last_modified_time: 	 <p>The last time the monitoring schedule was modified.</p>
       monitoring_schedule_status: 	 <p>The status of the monitoring schedule.</p>
       endpoint_name: 	 <p>The name of the endpoint using the monitoring schedule.</p>
       monitoring_job_definition_name: 	 <p>The name of the monitoring job definition that the schedule is for.</p>
       monitoring_type: 	 <p>The type of the monitoring job definition that the schedule is for.</p>
    """

    monitoring_schedule_name: str
    monitoring_schedule_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    monitoring_schedule_status: str
    endpoint_name: Optional[str] = Unassigned()
    monitoring_job_definition_name: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()


class NotebookInstanceLifecycleConfigSummary(Base):
    """
    NotebookInstanceLifecycleConfigSummary
         <p>Provides a summary of a notebook instance lifecycle configuration.</p>

        Attributes
       ----------------------
       notebook_instance_lifecycle_config_name: 	 <p>The name of the lifecycle configuration.</p>
       notebook_instance_lifecycle_config_arn: 	 <p>The Amazon Resource Name (ARN) of the lifecycle configuration.</p>
       creation_time: 	 <p>A timestamp that tells when the lifecycle configuration was created.</p>
       last_modified_time: 	 <p>A timestamp that tells when the lifecycle configuration was last modified.</p>
    """

    notebook_instance_lifecycle_config_name: str
    notebook_instance_lifecycle_config_arn: str
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class NotebookInstanceSummary(Base):
    """
    NotebookInstanceSummary
         <p>Provides summary information for an SageMaker notebook instance.</p>

        Attributes
       ----------------------
       notebook_instance_name: 	 <p>The name of the notebook instance that you want a summary for.</p>
       notebook_instance_arn: 	 <p>The Amazon Resource Name (ARN) of the notebook instance.</p>
       notebook_instance_status: 	 <p>The status of the notebook instance.</p>
       url: 	 <p>The URL that you use to connect to the Jupyter notebook running in your notebook instance. </p>
       instance_type: 	 <p>The type of ML compute instance that the notebook instance is running on.</p>
       creation_time: 	 <p>A timestamp that shows when the notebook instance was created.</p>
       last_modified_time: 	 <p>A timestamp that shows when the notebook instance was last modified.</p>
       notebook_instance_lifecycle_config_name: 	 <p>The name of a notebook instance lifecycle configuration associated with this notebook instance.</p> <p>For information about notebook instance lifestyle configurations, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-lifecycle-config.html">Step 2.1: (Optional) Customize a Notebook Instance</a>.</p>
       default_code_repository: 	 <p>The Git repository associated with the notebook instance as its default code repository. This can be either the name of a Git repository stored as a resource in your account, or the URL of a Git repository in <a href="https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html">Amazon Web Services CodeCommit</a> or in any other Git repository. When you open a notebook instance, it opens in the directory that contains this repository. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/nbi-git-repo.html">Associating Git Repositories with SageMaker Notebook Instances</a>.</p>
       additional_code_repositories: 	 <p>An array of up to three Git repositories associated with the notebook instance. These can be either the names of Git repositories stored as resources in your account, or the URL of Git repositories in <a href="https://docs.aws.amazon.com/codecommit/latest/userguide/welcome.html">Amazon Web Services CodeCommit</a> or in any other Git repository. These repositories are cloned at the same level as the default repository of your notebook instance. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/nbi-git-repo.html">Associating Git Repositories with SageMaker Notebook Instances</a>.</p>
    """

    notebook_instance_name: str
    notebook_instance_arn: str
    notebook_instance_status: Optional[str] = Unassigned()
    url: Optional[str] = Unassigned()
    instance_type: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    notebook_instance_lifecycle_config_name: Optional[str] = Unassigned()
    default_code_repository: Optional[str] = Unassigned()
    additional_code_repositories: Optional[List[str]] = Unassigned()


class TrainingJobStepMetadata(Base):
    """
    TrainingJobStepMetadata
         <p>Metadata for a training job step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the training job that was run by this step execution.</p>
    """

    arn: Optional[str] = Unassigned()


class ProcessingJobStepMetadata(Base):
    """
    ProcessingJobStepMetadata
         <p>Metadata for a processing job step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the processing job.</p>
    """

    arn: Optional[str] = Unassigned()


class TransformJobStepMetadata(Base):
    """
    TransformJobStepMetadata
         <p>Metadata for a transform job step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the transform job that was run by this step execution.</p>
    """

    arn: Optional[str] = Unassigned()


class TuningJobStepMetaData(Base):
    """
    TuningJobStepMetaData
         <p>Metadata for a tuning step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the tuning job that was run by this step execution.</p>
    """

    arn: Optional[str] = Unassigned()


class ModelStepMetadata(Base):
    """
    ModelStepMetadata
         <p>Metadata for Model steps.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the created model.</p>
    """

    arn: Optional[str] = Unassigned()


class RegisterModelStepMetadata(Base):
    """
    RegisterModelStepMetadata
         <p>Metadata for a register model job step.</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the model package.</p>
    """

    arn: Optional[str] = Unassigned()


class QualityCheckStepMetadata(Base):
    """
    QualityCheckStepMetadata
         <p>Container for the metadata for a Quality check step. For more information, see the topic on <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/build-and-manage-steps.html#step-type-quality-check">QualityCheck step</a> in the <i>Amazon SageMaker Developer Guide</i>. </p>

        Attributes
       ----------------------
       check_type: 	 <p>The type of the Quality check step.</p>
       baseline_used_for_drift_check_statistics: 	 <p>The Amazon S3 URI of the baseline statistics file used for the drift check.</p>
       baseline_used_for_drift_check_constraints: 	 <p>The Amazon S3 URI of the baseline constraints file used for the drift check.</p>
       calculated_baseline_statistics: 	 <p>The Amazon S3 URI of the newly calculated baseline statistics file.</p>
       calculated_baseline_constraints: 	 <p>The Amazon S3 URI of the newly calculated baseline constraints file.</p>
       model_package_group_name: 	 <p>The model package group name.</p>
       violation_report: 	 <p>The Amazon S3 URI of violation report if violations are detected.</p>
       check_job_arn: 	 <p>The Amazon Resource Name (ARN) of the Quality check processing job that was run by this step execution.</p>
       skip_check: 	 <p>This flag indicates if the drift check against the previous baseline will be skipped or not. If it is set to <code>False</code>, the previous baseline of the configured check type must be available.</p>
       register_new_baseline: 	 <p>This flag indicates if a newly calculated baseline can be accessed through step properties <code>BaselineUsedForDriftCheckConstraints</code> and <code>BaselineUsedForDriftCheckStatistics</code>. If it is set to <code>False</code>, the previous baseline of the configured check type must also be available. These can be accessed through the <code>BaselineUsedForDriftCheckConstraints</code> and <code> BaselineUsedForDriftCheckStatistics</code> properties. </p>
    """

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


class PipelineExecutionStepMetadata(Base):
    """
    PipelineExecutionStepMetadata
         <p>Metadata for a step execution.</p>

        Attributes
       ----------------------
       training_job: 	 <p>The Amazon Resource Name (ARN) of the training job that was run by this step execution.</p>
       processing_job: 	 <p>The Amazon Resource Name (ARN) of the processing job that was run by this step execution.</p>
       transform_job: 	 <p>The Amazon Resource Name (ARN) of the transform job that was run by this step execution.</p>
       tuning_job: 	 <p>The Amazon Resource Name (ARN) of the tuning job that was run by this step execution.</p>
       model: 	 <p>The Amazon Resource Name (ARN) of the model that was created by this step execution.</p>
       register_model: 	 <p>The Amazon Resource Name (ARN) of the model package that the model was registered to by this step execution.</p>
       condition: 	 <p>The outcome of the condition evaluation that was run by this step execution.</p>
       callback: 	 <p>The URL of the Amazon SQS queue used by this step execution, the pipeline generated token, and a list of output parameters.</p>
       lambda: 	 <p>The Amazon Resource Name (ARN) of the Lambda function that was run by this step execution and a list of output parameters.</p>
       e_m_r: 	 <p>The configurations and outcomes of an Amazon EMR step execution.</p>
       quality_check: 	 <p>The configurations and outcomes of the check step execution. This includes: </p> <ul> <li> <p>The type of the check conducted.</p> </li> <li> <p>The Amazon S3 URIs of baseline constraints and statistics files to be used for the drift check.</p> </li> <li> <p>The Amazon S3 URIs of newly calculated baseline constraints and statistics.</p> </li> <li> <p>The model package group name provided.</p> </li> <li> <p>The Amazon S3 URI of the violation report if violations detected.</p> </li> <li> <p>The Amazon Resource Name (ARN) of check processing job initiated by the step execution.</p> </li> <li> <p>The Boolean flags indicating if the drift check is skipped.</p> </li> <li> <p>If step property <code>BaselineUsedForDriftCheck</code> is set the same as <code>CalculatedBaseline</code>.</p> </li> </ul>
       clarify_check: 	 <p>Container for the metadata for a Clarify check step. The configurations and outcomes of the check step execution. This includes: </p> <ul> <li> <p>The type of the check conducted,</p> </li> <li> <p>The Amazon S3 URIs of baseline constraints and statistics files to be used for the drift check.</p> </li> <li> <p>The Amazon S3 URIs of newly calculated baseline constraints and statistics.</p> </li> <li> <p>The model package group name provided.</p> </li> <li> <p>The Amazon S3 URI of the violation report if violations detected.</p> </li> <li> <p>The Amazon Resource Name (ARN) of check processing job initiated by the step execution.</p> </li> <li> <p>The boolean flags indicating if the drift check is skipped.</p> </li> <li> <p>If step property <code>BaselineUsedForDriftCheck</code> is set the same as <code>CalculatedBaseline</code>.</p> </li> </ul>
       fail: 	 <p>The configurations and outcomes of a Fail step execution.</p>
       auto_m_l_job: 	 <p>The Amazon Resource Name (ARN) of the AutoML job that was run by this step.</p>
    """

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


class SelectiveExecutionResult(Base):
    """
    SelectiveExecutionResult
         <p>The ARN from an execution of the current pipeline.</p>

        Attributes
       ----------------------
       source_pipeline_execution_arn: 	 <p>The ARN from an execution of the current pipeline.</p>
    """

    source_pipeline_execution_arn: Optional[str] = Unassigned()


class PipelineExecutionStep(Base):
    """
    PipelineExecutionStep
         <p>An execution of a step in a pipeline.</p>

        Attributes
       ----------------------
       step_name: 	 <p>The name of the step that is executed.</p>
       step_display_name: 	 <p>The display name of the step.</p>
       step_description: 	 <p>The description of the step.</p>
       start_time: 	 <p>The time that the step started executing.</p>
       end_time: 	 <p>The time that the step stopped executing.</p>
       step_status: 	 <p>The status of the step execution.</p>
       cache_hit_result: 	 <p>If this pipeline execution step was cached, details on the cache hit.</p>
       failure_reason: 	 <p>The reason why the step failed execution. This is only returned if the step failed its execution.</p>
       metadata: 	 <p>Metadata to run the pipeline step.</p>
       attempt_count: 	 <p>The current attempt of the execution step. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-retry-policy.html">Retry Policy for SageMaker Pipelines steps</a>.</p>
       selective_execution_result: 	 <p>The ARN from an execution of the current pipeline from which results are reused for this step.</p>
    """

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


class PipelineExecutionSummary(Base):
    """
    PipelineExecutionSummary
         <p>A pipeline execution summary.</p>

        Attributes
       ----------------------
       pipeline_execution_arn: 	 <p>The Amazon Resource Name (ARN) of the pipeline execution.</p>
       start_time: 	 <p>The start time of the pipeline execution.</p>
       pipeline_execution_status: 	 <p>The status of the pipeline execution.</p>
       pipeline_execution_description: 	 <p>The description of the pipeline execution.</p>
       pipeline_execution_display_name: 	 <p>The display name of the pipeline execution.</p>
       pipeline_execution_failure_reason: 	 <p>A message generated by SageMaker Pipelines describing why the pipeline execution failed.</p>
    """

    pipeline_execution_arn: Optional[str] = Unassigned()
    start_time: Optional[datetime.datetime] = Unassigned()
    pipeline_execution_status: Optional[str] = Unassigned()
    pipeline_execution_description: Optional[str] = Unassigned()
    pipeline_execution_display_name: Optional[str] = Unassigned()
    pipeline_execution_failure_reason: Optional[str] = Unassigned()


class Parameter(Base):
    """
    Parameter
         <p>Assigns a value to a named Pipeline parameter.</p>

        Attributes
       ----------------------
       name: 	 <p>The name of the parameter to assign a value to. This parameter name must match a named parameter in the pipeline definition.</p>
       value: 	 <p>The literal value for the parameter.</p>
    """

    name: str
    value: str


class PipelineSummary(Base):
    """
    PipelineSummary
         <p>A summary of a pipeline.</p>

        Attributes
       ----------------------
       pipeline_arn: 	 <p> The Amazon Resource Name (ARN) of the pipeline.</p>
       pipeline_name: 	 <p>The name of the pipeline.</p>
       pipeline_display_name: 	 <p>The display name of the pipeline.</p>
       pipeline_description: 	 <p>The description of the pipeline.</p>
       role_arn: 	 <p>The Amazon Resource Name (ARN) that the pipeline used to execute.</p>
       creation_time: 	 <p>The creation time of the pipeline.</p>
       last_modified_time: 	 <p>The time that the pipeline was last modified.</p>
       last_execution_time: 	 <p>The last time that a pipeline execution began.</p>
    """

    pipeline_arn: Optional[str] = Unassigned()
    pipeline_name: Optional[str] = Unassigned()
    pipeline_display_name: Optional[str] = Unassigned()
    pipeline_description: Optional[str] = Unassigned()
    role_arn: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_execution_time: Optional[datetime.datetime] = Unassigned()


class ProcessingJobSummary(Base):
    """
    ProcessingJobSummary
         <p>Summary of information about a processing job.</p>

        Attributes
       ----------------------
       processing_job_name: 	 <p>The name of the processing job.</p>
       processing_job_arn: 	 <p>The Amazon Resource Name (ARN) of the processing job..</p>
       creation_time: 	 <p>The time at which the processing job was created.</p>
       processing_end_time: 	 <p>The time at which the processing job completed.</p>
       last_modified_time: 	 <p>A timestamp that indicates the last time the processing job was modified.</p>
       processing_job_status: 	 <p>The status of the processing job.</p>
       failure_reason: 	 <p>A string, up to one KB in size, that contains the reason a processing job failed, if it failed.</p>
       exit_message: 	 <p>An optional string, up to one KB in size, that contains metadata from the processing container when the processing job exits.</p>
    """

    processing_job_name: str
    processing_job_arn: str
    creation_time: datetime.datetime
    processing_job_status: str
    processing_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    exit_message: Optional[str] = Unassigned()


class ProjectSummary(Base):
    """
    ProjectSummary
         <p>Information about a project.</p>

        Attributes
       ----------------------
       project_name: 	 <p>The name of the project.</p>
       project_description: 	 <p>The description of the project.</p>
       project_arn: 	 <p>The Amazon Resource Name (ARN) of the project.</p>
       project_id: 	 <p>The ID of the project.</p>
       creation_time: 	 <p>The time that the project was created.</p>
       project_status: 	 <p>The status of the project.</p>
    """

    project_name: str
    project_arn: str
    project_id: str
    creation_time: datetime.datetime
    project_status: str
    project_description: Optional[str] = Unassigned()


class ResourceCatalog(Base):
    """
    ResourceCatalog
         <p> A resource catalog containing all of the resources of a specific resource type within a resource owner account. For an example on sharing the Amazon SageMaker Feature Store <code>DefaultFeatureGroupCatalog</code>, see <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/feature-store-cross-account-discoverability-share-sagemaker-catalog.html">Share Amazon SageMaker Catalog resource type</a> in the Amazon SageMaker Developer Guide. </p>

        Attributes
       ----------------------
       resource_catalog_arn: 	 <p> The Amazon Resource Name (ARN) of the <code>ResourceCatalog</code>. </p>
       resource_catalog_name: 	 <p> The name of the <code>ResourceCatalog</code>. </p>
       description: 	 <p> A free form description of the <code>ResourceCatalog</code>. </p>
       creation_time: 	 <p> The time the <code>ResourceCatalog</code> was created. </p>
    """

    resource_catalog_arn: str
    resource_catalog_name: str
    description: str
    creation_time: datetime.datetime


class SpaceSettingsSummary(Base):
    """
    SpaceSettingsSummary
         <p>Specifies summary information about the space settings.</p>

        Attributes
       ----------------------
       app_type: 	 <p>The type of app created within the space.</p>
       space_storage_settings: 	 <p>The storage settings for a private space.</p>
    """

    app_type: Optional[str] = Unassigned()
    space_storage_settings: Optional[SpaceStorageSettings] = Unassigned()


class SpaceSharingSettingsSummary(Base):
    """
    SpaceSharingSettingsSummary
         <p>Specifies summary information about the space sharing settings.</p>

        Attributes
       ----------------------
       sharing_type: 	 <p>Specifies the sharing type of the space.</p>
    """

    sharing_type: Optional[str] = Unassigned()


class OwnershipSettingsSummary(Base):
    """
    OwnershipSettingsSummary
         <p>Specifies summary information about the ownership settings.</p>

        Attributes
       ----------------------
       owner_user_profile_name: 	 <p>The user profile who is the owner of the private space.</p>
    """

    owner_user_profile_name: Optional[str] = Unassigned()


class SpaceDetails(Base):
    """
    SpaceDetails
         <p>The space's details.</p>

        Attributes
       ----------------------
       domain_id: 	 <p>The ID of the associated domain.</p>
       space_name: 	 <p>The name of the space.</p>
       status: 	 <p>The status.</p>
       creation_time: 	 <p>The creation time.</p>
       last_modified_time: 	 <p>The last modified time.</p>
       space_settings_summary: 	 <p>Specifies summary information about the space settings.</p>
       space_sharing_settings_summary: 	 <p>Specifies summary information about the space sharing settings.</p>
       ownership_settings_summary: 	 <p>Specifies summary information about the ownership settings.</p>
       space_display_name: 	 <p>The name of the space that appears in the Studio UI.</p>
    """

    domain_id: Optional[str] = Unassigned()
    space_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    space_settings_summary: Optional[SpaceSettingsSummary] = Unassigned()
    space_sharing_settings_summary: Optional[SpaceSharingSettingsSummary] = Unassigned()
    ownership_settings_summary: Optional[OwnershipSettingsSummary] = Unassigned()
    space_display_name: Optional[str] = Unassigned()


class StudioLifecycleConfigDetails(Base):
    """
    StudioLifecycleConfigDetails
         <p>Details of the Amazon SageMaker Studio Lifecycle Configuration.</p>

        Attributes
       ----------------------
       studio_lifecycle_config_arn: 	 <p> The Amazon Resource Name (ARN) of the Lifecycle Configuration.</p>
       studio_lifecycle_config_name: 	 <p>The name of the Amazon SageMaker Studio Lifecycle Configuration.</p>
       creation_time: 	 <p>The creation time of the Amazon SageMaker Studio Lifecycle Configuration.</p>
       last_modified_time: 	 <p>This value is equivalent to CreationTime because Amazon SageMaker Studio Lifecycle Configurations are immutable.</p>
       studio_lifecycle_config_app_type: 	 <p>The App type to which the Lifecycle Configuration is attached.</p>
    """

    studio_lifecycle_config_arn: Optional[str] = Unassigned()
    studio_lifecycle_config_name: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    studio_lifecycle_config_app_type: Optional[str] = Unassigned()


class TrainingJobSummary(Base):
    """
    TrainingJobSummary
         <p>Provides summary information about a training job.</p>

        Attributes
       ----------------------
       training_job_name: 	 <p>The name of the training job that you want a summary for.</p>
       training_job_arn: 	 <p>The Amazon Resource Name (ARN) of the training job.</p>
       creation_time: 	 <p>A timestamp that shows when the training job was created.</p>
       training_end_time: 	 <p>A timestamp that shows when the training job ended. This field is set only if the training job has one of the terminal statuses (<code>Completed</code>, <code>Failed</code>, or <code>Stopped</code>). </p>
       last_modified_time: 	 <p> Timestamp when the training job was last modified. </p>
       training_job_status: 	 <p>The status of the training job.</p>
       warm_pool_status: 	 <p>The status of the warm pool associated with the training job.</p>
    """

    training_job_name: str
    training_job_arn: str
    creation_time: datetime.datetime
    training_job_status: str
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    warm_pool_status: Optional[WarmPoolStatus] = Unassigned()


class TransformJobSummary(Base):
    """
    TransformJobSummary
         <p>Provides a summary of a transform job. Multiple <code>TransformJobSummary</code> objects are returned as a list after in response to a <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_ListTransformJobs.html">ListTransformJobs</a> call.</p>

        Attributes
       ----------------------
       transform_job_name: 	 <p>The name of the transform job.</p>
       transform_job_arn: 	 <p>The Amazon Resource Name (ARN) of the transform job.</p>
       creation_time: 	 <p>A timestamp that shows when the transform Job was created.</p>
       transform_end_time: 	 <p>Indicates when the transform job ends on compute instances. For successful jobs and stopped jobs, this is the exact time recorded after the results are uploaded. For failed jobs, this is when Amazon SageMaker detected that the job failed.</p>
       last_modified_time: 	 <p>Indicates when the transform job was last modified.</p>
       transform_job_status: 	 <p>The status of the transform job.</p>
       failure_reason: 	 <p>If the transform job failed, the reason it failed.</p>
    """

    transform_job_name: str
    transform_job_arn: str
    creation_time: datetime.datetime
    transform_job_status: str
    transform_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    failure_reason: Optional[str] = Unassigned()


class TrialComponentSummary(Base):
    """
    TrialComponentSummary
         <p>A summary of the properties of a trial component. To get all the properties, call the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrialComponent.html">DescribeTrialComponent</a> API and provide the <code>TrialComponentName</code>.</p>

        Attributes
       ----------------------
       trial_component_name: 	 <p>The name of the trial component.</p>
       trial_component_arn: 	 <p>The Amazon Resource Name (ARN) of the trial component.</p>
       display_name: 	 <p>The name of the component as displayed. If <code>DisplayName</code> isn't specified, <code>TrialComponentName</code> is displayed.</p>
       trial_component_source
       status: 	 <p>The status of the component. States include:</p> <ul> <li> <p>InProgress</p> </li> <li> <p>Completed</p> </li> <li> <p>Failed</p> </li> </ul>
       start_time: 	 <p>When the component started.</p>
       end_time: 	 <p>When the component ended.</p>
       creation_time: 	 <p>When the component was created.</p>
       created_by: 	 <p>Who created the trial component.</p>
       last_modified_time: 	 <p>When the component was last modified.</p>
       last_modified_by: 	 <p>Who last modified the component.</p>
    """

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


class TrialSummary(Base):
    """
    TrialSummary
         <p>A summary of the properties of a trial. To get the complete set of properties, call the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrial.html">DescribeTrial</a> API and provide the <code>TrialName</code>.</p>

        Attributes
       ----------------------
       trial_arn: 	 <p>The Amazon Resource Name (ARN) of the trial.</p>
       trial_name: 	 <p>The name of the trial.</p>
       display_name: 	 <p>The name of the trial as displayed. If <code>DisplayName</code> isn't specified, <code>TrialName</code> is displayed.</p>
       trial_source
       creation_time: 	 <p>When the trial was created.</p>
       last_modified_time: 	 <p>When the trial was last modified.</p>
    """

    trial_arn: Optional[str] = Unassigned()
    trial_name: Optional[str] = Unassigned()
    display_name: Optional[str] = Unassigned()
    trial_source: Optional[TrialSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class UserProfileDetails(Base):
    """
    UserProfileDetails
         <p>The user profile details.</p>

        Attributes
       ----------------------
       domain_id: 	 <p>The domain ID.</p>
       user_profile_name: 	 <p>The user profile name.</p>
       status: 	 <p>The status.</p>
       creation_time: 	 <p>The creation time.</p>
       last_modified_time: 	 <p>The last modified time.</p>
    """

    domain_id: Optional[str] = Unassigned()
    user_profile_name: Optional[str] = Unassigned()
    status: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()


class Model(Base):
    """
    Model
         <p>The properties of a model as returned by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p>

        Attributes
       ----------------------
       model_name: 	 <p>The name of the model.</p>
       primary_container
       containers: 	 <p>The containers in the inference pipeline.</p>
       inference_execution_config
       execution_role_arn: 	 <p>The Amazon Resource Name (ARN) of the IAM role that you specified for the model.</p>
       vpc_config
       creation_time: 	 <p>A timestamp that indicates when the model was created.</p>
       model_arn: 	 <p>The Amazon Resource Name (ARN) of the model.</p>
       enable_network_isolation: 	 <p>Isolates the model container. No inbound or outbound network calls can be made to or from the model container.</p>
       tags: 	 <p>A list of key-value pairs associated with the model. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a> in the <i>Amazon Web Services General Reference Guide</i>.</p>
       deployment_recommendation: 	 <p>A set of recommended deployment configurations for the model.</p>
    """

    model_name: Optional[str] = Unassigned()
    primary_container: Optional[ContainerDefinition] = Unassigned()
    containers: Optional[List[ContainerDefinition]] = Unassigned()
    inference_execution_config: Optional[InferenceExecutionConfig] = Unassigned()
    execution_role_arn: Optional[str] = Unassigned()
    vpc_config: Optional[VpcConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    model_arn: Optional[str] = Unassigned()
    enable_network_isolation: Optional[bool] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    deployment_recommendation: Optional[DeploymentRecommendation] = Unassigned()


class ModelCard(Base):
    """
    ModelCard
         <p>An Amazon SageMaker Model Card.</p>

        Attributes
       ----------------------
       model_card_arn: 	 <p>The Amazon Resource Name (ARN) of the model card.</p>
       model_card_name: 	 <p>The unique name of the model card.</p>
       model_card_version: 	 <p>The version of the model card.</p>
       content: 	 <p>The content of the model card. Content uses the <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards.html#model-cards-json-schema">model card JSON schema</a> and provided as a string.</p>
       model_card_status: 	 <p>The approval status of the model card within your organization. Different organizations might have different criteria for model card review and approval.</p> <ul> <li> <p> <code>Draft</code>: The model card is a work in progress.</p> </li> <li> <p> <code>PendingReview</code>: The model card is pending review.</p> </li> <li> <p> <code>Approved</code>: The model card is approved.</p> </li> <li> <p> <code>Archived</code>: The model card is archived. No more updates should be made to the model card, but it can still be exported.</p> </li> </ul>
       security_config: 	 <p>The security configuration used to protect model card data.</p>
       creation_time: 	 <p>The date and time that the model card was created.</p>
       created_by
       last_modified_time: 	 <p>The date and time that the model card was last modified.</p>
       last_modified_by
       tags: 	 <p>Key-value pairs used to manage metadata for the model card.</p>
       model_id: 	 <p>The unique name (ID) of the model.</p>
       risk_rating: 	 <p>The risk rating of the model. Different organizations might have different criteria for model card risk ratings. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-cards-risk-rating.html">Risk ratings</a>.</p>
       model_package_group_name: 	 <p>The model package group that contains the model package. Only relevant for model cards created for model packages in the Amazon SageMaker Model Registry. </p>
    """

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
    tags: Optional[List[Tag]] = Unassigned()
    model_id: Optional[str] = Unassigned()
    risk_rating: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()


class ModelDashboardEndpoint(Base):
    """
    ModelDashboardEndpoint
         <p>An endpoint that hosts a model displayed in the Amazon SageMaker Model Dashboard.</p>

        Attributes
       ----------------------
       endpoint_name: 	 <p>The endpoint name.</p>
       endpoint_arn: 	 <p>The Amazon Resource Name (ARN) of the endpoint.</p>
       creation_time: 	 <p>A timestamp that indicates when the endpoint was created.</p>
       last_modified_time: 	 <p>The last time the endpoint was modified.</p>
       endpoint_status: 	 <p>The endpoint status.</p>
    """

    endpoint_name: str
    endpoint_arn: str
    creation_time: datetime.datetime
    last_modified_time: datetime.datetime
    endpoint_status: str


class TransformJob(Base):
    """
    TransformJob
         <p>A batch transform job. For information about SageMaker batch transform, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html">Use Batch Transform</a>.</p>

        Attributes
       ----------------------
       transform_job_name: 	 <p>The name of the transform job.</p>
       transform_job_arn: 	 <p>The Amazon Resource Name (ARN) of the transform job.</p>
       transform_job_status: 	 <p>The status of the transform job.</p> <p>Transform job statuses are:</p> <ul> <li> <p> <code>InProgress</code> - The job is in progress.</p> </li> <li> <p> <code>Completed</code> - The job has completed.</p> </li> <li> <p> <code>Failed</code> - The transform job has failed. To see the reason for the failure, see the <code>FailureReason</code> field in the response to a <code>DescribeTransformJob</code> call.</p> </li> <li> <p> <code>Stopping</code> - The transform job is stopping.</p> </li> <li> <p> <code>Stopped</code> - The transform job has stopped.</p> </li> </ul>
       failure_reason: 	 <p>If the transform job failed, the reason it failed.</p>
       model_name: 	 <p>The name of the model associated with the transform job.</p>
       max_concurrent_transforms: 	 <p>The maximum number of parallel requests that can be sent to each instance in a transform job. If <code>MaxConcurrentTransforms</code> is set to 0 or left unset, SageMaker checks the optional execution-parameters to determine the settings for your chosen algorithm. If the execution-parameters endpoint is not enabled, the default value is 1. For built-in algorithms, you don't need to set a value for <code>MaxConcurrentTransforms</code>.</p>
       model_client_config
       max_payload_in_m_b: 	 <p>The maximum allowed size of the payload, in MB. A payload is the data portion of a record (without metadata). The value in <code>MaxPayloadInMB</code> must be greater than, or equal to, the size of a single record. To estimate the size of a record in MB, divide the size of your dataset by the number of records. To ensure that the records fit within the maximum payload size, we recommend using a slightly larger value. The default value is 6 MB. For cases where the payload might be arbitrarily large and is transmitted using HTTP chunked encoding, set the value to 0. This feature works only in supported algorithms. Currently, SageMaker built-in algorithms do not support HTTP chunked encoding.</p>
       batch_strategy: 	 <p>Specifies the number of records to include in a mini-batch for an HTTP inference request. A record is a single unit of input data that inference can be made on. For example, a single line in a CSV file is a record.</p>
       environment: 	 <p>The environment variables to set in the Docker container. We support up to 16 key and values entries in the map.</p>
       transform_input
       transform_output
       data_capture_config
       transform_resources
       creation_time: 	 <p>A timestamp that shows when the transform Job was created.</p>
       transform_start_time: 	 <p>Indicates when the transform job starts on ML instances. You are billed for the time interval between this time and the value of <code>TransformEndTime</code>.</p>
       transform_end_time: 	 <p>Indicates when the transform job has been completed, or has stopped or failed. You are billed for the time interval between this time and the value of <code>TransformStartTime</code>.</p>
       labeling_job_arn: 	 <p>The Amazon Resource Name (ARN) of the labeling job that created the transform job.</p>
       auto_m_l_job_arn: 	 <p>The Amazon Resource Name (ARN) of the AutoML job that created the transform job.</p>
       data_processing
       experiment_config
       tags: 	 <p>A list of tags associated with the transform job.</p>
    """

    transform_job_name: Optional[str] = Unassigned()
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
    tags: Optional[List[Tag]] = Unassigned()


class ModelDashboardMonitoringSchedule(Base):
    """
    ModelDashboardMonitoringSchedule
         <p>A monitoring schedule for a model displayed in the Amazon SageMaker Model Dashboard.</p>

        Attributes
       ----------------------
       monitoring_schedule_arn: 	 <p>The Amazon Resource Name (ARN) of a monitoring schedule.</p>
       monitoring_schedule_name: 	 <p>The name of a monitoring schedule.</p>
       monitoring_schedule_status: 	 <p>The status of the monitoring schedule.</p>
       monitoring_type: 	 <p>The monitor type of a model monitor.</p>
       failure_reason: 	 <p>If a monitoring job failed, provides the reason.</p>
       creation_time: 	 <p>A timestamp that indicates when the monitoring schedule was created.</p>
       last_modified_time: 	 <p>A timestamp that indicates when the monitoring schedule was last updated.</p>
       monitoring_schedule_config
       endpoint_name: 	 <p>The endpoint which is monitored.</p>
       monitoring_alert_summaries: 	 <p>A JSON array where each element is a summary for a monitoring alert.</p>
       last_monitoring_execution_summary
       batch_transform_input
    """

    monitoring_schedule_arn: Optional[str] = Unassigned()
    monitoring_schedule_name: Optional[str] = Unassigned()
    monitoring_schedule_status: Optional[str] = Unassigned()
    monitoring_type: Optional[str] = Unassigned()
    failure_reason: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    monitoring_schedule_config: Optional[MonitoringScheduleConfig] = Unassigned()
    endpoint_name: Optional[str] = Unassigned()
    monitoring_alert_summaries: Optional[List[MonitoringAlertSummary]] = Unassigned()
    last_monitoring_execution_summary: Optional[MonitoringExecutionSummary] = (
        Unassigned()
    )
    batch_transform_input: Optional[BatchTransformInput] = Unassigned()


class ModelDashboardModelCard(Base):
    """
    ModelDashboardModelCard
         <p>The model card for a model displayed in the Amazon SageMaker Model Dashboard.</p>

        Attributes
       ----------------------
       model_card_arn: 	 <p>The Amazon Resource Name (ARN) for a model card.</p>
       model_card_name: 	 <p>The name of a model card.</p>
       model_card_version: 	 <p>The model card version.</p>
       model_card_status: 	 <p>The model card status.</p>
       security_config: 	 <p>The KMS Key ID (<code>KMSKeyId</code>) for encryption of model card information.</p>
       creation_time: 	 <p>A timestamp that indicates when the model card was created.</p>
       created_by
       last_modified_time: 	 <p>A timestamp that indicates when the model card was last updated.</p>
       last_modified_by
       tags: 	 <p>The tags associated with a model card.</p>
       model_id: 	 <p>For models created in SageMaker, this is the model ARN. For models created outside of SageMaker, this is a user-customized string.</p>
       risk_rating: 	 <p>A model card's risk rating. Can be low, medium, or high.</p>
    """

    model_card_arn: Optional[str] = Unassigned()
    model_card_name: Optional[str] = Unassigned()
    model_card_version: Optional[int] = Unassigned()
    model_card_status: Optional[str] = Unassigned()
    security_config: Optional[ModelCardSecurityConfig] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    model_id: Optional[str] = Unassigned()
    risk_rating: Optional[str] = Unassigned()


class ModelDashboardModel(Base):
    """
    ModelDashboardModel
         <p>A model displayed in the Amazon SageMaker Model Dashboard.</p>

        Attributes
       ----------------------
       model: 	 <p>A model displayed in the Model Dashboard.</p>
       endpoints: 	 <p>The endpoints that host a model.</p>
       last_batch_transform_job
       monitoring_schedules: 	 <p>The monitoring schedules for a model.</p>
       model_card: 	 <p>The model card for a model.</p>
    """

    model: Optional[Model] = Unassigned()
    endpoints: Optional[List[ModelDashboardEndpoint]] = Unassigned()
    last_batch_transform_job: Optional[TransformJob] = Unassigned()
    monitoring_schedules: Optional[List[ModelDashboardMonitoringSchedule]] = (
        Unassigned()
    )
    model_card: Optional[ModelDashboardModelCard] = Unassigned()


class ModelPackage(Base):
    """
    ModelPackage
         <p>A versioned model that can be deployed for SageMaker inference.</p>

        Attributes
       ----------------------
       model_package_name: 	 <p>The name of the model.</p>
       model_package_group_name: 	 <p>The model group to which the model belongs.</p>
       model_package_version: 	 <p>The version number of a versioned model.</p>
       model_package_arn: 	 <p>The Amazon Resource Name (ARN) of the model package.</p>
       model_package_description: 	 <p>The description of the model package.</p>
       creation_time: 	 <p>The time that the model package was created.</p>
       inference_specification: 	 <p>Defines how to perform inference generation after a training job is run.</p>
       source_algorithm_specification: 	 <p>A list of algorithms that were used to create a model package.</p>
       validation_specification: 	 <p>Specifies batch transform jobs that SageMaker runs to validate your model package.</p>
       model_package_status: 	 <p>The status of the model package. This can be one of the following values.</p> <ul> <li> <p> <code>PENDING</code> - The model package is pending being created.</p> </li> <li> <p> <code>IN_PROGRESS</code> - The model package is in the process of being created.</p> </li> <li> <p> <code>COMPLETED</code> - The model package was successfully created.</p> </li> <li> <p> <code>FAILED</code> - The model package failed.</p> </li> <li> <p> <code>DELETING</code> - The model package is in the process of being deleted.</p> </li> </ul>
       model_package_status_details: 	 <p>Specifies the validation and image scan statuses of the model package.</p>
       certify_for_marketplace: 	 <p>Whether the model package is to be certified to be listed on Amazon Web Services Marketplace. For information about listing model packages on Amazon Web Services Marketplace, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-mkt-list.html">List Your Algorithm or Model Package on Amazon Web Services Marketplace</a>.</p>
       model_approval_status: 	 <p>The approval status of the model. This can be one of the following values.</p> <ul> <li> <p> <code>APPROVED</code> - The model is approved</p> </li> <li> <p> <code>REJECTED</code> - The model is rejected.</p> </li> <li> <p> <code>PENDING_MANUAL_APPROVAL</code> - The model is waiting for manual approval.</p> </li> </ul>
       created_by: 	 <p>Information about the user who created or modified an experiment, trial, trial component, lineage group, or project.</p>
       metadata_properties: 	 <p>Metadata properties of the tracking entity, trial, or trial component.</p>
       model_metrics: 	 <p>Metrics for the model.</p>
       last_modified_time: 	 <p>The last time the model package was modified.</p>
       last_modified_by: 	 <p>Information about the user who created or modified an experiment, trial, trial component, lineage group, or project.</p>
       approval_description: 	 <p>A description provided when the model approval is set.</p>
       domain: 	 <p>The machine learning domain of your model package and its components. Common machine learning domains include computer vision and natural language processing.</p>
       task: 	 <p>The machine learning task your model package accomplishes. Common machine learning tasks include object detection and image classification.</p>
       sample_payload_url: 	 <p>The Amazon Simple Storage Service path where the sample payload are stored. This path must point to a single gzip compressed tar archive (.tar.gz suffix).</p>
       additional_inference_specifications: 	 <p>An array of additional Inference Specification objects.</p>
       source_uri: 	 <p>The URI of the source for the model package.</p>
       tags: 	 <p>A list of the tags associated with the model package. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a> in the <i>Amazon Web Services General Reference Guide</i>.</p>
       customer_metadata_properties: 	 <p>The metadata properties for the model package. </p>
       drift_check_baselines: 	 <p>Represents the drift check baselines that can be used when the model monitor is set using the model package.</p>
       skip_model_validation: 	 <p>Indicates if you want to skip model validation.</p>
    """

    model_package_name: Optional[str] = Unassigned()
    model_package_group_name: Optional[str] = Unassigned()
    model_package_version: Optional[int] = Unassigned()
    model_package_arn: Optional[str] = Unassigned()
    model_package_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    inference_specification: Optional[InferenceSpecification] = Unassigned()
    source_algorithm_specification: Optional[SourceAlgorithmSpecification] = (
        Unassigned()
    )
    validation_specification: Optional[ModelPackageValidationSpecification] = (
        Unassigned()
    )
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
    additional_inference_specifications: Optional[
        List[AdditionalInferenceSpecificationDefinition]
    ] = Unassigned()
    source_uri: Optional[str] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    customer_metadata_properties: Optional[Dict[str, str]] = Unassigned()
    drift_check_baselines: Optional[DriftCheckBaselines] = Unassigned()
    skip_model_validation: Optional[str] = Unassigned()


class ModelPackageGroup(Base):
    """
    ModelPackageGroup
         <p>A group of versioned models in the model registry.</p>

        Attributes
       ----------------------
       model_package_group_name: 	 <p>The name of the model group.</p>
       model_package_group_arn: 	 <p>The Amazon Resource Name (ARN) of the model group.</p>
       model_package_group_description: 	 <p>The description for the model group.</p>
       creation_time: 	 <p>The time that the model group was created.</p>
       created_by
       model_package_group_status: 	 <p>The status of the model group. This can be one of the following values.</p> <ul> <li> <p> <code>PENDING</code> - The model group is pending being created.</p> </li> <li> <p> <code>IN_PROGRESS</code> - The model group is in the process of being created.</p> </li> <li> <p> <code>COMPLETED</code> - The model group was successfully created.</p> </li> <li> <p> <code>FAILED</code> - The model group failed.</p> </li> <li> <p> <code>DELETING</code> - The model group is in the process of being deleted.</p> </li> <li> <p> <code>DELETE_FAILED</code> - SageMaker failed to delete the model group.</p> </li> </ul>
       tags: 	 <p>A list of the tags associated with the model group. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services resources</a> in the <i>Amazon Web Services General Reference Guide</i>.</p>
    """

    model_package_group_name: Optional[str] = Unassigned()
    model_package_group_arn: Optional[str] = Unassigned()
    model_package_group_description: Optional[str] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    model_package_group_status: Optional[str] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()


class NestedFilters(Base):
    """
    NestedFilters
         <p>A list of nested <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Filter.html">Filter</a> objects. A resource must satisfy the conditions of all filters to be included in the results returned from the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p> <p>For example, to filter on a training job's <code>InputDataConfig</code> property with a specific channel name and <code>S3Uri</code> prefix, define the following filters:</p> <ul> <li> <p> <code>'{Name:"InputDataConfig.ChannelName", "Operator":"Equals", "Value":"train"}',</code> </p> </li> <li> <p> <code>'{Name:"InputDataConfig.DataSource.S3DataSource.S3Uri", "Operator":"Contains", "Value":"mybucket/catdata"}'</code> </p> </li> </ul>

        Attributes
       ----------------------
       nested_property_name: 	 <p>The name of the property to use in the nested filters. The value must match a listed property name, such as <code>InputDataConfig</code>.</p>
       filters: 	 <p>A list of filters. Each filter acts on a property. Filters must contain at least one <code>Filters</code> value. For example, a <code>NestedFilters</code> call might include a filter on the <code>PropertyName</code> parameter of the <code>InputDataConfig</code> property: <code>InputDataConfig.DataSource.S3DataSource.S3Uri</code>.</p>
    """

    nested_property_name: str
    filters: List[Filter]


class OnlineStoreConfigUpdate(Base):
    """
    OnlineStoreConfigUpdate
         <p>Updates the feature group online store configuration.</p>

        Attributes
       ----------------------
       ttl_duration: 	 <p>Time to live duration, where the record is hard deleted after the expiration time is reached; <code>ExpiresAt</code> = <code>EventTime</code> + <code>TtlDuration</code>. For information on HardDelete, see the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_feature_store_DeleteRecord.html">DeleteRecord</a> API in the Amazon SageMaker API Reference guide.</p>
    """

    ttl_duration: Optional[TtlDuration] = Unassigned()


class Parent(Base):
    """
    Parent
         <p>The trial that a trial component is associated with and the experiment the trial is part of. A component might not be associated with a trial. A component can be associated with multiple trials.</p>

        Attributes
       ----------------------
       trial_name: 	 <p>The name of the trial.</p>
       experiment_name: 	 <p>The name of the experiment.</p>
    """

    trial_name: Optional[str] = Unassigned()
    experiment_name: Optional[str] = Unassigned()


class Pipeline(Base):
    """
    Pipeline
         <p>A SageMaker Model Building Pipeline instance.</p>

        Attributes
       ----------------------
       pipeline_arn: 	 <p>The Amazon Resource Name (ARN) of the pipeline.</p>
       pipeline_name: 	 <p>The name of the pipeline.</p>
       pipeline_display_name: 	 <p>The display name of the pipeline.</p>
       pipeline_description: 	 <p>The description of the pipeline.</p>
       role_arn: 	 <p>The Amazon Resource Name (ARN) of the role that created the pipeline.</p>
       pipeline_status: 	 <p>The status of the pipeline.</p>
       creation_time: 	 <p>The creation time of the pipeline.</p>
       last_modified_time: 	 <p>The time that the pipeline was last modified.</p>
       last_run_time: 	 <p>The time when the pipeline was last run.</p>
       created_by
       last_modified_by
       parallelism_configuration: 	 <p>The parallelism configuration applied to the pipeline.</p>
       tags: 	 <p>A list of tags that apply to the pipeline.</p>
    """

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
    tags: Optional[List[Tag]] = Unassigned()


class PipelineExecution(Base):
    """
    PipelineExecution
         <p>An execution of a pipeline.</p>

        Attributes
       ----------------------
       pipeline_arn: 	 <p>The Amazon Resource Name (ARN) of the pipeline that was executed.</p>
       pipeline_execution_arn: 	 <p>The Amazon Resource Name (ARN) of the pipeline execution.</p>
       pipeline_execution_display_name: 	 <p>The display name of the pipeline execution.</p>
       pipeline_execution_status: 	 <p>The status of the pipeline status.</p>
       pipeline_execution_description: 	 <p>The description of the pipeline execution.</p>
       pipeline_experiment_config
       failure_reason: 	 <p>If the execution failed, a message describing why.</p>
       creation_time: 	 <p>The creation time of the pipeline execution.</p>
       last_modified_time: 	 <p>The time that the pipeline execution was last modified.</p>
       created_by
       last_modified_by
       parallelism_configuration: 	 <p>The parallelism configuration applied to the pipeline execution.</p>
       selective_execution_config: 	 <p>The selective execution configuration applied to the pipeline run.</p>
       pipeline_parameters: 	 <p>Contains a list of pipeline parameters. This list can be empty. </p>
    """

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
    pipeline_parameters: Optional[List[Parameter]] = Unassigned()


class ProcessingJob(Base):
    """
    ProcessingJob
         <p>An Amazon SageMaker processing job that is used to analyze data and evaluate models. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/processing-job.html">Process Data and Evaluate Models</a>.</p>

        Attributes
       ----------------------
       processing_inputs: 	 <p>List of input configurations for the processing job.</p>
       processing_output_config
       processing_job_name: 	 <p>The name of the processing job.</p>
       processing_resources
       stopping_condition
       app_specification
       environment: 	 <p>Sets the environment variables in the Docker container.</p>
       network_config
       role_arn: 	 <p>The ARN of the role used to create the processing job.</p>
       experiment_config
       processing_job_arn: 	 <p>The ARN of the processing job.</p>
       processing_job_status: 	 <p>The status of the processing job.</p>
       exit_message: 	 <p>A string, up to one KB in size, that contains metadata from the processing container when the processing job exits.</p>
       failure_reason: 	 <p>A string, up to one KB in size, that contains the reason a processing job failed, if it failed.</p>
       processing_end_time: 	 <p>The time that the processing job ended.</p>
       processing_start_time: 	 <p>The time that the processing job started.</p>
       last_modified_time: 	 <p>The time the processing job was last modified.</p>
       creation_time: 	 <p>The time the processing job was created.</p>
       monitoring_schedule_arn: 	 <p>The ARN of a monitoring schedule for an endpoint associated with this processing job.</p>
       auto_m_l_job_arn: 	 <p>The Amazon Resource Name (ARN) of the AutoML job associated with this processing job.</p>
       training_job_arn: 	 <p>The ARN of the training job associated with this processing job.</p>
       tags: 	 <p>An array of key-value pairs. For more information, see <a href="https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html#allocation-whatURL">Using Cost Allocation Tags</a> in the <i>Amazon Web Services Billing and Cost Management User Guide</i>.</p>
    """

    processing_inputs: Optional[List[ProcessingInput]] = Unassigned()
    processing_output_config: Optional[ProcessingOutputConfig] = Unassigned()
    processing_job_name: Optional[str] = Unassigned()
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
    tags: Optional[List[Tag]] = Unassigned()


class ProfilerConfigForUpdate(Base):
    """
    ProfilerConfigForUpdate
         <p>Configuration information for updating the Amazon SageMaker Debugger profile parameters, system and framework metrics configurations, and storage paths.</p>

        Attributes
       ----------------------
       s3_output_path: 	 <p>Path to Amazon S3 storage location for system and framework metrics.</p>
       profiling_interval_in_milliseconds: 	 <p>A time interval for capturing system metrics in milliseconds. Available values are 100, 200, 500, 1000 (1 second), 5000 (5 seconds), and 60000 (1 minute) milliseconds. The default value is 500 milliseconds.</p>
       profiling_parameters: 	 <p>Configuration information for capturing framework metrics. Available key strings for different profiling options are <code>DetailedProfilingConfig</code>, <code>PythonProfilingConfig</code>, and <code>DataLoaderProfilingConfig</code>. The following codes are configuration structures for the <code>ProfilingParameters</code> parameter. To learn more about how to configure the <code>ProfilingParameters</code> parameter, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/debugger-createtrainingjob-api.html">Use the SageMaker and Debugger Configuration API Operations to Create, Update, and Debug Your Training Job</a>. </p>
       disable_profiler: 	 <p>To turn off Amazon SageMaker Debugger monitoring and profiling while a training job is in progress, set to <code>True</code>.</p>
    """

    s3_output_path: Optional[str] = Unassigned()
    profiling_interval_in_milliseconds: Optional[int] = Unassigned()
    profiling_parameters: Optional[Dict[str, str]] = Unassigned()
    disable_profiler: Optional[bool] = Unassigned()


class Project(Base):
    """
    Project
         <p>The properties of a project as returned by the Search API.</p>

        Attributes
       ----------------------
       project_arn: 	 <p>The Amazon Resource Name (ARN) of the project.</p>
       project_name: 	 <p>The name of the project.</p>
       project_id: 	 <p>The ID of the project.</p>
       project_description: 	 <p>The description of the project.</p>
       service_catalog_provisioning_details
       service_catalog_provisioned_product_details
       project_status: 	 <p>The status of the project.</p>
       created_by: 	 <p>Who created the project.</p>
       creation_time: 	 <p>A timestamp specifying when the project was created.</p>
       tags: 	 <p>An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services Resources</a>.</p>
       last_modified_time: 	 <p>A timestamp container for when the project was last modified.</p>
       last_modified_by
    """

    project_arn: Optional[str] = Unassigned()
    project_name: Optional[str] = Unassigned()
    project_id: Optional[str] = Unassigned()
    project_description: Optional[str] = Unassigned()
    service_catalog_provisioning_details: Optional[
        ServiceCatalogProvisioningDetails
    ] = Unassigned()
    service_catalog_provisioned_product_details: Optional[
        ServiceCatalogProvisionedProductDetails
    ] = Unassigned()
    project_status: Optional[str] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    last_modified_by: Optional[UserContext] = Unassigned()


class QueryFilters(Base):
    """
    QueryFilters
         <p>A set of filters to narrow the set of lineage entities connected to the <code>StartArn</code>(s) returned by the <code>QueryLineage</code> API action.</p>

        Attributes
       ----------------------
       types: 	 <p>Filter the lineage entities connected to the <code>StartArn</code> by type. For example: <code>DataSet</code>, <code>Model</code>, <code>Endpoint</code>, or <code>ModelDeployment</code>.</p>
       lineage_types: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) by the type of the lineage entity.</p>
       created_before: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) by created date.</p>
       created_after: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) after the create date.</p>
       modified_before: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) before the last modified date.</p>
       modified_after: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) after the last modified date.</p>
       properties: 	 <p>Filter the lineage entities connected to the <code>StartArn</code>(s) by a set if property key value pairs. If multiple pairs are provided, an entity is included in the results if it matches any of the provided pairs.</p>
    """

    types: Optional[List[str]] = Unassigned()
    lineage_types: Optional[List[str]] = Unassigned()
    created_before: Optional[datetime.datetime] = Unassigned()
    created_after: Optional[datetime.datetime] = Unassigned()
    modified_before: Optional[datetime.datetime] = Unassigned()
    modified_after: Optional[datetime.datetime] = Unassigned()
    properties: Optional[Dict[str, str]] = Unassigned()


class Vertex(Base):
    """
    Vertex
         <p>A lineage entity connected to the starting entity(ies).</p>

        Attributes
       ----------------------
       arn: 	 <p>The Amazon Resource Name (ARN) of the lineage entity resource.</p>
       type: 	 <p>The type of the lineage entity resource. For example: <code>DataSet</code>, <code>Model</code>, <code>Endpoint</code>, etc...</p>
       lineage_type: 	 <p>The type of resource of the lineage entity.</p>
    """

    arn: Optional[str] = Unassigned()
    type: Optional[str] = Unassigned()
    lineage_type: Optional[str] = Unassigned()


class RemoteDebugConfigForUpdate(Base):
    """
    RemoteDebugConfigForUpdate
         <p>Configuration for remote debugging for the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateTrainingJob.html">UpdateTrainingJob</a> API. To learn more about the remote debugging functionality of SageMaker, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-remote-debugging.html">Access a training container through Amazon Web Services Systems Manager (SSM) for remote debugging</a>.</p>

        Attributes
       ----------------------
       enable_remote_debug: 	 <p>If set to True, enables remote debugging.</p>
    """

    enable_remote_debug: Optional[bool] = Unassigned()


class RenderableTask(Base):
    """
    RenderableTask
         <p>Contains input values for a task.</p>

        Attributes
       ----------------------
       input: 	 <p>A JSON object that contains values for the variables defined in the template. It is made available to the template under the substitution variable <code>task.input</code>. For example, if you define a variable <code>task.input.text</code> in your template, you can supply the variable in the JSON object as <code>"text": "sample text"</code>.</p>
    """

    input: str


class RenderingError(Base):
    """
    RenderingError
         <p>A description of an error that occurred while rendering the template.</p>

        Attributes
       ----------------------
       code: 	 <p>A unique identifier for a specific class of errors.</p>
       message: 	 <p>A human-readable message describing the error.</p>
    """

    code: str
    message: str


class ResourceConfigForUpdate(Base):
    """
    ResourceConfigForUpdate
         <p>The <code>ResourceConfig</code> to update <code>KeepAlivePeriodInSeconds</code>. Other fields in the <code>ResourceConfig</code> cannot be updated.</p>

        Attributes
       ----------------------
       keep_alive_period_in_seconds: 	 <p>The <code>KeepAlivePeriodInSeconds</code> value specified in the <code>ResourceConfig</code> to update.</p>
    """

    keep_alive_period_in_seconds: int


class ResourceInUse(Base):
    """
    ResourceInUse
         <p>Resource being accessed is in use.</p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class ResourceLimitExceeded(Base):
    """
    ResourceLimitExceeded
         <p> You have exceeded an SageMaker resource limit. For example, you might have too many training jobs created. </p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class ResourceNotFound(Base):
    """
    ResourceNotFound
         <p>Resource being access is not found.</p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class SearchExpression(Base):
    """
    SearchExpression
         <p>A multi-expression that searches for the specified resource or resources in a search. All resource objects that satisfy the expression's condition are included in the search results. You must specify at least one subexpression, filter, or nested filter. A <code>SearchExpression</code> can contain up to twenty elements.</p> <p>A <code>SearchExpression</code> contains the following components:</p> <ul> <li> <p>A list of <code>Filter</code> objects. Each filter defines a simple Boolean expression comprised of a resource property name, Boolean operator, and value.</p> </li> <li> <p>A list of <code>NestedFilter</code> objects. Each nested filter defines a list of Boolean expressions using a list of resource properties. A nested filter is satisfied if a single object in the list satisfies all Boolean expressions.</p> </li> <li> <p>A list of <code>SearchExpression</code> objects. A search expression object can be nested in a list of search expression objects.</p> </li> <li> <p>A Boolean operator: <code>And</code> or <code>Or</code>.</p> </li> </ul>

        Attributes
       ----------------------
       filters: 	 <p>A list of filter objects.</p>
       nested_filters: 	 <p>A list of nested filter objects.</p>
       sub_expressions: 	 <p>A list of search expression objects.</p>
       operator: 	 <p>A Boolean operator used to evaluate the search expression. If you want every conditional statement in all lists to be satisfied for the entire search expression to be true, specify <code>And</code>. If only a single conditional statement needs to be true for the entire search expression to be true, specify <code>Or</code>. The default value is <code>And</code>.</p>
    """

    filters: Optional[List[Filter]] = Unassigned()
    nested_filters: Optional[List[NestedFilters]] = Unassigned()
    sub_expressions: Optional[List["SearchExpression"]] = Unassigned()
    operator: Optional[str] = Unassigned()


class TrainingJob(Base):
    """
    TrainingJob
         <p>Contains information about a training job.</p>

        Attributes
       ----------------------
       training_job_name: 	 <p>The name of the training job.</p>
       training_job_arn: 	 <p>The Amazon Resource Name (ARN) of the training job.</p>
       tuning_job_arn: 	 <p>The Amazon Resource Name (ARN) of the associated hyperparameter tuning job if the training job was launched by a hyperparameter tuning job.</p>
       labeling_job_arn: 	 <p>The Amazon Resource Name (ARN) of the labeling job.</p>
       auto_m_l_job_arn: 	 <p>The Amazon Resource Name (ARN) of the job.</p>
       model_artifacts: 	 <p>Information about the Amazon S3 location that is configured for storing model artifacts.</p>
       training_job_status: 	 <p>The status of the training job.</p> <p>Training job statuses are:</p> <ul> <li> <p> <code>InProgress</code> - The training is in progress.</p> </li> <li> <p> <code>Completed</code> - The training job has completed.</p> </li> <li> <p> <code>Failed</code> - The training job has failed. To see the reason for the failure, see the <code>FailureReason</code> field in the response to a <code>DescribeTrainingJobResponse</code> call.</p> </li> <li> <p> <code>Stopping</code> - The training job is stopping.</p> </li> <li> <p> <code>Stopped</code> - The training job has stopped.</p> </li> </ul> <p>For more detailed information, see <code>SecondaryStatus</code>. </p>
       secondary_status: 	 <p> Provides detailed information about the state of the training job. For detailed information about the secondary status of the training job, see <code>StatusMessage</code> under <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_SecondaryStatusTransition.html">SecondaryStatusTransition</a>.</p> <p>SageMaker provides primary statuses and secondary statuses that apply to each of them:</p> <dl> <dt>InProgress</dt> <dd> <ul> <li> <p> <code>Starting</code> - Starting the training job.</p> </li> <li> <p> <code>Downloading</code> - An optional stage for algorithms that support <code>File</code> training input mode. It indicates that data is being downloaded to the ML storage volumes.</p> </li> <li> <p> <code>Training</code> - Training is in progress.</p> </li> <li> <p> <code>Uploading</code> - Training is complete and the model artifacts are being uploaded to the S3 location.</p> </li> </ul> </dd> <dt>Completed</dt> <dd> <ul> <li> <p> <code>Completed</code> - The training job has completed.</p> </li> </ul> </dd> <dt>Failed</dt> <dd> <ul> <li> <p> <code>Failed</code> - The training job has failed. The reason for the failure is returned in the <code>FailureReason</code> field of <code>DescribeTrainingJobResponse</code>.</p> </li> </ul> </dd> <dt>Stopped</dt> <dd> <ul> <li> <p> <code>MaxRuntimeExceeded</code> - The job stopped because it exceeded the maximum allowed runtime.</p> </li> <li> <p> <code>Stopped</code> - The training job has stopped.</p> </li> </ul> </dd> <dt>Stopping</dt> <dd> <ul> <li> <p> <code>Stopping</code> - Stopping the training job.</p> </li> </ul> </dd> </dl> <important> <p>Valid values for <code>SecondaryStatus</code> are subject to change. </p> </important> <p>We no longer support the following secondary statuses:</p> <ul> <li> <p> <code>LaunchingMLInstances</code> </p> </li> <li> <p> <code>PreparingTrainingStack</code> </p> </li> <li> <p> <code>DownloadingTrainingImage</code> </p> </li> </ul>
       failure_reason: 	 <p>If the training job failed, the reason it failed.</p>
       hyper_parameters: 	 <p>Algorithm-specific parameters.</p>
       algorithm_specification: 	 <p>Information about the algorithm used for training, and algorithm metadata.</p>
       role_arn: 	 <p>The Amazon Web Services Identity and Access Management (IAM) role configured for the training job.</p>
       input_data_config: 	 <p>An array of <code>Channel</code> objects that describes each data input channel.</p> <p>Your input must be in the same Amazon Web Services region as your training job.</p>
       output_data_config: 	 <p>The S3 path where model artifacts that you configured when creating the job are stored. SageMaker creates subfolders for model artifacts.</p>
       resource_config: 	 <p>Resources, including ML compute instances and ML storage volumes, that are configured for model training.</p>
       vpc_config: 	 <p>A <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_VpcConfig.html">VpcConfig</a> object that specifies the VPC that this training job has access to. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/train-vpc.html">Protect Training Jobs by Using an Amazon Virtual Private Cloud</a>.</p>
       stopping_condition: 	 <p>Specifies a limit to how long a model training job can run. It also specifies how long a managed Spot training job has to complete. When the job reaches the time limit, SageMaker ends the training job. Use this API to cap model training costs.</p> <p>To stop a job, SageMaker sends the algorithm the <code>SIGTERM</code> signal, which delays job termination for 120 seconds. Algorithms can use this 120-second window to save the model artifacts, so the results of training are not lost. </p>
       creation_time: 	 <p>A timestamp that indicates when the training job was created.</p>
       training_start_time: 	 <p>Indicates the time when the training job starts on training instances. You are billed for the time interval between this time and the value of <code>TrainingEndTime</code>. The start time in CloudWatch Logs might be later than this time. The difference is due to the time it takes to download the training data and to the size of the training container.</p>
       training_end_time: 	 <p>Indicates the time when the training job ends on training instances. You are billed for the time interval between the value of <code>TrainingStartTime</code> and this time. For successful jobs and stopped jobs, this is the time after model artifacts are uploaded. For failed jobs, this is the time when SageMaker detects a job failure.</p>
       last_modified_time: 	 <p>A timestamp that indicates when the status of the training job was last modified.</p>
       secondary_status_transitions: 	 <p>A history of all of the secondary statuses that the training job has transitioned through.</p>
       final_metric_data_list: 	 <p>A list of final metric values that are set when the training job completes. Used only if the training job was configured to use metrics.</p>
       enable_network_isolation: 	 <p>If the <code>TrainingJob</code> was created with network isolation, the value is set to <code>true</code>. If network isolation is enabled, nodes can't communicate beyond the VPC they run in.</p>
       enable_inter_container_traffic_encryption: 	 <p>To encrypt all communications between ML compute instances in distributed training, choose <code>True</code>. Encryption provides greater security for distributed training, but training might take longer. How long it takes depends on the amount of communication between compute instances, especially if you use a deep learning algorithm in distributed training.</p>
       enable_managed_spot_training: 	 <p>When true, enables managed spot training using Amazon EC2 Spot instances to run training jobs instead of on-demand instances. For more information, see <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/model-managed-spot-training.html">Managed Spot Training</a>.</p>
       checkpoint_config
       training_time_in_seconds: 	 <p>The training time in seconds.</p>
       billable_time_in_seconds: 	 <p>The billable time in seconds.</p>
       debug_hook_config
       experiment_config
       debug_rule_configurations: 	 <p>Information about the debug rule configuration.</p>
       tensor_board_output_config
       debug_rule_evaluation_statuses: 	 <p>Information about the evaluation status of the rules for the training job.</p>
       profiler_config
       environment: 	 <p>The environment variables to set in the Docker container.</p>
       retry_strategy: 	 <p>The number of times to retry the job when the job fails due to an <code>InternalServerError</code>.</p>
       tags: 	 <p>An array of key-value pairs. You can use tags to categorize your Amazon Web Services resources in different ways, for example, by purpose, owner, or environment. For more information, see <a href="https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html">Tagging Amazon Web Services Resources</a>.</p>
    """

    training_job_name: Optional[str] = Unassigned()
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
    vpc_config: Optional[VpcConfig] = Unassigned()
    stopping_condition: Optional[StoppingCondition] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    training_start_time: Optional[datetime.datetime] = Unassigned()
    training_end_time: Optional[datetime.datetime] = Unassigned()
    last_modified_time: Optional[datetime.datetime] = Unassigned()
    secondary_status_transitions: Optional[List[SecondaryStatusTransition]] = (
        Unassigned()
    )
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
    debug_rule_evaluation_statuses: Optional[List[DebugRuleEvaluationStatus]] = (
        Unassigned()
    )
    profiler_config: Optional[ProfilerConfig] = Unassigned()
    environment: Optional[Dict[str, str]] = Unassigned()
    retry_strategy: Optional[RetryStrategy] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()


class TrialComponentSimpleSummary(Base):
    """
    TrialComponentSimpleSummary
         <p>A short summary of a trial component.</p>

        Attributes
       ----------------------
       trial_component_name: 	 <p>The name of the trial component.</p>
       trial_component_arn: 	 <p>The Amazon Resource Name (ARN) of the trial component.</p>
       trial_component_source
       creation_time: 	 <p>When the component was created.</p>
       created_by
    """

    trial_component_name: Optional[str] = Unassigned()
    trial_component_arn: Optional[str] = Unassigned()
    trial_component_source: Optional[TrialComponentSource] = Unassigned()
    creation_time: Optional[datetime.datetime] = Unassigned()
    created_by: Optional[UserContext] = Unassigned()


class Trial(Base):
    """
    Trial
         <p>The properties of a trial as returned by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p>

        Attributes
       ----------------------
       trial_name: 	 <p>The name of the trial.</p>
       trial_arn: 	 <p>The Amazon Resource Name (ARN) of the trial.</p>
       display_name: 	 <p>The name of the trial as displayed. If <code>DisplayName</code> isn't specified, <code>TrialName</code> is displayed.</p>
       experiment_name: 	 <p>The name of the experiment the trial is part of.</p>
       source
       creation_time: 	 <p>When the trial was created.</p>
       created_by: 	 <p>Who created the trial.</p>
       last_modified_time: 	 <p>Who last modified the trial.</p>
       last_modified_by
       metadata_properties
       tags: 	 <p>The list of tags that are associated with the trial. You can use <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API to search on the tags.</p>
       trial_component_summaries: 	 <p>A list of the components associated with the trial. For each component, a summary of the component's properties is included.</p>
    """

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
    tags: Optional[List[Tag]] = Unassigned()
    trial_component_summaries: Optional[List[TrialComponentSimpleSummary]] = (
        Unassigned()
    )


class TrialComponentSourceDetail(Base):
    """
    TrialComponentSourceDetail
         <p>Detailed information about the source of a trial component. Either <code>ProcessingJob</code> or <code>TrainingJob</code> is returned.</p>

        Attributes
       ----------------------
       source_arn: 	 <p>The Amazon Resource Name (ARN) of the source.</p>
       training_job: 	 <p>Information about a training job that's the source of a trial component.</p>
       processing_job: 	 <p>Information about a processing job that's the source of a trial component.</p>
       transform_job: 	 <p>Information about a transform job that's the source of a trial component.</p>
    """

    source_arn: Optional[str] = Unassigned()
    training_job: Optional[TrainingJob] = Unassigned()
    processing_job: Optional[ProcessingJob] = Unassigned()
    transform_job: Optional[TransformJob] = Unassigned()


class TrialComponent(Base):
    """
    TrialComponent
         <p>The properties of a trial component as returned by the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API.</p>

        Attributes
       ----------------------
       trial_component_name: 	 <p>The name of the trial component.</p>
       display_name: 	 <p>The name of the component as displayed. If <code>DisplayName</code> isn't specified, <code>TrialComponentName</code> is displayed.</p>
       trial_component_arn: 	 <p>The Amazon Resource Name (ARN) of the trial component.</p>
       source: 	 <p>The Amazon Resource Name (ARN) and job type of the source of the component.</p>
       status
       start_time: 	 <p>When the component started.</p>
       end_time: 	 <p>When the component ended.</p>
       creation_time: 	 <p>When the component was created.</p>
       created_by: 	 <p>Who created the trial component.</p>
       last_modified_time: 	 <p>When the component was last modified.</p>
       last_modified_by
       parameters: 	 <p>The hyperparameters of the component.</p>
       input_artifacts: 	 <p>The input artifacts of the component.</p>
       output_artifacts: 	 <p>The output artifacts of the component.</p>
       metrics: 	 <p>The metrics for the component.</p>
       metadata_properties
       source_detail: 	 <p>Details of the source of the component.</p>
       lineage_group_arn: 	 <p>The Amazon Resource Name (ARN) of the lineage group resource.</p>
       tags: 	 <p>The list of tags that are associated with the component. You can use <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API to search on the tags.</p>
       parents: 	 <p>An array of the parents of the component. A parent is a trial the component is associated with and the experiment the trial is part of. A component might not have any parents.</p>
       run_name: 	 <p>The name of the experiment run.</p>
    """

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
    parameters: Optional[Dict[str, TrialComponentParameterValue]] = Unassigned()
    input_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    output_artifacts: Optional[Dict[str, TrialComponentArtifact]] = Unassigned()
    metrics: Optional[List[TrialComponentMetricSummary]] = Unassigned()
    metadata_properties: Optional[MetadataProperties] = Unassigned()
    source_detail: Optional[TrialComponentSourceDetail] = Unassigned()
    lineage_group_arn: Optional[str] = Unassigned()
    tags: Optional[List[Tag]] = Unassigned()
    parents: Optional[List[Parent]] = Unassigned()
    run_name: Optional[str] = Unassigned()


class SearchRecord(Base):
    """
    SearchRecord
         <p>A single resource returned as part of the <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_Search.html">Search</a> API response.</p>

        Attributes
       ----------------------
       training_job: 	 <p>The properties of a training job.</p>
       experiment: 	 <p>The properties of an experiment.</p>
       trial: 	 <p>The properties of a trial.</p>
       trial_component: 	 <p>The properties of a trial component.</p>
       endpoint
       model_package
       model_package_group
       pipeline
       pipeline_execution
       feature_group
       feature_metadata: 	 <p>The feature metadata used to search through the features.</p>
       project: 	 <p>The properties of a project.</p>
       hyper_parameter_tuning_job: 	 <p>The properties of a hyperparameter tuning job.</p>
       model_card: 	 <p>An Amazon SageMaker Model Card that documents details about a machine learning model.</p>
       model
    """

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
    hyper_parameter_tuning_job: Optional[HyperParameterTuningJobSearchEntity] = (
        Unassigned()
    )
    model_card: Optional[ModelCard] = Unassigned()
    model: Optional[ModelDashboardModel] = Unassigned()


class VisibilityConditions(Base):
    """
    VisibilityConditions
         <p>The list of key-value pairs used to filter your search results. If a search result contains a key from your list, it is included in the final search response if the value associated with the key in the result matches the value you specified. If the value doesn't match, the result is excluded from the search response. Any resources that don't have a key from the list that you've provided will also be included in the search response.</p>

        Attributes
       ----------------------
       key: 	 <p>The key that specifies the tag that you're using to filter the search results. It must be in the following format: <code>Tags.&lt;key&gt;</code>.</p>
       value: 	 <p>The value for the tag that you're using to filter the search results.</p>
    """

    key: Optional[str] = Unassigned()
    value: Optional[str] = Unassigned()


class ServiceCatalogProvisioningUpdateDetails(Base):
    """
    ServiceCatalogProvisioningUpdateDetails
         <p>Details that you specify to provision a service catalog product. For information about service catalog, see <a href="https://docs.aws.amazon.com/servicecatalog/latest/adminguide/introduction.html">What is Amazon Web Services Service Catalog</a>. </p>

        Attributes
       ----------------------
       provisioning_artifact_id: 	 <p>The ID of the provisioning artifact.</p>
       provisioning_parameters: 	 <p>A list of key value pairs that you specify when you provision a product.</p>
    """

    provisioning_artifact_id: Optional[str] = Unassigned()
    provisioning_parameters: Optional[List[ProvisioningParameter]] = Unassigned()


class ThroughputConfigUpdate(Base):
    """
    ThroughputConfigUpdate
         <p>The new throughput configuration for the feature group. You can switch between on-demand and provisioned modes or update the read / write capacity of provisioned feature groups. You can switch a feature group to on-demand only once in a 24 hour period. </p>

        Attributes
       ----------------------
       throughput_mode: 	 <p>Target throughput mode of the feature group. Throughput update is an asynchronous operation, and the outcome should be monitored by polling <code>LastUpdateStatus</code> field in <code>DescribeFeatureGroup</code> response. You cannot update a feature group's throughput while another update is in progress. </p>
       provisioned_read_capacity_units: 	 <p>For provisioned feature groups with online store enabled, this indicates the read throughput you are billed for and can consume without throttling. </p>
       provisioned_write_capacity_units: 	 <p>For provisioned feature groups, this indicates the write throughput you are billed for and can consume without throttling. </p>
    """

    throughput_mode: Optional[str] = Unassigned()
    provisioned_read_capacity_units: Optional[int] = Unassigned()
    provisioned_write_capacity_units: Optional[int] = Unassigned()


class VariantProperty(Base):
    """
    VariantProperty
         <p>Specifies a production variant property type for an Endpoint.</p> <p>If you are updating an endpoint with the <code>RetainAllVariantProperties</code> option of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html">UpdateEndpointInput</a> set to <code>true</code>, the <code>VariantProperty</code> objects listed in the <code>ExcludeRetainedVariantProperties</code> parameter of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateEndpoint.html">UpdateEndpointInput</a> override the existing variant properties of the endpoint.</p>

        Attributes
       ----------------------
       variant_property_type: 	 <p>The type of variant property. The supported values are:</p> <ul> <li> <p> <code>DesiredInstanceCount</code>: Overrides the existing variant instance counts using the <code>InitialInstanceCount</code> values in the <code>ProductionVariants</code> of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html">CreateEndpointConfig</a>.</p> </li> <li> <p> <code>DesiredWeight</code>: Overrides the existing variant weights using the <code>InitialVariantWeight</code> values in the <code>ProductionVariants</code> of <a href="https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateEndpointConfig.html">CreateEndpointConfig</a>.</p> </li> <li> <p> <code>DataCaptureConfig</code>: (Not currently supported.)</p> </li> </ul>
    """

    variant_property_type: str


class InternalDependencyException(Base):
    """
    InternalDependencyException
         <p>Your request caused an exception with an internal dependency. Contact customer support. </p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class InternalFailure(Base):
    """
    InternalFailure
         <p> An internal failure occurred. </p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class InternalStreamFailure(Base):
    """
    InternalStreamFailure
         <p>The stream processing failed because of an unknown error, exception or failure. Try your request again.</p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class PayloadPart(Base):
    """
    PayloadPart
         <p>A wrapper for pieces of the payload that's returned in response to a streaming inference request. A streaming inference response consists of one or more payload parts. </p>

        Attributes
       ----------------------
       bytes: 	 <p>A blob that contains part of the response for your streaming inference request.</p>
    """

    bytes: Optional[Any] = Unassigned()


class ModelStreamError(Base):
    """
    ModelStreamError
         <p> An error occurred while streaming the response body. This error can have the following error codes:</p> <dl> <dt>ModelInvocationTimeExceeded</dt> <dd> <p>The model failed to finish sending the response within the timeout period allowed by Amazon SageMaker.</p> </dd> <dt>StreamBroken</dt> <dd> <p>The Transmission Control Protocol (TCP) connection between the client and the model was reset or closed.</p> </dd> </dl>

        Attributes
       ----------------------
       message
       error_code: 	 <p>This error can have the following error codes:</p> <dl> <dt>ModelInvocationTimeExceeded</dt> <dd> <p>The model failed to finish sending the response within the timeout period allowed by Amazon SageMaker.</p> </dd> <dt>StreamBroken</dt> <dd> <p>The Transmission Control Protocol (TCP) connection between the client and the model was reset or closed.</p> </dd> </dl>
    """

    message: Optional[str] = Unassigned()
    error_code: Optional[str] = Unassigned()


class ResponseStream(Base):
    """
    ResponseStream
         <p>A stream of payload parts. Each part contains a portion of the response for a streaming inference request.</p>

        Attributes
       ----------------------
       payload_part: 	 <p>A wrapper for pieces of the payload that's returned in response to a streaming inference request. A streaming inference response consists of one or more payload parts. </p>
       model_stream_error: 	 <p> An error occurred while streaming the response body. This error can have the following error codes:</p> <dl> <dt>ModelInvocationTimeExceeded</dt> <dd> <p>The model failed to finish sending the response within the timeout period allowed by Amazon SageMaker.</p> </dd> <dt>StreamBroken</dt> <dd> <p>The Transmission Control Protocol (TCP) connection between the client and the model was reset or closed.</p> </dd> </dl>
       internal_stream_failure: 	 <p>The stream processing failed because of an unknown error, exception or failure. Try your request again.</p>
    """

    payload_part: Optional[PayloadPart] = Unassigned()
    model_stream_error: Optional[ModelStreamError] = Unassigned()
    internal_stream_failure: Optional[InternalStreamFailure] = Unassigned()


class ModelError(Base):
    """
    ModelError
         <p> Model (owned by the customer in the container) returned 4xx or 5xx error code. </p>

        Attributes
       ----------------------
       message
       original_status_code: 	 <p> Original status code. </p>
       original_message: 	 <p> Original message. </p>
       log_stream_arn: 	 <p> The Amazon Resource Name (ARN) of the log stream. </p>
    """

    message: Optional[str] = Unassigned()
    original_status_code: Optional[int] = Unassigned()
    original_message: Optional[str] = Unassigned()
    log_stream_arn: Optional[str] = Unassigned()


class ModelNotReadyException(Base):
    """
    ModelNotReadyException
         <p>Either a serverless endpoint variant's resources are still being provisioned, or a multi-model endpoint is still downloading or loading the target model. Wait and try your request again.</p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class ServiceUnavailable(Base):
    """
    ServiceUnavailable
         <p> The service is unavailable. Try your call again. </p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()


class ValidationError(Base):
    """
    ValidationError
         <p> Inspect your request and try again. </p>

        Attributes
       ----------------------
       message
    """

    message: Optional[str] = Unassigned()
