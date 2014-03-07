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


class TestGetImages(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImages, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=2)

    @tags(type='smoke')
    def test_get_images(self):
        """
        @summary: Get images

        1) Given two previously created images, get images
        2) Verify that the list is not empty
        3) Verify that the created images are in the list of images
        """

        list_images = self.images_behavior.list_images_pagination()
        self.assertNotEqual(len(list_images), 0)

        self.assertIn(self.images.pop(), list_images)
        self.assertIn(self.images.pop(), list_images)
