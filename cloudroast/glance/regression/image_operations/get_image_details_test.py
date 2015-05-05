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
    ImageContainerFormat, ImageDiskFormat, ImageMemberStatus, ImageOSType,
    ImageStatus, ImageType, ImageVisibility)

from cloudroast.glance.fixtures import ImagesFixture


class GetImageDetails(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(GetImageDetails, cls).setUpClass()

        member_id = cls.images_alt_one.auth.tenant_id

        cls.created_image = cls.images.behaviors.create_image_via_task(
            image_properties={'name': rand_name('get_image_details')})
        cls.image_created_at_time_in_sec = calendar.timegm(time.gmtime())

        cls.images.client.create_image_member(
            cls.created_image.id_, member_id)

        # Count set to number of images required for this module
        created_images = cls.images.behaviors.create_images_via_task(
            image_properties={'name': rand_name('get_image_details')}, count=4)

        cls.rejected_image = created_images.pop()
        cls.images.client.create_image_member(
            cls.rejected_image.id_, member_id)
        cls.images_alt_one.client.update_image_member(
            cls.rejected_image.id_, member_id, ImageMemberStatus.REJECTED)

        cls.deleted_image = created_images.pop()
        cls.images.client.delete_image(cls.deleted_image.id_)

        cls.deactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.deactivated_image.id_)

        cls.reactivated_image = created_images.pop()
        cls.images_admin.client.deactivate_image(cls.reactivated_image.id_)
        cls.images_admin.client.reactivate_image(cls.reactivated_image.id_)

    @classmethod
    def tearDownClass(cls):
        cls.images.behaviors.resources.release()
        super(GetImageDetails, cls).tearDownClass()

    def test_get_image_details(self):
        """
        @summary: Get image details

        1) Get image details passing in the image id
        2) Verify that the response code is 200
        3) Verify that the returned image's properties are as expected
        generically
        4) Verify that the returned image's properties are as expected more
        specifically
        """

        resp = self.images.client.get_image_details(self.created_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        get_image = resp.entity

        errors = self.images.behaviors.validate_image(get_image)

        errors.append(self._validate_image(get_image))

        self.assertEqual(
            errors, [[]],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_get_image_details_as_member_of_shared_image(self):
        """
        @summary: Get image details as member of shared image

        1) Get image details using the tenant who was added as a member
        2) Verify that the response code is 200
        3) Verify that the returned image's properties are as expected
        generically
        4) Verify that the returned image's properties are as expected more
        specifically
        """

        resp = self.images_alt_one.client.get_image_details(
            self.created_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))

        get_image = resp.entity

        errors = self.images.behaviors.validate_image(get_image)

        errors.append(self._validate_image(get_image))

        self.assertEqual(
            errors, [[]],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_get_image_details_as_tenant_without_access_to_image(self):
        """
        @summary: Get image details of an image as a tenant that is not a
        member of the image

        1) Get image details of an image using a tenant that is not a member
        of the image
        2) Verify that the response code is 404
        """

        resp = self.images_alt_two.client.get_image_details(
            self.created_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

        self.assertIsNone(
            resp.entity,
            msg='Unexpected image details returned. Expected: None '
                'Received: {0}'.format(resp.entity))

    def test_get_image_details_of_rejected_image(self):
        """
        @summary: Get image details of a rejected image

        1) Get image details of a rejected image
        2) Verify that the response code is 200
        3) Verify that the returned image's properties are as expected
        generically
        """

        resp = self.images.client.get_image_details(
            self.rejected_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_image = resp.entity

        errors = self.images.behaviors.validate_image(get_image)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

    def test_get_image_details_of_deleted_image(self):
        """
        @summary: Get image details of a deleted image

        1) Get image details of a deleted image
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_details(
            self.deleted_image.id_)
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_get_image_details_of_deactivated_image(self):
        """
        @summary: Get image details of a deactivated image

        1) Get image details of a deactivated image
        2) Verify that the response code is 200
        3) Verify that the returned image's properties are as expected
        generically
        4) Verify that the status of the image status is deactivated
        """

        resp = self.images.client.get_image_details(
            self.deactivated_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_image = resp.entity

        errors = self.images.behaviors.validate_image(get_image)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

        self.assertEqual(
            get_image.status, ImageStatus.DEACTIVATED,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.deactivated_image.id_,
                               ImageStatus.DEACTIVATED, get_image.status))

    def test_get_image_details_of_reactivated_image(self):
        """
        @summary: Get image details of a reactivated image

        1) Get image details of a reactivated image
        2) Verify that the response code is 200
        3) Verify that the returned image's properties are as expected
        generically
        4) Verify that the status of the image status is active
        """

        resp = self.images.client.get_image_details(
            self.reactivated_image.id_)
        self.assertEqual(
            resp.status_code, 200,
            Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        get_image = resp.entity

        errors = self.images.behaviors.validate_image(get_image)

        self.assertEqual(
            errors, [],
            msg=('Unexpected error received. Expected: No errors '
                 'Received: {0}').format(errors))

        self.assertEqual(
            get_image.status, ImageStatus.ACTIVE,
            msg=('Unexpected status for image {0}. '
                 'Expected: {1} Received: '
                 '{2}').format(self.deactivated_image.id_,
                               ImageStatus.ACTIVE, get_image.status))

    def test_get_image_details_using_blank_image_id(self):
        """
        @summary: Get image details using a blank image id

        1) Get image details using a blank image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_details(
            image_id='')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def test_get_image_details_using_invalid_image_id(self):
        """
        @summary: Get image details using an invalid image id

        1) Get image details using an invalid image id
        2) Verify that the response code is 404
        """

        resp = self.images.client.get_image_details(
            image_id='invalid')
        self.assertEqual(
            resp.status_code, 404,
            Messages.STATUS_CODE_MSG.format(404, resp.status_code))

    def _validate_image(self, get_image):
        """
        @summary: Validate an image's properties and return any errors

        @param get_image: Image to be validated
        @type get_image: Object

        @return: Errors
        @rtype: List
        """

        errors = []
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
        if get_image.name != self.created_image.name:
            errors.append(Messages.PROPERTY_MSG.format(
                'name', self.created_image.name, get_image.name))
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
        if get_image.status != ImageStatus.ACTIVE:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageStatus.ACTIVE, get_image.status))
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

        return errors
