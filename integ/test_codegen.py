import datetime

# import json
import logging
import time
import unittest
import pandas as pd
import os

from io import StringIO

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

from sagemaker_cleaner import handle_cleanup
from sagemaker_core.main.shapes import (
    AutoParameter,
    Autotune,
    ContainerDefinition,
    HyperParameterAlgorithmSpecification,
    HyperParameterTrainingJobDefinition,
    HyperParameterTuningJobConfig,
    HyperParameterTuningJobObjective,
    ParameterRanges,
    # ProductionVariant,
    # ProfilerConfig,
    ResourceLimits,
    TransformDataSource,
    TransformInput,
    TransformOutput,
    TransformResources,
    TransformS3DataSource,
)
from sagemaker_core.main.resources import (
    HyperParameterTuningJob,
    TrainingJob,
    TransformJob,
    AlgorithmSpecification,
    Channel,
    DataSource,
    S3DataSource,
    OutputDataConfig,
    ResourceConfig,
    StoppingCondition,
    Model,
    # EndpointConfig,
    # Endpoint,
)
from sagemaker_core.helper.session_helper import Session, get_execution_role

logger = logging.getLogger()

sagemaker_session = Session()
region = sagemaker_session.boto_region_name
role = get_execution_role()
bucket = sagemaker_session.default_bucket()

iris = load_iris()
iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
iris_df["target"] = iris.target

# Prepare Data
os.makedirs("./data", exist_ok=True)
iris_df = iris_df[["target"] + [col for col in iris_df.columns if col != "target"]]
train_data, test_data = train_test_split(iris_df, test_size=0.2, random_state=42)
train_data.to_csv("./data/train.csv", index=False, header=False)

# Upload Data
prefix = "DEMO-scikit-iris"
TRAIN_DATA = "train.csv"
DATA_DIRECTORY = "data"

train_input = sagemaker_session.upload_data(
    DATA_DIRECTORY, bucket=bucket, key_prefix="{}/{}".format(prefix, DATA_DIRECTORY)
)
s3_input_path = "s3://{}/{}/data/{}".format(bucket, prefix, TRAIN_DATA)
s3_output_path = "s3://{}/{}/output".format(bucket, prefix)
image = "433757028032.dkr.ecr.us-west-2.amazonaws.com/xgboost:latest"

# To be replaced with representing strings when executing from personal account
SUBNET_ONE = os.environ["SUBNET_ONE"]
SUBNET_TWO = os.environ["SUBNET_TWO"]
SECURITY_GROUP_ONE = os.environ["SECURITY_GROUP_ONE"]


