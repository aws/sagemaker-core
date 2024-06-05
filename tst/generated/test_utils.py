import pytest
import datetime
import logging
from unittest.mock import Mock, patch, call
from src.generated.resources import TrainingJob, DataQualityJobDefinition
from src.generated.utils import *


LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN = {
    "TrainingJobSummaries": [
        {
            "TrainingJobName": "xgboost-iris-1",
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:111111111111:training-job/xgboost-iris-1",
            "CreationTime": datetime.datetime.now(),
            "TrainingEndTime": datetime.datetime.now(),
            "LastModifiedTime": datetime.datetime.now(),
            "TrainingJobStatus": "Completed",
        },
        {
            "TrainingJobName": "xgboost-iris-2",
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:111111111111:training-job/xgboost-iris-2",
            "CreationTime": datetime.datetime.now(),
            "TrainingEndTime": datetime.datetime.now(),
            "LastModifiedTime": datetime.datetime.now(),
            "TrainingJobStatus": "Completed",
        },
    ],
    "NextToken": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
}

LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN = {
    "TrainingJobSummaries": [
        {
            "TrainingJobName": "xgboost-iris-1",
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:111111111111:training-job/xgboost-iris-1",
            "CreationTime": datetime.datetime.now(),
            "TrainingEndTime": datetime.datetime.now(),
            "LastModifiedTime": datetime.datetime.now(),
            "TrainingJobStatus": "Completed",
        },
        {
            "TrainingJobName": "xgboost-iris-2",
            "TrainingJobArn": "arn:aws:sagemaker:us-west-2:111111111111:training-job/xgboost-iris-2",
            "CreationTime": datetime.datetime.now(),
            "TrainingEndTime": datetime.datetime.now(),
            "LastModifiedTime": datetime.datetime.now(),
            "TrainingJobStatus": "Completed",
        },
    ],
}

LIST_DATA_QUALITY_JOB_DEFINITION_RESPONSE_WITHOUT_NEXT_TOKEN = {
    "JobDefinitionSummaries": [
        {
            "MonitoringJobDefinitionName": "data-quality-job-definition-1",
            "MonitoringJobDefinitionArn": "arn:aws:sagemaker:us-west-2:111111111111:data-quality-job-definition/data-quality-job-definition-1",
            "CreationTime": datetime.datetime.now(),
            "EndpointName": "sagemaker-tensorflow-serving-1",
        },
        {
            "MonitoringJobDefinitionName": "data-quality-job-definition-2",
            "MonitoringJobDefinitionArn": "arn:aws:sagemaker:us-west-2:111111111111:data-quality-job-definition/data-quality-job-definition-2",
            "CreationTime": datetime.datetime.now(),
            "EndpointName": "sagemaker-tensorflow-serving-2",
        },
    ],
}


@pytest.fixture
def resource_iterator():
    client = Mock()
    resource_cls = TrainingJob
    iterator = ResourceIterator(
        client=client,
        summaries_key="TrainingJobSummaries",
        summary_name="TrainingJobSummary",
        resource_cls=resource_cls,
        list_method="list_training_jobs",
        list_method_kwargs={},
        custom_key_mapping=None,
    )

    return iterator, client, resource_cls


@pytest.fixture
def resource_iterator_with_custom_key_mapping():
    client = Mock()
    resource_cls = DataQualityJobDefinition
    custom_key_mapping = {
        "monitoring_job_definition_name": "job_definition_name",
        "monitoring_job_definition_arn": "job_definition_arn",
    }
    iterator = ResourceIterator(
        client=client,
        list_method="list_data_quality_job_definitions",
        summaries_key="JobDefinitionSummaries",
        summary_name="MonitoringJobDefinitionSummary",
        resource_cls=DataQualityJobDefinition,
        custom_key_mapping=custom_key_mapping,
        list_method_kwargs={},
    )
    return iterator, client, resource_cls


def test_next_with_summaries_in_summary_list(resource_iterator):
    iterator, _, _ = resource_iterator
    iterator.index = 0
    iterator.summary_list = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN["TrainingJobSummaries"]
    expected_training_job_data = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN[
        "TrainingJobSummaries"
    ][0]

    with patch.object(TrainingJob, "refresh") as mock_refresh:
        next_item = next(iterator)
        assert isinstance(next_item, TrainingJob)
        assert mock_refresh.call_count == 1

        assert next_item.training_job_name == expected_training_job_data["TrainingJobName"]
        assert next_item.training_job_arn == expected_training_job_data["TrainingJobArn"]
        assert next_item.creation_time == expected_training_job_data["CreationTime"]
        assert next_item.training_end_time == expected_training_job_data["TrainingEndTime"]
        assert next_item.last_modified_time == expected_training_job_data["LastModifiedTime"]
        assert next_item.training_job_status == expected_training_job_data["TrainingJobStatus"]


