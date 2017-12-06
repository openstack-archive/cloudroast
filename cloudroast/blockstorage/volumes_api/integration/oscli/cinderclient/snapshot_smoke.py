from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cloudcafe.blockstorage.volumes_api.common.models.statuses import \
    Snapshot as SnapshotStatuses

from cloudroast.blockstorage.volumes_api.integration.oscli.fixtures \
    import CinderCLI_IntegrationFixture


@DataDrivenFixture
class CinderCLI_SnapshotSmoke(CinderCLI_IntegrationFixture):

    @data_driven_test(BlockstorageDatasets.volume_types())
    def ddtest_snapshot_create_and_delete(
            self, volume_type_name, volume_type_id):

        # Setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        volume = self.volumes.behaviors.create_available_volume(
            size=size, volume_type=volume_type_id)
        self.addCleanup(self.cinder.client.delete, volume.id_)

        # Test create response
        display_name = self.random_snapshot_name()
        display_description = "Snapshot_Description"

        resp = self.cinder.client.snapshot_create(
            volume.id_, display_name=display_name,
            display_description=display_description)

        self.assertIsNotNone(
            resp.entity, 'Could not parse snapshot-create output')

        snapshot = resp.entity

        self.assertEqual(
            snapshot.display_name, display_name,
            "Display name did not match expected display name")
        self.assertEqual(
            snapshot.display_description, display_description,
            "Display description did not match expected display description")
        self.assertEqual(
            str(snapshot.size), str(volume.size),
            "Snapshot size '{0}' did not match source volume size '{1}'"
            .format(snapshot.size, volume.size))
        self.assertEqual(
            snapshot.volume_id, volume.id_,
            "Volume id did not match source volume id")
        self.assertIn(
            snapshot.status,
            [SnapshotStatuses.AVAILABLE, SnapshotStatuses.CREATING],
            "Snapshot created with unexpected status: {0}".format(
                snapshot.status))

        # Wait for snapshot to attain 'available' status
        snapshot_timeout = \
            self.volumes.behaviors.calculate_snapshot_create_timeout(
                volume.size)

        self.volumes.behaviors.wait_for_snapshot_status(
            snapshot.id_, SnapshotStatuses.AVAILABLE, snapshot_timeout)

        # Make sure snapshot progress is at 100%
        resp = self.cinder.client.snapshot_show(snapshot.id_)
        self.assertIsNotNone(
            resp.entity, 'Could not parse snapshot-show output')
        snapshot = resp.entity
        self.assertEqual(
            snapshot.progress, '100%',
            "Snapshot attained 'AVAILABLE' status, but progress is not 100%")

        # Delete Snapshot
        resp = self.cinder.client.snapshot_delete(snapshot.id_)
        self.assertEqual(
            resp.return_code, 0, 'Could not delete snapshot')
