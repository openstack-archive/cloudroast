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

from unittest2.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.blockstorage.volumes_api.v1.models import statuses
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(CreateServerVolumeIntegrationTest(
        "test_attach_volume_to_server"))
    suite.addTest(CreateServerVolumeIntegrationTest(
        "test_format_and_mount_volume"))
    return suite


class CreateServerVolumeIntegrationTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateServerVolumeIntegrationTest, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            display_name='test-volume', size=cls.volume_size,
            volume_type=cls.volume_type,
            timeout=cls.volume_status_timeout)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.device = '/dev/xvdm'
        cls.mount_directory = '/mnt/test'
        cls.filesystem_type = 'ext3'

    @classmethod
    def tearDownClass(cls):
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.blockstorage_behavior.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.AVAILABLE)
        super(CreateServerVolumeIntegrationTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_attach_volume_to_server(self):
        """Verify that a volume can be attached to a server."""
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_, device=self.device)
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.IN_USE)

    @tags(type='smoke', net='yes')
    def test_format_and_mount_volume(self):
        """Verify that the volume can be formatted and mounted."""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config)
        disks = remote_client.get_all_disks()
        self.assertIn(self.device, disks.keys())
        self.assertEqual(disks.get(self.device), self.volume_size)
        remote_client.format_disk(disk=self.device,
                                  filesystem_type=self.filesystem_type)
        remote_client.create_directory(self.mount_directory)
        remote_client.mount_disk(self.device, self.mount_directory)

        # Unmount the disk so that it can be cleaned up
        remote_client.unmount_disk(self.mount_directory)
