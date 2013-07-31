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
from cloudcafe.identity.config import IdentityTokenConfig
from cloudcafe.identity.v2_0.extensions_api.client import ExtensionsAPI_Client
from cloudcafe.identity.v2_0.tenants_api.behaviors import TenantsBehaviors
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client


class BaseIdentityAdminTest(BaseTestFixture):
    """
    @summary: Base fixture for identity tests
    """

    @classmethod
    def setUpClass(cls):
        super(BaseIdentityAdminTest, cls).setUpClass()
        cls.token_config = IdentityTokenConfig()
        cls.user_config = UserConfig()
        cls.endpoint_url = cls.token_config.authentication_endpoint
        cls.serialize_format = cls.token_config.serialize_format
        cls.deserialize_format = cls.token_config.deserialize_format
        cls.auth_token = {'headers': {'X-Auth-Token': None}}

        cls.token_client = TokenAPI_Client(
            url=cls.endpoint_url,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.admin_auth_response = cls.token_client.authenticate(
            username=cls.token_config.username,
            password=cls.token_config.password,
            tenant_name=cls.token_config.tenant_name)
        cls.access_data = cls.admin_auth_response.entity
        cls.admin_token = cls.access_data.token
        cls.admin = cls.access_data.user

        cls.demo_auth_response = cls.token_client.authenticate(
            username=cls.user_config.username,
            password=cls.user_config.password,
            tenant_name=cls.user_config.tenant_name)
        cls.demo_access_data = cls.demo_auth_response.entity
        cls.demo_token = cls.demo_access_data.token

        cls.tenant_client = TenantsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.admin_token.id_,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.tenant_behavior = TenantsBehaviors(cls.tenant_client)
        cls.demo_tenant = cls.tenant_behavior.get_tenant_by_name(name="demo")
        cls.demo_user = cls.tenant_behavior.get_user_by_name(name="demo")

        cls.admin_role = cls.tenant_behavior.get_role_by_name(
            name="admin",
            user_id=cls.admin.id_,
            tenant_id=cls.admin_token.tenant.id_)

        cls.demo_tenant_client = TenantsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.demo_token.id_,
            deserialize_format=cls.deserialize_format,
            serialize_format=cls.serialize_format)

        cls.extension_client = ExtensionsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.admin_token.id_,
            serialized_format=cls.deserialize_format,
            deserialized_format=cls.deserialize_format)

        cls.demo_extension_client = ExtensionsAPI_Client(
            url=cls.endpoint_url,
            auth_token=cls.demo_token.id_,
            serialized_format=cls.deserialize_format,
            deserialized_format=cls.deserialize_format)

    @classmethod
    def tearDownClass(cls):
        super(BaseIdentityAdminTest, cls).tearDownClass()
