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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class UpdateServerTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Networking, default network from ComputeFixture.
            - 1 Server via create_active_server.
            - Server gets updated with AccessIPv4, AccessIPv6 and name.
            - Uses the get_server call to set member variable.
        """
        super(UpdateServerTest, cls).setUpClass()
        create_response = cls.server_behaviors.create_active_server()
        cls.original_server = create_response.entity
        cls.resources.add(cls.original_server.id,
                          cls.servers_client.delete_server)

        cls.accessIPv4 = '192.168.32.16'
        cls.accessIPv6 = '3ffe:1900:4545:3:200:f8ff:fe21:67cf'
        cls.new_name = rand_name("newname")
        cls.resp = cls.servers_client.update_server(
            cls.original_server.id, name=cls.new_name,
            accessIPv4=cls.accessIPv4, accessIPv6=cls.accessIPv6)
        cls.server_behaviors.wait_for_server_status(
            cls.original_server.id, NovaServerStatusTypes.ACTIVE)

        cls.server = cls.servers_client.get_server(
            cls.original_server.id).entity

    @tags(type='smoke', net='no')
    def test_update_server_response(self):
        """
        Will ensure that the server was updated, using the server response.

        This will validate the values defined during setup of the test.

        The following assertions occur:
            - Server name is equal to the new name.
            - AccessIPv4 address is equal to the new address (192.168.32.16).
            - AccessIPv6 address is equal to the new address
              (3ffe:1900:4545:3:200:f8ff:fe21:67cf).
        """
        updated_server = self.resp.entity
        self.assertEqual(updated_server.name, self.new_name,
                         msg="The name was not updated")
        self.assertEqual(self.accessIPv4, updated_server.accessIPv4,
                         msg="AccessIPv4 was not updated")
        self.assertEqual(self.accessIPv6, updated_server.accessIPv6,
                         msg="AccessIPv6 was not updated")

    @tags(type='smoke', net='no')
    def test_updated_server_details(self):
        """
        Will ensure that the server was updated, using the server response.

        This will validate the values set on the server after a get server
        details call is made.

        The following assertions occur:
            - Server name is equal to the new name.
            - AccessIPv4 address is equal to the new address (192.168.32.16).
            - AccessIPv6 address is equal to the new address
              (3ffe:1900:4545:3:200:f8ff:fe21:67cf).
            - Created date is equal to the original (didn't change).
            - Updated is not equal to the original (did change w/ update).
        """
        self.assertEqual(self.server.name, self.new_name,
                         msg="The name was not updated")
        self.assertEqual(self.accessIPv4, self.server.accessIPv4,
                         msg="AccessIPv4 was not updated")
        self.assertEqual(self.accessIPv6, self.server.accessIPv6,
                         msg="AccessIPv6 was not updated")
        self.assertEqual(self.server.created, self.original_server.created,
                         msg="The creation date was updated")
        self.assertNotEqual(
            self.server.updated, self.original_server.updated,
            msg='Updated time for server %s did not change '
                'after a modification to the server.' % self.server.id)
