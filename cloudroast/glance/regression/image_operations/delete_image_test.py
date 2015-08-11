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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture


class DeleteImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(DeleteImage, cls).setUpClass()

        member_id = cls.images_alt_one.auth.tenant_id

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('delete_image')}, count=6)

        cls.alt_created_image = created_images.pop()

        cls.shared_created_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.shared_created_image.id_, member_id)

        cls.alt_shared_created_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.alt_shared_created_image.id_, member_id)

        cls.protected_created_image = created_images.pop()
        cls.images.client.update_image(
            cls.protected_created_image.id_, replace={'protected': True})

        cls.deactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.deactivated_image.id_)

        cls.reactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.reactivated_image.id_)
        cls.images_admin.client.reactivate_image(cls.reactivated_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.client.update_image(
            cls.protected_created_image.id_, replace={'protected': False})
        cls.images.behaviors.resources.release()
        super(DeleteImage, cls).tearDownClass()

    def test_delete_shared_image(self):
        """
        @summary: Delete shared image

        1) Delete shared image via wrapper test method
        2) Verify that the response code is 404
        """

        get_deleted_image = self._delete_image(self.shared_created_image.id_)

        self.assertEqual(
            get_deleted_image.status_code, 404,
            Messages.STATUS_CODE_MSG.format(
                404, get_deleted_image.status_code))

    def test_delete_image_using_blank_image_id(self):
        """
        @summary: Delete image using blank image id

        1) Delete image using blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(image_id='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_using_invalid_image_id(self):
        """
        @summary: Delete image using invalid image id

        1) Delete image using invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_that_is_already_deleted(self):
        """
        @summary: Delete image that is already deleted

        1) Delete image
        2) Verify that the response code is 204
        3) Delete image again
        4) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(self.alt_created_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        resp = self.images.client.delete_image(self.alt_created_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_delete_image_that_is_protected(self):
        """
        @summary: Delete image that is protected

        1) Delete image that has protected set to true
        2) Verify that the response code is 403
        3) Get image details for the image
        4) Verify that the response is ok
        """

        resp = self.images.client.delete_image(
            self.protected_created_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(
            self.protected_created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

    def test_delete_shared_image_as_member(self):
        """
        @summary: Delete shared image as member

        1) Delete shared image as member
        2) Verify that the response code is 403
        3) Get image details for the image
        4) Verify that the response is ok
        """

        resp = self.images_alt_one.client.delete_image(
            self.alt_shared_created_image.id_)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

        resp = self.images.client.get_image_details(
            self.alt_shared_created_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))

    def test_delete_deactivated_image(self):
        """
        @summary: Delete deactivated image

        1) Delete deactivated image via wrapper test method
        2) Verify that the response code is 404
        """

        get_deleted_image = self._delete_image(self.deactivated_image.id_)

        self.assertEqual(
            get_deleted_image.status_code, 404,
            Messages.STATUS_CODE_MSG.format(
                404, get_deleted_image.status_code))

    def test_delete_reactivated_image(self):
        """
        @summary: Delete reactivated image

        1) Delete reactivated image via wrapper test method
        2) Verify that the response code is 404
        """

        get_deleted_image = self._delete_image(self.reactivated_image.id_)

        self.assertEqual(
            get_deleted_image.status_code, 404,
            Messages.STATUS_CODE_MSG.format(
                404, get_deleted_image.status_code))

    def _delete_image(self, image_id):
        """
        @summary: Delete an image and return the get image details response

        @param image_id: Image id to delete
        @type image_id: Uuid

        @return: Get image details response
        @rtype: Object

        1) Delete an image
        2) Verify that the response code is 204
        3) Get image details of the deleted image
        4) Return the get image details response
        """

        resp = self.images.client.delete_image(image_id)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        return self.images.client.get_image_details(image_id)
