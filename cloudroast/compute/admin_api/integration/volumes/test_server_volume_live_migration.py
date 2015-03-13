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
from cloudcafe.blockstorage.composites import VolumesAutoComposite
from cloudcafe.blockstorage.volumes_api.v1.models import statuses

from cloudroast.compute.instance_actions.admin_api.test_server_live_migration import \
    LiveMigratationServerTests


def load_tests(loader, standard_tests, pattern):
    """
    Generate a test suite of tests from several test classes.

    Specifically:
        - test_volume_attached_after_migration from
            LiveMigratateServerWithVolumeTests
        - test_format_and_mount_disks, test_live_migrate_server,
          test_verify_ephemeral_disks_mounted from
          LiveMigratateServerWithVolumeTests

    These tests are added in a specific order to the load_tests method to
    enforce run order. This run order will ensure that the instance
    generated during LiveMigratateServerWithVolumeTests setUpClass
    is setup and then migrated in the appropriate order for these tests.
    """
    suite = TestSuite()

    # During the LiveMigratateServerWithVolumeTests setup an instance is
    # created that will be used for the tests in this test module
    suite.addTest(LiveMigratateServerWithVolumeTests(
        "test_format_and_mount_disks"))
    # This test performs a live migrate on the instance
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
        """
        Perform actions that setup the neccesary resources for testing

        The following resources are accessed from a parent class:
            - An instance from LiveMigratationServerTests

        The following resources are created during this setup:
            - A volume with the minimum volume size and the volume
              type from the test configuration
            - An attachment between the create volume and the instance
              from the parent class
        """
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
        """
        Perform actions that allow for the cleanup of any generated resources

        The following resources are deleted during this tear down:
            - The volume attachment created in the setup
        """
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.volumes.behaviors.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.AVAILABLE,
            cls.volumes.config.volume_delete_max_timeout)
        super(LiveMigratateServerWithVolumeTests, cls).tearDownClass()

    @tags(type='smoke', net='yes')
    def test_volume_attached_after_migration(self):
        """
        Test that a volume has the status of "in-use"

        Get the details of the volume created and attached during the
        setup. Validate that the status of the volume is 'in-use'.

        This test will be successful if:
            - The user is able to get information on the volume created
              and attached during setup
            - The volume status shows as 'in-use'
        """
        volume_after_migration = self.volumes.client.get_volume_info(
            self.volume.id_).entity
        self.assertEqual(volume_after_migration.status, 'in-use')
