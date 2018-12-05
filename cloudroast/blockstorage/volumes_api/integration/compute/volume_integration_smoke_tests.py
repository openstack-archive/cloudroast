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
from qe_coverage.opencafe_decorators import tags, unless_coverage

from cafe.drivers.unittest.suite import OpenCafeUnittestTestSuite
from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import ComputeIntegrationTestFixture


def load_tests(loader, standard_tests, pattern):
    suite = OpenCafeUnittestTestSuite()
    tests = [
        "test_format_volume_on_server",
        "test_mount_volume_on_server",
        "test_verify_volume_writability",
        "test_verify_volume_readability",
        "test_unmount_used_volume",
        "test_detach_unmounted_volume"]
    for t in tests:
        suite.addTest(VolumeIntegrationSmokeTests(t))
    return suite


class VolumeIntegrationSmokeTests(ComputeIntegrationTestFixture):

    @unless_coverage
    @classmethod
    def setUpClass(cls):
        super(VolumeIntegrationSmokeTests, cls).setUpClass()

        # BUILD NEW SERVER FROM CONFIG
        cls.test_server = cls.new_server(add_cleanup=True)

        # Setup remote instance client
        cls.server_conn = cls.connect_to_instance(cls.test_server)
        cls.volume_mount_point = cls.server_conn.generate_mountpoint()
        cls.test_volume = cls.new_volume()
        cls.test_attachment = cls.attach_volume_and_get_device_info(
            cls.server_conn, cls.test_server.id, cls.test_volume.id_)

        cls.addClassCleanup(
            cls.volume_attachments.behaviors.delete_volume_attachment,
            cls.test_attachment.id_, cls.test_server.id)

    @unless_coverage
    def setUp(self):
        super(VolumeIntegrationSmokeTests, self).setUp()

    @tags('positive', 'integration')
    def test_format_volume_on_server(self):
        self.format_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name)

    @tags('positive', 'integration')
    def test_mount_volume_on_server(self):
        self.mount_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name,
            mount_point=self.volume_mount_point)

    @tags('positive', 'integration')
    def test_verify_volume_writability(self):
        resp = self.create_remote_file(
            self.server_conn, self.volume_mount_point, "testfile")
        assert resp is not None, (
            "Could not verify writability of attached volume")

    @tags('positive', 'integration')
    def test_verify_volume_readability(self):
        md5hash = self.get_remote_file_md5_hash(
            self.server_conn, self.volume_mount_point, "testfile")
        assert md5hash is not None, "Unable to hash file on mounted volume"

    @tags('positive', 'integration')
    def test_unmount_used_volume(self):
        self.unmount_attached_volume(
            self.server_conn, self.test_attachment.os_disk_device_name)

    @tags('positive', 'integration')
    def test_detach_unmounted_volume(self):
        self.volume_attachments.behaviors.delete_volume_attachment(
            self.test_attachment.id_, self.test_server.id)

    @unless_coverage
    def tearDown(self):
        super(VolumeIntegrationSmokeTests, self).tearDown()

    @unless_coverage
    @classmethod
    def tearDownClass(cls):
        super(VolumeIntegrationSmokeTests, cls).tearDownClass()
