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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture, tags, memoized)
from cafe.drivers.unittest.datasets import DatasetList

from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cloudroast.blockstorage.volumes_api.fixtures import \
    DataDrivenVolumesTestFixture


complete_volume_types = BlockstorageDatasets.volume_types()
complete_volume_types.apply_test_tags('snapshots-exhaustive-volume-types')
default_volume_type = BlockstorageDatasets.default_volume_type()
default_volume_type.apply_test_tags('snapshots-default-volume-type')
complete_volume_types.merge_dataset_tags(default_volume_type)



class SnapshotRestoreDataset(BlockstorageDatasets):

    @classmethod
    @memoized
    def volume_types_with_restore_control(
            cls, max_datasets=None, randomize=False, model_filter=None,
            filter_mode=BlockstorageDatasets.INCLUSION_MODE):
        """Returns a DatasetList of all VolumeTypes
        Filters should be dictionaries with model attributes as keys and
        lists of attributes as key values.
        """

        volume_type_list = cls._get_volume_types()
        volume_type_list = cls._filter_model_list(
            volume_type_list, model_filter=model_filter,
            filter_mode=filter_mode)

        dataset_list = DatasetList()
        is_enabled = \
            cls._volumes.config.allow_snapshot_restore_to_different_type
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_,
                    'restore_to_different_type_enabled': is_enabled}
            test_name = "{0}_to_other_is_{1}".format(
                vol_type.name, "allowed" if is_enabled else "disabled")
            dataset_list.append_new_dataset(test_name, data)

        # Apply modifiers
        return cls._modify_dataset_list(
            dataset_list, max_datasets=max_datasets, randomize=randomize)


@DataDrivenFixture
class SnapshotActions(DataDrivenVolumesTestFixture):

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
        self.assertVolumeCreateSuceeded(resp.entity.id_, resp.entity.size)
        restored_volume = self.volumes.behaviors.get_volume_info(
            resp.entity.id_)

        comparable_attributes_list = [
            "size", "volume_type", "bootable", "availability_zone",
            "attachments", "links", "status", "image_ref",
            "volume_image_metadata", "os_vol_host_attr_host",
            "os_vol_tenant_attr_tenant_id", "os_vol_mig_status_attr_migstat",
            "os_vol_mig_status_attr_name_id"]

        self.assertVolumeAttributesAreEqual(
            original_volume, restored_volume,
            attr_list=comparable_attributes_list)

    @data_driven_test(
        SnapshotRestoreDataset.volume_types_with_restore_control())
    def ddtest_verify_snapshot_restore_to_different_volume_type(
            self, volume_type_name, volume_type_id,
            restore_to_different_type_enabled):
        """Verify that a snapshot either CAN or CANNOT be restored to a
        volume of a type different from the snapshot's parent volume.
        The expected behavior is controlled via configuration.
        """

        all_types = self.volumes.behaviors.get_volume_type_list()
        other_types = [v.id_ for v in all_types if v.id_ != volume_type_id]
        if not other_types:
            setattr(self, '__unittest_skip__', True)
            setattr(
                self, '__unittest_skip_why__',
                'No other volume types available, skipping test.')

        original_volume = self.new_volume(vol_type=volume_type_id)
        snapshot = self.new_snapshot(original_volume.id_)

        resp = self.volumes.client.create_volume(
            original_volume.size, other_types[0],
            snapshot_id=snapshot.id_)

        self.assertResponseDeserializedAndOk(resp)
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed,
            resp.entity.id_)
        self.assertVolumeCreateSuceeded(resp.entity.id_, resp.entity.size)

        restored_volume = self.volumes.behaviors.get_volume_info(
            resp.entity.id_)

        if restore_to_different_type_enabled is False:
            assert original_volume.volume_type == restored_volume.volume_type,\
                (
                    "Snapshot {snapshot_id} unexpectedly restored to a volume "
                    "of type '{new_volume_type}', which does not match the "
                    "original volume's type '{original_volume_type}'".format(
                        snapshot_id=snapshot.id_,
                        new_volume_type=restored_volume.volume_type,
                        original_volume_type=original_volume.volume_type))

        if restore_to_different_type_enabled is True:
            assert original_volume.volume_type != restored_volume.volume_type,\
                (
                    "Snapshot {snapshot_id} unexpectedly restored to a volume "
                    "of type '{new_volume_type}', which does not match the "
                    "requested volume's type '{requested_volume_type}'".format(
                        snapshot_id=snapshot.id_,
                        new_volume_type=restored_volume.volume_type,
                        requested_volume_type=other_types[0]))

        comparable_attributes_list = [
            "size", "bootable", "availability_zone",
            "attachments", "links", "status", "image_ref",
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
    def ddtest_list_snapshots_detailed(
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
