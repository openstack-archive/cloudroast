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

from cloudcafe.auth.config import UserAuthConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tenants_api.behaviors import TenantsBehaviors
from cloudcafe.images.v1.client import ImagesClient as ImagesV1Client
from cloudcafe.images.v1.behaviors import ImagesV1Behaviors

from cloudroast.images.fixtures import ImagesFixture


class ImagesV1Fixture(ImagesFixture):
    @classmethod
    def setUpClass(cls):
        super(ImagesV1Fixture, cls).setUpClass()
        access_data = AuthProvider().get_access_data()
        images_endpoint = '{base_url}/v1'.format(
            base_url=cls.config.base_url)

        cls.remote_image = cls.config.remote_image
        cls.http_image = cls.config.http_image

        cls.tenants_client = TenantsAPI_Client(
            UserAuthConfig().auth_endpoint,
            access_data.token.id_,
            'json', 'json')

        cls.api_client = ImagesV1Client(images_endpoint, access_data.token.id_,
                                        'json', 'json')
        cls.behaviors = ImagesV1Behaviors(cls.api_client, cls.config)
        cls.tenant_ids = TenantsBehaviors(cls.tenants_client).get_all_tenant_ids()
