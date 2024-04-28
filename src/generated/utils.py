
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
import boto3

from pydantic import BaseModel
from typing import Optional


class Unassigned:
    """A custom type used to signify an undefined optional argument."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class SageMakerClient:
    _instance = None

    @staticmethod
    def getInstance():
        if SageMakerClient._instance == None:
            SageMakerClient()
        return SageMakerClient._instance

    def __init__(self, session=None, region_name='us-west-2', service_name='sagemaker'):
        if SageMakerClient._instance != None:
            raise Exception("This class is a singleton!")
        else:
            if session is None:
                session = boto3.Session(region_name=region_name)
            SageMakerClient._instance = session.client(service_name)


