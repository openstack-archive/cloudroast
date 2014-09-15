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
from cafe.drivers.unittest.suite import OpenCafeUnittestTestSuite
from cloudroast.blockstorage.volumes_api.integration.compute import \
    volume_integration_smoke_tests


def load_tests(loader, standard_tests, pattern):
    suite = OpenCafeUnittestTestSuite()
    tests = [
        "test_format_volume_on_server",
        "test_mount_volume_on_server",
        "test_write_data_to_volume_and_generate_md5_hash",
        "test_unmount_used_volume",
        "test_clone_a_volume_with_data_written_to_it",
        "test_attach_volume_clone_to_server",
        "test_mount_volume_clone_on_server",
        "test_verify_data_on_volume_clone",
        "test_unmount_volume_clone",
        "test_detach_unmounted_volume_clone"]
    for t in tests:
        suite.addTest(VolumeCloningIntegrationSmokeTests(t))
    return suite


class VolumeCloningIntegrationSmokeTests(
        volume_integration_smoke_tests.VolumeIntegrationSmokeTests):

    @classmethod
    def setUpClass(cls):
        super(VolumeCloningIntegrationSmokeTests, cls).setUpClass()
        cls.volume_clone = None
        cls.clone_attachment = None
        cls.volume_content_md5hash = None

    def test_write_data_to_volume_and_generate_md5_hash(self):
        r = self.create_remote_file(
            self.server_conn, self.volume_mount_point, "testfile")
        assert r is not None, "Could not verify writability of attached volume"

        self.volume_content_md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.volume_mount_point, "testfile")

    def test_clone_a_volume_with_data_written_to_it(self):
        clone_timeout = self.volumes.behaviors.calculate_volume_clone_timeout(
            self.test_volume.size)
        self.volume_clone = self.volumes.behaviors.create_available_volume(
            self.test_volume.size, self.test_volume.volume_type,
            source_volid=self.test_volume.id_, timeout=clone_timeout)

        self.assertIsNotNone(self.volume_clone)

    def test_attach_volume_clone_to_server(self):
        self.clone_attachment = self.attach_volume_and_get_device_info(
            self.server_conn, self.test_server.id, self.volume_clone.id_)

        self.assertIsNotNone(self.clone_attachment)

    def test_mount_volume_clone_on_server(self):
        self.mount_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name,
            mount_point=self.volume_mount_point)

    def test_verify_data_on_volume_clone(self):
        md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.volume_mount_point, "testfile")
        assert md5hash is not None, "Unable to hash file on mounted volume"
        self.assertEqual(md5hash, )

    def test_unmount_volume_clone(self):
        self.unmount_attached_volume(
            self.server_conn, self.clone_attachment.os_disk_device_name)

    def test_detach_unmounted_volume_clone(self):
        self.volume_attachments.behaviors.delete_volume_attachment(
            self.clone_attachment.id_, self.test_server.id)
