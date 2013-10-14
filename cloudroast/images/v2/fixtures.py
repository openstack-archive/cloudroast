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
from cloudcafe.common.constants import Messages
from cloudcafe.common.resources import ResourcePool
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.images.config import ImagesConfig
from cloudcafe.images.config import AdminUserConfig
from cloudcafe.images.v2.client import ImageClient as ImagesV2Client

MSG = Messages.ASSERT_MSG


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

    @classmethod
    def tearDownClass(cls):
        super(ImagesV2Fixture, cls).tearDownClass()
        cls.resources.release()

    @classmethod
    def register_basic_image(cls, image_client=None):
        response = cls.api_client.create_image(
            name=rand_name('basic_image_'),
            container_format='bare',
            disk_format='raw')

        image = response.entity

        cls.resources.add(cls.api_client.delete_image, image.id_)

        return image.id_

    @classmethod
    def register_private_image(cls, image_client=None):
        response = cls.api_client.create_image(
            name=rand_name('private_image_'),
            visibility='private',
            container_format='bare',
            disk_format='raw')

        image = response.entity

        cls.resources.add(cls.api_client.delete_image, image.id_)

        return image.id_

    @classmethod
    def get_member_ids(cls, image_id):
        response = cls.api_client.list_members(image_id)

        return [member.member_id for member in response.entity]
