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
from cloudcafe.images.common.types import ImageContainerFormat, ImageDiskFormat
from cloudcafe.images.config import ImagesConfig

from cloudroast.images.fixtures import ImagesFixture

images_config = ImagesConfig()
allow_post_images = images_config.allow_post_images


class TestUpdateImagePositive(ImagesFixture):

    @tags(type='positive', regression='true')
    def test_update_image_add_additional_property(self):
        """
        @summary: Update image add additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Verify that the new property is in the response
        5) Verify that the new property's value is correct
        """

        new_prop = 'user_prop'
        new_prop_value = rand_name('new_prop_value')
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertIn(new_prop, updated_image.additional_properties)
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_prop:
                self.assertEqual(prop_val, new_prop_value)

    @tags(type='positive', regression='true')
    def test_update_image_remove_additional_property(self):
        """
        @summary: Update image remove additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Update image again removing the new property
        5) Verify that the response code is 200
        6) Verify that the removed property is not in the response
        """

        new_prop = 'user_prop'
        new_prop_value = rand_name('new_prop_value')
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        response = self.images_client.update_image(
            image.id_, remove={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertNotIn(new_prop, updated_image.additional_properties)

    @tags(type='positive', regression='true')
    def test_update_image_replace_additional_property(self):
        """
        @summary: Update image replace additional property

        1) Create image
        2) Update image adding a new property
        3) Verify that the response code is 200
        4) Update image again replacing the value of the new property
        5) Verify that the response code is 200
        6) Verify that the new property is in the response
        7) Verify that the new property's value is correct
        """

        new_prop = 'user_prop'
        new_prop_value = rand_name('new_prop_value')
        updated_new_prop_value = rand_name('updated_new_prop_value')
        image = self.images_behavior.create_image_via_task()
        response = self.images_client.update_image(
            image.id_, add={new_prop: new_prop_value})
        self.assertEqual(response.status_code, 200)
        response = self.images_client.update_image(
            image.id_, replace={new_prop: updated_new_prop_value})
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertIn(new_prop, updated_image.additional_properties)
        for prop, prop_val in updated_image.additional_properties.iteritems():
            if prop == new_prop:
                self.assertEqual(prop_val, updated_new_prop_value)

    @unittest.skipUnless(allow_post_images, 'Endpoint has incorrect access')
    @tags(type='positive', regression='true', skipable='true')
    def test_update_image_with_data_of_another_image(self):
        """
        @summary: Update image with data of another image (update ignores
        duplication)

        1) Create an image (first_image)
        2) Create another image (second_image)
        3) Update first_image with data of second_image
        4) Verify that response code is 200
        5) Verify that the response contains an image entity with
        correct properties
        """

        first_image = self.images_behavior.create_new_image()
        second_image = self.images_behavior.create_new_image(
            name=rand_name("second_image"),
            container_format=ImageContainerFormat.AMI,
            disk_format=ImageDiskFormat.ISO, tags=[rand_name("tag")])

        response = self.images_client.update_image(
            image_id=first_image.id_,
            replace={"name": second_image.name,
                     "container_format": second_image.container_format,
                     "disk_format": second_image.disk_format,
                     "tags": second_image.tags})
        self.assertEqual(response.status_code, 200)

        updated_image = response.entity
        self.assertEqual(updated_image.id_, first_image.id_)
        self.assertEqual(updated_image.name, second_image.name)
        self.assertEqual(updated_image.visibility, second_image.visibility)
        self.assertEqual(
            updated_image.container_format, second_image.container_format)
        self.assertEqual(updated_image.disk_format, second_image.disk_format)
        self.assertEqual(updated_image.tags, second_image.tags)
