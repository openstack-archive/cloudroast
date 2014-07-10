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
from cloudcafe.images.common.types import ImageType

from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestGetImage(ObjectStorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(TestGetImage, cls).setUpClass()
        cls.images = cls.images_behavior.create_images_via_task(count=2)

    @tags(type='smoke')
    def test_get_image(self):
        """
        @summary: Get image

        1) Given a previously created image, get image
        2) Verify that the response code is 200
        3) Verify that the created image is returned
        """

        image = self.images.pop()
        response = self.images_client.get_image(image.id_)
        self.assertEqual(response.status_code, 200)
        get_image = response.entity
        errors = self._validate_get_image(image, get_image)
        if get_image.image_type != ImageType.IMPORT:
            errors.append(self.error_msg.format(
                'image_type', ImageType.IMPORT, get_image.image_type))
        if get_image.min_disk != self.images_config.min_disk:
            errors.append(self.error_msg.format(
                'min_disk', self.images_config.min_disk, get_image.min_disk))
        self.assertEqual(errors, [])

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
        image = response.entity

        errors = self.images_behavior.validate_image(image)
        if image.image_type != ImageType.IMPORT:
            errors.append(self.error_msg.format(
                'image_type', ImageType.IMPORT, image.image_type))
        if image.min_disk != self.images_config.min_disk:
            errors.append(self.error_msg.format(
                'min_disk', self.images_config.min_disk, image.min_disk))
        self.assertEqual(errors, [])

    @tags(type='positive', regression='true')
    def test_get_image_as_member_of_shared_image(self):
        """
        @summary: Get image as member of shared image

         1) Given a previously created image, add member to image using an
         alternate tenant id
         2) Verify that the response code is 200
         3) Get image using the tenant who was added as a member
         4) Verify that the response code is 200
         5) Verify that the image returned is the image that was created by
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

        if image.auto_disk_config != 'False':
            errors.append(self.error_msg.format(
                'auto_disk_config', 'False', image.auto_disk_config))
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
        if image.os_type != 'linux':
            errors.append(self.error_msg.format(
                'os_type', 'linux', image.os_type))
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
        if image.user_id != self.access_data.user.id_:
            errors.append(self.error_msg.format(
                'user_id', 'not None', image.user_id))
        if image.visibility != get_image.visibility:
            errors.append(self.error_msg.format(
                'visibility', image.visibility, get_image.visibility))
        if image.owner != get_image.owner:
            errors.append(self.error_msg.format(
                'owner', image.owner, get_image.owner))

        return errors
