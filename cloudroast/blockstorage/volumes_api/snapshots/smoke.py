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

from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cloudroast.blockstorage.volumes_api.fixtures import \
    VolumesTestFixture

complete_volume_types = BlockstorageDatasets.volume_types()
complete_volume_types.apply_test_tags('snapshots-exhaustive-volume-types')
default_volume_type = BlockstorageDatasets.default_volume_type()
default_volume_type.apply_test_tags('snapshots-default-volume-type')
complete_volume_types.merge_dataset_tags(default_volume_type)


@DataDrivenFixture
class SnapshotActions(VolumesTestFixture):

    @data_driven_test(complete_volume_types)
    def ddtest_verify_snapshot_status_progression(
            self, volume_type_name, volume_type_id):
        """Verify snapshot passes through all expected states after create"""

        volume = self.new_volume(vol_type=volume_type_id)
        snapshot_name = self.random_snapshot_name()
        snapshot_description = "this is a snapshot description."
        snapshot = self.volumes.behaviors.create_available_snapshot(
            volume.id_, name=snapshot_name, description=snapshot_description)
        self.addCleanup(
            self.volumes.behaviors.delete_snapshot_confirmed, snapshot.id_)

        self.assertEquals(snapshot.volume_id, volume.id_)
        self.assertEquals(snapshot.name, snapshot_name)
        self.assertEquals(snapshot.description, snapshot_description)
        self.assertIn(
            snapshot.status,
            [statuses.Snapshot.AVAILABLE, statuses.Snapshot.CREATING])
        self.assertEquals(snapshot.size, volume.size)

    @data_driven_test(complete_volume_types)
    def ddtest_verify_snapshot_restore_to_same_volume_type(
            self, volume_type_name, volume_type_id):
        """Verify that a snapshot can be restored to a volume of the
        same type as the snapshot's parent volume
        """

        original_volume = self.new_volume(vol_type=volume_type_id)
        snapshot = self.new_snapshot(original_volume.id_)

        resp = self.volumes.client.create_volume(
            original_volume.size, original_volume.volume_type,
            snapshot_id=snapshot.id_)

        self.assertResponseDeserializedAndOk(resp)
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, resp.entity.id_)
        self.assertRestoreSnapshotToVolumeSucceeded(
            resp.entity.id_, resp.entity.size)
        restored_volume = self.volumes.behaviors.get_volume_info(
            resp.entity.id_)

        comparable_attributes_list = [
            "size", "volume_type", "bootable", "availability_zone",
            "attachments", "status", "image_ref",
            "volume_image_metadata", "os_vol_host_attr_host",
            "os_vol_tenant_attr_tenant_id", "os_vol_mig_status_attr_migstat",
            "os_vol_mig_status_attr_name_id"]

        self.assertVolumeAttributesAreEqual(
            original_volume, restored_volume,
            attr_list=comparable_attributes_list)

    @data_driven_test(complete_volume_types)
    def ddtest_list_snapshots(
            self, volume_type_name, volume_type_id):
        """Verify that the api can list snapshots"""

        volume = self.new_volume(vol_type=volume_type_id)
        snapshot = self.new_snapshot(volume.id_)

        # Get snapshot list
        resp = self.volumes.client.list_all_snapshots()
        self.assertResponseDeserializedAndOk(
            resp, 'Unable to get snapshot list for volume {0}'.format(
                volume.id_))

        snapshot_list = resp.entity
        self.assertIn(snapshot.name, [s.name for s in snapshot_list])
        self.assertIn(snapshot.id_, [s.id_ for s in snapshot_list])

    @data_driven_test(complete_volume_types)
    def ddtest_list_detailed_snapshots(
            self, volume_type_name, volume_type_id):
        """Verify that the api can list snapshot details"""

        volume = self.new_volume(vol_type=volume_type_id)
        snapshot = self.new_snapshot(volume.id_)

        # Get snapshot list
        resp = self.volumes.client.list_all_snapshots_info()
        self.assertResponseDeserializedAndOk(
            resp, 'Unable to get snapshot list for volume {0}'.format(
                volume.id_))

        snapshot_list = resp.entity
        self.assertIn(snapshot.name, [s.name for s in snapshot_list])
        self.assertIn(snapshot.id_, [s.id_ for s in snapshot_list])

    @data_driven_test(complete_volume_types)
    def ddtest_get_snapshot_info(
            self, volume_type_name, volume_type_id):
        """Verify that the api return details on a single snapshot"""

        volume = self.new_volume(vol_type=volume_type_id)
        snapshot = self.new_snapshot(volume.id_)

        # Get snapshot info
        resp = self.volumes.client.get_snapshot_info(snapshot.id_)
        self.assertResponseDeserializedAndOk(
            resp,
            "Unable to get snapshot info for snapshot '{0}' of volume "
            "'{1}'".format(snapshot.id_, volume.id_))
        snapshot_info = resp.entity

        self.assertEqual(snapshot.name, snapshot_info.name)
        self.assertEqual(snapshot.id_, snapshot_info.id_)
