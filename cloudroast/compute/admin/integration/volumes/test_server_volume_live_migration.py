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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudcafe.blockstorage.volumes_api.v1.models import statuses

from cloudroast.compute.admin.servers.test_server_live_migration import \
    LiveMigratationServerTests


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(LiveMigratateServerWithVolumeTests(
        "test_format_and_mount_disks"))
    suite.addTest(LiveMigratateServerWithVolumeTests(
        "test_live_migrate_server"))
    suite.addTest(LiveMigratateServerWithVolumeTests(
        "test_verify_ephemeral_disks_mounted"))
    suite.addTest(LiveMigratateServerWithVolumeTests(
        "test_volume_attached_after_migration"))
    return suite


class LiveMigratateServerWithVolumeTests(LiveMigratationServerTests):

    @classmethod
    def setUpClass(cls):
        super(LiveMigratateServerWithVolumeTests, cls).setUpClass()
        cls.volumes = VolumesAutoComposite()

        # Create a volume
        cls.device = '/dev/xvdm'
        cls.volume = cls.volumes.behaviors.create_available_volume(
            cls.volumes.config.min_volume_size,
            cls.volumes.config.default_volume_type,
            rand_name('volume'))
        cls.resources.add(
            cls.volume.id_,
            cls.volumes.client.delete_volume)

        # Attach the volume to the server
        cls.volume_attachments_client.attach_volume(
            cls.server.id, cls.volume.id_, device=cls.device)
        cls.volumes.behaviors.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.IN_USE,
            cls.volumes.config.volume_create_max_timeout)
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.volumes.behaviors.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.AVAILABLE,
            cls.volumes.config.volume_delete_max_timeout)
        super(LiveMigratateServerWithVolumeTests, cls).tearDownClass()

    @tags(type='smoke', net='yes')
    def test_volume_attached_after_migration(self):
        volume_after_migration = self.volumes.client.get_volume_info(
            self.volume.id_).entity
        self.assertEqual(volume_after_migration.status, 'in-use')
