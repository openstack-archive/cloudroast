"""
Copyright 2015 Rackspace

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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import TaskStatus, TaskTypes

from cloudroast.glance.fixtures import ImagesFixture


class ImageTaskOperationsActions(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageTaskOperationsActions, cls).setUpClass()

        input_ = {'image_properties':
                  {'name': rand_name('image_task_operations_actions')},
                  'import_from': cls.images.config.import_from}

        cls.delete_task = cls.images.behaviors.create_new_task(input_)
        cls.task_created_at_time_in_sec = calendar.timegm(time.gmtime())

        cls.get_task = cls.images.behaviors.create_new_task(input_)
        cls.list_task = cls.images.behaviors.create_new_task(input_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageTaskOperationsActions, cls).tearDownClass()

    def test_delete_task(self):
        """
        @summary: Delete a task

        1) Delete a task passing in a task id
        2) Verify the response status code is 405
        3) Get task details
        4) Verify that the response is ok
        5) Verify that the returned task's properties are as expected
        generically
        """

        resp = self.images.client.delete_task(self.delete_task.id_)
        self.assertEqual(
            resp.status_code, 405,
            Messages.STATUS_CODE_MSG.format(405, resp.status_code))

        resp = self.images.client.get_task_details(self.delete_task.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_task_details = resp.entity

        errors = self.images.behaviors.validate_task(get_task_details)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_get_task_details(self):
        """
        @summary: Get task details

        1) Get task details of created task
        2) Verify that the response code is 200
        3) Verify that the returned task's properties are as expected more
        specifically
        """

        errors = []

        resp = self.images.client.get_task_details(self.get_task.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_task_details = resp.entity

        created_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.updated_at)
        expires_at_delta = self.images.behaviors.get_time_delta(
            self.task_created_at_time_in_sec, get_task_details.expires_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if get_task_details.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id,
                    get_task_details.owner))
        if get_task_details.status != TaskStatus.SUCCESS:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', TaskStatus.SUCCESS, get_task_details.status))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_list_tasks(self):
        """
        @summary: List tasks and verify that the created task is present

        1) List tasks
        2) Verify that the response code is 200
        3) Verify that the list is not empty
        4) Verify that the created task is in the list of tasks
        5) Verify that each returned tasks has the expected properties
        """

        returned_task_ids = []
        errors = []

        resp = self.images.client.list_tasks()
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        listed_tasks = resp.entity

        self.assertNotEqual(
            len(listed_tasks), 0,
            msg=('Unexpected number of tasks received. Expected: Not 0 '
                 'Received: {0}').format(len(listed_tasks)))

        [returned_task_ids.append(task.id_) for task in listed_tasks
         if task.id_ == self.list_task.id_]

        self.assertEqual(
            len(returned_task_ids), 1,
            msg=('Unexpected number of tasks received. Expected: 1 '
                 'Received: {0}').format(len(returned_task_ids)))

        for task in listed_tasks:
            if task.input_ is not None:
                errors.append(Messages.PROPERTY_MSG.format(
                    'input', 'None', task.input_))
            if task.result is not None:
                errors.append(Messages.PROPERTY_MSG.format(
                    'result', 'None', task.result))
            if task.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id, task.owner))

        self.assertEqual(
            errors, [],
            msg=('Unexpected errors received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_task_to_import_image(self):
        """
        @summary: Create a task to import an image

        1) Create a task to import an image
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the returned task's properties are as expected
        generically
        5) Verify that the returned task's properties are as expected more
        specifically
        """

        errors = []
        input_ = {'image_properties':
                  {'name': rand_name('task_to_import_image')},
                  'import_from': self.images.config.import_from}

        resp = self.images.client.task_to_import_image(
            input_, TaskTypes.IMPORT)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        task_id = resp.entity.id_

        task_creation_time_in_sec = calendar.timegm(time.gmtime())

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        created_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.updated_at)
        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)

        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if task.owner != self.images.auth.tenant_id:
                errors.append(Messages.PROPERTY_MSG.format(
                    'owner', self.images.auth.tenant_id, task.owner))
        if task.status != TaskStatus.SUCCESS:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', TaskStatus.SUCCESS, task.status))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))
