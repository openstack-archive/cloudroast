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
from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import ComputeIntegrationTestFixture


class VolumeSnapshotIntegrationSmokeTests(ComputeIntegrationTestFixture):

    @classmethod
    def setUpClass(cls):
        super(VolumeSnapshotIntegrationSmokeTests, cls).setUpClass()

        # Build new server using configured defaults
        cls.test_server = cls.new_server(add_cleanup=True)

        # Set remote instance client up
        cls.server_conn = cls.connect_to_instance(cls.test_server)
        cls.volume_mount_point = cls.server_conn.generate_mountpoint()
        cls.test_volume = cls.new_volume()
        cls.test_attachment = cls.attach_volume_and_get_device_info(
            cls.server_conn, cls.test_server.id, cls.test_volume.id_)

    def test_restore_snapshot_of_written_volume_and_verify_data(self):
        # Format Volume
        self.format_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name)

        # Mount Volume
        self.mount_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name,
            mount_point=self.volume_mount_point)

        # Write data to volume
        resp = self.create_remote_file(
            self.server_conn, self.volume_mount_point, "testfile")
        assert resp is not None, (
            "Could not verify writability of attached volume")

        # Save written file md5sum
        self.original_md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.volume_mount_point, "testfile")
        assert self.original_md5hash is not None, (
            "Unable to hash file on mounted volume")

        # Make the fs write cached data to disk before unmount.
        self.server_conn.filesystem_sync()

        # Unmount original volume
        self.unmount_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name)

        # Snapshot unattached used volume
        self.test_snapshot = self.new_snapshot(
            self.test_volume.id_, add_cleanup=False)
        self.addCleanup(
            self.volumes.behaviors.delete_snapshot_confirmed,
            self.test_snapshot.id_)

        # Restore snapshot to new volume
        self.restored_snapshot_volume = \
            self.volumes.behaviors.create_available_volume(
                self.test_volume.size, self.test_volume.volume_type,
                self.random_snapshot_name(), source_volid=self.test_volume.id_)
        self.addCleanup(
            self.volumes.behaviors.delete_volume_confirmed,
            self.restored_snapshot_volume.id_)

        # Attach new volume to server
        self.new_volume_mount_point = self.server_conn.generate_mountpoint()
        self.restored_volume_attachment = \
            self.attach_volume_and_get_device_info(
                self.server_conn, self.test_server.id,
                self.restored_snapshot_volume.id_)

        # Mount new volume on the server
        self.mount_attached_volume(
            self.server_conn,
            self.restored_volume_attachment.os_disk_device_name,
            mount_point=self.volume_mount_point)

        # Verify data on restored volume
        new_md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.volume_mount_point, "testfile")
        assert new_md5hash is not None, (
            "Unable to hash file on mounted volume")
        assert new_md5hash == self.original_md5hash, (
            "Unable to hash file on mounted volume")
