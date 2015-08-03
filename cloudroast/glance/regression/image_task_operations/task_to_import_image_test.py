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

from cloudroast.glance.fixtures import ImagesIntegrationFixture


class TaskToImportImage(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TaskToImportImage, cls).setUpClass()

        cls.container_name = rand_name('task_to_import_image_container_')
        cls.object_name = rand_name('task_to_import_image_object')
        copy_from = cls.images.config.import_from_bootable
        headers = {'X-Copy-From': copy_from}

        cls.object_storage_behaviors.create_container(cls.container_name)

        cls.object_storage_client.copy_object(
            cls.container_name, cls.object_name, headers)

    @classmethod
    def tearDownClass(cls):
        cls.object_storage_behaviors.force_delete_containers(
            [cls.container_name])
        super(TaskToImportImage, cls).tearDownClass()

    def test_task_to_import_image_states_success(self):
        """
        @summary: Validate task to import image states - pending, processing,
        success

        1) Create a task to import an image
        2) Verify that the status of the task transitions from pending to
        success
        3) Verify that the expired at property is as expected
        4) Verify that a result property with image_id is returned
        5) Verify that a message property is not returned
        """

        errors = []

        input_ = {'image_properties':
                  {'name': rand_name('task_to_import_image')},
                  'import_from': self.images.config.import_from}

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images.behaviors.create_task_with_transitions(
            input_, TaskTypes.IMPORT, TaskStatus.SUCCESS)

        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)

        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if task.result.image_id is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_id', 'not None', task.result.image_id))
        if task.message != '':
            errors.append(Messages.PROPERTY_MSG.format(
                'message', 'Empty message', task.message))

        self.assertListEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    def test_task_to_import_image_states_failure(self):
        """
        @summary: Validate task to import image states - pending, processing,
        failure

        1) Delete the object from container to create stale data
        2) Verify that the response is ok
        3) Create import task
        4) Verify that the status of the task transitions from pending to
        failure
        5) Verify that the expired at property is as expected
        6) Verify that a result property is not returned
        7) Verify that a message property with the proper error message is
        returned
        """

        errors = []

        input_ = {'image_properties':
                  {'name': rand_name('task_to_import_image')},
                  'import_from':
                  '{0}/{1}'.format(self.container_name, self.object_name)}

        resp = self.object_storage_client.delete_object(
            self.container_name, self.object_name)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images.behaviors.create_task_with_transitions(
            input_, TaskTypes.IMPORT, TaskStatus.FAILURE)

        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)

        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if task.result is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'export_location', 'None', task.result))
        if task.message != Messages.IMAGE_NOT_FOUND:
            errors.append(Messages.PROPERTY_MSG.format(
                'message', Messages.IMAGE_NOT_FOUND, task.message))

        self.assertListEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    def test_task_to_import_image_duplicate(self):
        """
        @summary: Attempt to create a duplicate of the task to import image

        1) Create a task to import an image
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create another task to import an image with the same input
        properties
        5) Verify that the response code is 201
        6) Wait for the task to complete successfully
        7) Verify that the first import task is not the same as the second
        import task
        """

        tasks = []
        input_ = {'image_properties':
                  {'name': rand_name('task_to_import_image')},
                  'import_from': self.images.config.import_from}

        for i in range(2):
            resp = self.images.client.task_to_import_image(
                input_, TaskTypes.IMPORT)
            self.assertEqual(
                resp.status_code, 201,
                Messages.STATUS_CODE_MSG.format(201, resp.status_code))
            task_id = resp.entity.id_

            task = self.images.behaviors.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)

            tasks.append(task)

        self.assertNotEqual(
            tasks[0], tasks[1],
            msg=('Unexpected tasks received. Expected: Tasks to be different '
                 'Received: {0} and {1}').format(tasks[0], tasks[1]))

    def test_multiple_simultaneous_tasks_to_import_images(self):
        """
        @summary: Create multiple tasks to import images at the same time

        1) Create multiple tasks to import images
        2) Verify that the response code is 201 for each request
        3) Wait for all tasks to complete successfully
        4) List all images
        5) Verify that all imported images are returned
        """

        tasks = []
        imported_image_ids = []
        listed_image_ids = []
        input_ = {'image_properties':
                  {'name': rand_name('task_to_import_image')},
                  'import_from': self.images.config.import_from}

        for i in range(5):
            resp = self.images.client.task_to_import_image(
                input_, TaskTypes.IMPORT)
            self.assertEqual(
                resp.status_code, 201,
                Messages.STATUS_CODE_MSG.format(201, resp.status_code))
            tasks.append(resp.entity)

        for task in tasks:
            task = self.images.behaviors.wait_for_task_status(
                task.id_, TaskStatus.SUCCESS)
            imported_image_ids.append(task.result.image_id)

        listed_images = self.images.behaviors.list_all_images()
        [listed_image_ids.append(image.id_) for image in listed_images]

        for id_ in imported_image_ids:
            self.assertIn(id_, listed_image_ids,
                          msg=('Unexpected image id received. Expected: {0} '
                               'to be listed in {1} Received: Image not '
                               'listed').format(id_, listed_image_ids))

    def test_task_to_import_image_passing_image_name_property(self):
        """
        @summary: Create a task to import an image passing in the image name
        property

        1) Create a task to import an image passing in the image name property
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the returned task's properties are as expected
        generically
        5) Get image details
        6) Verify that the response is ok
        7) Verify that the imported image's name is as expected
        """

        name = rand_name('task_to_import_image')

        input_ = {'image_properties': {'name': name},
                  'import_from': self.images.config.import_from}

        resp = self.images.client.task_to_import_image(
            input_, TaskTypes.IMPORT)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        task_id = resp.entity.id_

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images.behaviors.validate_task(task)

        resp = self.images.client.get_image_details(task.result.image_id)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        if get_image.name != name:
            errors.append(Messages.PROPERTY_MSG.format(
                'name', name, get_image.name))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_task_to_import_image_passing_other_properties_forbidden(self):
        """
        @summary: Create a task to import an image passing other image
        properties

        1) Create import task with other image properties
        2) Verify that the response code is 201
        3) Wait for the task to fail
        4) Verify that the failed task contains the correct message
        """

        input_ = {'image_properties':
                  {'image_type': TaskTypes.IMPORT,
                   'name': rand_name('task_to_import_image')},
                  'import_from': self.images.config.import_from}

        resp = self.images.client.task_to_import_image(
            input_, TaskTypes.IMPORT)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        task_id = resp.entity.id_

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)

        self.assertEqual(
            task.message, Messages.EXTRA_IMAGE_PROPERTIES_MSG,
            msg=('Unexpected message received. Expected: {0} '
                 'Received: {1}').format(Messages.EXTRA_IMAGE_PROPERTIES_MSG,
                                         task.message))
