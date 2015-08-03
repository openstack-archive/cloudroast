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

import calendar
import time

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.glance.common.constants import Messages
from cloudcafe.glance.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageOSType, ImageStatus, ImageType,
    ImageVisibility)

from cloudroast.glance.fixtures import ImagesFixture


class ImageOperationsActions(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageOperationsActions, cls).setUpClass()

        cls.get_image = cls.images.behaviors.create_image_via_task(
            image_properties={'name': rand_name('image_operations_actions')})
        cls.image_created_at_time_in_sec = calendar.timegm(time.gmtime())

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('image_operations_actions')},
            count=3)

        cls.delete_image = created_images.pop()
        cls.list_image = created_images.pop()
        cls.update_image = created_images.pop()

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(ImageOperationsActions, cls).tearDownClass()

    def test_delete_image(self):
        """
        @summary: Delete image

        1) Delete an image
        2) Verify that the response code is 204
        3) Get image details of the deleted image
        4) Verify that the response code is 404
        """

        resp = self.images.client.delete_image(self.delete_image.id_)
        self.assertEqual(
            resp.status_code, 204,
            Messages.STATUS_CODE_MSG.format(204, resp.status_code))

        get_image = self.images.client.get_image_details(self.delete_image.id_)

        self.assertEqual(
            get_image.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, get_image.status_code))

    def test_get_image_details(self):
        """
        @summary: Get image details

        1) Get image details passing in the image id
        2) Verify that the response code is 200
        3) Check that the returned image's properties are as expected
        generically
        4) Verify that there are no errors
        """

        errors = []

        resp = self.images.client.get_image_details(self.get_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        get_image = resp.entity

        created_at_delta = self.images.behaviors.get_time_delta(
            self.image_created_at_time_in_sec, get_image.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            self.image_created_at_time_in_sec, get_image.updated_at)

        if get_image.auto_disk_config != 'False':
            errors.append(Messages.PROPERTY_MSG.format(
                'auto_disk_config', 'False', get_image.auto_disk_config))
        if get_image.checksum is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'checksum', 'not None', get_image.checksum))
        if get_image.container_format != ImageContainerFormat.OVF:
            errors.append(Messages.PROPERTY_MSG.format(
                'container_format', ImageContainerFormat.OVF,
                get_image.container_format))
        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if get_image.disk_format != ImageDiskFormat.VHD:
            errors.append(Messages.PROPERTY_MSG.format(
                'disk_format', ImageDiskFormat.VHD, get_image.disk_format))
        if get_image.image_type != ImageType.IMPORT:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_type', ImageType.IMPORT, get_image.image_type))
        if get_image.min_disk != self.images.config.min_disk:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_disk', self.images.config.min_disk, get_image.min_disk))
        if get_image.min_ram != self.images.config.min_ram:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_ram', self.images.config.min_ram, get_image.min_ram))
        if get_image.name is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'name', self.get_image.name, get_image.name))
        if get_image.os_type != ImageOSType.LINUX:
            errors.append(Messages.PROPERTY_MSG.format(
                'os_type', ImageOSType.LINUX, get_image.os_type))
        if get_image.owner != self.images.auth.tenant_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'owner', self.images.auth.tenant_id, get_image.owner))
        if get_image.protected is not False:
            errors.append(Messages.PROPERTY_MSG.format(
                'protected', False, get_image.protected))
        if get_image.size > self.images.config.size_default:
            errors.append(Messages.PROPERTY_MSG.format(
                'size', 'Around {0}'.format(self.images.config.size_default),
                get_image.size))
        if get_image.tags is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'tags', 'not None', get_image.tags))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))
        if get_image.user_id != self.images.auth.access_data.user.id_:
            errors.append(Messages.PROPERTY_MSG.format(
                'user_id', self.images.auth.access_data.user.id_,
                get_image.user_id))
        if get_image.visibility != ImageVisibility.PRIVATE:
            errors.append(Messages.PROPERTY_MSG.format(
                'visibility', ImageVisibility.PRIVATE, get_image.visibility))

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_list_all_images(self):
        """
        @summary: List all images with no additional query parameters,
        paginating through the results as needed, and verify that the created
        image is listed

        1) List all images not passing in any additional query parameter,
        paginating through the results as needed
        2) Verify that the list is not empty
        3) Verify that the created image is in the returned list of images
        4) Verify that each image returned has a status of active or
        deactivated
        """

        acceptable_statuses = [ImageStatus.ACTIVE, ImageStatus.DEACTIVATED]

        listed_images = self.images.behaviors.list_all_images()
        self.assertNotEqual(
            len(listed_images), 0,
            msg=('Unexpected number of images received. Expected: Not {0} '
                 'Received: {1}').format(0, len(listed_images)))

        self.assertIn(
            self.list_image, listed_images,
            msg=('Unexpected images received. Expected: {0} in list of '
                 'images '
                 'Received: {1}').format(self.list_image.id_, listed_images))

        # TODO: Add additional assertions to verify all images are as expected
        for image in listed_images:
            if image.image_type == ImageType.IMPORT:
                self.assertIn(
                    image.status, acceptable_statuses,
                    msg=('Unexpected status for image {0} received. Expected:'
                         'active or deactivated Received: '
                         '{1}').format(image.id_, image.status))

    def test_update_image_add_new_property(self):
        """
        @summary: Update image by adding a new image property

        1) Update an image adding an image property
        2) Verify that the response code is 200
        3) Verify that the update image response shows that the property has
        been added as expected
        4) Get image details for the image
        5) Verify that the response code is ok
        6) Verify that the property has been added as expected
        """

        add_prop = rand_name('new_property')
        add_prop_value = rand_name('new_property_value')

        resp = self.images.client.update_image(
            self.update_image.id_, add={add_prop: add_prop_value})
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        updated_image = resp.entity

        new_prop_value = (
            updated_image.additional_properties.get(add_prop, None))

        self.assertEqual(
            new_prop_value, add_prop_value,
            msg=('Unexpected new image property value received. Expected: {0} '
                 'Received: '
                 '{1}').format(add_prop_value, new_prop_value))

        resp = self.images.client.get_image_details(self.update_image.id_)
        self.assertTrue(resp.ok, Messages.OK_RESP_MSG.format(resp.status_code))
        get_image = resp.entity

        added_prop_value = get_image.additional_properties.get(add_prop, None)

        self.assertEqual(
            added_prop_value, add_prop_value,
            msg=('Unexpected new image property value received. Expected: {0} '
                 'Received: '
                 '{1}').format(add_prop_value, added_prop_value))
