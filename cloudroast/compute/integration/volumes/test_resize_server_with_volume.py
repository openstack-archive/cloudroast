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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


flavors_config = FlavorsConfig()
resize_enabled = flavors_config.resize_enabled


@unittest.skipUnless(
    resize_enabled, 'Resize not enabled for this flavor class.')
class ResizeServerVolumeIntegrationTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(ResizeServerVolumeIntegrationTest, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        server_response = cls.server_behaviors.create_active_server(
            key_name=cls.key.name)
        cls.server = server_response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)
        cls.volume = cls.storage_behavior.create_available_volume(
            'test-volume', cls.volume_size, cls.volume_type,
            timeout=cls.volume_status_timeout)
        cls.resources.add(cls.volume.id_,
                          cls.storage_client.delete_volume)
        cls.volume_attachments_client.attach_volume(
            cls.server.id, cls.volume.id_)
        cls.storage_behavior.wait_for_volume_status(
            cls.volume.id_, 'in-use',
            timeout=cls.volume_status_timeout,
            wait_period=cls.poll_frequency)

    @classmethod
    def tearDownClass(cls):
        cls.volume_attachments_client.delete_volume_attachment(
            cls.volume.id_, cls.server.id)
        cls.storage_behavior.wait_for_volume_status(
            cls.volume.id_, 'available',
            timeout=cls.volume_status_timeout,
            wait_period=cls.poll_frequency)
        super(ResizeServerVolumeIntegrationTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_resize_server_and_confirm(self):
        self.resize_resp = self.servers_client.resize(
            self.server.id, self.flavor_ref_alt)
        self.server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.confirm_resize_resp = self.servers_client.confirm_resize(
            self.server.id)
        self.server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)
