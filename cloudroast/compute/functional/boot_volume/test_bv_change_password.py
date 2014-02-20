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

import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import NovaServerStatusTypes as \
    ServerStates
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeFixture as CreateServerFixture
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.blockstorage.config import BlockStorageConfig
compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(hypervisor in [ComputeHypervisors.KVM,
                                ComputeHypervisors.QEMU],
                 'Change password not supported in current configuration.')
class BVChangeServerPasswordTests(CreateServerFixture):

    @classmethod
    def setUpClass(cls):
        super(BVChangeServerPasswordTests, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)

        server_response, cls.volume_id = cls.server_behaviors.boot_volume(
            cls.key)

        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.new_password = "newslice129690TuG72Bgj2"

        # Change password and wait for server to return to active state
        cls.resp = cls.servers_client.change_password(cls.server.id,
                                                      cls.new_password)
        cls.server_behaviors.wait_for_server_status(cls.server.id,
                                                    ServerStates.ACTIVE)

    @tags(type='smoke', net='no')
    def test_change_password_response(self):
        self.assertEqual(202, self.resp.status_code)

    @tags(type='smoke', net='yes')
    def test_can_log_in_with_new_password(self):
        """Verify the admin user can log in with the new password"""
        self.can_log_in_with_new_password(self.server.id, self.new_password,
                                          self.servers_config)

    @tags(type='smoke', net='no')
    def test_password_changed_server_instance_actions(self):
        """
        Verify the correct actions are logged during a password change.
        """
        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the change password action is listed
        self.assertTrue(any(a.action == 'changePassword' for a in actions))
        filtered_actions = [a for a in actions
                            if a.action == 'changePassword']
        self.assertEquals(len(filtered_actions), 1)

        password_action = filtered_actions[0]
        self.validate_instance_action(
            password_action, self.server.id, self.user_config.user_id,
            self.user_config.project_id,
            self.resp.headers['x-compute-request-id'])
