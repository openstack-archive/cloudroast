from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.decorators import tags
from cloudroast.blockstorage.volumes_api.fixtures import \
    VolumesTestFixture
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cafe.drivers.unittest.decorators import DataDrivenFixture

volume_types_dataset = BlockstorageDatasets.volume_types()
volume_types_dataset.apply_test_tags('volume-cloning-complete-dataset')
configured_vtypes_dataset = BlockstorageDatasets.configured_volume_types()
configured_vtypes_dataset.apply_test_tags('volume-cloning-configured-dataset')
random_vtype_dataset = BlockstorageDatasets.volume_types(
    max_datasets=1, randomize=True)
random_vtype_dataset.apply_test_tags('volume-cloning-single-random-dataset')
volume_types_dataset.merge_dataset_tags(configured_vtypes_dataset)
volume_types_dataset.merge_dataset_tags(random_vtype_dataset)


@DataDrivenFixture
class CBSVolumeCloneTests(VolumesTestFixture):

    @data_driven_test(volume_types_dataset)
    @tags('smoke')
    def ddtest_create_exact_clone_of_existing_volume_and_verify_attributes(
            self, volume_type_name, volume_type_id):
        """Verify that data written to a volume is intact and available
        on a clone of that volume"""

        # Setup original volume
        metadata = {"OriginalVolumeMetadataKey": "OriginalVolumeMetadataValue"}
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        volume = self.volumes.behaviors.create_available_volume(
            size, volume_type_id,
            self.random_volume_name(), metadata=metadata)

        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        # Setup exact clone of original volume
        resp = self.volumes.client.create_volume(
            volume_type=volume_type_id, size=volume.size,
            source_volid=volume.id_)
        self.assertResponseStatusInRange(
            resp, 200, 299, msg='Volume clone create failed')
        self.assertResponseIsDeserialized(resp)
        volume_clone = resp.entity
        self.assertEqual(
            volume_clone.source_volid, volume.id_,
            "The source_volid of volume {0} (source_volid={1}) does not equal"
            "the volume id of the actual source volume ({2})".format(
                volume_clone.id_, volume_clone.source_volid, volume.id_))

        # Add cleanup for volume clone
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume_clone.id_)
        volume_clone_create_timeout = \
            self.volumes.behaviors.calculate_volume_clone_timeout(volume.size)

        self.volumes.behaviors.verify_volume_create_status_progresion(
            volume_clone.id_, volume_clone_create_timeout)
        volume_clone_info = self.volumes.behaviors.get_volume_info(
            volume_clone.id_)

        # Verify relevant clone attributes are the same as source volume
        excluded_attributes = [
            'created_at', 'id_', 'display_name', 'name', 'source_volid',
            'metadata', 'links', 'os_vol_host_attr_host']
        self.assertVolumeAttributesAreEqual(
            volume, volume_clone_info, excluded_attrs_list=excluded_attributes)

        # TODO: This currently fails, but it isn't clear if this is expected
        #       behavior or not.  Find out if cinder currently or will
        #       support metadata cloning.
        # Verify relevant clone metadata is the same as source volume
        # excluded_keys = ['storage-node']
        # key_list = [
        #    key for key in volume.metadata.keys() if key not in excluded_keys]
        # self.assertVolumeMetadataIsEqual(
        #    volume, volume_clone_info, key_list=key_list)

    @data_driven_test(volume_types_dataset)
    def ddtest_create_larger_clone_of_volume(
            self, volume_type_name, volume_type_id):
        """Clone a volume using a larger size than the original volume."""

        volume = self.new_volume(vol_type=volume_type_id)
        new_size = int(volume.size) + 1
        clone_response = self.volumes.client.create_volume(
            new_size, volume_type_id, source_volid=volume.id_)

        self.assertResponseDeserializedAndOk(clone_response)
        volume_clone = clone_response.entity
        self.assertVolumeCloneSucceeded(volume_clone.id_, volume_clone.size)

        # Add cleanup for volume clone
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume_clone.id_)
        volume_clone_create_timeout = \
            self.volumes.behaviors.calculate_volume_clone_timeout(volume.size)

        self.volumes.behaviors.wait_for_volume_status(
            volume_clone.id_, 'available', volume_clone_create_timeout)

        volume_clone_info = self.volumes.behaviors.get_volume_info(
            volume_clone.id_)

        # Verify new size
        assert int(volume_clone_info.size) == new_size, (
            'Volume clone size was {0} instead of the expected size '
            '{1}'.format(volume_clone_info.size, new_size))
        assert volume.size < volume_clone_info.size, (
            'Volume clone was not larger than source volume')

        # Verify Attributes
        excluded_attributes = [
            'created_at', 'id_', 'display_name', 'name', 'source_volid',
            'metadata', 'size']
        self.assertVolumeAttributesAreEqual(
            volume, volume_clone_info, excluded_attrs_list=excluded_attributes)

        # Verify metadata
        excluded_keys = ['storage-node']
        key_list = [
            key for key in volume.metadata.keys() if key not in excluded_keys]
        self.assertVolumeMetadataIsEqual(
            volume, volume_clone_info, key_list=key_list)
