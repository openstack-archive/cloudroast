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


class RolesTest(BaseIdentityAdminTest):
    def test_list_roles(self):
        admin_role = self.tenant_behavior.get_role_by_name(
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
        response = self.extension_client.list_roles(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, response.status_code)

    def test_create_role(self):
        role_name = rand_name("role-test-")
        create_response = self.extension_client.create_role(name=role_name)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)
        list_role_response = self.extension_client.list_roles()
        self.assertEqual(200, create_response.status_code)
        self.assertIn(create_response.entity, list_role_response.entity)

    def test_create_role_with_blank_name(self):
        response = self.extension_client.create_role()
        self.assertEqual(400, response.status_code)
        self.assertIn("Name field is required and cannot be empty",
                      response.content)

    def test_create_duplicate_role(self):
        role_name = rand_name("role-dup-")
        create_response = self.extension_client.create_role(name=role_name)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)
        response = self.extension_client.create_role(name=role_name)
        self.assertEqual(409, response.status_code)

    def test_delete_existent_role(self):
        role_name = rand_name("role-test-")
        create_response = self.extension_client.create_role(name=role_name)
        self.addCleanup(self.extension_client.delete_role,
                        create_response.entity.id_)
        delete_response = self.extension_client.delete_role(
            role_id=create_response.entity.id_)
        list_role_response = self.extension_client.list_roles()
        self.assertEqual(204, delete_response.status_code)
        self.assertNotIn(create_response.entity, list_role_response.entity)

    def test_delete_non_existing_role(self):
        delete_response = self.extension_client.delete_role(
            role_id="JUNK_ROLE_ID_999")
        self.assertEqual(404, delete_response.status_code)

    def test_assign_role_to_tenant_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.addCleanup(self.extension_client.delete_role, role.id_)
        assign_role_response = self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        self.assertEqual(200, assign_role_response.status_code)

    def test_assign_role_to_tenant_user_by_unauthorized_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        assign_role_response = (
            self.demo_tenant_client.assign_role_to_tenant_user(
                tenant_id=tenant.id_,
                user_id=tenant_user.id_,
                name=role.name,
                role_id=role.id_))
        self.assertEqual(403, assign_role_response.status_code)

    def test_assign_role_to_tenant_user_request_without_token(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        assign_role_response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_,
            requestslib_kwargs=self.auth_token))
        list_roles_response = self.extension_client.list_roles()
        self.assertEqual(401, assign_role_response.status_code)
        self.assertIsNot(role, list_roles_response.entity)

    def test_assign_role_to_tenant_user_for_non_existent_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        assign_role_response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id="JUNK_USER_ID_999",
            name=role.name,
            role_id=role.id_))
        self.assertEqual(404, assign_role_response.status_code)

    def test_assign_role_to_tenant_user_for_non_existent_role(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        assign_role_response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name="JUNK_ROLE_NAME",
            role_id="JUNK_ROLE_ID_999"))
        self.assertEqual(404, assign_role_response.status_code)

    def test_assign_duplicate_role_to_tenant_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        assign_duplicate_role_response = (
            self.tenant_client.assign_role_to_tenant_user(
                tenant_id=tenant.id_,
                user_id=tenant_user.id_,
                name=role.name,
                role_id=role.id_))
        self.assertEqual(409, assign_duplicate_role_response.status_code)

    def test_remove_role_to_tenant_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        remove_role_response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            role_id=role.id_)
        self.assertEqual(204, remove_role_response.status_code)

    def test_remove_role_to_tenant_user_unauthorized_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.demo_tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        remove_role_response = (
            self.demo_tenant_client.remove_role_of_tenant_user(
                tenant_id=tenant.id_,
                user_id=tenant_user.id_,
                role_id=role.id_))
        self.assertEqual(403, remove_role_response.status_code)

    def test_remove_role_to_tenant_user_request_without_token(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_,
            requestslib_kwargs=self.auth_token)
        remove_role_response = (self.tenant_client.remove_role_of_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            role_id=role.id_,
            requestslib_kwargs=self.auth_token))
        self.assertEqual(401, remove_role_response.status_code)

    def test_remove_role_to_non_existent_tenant_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        remove_role_response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=tenant.id_,
            user_id="JUNK_USER_ID_999",
            role_id=role.id_)
        self.assertEqual(404, remove_role_response.status_code)

    def test_remove_non_existent_role_to_tenant_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        remove_role_response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            role_id="JUNK_ROLE_ID_999")
        self.assertEqual(404, remove_role_response.status_code)

    def test_remove_role_to_tenant_user_for_non_existent_tenant(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        remove_role_response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id="JUNK_TENANT_ID_999",
            user_id=tenant_user.id_,
            role_id=role.id_)
        self.assertEqual(404, remove_role_response.status_code)

    def test_list_tenant_user_roles(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        list_roles_response = self.tenant_client.get_users_roles_on_tenant(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_)
        self.assertEqual(200, list_roles_response.status_code)
        self.assertIn(role, list_roles_response.entity)

    def test_list_tenant_user_roles_unauthorized_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        list_roles_response = (
            self.demo_tenant_client.get_users_roles_on_tenant(
                tenant_id=tenant.id_,
                user_id=tenant_user.id_))
        self.assertEqual(403, list_roles_response.status_code)

    def test_list_tenant_user_roles_request_without_token(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=tenant_user.id_,
            name=role.name,
            role_id=role.id_)
        list_roles_response = (
            self.tenant_client.get_users_roles_on_tenant(
                tenant_id=tenant.id_,
                user_id=tenant_user.id_,
                requestslib_kwargs=self.auth_token))
        self.assertEqual(401, list_roles_response.status_code)

    def test_list_tenant_user_roles_for_non_existent_user(self):
        (role, tenant, tenant_user) = self._get_role_params()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        list_roles_response = self.tenant_client.get_users_roles_on_tenant(
            tenant_id=tenant.id_,
            user_id="JUNK_USER_ID_999")
        self.assertEqual(404, list_roles_response.status_code)
