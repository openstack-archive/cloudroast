"""
Copyright 2013 Rackspace

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
from cloudroast.compute.fixtures import ComputeFixture


class ServersTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServersTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resp = cls.servers_client.delete_server(cls.server.id)
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)

    @tags(type='smoke', net='no')
    def test_delete_server_response(self):
        """The response code for a delete server request should be 204."""
        self.assertEqual(204, self.resp.status_code)

    @tags(type='smoke', net='no')
    def test_deleted_server_not_listed(self):
        """A deleted server should not be included in the list of servers."""
        servers = self.servers_client.list_servers().entity
        self.assertNotIn(self.server, servers)

        servers = self.servers_client.list_servers_with_detail().entity
        self.assertNotIn(self.server, servers)

    @tags(type='positive', net='no')
    def test_deleted_server_listed_with_changes_since(self):
        """
        A deleted server should be included in the list of servers if
        the changes-since parameter is a time before the server was deleted
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
        """A get server request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(self.server.id)

    @tags(type='negative', net='no')
    def test_update_deleted_server_fails(self):
        """An update server request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.update_server(self.server.id, name='newname')

    @tags(type='negative', net='no')
    def test_delete_deleted_server_fails(self):
        """A delete server request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(self.server.id)

    @tags(type='negative', net='no')
    def test_change_password_for_deleted_server_fails(self):
        """A change password request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.change_password(self.server.id, 'newP@ssw0rd')

    @tags(type='negative', net='no')
    def test_reboot_deleted_server_fails(self):
        """A reboot request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.reboot(self.server.id, 'HARD')

    @tags(type='negative', net='no')
    def test_rebuild_deleted_server_fails(self):
        """A rebuild request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.rebuild(self.server.id, self.image_ref_alt)

    @tags(type='negative', net='no')
    def test_resize_deleted_server_fails(self):
        """A resize request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.resize(self.server.id, self.flavor_ref_alt)

    @tags(type='negative', net='no')
    def test_create_image_for_deleted_server_fails(self):
        """A create image request for a deleted server should fail."""
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(self.server.id, 'backup')
