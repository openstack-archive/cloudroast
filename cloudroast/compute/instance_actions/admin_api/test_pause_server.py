"""
Copyright 2014 Rackspace

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
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudcafe.compute.common.clients.ping import PingClient
from cloudcafe.compute.common.types import NovaServerRebootTypes
from cloudcafe.compute.common.exceptions import Forbidden

from cloudroast.compute.fixtures import ServerFromImageFixture


class PauseServerTests(object):

    @tags(type='smoke', net='yes')
    def test_pause_unpause_server(self):
        """
        Verify that a server can be paused and then unpaused successfully
        First step is getting the IP address for communication based on the
        configuration, after that we pause the instance making sure that
        there is no connectivity. After that we check what happens when we
        unpause the instance and making sure the connectivity is restored
        """

        self.ping_ip = self.get_ip_address_for_live_communication(self.server)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        response = self.admin_servers_client.pause_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        response = self.admin_servers_client.unpause_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        PingClient.ping_until_reachable(
            self.ping_ip, timeout=60, interval_time=5)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config),
            "Unable to connect to active server {0} after unpausing".format(
                self.server.id))


class NegativePauseServerTests(object):

    @tags(type='smoke', net='yes')
    def test_pause_reboot_server(self):
        """Verify that a server reboot during pause does not restore it"""

        self.ping_ip = self.get_ip_address_for_live_communication(self.server)

        response = self.admin_servers_client.pause_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        with self.assertRaises(Forbidden):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.HARD)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)


class ServerFromImagePauseTests(ServerFromImageFixture,
                                PauseServerTests,
                                NegativePauseServerTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImagePauseTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
