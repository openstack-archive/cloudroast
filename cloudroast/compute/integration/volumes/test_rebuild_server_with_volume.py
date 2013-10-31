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

from unittest2.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import BlockstorageIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(RebuildServerVolumeIntegrationTest(
        "test_rebuild_server"))
    suite.addTest(RebuildServerVolumeIntegrationTest(
        "test_volume_detached_after_rebuild"))
    suite.addTest(RebuildServerVolumeIntegrationTest(
        "test_reattach_volume_after_rebuild"))
    return suite


class RebuildServerVolumeIntegrationTest(BlockstorageIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(RebuildServerVolumeIntegrationTest, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        response = cls.server_behaviors.create_active_server(
            key_name=cls.key.name)
        cls.server = response.entity
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
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

    @tags(type='smoke', net='no')
    def test_rebuild_server(self):
        self.name = rand_name('testserver')
        self.password = 'R3builds3ver'

        self.rebuilt_server_response = self.servers_client.rebuild(
            self.server.id, self.image_ref_alt, name=self.name,
            admin_pass=self.password, key_name=self.key.name)
        self.server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)

    @tags(type='smoke', net='no')
    def test_volume_detached_after_rebuild(self):
        volume_after_rebuild = self.storage_client.get_volume_info(
            self.volume.id_).entity
        self.assertEqual(volume_after_rebuild.status, 'available')

    @tags(type='smoke', net='no')
    def test_reattach_volume_after_rebuild(self):
        self.volume_attachments_client.attach_volume(
            self.server.id, self.volume.id_)
        self.storage_behavior.wait_for_volume_status(
            self.volume.id_, 'in-use',
            timeout=self.volume_status_timeout,
            wait_period=self.poll_frequency)
