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
import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudcafe.compute.common.clients.ping import PingClient
from cloudcafe.compute.config import ComputeConfig

from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class PauseServerTests(object):

    @tags(type='smoke', net='yes')
    def test_pause_unpause_server(self):
        """
        Verify that a server can be paused and then unpaused successfully.

        First step is getting the IP address for communication based on the
        configuration, after that we pause the instance making sure that
        there is no connectivity. After that we check what happens when we
        unpause the instance and making sure the connectivity is restored.

         The following assertions occur:
            - A 202 response is returned from the pause call.
            - A 202 response is returned from the unpause call.
            - The remote instance client is able to connect to
              the instance after it is unpaused.
        """

        self.ping_ip = self.get_accessible_ip_address(self.server)

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


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC],
    'Pause server not supported in current configuration.')
class ServerFromImagePauseTests(ServerFromImageFixture,
                                PauseServerTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create a server from server behaviors.
            - Initializes compute admin.
            - Initializes server behaviors.
        """
        super(ServerFromImagePauseTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
