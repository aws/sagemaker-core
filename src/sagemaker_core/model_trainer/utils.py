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

import re
import os
from datetime import datetime
from typing import Literal

def _is_valid_ecr_image(image: str) -> bool:
    pattern = r"^\d{12}\.dkr\.ecr\.\w+-\d{1,2}\.amazonaws\.com\/[\w-]+(:[\w.-]+)?$"
    return bool(re.match(pattern, image))

def _is_valid_s3_uri(path: str, path_type: Literal["File", "Directory", "Any"] = "Any") -> bool:
    # S3 URIs should start with "s3://", followed by the bucket name and the key
    pattern = r"^s3://(?P<bucket>[^/]+)/(?P<key>.*)$"
    match = re.fullmatch(pattern, path)
    
    if match is None:
        return False

    if path_type == "File":
        # If it's a file, it should not end with a slash
        return not path.endswith('/')
    elif path_type == "Directory":
        # If it's a directory, it should end with a slash
        return path.endswith('/')

    return path_type == "Any"

def _is_valid_path(path: str, path_type: Literal["File", "Directory", "Any"] = "Any") -> bool:
    if not os.path.exists(path):
        return False

    if path_type == "File":
        return os.path.isfile(path)
    elif path_type == "Directory":
        return os.path.isdir(path)
    
    return path_type == "Any"

def _get_unique_name(base, max_length=63):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_name = f"{base}-{current_time}"
    unique_name = re.sub(r'[^a-zA-Z0-9-]', '', unique_name)  # Remove invalid characters
    unique_name = unique_name[:max_length]  # Truncate to max_length
    return unique_name    

def _get_base_name_from_image(image: str) -> str:
    return image.split("/")[-1].split(":")[0]
    
    