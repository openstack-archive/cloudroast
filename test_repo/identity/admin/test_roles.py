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
from cloudcafe.compute.common.datagen import rand_name

from cloudcafe.identity.v2_0.tenants_api.behaviors import TenantsBehaviors
from test_repo.identity.fixtures import BaseIdentityAdminTest


class RolesTest(BaseIdentityAdminTest):
    @classmethod
    def setUpClass(cls):
        super(RolesTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(RolesTest, cls).tearDownClass()

    def test_list_roles(self):
        tenant_behavior = TenantsBehaviors(self.tenant_client)
        admin_role = tenant_behavior.get_role_by_name(
            name="admin",
            user_id=self.admin.id_,
            tenant_id=self.admin_token.tenant.id_)
        response = self.extension_client.list_roles()

        self.assertEqual(200, response.status_code)
        self.assertIn(admin_role, response.entity)

    def test_list_roles_by_unauthorized_user(self):
        """
        Response status code 403 indicates that user is not authorized to
        perform the requested action, administration privilege required.
        """
        response = self.demo_extension_client.list_roles()

        self.assertEqual(403, response.status_code)

    def test_list_roles_request_without_token(self):
        response = self.missing_token_client.list_roles()

        self.assertEqual(401, response.status_code)

    def test_create_role(self):
        role_name = rand_name('role-test-')
        create_response = self.extension_client.create_role(name=role_name)
        list_role_response = self.extension_client.list_roles()

        self.assertEqual(200, create_response.status_code)
        self.assertIn(role_name, create_response.content)
        self.assertIn(role_name, list_role_response.content)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)

    def test_create_role_with_blank_name(self):
        response = self.extension_client.create_role()

        self.assertEqual(400, response.status_code)
        self.assertIn("Name field is required and cannot be empty",
                      response.content)

    def test_create_duplicate_role(self):
        role_name = rand_name('role-dup-')
        create_response = self.extension_client.create_role(name=role_name)
        response = self.extension_client.create_role(name=role_name)

        self.assertEqual(409, response.status_code)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)

    def test_delete_existing_role(self):
        role_name = rand_name('role-test-')
        create_response = self.extension_client.create_role(name=role_name)
        delete_response = self.extension_client.delete_role(
            role_id=create_response.entity.id_)
        list_role_response = self.extension_client.list_roles()

        self.assertEqual(204, delete_response.status_code)
        self.assertNotIn(role_name, list_role_response.content)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)

    def test_delete_non_existing_role(self):
        delete_response = self.extension_client.delete_role(
            role_id="NON_EXISTING_ROLE_ID")
        self.assertEqual(404, delete_response.status_code)
