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


class TestCreateImportTask(ImagesFixture):

    @tags(type='smoke')
    def test_create_import_task(self):
        """
        @summary: Create import task

        1) Create import task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the task properties are returned correctly
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)
        self._validate_specific_task_properties(
            task, task_creation_time_in_sec)
        self.assertListEqual(errors, [])

    @tags(type='positive', regression='true')
    def test_attempt_duplicate_import_task(self):
        """
        @summary: Attempt to create a duplicate of the same import task

        1) Create import task
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create another import task with the same input properties
        5) Verify that the response code is 201
        6) Wait for the task to complete successfully
        7) Verify that the first import task is not the same as the second
        import task
        """

        tasks = []
        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        for i in range(2):
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.IMPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            task = self.images_behavior.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)
            tasks.append(task)

        self.assertNotEqual(tasks[0], tasks[1])

    @tags(type='positive', regression='true')
    def test_create_multiple_simultaneous_import_tasks(self):
        """
        @summary: When more than one import/export task is created at same
        time, verify that each task is handled properly by the workers

        1) Create import task
        2) Verify that the response code is 201
        3) Create another import task
        4) Verify that the response code is 201
        3) Wait for both tasks to complete successfully
        7) Verify that both imported images are in the customer's image list
        """

        tasks = []
        imported_images = []
        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        for i in range(2):
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.IMPORT)
            self.assertEqual(response.status_code, 201)
            tasks.append(response.entity)

        for task in tasks:
            task = self.images_behavior.wait_for_task_status(
                task.id_, TaskStatus.SUCCESS)
            imported_images.append(task.result.image_id)

        images = self.images_behavior.list_images_pagination()
        image_ids = [image.id_ for image in images]

        for imported_image in imported_images:
            self.assertIn(imported_image, image_ids)

    @tags(type='positive', regression='true')
    def test_create_import_task_with_allowed_image_properties(self):
        """
        @summary: Create import task with allowed image properties

        1) Create import task with allowed image properties
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that imported image is in the customer's image list
        """

        input_ = {'image_properties':
                  {'name': 'test_img'},
                  'import_from': self.import_from}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        images = self.images_behavior.list_images_pagination()
        image_ids = [image.id_ for image in images]

        self.assertIn(task.result.image_id, image_ids)

    def _validate_specific_task_properties(self, task,
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
        if task.input_.image_properties != {}:
            errors.append(self.error_msg.format(
                'image_properties', {}, task.input_.image_properties))
        if task.input_.import_from != self.import_from:
            errors.append(self.error_msg.format(
                'import_from', self.import_from, task.input_.import_from))
        if updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                updated_at_delta))
        if task.type_ != TaskTypes.IMPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.IMPORT, task.type_))
        if task.result is None:
            errors.append(self.error_msg.format(
                'result', 'not None', task.result))
        if self.id_regex.match(task.result.image_id) is None:
            errors.append(self.error_msg.format(
                'image_id', 'not None',
                self.id_regex.match(task.result.image_id)))
        if task.owner != self.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.tenant_id, task.owner))

        self.assertListEqual(errors, [])
