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
    data_driven_test, DataDrivenFixture)
from cafe.drivers.unittest.decorators import tags
from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudroast.blockstorage.volumes_api.fixtures import VolumesTestFixture
from cloudroast.blockstorage.volumes_api.datasets import VolumesDatasets


@DataDrivenFixture
class VolumeActions(VolumesTestFixture):

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('volumes', 'smoke')
    def ddtest_create_minimum_size_default_volume(
            self, volume_type_name, volume_type_id):

        #Setup
        size = self.volumes.config.min_volume_size
        name = self.random_volume_name()
        description = "{0}".format(self.__class__.__name__)
        metadata = {"metadata_key_one": "metadata_value_one"}
        availability_zone = self.volumes.blockstorage_auth.availability_zone

        resp = self.volumes.client.create_volume(
            size, volume_type_id, name=name,
            description=description,
            availability_zone=availability_zone,
            metadata=metadata)

        self.assertExactResponseStatus(resp, 200, msg='Volume create failed')
        self.assertResponseIsDeserialized(resp)
        volume = resp.entity

        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed, volume.id_)

        #Test
        self.assertEqual(volume.name, name)
        self.assertEqual(volume.description, description)
        self.assertEqual(str(volume.size), str(size))
        self.assertEqual(volume.attachments, list())
        self.assertIsNotNone(volume.created_at)
        self.assertIsNotNone(volume.status)
        self.assertIsNone(volume.snapshot_id)
        self.assertIn(
            volume.status.lower(),
            [statuses.Volume.AVAILABLE.lower(),
             statuses.Volume.CREATING.lower()])

        for key in metadata.iterkeys():
            self.assertIn(key, volume.metadata)
            self.assertEqual(metadata[key], volume.metadata[key])

        if availability_zone:
            self.assertEqual(volume.availability_zone, availability_zone)

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('volumes', 'smoke')
    def ddtest_get_volume_info(self, volume_type_name, volume_type_id):
        volume = self.new_volume(vol_type=volume_type_id)
        resp = self.volumes.client.get_volume_info(volume.id_)
        self.assertExactResponseStatus(
            resp, 200, msg='Get volume info call failed')
        self.assertResponseIsDeserialized(resp)
        volume_info = resp.entity

        #Test
        self.assertEquals(volume.name, volume_info.name)
        self.assertEquals(
            volume.description, volume_info.description)
        self.assertEquals(str(volume.size), str(volume_info.size))
        self.assertEquals(volume.metadata, volume_info.metadata)
        self.assertEquals(
            volume.availability_zone, volume_info.availability_zone)
        self.assertEquals(volume.attachments, volume_info.attachments)
        self.assertEquals(volume.created_at, volume_info.created_at)
        self.assertEquals(volume.status, volume_info.status)
        self.assertIsNone(volume.snapshot_id, volume_info.snapshot_id)
        self.assertEquals(volume.volume_type, volume_info.volume_type)

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('volumes', 'smoke')
    def ddtest_list_volumes(self, volume_type_name, volume_type_id):
        volume = self.new_volume(vol_type=volume_type_id)
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

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('volumes', 'smoke')
    def ddtest_list_volume_details(self, volume_type_name, volume_type_id):
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

        #Test
        self.assertEquals(volume.name, volume_info.name)
        self.assertEquals(
            volume.description, volume_info.description)
        self.assertEquals(str(volume.size), str(volume_info.size))
        self.assertEquals(volume.metadata, volume_info.metadata)
        self.assertEquals(
            volume.availability_zone, volume_info.availability_zone)
        self.assertEquals(volume.attachments, volume_info.attachments)
        self.assertEquals(volume.created_at, volume_info.created_at)
        self.assertEquals(volume.status, volume_info.status)
        self.assertIsNone(volume.snapshot_id, volume_info.snapshot_id)
        self.assertEquals(volume.volume_type, volume_info.volume_type)

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('volumes', 'smoke')
    def ddtest_delete_volume(self, volume_type_name, volume_type_id):
        volume = self.new_volume(vol_type=volume_type_id)
        result = self.volumes.behaviors.delete_volume_confirmed(volume.id_)
        self.assertTrue(result)
