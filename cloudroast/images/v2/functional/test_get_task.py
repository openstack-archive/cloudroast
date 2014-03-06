"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskStatus
from cloudroast.images.fixtures import ImagesFixture


class TestGetTask(ImagesFixture):

    @tags(type='smoke')
    def test_get_task(self):
        """
        @summary: Get task

        1) Create task
        2) Get task
        3) Verify that the response code is 200
        4) Verify that the task contains the expected data
        """

        task = self.images_behavior.create_new_task()

        response = self.images_client.get_task(task.id_)
        self.assertEqual(response.status_code, 200)
        get_task = response.entity

        self._validate_get_task_response(task, get_task)

    def _validate_get_task_response(self, task, get_task):
        """@summary: Validate that the task and get_task responses match"""

        errors = []

        if get_task.status != TaskStatus.SUCCESS:
            errors.append(self.error_msg.format(
                'status', TaskStatus.SUCCESS, get_task.status))
        if get_task.id_ != task.id_:
            errors.append(self.error_msg.format(
                'id_', task.id_, get_task.id_))
        if get_task.created_at != task.created_at:
            errors.append(self.error_msg.format(
                'created_at', task.created_at, get_task.created_at))
        if get_task.input_.image_properties != task.input_.image_properties:
            errors.append(self.error_msg.format(
                'image_properties', task.input_.image_properties,
                get_task.input_.image_properties))
        if get_task.input_.import_from != task.input_.import_from:
            errors.append(self.error_msg.format(
                'import_from', task.input_.import_from,
                get_task.input_.import_from))
        if (get_task.input_.import_from_format !=
                task.input_.import_from_format):
            errors.append(self.error_msg.format(
                'import_from_format', task.input_.import_from_format,
                get_task.input_.import_from_format))
        if get_task.expires_at != task.expires_at:
            errors.append(self.error_msg.format(
                'expires_at', task.expires_at, get_task.expires_at))
        if get_task.updated_at != task.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', task.updated_at, get_task.updated_at))
        if get_task.self_ != task.self_:
            errors.append(self.error_msg.format(
                'self_', task.self_, get_task.self_))
        if get_task.type_ != task.type_:
            errors.append(self.error_msg.format(
                'type_', task.type_, get_task.type_))
        if get_task.result.image_id != task.result.image_id:
            errors.append(self.error_msg.format(
                'image_id', task.result.image_id, get_task.result.image_id))
        if get_task.owner != task.owner:
            errors.append(self.error_msg.format(
                'owner', task.owner, get_task.owner))
        if get_task.message != task.message:
            errors.append(self.error_msg.format(
                'message', task.message, get_task.message))
        if get_task.schema != task.schema:
            errors.append(self.error_msg.format(
                'schema', task.schema, get_task.schema))

        self.assertListEqual(errors, [])
