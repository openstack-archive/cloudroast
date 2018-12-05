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
from qe_coverage.opencafe_decorators import tags, unless_coverage
from cafe.drivers.unittest.suite import OpenCafeUnittestTestSuite
from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import ComputeIntegrationTestFixture


def load_tests(loader, standard_tests, pattern):
    suite = OpenCafeUnittestTestSuite()
    suite.addTest(VolumeAttachmentsAPISmoke("test_attach_volume_to_server"))
    suite.addTest(
        VolumeAttachmentsAPISmoke("test_list_server_volume_attachments"))
    suite.addTest(
        VolumeAttachmentsAPISmoke("test_get_volume_attachment_details"))
    suite.addTest(VolumeAttachmentsAPISmoke("test_volume_attachment_delete"))

    return suite


class VolumeAttachmentsAPISmoke(ComputeIntegrationTestFixture):
    """Tests attaching a single volume to a server"""

    @unless_coverage
    @classmethod
    def setUpClass(cls):
        super(VolumeAttachmentsAPISmoke, cls).setUpClass()
        cls.test_server = cls.new_server()
        cls.test_volume = cls.new_volume(add_cleanup=False)
        cls.test_attachment = \
            cls.volume_attachments.behaviors.attach_volume_to_server(
                cls.test_server.id, cls.test_volume.id_)

        if cls.test_attachment is None:
            cls.assertClassSetupFailure(
                "Could not attach volume {0} to server {1}".format(
                    cls.test_volume.id_, cls.test_server.id))

        cls.addClassCleanup(
            cls.volume_attachments.client.delete_volume_attachment,
            cls.test_attachment.id_)
        cls.addClassCleanup(
            cls.volume_attachments.behaviors.
            verify_volume_status_progression_during_detachment,
            cls.test_volume.id_, raise_on_error=False)
        cls.addClassCleanup(
            cls.volumes.client.delete_volume, cls.test_volume.id_)

    @unless_coverage
    def setUp(self):
        super(VolumeAttachmentsAPISmoke, self).setUp()

    @tags('integration', 'smoke', 'positive')
    def test_attach_volume_to_server(self):
        # Note: For the attach test, I rely on the behavior that waits for
        # attachment propagation and status changes because in a smoke test,
        # all I care about is that the attachment eventually works
        self.assertEqual(
            self.test_attachment.server_id, self.test_server.id,
            "Attachment's Server id and actual Server id did not match")

        self.assertEqual(
            self.test_attachment.volume_id, self.test_volume.id_,
            "Attachment's Volume id and actual Volume id did not match")

    @tags('integration', 'smoke', 'positive')
    def test_list_server_volume_attachments(self):
        resp = self.volume_attachments.client.get_server_volume_attachments(
            self.test_server.id)

        self.assertResponseDeserializedAndOk(resp)
        attachments = resp.entity
        self.assertIn(
            self.test_attachment, attachments,
            "Unable to locate volume attachment {0} in list of server {1}'s"
            " volume attachments".format(
                self.test_attachment.id_, self.test_server.id))

    @tags('integration', 'smoke', 'positive')
    def test_get_volume_attachment_details(self):
        resp = self.volume_attachments.client.get_volume_attachment_details(
            self.test_attachment.id_, self.test_server.id)

        self.assertResponseDeserializedAndOk(resp)
        attachment_details = resp.entity
        self.assertDictEqual(
            vars(self.test_attachment), vars(attachment_details))

    @tags('integration', 'smoke', 'positive')
    def test_volume_attachment_delete(self):
        resp = self.volume_attachments.client.delete_volume_attachment(
            self.test_attachment.id_, self.test_server.id)
        self.assertExactResponseStatus(resp, 202)

    @unless_coverage
    @classmethod
    def tearDownClass(cls):
        super(VolumeAttachmentsAPISmoke, cls).tearDownClass()

    @unless_coverage
    def tearDown(self):
        super(VolumeAttachmentsAPISmoke, self).tearDown()