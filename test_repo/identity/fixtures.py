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
from cloudcafe.identity.config import IdentityEndpointConfig
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client


class BaseIdentityAdminTest(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        cls.tenant_id = "093362c0d50644c6af606c1e67e21d3f"
        cls.auth_token = "AUTH_TOKEN"
        cls.serialize_format = "json"
        cls.deserialize_format = "json"

        cls.identity_config = IdentityEndpointConfig()
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

    def disable_user(self, user_name):
        user = self.get_user_by_name(user_name)
        self.tenant_client.update_user(user_id=user['id'], enabled=False)

    def disable_tenant(self, tenant_name):
        tenant = self.get_tenant_by_name(tenant_name)
        self.tenant_client.update_tenant(tenant_id=tenant['id'], enabled=False)

    def get_user_by_name(self, name):
        _, users = self.tenant_client.list_users()
        user = [user for user in users if user['name'] == name]
        if len(user) > 0:
            return user[0]

    def get_tenant_by_name(self, name):
        _, tenants = self.tenant_client.list_tenants()
        tenant = [tenant for tenant in tenants if tenant['name'] == name]
        if len(tenant) > 0:
            return tenant[0]

    def get_role_by_name(self, name, user_id):
        _, roles = self.tenant_client.get_users_roles_on_tenant(
            tenant_id=self.tenant_id, user_id=user_id)
        role = [role for role in roles if role['name'] == name]
        if len(role) > 0:
            return role[0]