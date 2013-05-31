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
from cloudroast.blockstorage.v1.integration.fixtures import \
    ComputeBlockstorageIntegrationTestFixture


class ComputeIntegrationSmoke(ComputeBlockstorageIntegrationTestFixture):

    def test_attach_volume_to_server(self):
        test_server = self.new_server(add_cleanup=True)
        test_volume = self.new_volume(add_cleanup=True)

        # Test attach volume to server
        attachment = self.volume_attachments.behaviors.attach_volume_to_server(
            test_server.id, test_volume.id_)
        assert attachment is not None, 'Could not verify attachment'

        # Test list server volume attachments
        resp = \
            self.volume_attachments.client.get_server_volume_attachments(
                test_server.id)
        assert resp.ok, 'Info call failed in test list server vol attachments'
        assert resp.entity is not None, 'Unable to deserialize attachment info response'
        attachments = resp.entity
        assert attachment in attachments, 'Could not verify that attachment was listed for server'

        # Test get volume attachment details
        resp = self.volume_attachments.client.get_volume_attachment_details(
            attachment.id_, test_server.id)
        assert resp.ok, 'Info call failed in vol attach details test'
        assert resp.entity is not None, 'Unable to deserialize attachment info response'
        attachment_details = resp.entity
        self.assertDictEqual(vars(attachment), vars(attachment_details))

        # Test volume attachment delete
        resp = self.volume_attachments.client.delete_volume_attachment(
            attachment.id_, test_server.id)

        assert resp.ok, 'Delete call failed in test volume attach delete test'
