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
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ComputeFixture


class ServersNegativeTest(ComputeFixture):

    @tags(type='negative', net='no')
    def test_server_name_blank(self):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('', self.image_ref,
                                              self.flavor_ref)

    @tags(type='negative', net='no')
    def test_personality_file_contents_not_encoded(self):
        """Server creation should fail if the injected file is not encoded"""
        file_contents = 'This is a test file.'
        personality = [{'path': '/etc/testfile.txt',
                        'contents': file_contents}]
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'blankfile', self.image_ref, self.flavor_ref,
                personality=personality)

    @tags(type='negative', net='no')
    def test_invalid_ip_v4_access_address(self):
        """A server should not be created with an invalid ipv4 address"""
        accessIPv4 = '1.1.1.1.1.1'
        name = rand_name("testserver")
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                name, self.image_ref, self.flavor_ref, accessIPv4=accessIPv4)

    @tags(type='negative', net='no')
    def test_invalid_ip_v6_access_address(self):
        """A server should not be created with invalid ipv6 address"""
        accessIPv6 = '2.2.2.2'
        name = rand_name("testserver")
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                name, self.image_ref, self.flavor_ref, accessIPv6=accessIPv6)

    @tags(type='negative', net='no')
    def test_create_server_with_unknown_flavor(self):
        """Server creation with a flavor which does not exist should fail"""
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', self.image_ref, 999)

    @tags(type='negative', net='no')
    def test_create_server_with_unknown_image(self):
        """Server creation with an image which does not exist should fail"""
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', 999, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_get_nonexistent_server_fails(self):
        """A GET request for a server that does not exist should fail"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(999)

    @tags(type='negative', net='no')
    def test_delete_nonexistent_server_fails(self):
        """A delete request for a server that does not exist should fail"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(999)

    @tags(type='negative', net='no')
    def test_list_addresses_for_nonexistant_server_fails(self):
        """
        A list address request for a server that does not exist should fail
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_addresses(999)

    @tags(type='negative', net='no')
    def test_list_addresses_for_invalid_network_id_fails(self):
        """
        List addresses by network with a network id that not exist should fail
        """
        server_response = self.server_behaviors.create_active_server()
        server = server_response.entity
        self.resources.add(server.id, self.servers_client.delete_server)
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_addresses_by_network(server.id, 999)

    @tags(type='negative', net='no')
    def test_list_addresses_by_network_for_nonexistent_server_fails(self):
        """
        List addresses by network for a server that does not exist should fail
        """
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_addresses_by_network(999, 'public')

    @tags(type='negative', net='no')
    def test_cannot_get_deleted_server(self):
        """A 404 response is expected for server which is deleted"""
        server = self.server_behaviors.create_active_server()
        delete_resp = self.servers_client.delete_server(server.entity.id)
        self.assertEqual(204, delete_resp.status_code)
        self.server_behaviors.wait_for_server_to_be_deleted(server.entity.id)
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(server.entity.id)

    @tags(type='negative', net='no')
    def test_create_server_with_invalid_name(self):
        """Server creation with a blank/invalid name should not be allowed"""
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                '', self.image_ref, self.flavor_ref)
