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
        roles = response.entity
        self.assertEqual(200, response.status_code)
        self.assertIn(admin_role, roles)

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
