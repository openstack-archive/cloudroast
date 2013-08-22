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
from uuid import uuid4
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cafe.drivers.unittest.decorators import skip_open_issue
from cloudroast.meniscus.fixtures import TenantFixture


class PositiveDatasetList(DatasetList):

    def __init__(self):
        self.append_new_dataset('with_uuid', {'tenant_id': str(uuid4())})
        self.append_new_dataset('with_int', {'tenant_id': None})
        self.append_new_dataset('with_long_str', {'tenant_id': 'a' * 256})


@DataDrivenFixture
class TenantAPI(TenantFixture):

    def _check_create_and_get(self, tenant_id=None):
        tenant_id, resp = self.tenant_behaviors.create_tenant(tenant_id)
        self.assertEqual(resp.status_code, 201)

        resp = self.tenant_client.get_tenant(tenant_id)
        self.assertEqual(resp.status_code, 200)
        return tenant_id, resp

    def _check_reset_token(self, invalidate):
        tenant_id, resp = self._check_create_and_get()
        orig_token = resp.entity[0].token

        resp = self.tenant_client.reset_token(tenant_id,
                                              invalidate_now=invalidate)
        self.assertEqual(resp.status_code, 203)

        resp = self.tenant_client.get_tenant(tenant_id)
        new_token = resp.entity[0].token

        self.assertNotEqual(new_token, orig_token)
        return new_token, orig_token

    @data_driven_test(PositiveDatasetList())
    @tags(type='positive')
    def ddtest_get_tenant(self, tenant_id):
        self._check_create_and_get(tenant_id=tenant_id)

    @skip_open_issue('GitHub', '268')
    @tags(type='positive')
    def test_reset_tenant_token_now(self):
        """ Verify that we can reset the tenant token"""
        self._check_reset_token(invalidate=True)

    @skip_open_issue('GitHub', '268')
    @tags(type='positive')
    def test_reset_tenant_token_later(self):
        """ Verify that we can reset the tenant token"""
        new_token, orig_token = self._check_reset_token(invalidate=False)
        self.assertEqual(new_token.previous, orig_token.valid)
