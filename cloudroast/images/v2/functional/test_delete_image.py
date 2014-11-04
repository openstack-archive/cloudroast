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

from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.images.fixtures import ImagesFixture


class TestDeleteImage(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestDeleteImage, cls).setUpClass()
        cls.image = cls.images_behavior.create_image_via_task()

    @tags(type='smoke')
    def test_delete_image(self):
        """
        @summary: Delete image

        1) Given a previously created image, delete the image
        2) Verify that the response code is 204
        3) Get deleted image
        4) Verify that the response code is 404
        """

        response = self.images_client.delete_image(self.image.id_)
        self.assertEqual(response.status_code, 204)

        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(self.image.id_)
