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
from random import shuffle

from cafe.drivers.unittest.decorators import tags

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.images.v2.fixtures import ImagesV2Fixture
from cloudroast.images.v2.fixtures import MSG


class DeleteImageTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_delete_image(self):
        """ Delete an image.

        1. Create standard image.
        2. Delete image
        3. Verify response code is 204 and has no response body
        4. Try get deleted image
        5. Verify response code is 404
        """
        image_id = self.register_basic_image(self.api_client)

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 204,
                         MSG.format('status_code', 204,
                                    response.status_code))
        self.assertIsNone(response.entity,
                          'Response does not contain expected model.')

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

    @tags(type='negative')
    def test_delete_image_with_invalid_image_id(self):
        """ Try delete an image given an invalid id.

        1. Try delete image
        2. Verify response code is 404
        """
        image_id = self.register_basic_image(self.api_client)
        invalid_id = shuffle([char for char in image_id])

        response = self.api_client.delete_image(invalid_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

    @tags(type='negative')
    def test_delete_image_with_deleted_image_id(self):
        """ Try delete an image given an already deleted image id.

        1. Create standard image.
        2. Delete image
        3. Verify response code is 204
        4. Try delete the deleted image
        5. Verify response code is 404
        """
        image_id = self.register_basic_image(self.api_client)

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 204,
                         MSG.format('status_code', 204,
                                    response.status_code))

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

    @tags(type='negative')
    def test_delete_image_that_is_protected(self):
        """ Try delete an image that is protected.

        1. Create standard protected image (protected=true).
        2. Try delete image
        3. Verify response code is 404
        """
        response = self.admin_api_client.create_image(
            name=rand_name(),
            protected=True,
            container_format='bare',
            disk_format='raw')
        self.assertEqual(response.status_code, 201,
                         MSG.format('status_code', 201,
                                    response.status_code))

        image_id = response.entity.id_
        self.resources.add(image_id, self.admin_api_client.delete_image)

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

    @tags(type='negative')
    def test_delete_shared_image_as_non_admin(self):
        """ Delete an image that is shared with tenant.

        1. Try delete image
        2. Verify response code is 404
        """
        image_id = self.register_basic_image(self.admin_api_client)

        self.admin_api_client.add_member(image_id, self.access_data.user.id_)

        response = self.api_client.delete_image(image_id)

        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

    @tags(type='negative')
    def test_delete_image_using_incorrect_url(self):
        """ Delete an image with incorrect url.

        1. Try delete image using uri endpoint `/image`
        2. Verify the response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_using_method_mismatch_post(self):
        """ Try delete an image with HTTP method mismatch.

        1. Delete image using method mismatch of `POST`.
        2. Verify the response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_with_blank_image_id(self):
        """ Delete an image with missing id.

        1. Try delete image without image id
        2. Verify response code is 404
        """
        image_id = self.register_basic_image(self.api_client)
        image_id = ''

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))

        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404, response.status_code))

    @tags(type='negative')
    def test_delete_public_image_as_non_admin(self):
        """ Delete a public image as a normal tenant.

        1. Try delete image
        2. Verify response code is 403
        """
        response = self.api_client.create_image(
            name=rand_name(), visibility='public', protected=True,
            container_format='bare', disk_format='raw')
        self.assertEqual(response.status_code, 201,
                         MSG.format('status_code', 201,
                                    response.status_code))

        image_id = response.entity.id_
        self.resources.add(image_id, self.api_client.delete_image)

        response = self.admin_api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 403,
                         MSG.format('status_code', 403,
                                    response.status_code))

    @tags(type='positive')
    def test_delete_shared_image(self):
        """ Delete a private, shared image.

        1. Delete image.
        2. Try get image as a member.
        3. Verify response code 404
        """
        response = self.admin_api_client.create_image(
            name=rand_name(), visibility='private', container_format='bare',
            disk_format='raw')
        self.assertEqual(response.status_code, 201,
                         MSG.format('status_code', 201,
                                    response.status_code))

        image_id = response.entity.id_
        self.resources.add(image_id, self.admin_api_client.delete_image)

        response = self.admin_api_client.add_member(image_id,
                                                    self.access_data.user.id_)
        self.assertEqual(response.status_code, 201,
                         MSG.format('status_code', 201,
                                    response.status_code))

        response = self.admin_api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 201,
                         MSG.format('status_code', 201,
                                    response.status_code))

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 404,
                         MSG.format('status_code', 404,
                                    response.status_code))
