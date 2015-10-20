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
from cloudcafe.compute.common.clients.ping import PingClient
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates

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
        cls.connection_timeout = cls.servers_config.connection_timeout
        cls.retry_interval = cls.servers_config.connection_retry_interval
        key_resp = cls.keypairs_client.create_keypair(rand_name("key"))
        assert key_resp.status_code is 200, ("Create keypair failed with response "
                                             "code {0}".format(key_resp.status_code))
        cls.key = key_resp.entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            key_name=cls.key.name).entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        cls.ping_ip = cls.server.addresses.get_by_name(
            cls.servers_config.network_for_ssh).ipv4
        PingClient.ping_until_reachable(
            cls.ping_ip, timeout=cls.connection_timeout,
            interval_time=cls.retry_interval)

    @tags(type='smoke', net='no')
    def test_stop_start_server(self):
        """
        Verify that a server can be stopped and then started.

        Will stop the server and waits for the server state to be shutoff
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
            self.ping_ip, timeout=self.connection_timeout,
            interval_time=self.retry_interval)

        response = self.admin_servers_client.start_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        PingClient.ping_until_reachable(
            self.ping_ip, timeout=self.connection_timeout,
            interval_time=self.retry_interval)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key),
            "Unable to connect to active server {0} after stopping "
            "and starting".format(self.server.id))
