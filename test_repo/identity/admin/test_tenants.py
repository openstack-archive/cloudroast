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
from test_repo.identity.fixtures import BaseIdentityAdminTest


class TenantsTest(BaseIdentityAdminTest):
    def test_create_tenant(self):
        tenant_name = rand_name("tenant-test-")
        tenant_desc = rand_name("desc-test-")
        tenant_enabled = True
        response = self.tenant_client.create_tenant(
            name=tenant_name,
            description=tenant_desc,
            enabled=tenant_enabled)
        self.addCleanup(
            self.tenant_client.delete_tenant,
            response.entity.id_)
        self.assertEqual(200, response.status_code)
        self.assertEqual(tenant_name, response.entity.name)
        self.assertEqual(tenant_desc, response.entity.description)
        self.assertEqual(tenant_enabled, response.entity.enabled)

    def test_create_tenant_unauthorized_user(self):
        tenant_name = rand_name("tenant-test-")
        tenant_desc = rand_name("desc-test-")
        response = self.demo_tenant_client.create_tenant(
            name=tenant_name,
            description=tenant_desc,
            enabled=True)
        self.assertEqual(403, response.status_code)

    def test_create_tenant_request_without_token(self):
        tenant_name = rand_name("tenant-test-")
        tenant_desc = rand_name("desc-test-")
        response = self.tenant_client.create_tenant(
            name=tenant_name,
            description=tenant_desc,
            enabled=True,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(400, response.status_code)

    def test_create_tenant_with_duplicate_name(self):
        tenant_name = rand_name("tenant-dup-")
        first_response = self.tenant_client.create_tenant(
            name=tenant_name,
            enabled=True)
        self.addCleanup(
            self.tenant_client.delete_tenant,
            first_response.entity.id_)
        self.assertEqual(200, first_response.status_code)
        second_response = self.tenant_client.create_tenant(
            name=tenant_name)
        self.assertEqual(409, second_response.status_code)

    def test_create_tenant_with_empty_name(self):
        response = self.tenant_client.create_tenant()
        self.assertEqual(400, response.status_code)
        self.assertIn("Name field is required and cannot be empty",
                      response.content)

    def test_create_tenant_with_name_length_over_64_characters(self):
        tenant_name = 't' * 65
        response = self.tenant_client.create_tenant(name=tenant_name)
        self.assertEqual(400, response.status_code)
        self.assertIn("Project name should not be greater than 64 "
                      "characters", response.content)

    def test_list_tenant(self):
        tenant_name = rand_name("tenant-test-")
        tenant_desc = rand_name("desc-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name,
            description=tenant_desc,
            enabled=True)
        self.addCleanup(
            self.tenant_client.delete_tenant,
            create_response.entity.id_)
        list_tenants_response = self.tenant_client.list_tenants()
        self.assertEqual(200, list_tenants_response.status_code)
        self.assertIn(create_response.entity, list_tenants_response.entity)

    def test_list_tenant_unauthorized_user(self):
        list_tenants_response = self.demo_tenant_client.list_tenants()
        self.assertEqual(403, list_tenants_response.status_code)

    def test_list_tenant_request_without_token(self):
        list_tenants_response = self.tenant_client.list_tenants(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, list_tenants_response.status_code)
        self.assertIn("Could not find token, None.",
                      list_tenants_response.content)

    def test_delete_tenant(self):
        tenant_name = rand_name("tenant-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name)
        self.addCleanup(self.tenant_client.delete_tenant,
                        create_response.entity.id_)
        delete_response = self.tenant_client.delete_tenant(
            tenant_id=create_response.entity.id_)
        self.assertEqual(204, delete_response.status_code)
        self.assertNotIn(create_response.entity,
                         self.tenant_client.list_tenants())

    def test_delete_tenant_unauthorized_user(self):
        tenant_name = rand_name("tenant-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name)
        self.addCleanup(self.tenant_client.delete_tenant,
                        create_response.entity.id_)
        delete_response = self.demo_tenant_client.delete_tenant(
            tenant_id=create_response.entity.id_)
        self.assertEqual(403, delete_response.status_code)

    def test_delete_tenant_request_without_token(self):
        tenant_name = rand_name("tenant-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name)
        self.addCleanup(self.tenant_client.delete_tenant,
                        create_response.entity.id_)
        delete_response = self.tenant_client.delete_tenant(
            tenant_id=create_response.entity.id_,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, delete_response.status_code)
        self.assertIn("Could not find token, None.", delete_response.content)

    def test_delete_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        delete_response = self.tenant_client.delete_tenant(
            tenant_id=funky_tenant_id)
        self.assertEqual(404, delete_response.status_code)
        self.assertIn("Could not find project, {0}.".format(funky_tenant_id),
                      delete_response.content)

    def test_update_tenant(self):
        tenant_name = rand_name("tenant-test-")
        tenant_desc = rand_name("desc-test-")
        tenant_enabled = False
        create_response = self.tenant_client.create_tenant(
            name=tenant_name,
            description=tenant_desc,
            enabled=tenant_enabled)
        tenant = create_response.entity
        self.addCleanup(self.tenant_client.delete_tenant, tenant.id_)

        updated_name = rand_name("tenant-updated-name-")
        updated_desc = rand_name("tenant-updated-desc")
        updated_enabled = True
        update_response = self.tenant_client.update_tenant(
            tenant_id=tenant.id_,
            name=updated_name,
            description=updated_desc,
            enabled=updated_enabled)
        updated_tenant = update_response.entity
        self.assertEqual(200, update_response.status_code)
        self.assertEqual(updated_name, updated_tenant.name)
        self.assertEqual(updated_desc, updated_tenant.description)
        self.assertEqual(updated_enabled, updated_tenant.enabled)
        self.assertEqual(tenant.id_, updated_tenant.id_)

    def test_update_tenant_unauthorized_user(self):
        tenant_name = rand_name("tenant-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name,
            enabled=True)
        tenant = create_response.entity
        self.addCleanup(self.tenant_client.delete_tenant, tenant.id_)

        updated_name = rand_name("tenant-updated-name-")
        update_response = self.demo_tenant_client.update_tenant(
            tenant_id=tenant.id_,
            name=updated_name)
        self.assertEqual(403, update_response.status_code)

    def test_update_tenant_request_without_token(self):
        tenant_name = rand_name("tenant-test-")
        create_response = self.tenant_client.create_tenant(
            name=tenant_name)
        self.addCleanup(self.tenant_client.delete_tenant,
                        create_response.entity.id_)
        updated_name = rand_name("tenant-updated-name-")
        update_response = self.tenant_client.update_tenant(
            tenant_id=create_response.entity.id_,
            name=updated_name,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(400, update_response.status_code)

    def test_update_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        update_response = self.tenant_client.update_tenant(
            tenant_id=funky_tenant_id,
            name=rand_name("tenant-updated-test-"))
        self.assertEqual(404, update_response.status_code)
        self.assertIn("Could not find project, {0}.".format(funky_tenant_id),
                      update_response.content)
