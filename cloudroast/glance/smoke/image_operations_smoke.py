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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ImageOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageOperationsSmoke, cls).setUpClass()
        created_images = cls.images.behaviors.create_images_via_task(count=2)
        cls.image = created_images.pop()
        cls.alt_image = created_images.pop()

    @data_driven_test(ImagesDatasetListGenerator.ListImagesDatasetList())
    def ddtest_list_images(self, params):
        """
        @summary: List all images

        @param params: Parameter being passed to the list images request
        @type params: Dictionary

        1) List all images passing in a query parameter
        2) Verify the response status code is 200
        """

        resp = self.images.client.list_images(params)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_get_image_details(self):
        """
        @summary: Get the details of an image

        1) Get the details of an image passing in an image id
        2) Verify the response status code is 200
        """

        resp = self.images.client.get_image_details(self.image.id_)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_update_image(self):
        """
        @summary: Update an image

        1) Update an image replacing a single property
        2) Verify that the response code is 200
        """

        updated_name = rand_name('updated_image')

        resp = self.images.client.update_image(
            self.image.id_, replace={'name': updated_name})
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))

    def test_delete_image(self):
        """
        @summary: Delete an image

        1) Delete an image
        2) Verify that the response code is 204
        """

        resp = self.images.client.delete_image(self.alt_image.id_)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))
