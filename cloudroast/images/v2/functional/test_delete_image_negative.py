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

from cloudroast.images.fixtures import ImagesFixture


class TestDeleteImageNegative(ImagesFixture):

    @tags(type='negative', regression='true')
    def test_delete_image_using_blank_image_id(self):
        """
        @summary: Delete image using blank image id

        1) Delete image using blank image id
        2) Verify that the response code is 404
        """

        image_id = ''
        response = self.images_client.delete_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_using_invalid_image_id(self):
        """
        @summary: Delete image using invalid image id

        1) Delete image using invalid image id
        2) Verify that the response code is 404
        """

        image_id = 'invalid'
        response = self.images_client.delete_image(image_id)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_that_is_already_deleted(self):
        """
        @summary: Delete image that is already deleted

        1) Create image
        2) Delete image
        3) Verify that the response code is 204
        4) Delete image again
        5) Verify that the response code is 404
        """

        image = self.images_behavior.create_image_via_task()
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 404)

    @tags(type='negative', regression='true')
    def test_delete_image_that_is_protected(self):
        """
        @summary: Delete image that is protected

        1) Create image
        2) Verify that the response code is 201
        3) Update image setting protected to true
        4) Verify that the response code is 204
        5) Delete image
        6) Verify that the response code is 403
        """

        protected = True
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.update_image(
            image.id_, replace={'protected': protected})
        self.assertEqual(response.status_code, 200)
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 403)

    @tags(type='negative', regression='true')
    def test_delete_image_as_member_of_shared_image(self):
        """
        @summary: Delete image as member of shared image

        1) Create image
        2) Add alternate tenant as member of image
        3) Delete image as member of shared image
        4) Verify that the response code is 403
        """

        member_id = self.alt_tenant_id
        image = self.images_behavior.create_image_via_task()
        self.images_client.add_member(image.id_, member_id)
        response = self.alt_images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 403)
