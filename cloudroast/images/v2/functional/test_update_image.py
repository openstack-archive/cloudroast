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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import \
    ImageContainerFormat, ImageDiskFormat, ImageVisibility
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestUpdateImage(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImage, cls).setUpClass()
        server = cls.server_behaviors.create_active_server().entity
        image = cls.compute_image_behaviors.create_active_image(server.id)
        cls.image = cls.images_client.get_image(image.entity.id).entity

    @tags(type='smoke')
    def test_update_image_replace_core_properties(self):
        """
        @summary: Replace values of core properties

        1) Create image
        2) Update image replacing all allowed core properties
        3) Verify that the response code is 200
        4) Verify that the updated properties are correct
        5) Revert protected property
        6) Verify that the response code is 200
        """

        updated_container_format = ImageContainerFormat.AKI
        updated_disk_format = ImageDiskFormat.ISO
        updated_name = rand_name('updated_image')
        updated_tags = rand_name('updated_tag')
        updated_visibility = ImageVisibility.PRIVATE
        errors = []
        image = self.image
        response = self.images_client.update_image(
            image.id_, replace={'container_format': updated_container_format,
                                'disk_format': updated_disk_format,
                                'name': updated_name,
                                'protected': True,
                                'tags': [updated_tags],
                                'visibility': updated_visibility})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        attributes = ['checksum', 'created_at', 'file_', 'id_', 'min_disk',
                      'min_ram', 'schema', 'self_', 'size', 'status',
                      'visibility']
        for attribute in attributes:
            if getattr(updated_image, attribute) != getattr(image, attribute):
                errors.append(self.error_msg.format(
                    attribute, getattr(image, attribute),
                    getattr(updated_image, attribute)))
        attributes = ['container_format', 'disk_format', 'name', 'protected',
                      'tags']
        for attribute in attributes:
            if getattr(updated_image, attribute) == getattr(image, attribute):
                errors.append(self.error_msg.format(
                    attribute, getattr(image, attribute),
                    getattr(updated_image, attribute)))
        if updated_image.updated_at < image.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', image.updated_at, updated_image.updated_at))
        # Need to revert protected property so that the image can be torn down
        response = self.images_client.update_image(
            image.id_, replace={'protected': False})
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(errors, [])
