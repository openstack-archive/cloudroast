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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.auth.config import UserConfig
from cloudcafe.compute.quotas_api.config import DefaultQuotaSetConfig
from cloudroast.compute.fixtures import ComputeAdminFixture


class QuotasAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(QuotasAdminTest, cls).setUpClass()
        cls.tenant_id = UserConfig().tenant_id
        cls.default_quota_set = DefaultQuotaSetConfig()

    @tags(type='smoke', net='no')
    def test_get_default_quota_set(self):
        quota = self.admin_quotas_client.\
            get_default_quota(self.tenant_id).entity
        self.assertEqual(quota.ram, self.default_quota_set.ram,
                         "Ram in quota set is not equal to the default value.")
        self.assertEqual(quota.cores, self.default_quota_set.cores,
                         "Cores in quota set is not equal to"
                         " the default value.")

    @tags(type='smoke', net='no')
    def test_update_quota(self):
        self.admin_quotas_client.\
            update_quota(self.tenant_id, instances=20)
        quota = self.admin_quotas_client.\
            get_quota(self.tenant_id).entity
        self.assertEqual(quota.instances, 20)

    @tags(type='smoke', net='no')
    def test_delete_quota(self):
        self.admin_quotas_client.\
            update_quota(self.tenant_id, instances=20)
        quota = self.admin_quotas_client.\
            get_quota(self.tenant_id).entity
        self.assertEqual(quota.instances, 20)

        self.admin_quotas_client.delete_quota(self.tenant_id)
        quota = self.admin_quotas_client.\
            get_quota(self.tenant_id).entity
        self.assertEqual(quota.instances, self.default_quota_set.instances,
                         "Instances in quota set is not equal to"
                         " the default value.")
