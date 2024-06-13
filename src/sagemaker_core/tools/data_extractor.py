import json
from functools import lru_cache

from pydantic import BaseModel

from sagemaker_core.tools.constants import (
    ADDITIONAL_OPERATION_FILE_PATH,
    SERVICE_JSON_FILE_PATH,
    RUNTIME_SERVICE_JSON_FILE_PATH,
)


class ServiceJsonData(BaseModel):
    sagemaker: dict
    sagemaker_runtime: dict


@lru_cache(maxsize=1)
def load_service_jsons() -> ServiceJsonData:
    with open(SERVICE_JSON_FILE_PATH, "r") as file:
        service_json = json.load(file)
    with open(RUNTIME_SERVICE_JSON_FILE_PATH, "r") as file:
        runtime_service_json = json.load(file)
    return ServiceJsonData(sagemaker=service_json, sagemaker_runtime=runtime_service_json)


@lru_cache(maxsize=1)
def load_combined_shapes_data() -> dict:
    service_json_data = load_service_jsons()
    return {
        **service_json_data.sagemaker["shapes"],
        **service_json_data.sagemaker_runtime["shapes"],
    }


@lru_cache(maxsize=1)
def load_combined_operations_data() -> dict:
    service_json_data = load_service_jsons()
    return {
        **service_json_data.sagemaker["operations"],
        **service_json_data.sagemaker_runtime["operations"],
    }


@lru_cache(maxsize=1)
def load_additional_operations_data() -> dict:
    with open(ADDITIONAL_OPERATION_FILE_PATH, "r") as file:
        additional_operation_json = json.load(file)
    return additional_operation_json
