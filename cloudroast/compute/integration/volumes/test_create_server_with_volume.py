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

from unittest.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
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
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create an active server.
            - Create an available volume.
            - Defines device to /dev/xvdm.
            - Defines mount directory to /mnt/test.
            - Defines filesystem type to ext3.

        """
        super(CreateServerVolumeIntegrationTest, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.server = cls.server_behaviors.create_active_server(
            key_name=cls.key.name).entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size,
            volume_type=cls.volume_type,
            timeout=cls.volume_create_timeout)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.device = '/dev/xvdm'
        cls.mount_directory = '/mnt/test'
        cls.filesystem_type = 'ext3'

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that teardown the necessary resources for testing.

        The following resources are released during this teardown:
            - Deletes the volume attached to the server.

        """
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.blockstorage_behavior.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.AVAILABLE,
            cls.volume_delete_timeout)
        super(CreateServerVolumeIntegrationTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_attach_volume_to_server(self):
        """
        Verify that a volume can be attached to a server.

        Will attach an already created volume to a server and then waits
        for the volume status to change status to "In Use".
        """
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_, device=self.device)
        self.blockstorage_behavior.wait_for_volume_status(
            self.volume.id_, statuses.Volume.IN_USE,
            self.volume_create_timeout)

    @tags(type='smoke', net='yes')
    def test_format_and_mount_volume(self):
        """
        Verify that the volume can be formatted and mounted.

        Will get the remote instance and then get all disks attached to the
        server.  It will make sure the correct disk is in the list and that
        the volume is of the correct size.  It will then format the disk and
        create a directory followed by mounting the disk.  Finally it will
        un-mount the disk.

        The following assertions occur:
            - The disk is in the disks retrieved from the server.
            - The size of the disk is the size defined.
        """
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
