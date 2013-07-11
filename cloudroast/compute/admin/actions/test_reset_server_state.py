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
from cloudroast.compute.fixtures import ComputeAdminFixture

class ResetServerStateTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(ResetServerStateTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(ResetServerStateTests, cls).tearDownClass()

    def test_set_server_state(self):

        # Set the active server into error status
        self.admin_servers_client.reset_state(self.server.id, 'error')
        current_server = self.admin_servers_client.get_server(self.server.id).entity
        self.assertEqual(current_server.status.lower(), 'error')

        # Reset the server's error status back to active
        self.admin_servers_client.reset_state(self.server.id, 'active')
        current_server = self.admin_servers_client.get_server(self.server.id).entity
        self.assertEqual(current_server.status.lower(), 'active')
