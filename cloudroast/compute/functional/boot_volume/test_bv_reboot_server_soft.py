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
from cloudroast.compute.fixtures import ComputeFixture


class RebootServerSoftTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebootServerSoftTests, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        response, cls.volume_id = cls.server_behaviors.boot_volume(cls.key)
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='smoke', net='yes')
    def test_reboot_server_soft(self):
        self.reboot_time(server=self.server, reboot="SOFT",
                         servers_config=self.servers_config)
