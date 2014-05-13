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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.constants import Messages
from cloudcafe.images.common.types import TaskStatus, TaskTypes

from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestCreateExportTaskNegative(ObjectStorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestCreateExportTaskNegative, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='negative', regression='true')
    def test_attempt_duplicate_export_task(self):
        """
        @summary: Attempt to create a duplicate of the same export task

        1) Create image
        2) Create export task
        3) Verify that the response code is 201
        4) Wait for the task to complete successfully
        5) Create another export task with the same input properties
        6) Verify that the response code is 201
        7) Wait for the task to fail
        8) Verify that the failed task contains the correct message
        9) List files in the user's container
        10) Verify that the response code is 200
        11) Verify that only one image with the image name exists
        """

        input_ = {'image_uuid': self.image.id_,
                  'receiving_swift_container': self.export_to}
        error_msg = Messages.DUPLICATE_FILE_MSG
        exported_images = []

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        self.images_behavior.wait_for_task_status(task_id, TaskStatus.SUCCESS)

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(
            task.message, error_msg.format(self.export_to, self.image.id_))

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        files = response.entity

        errors, file_names = self.images_behavior.validate_exported_files(
            export_to=self.export_to, expect_success=True, files=files,
            image_id=self.image.id_)
        self.assertListEqual(errors, [])
        for name in file_names:
            if name == '{0}.vhd'.format(self.image.id_):
                exported_images.append(name)
        self.assertEqual(len(exported_images), 1)

    @unittest.skip('Bug, Redmine #5105')
    @tags(type='negative', regression='true')
    def test_export_coalesced_snapshot(self):
        """
        @summary: Export a snapshot that has multiple files and verify a single
        export file is created for it

        1) Create a server
        2) Modify something on the server
        3) Create a snapshot
        4) Export the snapshot
        5) Verify that the task is successful
        6) Verify that the image appears in the user's container as a single
        vhd file
        """

        image_id = self.images_config.primary_image

        response = self.server_behaviors.create_active_server(
            image_ref=image_id)
        server = response.entity

        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config)

        disks = remote_client.get_all_disks()
        for disk in disks:
            mount_point = '/mnt/{name}'.format(name=rand_name('disk'))
            self._mount_disk(remote_client=remote_client, disk=disk,
                             mount_point=mount_point)
            test_directory = '{mount}/test'.format(mount=mount_point)
            remote_client.create_directory(test_directory)

        response = self.compute_image_behaviors.create_active_image(server.id)
        snapshot = response.entity

        input_ = {'image_uuid': snapshot.id,
                  'receiving_swift_container': self.export_to}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_
        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)
        errors = self.images_behavior.validate_task(task)
        self.assertListEqual(errors, [])

        response = self.object_storage_client.list_objects(self.export_to)
        self.assertEqual(response.status_code, 200)
        files = response.entity

        errors, file_names = self.images_behavior.validate_exported_files(
            export_to=self.export_to, expect_success=True, files=files,
            image_id=snapshot.id)
        self.assertListEqual(errors, [])
        self.assertEqual(len(file_names), 1)

    @tags(type='negative', regression='true')
    def test_export_task_with_container_does_not_exist(self):
        """
        @summary: Create export task

        1) Given a previously created image, create export task with container
        does not exist
        2) Verify that the response code is 201
        3) Wait for the task to fail
        4) Verify that the failed task contains the correct message
        """

        container_name = "nonexistent"
        input_ = {'image_uuid': self.image.id_,
                  'receiving_swift_container': container_name}
        error_msg = Messages.CONTAINER_DNE

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.EXPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.FAILURE)
        self.assertEqual(task.message, error_msg.format(container_name))
