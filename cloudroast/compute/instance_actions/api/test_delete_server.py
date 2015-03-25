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
from cloudcafe.compute.common.exceptions import ItemNotFound

from cloudroast.compute.fixtures import ServerFromImageFixture


class DeleteServersTest(object):

    @tags(type='smoke', net='no')
    def test_delete_server_response(self):
        """
        The status code for a delete server request should be 204.

        Validate that the response to the delete server request in the test set
        up has a status code of 204.

        The following assertions occur:
            - The delete server response status code is equal to 204
        """
        self.assertEqual(204, self.resp.status_code)

    @tags(type='smoke', net='no')
    def test_deleted_server_not_listed(self):
        """
        A deleted server should not be included in the list of servers.

        As the test user, get a list of servers. Validate that the server
        deleted during test set up is not found in that list. As the test user,
        get a detailed list of servers. Validate that the server deleted during
        test set up is not found in that detailed list.

        The following assertions will occur:
            - The server deleted during test set up should not be in a list of
              servers
            - The server deleted during test set up should not be in a detailed
              list of servers
        """
        servers = self.servers_client.list_servers().entity
        self.assertNotIn(self.server, servers)

        servers = self.servers_client.list_servers_with_detail().entity
        self.assertNotIn(self.server, servers)

    @tags(type='positive', net='no')
    def test_deleted_server_listed_with_changes_since(self):
        """
        A server list using the changes since value should show a deleted server

        A deleted server should be included in the list of servers if the
        changes-since parameter is a time before the server was deleted. As a
        test user get a list of servers using the server created value of the
        server deleted during test set up. Validate that the deleted server is
        in this list. As a test user get a detailed list of servers using the
        server created value of the server deleted during test set up. Validate
        that the deleted server is in this detailed list.

        The following assertions will occur:
            - The id of the server deleted during test set up will be in a list
              of servers gotten using the 'changes_since' parameter
            - The id of the server deleted during test set up will be in a
              detailed list of servers gotten using the 'changes_since' parameter
        """

        servers = self.servers_client.list_servers(
            changes_since=self.server.created).entity
        self.assertTrue(
            any([s for s in servers if s.id == self.server.id]))

        servers = self.servers_client.list_servers_with_detail(
            changes_since=self.server.created).entity
        self.assertTrue(
            any([s for s in servers if s.id == self.server.id]))

    @tags(type='negative', net='no')
    def test_get_deleted_server_fails(self):
        """
        A get server request for a deleted server should fail.

        Attempt to get the details of the server deleted during test set up.
        The request should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to get the details of the server deleted during test
              set up will result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(self.server.id)

    @tags(type='negative', net='no')
    def test_update_deleted_server_fails(self):
        """
        An update server request for a deleted server should fail.

        Attempt to change the name of the server deleted during test set up to
        'newname' using the update_server method. The request should raise an
        'ItemNotFound error.'

        The following assertions will occur:
            - A request to update the name of a server deleted during test set
              up will result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.update_server(self.server.id, name='newname')

    @tags(type='negative', net='no')
    def test_delete_deleted_server_fails(self):
        """
        A delete request for a deleted server should fail.

        Attempt to delete the server deleted during test set up. The request
        should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to delete the server deleted during test set up
              will result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(self.server.id)

    @tags(type='negative', net='no')
    def test_change_password_for_deleted_server_fails(self):
        """
        A change password request for a deleted server should fail.

        Attempt to change the password of the server deleted during test set up.
        The request should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to change the password of the server deleted during test
              set up will result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.change_password(self.server.id, 'newP@ssw0rd')

    @tags(type='negative', net='no')
    def test_reboot_deleted_server_fails(self):
        """
        A hard reboot request for a deleted server should fail.

        Attempt to hard reboot the server deleted during test set up. The request
        should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to hard reboot the server deleted during test set up
              will result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.reboot(self.server.id, 'HARD')

    @tags(type='negative', net='no')
    def test_rebuild_deleted_server_fails(self):
        """
        A rebuild request for a deleted server should fail.

        Attempt to rebuild the server deleted during test set up. The request
        should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to rebuild the server deleted during test set up will
              result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.rebuild(self.server.id, self.image_ref_alt)

    @tags(type='negative', net='no')
    def test_resize_deleted_server_fails(self):
        """
        A resize request for a deleted server should fail.

        Attempt to resize the server deleted during test set up. The request
        should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to resize the server deleted during test set up will
              result in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.resize(self.server.id, self.flavor_ref_alt)

    @tags(type='negative', net='no')
    def test_create_image_for_deleted_server_fails(self):
        """
        A create image request for a deleted server should fail.

        Attempt to create a image snapshot using the id of the server deleted
        during test set up. The request should raise an 'ItemNotFound error.'

        The following assertions will occur:
            - A request to create an image from a deleted server will result
              in an 'ItemNotFound' error
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(self.server.id, 'backup')


class ServerFromImageDeleteServerTests(ServerFromImageFixture,
                                       DeleteServersTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that set up the neccesary resources for testing

        The following resources are created during this set up:
            - A server with values from the test configuration

        The following actions are performed during this set up:
            - The server created during set up is deleted
        """
        super(ServerFromImageDeleteServerTests, cls).setUpClass()
        cls.create_server()
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)
