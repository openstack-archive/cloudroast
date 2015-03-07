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

from cloudroast.glance.fixtures import ImagesIntergrationFixture


class TaskToExportImage(ImagesIntergrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TaskToExportImage, cls).setUpClass()

        created_images = cls.images.behaviors.create_images_via_task(count=6)

        cls.export_image = created_images.pop()
        cls.export_success_image = created_images.pop()
        cls.export_failure_image = created_images.pop()
        cls.multiple_export_image = created_images.pop()
        cls.duplicate_export_image = created_images.pop()
        cls.container_dne_image = created_images.pop()

        created_server = cls.compute.servers.behaviors.create_active_server(
            image_ref=cls.images.config.primary_image).entity
        cls.resources.add(
            created_server.id, cls.compute.servers.client.delete_server)
        remote_client = (
            cls.compute.servers.behaviors.get_remote_instance_client(
                created_server, cls.compute.servers.config))
        disks = remote_client.get_all_disks()
        for disk in disks:
            mount_point = '/mnt/{name}'.format(name=rand_name('disk'))
            test_directory = '{mount}/test'.format(mount=mount_point)
            remote_client.create_directory(mount_point)
            remote_client.mount_disk(disk, mount_point)
            remote_client.create_directory(test_directory)
        cls.created_snapshot = (
            cls.compute.images.behaviors.create_active_image(
                created_server.id).entity)
        cls.resources.add(
            cls.created_snapshot.id, cls.images.client.delete_image)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(TaskToExportImage, cls).tearDownClass()

    def test_task_to_export_image(self):
        """
        @summary: Create a task to export an image

        1) Create a task to export an image
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the returned task's properties are as expected
        generically
        5) Verify that the returned task's properties are as expected more
        specifically
        """

        input_ = {'image_uuid': self.export_image.id_,
                  'receiving_swift_container': self.images.config.export_to}

        resp = self.images.client.task_to_export_image(
            input_, TaskTypes.EXPORT)
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        task_id = resp.entity.id_

        task_creation_time_in_sec = calendar.timegm(time.gmtime())

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images.behaviors.validate_task(task)

        created_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.updated_at)
        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)
        expected_location = (
            '{0}/{1}.vhd'.format(self.images.config.export_to,
                                 self.export_image.id_))

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
        if task.result.export_location != expected_location:
                errors.append(Messages.PROPERTY_MSG.format(
                    'export_location', expected_location,
                    task.result.export_location))
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

    def test_export_task_states_success(self):
        """
        @summary: Validate task to import image states - pending, processing,
        success

        1) Create a task to export an image
        2) Verify that the status of the task transitions from pending to
        success
        3) Verify that the expired at property is as expected
        4) Verify that a result property with export location is returned
        5) Verify that a message property is not returned
        """

        input_ = {'image_uuid': self.export_success_image.id_,
                  'receiving_swift_container': self.images.config.export_to}
        expected_location = '{0}/{1}.vhd'.format(
            self.images.config.export_to, self.export_success_image.id_)
        errors = []

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images.behaviors.create_task_with_transitions(
            input_, TaskTypes.EXPORT, TaskStatus.SUCCESS)

        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)

        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if task.result.export_location != expected_location:
            errors.append(Messages.PROPERTY_MSG.format(
                'export_location', expected_location,
                task.result.export_location))
        if task.message != '':
            errors.append(Messages.PROPERTY_MSG.format(
                'message', 'Empty message', task.message))

        self.assertListEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    def test_export_task_states_failure(self):
        """
        @summary: Validate task to import image states - pending, processing,
        failing

        1) Create a task to export an image
        2) Verify that the status of the task transitions from pending to
        failure
        3) Verify that the expired at property is as expected
        4) Verify that a result property is not returned
        5) Verify that a message property with the proper error message is
        returned
        """

        input_ = {'image_uuid': self.export_failure_image.id_,
                  'receiving_swift_container': 'container_dne'}
        errors = []

        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        task = self.images.behaviors.create_task_with_transitions(
            input_, TaskTypes.EXPORT, TaskStatus.FAILURE)

        expires_at_delta = self.images.behaviors.get_time_delta(
            task_creation_time_in_sec, task.expires_at)

        if expires_at_delta > self.images.config.max_expires_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'expires_at delta', self.images.config.max_expires_at_delta,
                expires_at_delta))
        if task.result is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'export_location', None, task.result))
        if task.message != Messages.CONTAINER_DNE.format('container_dne'):
            errors.append(Messages.PROPERTY_MSG.format(
                'message', Messages.CONTAINER_DNE.format('container_dne'),
                task.message))

        self.assertListEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    def test_task_to_export_image_multiple_containers(self):
        """
        @summary: Create a task to export an image to multiple containers

        1) Create a task to export an image
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create a task to export an image to a different container
        5) Verify that the response code is 201
        6) Wait for the task to complete successfully
        7) List objects for each container
        8) Verify that the response is ok
        9) Verify that only one image with the image name exists in each
        container
        """

        containers = [self.images.config.export_to,
                      self.images.config.alt_export_to]

        for container in containers:
            exported_images = []
            input_ = {'image_uuid': self.multiple_export_image.id_,
                      'receiving_swift_container': container}

            resp = self.images.client.task_to_export_image(
                input_, TaskTypes.EXPORT)
            self.assertEqual(resp.status_code, 201,
                             self.status_code_msg.format(201,
                                                         resp.status_code))
            task_id = resp.entity.id_

            self.images.behaviors.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)

            resp = self.object_storage_client.list_objects(
                self.images.config.export_to)
            self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
            files = resp.entity

            errors, file_names = self.images.behaviors.validate_exported_files(
                True, files, self.multiple_export_image.id_)
            self.assertListEqual(
                errors, [],
                msg=('Unexpected error received. Expected: No errors '
                     'Received: {0}').format(errors))
            for name in file_names:
                if name == '{0}.vhd'.format(self.multiple_export_image.id_):
                    exported_images.append(name)
            self.assertEqual(
                len(exported_images), 1,
                msg=('Unexpected number of exported images received. '
                     'Expected: 1'
                     'Received: {0}').format(len(exported_images)))

    def test_task_to_export_image_duplicate_forbidden(self):
        """
        @summary: Create a task to export an image to the same container

        1) Create a task to export an image
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Create a task to export an image to the same container
        5) Verify that the response code is 201
        6) Wait for the task to fail
        7) Verify that the exception message is as expected
        8) List objects for each container
        9) Verify that the response is ok
        10) Verify that only one image with the image name exists in each
        container
        """

        exported_images = []
        input_ = {'image_uuid': self.duplicate_export_image.id_,
                  'receiving_swift_container': self.images.config.export_to}
        exception_msg = Messages.DUPLICATE_FILE_MSG.format(
            self.images.config.export_to, self.duplicate_export_image.id_)

        resp = self.images.client.task_to_export_image(
            input_, TaskTypes.EXPORT)
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        task_id = resp.entity.id_

        self.images.behaviors.wait_for_task_status(task_id, TaskStatus.SUCCESS)

        resp = self.images.client.task_to_export_image(
            input_, TaskTypes.EXPORT)
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        task_id = resp.entity.id_

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)

        self.assertEqual(
            task.message, exception_msg,
            msg=('Unexpected message received. Expected: {0} '
                 'Received: {1}').format(exception_msg, task.message))

        resp = self.object_storage_client.list_objects(
            self.images.config.export_to)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        files = resp.entity

        errors, file_names = self.images.behaviors.validate_exported_files(
            True, files, self.duplicate_export_image.id_)
        self.assertListEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))
        for name in file_names:
            if name == '{0}.vhd'.format(self.duplicate_export_image.id_):
                exported_images.append(name)
        self.assertEqual(
            len(exported_images), 1,
            msg=('Unexpected number of exported images received. '
                 'Expected: 1'
                 'Received: {0}').format(len(exported_images)))

    def test_task_to_export_image_container_does_not_exist(self):
        """
        @summary: Create a task to export an image to container that does not
        exist

        1) Create a task to export an image to container that does not exist
        2) Verify that the response code is 201
        3) Wait for the task to fail
        4) Verify that the failed task contains the correct message
        """

        container_name = 'doesnotexist'
        input_ = {'image_uuid': self.container_dne_image.id_,
                  'receiving_swift_container': container_name}

        resp = self.images.client.task_to_export_image(
            input_, TaskTypes.EXPORT)
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        task_id = resp.entity.id_

        task = self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.FAILURE)

        self.assertEqual(
            task.message, Messages.CONTAINER_DNE.format(container_name),
            msg=('Unexpected message received. Expected: {0} Received: '
                 '{1}').format(Messages.CONTAINER_DNE.format(container_name),
                               task.message))

    def test_export_coalesced_snapshot(self):
        """
        @summary: Export a snapshot that has multiple files and verify a single
        export file is created for it

        1) Create a task to export an image
        2) Verify that the response code is 201
        3) Verify that the task is successful
        4) List objects for the user's container
        5) Verify that the response is ok
        6) Verify that the image appears in the user's container as a single
        vhd file
        """

        exported_images = []

        input_ = {'image_uuid': self.created_snapshot.id,
                  'receiving_swift_container': self.images.config.export_to}

        resp = self.images.client.task_to_export_image(
            input_, TaskTypes.EXPORT)
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        task_id = resp.entity.id_

        self.images.behaviors.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        resp = self.object_storage_client.list_objects(
            self.images.config.export_to)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        files = resp.entity

        errors, file_names = self.images.behaviors.validate_exported_files(
            True, files, self.created_snapshot.id)
        self.assertListEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))
        for name in file_names:
            if name == '{0}.vhd'.format(self.created_snapshot.id):
                exported_images.append(name)
        self.assertEqual(
            len(exported_images), 1,
            msg=('Unexpected number of exported images received. '
                 'Expected: 1'
                 'Received: {0}').format(len(exported_images)))
