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

from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


class DeleteImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteImage, cls).setUpClass()

        member_id = cls.images_alt_one.auth.tenant_id

        created_images = cls.images.behaviors.create_images_via_task(count=5)

        cls.created_image = created_images.pop()

        cls.alt_one_created_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.alt_one_created_image.id_, member_id)

        cls.alt_two_created_image = created_images.pop()

        cls.alt_three_created_image = created_images.pop()
        cls.images.client.update_image(
            cls.alt_three_created_image.id_, replace={'protected': True})

        cls.alt_four_created_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.alt_four_created_image.id_, member_id)

    @classmethod
    def tearDownClass(cls):
        cls.images.client.update_image(
            cls.alt_three_created_image.id_, replace={'protected': False})
        cls.images.behaviors.resources.release()
        super(DeleteImage, cls).tearDownClass()

    def test_delete_image(self):
        """
        @summary: Delete image

        1) Delete image
        2) Verify that the response code is 204
        3) Get image details of the deleted image
        4) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(self.created_image.id_)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_shared_image(self):
        """
        @summary: Delete shared image

        1) Delete shared image
        4) Verify that the response code is 204
        5) Get image details as member of shared image
        6) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(self.alt_one_created_image.id_)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images_alt_one.client.get_image_details(
            self.created_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_image_using_blank_image_id(self):
        """
        @summary: Delete image using blank image id

        1) Delete image using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(image_id='')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_image_using_invalid_image_id(self):
        """
        @summary: Delete image using invalid image id

        1) Delete image using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(image_id='invalid')
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_image_that_is_already_deleted(self):
        """
        @summary: Delete image that is already deleted

        1) Delete image
        2) Verify that the response code is 204
        3) Delete image again
        4) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(self.alt_two_created_image.id_)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.delete_image(self.alt_two_created_image.id_)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))

    def test_delete_image_that_is_protected(self):
        """
        @summary: Delete image that is protected

        1) Delete image that has protected set to true
        2) Verify that the response code is 403
        """

        resp = self.images.client.delete_image(
            self.alt_three_created_image.id_)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))

    def test_delete_shared_image_as_member(self):
        """
        @summary: Delete shared image as member

        1) Delete shared image as member
        3) Verify that the response code is 403
        """

        resp = self.images_alt_one.client.delete_image(
            self.alt_four_created_image.id_)
        self.assertEqual(resp.status_code, 403,
                         self.status_code_msg.format(403, resp.status_code))
