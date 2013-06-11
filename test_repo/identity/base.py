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

from unittest import TestCase
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.identity.v2_0.tenants_api.client import TenantsAPI_Client
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client

IDENTITY_ENDPOINT_URL = "http://localhost:5000"


class BaseIdentityAdminTest(TestCase):
    def setUpClass(self):
        self.tenant_id = "093362c0d50644c6af606c1e67e21d3f"
        self.url = IDENTITY_ENDPOINT_URL
        self.auth_token = "AUTH_TOKEN"
        self.serialize_format = "json"
        self.deserialize_format = "json"
        self.token_client = TokenAPI_Client(url=self.url,
                                            auth_token=self.auth_token,
                                            deserialize_format=self
                                            .deserialize_format,
                                            serialize_format=self.
                                            serialize_format)
        self.tenant_client = TenantsAPI_Client(url=self.url,
                                               auth_token=self.auth_token,
                                               deserialize_format=self
                                               .deserialize_format,
                                               serialize_format=self
                                               .serialize_format)

        self.data = DataGenerator(self.tenant_client)

    def tearDownClass(self):
        self.data.teardown_all()

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


class DataGenerator(object):
    def __init__(self, client):
        self.client = client
        self.users = []
        self.tenants = []
        self.roles = []
        self.role_name = None

    def setup_test_user(self):
        """Set up a test user."""
        self.setup_test_tenant()
        self.test_user_name = rand_name('test_user_')
        self.test_user_email = self.test_user_name + '@testmail.tm'
        resp, self.user = self.client.create_user_for_a_tenant(
            name=self.test_user_name,
            tenant_id=self.tenant['id'],
            email=self.test_user_email,
            enabled=True)
        self.users.append(self.user)

    def setup_test_tenant(self):
        """Set up a test tenant."""
        self.test_tenant_name = rand_name('test_tenant_')
        self.test_tenant_description = rand_name('desc_')
        self.test_tenant_enabled = True
        resp, self.tenant = self.client.create_tenant(
            name=self.test_tenant_name,
            description=self.test_tenant_description,
            enabled=self.test_tenant_enabled)
        self.tenants.append(self.tenant)

    def setup_test_role(self):
        """Set up a test role."""
        self.test_role_name = rand_name('role')
        resp, self.role = self.client.create_role_for_tenant_user(
            name=self.test_role_name,
            user_id=self.user['id'],
            tenant_id=self.tenant['id'])
        self.roles.append(self.role)

    def teardown_all(self):
        for user in self.users:
            self.client.delete_user(user['id'])
        for tenant in self.tenants:
            self.client.delete_tenant(tenant['id'])

        self.client.delete_role_of_tenant_user(
            tenant_id=self.tenant['id'],
            user_id=self.user['id'])
