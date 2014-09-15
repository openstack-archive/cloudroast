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
from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture
from cloudcafe.common.tools.datagen import random_string
from cloudcafe.blockstorage.datasets import ComputeIntegrationDatasets

from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import VolumesImagesIntegrationFixture


# Temporary.  Replace this with a direct call to get configured
# default volume typ details
volume_type_list = ComputeIntegrationDatasets._get_volume_types()
default_volume_type = None
for vtype in volume_type_list:
    if vtype.name == 'SATA':
        default_volume_type = vtype
        break

# Create tagged Image dataset
images_complete_dataset = ComputeIntegrationDatasets.images()
images_single_random_dataset = ComputeIntegrationDatasets.images(
    max_datasets=1, randomize=True)
images_configured_dataset = ComputeIntegrationDatasets.configured_images()
images_complete_dataset.apply_test_tags("bfv-exhaustive")
images_configured_dataset.apply_test_tags("bfv-configured")
images_single_random_dataset.apply_test_tags("bfv-single-random")
images_complete_dataset.merge_dataset_tags(
    images_configured_dataset,
    images_single_random_dataset)

# Create tagged Images by VolumeType dataset
images_by_volume_complete_dataset = \
    ComputeIntegrationDatasets.images_by_volume_type()
images_by_volume_single_random_dataset = \
    ComputeIntegrationDatasets.images_by_volume_type(
        max_datasets=1, randomize=True)
images_by_volume_configured_dataset = \
    ComputeIntegrationDatasets.configured_images_by_volume_type()
images_by_volume_complete_dataset.apply_test_tags("bfv-exhaustive")
images_by_volume_configured_dataset.apply_test_tags("bfv-configured")
images_by_volume_single_random_dataset.apply_test_tags("bfv-single-random")
images_by_volume_complete_dataset.merge_dataset_tags(
    images_by_volume_configured_dataset,
    images_by_volume_single_random_dataset)

# Create tagged Images by Flavor dataset
images_by_flavor_complete_dataset = \
    ComputeIntegrationDatasets.images_by_flavor()
images_by_flavor_single_random_dataset = \
    ComputeIntegrationDatasets.images_by_flavor(
        max_datasets=1, randomize=True)
images_by_flavor_configured_dataset = \
    ComputeIntegrationDatasets.configured_images_by_flavor()
images_by_flavor_complete_dataset.apply_test_tags("bfv-exhaustive")
images_by_flavor_configured_dataset.apply_test_tags("bfv-configured")
images_by_flavor_single_random_dataset.apply_test_tags("bfv-single-random")
images_by_flavor_complete_dataset.merge_dataset_tags(
    images_by_flavor_configured_dataset,
    images_by_flavor_single_random_dataset)


@DataDrivenFixture
class BootFromVolumeIntegrationTests(VolumesImagesIntegrationFixture):

    @data_driven_test(images_complete_dataset)
    def ddtest_non_asserting_min_disk_check_for_image(self, image):
        """Check if the image has min disk attribute set, print a
        message if it doesn't.  This test will only fail on Error"""
        self.check_if_minimum_disk_size_is_set(image)

    @data_driven_test(images_complete_dataset)
    def ddtest_min_disk_is_set_for_image(self, image):
        """Verify that image has min disk attribute set"""
        self.assertMinDiskSizeIsSet(image)

    @data_driven_test(images_by_volume_complete_dataset)
    def ddtest_create_basic_bootable_volume_from(self, volume_type, image):
        """Create a single volume_type volume from image"""
        self.create_volume_from_image_test(volume_type, image)

    @data_driven_test(images_by_flavor_complete_dataset)
    def ddtest_create_bootable_volume_from_a_snapshot_of_a_server(
            self, image, flavor, volume_type=default_volume_type):
        self.create_bootable_volume_from_server_snapshot(
            image, flavor, volume_type)

    @data_driven_test(images_by_flavor_complete_dataset)
    def ddtest_create_bootable_volume_from_last_of_3_snapshots_of_a_server(
            self, image, flavor, volume_type=default_volume_type):
        self.create_bootable_volume_from_third_snapshot_of_server_test(
            image, flavor, volume_type)

    @data_driven_test(images_by_flavor_complete_dataset)
    def ddtest_verify_data_on_custom_snapshot_after_copy_to_volume(
            self, image, flavor, volume_type=default_volume_type):
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
            self.random_server_name(), server_snapshot.id, flavor.id,
            block_device_mapping=bdm).entity

        # Setup remote instance client
        restored_server_conn = self.connect_to_instance(new_bfv_server)

        # Get hash of remote file
        restored_hash = self.get_remote_file_md5_hash(
            restored_server_conn, '/', file_name)

        assert original_hash == restored_hash, (
            'Restored data hash "{0}" did not match original data hash "{1}"'
            .format(restored_hash, original_hash))
