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
import unittest2 as unittest

from cloudcafe.compute.common.types import HostServiceTypes, ComputeHypervisors
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeAdminFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(hypervisor in [ComputeHypervisors.KVM,
                 ComputeHypervisors.QEMU],
                 "These hypervisors do not implement host"
                 " disabled/enabled status.")
class HostActionsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A list of hosts
            - The host name of a compute host
        """
        super(HostActionsAdminTest, cls).setUpClass()
        cls.hosts = cls.admin_hosts_client.list_hosts().entity
        cls.compute_host_name = next(
            host.host_name for host in cls.hosts
            if host.service == HostServiceTypes.COMPUTE)

    def test_disable_host(self):
        """
        Test that an admin user can disable and enable a host

        Disable the compute host identified during setup. Validate that
        host becomes disabled. Re-enable the compute host. Validate that
        the host becomes enabled.

        The following assertions occur:
            - The admin test user is able to set a host to disabled
            - The admin test user is able to set a host to enabled
        """
        host_response = self.admin_hosts_client.\
            update_host(self.compute_host_name, status="disable").entity
        self.assertEqual(host_response.status, "disabled")
        host_response = self.admin_hosts_client.\
            update_host(self.compute_host_name, status="enable").entity
        self.assertEqual(host_response.status, "enabled")
