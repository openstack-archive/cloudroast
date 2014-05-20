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
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestImportExportLifeCycle(ObjectStorageIntegrationFixture):

    @tags(type='positive', regression='true')
    def test_import_export_life_cycle(self):
        """
        @summary: Verify that a server created from an imported image can be
        connected to and that a snapshot from the server can be exported

        1) Create import task using bootable vhd
        2) Verify that the response code is 201
        3) Wait for the task to complete successfully
        4) Verify that the task properties are returned correctly
        5) Create a new server using the imported image
        6) Verify that the server goes to active status
        7) Verify that the server can be connected to
        8) Create a snapshot of the server
        9) Create export task using the snapshot
        10) Verify that the response code is 201
        11) Wait for the task to complete successfully
        12) Verify that the task properties are returned correctly
        13) List files in the user's container
        14) Verify that the response code is 200
        15) Verify that only one image with the image name exists
        """

        exported_images = []
        input_ = {'image_properties': {},
                  'import_from': self.import_from_bootable,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)
        task_id = response.entity.id_

        task = self.images_behavior.wait_for_task_status(
            task_id, TaskStatus.SUCCESS)

        errors = self.images_behavior.validate_task(task)
        self.assertListEqual(errors, [])

        response = self.server_behaviors.create_active_server(
            image_ref=task.result.image_id)
        self.assertEqual(response.status_code, 200)
        server = response.entity

        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config)
        self.assertTrue(remote_client.can_authenticate())

        response = self.compute_image_behaviors.create_active_image(server.id)
        image = response.entity

        input_ = {'image_uuid': image.id,
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
            image_id=image.id)
        self.assertListEqual(errors, [])
        for name in file_names:
            if name == '{0}.vhd'.format(image.id):
                exported_images.append(name)
        self.assertEqual(len(exported_images), 1)
