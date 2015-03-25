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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ImagesTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A server using the values from test configuration
        """
        super(ImagesTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity

    @tags(type='negative', net='no')
    def test_create_image_invalid_server_id(self):
        """
        Image creation should fail if the server id does not exist

        Attempting to create an image from a server with an id of 999 should
        result in an 'ItemNotFound' error.

        The following assertions occur:
            - Create an image from a server with an id of 999 should raise an
              'ItemNotFound error'
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(999, 'test_neg')

    @tags(type='negative', net='no')
    def test_delete_image_invalid_id(self):
        """
        Image deletion should fail if the image id does not exist

        Attempting to delete an image with an id of 999 should result in an
        'ItemNotFound' error.

        The following assertions occur:
            - Deleting an image with id of 999 should raise an 'ItemNotFound
             error'
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(999)

    @tags(type='negative', net='no')
    def test_create_image_invalid_server_name(self):
        """
        Image creation should fail if the image name is blank

        Attempt to create an image using the id of the server created during
        test set up and a 'blank' name. If the create image request recieves any
        errors the test will complete. If the create image request does not
        recieve an error, parse the response for the image_id, wait for the
        image to achieve 'ACTIVE' status, delete the image and fail the test.
        """
        try:
            image_resp = self.servers_client.create_image(self.server.id, '')
        except:
            pass
        else:
            image_id = self.parse_image_id(image_resp)
            self.image_behaviors.wait_for_image_resp_code(image_id, 200)
            self.image_behaviors.wait_for_image_status(
                image_id, NovaImageStatusTypes.ACTIVE)
            self.images_client.delete_image(image_id)
            self.fail('The create request should fail when the name is blank')
