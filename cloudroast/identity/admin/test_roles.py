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


class RolesTest(BaseIdentityAdminTest):
    def test_list_roles(self):
        response = self.extension_client.list_roles()
        self.assertEqual(200, response.status_code)
        self.assertIn(self.admin_role, response.entity)

    def test_list_roles_by_unauthorized_user(self):
        response = self.demo_extension_client.list_roles()
        self.assertEqual(403, response.status_code)

    def test_list_roles_with_request_without_token(self):
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
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        create_duplicate_role = self.extension_client.create_role(
            name=role.name)
        self.assertEqual(409, create_duplicate_role.status_code)

    def test_delete_role(self):
        role = self._create_role()
        delete_response = self.extension_client.delete_role(
            role_id=role.id_)
        self.assertEqual(204, delete_response.status_code)
        list_role_response = self.extension_client.list_roles()
        self.assertNotIn(role, list_role_response.entity)

    def test_delete_non_existent_role(self):
        response = self.extension_client.delete_role(
            role_id="FUNKY_ROLE_ID_999")
        self.assertEqual(404, response.status_code)

    def test_assign_role_to_tenant_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        response = self.tenant_client.assign_role_to_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            name=role.name,
            role_id=role.id_)
        self.assertEqual(200, response.status_code)

    def test_assign_role_to_tenant_user_by_unauthorized_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        response = (
            self.demo_tenant_client.assign_role_to_tenant_user(
                tenant_id=self.demo_tenant.id_,
                user_id=self.demo_user.id_,
                name=role.name,
                role_id=role.id_))
        self.assertEqual(403, response.status_code)

    def test_assign_role_to_tenant_user_request_without_token(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            name=role.name,
            role_id=role.id_,
            requestslib_kwargs=self.auth_token))
        self.assertEqual(401, response.status_code)

    def test_assign_role_to_tenant_user_for_non_existent_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id="FUNKY_USER_ID_999",
            name=role.name,
            role_id=role.id_))
        self.assertEqual(404, response.status_code)

    def test_assign_role_to_tenant_user_for_non_existent_role(self):
        response = (self.tenant_client.assign_role_to_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            name="FUNKY_ROLE_NAME",
            role_id="FUNKY_ROLE_ID_999"))
        self.assertEqual(404, response.status_code)

    def test_assign_duplicate_role_to_tenant_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        assign_duplicate_role_response = (
            self.tenant_client.assign_role_to_tenant_user(
                tenant_id=self.demo_tenant.id_,
                user_id=self.demo_user.id_,
                name=role.name,
                role_id=role.id_))
        self.assertEqual(409, assign_duplicate_role_response.status_code)

    def test_remove_role_to_tenant_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            role_id=role.id_)
        self.assertEqual(204, response.status_code)

    def test_remove_role_to_tenant_user_by_unauthorized_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        response = (
            self.demo_tenant_client.remove_role_of_tenant_user(
                tenant_id=self.demo_tenant.id_,
                user_id=self.demo_user.id_,
                role_id=role.id_))
        self.assertEqual(403, response.status_code)

    def test_remove_role_to_tenant_user_with_request_without_token(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        response = (self.tenant_client.remove_role_of_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            role_id=role.id_,
            requestslib_kwargs=self.auth_token))
        self.assertEqual(401, response.status_code)

    def test_remove_role_to_non_existent_tenant_user(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id="FUNKY_USER_ID_999",
            role_id=role.id_)
        self.assertEqual(404, response.status_code)

    def test_remove_non_existent_role_for_tenant_user(self):
        response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_,
            role_id="FUNKY_ROLE_ID_999")
        self.assertEqual(404, response.status_code)

    def test_remove_role_to_tenant_user_for_non_existent_tenant(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        remove_role_response = self.tenant_client.remove_role_of_tenant_user(
            tenant_id="FUNKY_TENANT_ID_999",
            user_id=self.demo_user.id_,
            role_id=role.id_)
        self.assertEqual(404, remove_role_response.status_code)

    def test_get_tenant_user_roles(self):
        role = self._create_role()
        self.addCleanup(self.extension_client.delete_role, role.id_)
        self._assign_role_to_tenant_user(
            self.demo_tenant,
            self.demo_user,
            role)
        list_roles_response = self.tenant_client.get_users_roles_on_tenant(
            tenant_id=self.demo_tenant.id_,
            user_id=self.demo_user.id_)
        self.assertEqual(200, list_roles_response.status_code)
        self.assertIn(role, list_roles_response.entity)

    def test_get_tenant_user_roles_by_unauthorized_user(self):
        response = (
            self.demo_tenant_client.get_users_roles_on_tenant(
                tenant_id=self.demo_tenant.id_,
                user_id=self.demo_user.id_))
        self.assertEqual(403, response.status_code)

    def test_get_tenant_user_roles_with_request_without_token(self):
        response = (
            self.tenant_client.get_users_roles_on_tenant(
                tenant_id=self.demo_tenant.id_,
                user_id=self.demo_user.id_,
                requestslib_kwargs=self.auth_token))
        self.assertEqual(401, response.status_code)

    def test_get_tenant_user_roles_for_non_existent_user(self):
        response = self.tenant_client.get_users_roles_on_tenant(
            tenant_id=self.demo_tenant.id_,
            user_id="FUNKY_USER_ID_999")
        self.assertEqual(404, response.status_code)

    def _create_role(self):
        response = self.extension_client.create_role(
            name=rand_name("role-test-"))
        self.assertEqual(200, response.status_code)
        return response.entity

    def _assign_role_to_tenant_user(self, tenant, user, role):
        response = self.tenant_client.assign_role_to_tenant_user(
            tenant_id=tenant.id_,
            user_id=user.id_,
            name=role.name,
            role_id=role.id_)
        self.assertEqual(200, response.status_code)
