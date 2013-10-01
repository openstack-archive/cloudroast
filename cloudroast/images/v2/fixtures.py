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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.common.types import ImageDiskFormat, \
    ImageContainerFormat
from cloudcafe.images.config import ImagesConfig, AdminUserConfig
from cloudcafe.images.v2.client import ImageClient as ImagesV2Client


class ImagesV2Fixture(BaseTestFixture):
    """
    @summary: Base fixture for Images V2 API tests
    """

    @classmethod
    def setUpClass(cls):
        super(ImagesV2Fixture, cls).setUpClass()
        cls.config = ImagesConfig()
        cls.resources = ResourcePool()

        cls.access_data = AuthProvider.get_access_data()
        cls.admin_access_data = AuthProvider.get_access_data(
            None,
            AdminUserConfig())

        cls.images_endpoint = '{base_url}/v2'.format(
            base_url=cls.config.base_url)

        cls.api_client = ImagesV2Client(cls.images_endpoint,
                                        cls.access_data.token.id_,
                                        'json', 'json')
        cls.admin_api_client = ImagesV2Client(cls.images_endpoint,
                                              cls.admin_access_data.token.id_,
                                              'json', 'json')

        cls.image_schema_json = (
            open(cls.config.image_schema_json).read().rstrip())

        cls.images_schema_json = (
            open(cls.config.images_schema_json).read().rstrip())

    @classmethod
    def tearDownClass(cls):
        super(ImagesV2Fixture, cls).tearDownClass()
        cls.resources.release()

    def register_basic_image(self):
        response = self.api_client.create_image(
            name=rand_name('basic_image_'),
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)

        image = response.entity

        self.resources.add(self.api_client.delete_image, image.id_)

        return image.id_

    def register_private_image(self):
        response = self.api_client.create_image(
            name=rand_name('private_image_'), visibility='private',
            container_format=ImageContainerFormat.BARE,
            disk_format=ImageDiskFormat.RAW)

        image = response.entity

        self.resources.add(self.api_client.delete_image, image.id_)

        return image.id_

    def get_member_ids(self, image_id):
        response = self.api_client.list_members(image_id)

        return [member.member_id for member in response.entity]
