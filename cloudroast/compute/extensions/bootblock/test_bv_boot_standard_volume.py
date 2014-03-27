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
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


class BootStandardVolume(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(BootStandardVolume, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        cls.volume_size = cls.block_device_mapping.bdm_size
        cls.volume_type = cls.block_device_mapping.bdm_type
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size, volume_type=cls.volume_type)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.err_msg = ""

    @tags(type='smoke', net='yes')
    def test_server_built(self):
        boot_from_block = {'volume_id': self.volume.id_,
                           'del_on_termination': None,
                           'source_type': None,
                           'dest_type': None,
                           'device_name': None,
                           'type': None}
        try:
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            # Pass needs to be changed to a specific error when testing can be
            # done on this script and the correct error determined.
            pass
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because volume was standard")
