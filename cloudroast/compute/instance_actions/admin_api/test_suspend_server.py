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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudcafe.compute.common.types import NovaServerRebootTypes
from cloudcafe.compute.common.exceptions import Forbidden
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudcafe.compute.common.clients.ping import PingClient

from cloudroast.compute.fixtures import ServerFromImageFixture


class SuspendServerTests(object):

    @tags(type='smoke', net='yes')
    def test_suspend_resume_server(self):
        """
        Verify that a server can be suspended and then resumed.

        Will suspend the server and waits for the server state to be
        suspended followed by pinging the ip until it's unreachable.  Resumes
        the server and waits for the server state to be active followed
        by pinging the server until it's reachable. Then retrieve the instance.

        The following assertions occur:
            - 202 status code response from the stop server call.
            - 202 status code response from the start server call.
            - Get remote instance client returns true (successful connection).
        """

        self.ping_ip = self.server.addresses.get_by_name(
            self.servers_config.network_for_ssh).ipv4

        response = self.admin_servers_client.suspend_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.SUSPENDED)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        response = self.admin_servers_client.resume_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)

        PingClient.ping_until_reachable(
            self.ping_ip, timeout=600, interval_time=5)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key),
            "Unable to connect to active server {0} after suspending "
            "and resuming".format(self.server.id))


class NegativeSuspendServerTests(object):

    @tags(type='smoke', net='yes')
    def test_reboot_hard_suspended_server(self):
        """
        Verify that a server reboot after suspend does not restore it.

        Will suspend the server and waits for the server state to be
        suspended followed by pinging the ip until it's unreachable.  Tries to
        reboot the server and expects a "Forbidden" exception to be raised.
        Then will ping until it's unreachable again.

        The following assertions occur:
            - 202 status code response from the stop server call.
            - 202 status code response from the start server call.
            - Get remote instance client returns true (successful connection).
        """

        self.ping_ip = self.server.addresses.get_by_name(
            self.servers_config.network_for_ssh).ipv4

        response = self.admin_servers_client.suspend_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.SUSPENDED)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        with self.assertRaises(Forbidden):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.HARD)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)


class ServerFromImageSuspendTests(ServerFromImageFixture,
                                  SuspendServerTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Create a server in active state.
        """
        super(ServerFromImageSuspendTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            key_name=cls.key.name).entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)


@unittest.skip("Failing due to RM11052.")
class ServerFromImageNegativeSuspendTests(ServerFromImageFixture,
                                          NegativeSuspendServerTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Create a server in active state.
        """
        super(ServerFromImageNegativeSuspendTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
