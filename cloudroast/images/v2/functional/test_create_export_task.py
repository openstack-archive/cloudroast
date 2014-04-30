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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestCreateExportTask(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestCreateExportTask, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='smoke')
    def test_create_export_task(self):
        """
        @summary: Create export task

        1) Given a previously created image, create export task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the task properties are returned correctly
        """

        input_ = {'image_uuid': self.image.id_,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)
        self.assertListEqual(errors, [])
        self._validate_specific_task_properties(
            self.image.id_, task, task_creation_time_in_sec)

    def _validate_specific_task_properties(self, image_id, task,
                                           task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []

        created_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.created_at)
        updated_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.updated_at)
        expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)
        expected_location = '{0}/{1}.vhd'.format(self.export_to, image_id)

        if task.status != TaskStatus.SUCCESS:
            errors.append(self.error_msg.format(
                'status', TaskStatus.SUCCESS, task.status))
        if created_at_delta > self.max_created_at_delta:
            errors.append(self.error_msg.format(
                'created_at delta', self.max_created_at_delta,
                created_at_delta))
        if expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                expires_at_delta))
        if task.input_.image_uuid != image_id:
            errors.append(self.error_msg.format(
                'image_uuid', image_id, task.input_.image_uuid))
        if task.input_.receiving_swift_container != self.export_to:
            errors.append(self.error_msg.format(
                'receiving_swift_container', self.export_to,
                task.input_.receiving_swift_container))
        if updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                updated_at_delta))
        if task.type_ != TaskTypes.EXPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.EXPORT, task.type_))
        if task.result is None:
            errors.append(self.error_msg.format(
                'result', 'Not None', task.result))
        if task.result.export_location != expected_location:
            errors.append(self.error_msg.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.owner != self.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.tenant_id, task.owner))

        self.assertListEqual(errors, [])
