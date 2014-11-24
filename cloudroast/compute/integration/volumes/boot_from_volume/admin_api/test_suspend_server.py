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

from cloudcafe.compute.common.types import NovaServerRebootTypes
from cloudcafe.compute.common.exceptions import ActionInProgress
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudcafe.compute.common.clients.ping import PingClient


class SuspendServerTests(object):

    @tags(type='smoke', net='yes')
    def test_reboot_hard_suspended_server(self):
        """Verify that a server can be suspended and then resumed"""

        self.ping_ip = self.parse_ip_address_for_communication(self.server)

        response = self.admin_servers_client.suspend_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

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


class NegativeSuspendServerTests(object):

    @tags(type='smoke', net='yes')
    def test_suspend_reboot_hard_server(self):
        """Verify that a server reboot after suspend does not restore it"""

        self.ping_ip = self.parse_ip_address_for_communication(self.server)

        response = self.admin_servers_client.suspend_server(self.server.id)
        self.assertEqual(response.status_code, 202)

        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.PAUSED)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)

        with self.assertRaises(ActionInProgress):
            self.servers_client.reboot(self.server.id,
                                       NovaServerRebootTypes.HARD)

        PingClient.ping_until_unreachable(
            self.ping_ip, timeout=60, interval_time=5)
