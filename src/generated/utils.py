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

import logging

import botocore
import time
from boto3.session import Session
from typing import TypeVar, Generic, Type
from src.code_injection.codec import transform

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


def snake_to_pascal(snake_str):
    """
    Convert a snake_case string to PascalCase.

    Args:
        snake_str (str): The snake_case string to be converted.

    Returns:
        str: The PascalCase string.

    """
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
    return "".join(["_" + i.lower() if i.isupper() else i for i in pascal_str]).lstrip("_")


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

    def __init__(self, session: Session = None, region_name: str = None, service_name="sagemaker"):
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

        self.session = session
        self.region_name = region_name
        self.service_name = service_name
        self.client = session.client(service_name, region_name)


class ResourceIterator(Generic[T]):
    def __init__(
        self,
        client: SageMakerClient,
        summaries_key: str,
        summary_key: str,
        resource_cls: Type[T],
        list_method: str,
        list_method_kwargs: dict = {},
    ):
        self.summaries_key = summaries_key
        self.summary_key = summary_key
        self.client = client
        self.list_method = list_method
        self.list_method_kwargs = list_method_kwargs

        self.resource_cls = resource_cls
        self.index = 0
        self.items = []
        self.next_token = None

    def __iter__(self):
        return self

    def __next__(self, sleep=1, retry=0) -> T:
        if len(self.items) > 0 and self.index < len(self.items):
            item = self.items[self.index]
            self.index += 1
            init_data = transform(item, self.summary_key)
            resource_object = self.resource_cls(**init_data)
            try:
                resource_object.refresh()
            except botocore.exceptions.ClientError as error:
                if (
                    error.response["Error"]["Code"] == "ThrottlingException"
                    and retry < 5
                ):
                    time.sleep(sleep)
                    sleep *= 2
                    retry += 1
                    logger.debug(
                        f"ThrottlingException encountered. Retrying in {sleep} seconds."
                    )
                    return self.__next__(sleep=sleep, retry=retry)
                raise error
            return resource_object
        elif (
            len(self.items) > 0
            and self.index >= len(self.items)
            and self.next_token is None
        ):
            raise StopIteration
        else:
            try:
                if self.next_token is not None:
                    response = getattr(self.client, self.list_method)(
                        NextToken=self.next_token, **self.list_method_kwargs
                    )
                else:
                    response = getattr(self.client, self.list_method)(
                        **self.list_method_kwargs
                    )
            except botocore.exceptions.ClientError as error:
                if (
                    error.response["Error"]["Code"] == "ThrottlingException"
                    and retry < 5
                ):
                    time.sleep(sleep)
                    sleep *= 2
                    retry += 1
                    logger.debug(
                        f"ThrottlingException encountered. Retrying in {sleep} seconds."
                    )
                    return self.__next__(sleep=sleep, retry=retry)
                raise error
            self.items = response.get(self.summaries_key, [])
            self.next_token = response.get("NextToken", None)
            self.index = 0
            if len(self.items) == 0:
                raise StopIteration
            return self.__next__()
