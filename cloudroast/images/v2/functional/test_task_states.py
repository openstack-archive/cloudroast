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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.constants import Messages
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestTaskStates(ObjectStorageIntegrationFixture):

    @tags(type='positive', regression='true')
    def test_import_task_states_success(self):
        """
        @summary: Import task states - pending, processing, success

        1) Create import task
        2) Verify that the status of the task transitions from 'pending' to
        'success'
        3) Verify that the task's properties appear correctly
        4) Verify that a result property with image_id is returned
        5) Verify that a message property is not returned
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images_behavior.create_task_with_transitions(
            input_, task_type=TaskTypes.IMPORT,
            final_status=TaskStatus.SUCCESS)

        expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                expires_at_delta))
        if self.id_regex.match(task.result.image_id) is None:
            errors.append(self.error_msg.format(
                'image_id', 'not None',
                self.id_regex.match(task.result.image_id)))
        if task.message != 'None':
            errors.append(self.error_msg.format(
                'message', 'None', task.message))

        self.assertListEqual(errors, [])

    @tags(type='negative', regression='true')
    def test_import_task_states_failure(self):
        """
        @summary: Import task states - pending, processing, failing

        1) Create storage container
        2) Copy the import_test_bootable file from the test_container to the
        new storage container
        3) Verify that the response code is 201
        4) Create import task
        5) Verify that the status of the task transitions from 'pending' to
        'processing'
        6) Delete the file being imported
        7) Get task, verify that the status changes from 'processing' to
        'failure'
        8) Verify that the task's properties appear correctly
        9) Verify that a result property is not returned
        10) Verify that a message property with the proper error message is
        returned
        """

        container_name = rand_name('container')
        object_name = rand_name('object')
        copy_from = self.import_from_bootable
        headers = {'X-Copy-From': copy_from}

        self.object_storage_behaviors.create_container(
            container_name=container_name)

        response = self.object_storage_client.copy_object(
            container_name=container_name, object_name=object_name,
            headers=headers)
        self.assertEqual(response.status_code, 201)

        import_from = '{0}/{1}'.format(container_name, object_name)
        input_ = {'image_properties': {},
                  'import_from': import_from,
                  'import_from_format': self.import_from_format}

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images_behavior.create_task_with_transitions(
            input_, task_type=TaskTypes.IMPORT)
        response = self.object_storage_client.delete_object(
            container_name=container_name, object_name=object_name)
        self.assertEqual(response.status_code, 204)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.FAILURE)

        expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                expires_at_delta))
        if task.result is not None:
            errors.append(self.error_msg.format(
                'export_location', None, task.result))
        if (task.message != Messages.OBJECT_NOT_FOUND.format(object_name)):
            errors.append(self.error_msg.format(
                'message', Messages.OBJECT_NOT_FOUND.format(object_name),
                task.message))

    @tags(type='positive', regression='true')
    def test_export_task_states_success(self):
        """
        @summary: Export task states - pending, processing, success

        1) Create new image
        2) Create export task
        3) Verify that the status of the task transitions from 'pending' to
        'success'
        4) Verify that the task's properties appear correctly
        5) Verify that a result property with export location is returned
        6) Verify that a message property is not returned
        """

        image = self.images_behavior.create_image_via_task()
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': self.export_to}
        expected_location = '{0}/{1}.vhd'.format(self.export_to, image.id_)

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images_behavior.create_task_with_transitions(
            input_, task_type=TaskTypes.EXPORT,
            final_status=TaskStatus.SUCCESS)

        expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                expires_at_delta))
        if task.result.export_location != expected_location:
            errors.append(self.error_msg.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.message != 'None':
            errors.append(self.error_msg.format(
                'message', 'None', task.message))

        self.assertListEqual(errors, [])

    @tags(type='negative', regression='true')
    def test_export_task_states_failure(self):
        """
        @summary: Export task states - pending, processing, failing

        1) Create new image
        2) Create export task
        3) Verify that the status of the task transitions from 'pending' to
        'processing'
        4) Delete the image being exported
        5) Verify that the response code is 204
        6) Get task, verify that the status changes from 'processing' to
        'failure'
        7) Verify that the task's properties appear correctly
        8) Verify that a result property is not returned
        9) Verify that a message property with the proper error message is
        returned
        """

        container_name = rand_name('container')
        image = self.images_behavior.create_image_via_task(
            import_from=self.import_from_bootable)
        input_ = {'image_uuid': image.id_,
                  'receiving_swift_container': container_name}

        self.object_storage_behaviors.create_container(
            container_name=container_name)

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images_behavior.create_task_with_transitions(
            input_, task_type=TaskTypes.EXPORT)
        response = self.object_storage_client.delete_container(
            container_name=container_name)
        self.assertEqual(response.status_code, 204)
        task = self.images_behavior.wait_for_task_status(
            task.id_, TaskStatus.FAILURE)

        expires_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.expires_at)

        errors = self.images_behavior.validate_task(task)
        if expires_at_delta > self.max_expires_at_delta:
            errors.append(self.error_msg.format(
                'expires_at delta', self.max_expires_at_delta,
                expires_at_delta))
        if task.result is not None:
            errors.append(self.error_msg.format(
                'export_location', None, task.result))
        if (task.message != Messages.CONTAINER_DNE.format(container_name)):
            errors.append(self.error_msg.format(
                'message', Messages.CONTAINER_DNE.format(container_name),
                task.message))
