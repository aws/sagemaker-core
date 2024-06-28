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
import logging
import os
import re

from boto3.session import Session
from botocore.config import Config
from typing import TypeVar, Generic, Type
from sagemaker_core.code_injection.codec import transform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")

SPECIAL_SNAKE_TO_PASCAL_MAPPINGS = {
    "volume_size_in_g_b": "VolumeSizeInGB",
    "volume_size_in_gb": "VolumeSizeInGB",
}


def configure_logging(log_level=None):
    """Configure the logging configuration based on log level.

    Usage:
        Set Environment Variable LOG_LEVEL to DEBUG to see debug logs
        configure_logging()
        configure_logging("DEBUG")

    Args:
        log_level (str): The log level to set.
            Accepted values are: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
            Defaults to the value of the LOG_LEVEL environment variable.
            If argument/environment variable is not set, defaults to "INFO".

    Raises:
        AttributeError: If the log level is invalid.
    """

    if not log_level:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    _logger = logging.getLogger()
    _logger.setLevel(getattr(logging, log_level))
    # reset any currently associated handlers with log level
    for handler in _logger.handlers:
        _logger.removeHandler(handler)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s : %(levelname)s : %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    _logger.addHandler(console_handler)


def is_snake_case(s: str):
    if not s:
        return False
    if s[0].isupper():
        return False
    if not s.islower() and not s.isalnum():
        return False
    if s.startswith("_") or s.endswith("_"):
        return False
    if "__" in s:
        return False
    return True


def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
    if pascal_str := SPECIAL_SNAKE_TO_PASCAL_MAPPINGS.get(snake_str):
        return pascal_str
    components = snake_str.split("_")
    return "".join(x.title() for x in components[0:])


def pascal_to_snake(pascal_str):
    """
    Converts a PascalCase string to snake_case.

    Args:
        pascal_str (str): The PascalCase string to be converted.

    Returns:
        str: The converted snake_case string.
    """
    snake_case = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", pascal_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake_case).lower()


def is_not_primitive(obj):
    return not isinstance(obj, (int, float, str, bool, complex))


def is_not_str_dict(obj):
    return not isinstance(obj, dict) or not all(isinstance(k, str) for k in obj.keys())


def is_primitive_list(obj):
    return all(not is_not_primitive(s) for s in obj)


def is_primitive_class(cls):
    return cls in (str, int, bool, float, datetime.datetime)


class Unassigned:
    """A custom type used to signify an undefined optional argument."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class SingletonMeta(type):
    """
    Singleton metaclass. Ensures that a single instance of a class using this metaclass is created.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Overrides the call method to return an existing instance of the class if it exists,
        or create a new one if it doesn't.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SageMakerClient(metaclass=SingletonMeta):
    """
    A singleton class for creating a SageMaker client.
    """

    def __init__(
        self,
        session: Session = None,
        region_name: str = None,
        service_name="sagemaker",
        config: Config = None,
    ):
        """
        Initializes the SageMakerClient with a boto3 session, region name, and service name.
        Creates a boto3 client using the provided session, region, and service.
        """
        if session is None:
            logger.warning("No boto3 session provided. Creating a new session.")
            session = Session()

        if region_name is None:
            logger.warning("No region provided. Using default region.")
            region_name = session.region_name

        if config is None:
            logger.warning("No config provided. Using default config.")
            config = Config(retries={"max_attempts": 10, "mode": "standard"})

        self.session = session
        self.region_name = region_name
        self.service_name = service_name
        self.client = session.client(service_name, region_name, config=config)


class SageMakerRuntimeClient(metaclass=SingletonMeta):
    """
    A singleton class for creating a SageMaker client.
    """

    def __init__(
        self,
        session: Session = None,
        region_name: str = None,
        service_name="sagemaker-runtime",
        config: Config = None,
    ):
        """
        Initializes the SageMakerClient with a boto3 session, region name, and service name.
        Creates a boto3 client using the provided session, region, and service.
        """
        if session is None:
            logger.warning("No boto3 session provided. Creating a new session.")
            session = Session()

        if region_name is None:
            logger.warning("No region provided. Using default region.")
            region_name = session.region_name

        if config is None:
            logger.warning("No config provided. Using default config.")
            config = Config(retries={"max_attempts": 10, "mode": "standard"})

        self.session = session
        self.region_name = region_name
        self.service_name = service_name
        self.client = session.client(service_name, region_name, config=config)


class ResourceIterator(Generic[T]):
    """ResourceIterator class to iterate over a list of resources."""

    def __init__(
        self,
        client: SageMakerClient,
        summaries_key: str,
        summary_name: str,
        resource_cls: Type[T],
        list_method: str,
        list_method_kwargs: dict = {},
        custom_key_mapping: dict = None,
    ):
        """Initialize a ResourceIterator object

        Args:
            client (SageMakerClient): The sagemaker client object used to make list method calls.
            summaries_key (str): The summaries key string used to access the list of summaries in the response.
            summary_name (str): The summary name used to transform list response data.
            resource_cls (Type[T]): The resource class to be instantiated for each resource object.
            list_method (str): The list method string used to make list calls to the client.
            list_method_kwargs (dict, optional): The kwargs used to make list method calls. Defaults to {}.
            custom_key_mapping (dict, optional): The custom key mapping used to map keys from summary object to those expected from resource object during initialization. Defaults to None.
        """
        self.summaries_key = summaries_key
        self.summary_name = summary_name
        self.client = client
        self.list_method = list_method
        self.list_method_kwargs = list_method_kwargs
        self.custom_key_mapping = custom_key_mapping

        self.resource_cls = resource_cls
        self.index = 0
        self.summary_list = []
        self.next_token = None

    def __iter__(self):
        return self

    def __next__(self) -> T:

        # If there are summaries in the summary_list, return the next summary
        if len(self.summary_list) > 0 and self.index < len(self.summary_list):
            # Get the next summary from the resource summary_list
            summary = self.summary_list[self.index]
            self.index += 1

            # Initialize the resource object
            if is_primitive_class(self.resource_cls):
                # If the resource class is a primitive class, there will be only one element in the summary
                resource_object = list(summary.values())[0]
            else:
                # Transform the resource summary into format to initialize object
                init_data = transform(summary, self.summary_name)

                if self.custom_key_mapping:
                    init_data = {self.custom_key_mapping.get(k, k): v for k, v in init_data.items()}
                resource_object = self.resource_cls(**init_data)

            # If the resource object has refresh method, refresh and return it
            if hasattr(resource_object, "refresh"):
                resource_object.refresh()
            return resource_object

        # If index reached the end of summary_list, and there is no next token, raise StopIteration
        elif (
            len(self.summary_list) > 0
            and self.index >= len(self.summary_list)
            and self.next_token is None
        ):
            raise StopIteration

        # Otherwise, get the next page of summaries by calling the list method with the next token if available
        else:
            if self.next_token is not None:
                response = getattr(self.client, self.list_method)(
                    NextToken=self.next_token, **self.list_method_kwargs
                )
            else:
                response = getattr(self.client, self.list_method)(**self.list_method_kwargs)

            self.summary_list = response.get(self.summaries_key, [])
            self.next_token = response.get("NextToken", None)
            self.index = 0

            # If list_method returned an empty list, raise StopIteration
            if len(self.summary_list) == 0:
                raise StopIteration

            return self.__next__()
