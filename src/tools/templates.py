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
"""Templates for generating resources."""

RESOURCE_CLASS_TEMPLATE ='''
class {class_name}:
{data_class_members}
{init_method}
{class_methods}
{object_methods}
'''

INIT_METHOD_TEMPLATE = '''
def __init__(self, 
    session: Optional[Session] = None, 
    region: Optional[str] = None
    {init_args}):
    self.session = session
    self.region = region
    {init_assignments}

'''

CREATE_METHOD_TEMPLATE = '''
@classmethod
def create(
    cls,
{create_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    {resource_lower} = cls(session, region)

    operation_input_args = {{
{operation_input_args}
    }}
    response = {resource_lower}.client.{operation}(**operation_input_args)

    pprint(response)

    # deserialize the response
{object_attribute_assignments}
    return {resource_lower}
'''

GET_METHOD_TEMPLATE = '''
@classmethod
def get(
    cls,
{describe_args}
    session: Optional[Session] = None,
    region: Optional[str] = None,
) -> Optional[object]:
    {resource_lower} = cls(session, region)

    operation_input_args = {{
{operation_input_args}
    }}
    response = {resource_lower}.client.{operation}(**operation_input_args)

    pprint(response)

    # deserialize the response
    deserializer({resource_lower}, response, '{describe_operation_output_shape}')
    return {resource_lower}
'''

REFRESH_METHOD_TEMPLATE = '''
def refresh(self) -> Optional[object]:

    operation_input_args = {{
{operation_input_args}
    }}
    response = self.client.{operation}(**operation_input_args)

    # deserialize the response
    deserializer(self, response, '{describe_operation_output_shape}')
    return self
'''

DELETE_METHOD_TEMPLATE = '''
def delete(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
'''

STOP_METHOD_TEMPLATE = '''
def stop(self) -> None:

    operation_input_args = {{
{operation_input_args}
    }}
    self.client.{operation}(**operation_input_args)
'''

SHAPE_BASE_CLASS_TEMPLATE ='''
class {class_name}:
    """{docstring}"""
{init_method_body}
'''

SHAPE_CLASS_TEMPLATE ='''
class {class_name}:
    """
    {docstring}
    """
{data_class_members}
'''