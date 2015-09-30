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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates

from cloudroast.compute.fixtures import ComputeAdminFixture


class ResetServerStateTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Create a server in active state.
        """
        super(ResetServerStateTests, cls).setUpClass()
        key_resp = cls.keypairs_client.create_keypair(rand_name("key"))
        assert key_resp.status_code is 200
        cls.key = key_resp.entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            key_name=cls.key.name).entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_set_server_state(self):
        """
        Verify that the state of a server can be set manually.

        Will change the state of the server to an error state and after
        confirming the change of the state to error, it will execute a state
        change to active.  After which, will be verified the server is in an
        active state.

         The following assertions occur:
            - The server state is error, after first call.
            - The server state is active, after second call.
        """

        # Set the active server into error status.
        # reset_state requires the state to be in lowercase
        self.admin_servers_client.reset_state(
            self.server.id, ServerStates.ERROR.lower())
        current_server = self.admin_servers_client.get_server(
            self.server.id).entity
        self.assertEqual(current_server.status,
                         ServerStates.ERROR)

        # Reset the server's error status back to active
        # reset_state requires the state to be in lowercase
        self.admin_servers_client.reset_state(
            self.server.id, ServerStates.ACTIVE.lower())
        current_server = self.admin_servers_client.get_server(
            self.server.id).entity
        self.assertEqual(current_server.status,
                         ServerStates.ACTIVE)
