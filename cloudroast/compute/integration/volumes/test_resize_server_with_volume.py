"""
Copyright 2015 Rackspace

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

import unittest
from unittest.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudcafe.blockstorage.volumes_api.v1.models import statuses
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


flavors_config = FlavorsConfig()
resize_enabled = flavors_config.resize_enabled


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(ResizeServerVolumeIntegrationTest(
        "test_resize_server_and_confirm"))
    suite.addTest(ResizeServerVolumeIntegrationTest(
        "test_volume_attached_after_resize"))
    return suite


@unittest.skipUnless(
    resize_enabled, 'Resize not enabled for this flavor class.')
class ResizeServerVolumeIntegrationTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create a server from server behaviors.
        """
        super(ResizeServerVolumeIntegrationTest, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        server_response = cls.server_behaviors.create_active_server(
            key_name=cls.key.name)
        cls.server = server_response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.volume = cls.blockstorage_behavior.create_available_volume(
            size=cls.volume_size,
            volume_type=cls.volume_type,
            timeout=cls.volume_create_timeout)
        cls.resources.add(cls.volume.id_,
                          cls.blockstorage_client.delete_volume)
        cls.volume_attachments_client.attach_volume(
            cls.server.id, cls.volume.id_)
        cls.blockstorage_behavior.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.IN_USE,
            timeout=cls.volume_create_timeout)

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that teardown the necessary resources for testing.

        The following resources are released during this teardown:
            - Deletes the volume attached to the server.
        """
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.blockstorage_behavior.wait_for_volume_status(
            cls.volume.id_, statuses.Volume.AVAILABLE,
            cls.volume_delete_timeout)
        super(ResizeServerVolumeIntegrationTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_resize_server_and_confirm(self):
        """
        Verify that you can resize the server.

        Will resize the server with the alternate flavor and waits for
        the server to reach a "VERIFY_RESIZE" state.  Then will call confirm
        resize and waits for the server to be in an "ACTIVE" state.
        """
        self.resize_resp = self.servers_client.resize(
            self.server.id, self.flavor_ref_alt)
        self.server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.confirm_resize_resp = self.servers_client.confirm_resize(
            self.server.id)
        self.server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)

    @tags(type='smoke', net='no')
    def test_volume_attached_after_resize(self):
        """
        Verify that the volume stayed attached during resize.

        Will get the volume info by volume id and then verify that the
        volume is an "in-use" state.

        The following assertions occur:
            - The volume status is "in-use".
        """
        volume_after_rebuild = self.blockstorage_client.get_volume_info(
            self.volume.id_).entity
        self.assertEqual(volume_after_rebuild.status, 'in-use')
