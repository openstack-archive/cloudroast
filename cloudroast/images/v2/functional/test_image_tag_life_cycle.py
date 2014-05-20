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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images


@unittest.skipUnless(allow_post_images, 'Endpoint has incorrect access')
class TestImageTagLifeCycle(ImagesFixture):

    @tags(type='positive', regression='true', skipable='true')
    def test_image_tag_life_cycle(self):
        """
        @summary: Image tag life cycle

        1) Create image
        2) Get image
        3) Verify that the response code is 200
        4) Verify that image tags are empty
        5) Add image tag
        6) Verify that the response code is 204
        8) Get image again
        9) Verify that the response code is 200
        10) Verify that image tags contain the added tag
        11) Delete image tag
        12) Verify that the response code is 204
        13) Get image again
        14) Verify that the response code is 200
        15) Verify that image tags are empty
        """

        tag = rand_name('tag')
        image = self.images_behavior.create_new_image()
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image_resp = response.entity
        self.assertIsNotNone(get_image_resp)
        self.assertListEqual(get_image_resp.tags, [])
        response = self.images_client.add_tag(image.id_, tag)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image_resp = response.entity
        self.assertIsNotNone(get_image_resp)
        self.assertListEqual(get_image_resp.tags, [tag])
        response = self.images_client.delete_tag(image.id_, tag)
        self.assertEqual(response.status_code, 204)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image_resp = response.entity
        self.assertIsNotNone(get_image_resp)
        self.assertListEqual(get_image_resp.tags, [])
