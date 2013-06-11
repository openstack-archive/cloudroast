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
from cloudcafe.auth.config import UserConfig
from cloudcafe.auth.provider import AuthProvider
from cloudcafe.identity.config import IdentityEndpointConfig, \
    IdentityTokenConfig
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client


class BaseIdentityAdminTest(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        cls.identity_config = IdentityEndpointConfig()
        cls.token_config = IdentityTokenConfig()
        cls.user_config = UserConfig()
        cls.auth = AuthProvider()

        cls.tenant_id = cls.user_config.tenant_id
        cls.serialize_format = cls.token_config.serialize_format
        cls.deserialize_format = cls.token_config.deserialize_format

        cls.access_data = cls.auth.get_access_data()
        cls.auth_token = cls.access_data.token
        cls.endpoint_url = cls.identity_config.endpoint_url

        cls.token_client = TokenAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.auth_token,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.tenant_client = TenantsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.auth_token,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

    @classmethod
    def tearDownClass(cls):
        super(BaseIdentityAdminTest, cls).tearDownClass()