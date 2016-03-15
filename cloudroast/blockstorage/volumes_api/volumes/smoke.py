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

from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.decorators import tags
from cloudroast.blockstorage.volumes_api.fixtures import \
    VolumesTestFixture
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cafe.drivers.unittest.decorators import DataDrivenFixture

volume_types_dataset = BlockstorageDatasets.volume_types()


@DataDrivenFixture
class VolumeActions(VolumesTestFixture):

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_create_volume(
            self, volume_type_name, volume_type_id):
        """Verify that a volume of minimum size can be created"""

        # Setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        name = self.random_volume_name()
        description = "{0}".format(self.__class__.__name__)
        metadata = {"metadata_key_one": "metadata_value_one"}
        availability_zone = self.volumes.auth.availability_zone

        resp = self.volumes.client.create_volume(
            size, volume_type_id, name=name,
            description=description,
            availability_zone=availability_zone,
            metadata=metadata)

        self.assertResponseStatusInRange(
            resp, 200, 299, msg='Volume create failed')
        self.assertResponseIsDeserialized(resp)
        volume = resp.entity

        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        # TODO: Replace these seperate assertions with a call to
        #       assertVolumeAttributesAreEqual
        self.assertEqual(volume.name, name)
        self.assertEqual(volume.description, description)
        self.assertEqual(str(volume.size), str(size))
        self.assertEqual(volume.attachments, list())
        self.assertIsNotNone(volume.created_at)
        self.assertIsNotNone(volume.status)
        self.assertIsNone(volume.snapshot_id)

        # Verify that metadata is set as expected
        for key in metadata.iterkeys():
            self.assertIn(key, volume.metadata)
            self.assertEqual(metadata[key], volume.metadata[key])

        if availability_zone:
            self.assertEqual(volume.availability_zone, availability_zone)

        # Verify volume create suceeded
        self.assertVolumeCreateSucceeded(volume.id_, volume.size)

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_final_volume_metadata(
            self, volume_type_name, volume_type_id):
        """Verify that a volume of minimum size can be created"""

        # Setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        name = self.random_volume_name()
        description = "{0}".format(self.__class__.__name__)
        metadata = {"metadata_key_one": "metadata_value_one"}
        availability_zone = self.volumes.auth.availability_zone

        volume = self.volumes.behaviors.create_available_volume(
            size, volume_type_id, name=name, description=description,
            availability_zone=availability_zone, metadata=metadata)

        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        # Wait for all processes to update metadata field
        volume = self.volumes.behaviors.get_volume_info(volume.id_)

        # Verify that metadata is set as expected
        for key in metadata.iterkeys():
            self.assertIn(key, volume.metadata)
            self.assertEqual(metadata[key], volume.metadata[key])

        if availability_zone:
            self.assertEqual(volume.availability_zone, availability_zone)

        # Verify volume create suceeded
        self.assertVolumeCreateSucceeded(volume.id_, volume.size)

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_update_volume_info_via_body(
            self, volume_type_name, volume_type_id):
        """Verify that a volume's name and description can be updated after
        creation
        """

        # Setup
        volume = self.new_volume(vol_type=volume_type_id)
        volume_info = self.volumes.behaviors.get_volume_info(volume.id_)
        self.assertVolumeAttributesAreEqual(volume, volume_info)

        # Update volume info
        new_name = "NewUpdatedVolumeName"
        new_description = "NewUpdatedVolumeDescription"

        resp = self.volumes.client.update_volume(
            volume.id_, name=new_name, description=new_description)
        updated_volume = resp.entity

        updated_volume_info = self.volumes.behaviors.get_volume_info(
            updated_volume.id_)

        # Test Update Volume Response
        self.assertEqual(
            updated_volume.name, new_name,
            'New name was not found in update volume response')
        self.assertEqual(
            updated_volume.description, new_description,
            'New description was not found in update volume response')

        # Test get-info response on updated volume
        self.assertEqual(
            updated_volume_info.name, new_name,
            'New name was not found in update volume get-info response')
        self.assertEqual(
            updated_volume_info.description, new_description,
            'New description was not found in update volume get-info response')

        # Test that all other attributes are untouched
        similar_attributes = [
            'size', 'availability_zone', 'attachments', 'created_at',
            'status', 'snapshot_id', 'volume_type']
        self.assertVolumeAttributesAreEqual(
            volume_info, updated_volume,
            attr_list=similar_attributes,
            msg="Unmodified updated volume info did not match original volume "
            "info")

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_get_volume_info(self, volume_type_name, volume_type_id):
        """Verify that the API can return detailed information on a single
        volume
        """

        # Setup
        volume = self.new_volume(vol_type=volume_type_id)
        resp = self.volumes.client.get_volume_info(volume.id_)
        self.assertExactResponseStatus(
            resp, 200, msg='Get volume info call failed')
        self.assertResponseIsDeserialized(resp)
        volume_info = resp.entity

        # Test
        self.assertVolumeAttributesAreEqual(volume, volume_info)

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_list_volumes(self, volume_type_name, volume_type_id):
        """Verify that the API can return a list of all volumes"""

        # Setup
        volume = self.new_volume(vol_type=volume_type_id)

        # Test
        resp = self.volumes.client.list_all_volumes()
        self.assertExactResponseStatus(
            resp, 200, msg='Get volume list call failed')
        self.assertResponseIsDeserialized(resp)
        volume_list = resp.entity

        expected_volumes = [v for v in volume_list if v.id_ == volume.id_]
        self.assertTrue(
            len(expected_volumes) > 0,
            'No volumes where found in the volume list with an id == '
            '{0}'.format(volume.id_))

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_list_volume_details(self, volume_type_name, volume_type_id):
        """Verify that the API can return a list detailed information for
        all volumes
        """

        # Setup
        volume = self.new_volume(vol_type=volume_type_id)
        resp = self.volumes.client.list_all_volumes_info()
        self.assertExactResponseStatus(
            resp, 200, msg='Get volume list call failed')
        self.assertResponseIsDeserialized(resp)
        volume_list = resp.entity

        expected_volumes = [v for v in volume_list if v.id_ == volume.id_]
        self.assertTrue(
            len(expected_volumes) > 0,
            'No volumes where found in the volume list with an id == '
            '{0}'.format(volume.id_))
        volume_info = expected_volumes[0]

        # Test
        self.assertVolumeAttributesAreEqual(
            volume, volume_info, excluded_attrs_list=['volume_image_metadata'])

    @data_driven_test(volume_types_dataset)
    @tags('volumes', 'smoke')
    def ddtest_delete_volume(self, volume_type_name, volume_type_id):
        """Verify that a volume can be deleted"""

        # Setup
        volume = self.new_volume(vol_type=volume_type_id)

        # Test
        result = self.volumes.behaviors.delete_volume_confirmed(volume.id_)
        self.assertTrue(
            result, "Unable to confirm that volume {0} was deleted".format(
                volume.id_))
