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
class SnapshotActions(VolumesTestFixture):

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('snapshots', 'smoke')
    def ddtest_verify_snapshot_status_progression(
            self, volume_type_name, volume_type_id):
        volume = self.new_volume(vol_type=volume_type_id)
        snapshot_name = self.random_snapshot_name()
        snapshot_description = "this is a snapshot description."
        snapshot = self.volumes.behaviors.create_available_snapshot(
            volume.id_, name=snapshot_name, description=snapshot_description)

        self.assertEquals(snapshot.volume_id, volume.id_)
        self.assertEquals(snapshot.name, snapshot_name)
        self.assertEquals(snapshot.description, snapshot_description)
        self.assertIn(
            snapshot.status,
            [statuses.Snapshot.AVAILABLE, statuses.Snapshot.CREATING])
        self.assertEquals(snapshot.size, volume.size)

    @data_driven_test(VolumesDatasets.volume_types())
    @tags('snapshots', 'smoke')
    def ddtest_create_minimum_size_volume_snapshot(
            self, volume_type_name, volume_type_id):
        volume = self.new_volume(vol_type=volume_type_id)
        snapshot_name = self.random_snapshot_name()
        snapshot_description = "this is a snapshot description."

        resp = self.volumes.client.create_snapshot(
            volume.id_, display_name=snapshot_name,
            display_description=snapshot_description, force_create=True)

        self.assertExactResponseStatus(
            resp, 200, msg='Volume Snapshot create failed')
        self.assertResponseIsDeserialized(resp)
        snapshot = resp.entity
        self.assertEquals(snapshot.volume_id, volume.id_)
        self.assertEquals(snapshot.display_name, snapshot_name)
        self.assertEquals(
            snapshot.display_description, snapshot_description)
        self.assertIn(
            snapshot.status,
            [statuses.Snapshot.AVAILABLE, statuses.Snapshot.CREATING])
        self.assertEquals(snapshot.size, volume.size)
