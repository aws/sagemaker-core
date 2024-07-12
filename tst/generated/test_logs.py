import botocore
import pytest
from unittest.mock import patch, MagicMock
from sagemaker_core.main.logs import LogStreamHandler, MultiLogStreamHandler

@patch('sagemaker_core.generated.logs.cw_client.get_log_events', autospec=True)
def test_single_stream_handler_get_latest(mock_get_log_events):
    mock_get_log_events.side_effect = [
        {
            "nextForwardToken": "nextToken1",
            "events": [
                {
                    "ingestionTime": 123456789,
                    "message": "test message",
                    "timestamp": 123456789
                }
            ]
        },
        {
            "nextForwardToken": "nextToken2",
            "events": []
        }
    ]
    
    log_stream_handler = LogStreamHandler("logGroupName", "logStreamName")
    events = log_stream_handler.get_latest_log_events()
    
    result = next(events)

    assert result == (
        "logStreamName", 
        {
            "ingestionTime": 123456789,
            "message": "test message",
            "timestamp": 123456789
        }
    )
    
    mock_get_log_events.assert_called_once_with(
        logGroupName="logGroupName",
        logStreamName="logStreamName",
        startFromHead=True
    )
    
    with pytest.raises(StopIteration):
        next(events)
    

@patch('sagemaker_core.generated.logs.MultiLogStreamHandler.ready', autospec=True)
def test_multi_stream_handler_get_latest(mock_ready):
    mock_ready.return_value = True
    
    mock_stream = MagicMock(spec=LogStreamHandler)
    mock_stream.get_latest_log_events.return_value = iter([
        ("streamName", {
            "ingestionTime": 123456789,
            "message": "test message",
            "timestamp": 123456789
        })
    ])

    
    mulit_log_stream_handler = MultiLogStreamHandler("log_group_name", "training_job_name", 1)
    mulit_log_stream_handler.streams = [mock_stream]
    
    events = mulit_log_stream_handler.get_latest_log_events()
    
    result = next(events)
    
    assert result == (
        "streamName", 
        {
            "ingestionTime": 123456789,
            "message": "test message",
            "timestamp": 123456789
        }
    )  
    
    with pytest.raises(StopIteration):
        next(events)

  
@patch('sagemaker_core.generated.logs.cw_client.describe_log_streams', autospec=True)
def test_ready(mock_describe_log_streams):
    mock_describe_log_streams.return_value = {
        'logStreams': [{'logStreamName': 'streamName'}],
        'nextToken': None
    }

    multi_log_stream_handler = MultiLogStreamHandler("logGroupName", "logStreamNamePrefix", 1)
    result = multi_log_stream_handler.ready()

    assert result == True
    mock_describe_log_streams.assert_called_once()


@patch('sagemaker_core.generated.logs.cw_client.describe_log_streams', autospec=True)
def test_ready_streams_set(mock_describe_log_streams):
    log_stream = LogStreamHandler("logGroupName", "logStreamName")
    multi_log_stream_handler = MultiLogStreamHandler("logGroupName", "logStreamNamePrefix", 1)
    multi_log_stream_handler.streams = [log_stream]
    
    result = multi_log_stream_handler.ready()

    assert result == True
    mock_describe_log_streams.assert_not_called()


@patch('sagemaker_core.generated.logs.cw_client.describe_log_streams', autospec=True)
def test_not_ready(mock_describe_log_streams):
    mock_describe_log_streams.return_value = {
        'logStreams': [],
        'nextToken': None
    }

    multi_log_stream_handler = MultiLogStreamHandler("logGroupName", "logStreamNamePrefix", 1)
    result = multi_log_stream_handler.ready()

    assert result == False
    mock_describe_log_streams.assert_called_once()



@patch('sagemaker_core.generated.logs.cw_client.describe_log_streams', autospec=True)
def test_ready_resource_not_found(mock_describe_log_streams):
    mock_describe_log_streams.side_effect = botocore.exceptions.ClientError(
        error_response={'Error': {'Code': 'ResourceNotFoundException'}},
        operation_name='test'
    )

    multi_log_stream_handler = MultiLogStreamHandler("logGroupName", "logStreamNamePrefix", 1)
    result = multi_log_stream_handler.ready()

    assert result == False
    mock_describe_log_streams.assert_called_once()