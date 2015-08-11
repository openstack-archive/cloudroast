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
import time

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

    @classmethod
    def attach_volume_and_get_device_info(
            cls, server_connection, server_id, volume_id):

        # Get list of devices with original volume attached
        original_devices = server_connection.get_all_disk_details()
        cls.fixture_log.debug(
            "Pre-attach devices: {}".format(original_devices))

        attachment = \
            cls.volume_attachments.behaviors.attach_volume_to_server(
                server_id, volume_id)

        assert attachment, "Could not attach volume {0} to server {1}".format(
            volume_id, server_id)

        # Wait for device to show up on VM.  Currently this is expected to
        # be fairly instantaneous; the wait was added to help catch rare
        # erroneous behavior.
        volume_details = None
        current_devices = None
        cls.fixture_log.debug("Waiting for device to show up on server")
        # Note, this timeout is arbitrary and will be removed once this
        # loop is replaced with a StatusProgressionVerifier.
        end = time.time() + 30
        while end > time.time():
            current_devices = server_connection.get_all_disk_details()
            new_devices = [
                d for d in current_devices if d not in original_devices]
            if len(new_devices) > 0:
                volume_details = new_devices
                break
            else:
                cls.fixture_log.debug(
                    "New device hasn't shown up yet, waiting 5 seconds")
                time.sleep(5)
        else:
            cls.fixture_log.debug(
                "Visible devices: {}".format(current_devices))
            raise Exception("Could not verify attached volume assigned device")

        cls.fixture_log.debug("Device found on server")
        cls.fixture_log.debug("Visible devices: {}".format(current_devices))
        setattr(attachment, 'os_disk_details', volume_details)

        os_disk_device_name = \
            volume_details[0].get('Number') or "/dev/{0}".format(
                volume_details[0].get('name'))

        assert os_disk_device_name, (
            "Could not get a unique device name from the OS")
        setattr(attachment, 'os_disk_device_name', os_disk_device_name)

        return attachment

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
            self.test_volume.id_, add_cleanup=True)
        self.addCleanup(
            self.volumes.behaviors.delete_snapshot_confirmed,
            self.test_snapshot.id_)

        # Restore snapshot to new volume
        self.restored_snapshot_volume = \
            self.volumes.behaviors.create_available_volume(
                self.test_volume.size,
                self.test_volume.volume_type,
                self.random_snapshot_name(),
                snapshot_id=self.test_snapshot.id_)
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
