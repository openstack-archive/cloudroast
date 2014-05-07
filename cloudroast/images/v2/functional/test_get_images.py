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
from cloudcafe.images.common.types import ImageStatus, TaskTypes
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

    @tags(type='positive', regression='true')
    def test_get_images_for_import_task(self):
        """
        @summary: Verify get images returns import images with status active

        1) Create import task
        2) Verify that the response code is 201
        3) Get all images with status queued
        4) Get all images with image_type import
        5) Get all images
        6) Verify all 3 above list doesn't have import image with status other
        than active
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        queued_images = self.images_behavior.list_images_pagination(
            status=ImageStatus.QUEUED)

        import_images = self.images_behavior.list_images_pagination(
            image_type=TaskTypes.IMPORT)

        images = self.images_behavior.list_images_pagination()
        images_list = [queued_images, import_images, images]

        errors = []
        for images in images_list:
            for image in images:
                if (image.image_type == TaskTypes.IMPORT and
                        image.status != ImageStatus.ACTIVE):
                    errors.append(self.error_msg.format(
                        image.id_, "Active", image.status))

        # Override max length of diff to ensure that all errors can be viewed
        self.assertEqual.im_class.maxDiff = None
        self.assertListEqual(errors, [])
