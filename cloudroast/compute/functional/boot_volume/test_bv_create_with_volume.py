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
from cloudcafe.blockstorage.volumes_api.v2.models import statuses
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture
from cloudcafe.blockstorage.config import BlockStorageConfig


class BVCreateWithVolumeTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(BVCreateWithVolumeTest, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        cls.response, cls.volume_id = cls.server_behaviors.boot_volume(cls.key)
        cls.resources.add(cls.volume_id,
                          cls.blockstorage_client.delete_volume)
        cls.server = cls.response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.volume_size = 100
        cls.volume_type = "SATA"
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            name='test-volume', size=cls.volume_size,
            volume_type=cls.volume_type,
            timeout=cls.volume_status_timeout)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.device = '/dev/xvdm'
        cls.mount_directory = '/mnt/test'
        cls.filesystem_type = 'ext3'

    @tags(type='smoke', net='no')
    @unittest.skip("Known issue")
    def test_attach_volume_to_server(self):
        """Verify that a volume can be attached to a server."""
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_, device=self.device)
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.IN_USE,
            timeout=self.volume_status_timeout,
            wait_period=self.poll_frequency)
