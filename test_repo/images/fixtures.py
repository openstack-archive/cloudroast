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
from cloudcafe.images.config import ImagesConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.common.resources import ResourcePool
from cloudcafe.images.v1_0.client import ImagesClient as ImagesV1Client
from cloudcafe.images.behaviors import ImageBehaviors


class ImageFixture(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageFixture, cls).setUpClass()
        cls.config = ImagesConfig()
        cls.resources = ResourcePool()

    @classmethod
    def tearDownClass(cls):
        cls.resources.release()
        super(ImageFixture, cls).tearDownClass()


class ImageV1Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageV1Fixture, cls).setUpClass()
        access_data = AuthProvider().get_access_data()
        images_endpoint = '{base_url}/{api_version}'.format(
            base_url=cls.config.base_url,
            api_version=cls.config.api_version)

        cls.api_client = ImagesV1Client(images_endpoint, access_data.token.id_,
                                        'json', 'json')
        cls.behaviors = ImageBehaviors(cls.api_client, cls.config)
