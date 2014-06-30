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
from cloudroast.compute.fixtures import ComputeFixture


class ServerMetadataTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerMetadataTest, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def setUp(self):
        super(ServerMetadataTest, self).setUp()
        self.meta = {'meta_key_1': 'meta_value_1',
                     'meta_key_2': 'meta_value_2'}
        self.servers_client.set_server_metadata(self.server.id, self.meta)

    @tags(type='positive', net='no')
    def test_list_server_metadata(self):
        """All metadata key/value pairs for a server should be returned"""
        metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('meta_key_1'), 'meta_value_1')
        self.assertEqual(metadata.get('meta_key_2'), 'meta_value_2')

    @tags(type='positive', net='no')
    def test_set_server_metadata(self):
        """The server's metadata should be replaced with the provided values"""
        meta = {'meta1': 'data1'}
        server_response = self.server_behaviors.create_active_server(
            metadata=meta)
        server = server_response.entity
        self.resources.add(server.id, self.servers_client.delete_server)

        new_meta = {'meta2': 'data2', 'meta3': 'data3'}
        metadata_response = self.servers_client.set_server_metadata(
            server.id, new_meta)
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('meta2'), 'data2')
        self.assertEqual(metadata.get('meta3'), 'data3')
        self.assertNotIn(
            'meta1', metadata,
            msg='The key should have been removed after setting new metadata')

        actual_metadata_response = self.servers_client.list_server_metadata(
            server.id)
        actual_metadata = actual_metadata_response.entity
        self.assertEqual(actual_metadata.get('meta2'), 'data2')
        self.assertEqual(actual_metadata.get('meta3'), 'data3')
        self.assertNotIn('meta1', actual_metadata)

    @tags(type='positive', net='no')
    def test_update_server_metadata(self):
        """The server's metadata should be updated to the provided values"""
        meta = {'key1': 'alt1', 'key2': 'alt2', 'meta_key_1': 'alt3'}
        metadata_response = self.servers_client.update_server_metadata(
            self.server.id, meta)
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('key1'), 'alt1')
        self.assertEqual(metadata.get('key2'), 'alt2')
        self.assertEqual(metadata.get('meta_key_1'), 'alt3')
        self.assertEqual(metadata.get('meta_key_2'), 'meta_value_2')

        #Verify the values have been updated to the proper values
        actual_metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        actual_metadata = actual_metadata_response.entity
        self.assertEqual(actual_metadata.get('key1'), 'alt1')
        self.assertEqual(actual_metadata.get('key2'), 'alt2')
        self.assertEqual(actual_metadata.get('meta_key_1'), 'alt3')
        self.assertEqual(actual_metadata.get('meta_key_2'), 'meta_value_2')

    @tags(type='positive', net='no')
    def test_get_server_metadata_item(self):
        """The value for a specific metadata key should be returned"""
        metadata_response = self.servers_client.get_server_metadata_item(
            self.server.id, 'meta_key_1')
        metadata = metadata_response.entity
        self.assertEqual(metadata.get('meta_key_1'), 'meta_value_1')

    @tags(type='positive', net='no')
    def test_set_server_metadata_item(self):
        """The value provided for the given meta item should be updated"""
        metadata_response = self.servers_client.set_server_metadata_item(
            self.server.id, 'meta_key_2', 'nova')
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('meta_key_2'), 'nova')

        actual_metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        actual_metadata = actual_metadata_response.entity
        self.assertEqual(actual_metadata.get('meta_key_2'), 'nova')
        self.assertEqual(actual_metadata.get('meta_key_1'), 'meta_value_1')

    @tags(type='positive', net='no')
    def test_add_new_server_metadata_item(self):
        """ The metadata item should be added to the server"""
        metadata_response = self.servers_client.set_server_metadata_item(
            self.server.id, 'meta_key_3', 'meta_value_3')
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('meta_key_3'), 'meta_value_3')

        actual_metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        actual_metadata = actual_metadata_response.entity
        self.assertEqual(actual_metadata.get('meta_key_3'), 'meta_value_3')
        self.assertEqual(actual_metadata.get('meta_key_2'), 'meta_value_2')
        self.assertEqual(actual_metadata.get('meta_key_1'), 'meta_value_1')

    @tags(type='positive', net='no')
    def test_delete_server_metadata_item(self):
        """The metadata value/key pair should be deleted from the server"""

        response = self.servers_client.delete_server_metadata_item(
            self.server.id, 'meta_key_1')
        self.assertEqual(204, response.status_code)
        metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        metadata = metadata_response.entity
        self.assertNotIn('meta_key_1', metadata)
