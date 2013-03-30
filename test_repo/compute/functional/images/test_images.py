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
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.types import NovaImageStatusTypes
from test_repo.compute.fixtures import CreateServerFixture


class ImagesTest(CreateServerFixture):

    @classmethod
    def setUpClass(cls):
        super(ImagesTest, cls).setUpClass()
        cls.name = rand_name('testserver')
        cls.server = cls.server_response.entity

    @classmethod
    def tearDownClass(cls):
        super(ImagesTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_create_delete_image(self):
        """An image for the provided server should be created"""

        name = rand_name('testimage')
        server_id = self.server.id
        image_response = self.servers_client.create_image(server_id, name)
        image_id = self.parse_image_id(image_response)
        self.image_behaviors.wait_for_image_status(image_id,
                                                    NovaImageStatusTypes.ACTIVE)

        # Delete image and wait for image to be deleted
        self.image_behaviors.wait_for_image_to_be_deleted(image_id)

    @tags(type='smoke', net='no')
    def test_get_image(self):
        '''The expected image should be returned'''
        image_response = self.images_client.get_image(self.image_ref)
        image = image_response.entity
        self.assertEqual(self.image_ref, image.id,
                         "Could not retrieve the expected image with id %s" %
                         (image.id))
