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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import ActionInProgress
from cloudcafe.compute.common.types import InstanceAuthStrategies
from cloudroast.compute.fixtures import ComputeFixture


class CreateKeypairTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup:
            - Uses keypairs client to create a new keypair.
            - Uses keypairs client to get keypair by name.
        """
        super(CreateKeypairTest, cls).setUpClass()
        cls.name = rand_name("key")
        cls.create_resp = cls.keypairs_client.create_keypair(cls.name)
        cls.keypair = cls.keypairs_client.get_keypair(cls.name).entity
        cls.resources.add(cls.name,
                          cls.keypairs_client.delete_keypair)

    @tags(type='positive', net='no')
    def test_create_keypair_response(self):
        """
        Verify the response code and contents are correct.

        Pulling the response entity and interrogating the object.

         The following assertions occur:
            - 200 status code from the http call.
            - keypair's name is the same as given.
            - keypair's public key is not empty.
            - keypair's fingerprint is not empty.
        """

        # Get the keypair from the original response
        keypair = self.create_resp.entity

        self.assertEqual(self.create_resp.status_code, 200)
        self.assertEqual(keypair.name, self.name)
        self.assertIsNotNone(keypair.public_key)
        self.assertIsNotNone(keypair.fingerprint)

    @tags(type='positive', net='no')
    def test_created_keypair_listed(self):
        """
        Verify the new key appears in the list of keypairs.

        Using list_keypairs from cloudcafe's keypairs client,
        it pulls the list from the response and then iterates through the
        list to find a keypair with the same name.

         The following assertions occur:
            - True if any keypair in the list has the same name.
        """

        keypairs_list = self.keypairs_client.list_keypairs().entity

        # Format of keypairs in list differs from the normal keypair model
        # Just check for a keypair by name
        self.assertTrue(any([key for key in keypairs_list
                             if key.name == self.keypair.name]))

    @tags(type='negative', net='no')
    def test_cannot_create_duplicate_keypair(self):
        """
        Verify a duplicate keypair cannot be created.

        Using create_keypair from cloudcafe's keypairs client,
        it will try the same call as in setup with the same name
        but it's expecting ActionInProgress exception.

         The following assertions occur:
            - Expecting the ActionInProgress Exception to be raised.
        """
        with self.assertRaises(ActionInProgress):
            self.keypairs_client.create_keypair(self.name)

    @tags(type='positive', net='yes')
    def test_created_server_has_new_keypair(self):
        """
        Verify the key is injected into a built server.

        Will create a new server with the keypair name defined
        in setup.  After calling to get the remote instance to validate
        authorized_keys in the home directory is present and contains
        the keypair's public key.

         The following assertions occur:
            - True if ~/.ssh/authorized_keys is present.
            - If the keypair's public key is in the file contents.
        """
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
