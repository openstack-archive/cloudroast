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
from cloudcafe.blockstorage.volumes_api.v2.models import statuses
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


class BVCreateWithVolumeTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(BVCreateWithVolumeTest, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
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
    def test_attach_volume_to_server(self):
        """Verify that a volume can be attached to a server."""
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_, device=self.device)
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.IN_USE,
            timeout=self.volume_status_timeout,
            poll_rate=self.poll_frequency)
