"""
Copyright 2016 Rackspace

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
import re

import time
import unittest
import uuid

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import rand_name, random_string
from cloudcafe.glance.common.constants import ImageProperties, Messages
from cloudcafe.glance.common.types import (
    ImageContainerFormat, ImageDiskFormat, ImageOSType, ImageStatus, ImageType,
    ImageVisibility, Schemas)
from cloudcafe.glance.composite import ImagesComposite, ImagesAuthComposite

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator

user_one = ImagesAuthComposite()
images = ImagesComposite(user_one)


@unittest.skipUnless(
    images.config.allow_post_images, 'Endpoint has incorrect access')
@DataDrivenFixture
class RegisterImage(ImagesFixture):

    @classmethod
    def tearDownClass(cls):
        cls.resources.release()
        super(RegisterImage, cls).tearDownClass()

    def test_register_image_without_passing_properties(self):
        """
        @summary: Register image without passing any properties

        1) Register image without passing any properties
        2) Verify that the response code is 201
        3) Add the image to the resource pool for deletion
        4) Verify that the response contains the properties and values as
        expected
        """

        errors = []
        id_regex = re.compile(ImageProperties.ID_REGEX)

        resp = self.images.client.register_image()
        image_created_at_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        reg_image = resp.entity

        self.resources.add(reg_image.id_, self.images.client.delete_image)

        created_at_delta = self.images.behaviors.get_time_delta(
            image_created_at_time_in_sec, reg_image.created_at)
        updated_at_delta = self.images.behaviors.get_time_delta(
            image_created_at_time_in_sec, reg_image.updated_at)

        if reg_image.auto_disk_config is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'auto_disk_config', 'None', reg_image.auto_disk_config))
        if reg_image.checksum is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'checksum', 'None', reg_image.checksum))
        if reg_image.container_format is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'container_format', 'None', reg_image.container_format))
        if created_at_delta > self.images.config.max_created_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'created_at delta', self.images.config.max_created_at_delta,
                created_at_delta))
        if reg_image.disk_format is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'disk_format', 'None', reg_image.disk_format))
        if reg_image.file_ != '/v2/images/{0}/file'.format(reg_image.id_):
            errors.append(Messages.PROPERTY_MSG.format(
                'file_', '/v2/images/{0}/file'.format(reg_image.id_),
                reg_image.file_))
        if id_regex.match(reg_image.id_) is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'id_', 'not None', id_regex))
        if reg_image.image_type is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_type', 'None', reg_image.image_type))
        if reg_image.min_disk != 0:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_disk', 0, reg_image.min_disk))
        if reg_image.min_ram != 0:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_ram', 0, reg_image.min_ram))
        if reg_image.name is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'name', 'None', reg_image.name))
        if reg_image.os_type is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'os_type', 'None', reg_image.os_type))
        if reg_image.owner != self.images.auth.tenant_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'owner', self.images.auth.tenant_id, reg_image.owner))
        if reg_image.protected is not False:
            errors.append(Messages.PROPERTY_MSG.format(
                'protected', False, reg_image.protected))
        if reg_image.schema != Schemas.IMAGE_SCHEMA:
            errors.append(Messages.PROPERTY_MSG.format(
                'schema', Schemas.IMAGE_SCHEMA, reg_image.schema))
        if reg_image.self_ != '/v2/images/{0}'.format(reg_image.id_):
            errors.append(Messages.PROPERTY_MSG.format(
                'self', '/v2/images/{0}'.format(reg_image.id_),
                reg_image.self_))
        if reg_image.size is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'size', 'None', reg_image.size))
        if reg_image.status != ImageStatus.QUEUED:
            errors.append(Messages.PROPERTY_MSG.format(
                'status', ImageStatus.QUEUED, reg_image.status))
        if reg_image.tags != []:
            errors.append(Messages.PROPERTY_MSG.format(
                'tags', [], reg_image.tags))
        if updated_at_delta > self.images.config.max_updated_at_delta:
            errors.append(Messages.PROPERTY_MSG.format(
                'updated_at delta', self.images.config.max_updated_at_delta,
                updated_at_delta))
        if reg_image.user_id is not None:
            errors.append(Messages.PROPERTY_MSG.format(
                'user_id', 'None', reg_image.user_id))
        if reg_image.visibility != ImageVisibility.PRIVATE:
            errors.append(Messages.PROPERTY_MSG.format(
                'visibility', ImageVisibility.PRIVATE, reg_image.visibility))
        if reg_image.additional_properties != {}:
            errors.append(Messages.PROPERTY_MSG.format(
                'additional_properties', {}, reg_image.additional_properties))

        self.assertEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    def test_register_image_passing_all_allowed_properties(self):
        """
        @summary: Register image passing all allowed properties

        1) Register image passing all allowed properties
        2) Verify that the response code is 201
        3) Add the image to the resource pool for deletion
        4) Verify that the response contains values for all allowed properties
        as expected
        """

        errors = []
        id_regex = re.compile(ImageProperties.ID_REGEX)
        auto_disk_config = 'False'
        container_format = ImageContainerFormat.AKI
        disk_format = ImageDiskFormat.ISO
        id_ = str(uuid.uuid1())
        image_type = ImageType.IMPORT
        min_disk = images.config.min_disk
        min_ram = images.config.min_ram
        name = rand_name('register_image')
        os_type = ImageOSType.LINUX
        owner = images.auth.access_data.token.tenant.id_
        protected = False
        tags = [rand_name('tag1')]
        user_id = random_string()
        additional_properties = {self.images.config.additional_property:
                                 self.images.config.additional_property_value}

        resp = self.images.client.register_image(
            auto_disk_config=auto_disk_config,
            container_format=container_format, disk_format=disk_format,
            id_=id_, image_type=image_type, min_disk=min_disk, min_ram=min_ram,
            name=name, os_type=os_type, owner=owner, protected=protected,
            tags=tags, user_id=user_id,
            additional_properties=additional_properties)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        reg_image = resp.entity

        self.resources.add(
            reg_image.id_, self.images.client.delete_image)

        if reg_image.auto_disk_config != auto_disk_config:
            errors.append(Messages.PROPERTY_MSG.format(
                'auto_disk_config', auto_disk_config,
                reg_image.auto_disk_config))
        if reg_image.container_format != container_format:
            errors.append(Messages.PROPERTY_MSG.format(
                'container_format', container_format,
                reg_image.container_format))
        if reg_image.disk_format != disk_format:
            errors.append(Messages.PROPERTY_MSG.format(
                'disk_format', disk_format, reg_image.disk_format))
        if id_regex.match(reg_image.id_) is None:
            errors.append(Messages.PROPERTY_MSG.format(
                'id_', 'not None', id_regex))
        if reg_image.image_type != image_type:
            errors.append(Messages.PROPERTY_MSG.format(
                'image_type', 'not None', reg_image.image_type))
        if reg_image.min_disk != min_disk:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_disk', min_disk, reg_image.min_disk))
        if reg_image.min_ram != min_ram:
            errors.append(Messages.PROPERTY_MSG.format(
                'min_ram', min_ram, reg_image.min_ram))
        if reg_image.name != name:
            errors.append(Messages.PROPERTY_MSG.format(
                'name', name, reg_image.name))
        if reg_image.os_type != os_type:
            errors.append(Messages.PROPERTY_MSG.format(
                'os_type', 'not None', reg_image.os_type))
        if reg_image.owner != owner:
            errors.append(Messages.PROPERTY_MSG.format(
                'owner', 'not None', reg_image.owner))
        if reg_image.protected != protected:
            errors.append(Messages.PROPERTY_MSG.format(
                'protected', protected, reg_image.protected))
        if reg_image.tags != tags:
            errors.append(Messages.PROPERTY_MSG.format(
                'tags', tags, reg_image.tags))
        if reg_image.user_id != user_id:
            errors.append(Messages.PROPERTY_MSG.format(
                'user_id', 'not None', reg_image.user_id))
        if reg_image.additional_properties != additional_properties:
            errors.append(Messages.PROPERTY_MSG.format(
                'additional_properties', additional_properties,
                reg_image.additional_properties))

        self.assertEqual(
            errors, [], msg=('Unexpected error received. Expected: No errors '
                             'Received: {0}').format(errors))

    @data_driven_test(
        ImagesDatasetListGenerator.RegisterImageRestricted())
    def ddtest_register_image_passing_restricted_property(self, prop):
        """
        @summary: Register image passing restricted property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Register image passing restricted property
        2) Verify that the response code is 403
        """

        underscore_props = ['file', 'self']

        # Each prop passed in only has one key-value pair
        for key, val in prop.iteritems():
            prop_key = key
            prop_val = val

        if prop_key in underscore_props:
            prop = {'{0}_'.format(prop_key): prop_val}

        resp = self.images.client.register_image(
            name=rand_name('register_image'), **prop)
        self.assertEqual(
            resp.status_code, 403,
            Messages.STATUS_CODE_MSG.format(403, resp.status_code))

    def test_register_two_images_passing_same_name(self):
        """
        @summary: Register two images passing the same name for both

        1) Register image passing only name
        2) Verify that the response code is 201
        3) Add the image to the resource pool for deletion
        4) Register another image passing only the same name
        5) Verify that the response code is 201
        6) Add the image to the resource pool for deletion
        7) Verify that the image ids are not the equal
        """

        name = rand_name('register_image')

        resp = self.images.client.register_image(name=name)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        reg_image = resp.entity

        self.resources.add(reg_image.id_, self.images.client.delete_image)

        resp = self.images.client.register_image(name=name)
        self.assertEqual(
            resp.status_code, 201,
            Messages.STATUS_CODE_MSG.format(201, resp.status_code))
        alt_reg_image = resp.entity

        self.resources.add(alt_reg_image.id_, self.images.client.delete_image)

        self.assertNotEqual(
            reg_image.id_, alt_reg_image.id_,
            msg=('Unexpected image ids received. Expected: Image {0} to be '
                 'different from image {1} '
                 'Received: The same image ids'.format(reg_image.id_,
                                                       alt_reg_image.id_)))

    @data_driven_test(
        ImagesDatasetListGenerator.RegisterImageInvalidValues())
    def ddtest_register_image_passing_invalid_values(self, prop):
        """
        @summary: Register image passing invalid value for image property

        @param prop: Key-value pair containing the image property to validate
        @type prop: Dictionary

        1) Register image passing invalid value for image property
        2) Verify that the response code is 400
        """

        # Each prop passed in only has one key-value pair
        for key, val in prop.iteritems():
            prop_key = key

        if prop_key == 'name':
            resp = self.images.client.register_image(**prop)
        else:
            resp = self.images.client.register_image(
                name=rand_name('register_image'), **prop)
        self.assertEqual(
            resp.status_code, 400,
            Messages.STATUS_CODE_MSG.format(400, resp.status_code))

    def test_register_public_image(self):
        """
        @summary: Register a public image by setting the visibility property to
        public

        1) Register image setting the visibility property to public
        2) If the allow_public_images_crud property is true, verify
        that the response code is 201, else verify that the response code is
        403
        3) If the allow_public_images_crud property is true, add the image for
        deletion. List all images accounting for pagination and verify that
        the image is present.
        """

        name = rand_name('register_image')
        resp = self.images.client.register_image(
            name=name, visibility=ImageVisibility.PUBLIC)

        if self.images.config.allow_public_images_crud:
            self.assertEqual(
                resp.status_code, 201,
                Messages.STATUS_CODE_MSG.format(201, resp.status_code))
            reg_image = resp.entity

            self.resources.add(reg_image.id_, self.images.client.delete_image)

            list_images = self.images.behaviors.list_all_images()

            image_names = [image.name for image in list_images]
            self.assertIn(
                name, image_names,
                msg=('Unexpected image name received. Expected: {0} in {1} '
                     'Received: Was not present').format(name, image_names))

        else:
            self.assertEqual(
                resp.status_code, 403,
                Messages.STATUS_CODE_MSG.format(403, resp.status_code))
