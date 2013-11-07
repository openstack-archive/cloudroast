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
from cloudcafe.images.config import ImagesConfig, AdminUserConfig
from cloudcafe.images.v2.behaviors import ImagesV2Behaviors
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

        cls.images_behavior = ImagesV2Behaviors(images_client=cls.api_client,
                                                images_config=cls.config)

    @classmethod
    def tearDownClass(cls):
        super(ImagesV2Fixture, cls).tearDownClass()
        cls.resources.release()

    @classmethod
    def get_new_images_v2_client(self, auth_data):
        """Return new images v2 client for requested auth data """

        return ImagesV2Client(self.images_endpoint, auth_data.token.id_)
