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
from cloudroast.compute.fixtures import ComputeFixture


class ServerMetadataTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing server meta data

        The following resources are created/defined during the setup
            - Uses server behaviors to create active server
            - Adds server id to resources wit the function to delete_server
        """
        super(ServerMetadataTest, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def setUp(self):
        """
        This sets up by create a dictionary of metadata and sets it to the server

        The following calls the BaseTestFixture setUp and then using cloudcafe's server_client, sets the server that was
        created in the setUpClass with the metadata keys meta_key_1 and meta_key_2 with values meta_value_1 and
        meta_value_2 respectively.
        """
        super(ServerMetadataTest, self).setUp()
        self.meta = {'meta_key_1': 'meta_value_1',
                     'meta_key_2': 'meta_value_2'}
        self.servers_client.set_server_metadata(self.server.id, self.meta)

    @tags(type='positive', net='no')
    def test_list_server_metadata(self):
        """
        All metadata key/value pairs for a server should be returned that was defined in setUp

        This will call the list_server_metadata passing int he server id created in setup
        The following assertions occur
            - 200 status code from the http call
            - meta_key_1 key has meta_value_1 for value
            - meat_key_2 key has meta_value_2 for value
        """
        metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        metadata = metadata_response.entity
        self.assertEqual(200, metadata_response.status_code)
        self.assertEqual(metadata.get('meta_key_1'), 'meta_value_1')
        self.assertEqual(metadata.get('meta_key_2'), 'meta_value_2')

    @tags(type='positive', net='no')
    def test_set_server_metadata(self):
        """
        Create a server with metadata and then call set server metadata with new values, validating only new values

        Will create a new active server with a server_behaviors, passing in metadata.
        Then will call set_server_metadata with a completely new set, pull the response and making sure the new values
        are there and the old values are not. Lastly will call list_server_metadata and be sure the same holds true.
        The following assertions occur
            - 200 status on the set_server_metadata
            - meta2 key in set_server_metadata result has data2 value
            - meta3 key in set_server_metadata result has data3 value
            - meta1 isn't in the set_server_metadata result
            - meta2 key in list_server_metadata result has data2 value
            - meta3 key in list_server_metadata result has data3 value
            - meta1 isn't in the list_server_metadata result
        """
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
        """
        Update server metadata to ensure the the values are updated and existing are still on the server from setup

        Will use the existing server created in setup to add new and update meta_key_1 key to value alt3.
        Calling the update_server_metadata from cloudcafe's server client and then list_server_metadata to validate.
        The following assertions occur
            - 200 status on the update_server_metadata
            - key1 key in update_server_metadata result has alt1 value
            - key2 key in update_server_metadata result has alt2 value
            - meta_key_1 key in update_server_metadata result has alt3 value
            - meta_key_2 key in update_server_metadata result has meta_value_2 value
            - key1 key in list_server_metadata result has alt1 value
            - key2 key in list_server_metadata result has alt2 value
            - meta_key_1 key in list_server_metadata result has alt3 value
            - meta_key_2 key in list_server_metadata result has meta_value_2 value
        """
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
        """
        Calling get server metadata providing it meta_key_1 defined in setUp

        Calling get_server_metadata_item from cloudcafe's server client providing it meta_key_1 as the only parameter
        The following assertions occur
            - meta_key_1 key has meta_value_1 value
        """
        metadata_response = self.servers_client.get_server_metadata_item(
            self.server.id, 'meta_key_1')
        metadata = metadata_response.entity
        self.assertEqual(metadata.get('meta_key_1'), 'meta_value_1')

    @tags(type='positive', net='no')
    def test_set_server_metadata_item(self):
        """
        Set server metadata item call using meta_key_2 key setting nova as the value and verifies with list server meta

        Will call the set_server_metadata_item from cloudcafe's server client passing in the server's id created in
        setup with meta_key_2 as the meta data key and nova as the metadata value.
        The following assertions occur
            - 200 status on the set_server_metadata_item
            - meta_key_2 key in set_server_metadata_item result has nova value
            - meta_key_2 key in list_server_metadata result has nova value
            - meta_key_1 key in list_server_metadata result has meta_value_1 value
        """
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
        """
        Set server metadata item using meta_key_3 to set value meta_value_3 on server created during setup

        Will call the set_server_metadata_item from cloudcafe's server client passing in the server's id created in
        setup with meta_key_3 as the meta data key and meta_value_3 as the metadata value.
        The following assertions occur
            - 200 status on the set_server_metadata_item
            - meta_key_3 key in set_server_metadata_item result has meta_value_3 value
            - meta_key_3 key in list_server_metadata result has meta_value_3 value
            - meta_key_2 key in list_server_metadata result has meta_value_2 value
            - meta_key_1 key in list_server_metadata result has meta_value_1 value
        """
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
        """
        The metadata value/key pair with key meta_key_1 will be deleted from the server, list_server_metadata to verify

        Will call the delete_server_metadata_item from cloudcafe's server client passing in the server's id created in
        setup with meta_key_1 as the meta data key.
        The following assertions occur
            - 204 status on the delete_server_metadata_item
            - meta_key_1 key not in list_server_metadata result
        """

        response = self.servers_client.delete_server_metadata_item(
            self.server.id, 'meta_key_1')
        self.assertEqual(204, response.status_code)
        metadata_response = self.servers_client.list_server_metadata(
            self.server.id)
        metadata = metadata_response.entity
        self.assertNotIn('meta_key_1', metadata)