class TestSageMakerCore(unittest.TestCase):

    # def test_training_and_inference(self):
    #     os.environ["SAGEMAKER_CORE_ADMIN_CONFIG_OVERRIDE"] = ""
    #     job_name_v3 = "xgboost-iris-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    #     training_job = TrainingJob.create(
    #         training_job_name=job_name_v3,
    #         hyper_parameters={
    #             "objective": "multi:softmax",
    #             "num_class": "3",
    #             "num_round": "10",
    #             "eval_metric": "merror",
    #         },
    #         algorithm_specification=AlgorithmSpecification(
    #             training_image=image, training_input_mode="File"
    #         ),
    #         role_arn=role,
    #         input_data_config=[
    #             Channel(
    #                 channel_name="train",
    #                 content_type="csv",
    #                 compression_type="None",
    #                 record_wrapper_type="None",
    #                 data_source=DataSource(
    #                     s3_data_source=S3DataSource(
    #                         s3_data_type="S3Prefix",
    #                         s3_uri=s3_input_path,
    #                         s3_data_distribution_type="FullyReplicated",
    #                     )
    #                 ),
    #             )
    #         ],
    #         profiler_config=ProfilerConfig(profiling_interval_in_milliseconds=1000),
    #         output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
    #         resource_config=ResourceConfig(
    #             instance_type="ml.m4.xlarge",
    #             instance_count=1,
    #             volume_size_in_gb=30,
    #         ),
    #         stopping_condition=StoppingCondition(max_runtime_in_seconds=600),
    #     )
    #     training_job.wait()

    #     fetched_training_job = TrainingJob.get(training_job_name=job_name_v3)
    #     assert fetched_training_job.output_data_config.s3_output_path == s3_output_path
    #     assert fetched_training_job.profiler_config.profiling_interval_in_milliseconds == 1000

    #     creation_time_after = datetime.datetime.now() - datetime.timedelta(days=5)

    #     resource_iterator = TrainingJob.get_all(creation_time_after=creation_time_after)
    #     training_jobs = [job.training_job_name for job in resource_iterator]

    #     assert len(training_jobs) > 1
    #     assert job_name_v3 in training_jobs

    #     model_data_url = fetched_training_job.model_artifacts.s3_model_artifacts

    #     key = f'xgboost-iris-test-{time.strftime("%H-%M-%S", time.gmtime())}'
    #     print("Key:", key)

    #     model = Model.create(
    #         model_name=key,
    #         primary_container=ContainerDefinition(
    #             image=image,
    #             model_data_url=model_data_url,
    #         ),
    #         execution_role_arn=role,
    #     )

    #     # Testing Resource Chaining
    #     endpoint_config = EndpointConfig.create(
    #         endpoint_config_name=key,
    #         production_variants=[
    #             ProductionVariant(
    #                 variant_name=key,
    #                 initial_instance_count=1,
    #                 instance_type="ml.m5.xlarge",
    #                 model_name=model,  # Pass `Model`` object created above
    #             )
    #         ],
    #     )
    #     endpoint: Endpoint = Endpoint.create(
    #         endpoint_name=key,
    #         # Pass `EndpointConfig` object created above
    #         endpoint_config_name=endpoint_config,
    #     )
    #     endpoint.wait_for_status("InService")

    # def test_intelligent_defaults(self):
    #     os.environ["SAGEMAKER_CORE_ADMIN_CONFIG_OVERRIDE"] = (
    #         self._setup_intelligent_default_configs_and_fetch_path()
    #     )
    #     job_name_v3 = "xgboost-test-intelligent-default-" + time.strftime(
    #         "%Y-%m-%d-%H-%M-%S", time.gmtime()
    #     )

    #     training_job = TrainingJob.create(
    #         training_job_name=job_name_v3,
    #         hyper_parameters={
    #             "objective": "multi:softmax",
    #             "num_class": "3",
    #             "num_round": "10",
    #             "eval_metric": "merror",
    #         },
    #         algorithm_specification=AlgorithmSpecification(
    #             training_image=image, training_input_mode="File"
    #         ),
    #         role_arn=role,
    #         input_data_config=[
    #             Channel(
    #                 channel_name="train",
    #                 content_type="csv",
    #                 compression_type="None",
    #                 record_wrapper_type="None",
    #                 data_source=DataSource(
    #                     s3_data_source=S3DataSource(
    #                         s3_data_type="S3Prefix",
    #                         s3_uri=s3_input_path,
    #                         s3_data_distribution_type="FullyReplicated",
    #                     )
    #                 ),
    #             )
    #         ],
    #         output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
    #         resource_config=ResourceConfig(
    #             instance_type="ml.m4.xlarge",
    #             instance_count=1,
    #             volume_size_in_gb=30,
    #         ),
    #         stopping_condition=StoppingCondition(max_runtime_in_seconds=600),
    #     )
    #     training_job.wait()

    #     assert training_job.vpc_config.subnets == [
    #         SUBNET_ONE,
    #         SUBNET_TWO,
    #     ]
    #     assert training_job.vpc_config.security_group_ids == [SECURITY_GROUP_ONE]

    # def tearDown(self) -> None:
    #     handle_cleanup()

    # def _setup_intelligent_default_configs_and_fetch_path(self) -> str:
    #     DEFAULTS_CONTENT = {
    #         "SchemaVesion": "1.0",
    #         "SageMaker": {
    #             "PythonSDK": {
    #                 "Resources": {
    #                     "GlobalDefaults": {
    #                         "vpc_config": {
    #                             "security_group_ids": [SECURITY_GROUP_ONE],
    #                             "subnets": [SUBNET_ONE, SUBNET_TWO],
    #                         }
    #                     },
    #                     "TrainingJob": {
    #                         "role_arn": role,
    #                         "output_data_config": {"s3_output_path": s3_output_path},
    #                     },
    #                 }
    #             }
    #         },
    #     }

    #     path_to_defaults = os.path.join(DATA_DIRECTORY, "defaults.json")
    #     with open(os.path.join(DATA_DIRECTORY, "defaults.json"), "w") as f:
    #         json.dump(DEFAULTS_CONTENT, f, indent=4)
    #     return path_to_defaults

    def test_hyperparameter_tuning_job_and_transform_job(self):
        ### Data preparation for test_hyperparameter_tuning_job and test_transform_job
        data = sagemaker_session.read_s3_file(
            f"sagemaker-example-files-prod-{region}", "datasets/tabular/synthetic/churn.txt"
        )

        df = pd.read_csv(StringIO(data))

        df = df.drop("Phone", axis=1)
        df["Area Code"] = df["Area Code"].astype(object)
        df = df.drop(["Day Charge", "Eve Charge", "Night Charge", "Intl Charge"], axis=1)

        model_data = pd.get_dummies(df)
        model_data = pd.concat(
            [
                model_data["Churn?_True."],
                model_data.drop(["Churn?_False.", "Churn?_True."], axis=1),
            ],
            axis=1,
        )
        model_data = model_data.astype(float)

        train_data2, validation_data = train_test_split(model_data, test_size=0.33, random_state=42)

        validation_data, test_data2 = train_test_split(
            validation_data, test_size=0.33, random_state=42
        )

        test_target_column = test_data2["Churn?_True."]
        test_data2.drop(["Churn?_True."], axis=1, inplace=True)

        train_data2.to_csv("train2.csv", header=False, index=False)
        validation_data.to_csv("validation.csv", header=False, index=False)
        test_data2.to_csv("test.csv", header=False, index=False)

        s3_train_input = sagemaker_session.upload_data("train2.csv", bucket)
        s3_validation_input = sagemaker_session.upload_data("validation.csv", bucket)
        s3_test_input = sagemaker_session.upload_data("test.csv", bucket)

        image2 = "246618743249.dkr.ecr.us-west-2.amazonaws.com/sagemaker-xgboost:1.7-1"
        instance_type = "ml.m4.xlarge"
        instance_count = 1
        volume_size_in_gb = 30
        max_runtime_in_seconds = 600

        ############ Create training jobs resource
        job_name = "xgboost-churn-" + time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.gmtime()
        )  # Name of training job
        instance_type = "ml.m4.xlarge"  # SageMaker instance type to use for training
        instance_count = 1  # Number of instances to use for training
        volume_size_in_gb = 30  # Amount of storage to allocate to training job
        max_runtime_in_seconds = 600  # Maximum runtimt. Job exits if it doesn't finish before this
        s3_output_path = f"s3://{bucket}"  # bucket and optional prefix where the training job stores output artifacts, like model artifact.

        hyper_parameters = {
            "max_depth": "5",
            "eta": "0.2",
            "gamma": "4",
            "min_child_weight": "6",
            "subsample": "0.8",
            "verbosity": "0",
            "objective": "binary:logistic",
            "num_round": "100",
        }

        training_job = TrainingJob.create(
            training_job_name=job_name,
            hyper_parameters=hyper_parameters,
            algorithm_specification=AlgorithmSpecification(
                training_image=image2, training_input_mode="File"
            ),
            role_arn=role,
            input_data_config=[
                Channel(
                    channel_name="train",
                    content_type="csv",
                    data_source=DataSource(
                        s3_data_source=S3DataSource(
                            s3_data_type="S3Prefix",
                            s3_uri=s3_train_input,
                            s3_data_distribution_type="FullyReplicated",
                        )
                    ),
                ),
                Channel(
                    channel_name="validation",
                    content_type="csv",
                    data_source=DataSource(
                        s3_data_source=S3DataSource(
                            s3_data_type="S3Prefix",
                            s3_uri=s3_validation_input,
                            s3_data_distribution_type="FullyReplicated",
                        )
                    ),
                ),
            ],
            output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
            resource_config=ResourceConfig(
                instance_type=instance_type,
                instance_count=instance_count,
                volume_size_in_gb=volume_size_in_gb,
            ),
            stopping_condition=StoppingCondition(max_runtime_in_seconds=max_runtime_in_seconds),
        )

        training_job.wait()

        ########### Create and test HyperParameterTuningJob
        tuning_job_name = "xgboost-tune-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
        max_number_of_training_jobs = 50
        max_parallel_training_jobs = 5
        max_runtime_in_seconds = 3600
        s3_output_path = f"s3://{bucket}/tuningjob"

        hyper_parameter_training_job_definition = HyperParameterTrainingJobDefinition(
            role_arn=role,
            algorithm_specification=HyperParameterAlgorithmSpecification(
                training_image=image2, training_input_mode="File"
            ),
            input_data_config=[
                Channel(
                    channel_name="train",
                    content_type="csv",
                    data_source=DataSource(
                        s3_data_source=S3DataSource(
                            s3_data_type="S3Prefix",
                            s3_uri=s3_train_input,
                            s3_data_distribution_type="FullyReplicated",
                        )
                    ),
                ),
                Channel(
                    channel_name="validation",
                    content_type="csv",
                    data_source=DataSource(
                        s3_data_source=S3DataSource(
                            s3_data_type="S3Prefix",
                            s3_uri=s3_validation_input,
                            s3_data_distribution_type="FullyReplicated",
                        )
                    ),
                ),
            ],
            output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
            stopping_condition=StoppingCondition(max_runtime_in_seconds=max_runtime_in_seconds),
            resource_config=ResourceConfig(
                instance_type=instance_type,
                instance_count=instance_count,
                volume_size_in_gb=volume_size_in_gb,
            ),
        )

        tuning_job_config = HyperParameterTuningJobConfig(
            strategy="Bayesian",
            hyper_parameter_tuning_job_objective=HyperParameterTuningJobObjective(
                type="Maximize", metric_name="validation:auc"
            ),
            resource_limits=ResourceLimits(
                max_number_of_training_jobs=max_number_of_training_jobs,
                max_parallel_training_jobs=max_parallel_training_jobs,
                max_runtime_in_seconds=3600,
            ),
            training_job_early_stopping_type="Auto",
            parameter_ranges=ParameterRanges(
                auto_parameters=[
                    AutoParameter(name="max_depth", value_hint="5"),
                    AutoParameter(name="eta", value_hint="0.1"),
                    AutoParameter(name="gamma", value_hint="8"),
                    AutoParameter(name="min_child_weight", value_hint="2"),
                    AutoParameter(name="subsample", value_hint="0.5"),
                    AutoParameter(name="num_round", value_hint="50"),
                ]
            ),
        )

        tuning_job = HyperParameterTuningJob.create(
            hyper_parameter_tuning_job_name=tuning_job_name,
            autotune=Autotune(mode="Enabled"),
            training_job_definition=hyper_parameter_training_job_definition,
            hyper_parameter_tuning_job_config=tuning_job_config,
        )

        tuning_job.wait()

        fetch_tuning_job = HyperParameterTuningJob.get(
            hyper_parameter_tuning_job_name=tuning_job_name
        )
        assert (
            fetch_tuning_job.training_job_definition.output_data_config.s3_output_path
            == s3_output_path
        )
        assert fetch_tuning_job.hyper_parameter_tuning_job_config.strategy == "Bayesian"

        creation_time_after = datetime.datetime.now() - datetime.timedelta(days=5)

        resource_iterator = HyperParameterTuningJob.get_all(creation_time_after=creation_time_after)
        tuning_jobs = [job.hyper_parameter_tuning_job_name for job in resource_iterator]

        assert len(tuning_jobs) > 0
        assert tuning_job_name in tuning_jobs

        ########### Create Model resource for transform job use
        model_s3_uri = TrainingJob.get(
            tuning_job.best_training_job.training_job_name
        ).model_artifacts.s3_model_artifacts
        model_name_for_tranformjob = (
            f'customer-churn-xgboost-{time.strftime("%H-%M-%S", time.gmtime())}'
        )
        customer_churn_model = Model.create(
            model_name=model_name_for_tranformjob,
            primary_container=ContainerDefinition(image=image2, model_data_url=model_s3_uri),
            execution_role_arn=role,
        )

        ########### Create and test Transform jobs
        s3_output_path = f"s3://{bucket}/transform"
        transform_job_name = "churn-prediction" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

        transform_job = TransformJob.create(
            transform_job_name=transform_job_name,
            model_name=model_name_for_tranformjob,
            transform_input=TransformInput(
                data_source=TransformDataSource(
                    s3_data_source=TransformS3DataSource(
                        s3_data_type="S3Prefix", s3_uri=s3_test_input
                    )
                ),
                content_type="text/csv",
            ),
            transform_output=TransformOutput(s3_output_path=s3_output_path),
            transform_resources=TransformResources(
                instance_type=instance_type, instance_count=instance_count
            ),
        )

        transform_job.wait()

        fetch_transform_job = TransformJob.get(transform_job_name=transform_job_name)
        assert fetch_transform_job.transform_output.s3_output_path == s3_output_path

        creation_time_after = datetime.datetime.now() - datetime.timedelta(days=5)

        resource_iterator = TransformJob.get_all(creation_time_after=creation_time_after)
        transform_jobs = [job.transform_job_name for job in resource_iterator]

        assert len(transform_jobs) > 0
        assert transform_job_name in transform_jobs
