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
from cloudroast.images.fixtures import ComputeIntegrationFixture


class TestGetImages(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImages, cls).setUpClass()
        cls.images = []
        server = cls.server_behaviors.create_active_server().entity
        image = cls.compute_image_behaviors.create_active_image(server.id)
        alt_image = cls.compute_image_behaviors.create_active_image(server.id)
        cls.images.append(cls.images_client.get_image(image.entity.id).entity)
        cls.images.append(cls.images_client.get_image(
            alt_image.entity.id).entity)

    @tags(type='smoke')
    def test_get_images(self):
        """
        @summary: Get images

        1) Given two images
        2) Get images
        3) Verify that the list is not empty
        4) Verify that the created images are in the list of images
        """

        owner = self.tenant_id
        images = self.images_behavior.list_images_pagination(owner=owner)
        self.assertNotEqual(len(images), 0)
        self.assertIn(self.images.pop(), images)
        self.assertIn(self.images.pop(), images)
