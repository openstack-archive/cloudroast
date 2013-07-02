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
import json

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.identity.config import \
    IdentityTokenConfig, IdentityExtensionConfig
from cloudcafe.identity.v2_0.extensions_api.client import ExtensionAPI_Client
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client
from cloudcafe.identity.v2_0.tokens_api.models.responses.access import Access


class BaseIdentityAdminTest(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(BaseIdentityAdminTest, cls).setUpClass()
        cls.token_config = IdentityTokenConfig()
        cls.extension_config = IdentityExtensionConfig()
        cls.endpoint_url = cls.token_config.authentication_endpoint
        cls.serialize_format = cls.token_config.serialize_format
        cls.deserialize_format = cls.token_config.deserialize_format

        cls.token_client = TokenAPI_Client(
            url=cls.endpoint_url,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.auth_response = cls.token_client.authenticate(
            username=cls.token_config.username,
            password=cls.token_config.password,
            tenant_name=cls.token_config.tenant_name)

        cls.access_dict = json.loads(cls.auth_response.content).get('access')
        cls.access_data = Access._dict_to_obj(cls.access_dict)
        cls.token = cls.access_data.token
        cls.user = cls.access_data.user

        cls.tenant_client = TenantsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.token.id_,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.extension_client = ExtensionAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.token.id_,
            serialized_format=cls.deserialize_format,
            deserialized_format=cls.deserialize_format,
            keystone_admin=cls.extension_config.openstack_keystone_admin
        )

    @classmethod
    def tearDownClass(cls):
        super(BaseIdentityAdminTest, cls).tearDownClass()
