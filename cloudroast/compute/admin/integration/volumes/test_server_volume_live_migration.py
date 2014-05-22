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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeAdminFixture
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudcafe.blockstorage.volumes_api.v1.models import statuses


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(LiveMigratationServerTests(
        "test_format_and_mount_disks"))
    suite.addTest(LiveMigratationServerTests(
        "test_live_migrate_server"))
    suite.addTest(LiveMigratationServerTests(
        "test_verify_ephemeral_disks_mounted"))
    return suite


class LiveMigratationServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(LiveMigratationServerTests, cls).setUpClass()
        cls.volumes = VolumesAutoComposite()
        # Create a volume
        cls.device = '/dev/xvdm'
        cls.volume = cls.volumes.behaviors.create_available_volume(
            cls.volumes.config.min_volume_size,
            cls.volumes.config.default_volume_type,
            rand_name('volume'))
        # Create Instance
        cls.server = cls.server_behaviors.create_active_server().entity
        # Attach the volume to the server
        cls.volume_attachments_client.attach_volume(
            cls.server.id, cls.volume.id_, device=cls.device)
        cls.volumes.behaviors.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.IN_USE,
            cls.volumes.config.volume_create_max_timeout)
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.test_directories = []

    @tags(type='smoke', net='yes')
    def test_format_and_mount_disks(self):
        """Format and mount ephemeral disks, if any."""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config)

        # Get all disks and remove the primary disk from the list
        disks = remote_client.get_all_disks()
        disks.pop(self.servers_config.instance_disk_path, None)

        for disk in disks:
            self._format_disk(remote_client=remote_client, disk=disk,
                              disk_format=self.disk_format_type)
            mount_point = '/mnt/{name}'.format(name=rand_name('disk'))
            self._mount_disk(remote_client=remote_client, disk=disk,
                             mount_point=mount_point)
            test_directory = '{mount}/test'.format(mount=mount_point)
            remote_client.create_directory(test_directory)
            self.test_directories.append(test_directory)

    @tags(type='smoke', net='no')
    def test_live_migrate_server(self):
        """Verify the server completes the live migration."""
        self.admin_servers_client.live_migrate_server(
            self.server.id, block_migration=True, disk_over_commit=False)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)

    @tags(type='smoke', net='yes')
    def test_verify_ephemeral_disks_mounted(self):
        """Verify the server's ephemeral disks are still attached."""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config)
        for directory in self.test_directories:
            self.assertTrue(remote_client.is_directory_present(directory))
