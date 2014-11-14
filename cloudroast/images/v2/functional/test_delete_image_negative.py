"""
Copyright 2014 Rackspace

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
from cloudcafe.compute.common.exceptions import Forbidden, ItemNotFound

from cloudroast.images.fixtures import ImagesFixture


class TestDeleteImageNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImageNegative, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=3)

    @tags(type='negative', regression='true')
    def test_delete_image_using_blank_image_id(self):
        """
        @summary: Delete image using blank image id

        1) Delete image using blank image id
        2) Verify that the response code is 404
        """

        image_id = ''
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(image_id)

    @tags(type='negative', regression='true')
    def test_delete_image_using_invalid_image_id(self):
        """
        @summary: Delete image using invalid image id

        1) Delete image using invalid image id
        2) Verify that the response code is 404
        """

        image_id = 'invalid'
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(image_id)

    @tags(type='negative', regression='true')
    def test_delete_image_that_is_already_deleted(self):
        """
        @summary: Delete image that is already deleted

        1) Given a previously created image, delete image
        2) Verify that the response code is 204
        3) Delete image again
        4) Verify that the response code is 404
        """

        image = self.images.pop()
        response = self.images_client.delete_image(image.id_)
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(image.id_)

    @tags(type='negative', regression='true')
    def test_delete_image_that_is_protected(self):
        """
        @summary: Delete image that is protected

        1) Given a previously created image, update image setting protected to
        true
        2) Verify that the response code is 204
        3) Delete image
        4) Verify that the response code is 403
        """

        image = self.images.pop()
        protected = True
        response = self.images_client.update_image(
            image.id_, replace={'protected': protected})
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(Forbidden):
            self.images_client.delete_image(image.id_)

    @tags(type='negative', regression='true')
    def test_delete_image_as_member_of_shared_image(self):
        """
        @summary: Delete image as member of shared image

        1) Given a previously created image, add alternate tenant as member of
        image
        2) Delete image as member of shared image
        3) Verify that the response code is 403
        """

        image = self.images.pop()
        member_id = self.alt_tenant_id
        self.images_client.add_member(image.id_, member_id)
        with self.assertRaises(Forbidden):
            self.alt_images_client.delete_image(image.id_)
