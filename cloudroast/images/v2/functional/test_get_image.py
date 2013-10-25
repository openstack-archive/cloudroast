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
from cloudcafe.images.common.types import ImageVisibility
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class GetImageTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_get_image(self):
        """ Get a valid image.

         1. Get an image with a valid id.
         2. Verify the response is 200
         3. Verify the body data is a single image and contains expected
         values.
        """

        image_id = self.images_behavior.register_basic_image()
        response = self.api_client.get_image(image_id)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')
        self.assertEqual(response.entity.id_, image_id)

    @tags(type='negative')
    def test_get_image_using_http_method_post(self):
        """
        Try get image with incorrect HTTP method.

        1. Get image with HTTP method POST
        2. Verify the response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='positive')
    def test_get_private_image_as_a_member(self):
        """ Get a valid private image as a member of the image.

         1. Register a new, private image
         2. Add default user as a member to it
         3. Get image as the default member
         4. Verify the response is 200
        """
        response = self.admin_api_client.create_image(
            name=rand_name('admin_image'), visibility=ImageVisibility.PRIVATE)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')

        image_id = response.entity.id_
        self.resources.add(image_id, self.admin_api_client.delete_image)

        tenant_id = self.access_data.token.tenant.id_
        response = self.admin_api_client.add_member(image_id, tenant_id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')

    @tags(type='negative')
    def test_get_private_image_as_non_member_and_not_admin(self):
        """ Get a valid private image as a non member of the image

         1. Register a new private image as admin.
         2. Try get image as a non admin
         3. Verify the response is 404
        """
        response = self.admin_api_client.create_image(
            name=rand_name('admin_image'), visibility=ImageVisibility.PRIVATE)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')

        image_id = response.entity.id_
        self.resources.add(image_id, self.admin_api_client.delete_image)

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_get_deleted_image(self):
        """ Get a deleted image.

         1. Register an image
         2. Delete the image
         3. Try to get deleted image
         4. Verify the response is 404
        """
        response = self.api_client.create_image(
            name=rand_name('admin_image'), visibility=ImageVisibility.PRIVATE)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.entity,
                             'Response does not contain expected model.')

        image_id = response.entity.id_
        self.resources.add(image_id, self.admin_api_client.delete_image)

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 204)

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_get_image_with_blank_image_id(self):
        """ Get an image with a blank id.

         1. Try get an image with a blank id
         2. Verify the response is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_get_image_with_invalid_image_id(self):
        """ Get an image with an invalid id.

         1. Try get an image with an invalid id
         2. Verify the response is 404
        """
        response = self.api_client.get_image(rand_name('invalid_image'))
        self.assertEqual(response.status_code, 404)
