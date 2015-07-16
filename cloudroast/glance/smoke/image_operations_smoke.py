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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.config import ImagesConfig

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator

images_config = ImagesConfig()


@DataDrivenFixture
class ImageOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageOperationsSmoke, cls).setUpClass()

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('image_operations_smoke')},
            count=4)

        cls.image = created_images.pop()
        cls.alt_image = created_images.pop()
        cls.activated_image = created_images.pop()

        cls.deactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(
            cls.deactivated_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageOperationsSmoke, cls).tearDownClass()

    @data_driven_test(ImagesDatasetListGenerator.ListImagesSmoke())
    def ddtest_list_images(self, params):
        """
        @summary: List a subset of images passing in valid query parameters

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List subset of images passing in a query parameter
        2) Verify the response status code is 200
        """

        resp = self.images.client.list_images(params)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    @data_driven_test(
        ImagesDatasetListGenerator.ListImagesInvalidParameters())
    def ddtest_invalid_list_images(self, params):
        """
        @summary: Attempt to list a subset of images passing in invalid query
        parameters

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) Attempt to list a subset of images passing in an invalid query
        parameter
        2) Verify the response status code is 200
        """

        # Invalid parameters should be ignored, the response code should be 200
        resp = self.images.client.list_images(params)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_get_image_details(self):
        """
        @summary: Get the details of an image

        1) Get the details of an image passing in an image id
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_image_details(self.image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_update_image(self):
        """
        @summary: Update an image

        1) Update an image replacing a single property
        2) Verify that the response code is 200
        """

        updated_name = rand_name('image_operations_smoke_updated')

        resp = self.images.client.update_image(
            self.image.id_, replace={'name': updated_name})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

    def test_delete_image(self):
        """
        @summary: Delete an image

        1) Delete an image
        2) Verify that the response code is 204
        """

        resp = self.images.client.delete_image(self.alt_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

    @unittest.skipUnless(images_config.allow_deactivate_reactivate,
                         'Endpoint has incorrect access')
    def test_deactivate_image(self):
        """
        @summary: Deactivate an image

        1) Deactivate an image
        2) Verify that the response code is 204
        """

        resp = self.images_admin.client.deactivate_image(
            self.activated_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

    @unittest.skipUnless(images_config.allow_deactivate_reactivate,
                         'Endpoint has incorrect access')
    def test_reactivate_image(self):
        """
        @summary: Reactivate an image

        1) Reactivate an image
        2) Verify that the response code is 204
        """

        resp = self.images_admin.client.reactivate_image(
            self.deactivated_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))
