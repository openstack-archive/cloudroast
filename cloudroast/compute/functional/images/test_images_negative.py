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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import CreateServerFixture


class ImagesTest(CreateServerFixture):

    @classmethod
    def setUpClass(cls):
        super(ImagesTest, cls).setUpClass()
        cls.server = cls.server_response.entity

    @classmethod
    def tearDownClass(cls):
        super(ImagesTest, cls).tearDownClass()

    @tags(type='negative', net='no')
    def test_create_image_invalid_server_id(self):
        """Image creation should fail if the server id does not exist"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(999, 'test_neg')

    @tags(type='negative', net='no')
    def test_delete_image_invalid_id(self):
        """Image deletion should fail if the image id does not exist"""
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(999)

    @tags(type='negative', net='no')
    def test_create_image_invalid_server_name(self):
        """Image creation should fail if the image name is blank"""
        try:
            image_resp = self.servers_client.create_image(self.server.id, '')
        except:
            pass
        else:
            image_id = self.parse_image_id(image_resp)
            self.image_behaviors.wait_for_image_resp_code(image_id, 200)
            self.image_behaviors.wait_for_image_status(image_id,
                                                       NovaImageStatusTypes.ACTIVE)
            self.images_client.delete_image(image_id)
            self.fail('The create request should have failed since the name was blank.')
