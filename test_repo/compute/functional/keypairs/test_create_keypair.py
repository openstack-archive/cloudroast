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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.exceptions import ActionInProgress
from cloudcafe.compute.common.types import InstanceAuthStrategies
from test_repo.compute.fixtures import ComputeFixture


class CreateKeypairTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateKeypairTest, cls).setUpClass()
        cls.name = rand_name("key")
        cls.create_resp = cls.keypairs_client.create_keypair(cls.name)
        cls.keypair = cls.keypairs_client.get_keypair(cls.name).entity
        cls.resources.add(cls.name,
                          cls.keypairs_client.delete_keypair)

    @tags(type='positive', net='no')
    def test_create_keypair_response(self):
        """Verify the response code and contents are correct"""

        # Get the keypair from the original response
        keypair = self.create_resp.entity

        self.assertEqual(self.create_resp.status_code, 200)
        self.assertEqual(keypair.name, self.name)
        self.assertIsNotNone(keypair.public_key)
        self.assertIsNotNone(keypair.fingerprint)

    @tags(type='positive', net='no')
    def test_created_keypair_listed(self):
        """Verify the new key appears in list of keypairs"""

        keypairs_list = self.keypairs_client.list_keypairs().entity

        # Format of keypairs in list differs from the normal keypair model
        # Just check for a keypair by name
        self.assertTrue(any([key for key in keypairs_list
                             if key.name == self.keypair.name]))

    @tags(type='negative', net='no')
    def test_cannot_create_duplicate_keypair(self):
        """Verify a duplicate keypair cannot be created"""
        with self.assertRaises(ActionInProgress):
            self.keypairs_client.create_keypair(self.name)

    @tags(type='positive', net='yes')
    def test_created_server_has_new_keypair(self):
        """Verify the key is injected into a built server"""
        server = self.server_behaviors.create_active_server(
            key_name=self.name).entity
        self.resources.add(server.id, self.servers_client.delete_server)

        # Get the keypair from the original response
        keypair = self.create_resp.entity

        # Verify the authorized_keys file was generated
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, self.servers_config, key=keypair.private_key,
            auth_strategy=InstanceAuthStrategies.KEY)
        self.assertTrue(remote_client.is_file_present(
            '~/.ssh/authorized_keys'))

        # Verify the file contains the expected key
        file_contents = remote_client.get_file_details(
            '~/.ssh/authorized_keys')
        self.assertIn(self.keypair.public_key, file_contents.content)
