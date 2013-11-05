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

        1. List images and verify the response return a list of default
        images only - There are 3 (number_of_default_images) default images
        that are automatically created when we stack up (devstack is up and
        running)
        2. Register a new image
        3. Verify the response contains an image entity with the correct
        properties
        4. List images and verify the response should now have an additional
        image
        5. Get the added image and verify that the response contains an
        image entity with the correct properties
        6. Update the image and verify the response contains an image
        entity with the correct updated properties
        7. Delete the updated image
        8. Verify the response code is 204
        9 Try get the deleted image and verify the response code is 404
        """

        image_name = rand_name('image_')
        image_updated_name = rand_name('image_updated_')
        image_disk_format = ImageDiskFormat.RAW
        image_container_format = ImageContainerFormat.BARE
        number_of_default_images = 3

        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity

        # Specific properties of the default images
        self.assertEqual(len(images), number_of_default_images)
        for image in images:
            self.assertEqual(image.container_format, image.disk_format)

        response = self.api_client.create_image(
            name=image_name, container_format=image_container_format,
            disk_format=image_disk_format)
        self.assertEqual(response.status_code, 201)
        image = response.entity
        self.resources.add(image.id_, self.api_client.delete_image)
        self.assertEqual(image.name, image_name)
        self.assertEqual(image.disk_format, image_disk_format)
        self.assertEqual(image.container_format, image_container_format)

        response = self.api_client.list_images()
        self.assertEqual(response.status_code, 200)
        images = response.entity
        self.assertEqual(len(images), number_of_default_images+1)
        self.assertIn(image, images)

        response = self.api_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.entity, image)

        response = self.api_client.update_image(
            image_id=image.id_,
            replace={"name": image_updated_name,
                     "visibility": ImageVisibility.PUBLIC,
                     "disk_format": ImageDiskFormat.QCOW2,
                     "container_format": ImageContainerFormat.AMI})

        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.name, image_updated_name)
        self.assertEqual(updated_image.disk_format, ImageDiskFormat.QCOW2)
        self.assertEqual(updated_image.container_format,
                         ImageContainerFormat.AMI)

        response = self.api_client.delete_image(image_id=updated_image.id_)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id=updated_image.id_)
        self.assertEqual(response.status_code, 404)
