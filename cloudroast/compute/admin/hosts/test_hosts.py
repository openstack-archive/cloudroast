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
from cloudcafe.compute.common.types import HostServiceTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeAdminFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class HostsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(HostsAdminTest, cls).setUpClass()
        cls.hosts = cls.admin_hosts_client.list_hosts().entity

    @classmethod
    def tearDownClass(cls):
        super(HostsAdminTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_list_hosts(self):
        self.assertTrue(len(self.hosts) > 0, "The hosts list is empty.")
        for host in self.hosts:
            if host.service == HostServiceTypes.COMPUTE:
                return
        self.fail("The expected host: %s"
                  " is not found in hosts list." % HostServiceTypes.COMPUTE)

    @tags(type='smoke', net='no')
    def test_get_host(self):
        host_name = self.hosts[0].host_name
        host = self.admin_hosts_client.get_host(host_name).entity
        self.assertTrue(len(host.resources) > 0,
                        "The resources list is empty.")
        for resource in host.resources:
            self.assertEqual(resource.host, host_name,
                             "Resource is not mapped to host %s." % host_name)
