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
from cloudroast.blockstorage.volumes_api.integration.compute.fixtures import \
    ComputeIntegrationTestFixture


class VolumeCloningIntegrationSmokeTests(ComputeIntegrationTestFixture):

    @classmethod
    def setUpClass(cls):
        super(VolumeCloningIntegrationSmokeTests, cls).setUpClass()
        cls.setup_server_and_attached_volume_with_data()

    def test_source_volume_data_on_volume_clone(self):

        # Unmount and detach the original volume
        self.unmount_and_detach_test_volume()

        # Verify that the volume detaches properly
        self.compute.volume_attachments.behaviors.\
            verify_volume_status_progression_during_detachment(
                self.test_volume.id_)

        # Create a clone of the test volume
        self.volume_clone = self.volumes.behaviors.create_available_volume(
            self.test_volume.size, self.test_volume.volume_type,
            source_volid=self.test_volume.id_)
        assert self.volume_clone is not None, "Unable to clone volume"

        # Attach clone to server(self):
        self.clone_attachment = self.attach_volume_and_get_device_info(
            self.server_conn, self.test_server.id, self.volume_clone.id_)
        assert self.clone_attachment is not None, "Unable to attach clone"

        # mount volume clone on server
        self.clone_mount_point = self.server_conn.generate_mountpoint()
        self.mount_attached_volume(
            self.server_conn, self.clone_attachment.os_disk_device_name,
            mount_point=self.clone_mount_point)

        # verify data on volume clone
        md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.clone_mount_point, self.written_filename)
        assert md5hash is not None, "Unable to hash file on mounted volume"
        assert self.original_md5hash == md5hash, (
            "Original hash {0} and cloned volume hash {1] for file '{2}' did "
            "not match".format(
                self.original_hash, md5hash, self.written_filename))

    def tearDown(self):
        if hasattr(self, 'clone_attachment'):
            self.unmount_attached_volume(
                self.server_conn, self.clone_attachment.os_disk_device_name)
            self.volume_attachments.behaviors.delete_volume_attachment(
                self.clone_attachment.id_, self.test_server.id)
        super(VolumeCloningIntegrationSmokeTests, self).tearDown()
