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
from cloudcafe.blockstorage.volumes_api.common.models import statuses
from cloudroast.blockstorage.volumes_api.fixtures import \
    VolumesTestFixture
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cafe.drivers.unittest.decorators import DataDrivenFixture


volume_types_dataset = BlockstorageDatasets.volume_types()


@DataDrivenFixture
class VolumeCapacity(VolumesTestFixture):

    @data_driven_test(volume_types_dataset)
    def ddtest_create_maximum_size_volume(
            self, volume_type_name, volume_type_id):
        """Verify that a volume of maximum size can be created"""

        # Setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "max_size", id_=volume_type_id, name=volume_type_name)
        name = self.random_volume_name()
        description = "{0}".format(self.__class__.__name__)
        metadata = {"metadata_key_one": "metadata_value_one"}
        availability_zone = self.volumes.auth.availability_zone

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

        # TODO: Replace these seperate assertions with a call to
        #       assertVolumeAttributesAreEqual
        self.assertEqual(volume.name, name)
        self.assertEqual(volume.description, description)
        self.assertEqual(str(volume.size), str(size))
        self.assertEqual(volume.attachments, list())
        self.assertIsNotNone(volume.created_at)
        self.assertIsNotNone(volume.status)
        self.assertIsNone(volume.snapshot_id)

        # TODO: Replace this assertion with a call to
        #       assertVolumeCreateSucceeded
        self.assertIn(
            volume.status.lower(),
            [statuses.Volume.AVAILABLE.lower(),
             statuses.Volume.CREATING.lower()])

        # Verify that metadata is set as expected
        for key in metadata.iterkeys():
            self.assertIn(key, volume.metadata)
            self.assertEqual(metadata[key], volume.metadata[key])

        if availability_zone:
            self.assertEqual(volume.availability_zone, availability_zone)
