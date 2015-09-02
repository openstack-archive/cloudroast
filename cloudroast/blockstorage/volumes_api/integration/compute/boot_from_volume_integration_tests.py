"""
Copyright 2014 Rackspace

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
from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.datasets import BlockstorageDatasets

from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import ComputeIntegrationTestFixture
from cloudroast.blockstorage.volumes_api.integration.compute.datasets \
    import bfv_datasets


@DataDrivenFixture
class BootFromVolumeIntegrationTests(ComputeIntegrationTestFixture):

    @data_driven_test(bfv_datasets.images)
    def ddtest_non_asserting_min_disk_check_for_image(self, image):
        """Check if the image has min disk attribute set, print a
        message if it doesn't.  This test will only fail on Error"""
        self.check_if_minimum_disk_size_is_set(image)

    @data_driven_test(bfv_datasets.images)
    def ddtest_min_disk_is_set_for_image(self, image):
        """Verify that image has min disk attribute set"""
        self.assertMinDiskSizeIsSet(image)

    @data_driven_test(bfv_datasets.images_by_volume)
    def ddtest_create_basic_bootable_volume_from(self, volume_type, image):
        """Create a single volume_type volume from image"""
        self.create_volume_from_image_test(volume_type, image)

    @data_driven_test(bfv_datasets.images_by_flavor)
    def ddtest_create_bootable_volume_from_a_snapshot_of_a_server(
            self, image, flavor,
            volume_type=BlockstorageDatasets.default_volume_type_model()):
        self.create_bootable_volume_from_server_snapshot(
            image, flavor, volume_type)

    @data_driven_test(bfv_datasets.images_by_flavor)
    def ddtest_create_bootable_volume_from_last_of_3_snapshots_of_a_server(
            self, image, flavor,
            volume_type=BlockstorageDatasets.default_volume_type_model()):
        self.create_bootable_volume_from_third_snapshot_of_server_test(
            image, flavor, volume_type)

    @data_driven_test(bfv_datasets.flavors_by_images_by_volume_type)
    def ddtest_boot_a_server_from_a_volume(
            self, image, flavor, volume_type):

        os_type = self.get_image_os_type(image.id)

        # Create a bootable volume
        volume = self.create_volume_from_image_test(volume_type, image)

        # Create block device mapping
        bdm = self.compute.servers.behaviors.create_block_device_mapping_v1(
            volume.id_, True, 'vda', volume.size, volume_type.id_)

        # Boot a server from the volume
        server = self.servers.behaviors.create_active_server(
            name=self.random_server_name(), flavor_ref=flavor.id,
            block_device_mapping=bdm).entity

        # Connect to server
        self.server_conn = self.connect_to_instance(server, os_type=os_type)

        # Write data to the root disk
        resp = self.server_conn.create_large_file(multiplier=0.1)
        self.assertTrue(resp, "Unable to write data to bootable OS volume")

    @data_driven_test(bfv_datasets.images_by_flavor)
    def ddtest_verify_data_on_custom_snapshot_after_copy_to_volume(
            self, image, flavor,
            volume_type=BlockstorageDatasets.default_volume_type_model()):
        """This test currently only works for Linux images"""

        # Create a server
        original_server = self.new_server(
            name=self.random_server_name(), image=image.id, flavor=flavor.id,
            add_cleanup=False)

        # Connect to server
        original_server_connection = self.connect_to_instance(
            original_server)

        # Write data to the root disk
        file_name = random_string("original_data")
        file_content = "a" * 1024
        self.create_remote_file(
            original_server_connection, '/', file_name, file_content)
        original_server_connection.filesystem_sync()

        # Get hash of remote file
        original_hash = self.get_remote_file_md5_hash(
            original_server_connection, '/', file_name)

        # Create a snapshot of the server
        server_snapshot = self.make_server_snapshot(original_server)

        # Create a bootable volume from the server snapshot
        bootable_volume = self.create_volume_from_image_test(
            volume_type, server_snapshot)

        # Create block device mapping
        bdm = self.compute.servers.behaviors.create_block_device_mapping_v1(
            bootable_volume.id_, True, 'vda', bootable_volume.size,
            volume_type.id_)

        # Boot a server from the volume
        new_bfv_server = self.servers.behaviors.create_active_server(
            name=self.random_server_name(), flavor_ref=flavor.id,
            block_device_mapping=bdm).entity

        assert new_bfv_server is not None, (
            "Unable to build a server from volume '{volume}' and flavor "
            "'{flavor}' with block device mapping: {bdm}".format(
                volume=bootable_volume.id_, flavor=flavor.id, bdm=bdm))

        # Setup remote instance client
        new_bfv_server_conn = self.connect_to_instance(
            new_bfv_server, os_type='linux')

        # Get hash of remote file
        restored_hash = self.get_remote_file_md5_hash(
            new_bfv_server_conn, '/', file_name)

        assert original_hash == restored_hash, (
            'Restored data hash "{0}" did not match original data hash "{1}"'
            .format(restored_hash, original_hash))
