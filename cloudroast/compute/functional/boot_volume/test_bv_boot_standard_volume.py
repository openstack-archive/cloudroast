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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.blockstorage.config import BlockStorageConfig
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


class BootStandardVolume(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(BootStandardVolume, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        cls.volume_size = 100
        cls.volume_type = "SATA"
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size, volume_type=cls.volume_type)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.err_msg = ""
        try:
            cls.response, cls.volume_id = cls.server_behaviors.boot_volume(
                cls.key, standard_volume_id=cls.volume)
        except Exception as cls.err_msg:
            print cls.err_msg
        else:
            cls.server = cls.response.entity
            cls.resources.add(cls.server.id,
                              cls.servers_client.delete_server)

    @tags(type='smoke', net='yes')
    @unittest.skip("Known issue")
    def test_server_built(self):
        self.assertNotEqual(self.err_msg, "",
                            "Server built (should not have been built)")
