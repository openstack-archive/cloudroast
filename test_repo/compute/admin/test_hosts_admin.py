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
from test_repo.compute.fixtures import ComputeAdminFixture


class HostsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(HostsAdminTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(HostsAdminTest, cls).tearDownClass()

    def test_list_hosts(self):
        hosts = self.admin_hosts_client.list_hosts().entity
        self.assertTrue(len(hosts) > 0, "The hosts list is empty.")
        for host in hosts:
            if host.service == HostServiceTypes.COMPUTE:
                return
        self.fail("The expected host: %s"
                  " is not found in hosts list." % HostServiceTypes.COMPUTE)
