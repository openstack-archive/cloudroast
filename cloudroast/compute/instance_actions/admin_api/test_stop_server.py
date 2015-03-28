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
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudcafe.compute.common.clients.ping import PingClient

from cloudroast.compute.fixtures import ComputeAdminFixture


class StopServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Create a server in active state.
        """
        super(StopServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        cls.ping_ip = cls.server.addresses.get_by_name(
            cls.servers_config.network_for_ssh).ipv4
        cls.verify_server_reachable(cls.ping_ip)

    @tags(type='smoke', net='no')
    def test_stop_start_server(self):
        """
        Verify that a server can be stopped and then started.

        Will stop the server and waits for a the server state to be shutoff
        followed by pinging the ip until its unreachable.  Start the server
        back up and wait for the server state to be active followed by
        pinging the server until its reachable.  Then retrieve the instance.

        The following assertions occur:
            - 202 status code response from the stop server call.
            - 202 status code response from the start server call.
            - Get remote instance client returns true (successful connection).
        """

        response = self.admin_servers_client.stop_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.SHUTOFF)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        response = self.admin_servers_client.start_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        PingClient.ping_until_reachable(
            self.ping_ip, timeout=60, interval_time=5)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config),
            "Unable to connect to active server {0} after stopping "
            "and starting".format(self.server.id))
