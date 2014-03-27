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
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


#class BootInvalidValues(ComputeFixture):
class BVDeleteOnTerminate(BlockstorageIntegrationFixture):
    @classmethod
    def setUpClass(cls):
        super(BVDeleteOnTerminate, cls).setUpClass()

    @tags(type='smoke', net='yes')
    def test_for_do_not_delete_on_terminate(self):
        boot_from_block = {'volume_id': None,
                           'del_on_termination': 0,
                           'source_type': None,
                           'dest_type': None,
                           'device_name': None,
                           'type': None}
        self.response = self.server_behaviors.create_active_server(
            boot_from_block=boot_from_block)
        self.server = self.response.entity
        self.resources.add(self.server.id, self.servers_client.delete_server)
        self.resp = self.servers_client.delete_server(self.server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)
        self.volume_status = self.blockstorage_behavior.get_volume_status(
            self.server.volume_id)
        self.assertEqual(self.volume_status, "available", "Volume deleted")

    @tags(type='smoke', net='yes')
    def test_for_delete_on_terminate(self):
        boot_from_block = {'volume_id': None,
                           'del_on_termination': 1,
                           'source_type': None,
                           'dest_type': None,
                           'device_name': None,
                           'type': None}
        self.response = self.server_behaviors.create_active_server(
            boot_from_block=boot_from_block)
        self.server = self.response.entity
        self.resources.add(self.server.id, self.servers_client.delete_server)
        self.resp = self.servers_client.delete_server(self.server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)
        try:
            self.volume_status = self.blockstorage_behavior.get_volume_status(
                self.server.volume_id)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[1:4], "404", self.err_msg)
        else:
            self.fail("Test case should have becasue volume was deleted")
