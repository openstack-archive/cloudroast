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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.identity.fixtures import BaseIdentityAdminTest


class TenantsTest(BaseIdentityAdminTest):

    @classmethod
    def setUpClass(cls):
        super(TenantsTest, cls).setUpClass()
        cls.tenant_name = rand_name("tenant-test-")
        cls.tenant_desc = rand_name("desc-test-")
        cls.tenant_enabled = True
        cls.updated_name = rand_name("tenant-updated-name-")
        cls.updated_desc = rand_name("tenant-updated-desc")
        cls.updated_enabled = False

    def test_create_tenant(self):
        response = self.tenant_client.create_tenant(
            name=self.tenant_name,
            description=self.tenant_desc,
            enabled=self.tenant_enabled)
        tenant = response.entity
        self.assertEqual(response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_tenant, tenant.id_)
        self.assertEqual(tenant.name, self.tenant_name)
        self.assertEqual(tenant.description, self.tenant_desc)
        self.assertEqual(tenant.enabled, self.tenant_enabled)

    def test_create_tenant_by_unauthorized_user(self):
        response = self.demo_tenant_client.create_tenant(
            name=rand_name("tenant-test-"),
            description=self.tenant_desc,
            enabled=self.tenant_enabled)
        self.assertEqual(response.status_code, 403)

    def test_create_tenant_with_request_without_token(self):
        response = self.tenant_client.create_tenant(
            name=rand_name("tenant-test-"),
            description=self.tenant_desc,
            enabled=self.tenant_enabled,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(response.status_code, 400)

    def test_create_tenant_with_duplicate_name(self):
        response = self.tenant_client.create_tenant(
            name=self.demo_tenant.name)
        self.assertEqual(response.status_code, 409)

    def test_create_tenant_with_empty_name(self):
        response = self.tenant_client.create_tenant(
            description=self.tenant_desc,
            enabled=self.tenant_enabled)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name field is required and cannot be empty",
                      response.content)

    def test_create_tenant_with_name_length_over_64_characters(self):
        response = self.tenant_client.create_tenant(name='t' * 65)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Project name should not be greater than 64 "
                      "characters", response.content)

    def test_list_tenant(self):
        response = self.tenant_client.list_tenants()
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.demo_tenant, response.entity)

    def test_list_tenant_by_unauthorized_user(self):
        response = self.demo_tenant_client.list_tenants()
        self.assertEqual(response.status_code, 403)

    def test_list_tenant_with_request_without_token(self):
        response = self.tenant_client.list_tenants(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Could not find token, None.",
                      response.content)

    def test_delete_tenant(self):
        create_response = self.tenant_client.create_tenant(
            name=self.tenant_name,
            description=self.tenant_desc,
            enabled=self.tenant_enabled)
        tenant = create_response.entity
        delete_response = self.tenant_client.delete_tenant(
            tenant_id=tenant.id_)
        self.assertEqual(delete_response.status_code, 204)
        self.assertNotIn(tenant, self.tenant_client.list_tenants())

    def test_delete_tenant_by_unauthorized_user(self):
        response = self.demo_tenant_client.delete_tenant(
            tenant_id=self.demo_tenant.id_)
        self.assertEqual(response.status_code, 403)

    def test_delete_tenant_with_request_without_token(self):
        response = self.tenant_client.delete_tenant(
            tenant_id=self.demo_tenant.id_,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(response.status_code, 401)
        self.assertIn("Could not find token, None.", response.content)

    def test_delete_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        response = self.tenant_client.delete_tenant(
            tenant_id=funky_tenant_id)
        self.assertEqual(response.status_code, 404)
        self.assertIn("Could not find project, {0}.".format(funky_tenant_id),
                      response.content)

    def test_update_tenant(self):
        create_response = self.tenant_client.create_tenant(
            name=self.tenant_name,
            description=self.tenant_desc,
            enabled=self.tenant_enabled)
        tenant = create_response.entity
        self.assertEqual(create_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_tenant, tenant.id_)
        update_response = self.tenant_client.update_tenant(
            tenant_id=tenant.id_,
            name=self.updated_name,
            description=self.updated_desc,
            enabled=self.updated_enabled)
        updated_tenant = update_response.entity
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(updated_tenant.name, self.updated_name)
        self.assertEqual(updated_tenant.description, self.updated_desc)
        self.assertEqual(updated_tenant.enabled, self.updated_enabled)
        self.assertEqual(updated_tenant.id_, tenant.id_)

    def test_update_tenant_by_unauthorized_user(self):
        response = self.demo_tenant_client.update_tenant(
            tenant_id=self.demo_tenant.id_,
            name=self.tenant_name)
        self.assertEqual(response.status_code, 403)

    def test_update_tenant_request_without_token(self):
        response = self.tenant_client.update_tenant(
            tenant_id=self.demo_tenant.id_,
            name=self.tenant_name,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(response.status_code, 400)

    def test_update_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        response = self.tenant_client.update_tenant(
            tenant_id=funky_tenant_id,
            name=rand_name("tenant-updated-test-"))
        self.assertEqual(response.status_code, 404)
        self.assertIn("Could not find project, {0}.".format(funky_tenant_id),
                      response.content)
