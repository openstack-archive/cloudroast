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
from cloudcafe.compute.common.types import HostServiceTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeAdminFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class HostsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A list of hosts
        """
        super(HostsAdminTest, cls).setUpClass()
        cls.hosts = cls.admin_hosts_client.list_hosts().entity

    @tags(type='smoke', net='no')
    def test_list_hosts(self):
        """
        Test that an admin user can get a list of hosts

        Ensure that the host list created during setup is not empty.
        Validate that a Compute host is in the list.

        The following assertions occur:
            - The host list is populated
            - A compute host is found in the host list
        """
        self.assertTrue(len(self.hosts) > 0, "The hosts list is empty.")
        for host in self.hosts:
            if host.service == HostServiceTypes.COMPUTE:
                return
        self.fail("The expected host: %s"
                  " is not found in hosts list." % HostServiceTypes.COMPUTE)

    @tags(type='smoke', net='no')
    def test_get_host(self):
        """
        Test that an admin user can get details about a host

        Select the first host name from the list of hosts generated during
        setup. Get details of the host. For each resource in the host's
        resource list ensure that the resource is mapped to the correct
        (the selected) host.

        The following assertions occur:
            - The host details contain a list of resources
            - Every resource in the host's resource list correctly maps
              to the selected host
        """
        host_name = self.hosts[0].host_name
        host = self.admin_hosts_client.get_host(host_name).entity
        self.assertTrue(len(host.resources) > 0,
                        "The resources list is empty.")
        for resource in host.resources:
            self.assertEqual(resource.host, host_name,
                             "Resource is not mapped to host %s." % host_name)