def test_next_reached_end_of_summary_list_without_next_token(resource_iterator):
    iterator, _, _ = resource_iterator
    iterator.summary_list = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN["TrainingJobSummaries"]
    iterator.index = len(iterator.summary_list)

    with pytest.raises(StopIteration):
        next(iterator)


def test_next_client_returns_empty_list(resource_iterator):
    iterator, client, _ = resource_iterator
    client.list_training_jobs.return_value = {"TrainingJobSummaries": []}

    with pytest.raises(StopIteration):
        next(iterator)


def test_next_without_next_token(resource_iterator):
    iterator, client, _ = resource_iterator
    client.list_training_jobs.return_value = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN

    with patch.object(TrainingJob, "refresh") as mock_refresh:
        index = 0
        while True:
            try:
                next_item = next(iterator)
                assert isinstance(next_item, TrainingJob)

                expected_training_job_data = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN[
                    "TrainingJobSummaries"
                ][index]
                assert next_item.training_job_name == expected_training_job_data["TrainingJobName"]
                assert next_item.training_job_arn == expected_training_job_data["TrainingJobArn"]
                assert next_item.creation_time == expected_training_job_data["CreationTime"]
                assert next_item.training_end_time == expected_training_job_data["TrainingEndTime"]
                assert (
                    next_item.last_modified_time == expected_training_job_data["LastModifiedTime"]
                )
                assert (
                    next_item.training_job_status == expected_training_job_data["TrainingJobStatus"]
                )
                index += 1
            except StopIteration:
                break

        assert mock_refresh.call_count == 2
        assert client.list_training_jobs.call_args_list == [call()]


def test_next_with_next_token(resource_iterator):
    iterator, client, _ = resource_iterator
    client.list_training_jobs.side_effect = [
        LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN,
        LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN,
    ]

    with patch.object(TrainingJob, "refresh") as mock_refresh:
        index = 0
        while True:
            try:
                next_item = next(iterator)
                assert isinstance(next_item, TrainingJob)

                if index < len(LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN["TrainingJobSummaries"]):
                    expected_training_job_data = LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN[
                        "TrainingJobSummaries"
                    ][index]
                else:
                    expected_training_job_data = LIST_TRAINING_JOB_RESPONSE_WITHOUT_NEXT_TOKEN[
                        "TrainingJobSummaries"
                    ][
                        index
                        - len(LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN["TrainingJobSummaries"])
                    ]

                assert next_item.training_job_name == expected_training_job_data["TrainingJobName"]
                assert next_item.training_job_arn == expected_training_job_data["TrainingJobArn"]
                assert next_item.creation_time == expected_training_job_data["CreationTime"]
                assert next_item.training_end_time == expected_training_job_data["TrainingEndTime"]
                assert (
                    next_item.last_modified_time == expected_training_job_data["LastModifiedTime"]
                )
                assert (
                    next_item.training_job_status == expected_training_job_data["TrainingJobStatus"]
                )
                index += 1
            except StopIteration:
                break

        assert mock_refresh.call_count == 4
        assert client.list_training_jobs.call_args_list == [
            call(),
            call(NextToken=LIST_TRAINING_JOB_RESPONSE_WITH_NEXT_TOKEN["NextToken"]),
        ]


def test_next_with_custom_key_mapping(resource_iterator_with_custom_key_mapping):
    iterator, client, _ = resource_iterator_with_custom_key_mapping
    client.list_data_quality_job_definitions.return_value = (
        LIST_DATA_QUALITY_JOB_DEFINITION_RESPONSE_WITHOUT_NEXT_TOKEN
    )
    iterator.index = 0
    with patch.object(DataQualityJobDefinition, "refresh") as mock_refresh:
        index = 0
        while True:
            try:
                next_item = next(iterator)
                assert isinstance(next_item, DataQualityJobDefinition)
                print(next_item)
                expected_data_quality_job_definition_data = (
                    LIST_DATA_QUALITY_JOB_DEFINITION_RESPONSE_WITHOUT_NEXT_TOKEN[
                        "JobDefinitionSummaries"
                    ][index]
                )

                assert (
                    next_item.job_definition_name
                    == expected_data_quality_job_definition_data["MonitoringJobDefinitionName"]
                )
                assert (
                    next_item.job_definition_arn
                    == expected_data_quality_job_definition_data["MonitoringJobDefinitionArn"]
                )
                assert (
                    next_item.creation_time
                    == expected_data_quality_job_definition_data["CreationTime"]
                )
                assert not hasattr(next_item, "endpoint_name")
                index += 1
            except StopIteration:
                break

        assert mock_refresh.call_count == 2
        assert client.list_data_quality_job_definitions.call_args_list == [call()]

def test_configure_logging_with_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    configure_logging()
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_with_debug_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    configure_logging()
    assert logging.getLogger().level == logging.DEBUG


def test_configure_logging_with_invalid_log_level():
    with pytest.raises(AttributeError):
        configure_logging("INVALID_LOG_LEVEL")


def test_configure_logging_with_explicit_log_level():
    configure_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
