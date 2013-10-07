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
from cloudroast.images.v2.fixtures import ImagesV2Fixture


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
        image_id = self.register_basic_image()

        response = self.api_client.delete_image(image_id)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(response.content)

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative')
    def test_delete_image_with_invalid_image_id(self):
        """ Try delete an image given an invalid id.

        1. Try delete image
        2. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_with_deleted_image_id(self):
        """ Try delete an image given an already deleted image id.

        1. Create standard image.
        2. Delete image
        3. Verify response code is 204
        4. Try delete the deleted image
        5. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_that_is_protected(self):
        """ Try delete an image that is protected.

        1. Create standard protected image (protected=true).
        2. Try delete image
        3. Verify response code is 403
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_with_blank_image_id(self):
        """ Delete an image with missing id.

        1. Try delete image without image id
        2. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_public_image_as_non_admin(self):
        """ Delete a public image as a normal tenant.

        1. Try delete image
        2. Verify response code is 403
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_shared_image(self):
        """ Delete an image that is shared with tenant.

        1. Delete image
        2. Verify response code is 204
        3. Try get image as tenant
        4. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_delete_image_using_incorrect_url(self):
        """ Delete an image with incorrect url.

        1. Try delete image using uri endpoint `/image`
        2. Verify the response code is 404
        """

    @tags(type='negative')
    def test_delete_image_using_method_mismatch_post(self):
        """ Try delete an image with HTTP method mismatch.

        1. Delete image using method mismatch of `POST`.
        2. Verify the response code is 404
        """
        self.assertTrue(False, 'Not Implemented')
