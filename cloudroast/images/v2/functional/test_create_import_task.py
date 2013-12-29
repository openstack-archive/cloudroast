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

import calendar
import time
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestCreateImportTask(ImagesFixture):

    @tags(type='smoke')
    @unittest.skip('Bug, Redmine #4226')
    def test_create_import_task(self):
        """
        @summary: Create import task

        1) Create import task
        2) Verify that the response code is 201
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        self._validate_new_task(task, task_creation_time_in_sec)

    @tags(type='positive', regression='true')
    def test_attempt_duplicate_import_task(self):
        """
        @summary: Attempt to create a duplicate of the same import take

        1) Create import task
        2) Verify that the response code is 201
        3) Create another import take with the same input properties
        4) Verify that the response code is 201
        5) Verify that the first import task is not the same as the second
        import task
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        task = response.entity

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        alt_task = response.entity

        self.assertNotEqual(task, alt_task)

    def _validate_new_task(self, task, task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []
        get_created_at_offset = self.images_behavior.get_creation_offset(
            task_creation_time_in_sec, task.created_at)
        get_updated_at_offset = self.images_behavior.get_creation_offset(
            task_creation_time_in_sec, task.updated_at)

        if task.status != TaskStatus.PENDING:
            errors.append(self.error_msg.format(
                'status', TaskStatus.PENDING, task.status))
        if self.id_regex.match(task.id_) is None:
            errors.append(self.error_msg.format(
                'id_', not None, self.id_regex.match(task.id_)))
        if get_created_at_offset > self.created_at_offset:
            errors.append(self.error_msg.format(
                'created_at offset', self.created_at_offset,
                get_created_at_offset))
        if task.input_.image_properties != {}:
            errors.append(self.error_msg.format(
                'image_properties', not {}, task.input_.image_properties))
        if task.input_.import_from != self.import_from:
            errors.append(self.error_msg.format(
                'import_from', self.import_from, task.input_.import_from))
        if task.input_.import_from_format != self.import_from_format:
            errors.append(self.error_msg.format(
                'import_from_format', self.import_from_format,
                task.input_.import_from_format))
        if task.expires_at is not None:
            errors.append(self.error_msg.format(
                'expires_at', None, task.expires_at))
        if get_updated_at_offset > self.updated_at_offset:
            errors.append(self.error_msg.format(
                'updated_at offset', self.updated_at_offset,
                get_updated_at_offset))
        if task.self_ != '/v2/tasks/{0}'.format(task.id_):
            errors.append(self.error_msg.format(
                'self_', '/v2/tasks/{0}'.format(task.id_), task.self_))
        if task.type_ != TaskTypes.IMPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.IMPORT, task.type_))
        if task.result is not None:
            errors.append(self.error_msg.format(
                'result', None, task.result))
        if task.owner != self.user_config.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.user_config.tenant_id, task.owner))
        if task.message is not None:
            errors.append(self.error_msg.format(
                'message', None, task.message))
        if task.schema != '/v2/schemas/task':
            errors.append(self.error_msg.format(
                'schema', '/v2/schemas/task', task.schema))

        self.assertListEqual(errors, [])
