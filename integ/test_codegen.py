import datetime
import json
import logging
import time
import unittest
import pandas as pd
import os

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sagemaker import get_execution_role, Session, image_uris

from sagemaker_core.generated.utils import Unassigned
from sagemaker_core.generated.shapes import (
    ClusterInstanceGroupSpecification,
    ClusterLifeCycleConfig,
    ContainerDefinition,
    ProductionVariant,
)
from sagemaker_core.generated.resources import (
    TrainingJob,
    AlgorithmSpecification,
    Channel,
    DataSource,
    S3DataSource,
    OutputDataConfig,
    ResourceConfig,
    StoppingCondition,
    Cluster,
    Model,
    EndpointConfig,
    Endpoint,
)

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
image = image_uris.retrieve(framework="xgboost", region=region, version="latest")


# To be replaced with representing strings when executing from personal account
SUBNET_ONE = os.environ['SUBNET_ONE']
SUBNET_TWO = os.environ['SUBNET_TWO']
SECURITY_GROUP_ONE = os.environ['SECURITY_GROUP_ONE']

logger.warning("Completed Setup steps")

class TestSageMakerCore(unittest.TestCase):
    def test_training_and_inference(self):

        job_name_v3 = "xgboost-iris-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
        training_job = TrainingJob.create(
            training_job_name=job_name_v3,
            hyper_parameters={
                "objective": "multi:softmax",
                "num_class": "3",
                "num_round": "10",
                "eval_metric": "merror",
            },
            algorithm_specification=AlgorithmSpecification(
                training_image=image, training_input_mode="File"
            ),
            role_arn=role,
            input_data_config=[
                Channel(
                    channel_name="train",
                    content_type="csv",
                    compression_type="None",
                    record_wrapper_type="None",
                    data_source=DataSource(
                        s3_data_source=S3DataSource(
                            s3_data_type="S3Prefix",
                            s3_uri=s3_input_path,
                            s3_data_distribution_type="FullyReplicated",
                        )
                    ),
                )
            ],
            output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
            resource_config=ResourceConfig(
                instance_type="ml.m4.xlarge",
                instance_count=2,
                volume_size_in_gb=30,
                keep_alive_period_in_seconds=300,
            ),
            stopping_condition=StoppingCondition(max_runtime_in_seconds=600),
        )

        training_job.wait()

        fetched_training_job = TrainingJob.get(training_job_name=job_name_v3)
        assert fetched_training_job.output_data_config.s3_output_path == s3_output_path
        assert fetched_training_job.profiler_config == Unassigned()

        # fetched_training_job.update(profiler_config=ProfilerConfigForUpdate(disable_profiler=False))

        # assert TrainingJob.get(training_job_name=job_name_v3).profiler_config.disable_profiler == False

        creation_time_after = datetime.datetime.now() - datetime.timedelta(days=5)

        resource_iterator = TrainingJob.get_all(creation_time_after=creation_time_after)
        training_jobs = [job.training_job_name for job in resource_iterator]

        assert len(training_jobs) > 1
        assert job_name_v3 in training_jobs

        model_data_url = fetched_training_job.model_artifacts.s3_model_artifacts

        key = f'xgboost-iris-{time.strftime("%H-%M-%S", time.gmtime())}'
        print("Key:", key)

        model = Model.create(
            model_name=key,
            primary_container=ContainerDefinition(
                image=image,
                model_data_url=model_data_url,
            ),
            execution_role_arn=role,
        )
        endpoint_config = EndpointConfig.create(
            endpoint_config_name=key,
            production_variants=[
                ProductionVariant(
                    variant_name=key,
                    initial_instance_count=1,
                    instance_type="ml.m5.xlarge",
                    model_name=model,  # Pass `Model`` object created above
                )
            ],
        )

        endpoint: Endpoint = Endpoint.create(
            endpoint_name=key,
            endpoint_config_name=endpoint_config,  # Pass `EndpointConfig` object created above
        )
        endpoint.wait_for_status("InService")


    def test_intelligent_defaults(self):
        os.environ["SAGEMAKER_ADMIN_CONFIG_OVERRIDE"] = (
            self._setup_intelligent_default_configs_and_fetch_path()
        )
        job_name_v3 = "xgboost-cluster-" + time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

        training_job = TrainingJob.create(
                training_job_name=job_name_v3,
                hyper_parameters={
                    "objective": "multi:softmax",
                    "num_class": "3",
                    "num_round": "10",
                    "eval_metric": "merror",
                },
                algorithm_specification=AlgorithmSpecification(
                    training_image=image, training_input_mode="File"
                ),
                role_arn=role,
                input_data_config=[
                    Channel(
                        channel_name="train",
                        content_type="csv",
                        compression_type="None",
                        record_wrapper_type="None",
                        data_source=DataSource(
                            s3_data_source=S3DataSource(
                                s3_data_type="S3Prefix",
                                s3_uri=s3_input_path,
                                s3_data_distribution_type="FullyReplicated",
                            )
                        ),
                    )
                ],
                output_data_config=OutputDataConfig(s3_output_path=s3_output_path),
                resource_config=ResourceConfig(
                    instance_type="ml.m4.xlarge",
                    instance_count=2,
                    volume_size_in_gb=30,
                    keep_alive_period_in_seconds=300,
                ),
                stopping_condition=StoppingCondition(max_runtime_in_seconds=600),
            )
        training_job.wait()

        assert training_job.vpc_config.subnets == [
            SUBNET_ONE,
            SUBNET_TWO,
        ]
        assert training_job.vpc_config.security_group_ids == [SECURITY_GROUP_ONE]

    def _setup_intelligent_default_configs_and_fetch_path(self) -> str:
        DEFAULTS_CONTENT = {
            "SchemaVesion": "1.0",
            "SageMaker": {
                "PythonSDK": {
                    "Resources": {
                        "GlobalDefaults": {
                            "vpc_config": {
                                "security_group_ids": [SECURITY_GROUP_ONE],
                                "subnets": [
                                    SUBNET_ONE,
                                    SUBNET_TWO
                                ],
                            }
                        },
                        "TrainingJob": {
                            "role_arn": role,
                            "output_data_config": {"s3_output_path": s3_output_path},
                        },
                    }
                }
            },
        }

        path_to_defaults = os.path.join(DATA_DIRECTORY, "defaults.json")
        with open(os.path.join(DATA_DIRECTORY, "defaults.json"), "w") as f:
            json.dump(DEFAULTS_CONTENT, f, indent=4)
        return path_to_defaults
