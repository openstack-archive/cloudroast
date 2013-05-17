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
from test_repo.compute.fixtures import ComputeAdminFixture


class HypervisorsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(HypervisorsAdminTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(HypervisorsAdminTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_list_hypervisors(self):
        hypervisors = self.admin_hypervisors_client.list_hypervisors().entity
        self.assertTrue(len(hypervisors) > 0, "The hypervisors list is empty.")

    @tags(type='smoke', net='no')
    def test_list_hypervisor_servers(self):
        server = self.admin_server_behaviors.create_active_server().entity
        self.resources.add(server.id, self.admin_servers_client.delete_server)
        hypervisors = self.admin_hypervisors_client.list_hypervisors().entity
        for hypervisor in hypervisors:
            hypervisor_with_servers = self.admin_hypervisors_client.\
                list_hypervisor_servers(hypervisor.hypervisor_hostname).entity
            server_id_list = [hypervisor_server.id for
                              hypervisor_server in
                              hypervisor_with_servers.servers]
            if server.id in server_id_list:
                return
        self.assertFail("Server not found in the Server list")
