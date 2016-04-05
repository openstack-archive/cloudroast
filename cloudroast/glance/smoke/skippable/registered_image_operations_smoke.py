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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.config import ImagesConfig
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture

images_config = ImagesConfig()


@unittest.skipUnless(images_config.allow_post_images,
                     'Functionality disabled with provided endpoint')
class RegisteredImageOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(RegisteredImageOperationsSmoke, cls).setUpClass()

        with open(cls.images.config.test_file, 'r') as DATA:
            cls.file_data = DATA.read().rstrip()

        # Count set to number of images required for this module
        registered_images = cls.images.behaviors.register_new_images(
            name=rand_name('registered_image_operations_smoke'), count=2)

        cls.registered_image = registered_images.pop()

        cls.alt_registered_image = registered_images.pop()
        cls.images.client.store_image_file(
            cls.alt_registered_image.id_, cls.file_data)

    @unittest.skipUnless(images_config.allow_put_image_file,
                         'Functionality disabled with provided endpoint')
    def test_store_image_file(self):
        """
        @summary: Store an image file data

        1) Store an image file data passing the image id and file data
        2) Verify that the response code is 204
        """

        resp = self.images.client.store_image_file(
            self.registered_image.id_, self.file_data)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

    @unittest.skipUnless(images_config.allow_put_image_file and
                         images_config.allow_get_image_file,
                         'Functionality disabled with provided endpoint')
    def test_get_image_file(self):
        """
        @summary: Get an image file data

        1) Get the image file data passing the image id
        2) Verify that the response code is 200
        """

        resp = self.images.client.get_image_file(self.alt_registered_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
