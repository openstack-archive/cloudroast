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
from cloudcafe.images.common.types import ImageType, TaskTypes
from cloudcafe.images.config import ImagesConfig
from cloudroast.images.fixtures import ComputeIntegrationFixture

images_config = ImagesConfig()
internal_url = images_config.internal_url


class TestGetImage(ComputeIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImage, cls).setUpClass()
        cls.images = []
        server = cls.server_behaviors.create_active_server().entity
        image = cls.compute_image_behaviors.create_active_image(server.id)
        alt_image = cls.compute_image_behaviors.create_active_image(server.id)
        cls.images.append(cls.images_client.get_image(image.entity.id).entity)
        cls.images.append(cls.images_client.get_image(
            alt_image.entity.id).entity)

    @tags(type='smoke')
    def test_get_image(self):
        """
        @summary: Get image

        1) Given a previously created image
        2) Get image
        3) Verify that the response code is 200
        4) Verify that the created image is returned
        """

        image = self.images.pop()
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self._validate_get_image(image, get_image)

    @tags(type='positive', regression='true')
    def test_get_image_after_successful_import(self):
        """
        @summary: Get image after successful import

        1) Create import task
        2) From the successful import task, get image
        3) Verify that the response code is 200
        4) Verify that the response contains the correct properties
        """

        task = self.images_behavior.create_new_task()
        image_id = task.result.image_id

        response = self.images_client.get_image(image_id)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity

        errors = self.images_behavior.validate_image(get_image)
        if get_image.image_type != ImageType.IMPORT:
            errors.append(self.error_msg.format(
                'image_type', ImageType.IMPORT, get_image.image_type))
        self.assertEqual(errors, [])

    @unittest.skipIf(internal_url is None,
                     ('The internal_url property is None, test can only be '
                      'executed against internal Glance nodes'))
    @tags(type='positive', regression='true', internal='true')
    def test_verify_object_and_imported_exported_image_content(self):
        """
        @summary: Verify that an imported image's content is same as the file
        object's content in the customer's container and the exported image's
        content

        1) Get the import file object's content
        2) Verify that the response code is 200
        3) Create new image
        4) Get the new image's file content
        5) Verify that the response code is 200
        6) Verify that the import file object's content is the same data as as
        the image's file content
        7) Export the image
        8) Get the exported file object's content
        9) Verify that the response code is 200
        10) Verify that the export file object's content is the same data as as
        the image's file content
        11) Verify that the import file object's content is the same data as as
        the export file object's content
        """

        response = self.object_storage_client.get_object(
            container_name='test_container', object_name='import_test.vhd')
        self.assertEqual(response.status_code, 200)
        file_content = response.content

        task = self.images_behavior.create_new_task()
        image_id = task.result.image_id

        response = self.images_client.get_image_file(image_id)
        self.assertEqual(response.status_code, 200)
        image_content = response.content

        self.assertEqual(file_content, image_content)

        input_ = {'image_uuid': image_id,
                  'receiving_swift_container': self.export_to}

        task = self.images_behavior.create_new_task(
            input_=input_, type_=TaskTypes.EXPORT)

        export_location = [
            x.strip() for x in task.result.export_location.split('/')]
        response = self.object_storage_client.get_object(
            container_name=export_location[0], object_name=export_location[1])
        self.assertEqual(response.status_code, 200)
        new_file_content = response.content

        self.assertEqual(new_file_content, image_content)
        self.assertEqual(file_content, new_file_content)

    @tags(type='positive', regression='true')
    def test_get_image_as_member_of_shared_image(self):
        """
        @summary: Get image as member of shared image

         1) Given a previously created image
         2) Add member to image using an alternate tenant id
         3) Verify that the response code is 200
         4) Get image using the tenant who was added as a member
         5) Verify that the response code is 200
         6) Verify that the image returned is the image that was created by
         the original tenant
        """

        member_id = self.alt_tenant_id
        image = self.images.pop()
        response = self.images_client.add_member(image.id_, member_id)
        self.assertEqual(response.status_code, 200)
        response = self.alt_images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        self._validate_get_image(image, get_image)

    def _validate_get_image(self, image, get_image):
        """@summary: Validate that the image and get_image responses match"""

        errors = []
        if image.checksum != get_image.checksum:
            errors.append(self.error_msg.format(
                'checksum', image.checksum, get_image.checksum))
        if image.container_format != get_image.container_format:
            errors.append(self.error_msg.format(
                'container_format', image.container_format,
                get_image.container_format))
        if image.created_at != get_image.created_at:
            errors.append(self.error_msg.format(
                'created_at', image.created_at, get_image.created_at))
        if image.disk_format != get_image.disk_format:
            errors.append(self.error_msg.format(
                'disk_format', image.disk_format, get_image.disk_format))
        if image.file_ != get_image.file_:
            errors.append(self.error_msg.format(
                'file_', image.file_, get_image.file_))
        if image.id_ != get_image.id_:
            errors.append(self.error_msg.format(
                'id_', image.id_, get_image.id_))
        if image.image_type != get_image.image_type:
            errors.append(self.error_msg.format(
                'image_type', image.image_type, get_image.image_type))
        if image.min_disk != get_image.min_disk:
            errors.append(self.error_msg.format(
                'min_disk', image.min_disk, get_image.min_disk))
        if image.min_ram != get_image.min_ram:
            errors.append(self.error_msg.format(
                'min_ram', image.min_ram, get_image.min_ram))
        if image.name != get_image.name:
            errors.append(self.error_msg.format(
                'name', image.name, get_image.name))
        if image.protected != get_image.protected:
            errors.append(self.error_msg.format(
                'protected', image.protected, get_image.protected))
        if image.schema != get_image.schema:
            errors.append(self.error_msg.format(
                'schema', image.schema, get_image.schema))
        if image.self_ != get_image.self_:
            errors.append(self.error_msg.format(
                'self_', image.self_, get_image.self_))
        if image.size != get_image.size:
            errors.append(self.error_msg.format(
                'size', image.size, get_image.size))
        if image.status != get_image.status:
            errors.append(self.error_msg.format(
                'status', image.status, get_image.status))
        if image.tags != get_image.tags:
            errors.append(self.error_msg.format(
                'tags', image.tags, get_image.tags))
        if image.updated_at != get_image.updated_at:
            errors.append(self.error_msg.format(
                'updated_at', image.updated_at, get_image.updated_at))
        if image.visibility != get_image.visibility:
            errors.append(self.error_msg.format(
                'visibility', image.visibility, get_image.visibility))
