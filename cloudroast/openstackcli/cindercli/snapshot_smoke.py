from cafe.drivers.unittest.decorators import \
    DataDrivenFixture, data_driven_test

from cloudroast.openstackcli.cindercli.fixtures import \
    CinderCLI_Datasets, CinderTestFixture

from cloudcafe.blockstorage.volumes_api.v1.models.statuses import \
    Snapshot as SnapshotStatuses


@DataDrivenFixture
class CinderCLI_SnapshotSmoke(CinderTestFixture):

    @data_driven_test(CinderCLI_Datasets.volume_types())
    def ddtest_snapshot_create(self, volume_type_name, volume_type_id):
        """Snapshots take a relative eternity to test compared to volumes.
        To facilitate this smoke test running as quickly as possible,
        it is a composite of logic that would normally be broken up into
        several different tests."""

        # Setup
        volume = self.cinder.cli.behaviors.create_available_volume(
            type_=volume_type_id)
        self.addCleanup(self.cinder.cli.client.delete_volume, volume.id_)

        # Test create response
        display_name = self.random_snapshot_name()
        display_description = "Snapshot_Description"

        resp = self.cinder.cli.client.create_snapshot(
            volume.id_, display_name=display_name,
            display_description=display_description)

        self.assertIsNotNone(
            resp.entity, 'Could not parse snapshot-create output')

        snapshot = resp.entity

        self.assertEquals(
            snapshot.display_name, display_name,
            "Display name did not match expected display name")
        self.assertEquals(
            snapshot.display_description, display_description,
            "Display description did not match expected display description")
        self.assertEquals(
            snapshot.size, volume.size,
            "Size did not match source volume size")
        self.assertEquals(
            snapshot.volume_id, volume.id_,
            "Volume id did not match source volume id")
        self.assertIn(
            snapshot.status,
            [SnapshotStatuses.AVAILABLE, SnapshotStatuses.CREATING],
            "Snapshot created with unexpected status: {0}".format(
                snapshot.status))

        # Wait for snapshot to attain 'available' status
        snapshot_timeout = \
            self.cinder.api.behaviors.calculate_snapshot_create_timeout(
                volume.size)

        self.cinder.cli.behaviors.wait_for_snapshot_status(
            snapshot.id_, SnapshotStatuses.AVAILABLE, snapshot_timeout)

        # Make sure snapshot progress is at 100%
        resp = self.cinder.cli.client.show_snapshot(snapshot.id_)
        self.assertIsNotNone(
            resp.entity, 'Could not parse snapshot-show output')
        snapshot = resp.entity
        self.assertEquals(
            snapshot.progress, '100%',
            "Snapshot attained 'AVAILABLE' status, but progress is not 100%")
