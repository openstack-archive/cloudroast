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


class UsersTest(BaseIdentityAdminTest):

    @classmethod
    def setUpClass(cls):
        super(UsersTest, cls).setUpClass()
        cls.user_name = rand_name("user-test-")
        cls.user_email = "{0}@testmail.com".format(cls.user_name)
        cls.user_enabled = True

    @classmethod
    def tearDownClass(cls):
        super(UsersTest, cls).tearDownClass()

    def test_create_user_for_tenant(self):
        tenant = self._set_tenant()
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=self.user_name,
            email=self.user_email,
            enabled=self.user_enabled)
        user = response.entity
        self.addCleanup(self.tenant_client.delete_user, user.id_)
        self.assertEqual(200, response.status_code)
        self.assertEqual(user.name, self.user_name)
        self.assertEqual(user.email, self.user_email)
        self.assertEqual(user.enabled, self.user_enabled)
        self.assertEqual(user.tenant_id, tenant.id_)

    def test_create_user_for_tenant_by_unauthorized_user(self):
        tenant = self._set_tenant()
        user_name = rand_name("user-test-")
        response = self.demo_tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            email="{0}@testmail.com".format(user_name),
            enabled=self.user_enabled)
        self.assertEqual(403, response.status_code)

    def test_create_user_for_tenant_with_request_without_token(self):
        tenant = self._set_tenant()
        user_name = rand_name("user-test-")
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            email=self.user_email,
            enabled=self.user_enabled,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(400, response.status_code)

    def test_create_user_with_empty_name(self):
        tenant = self._set_tenant()
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            email=self.user_email,
            enabled=self.user_enabled)
        self.assertEqual(400, response.status_code)
        self.assertIn("Name field is required and cannot be empty",
                      response.content)

    def test_create_user_for_tenant_with_name_length_over_64(self):
        tenant = self._set_tenant()
        user_name = "t" * 65
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            enabled=self.user_enabled)
        self.assertEqual(400, response.status_code)
        self.assertIn("User name should not be greater than 64 characters.",
                      response.content)

    def test_create_user_for_tenant_with_duplicate_name(self):
        tenant = self._set_tenant()
        duplicate_name = rand_name("user-dupl-")
        first_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=duplicate_name,
            email="{0}@testmail.com".format(rand_name("user-dup-")),
            enabled=self.user_enabled)
        user = first_response.entity
        self.addCleanup(self.tenant_client.delete_user, user.id_)
        self.assertEqual(200, first_response.status_code)
        duplicate_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=duplicate_name,
            email=self.user_email,
            enabled=self.user_enabled)
        self.assertEqual(409, duplicate_response.status_code)

    def test_create_user_for_tenant_with_empty_email(self):
        """Email format is not validated while creating a user for a tenant """
        tenant = self._set_tenant()
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=rand_name("user-test-"),
            enabled=self.user_enabled)
        self.assertEqual(200, response.status_code)

    def test_create_user_for_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=funky_tenant_id,
            name=rand_name("user-test-"),
            enabled=True)
        self.assertEqual(404, response.status_code)
        self.assertIn(
            "Could not find project, {0}.".format(funky_tenant_id),
            response.content)

    def test_list_users(self):
        list_users_response = self.tenant_client.list_users()
        self.assertEqual(200, list_users_response.status_code)

    def test_list_users_by_unauthorized_user(self):
        list_users_response = self.demo_tenant_client.list_users()
        self.assertEqual(403, list_users_response.status_code)

    def test_list_users_with_request_without_token(self):
        list_users_response = self.demo_tenant_client.list_users(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, list_users_response.status_code)
        self.assertIn("Could not find token, None.",
                      list_users_response.content)

    def test_get_users_for_tenant(self):
        tenant = self._set_tenant()
        user_name = rand_name("user-test-")
        create_user_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            email=self.user_email,
            enabled=self.user_enabled)
        tenant_user = create_user_response.entity
        self.addCleanup(self.tenant_client.delete_service, tenant_user.id_)
        get_users_response = self.tenant_client.get_users_for_tenant(
            tenant_id=tenant.id_)
        tenant_users = get_users_response.entity
        self.assertEqual(200, get_users_response.status_code)
        self.assertIn(tenant_user, tenant_users)

    def test_get_users_for_tenant_by_unauthorized_user(self):
        tenant = self._set_tenant()
        get_users_response = self.demo_tenant_client.get_users_for_tenant(
            tenant_id=tenant.id_)
        self.assertEqual(403, get_users_response.status_code)

    def test_get_users_for_tenant_with_request_without_token(self):
        tenant = self._set_tenant()
        get_users_response = self.tenant_client.get_users_for_tenant(
            tenant_id=tenant.id_,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, get_users_response.status_code)
        self.assertIn("Could not find token, None.",
                      get_users_response.content)

    def test_get_users_for_non_existent_tenant(self):
        funky_tenant_id = "FUNKY_TENANT_ID"
        get_users_response = self.tenant_client.get_users_for_tenant(
            tenant_id=funky_tenant_id)
        self.assertEqual(404, get_users_response.status_code)
        self.assertIn("Could not find project, {0}.".format(funky_tenant_id),
                      get_users_response.content)

    def test_delete_user(self):
        tenant = self._set_tenant()
        create_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=rand_name("user-test-"),
            email=self.user_email,
            enabled=self.user_enabled)
        user = create_response.entity
        delete_response = self.tenant_client.delete_user(user_id=user.id_)
        self.assertEqual(204, delete_response.status_code)
        self.assertNotIn(user, self.tenant_client.get_users_for_tenant(
            tenant_id=tenant.id_))

    def test_delete_user_by_unauthorized_user(self):
        tenant = self._set_tenant()
        user_name = rand_name("user-test-")
        create_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            email="{0}@testmail.com".format(user_name),
            enabled=self.user_enabled)
        user = create_response.entity
        delete_response = self.demo_tenant_client.delete_user(user_id=user.id_)
        self.assertEqual(403, delete_response.status_code)

    def test_delete_user_with_request_without_token(self):
        tenant = self._set_tenant()
        user_name = rand_name("user-test-")
        create_response = self.tenant_client.create_user_for_a_tenant(
            tenant_id=tenant.id_,
            name=user_name,
            email="{0}@testmail.com".format(user_name),
            enabled=self.user_enabled)
        user = create_response.entity
        delete_response = self.tenant_client.delete_user(
            user_id=user.id_,
            requestslib_kwargs=self.auth_token)
        self.assertEqual(401, delete_response.status_code)
        self.assertIn("Could not find token, None.", delete_response.content)

    def test_delete_non_existent_user(self):
        user_funky_id = "USER_FUNKY_ID"
        delete_response = self.tenant_client.delete_user(
            user_id=user_funky_id)
        self.assertEqual(404, delete_response.status_code)
        self.assertIn("Could not find user, {0}.".format(user_funky_id),
                      delete_response.content)
