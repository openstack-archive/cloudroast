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

from cloudroast.glance.fixtures import ImagesFixture


class ImageTagOperationsSmoke(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageTagOperationsSmoke, cls).setUpClass()
        cls.created_images = cls.images.behaviors.create_images_via_task(
            count=2)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageTagOperationsSmoke, cls).tearDownClass()

    def test_add_image_tag(self):
        """
        @summary: Add an image tag

        1) Add an image tag passing in an image id and tag
        2) Verify the response status code is 204
        """

        image = self.created_images.pop()
        tag = rand_name('tag')

        resp = self.images.client.add_image_tag(image.id_, tag)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

    def test_delete_image_tag(self):
        """
        @summary: Delete an image tag

        1) Add an image tag passing in an image id and tag
        2) Verify the response status code is 204
        3) Delete an image tag passing in an image id and tag
        4) Verify that the response code is 204
        """

        image = self.created_images.pop()
        tag = rand_name('tag')

        resp = self.images.client.add_image_tag(image.id_, tag)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.delete_image_tag(image.id_, tag)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))
