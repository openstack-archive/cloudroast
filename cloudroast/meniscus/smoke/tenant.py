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
from cloudroast.meniscus.fixtures import TenantFixture


class TestTenant(TenantFixture):

    def test_create_tenant(self):
        tenant_id, resp = self.tenant_behaviors.create_tenant()
        self.assertEqual(resp.status_code, 201,
                         'Wrong status code. The tenant was probably not '
                         'created')

    def test_get_tenant(self):
        tenant_id, resp = self.tenant_behaviors.create_tenant()
        resp = self.tenant_client.get_tenant(tenant_id)

        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.entity)
        self.assertEqual(resp.entity[0].tenant_id, tenant_id)
