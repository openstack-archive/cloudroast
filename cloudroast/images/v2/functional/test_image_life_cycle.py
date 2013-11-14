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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageContainerFormat, \
    ImageDiskFormat, ImageVisibility
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class ImageLifeCycleTest(ImagesV2Fixture):

    def test_image_life_cycle(self):
        """
        Image Life Cycle - CRUD operation

        1. Register a new image
        2. Verify the response contains an image entity with the correct
        properties
        3. List images and verify the response contains the added image
        4. Get the added image and verify that the response contains an
        image entity with the correct properties
        5. Update the image and verify the response contains an image
        entity with the correct updated properties
        6. Delete the updated image
        7. Verify the response code is 204
        8 Try get the deleted image and verify the response code is 404
        """

        image_name = rand_name('image_')
        updated_image_name = rand_name('image_updated_')

        response = self.api_client.create_image(
            name=image_name, container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)
        self.assertEqual(response.status_code, 201)
        image = response.entity

        self.resources.add(image.id_, self.api_client.delete_image)
        self.assertEqual(image.name, image_name)
        self.assertEqual(image.visibility, ImageVisibility.PRIVATE)
        self.assertEqual(image.disk_format, ImageDiskFormat.RAW)
        self.assertEqual(image.container_format, ImageContainerFormat.BARE)

        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        self.assertIsNotNone(images, 'Images deserialization failed.')
        self.assertIn(image, images)

        response = self.api_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.api_client.update_image(
            image_id=image.id_,
            replace={"name": updated_image_name,
                     "visibility": ImageVisibility.PUBLIC,
                     "disk_format": ImageDiskFormat.QCOW2,
                     "container_format": ImageContainerFormat.AMI})

        self.assertEqual(response.status_code, 200)
        updated_image = response.entity

        self.assertEqual(updated_image.name, updated_image_name)
        self.assertEqual(updated_image.visibility, ImageVisibility.PUBLIC)
        self.assertEqual(updated_image.disk_format, ImageDiskFormat.QCOW2)
        self.assertEqual(updated_image.container_format,
                         ImageContainerFormat.AMI)

        response = self.api_client.delete_image(image_id=updated_image.id_)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=updated_image.id_)
        self.assertEqual(response.status_code, 404)
