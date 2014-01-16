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
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestCreateExportTask(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestCreateExportTask, cls).setUpClass()
        cls.images = cls.images_behavior.create_new_images(count=2)

    @tags(type='smoke')
    def test_create_export_task(self):
        """
        @summary: Create export task

        1) Given a previously created image, create export task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the task properties are returned correctly
        """

        image = self.images.pop()
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)

        self._validate_specific_task_properties(
            image.id_, task, task_creation_time_in_sec)

        self.assertListEqual(errors, [])

    @tags(type='negative', regression='true')
    def test_attempt_duplicate_export_task(self):
        """
        @summary: Attempt to create a duplicate of the same export task

        1) Given a previous created image, create export task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create another export task with the same input properties
        5) Verify that the response code is 201
        6) Wait for the task to fail
        7) Verify that the failed task contains the correct message
        8) List files in the user's container
        9) Verify that the response code is 200
        9) Verify that only one image with the image name exists
        """

        image = self.images.pop()
        statuses = [TaskStatus.SUCCESS, TaskStatus.FAILURE]
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}
        exported_images = []

        for status in statuses:
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.EXPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            task = self.images_behavior.wait_for_task_status(task_id, status)
            if status == TaskStatus.FAILURE:
                self.assertEqual(
                    task.message, 'Swift already has an object with id '
                    '\'{0}\' in container \'{1}\''.
                    format(image.id_, self.export_to))

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        for obj in objects:
            if obj.name == image.id_:
                exported_images.append(obj)
        self.assertEqual(len(exported_images), 1)

    @tags(type='negative', regression='true')
    def test_attempt_to_export_base_image(self):
        """
        @summary: Attempt to export a base image

        1) Attempt to export a base image
        2) Verify that the task fails
        3) Verify that the image does not appear in the user's container
        """

        image_id = self.images_config.primary_image
        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(
            task.message, 'Unknown error occurred during execution')

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        objects = response.entity

        exported_image_names = [obj.name for obj in objects]
        self.assertNotIn(image_id, exported_image_names)

    def _validate_specific_task_properties(self, image_id, task,
                                           task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []

        get_created_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.created_at)
        get_updated_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.updated_at)
        get_expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)
        expected_location = '{0}/{1}'.format(self.export_to, image_id)

        if task.status != TaskStatus.SUCCESS:
            errors.append(self.error_msg.format(
                'status', TaskStatus.SUCCESS, task.status))
        if get_created_at_delta > self.max_created_at_delta:
            errors.append(self.error_msg.format(
                'created_at delta', self.max_created_at_delta,
                get_created_at_delta))
        if get_expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                get_expires_at_delta))
        if task.input_.image_uuid != image_id:
            errors.append(self.error_msg.format(
                'image_uuid', image_id, task.input_.image_uuid))
        if task.input_.receiving_swift_container != self.export_to:
            errors.append(self.error_msg.format(
                'receiving_swift_container', self.export_to,
                task.input_.receiving_swift_container))
        if get_updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                get_updated_at_delta))
        if task.type_ != TaskTypes.EXPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.EXPORT, task.type_))
        if task.result is None:
            errors.append(self.error_msg.format('result', None, task.result))
        if task.result.export_location != expected_location:
            errors.append(self.error_msg.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.owner != self.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.tenant_id, task.owner))

        self.assertListEqual(errors, [])
