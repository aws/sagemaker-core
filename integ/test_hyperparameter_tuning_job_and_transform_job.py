import datetime
import logging
import time
import unittest
import pandas as pd
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
)
from sagemaker_core.helper.session_helper import Session, get_execution_role

logger = logging.getLogger()

sagemaker_session = Session()
region = sagemaker_session.boto_region_name
role = get_execution_role()
bucket = sagemaker_session.default_bucket()

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

validation_data, test_data2 = train_test_split(validation_data, test_size=0.33, random_state=42)

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


class TestSageMakerCore(unittest.TestCase):

    def test_hyperparameter_tuning_job_and_transform_job(self):
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
