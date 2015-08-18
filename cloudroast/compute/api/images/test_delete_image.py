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
from cloudcafe.compute.common.exceptions import ItemNotFound, BadRequest
from cloudcafe.compute.common.types import NovaImageStatusTypes as ImageStates
from cloudroast.compute.fixtures import ComputeFixture


class DeleteImageTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the neccesary resources for testing

        The following resources are created during this setup:
            - A server with values pulled from the test configuration
            - An image created from the server

        The following resources are deleted during this setup:
            - The image created previously in the setup
        """
        super(DeleteImageTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.image = cls.image_behaviors.create_active_image(
            cls.server.id).entity
        cls.resp = cls.images_client.delete_image(cls.image.id)
        cls.image_behaviors.wait_for_image_to_be_deleted(cls.image.id)

    @tags(type='smoke', net='no')
    def test_delete_image_response_code(self):
        """
        The status code for a delete image request should be 204.

        Validate that the response for the delete image request in the test
        set up has a status code of 204.

        The following assertions occur:
            - The response status code for the image deleted during setup is
              equal to 204
        """
        self.assertEqual(self.resp.status_code, 204)

    @tags(type='smoke', net='no')
    def test_deleted_image_not_listed(self):
        """
        A deleted image should not be included in the list of images.

        Request a detailed list of images. Ensure that the image id of the image
        created and deleted during setup is not found in the detailed list.
        Request a list of images. Ensure that the  image id of the image created
        and deleted during setup is not found in the list.

        The following assertions occur:
            - The image id of the image created and deleted during setup is not
              in a detailed list of images
            - The image id of the image created and deleted during setup is not
              in a list of images
        """
        images = self.images_client.list_images_with_detail()
        image_ids = [image.id for image in images.entity]
        self.assertNotIn(self.image.id, image_ids)

        images = self.images_client.list_images()
        image_ids = [image.id for image in images.entity]
        self.assertNotIn(self.image.id, image_ids)

    @tags(type='positive', net='no')
    def test_deleted_image_listed_with_changes_since(self):
        """
        A deleted image should be in the list of images using 'changed since'

        A deleted image should be included in the both the list and detailed
        list of images if the  'changes-since' parameter is a time before the
        image was deleted. As the test user get both a list of images and a
        detailed list of images using the 'created' value from the server
        created during test set up as the changed_since parameter. Validate that
        image created during test set up is found in both lists.

        The following assertions occur:
            - The image id of the image created during test set up is found
              in a list of images when the create value of the image is used
              as the 'changed_since' filter parameter
            - The image id of the image created during test set up is found
              in a detailed list of images when the create value of the image is
              used as the 'changed_since' filter parameter
        """

        images = self.images_client.list_images_with_detail(
            changes_since=self.image.created)
        image_ids = [image.id for image in images.entity]
        self.assertIn(self.image.id, image_ids)

        images = self.images_client.list_images(
            changes_since=self.image.created)
        image_ids = [image.id for image in images.entity]
        self.assertIn(self.image.id, image_ids)

    @tags(type='negative', net='no')
    def test_get_for_deleted_image(self):
        """
        Validates behavior for GETs on a deleted image.

        If the test configuration is set to allow a 'GET' request on a deleted
        image, run the get_deleted_image behavior. Otherwise run the
        get_deleted_image_fails behavior.
        """
        if self.images_config.can_get_deleted_image:
            self.get_deleted_image()
        else:
            self.get_deleted_image_fails()

    def get_deleted_image_fails(self):
        """
        A get image request for a deleted image should fail.
        """
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(self.image.id)

    def get_deleted_image(self):
        """
        A get image request for a deleted image should return the image.
        """
        image = self.images_client.get_image(self.image.id).entity
        self.assertEqual(
            image.status, ImageStates.DELETED,
            msg="Expected image state to be DELETED, was {}".format(
                image.status))

    @tags(type='negative', net='no')
    def test_create_server_from_deleted_image_fails(self):
        """
        A create server request using a deleted image should fail.

        Attempting to create a server using the image that was created and
        deleted during test set up and the flavor_ref from test configuration
        should result in a 'BadRequest' error.

        The following assertions occur:
            - Creating a server using the image id of the image deleted during
              test set up should raise a 'BadRequest' error
        """
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('server',
                                              self.image.id,
                                              self.flavor_ref)

    @tags(type='negative', net='no')
    def test_rebuild_server_from_deleted_image_fails(self):
        """
        A rebuild server request using a deleted image should fail.

        Attempting to rebuild the server created during test set up using the
        image that was created and deleted during test set up should result in
        a 'BadRequest' error.

        The following assertions occur:
            - Rebuilding a server using the image id of the image deleted during
              test set up should raise a 'BadRequest' error
        """
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, self.image.id)
