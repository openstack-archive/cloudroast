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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound

from cloudroast.compute.fixtures import ComputeFixture


class ServerMetadataTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerMetadataTest, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_delete_nonexistent_server_metadata_item(self):
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server_metadata_item(
                self.server.id, 'meta_key_5')

    @tags(type='negative', net='no')
    def test_get_nonexistent_server_metadata_item(self):
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server_metadata_item(
                self.server.id, 'meta_key_5')

    @tags(type='negative', net='no')
    def test_set_blank_metadata_dict(self):
        blank_meta = {'': ''}
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                rand_name('testserver'), self.image_ref,
                self.flavor_ref, metadata=blank_meta)

    @tags(type='negative', net='no')
    def test_server_metadata_item_nonexistent_server(self):
        """Negative test: GET on nonexistent server should not succeed"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server_metadata_item(999, 'test2')

    @tags(type='negative', net='no')
    def test_list_server_metadata_nonexistent_server(self):
        """List metadata on a non existent server should not succeed"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.list_server_metadata(999)

    @tags(type='negative', net='no')
    def test_set_server_metadata_nonexistent_server(self):
        """Set metadata on a non existent server should not succeed"""
        meta = {'meta1': 'data1'}

        with self.assertRaises(ItemNotFound):
            self.servers_client.set_server_metadata(999, meta)

    @tags(type='negative', net='no')
    def test_update_server_metadata_nonexistent_server(self):
        """An update should not happen for a non existent image"""
        meta = {'key1': 'value1', 'key2': 'value2'}
        with self.assertRaises(ItemNotFound):
            self.servers_client.update_server_metadata(999, meta)

    @tags(type='negative', net='no')
    def test_delete_server_metadata_item_nonexistent_server(self):
        """Deleting a metadata item from a non existent server should fail"""
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server_metadata_item(999, 'delkey')
