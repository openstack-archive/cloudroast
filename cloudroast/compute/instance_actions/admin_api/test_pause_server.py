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
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates

from cloudroast.compute.fixtures import ComputeAdminFixture


class PauseServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(PauseServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_pause_unpause_server(self):
        """Verify that a server can be paused and then unpaused successfully"""

        response = self.admin_servers_client.pause_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        ip = self.server_behaviors.get_public_ip_address(self.server.id)
        self.server_behaviors.ping_until_unreachable(ip)

        # Should already be paused, but need to check the status
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

        response = self.admin_servers_client.unpause_server(self.server.id)
        self.assertEqual(response.status_code, 202)
        
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key),
            "Unable to connect to active server after unpausing")
