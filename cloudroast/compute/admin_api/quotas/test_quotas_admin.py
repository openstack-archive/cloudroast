"""
Copyright 2015 Rackspace

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
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - An instance is created using the tenant identified in
              the test config
        """
        super(QuotasAdminTest, cls).setUpClass()
        cls.tenant_id = UserConfig().tenant_id
        cls.default_quota_set = DefaultQuotaSetConfig()
        cls.server_response = cls.server_behaviors.create_active_server()
        cls.server_to_resize = cls.server_response.entity
        cls.resources.add(cls.server_to_resize.id,
                          cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_get_default_quota_set(self):
        """
        Test that an admin user can get the quota values for a tenant

        As an admin test user get the default quota values for the tenant
        identified during setup. Validate that this quota is not empty
        and that the RAM and Core values for the quote match the expected
        default values set during test configuration.

        The following assertions occur:
            - The default quota values for the tenant identified during setup
              are populated
            - The RAM quota value for the tenant matches the expected
              default values set during test configuration
            - The Cores quota value for the tenant matches the expected
              default values set during test configuration
        """
        quota = self.admin_quotas_client.get_default_quota(
            self.tenant_id).entity
        self.assertIsNotNone(quota, "Default quota is none.")
        self.assertEqual(quota.ram, self.default_quota_set.ram,
                         "Ram in quota set is not equal to the default value.")
        self.assertEqual(quota.cores, self.default_quota_set.cores,
                         "Cores in quota set is not equal to"
                         " the default value.")

    @tags(type='smoke', net='no')
    def test_update_quota(self):
        """
        Test that an admin user can change the quota values for a tenant

        As an admin test user change the instances quota value for the tenant
        identified during setup from the current value to 20 instances.
        Ensure that the API returns the correct updated instances quota value.

        The following assertions occur:
            - The admin user is able to change the instances quota value for
              the tenant identified in the setup
            - The API shows that the instances quota values has been updated to
              show an instance quota value of 20 instances
        """
        self.admin_quotas_client.update_quota(
            self.tenant_id, instances=20)
        quota = self.admin_quotas_client.get_quota(
            self.tenant_id).entity
        self.assertIsNotNone(quota)
        self.assertEqual(quota.instances, 20)

    @tags(type='smoke', net='no')
    def test_delete_quota(self):
        """
        Test that an admin user can delete the quota values for a tenant

        As an admin test user change the instances quota value for the tenant
        identified during setup from the default value to 20 instances.
        Confirm that the instances quota value has updated to 20 instances.
        Delete the quota values, the instances quota value should now
        return to the default value. Validate that the quota is not None and
        that the instances quota value matches the default instances quota
        value set during test configuration.

        The following assertions occur:
            - The quota values for the tenant identified during setup
              are populated
            - The quota value for instances is equal to 20
            - After the admin deletes the quota values for the tenant identified
              during setup the quoate values are populated
            - The quota value for instances is equal to the configured
              default value
        """
        self.admin_quotas_client.update_quota(
            self.tenant_id, instances=20)
        quota = self.admin_quotas_client.get_quota(
            self.tenant_id).entity
        self.assertIsNotNone(quota)
        self.assertEqual(quota.instances, 20)

        self.admin_quotas_client.delete_quota(self.tenant_id)
        quota = self.admin_quotas_client.get_quota(
            self.tenant_id).entity
        self.assertIsNotNone(quota)
        self.assertEqual(quota.instances, self.default_quota_set.instances,
                         "Instances in quota set is not equal to"
                         " the default value.")

    @tags(type='negative', net='no')
    def test_admin_quota_is_not_checked_on_resizing_user_server_by_admin(self):
        """
        Test that changing the quota values does not affect instance resizes

        As an admin test user change the RAM quota value for the tenant
        identified during setup to 0. Resize the instance created during setup
        and confirm that the resize was successful. The updated quota value
        should not affect the resize.

        The following assertions occur:
            - The admin user is able to resize the instance created during
              setup to the alternative flavor set during test configuration.
            - The resized server's flavor id matches the alt flavor id set
              during test configuration
        """
        self._update_admin_ram_quota_to(0)
        self.admin_server_behaviors.resize_and_confirm(
            self.server_to_resize.id,
            self.flavor_ref_alt)
        resized_server = self.admin_servers_client.get_server(
            self.server_to_resize.id).entity
        self.assertIsNotNone(resized_server)
        self.assertEqual(self.flavor_ref_alt, resized_server.flavor.id)

    def _update_admin_ram_quota_to(self, ram_value):
        self.admin_quotas_client.update_quota(self.user_config.tenant_id,
                                              ram=ram_value)

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the cleanup of any generated resources

        The following actions are performed during this tear down:
            - The RAM and Instances quota for the tenant identified during
              the setup are set to the default values set during test
              configuration
        """
        cls.admin_quotas_client.update_quota(
            cls.user_config.tenant_id,
            ram=cls.default_quota_set.ram,
            instances=cls.default_quota_set.instances)
