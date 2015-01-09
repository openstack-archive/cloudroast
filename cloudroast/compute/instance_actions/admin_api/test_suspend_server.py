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

import unittest

from cafe.drivers.unittest.decorators import tags
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
        """Verify that a server can be suspended and then resumed"""

        self.ping_ip = self.get_accessible_ip_address(self.server)

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
            self.ping_ip, timeout=60, interval_time=5)

        self.assertTrue(self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config),
            "Unable to connect to active server {0} after suspending "
            "and resuming".format(self.server.id))

@unittest.skip("Failing due to RM11052")
class NegativeSuspendServerTests(object):

    @tags(type='smoke', net='yes')
    def test_reboot_hard_suspended_server(self):
        """Verify that a server reboot after suspend does not restore it"""

        self.ping_ip = self.get_accessible_ip_address(self.server)

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
        super(ServerFromImageSuspendTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.server = cls.server_behaviors.create_active_server().entity


class ServerFromImageNegativeSuspendTests(ServerFromImageFixture,
                                          NegativeSuspendServerTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageNegativeSuspendTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
