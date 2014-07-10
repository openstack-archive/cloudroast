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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageStatus, ImageVisibility)

from cloudroast.images.fixtures import ImagesFixture


class TestUpdateImageNegative(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateImageNegative, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=6)

    @tags(type='negative', regression='true')
    def test_update_image_replace_core_property(self):
        """
        @summary: Update image replace core property

        1) Given a previously created image, update image replacing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        updated_status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            image.id_, replace={'status': updated_status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_add_core_property(self):
        """
        @summary: Update image add core property

        1) Given a previously created image, update image adding the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        status = ImageStatus.ACTIVE
        response = self.images_client.update_image(
            image.id_, add={"status": status})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_remove_core_property(self):
        """
        @summary: Update image remove core property

        1) Given a previously created image, update image removing the status
        core property
        2) Verify that the response code is 403
        3) Get image
        4) Verify that the response code is 200
        5) Verify that the status has not changed
        6) Verify that image is still valid
        """

        image = self.images.pop()
        response = self.images_client.update_image(
            image.id_, remove={'status': ImageStatus.QUEUED})
        self.assertEqual(response.status_code, 403)
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertEqual(get_image.status, image.status)
        self.images_behavior.validate_image(image)

    @tags(type='negative', regression='true')
    def test_update_image_using_blank_image_id(self):
        """
        @summary: Update image using blank image id

        1) Update image using blank image id
        2) Verify that the response code is 404
        """

        self._validate_update_image_fails('')

    @tags(type='negative', regression='true')
    def test_update_image_using_invalid_image_id(self):
        """
        @summary: Update image using invalid image id

        1) Update image using invalid image id
        2) Verify that the response code is 404
        """

        self._validate_update_image_fails('invalid')

    @tags(type='negative', regression='true')
    def test_verify_location_of_active_image_cannot_be_updated(self):
        """
        @summary: Verify location of active image cannot be updated

        1) Using a previously created image, get the image
        2) Verify that the image is active
        3) Update image location
        4) Verify that the response code is 403
        5) Get the image
        6) Verify that image location has not changed
        """

        image = self.images.pop()
        updated_location = "/v2/images/{0}/new_file".format(image.id_)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        active_image = response.entity
        self.assertEqual(active_image.status, ImageStatus.ACTIVE)

        response = self.images_client.update_image(
            image_id=active_image.id_, replace={"location": updated_location})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.get_image(image_id=image.id_)
        self.assertEqual(response.status_code, 200)
        updated_image = response.entity
        self.assertEqual(updated_image.file_, image.file_)

    @unittest.skip('Bug, Redmine #7467')
    @tags(type='negative', regression='true')
    def test_verify_format_of_active_image_cannot_be_updated(self):
        """
        @summary: Verify container format and disk format of active image
        cannot be updated

        1) Using a previously created image, update image replacing container
        format
        2) Verify that the response code is 403
        3) Verify that the image container format has not been updated
        4) Update image replacing disk format
        5) Verify that the response code is 403
        6) Verify that the image disk format has not been updated
        """

        image = self.images.pop()
        response = self.images_client.update_image(
            image.id_, replace={'container_format': ImageContainerFormat.AKI})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertNotEqual(
            get_image.container_format, ImageContainerFormat.AKI)

        response = self.images_client.update_image(
            image.id_, replace={'disk_format': ImageDiskFormat.ISO})
        self.assertEqual(response.status_code, 403)

        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self.assertNotEqual(get_image.disk_format, ImageDiskFormat.ISO)

    @tags(type='negative', regression='true')
    def test_verify_update_image_setting_visibility_public_not_allowed(self):
        """
        @summary: Verify that updating an image setting the visibility property
        to public is not allowed

        1) Given a previously created image, update image setting the
        visibility property to 'public'
        2) Verify that the response code is 403
        3) List images accounting for pagination passing the filter for
        visibility set to 'public'
        4) Verify that the image that was attempted to be updated is not
        present in the list
        """

        image = self.images.pop()
        response = self.images_client.update_image(
            image.id_, replace={'visibility': ImageVisibility.PUBLIC})
        self.assertEqual(response.status_code, 403)

        images = self.images_behavior.list_images_pagination(
            visibility=ImageVisibility.PUBLIC)
        image_names = [listed_image.name for listed_image in images]
        self.assertNotIn(image.name, image_names)

    def _validate_update_image_fails(self, image_id):
        """
        @summary: Update an image with a negative value expecting it to fail
        """

        response = self.images_client.update_image(
            image_id, add={'new_prop': rand_name('new_prop_value')})
        self.assertEqual(response.status_code, 404)
