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


class TestCreateExportTaskPositive(ObjectStorageIntegrationFixture):

    @tags(type='positive', regression='true')
    def test_export_same_image_two_different_containers(self):
        """
        @summary: Export the same image to two different containers

        1) Create image
        2) Create export task for container A
        3) Verify that the response code is 201
        4) Wait for the task to complete successfully
        5) Create another export task for container B using the same image
        6) Verify that the response code is 201
        7) Wait for the task to complete successfully
        8) List files in the user container A
        9) Verify that the response code is 200
        10) Verify that only one image with the image name exists
        11) List files in the user container B
        12) Verify that the response code is 200
        13) Verify that only one image with the image name exists
        """

        image = self.images_behavior.create_image_via_task()
        containers = [self.export_to, self.images_config.alt_export_to]

        for container in containers:
            exported_images = []
            input_ = {'image_uuid': image.id_,
                      'receiving_swift_container': container}
            response = self.images_client.create_task(
                input_=input_, type_=TaskTypes.EXPORT)
            self.assertEqual(response.status_code, 201)
            task_id = response.entity.id_
            self.images_behavior.wait_for_task_status(
                task_id, TaskStatus.SUCCESS)

            response = self.object_storage_client.list_objects(self.export_to)
            self.assertEqual(response.status_code, 200)
            files = response.entity

            errors, file_names = self.images_behavior.validate_exported_files(
                export_to=self.export_to, expect_success=True, files=files,
                image_id=image.id_)
            self.assertListEqual(errors, [])
            for name in file_names:
                if name == '{0}.vhd'.format(image.id_):
                    exported_images.append(name)
            self.assertEqual(len(exported_images), 1)
