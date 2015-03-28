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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.fixtures import ComputeAdminFixture


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
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Create a server in active state.
            - Initialize the test directories to an empty list.
        """
        super(LiveMigratationServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.test_directories = []

    @tags(type='smoke', net='yes')
    def test_format_and_mount_disks(self):
        """
        Format and mount ephemeral disks, if any.

        Will get the instance of the server and get all disks and removes the
        primary disk from the list and then formats and mounts each of the
        ephemeral disks.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config)

        # Get all disks and remove the primary disk from the list
        disks = remote_client.get_all_disks()
        disks.pop(self.servers_config.instance_disk_path, None)

        for disk in disks:
            self._format_disk(remote_client=remote_client, disk=disk,
                              disk_format=self.disk_format_type)
            mount_point = remote_client.generate_mountpoint()
            self._mount_disk(remote_client=remote_client, disk=disk,
                             mount_point=mount_point)
            test_directory = '{mount}/test'.format(mount=mount_point)
            remote_client.create_directory(test_directory)
            self.test_directories.append(test_directory)

    @tags(type='smoke', net='no')
    def test_live_migrate_server(self):
        """
        Verify the server completes the live migration.

        Will invoke a live migration of the server with the block migration
        flag set to true and the disk over commit flag to false.  Will
        continue to wait until the server reaches an active state or a
        timeout has been reached.
        """
        self.admin_servers_client.live_migrate_server(
            self.server.id, block_migration=True, disk_over_commit=False)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)

    @tags(type='smoke', net='yes')
    def test_verify_ephemeral_disks_mounted(self):
        """
        Verify the server's ephemeral disks are still attached.

        Will get the instance of the server and then go through each
        directory in the list of test directories and make sure
        each directory is present and reachable.

        The following assertions occur:
            - Directory Present call returns true.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config)
        for directory in self.test_directories:
            self.assertTrue(remote_client.is_directory_present(directory))
