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

import unittest


from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import ImageStatus
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@unittest.skipUnless(
    images.config.allow_post_images, 'Endpoint has incorrect access')
class StoreImageFile(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(StoreImageFile, cls).setUpClass()

        reg_images = cls.images.behaviors.register_new_images(count=3)
        cls.reg_image = reg_images.pop()
        cls.duplicate_reg_image = reg_images.pop()
        cls.content_type_reg_image = reg_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(StoreImageFile, cls).tearDownClass()

    def test_store_image_file(self):
        """
        @summary: Store image file

        1) Store image file
        2) Verify that the response code is 204
        3) Get image details of the image
        4) Verify that the response code is ok
        5) Verify that the image contains the correct updated properties
        """

        errors = []

        resp = self.images.client.store_image_file(
            self.reg_image.id_, self.images.config.test_file)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.get_image_details(self.reg_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        if get_image.checksum is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'checksum', 'not None', get_image.checksum))
        if get_image.size != len(self.images.config.test_file):
            errors.append(Messages.PROPERTY_MSG.format(
                'size', len(self.images.config.test_file), get_image.size))
        if get_image.status != ImageStatus.ACTIVE:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageStatus.ACTIVE, get_image.status))

        self.assertEqual(errors, [])

    def test_store_image_file_duplicate_file_forbidden(self):
        """
        @summary: Verify that attempting to store duplicate image file is
        forbidden

        1) Store image file
        2) Verify that the response code is 204
        3) Attempt to store the same image file
        4) Verify that the response code is 409
        """

        resp = self.images.client.store_image_file(
            self.duplicate_reg_image.id_, self.images.config.test_file)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.store_image_file(
            self.duplicate_reg_image.id_, self.images.config.test_file)
        self.assertEqual(resp.status_code, 409,
                         self.status_code_msg.format(409, resp.status_code))

    def test_store_image_file_using_invalid_content_type(self):
        """
        @summary: Store image file using invalid content type

        1) Store image file using invalid content type
        2) Verify response code is 415
        3) Get image details of the image
        4) Verify that the response code is ok
        5) Verify that the image has not been updated
        """

        errors = []

        resp = self.images.client.store_image_file(
            self.content_type_reg_image.id_, self.images.config.test_file,
            content_type="invalid_content_type")
        self.assertEqual(resp.status_code, 415,
                         self.status_code_msg.format(415, resp.status_code))

        resp = self.images.client.get_image_details(
            self.content_type_reg_image.id_)
        self.assertTrue(resp.ok, self.ok_resp_msg.format(resp.status_code))
        get_image = resp.entity

        if get_image.checksum is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'checksum', 'None', get_image.checksum))
        if get_image.size is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'size', 'None', get_image.size))
        if get_image.status != ImageStatus.QUEUED:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageStatus.QUEUED, get_image.status))

        self.assertEqual(errors, [])

    def test_store_image_file_using_blank_image_id(self):
        """
        @summary: Store image file using blank image id

        1) Store image file using blank image id
        2) Verify response code is 400
        """

        resp = self.images.client.store_image_file(
            image_id='', file_data=self.images.config.test_file)
        self.assertEqual(resp.status_code, 400,
                         self.status_code_msg.format(400, resp.status_code))

    def test_store_image_file_using_invalid_image_id(self):
        """
        @summary: Store image file using invalid image id

        1) Store image file using invalid image id
        2) Verify response code is 404
        """

        resp = self.images.client.store_image_file(
            image_id='invalid', file_data=self.images.config.test_file)
        self.assertEqual(resp.status_code, 404,
                         self.status_code_msg.format(404, resp.status_code))
