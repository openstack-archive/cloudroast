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
from cloudcafe.blockstorage.config import BlockStorageConfig
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


#class BootInvalidValues(ComputeFixture):
class BVDeleteOnTerminate(BlockstorageIntegrationFixture):
    @classmethod
    def setUpClass(cls):
        super(BVDeleteOnTerminate, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)

    @tags(type='smoke', net='yes')
    def test_for_do_not_delete_on_terminate(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        # PDN = Positive Do Not Delete on Terminate
        self.trigger_value = "PDN"
        self.response, self.volume_id = self.server_behaviors.boot_volume(
            self.key, self.trigger_value)
        self.server = self.response.entity
        self.resources.add(self.server.id, self.servers_client.delete_server)
        self.resp = self.servers_client.delete_server(self.server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)
        self.volume_status = self.blockstorage_behavior.get_volume_status(
            self.volume_id.id_)
        self.assertEqual(self.volume_status, "available", "Volume deleted")

    @tags(type='smoke', net='yes')
    def test_for_delete_on_terminate(self):
        self.key = self.keypairs_client.create_keypair(rand_name("key")).entity
        self.resources.add(self.key.name, self.keypairs_client.delete_keypair)
        # PDT = Positive Delete on Terminate
        self.trigger_value = "PDT"
        self.response, self.volume_id = self.server_behaviors.boot_volume(
            self.key, self.trigger_value)
        self.server = self.response.entity
        self.resources.add(self.server.id, self.servers_client.delete_server)
        self.resp = self.servers_client.delete_server(self.server.id)
        self.server_behaviors.wait_for_server_to_be_deleted(self.server.id)
        try:
            self.volume_status = self.blockstorage_behavior.get_volume_status(
                self.volume_id.id_)
            self.assertEqual(self.volume_status, "available", "Volume deleted")
        except Exception as self.err_msg:
            pass
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")
