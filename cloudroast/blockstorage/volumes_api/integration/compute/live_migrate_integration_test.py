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
from cloudcafe.compute.composites import ComputeAdminComposite

from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import ComputeIntegrationTestFixture
from cloudroast.blockstorage.volumes_api.integration.compute.datasets \
    import bfv_datasets


@DataDrivenFixture
class BootFromVolumeLiveMigrateIntegration(ComputeIntegrationTestFixture):

    @data_driven_test(bfv_datasets.flavors_by_images_by_volume_type)
    def ddtest_live_migrate_bfv_server_with_seven_attached_volumes(
            self, image, flavor, volume_type):

        os_type = self.get_image_os_type(image.id)

        # Create a volume
        volume = self.create_volume_from_image_test(volume_type, image)

        # Create block device mapping
        bdm = self.compute.servers.behaviors.create_block_device_mapping_v1(
            volume.id_, True, 'vda', volume.size, volume_type.id_)

        # Boot a server from the volume
        self.server = self.servers.behaviors.create_active_server(
            name=self.random_server_name(), flavor_ref=flavor.id,
            block_device_mapping=bdm).entity

        # Connect to server
        self.server_conn = self.connect_to_instance(
            self.server, os_type=os_type)

        # Create list for extra volumes
        extra_volumes = []

        # Create and attach seven volumes
        for x in range(0, 7):
            bonus_volume = self.new_volume()
            resp = self.compute.volume_attachments.behaviors. \
                _validated_volume_attach(self.server.id, bonus_volume.id_)
            extra_volumes.append((bonus_volume, resp.entity))

        for extra_volume, attachment in extra_volumes:

                # Todo: This works because a single volume attaches to a server
                #       Must be fixed when multi-attach becomes available

                self.compute.volume_attachments.behaviors. \
                    wait_for_attachment_to_propagate(
                        attachment.id_, self.server.id)
                self.compute.volume_attachments.behaviors. \
                    verify_volume_status_progression_during_attachment(
                        extra_volume.id_)

        # Write data to the root disk
        resp = self.server_conn.create_large_file(multiplier=0.1)
        self.assertTrue(resp, "Unable to write data to bootable OS volume")

        # Live migration
        # Verify live migration
        self.compute_admin = ComputeAdminComposite()

        self.compute_admin.servers.client.live_migrate_server(
            self.server.id, block_migration=True, disk_over_commit=False)
        self.compute_admin.servers.behaviors.wait_for_server_status(
            self.server.id, "ACTIVE")

        # Verify seven volumes are "in use"
        for extra_volume, attachment in extra_volumes:
            self.compute.volume_attachments.behaviors._get_volume_status(
                extra_volume.id_)
