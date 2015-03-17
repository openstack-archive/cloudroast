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
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import ComputeFixture


class DeleteKeypairTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing keypair.

        The following resources are created during the setup.
            - Uses keypairs client to create a new keypair.
        """
        super(DeleteKeypairTest, cls).setUpClass()
        cls.name = rand_name("key")
        cls.keypair = cls.keypairs_client.create_keypair(cls.name).entity
        cls.delete_resp = cls.keypairs_client.delete_keypair(cls.name)

    @tags(type='positive', net='no')
    def test_delete_keypair_response(self):
        """
        Verify the response code of the delete call.

        Pulling the response and interrogating the object.

         The following assertions occur:
            - 202 status code from the http call.
        """
        self.assertEqual(self.delete_resp.status_code, 202)

    @tags(type='positive', net='no')
    def test_deleted_keypair_not_listed(self):
        """
        Verify the keypair is no longer returned in the lists.

        Using list_keypairs from the keypairs client,
        it will validate the keypair is no longer returned in the list.

         The following assertions occur:
            - keypair object is not in the list returned
        """
        keypairs_list = self.keypairs_client.list_keypairs().entity
        self.assertNotIn(self.keypair, keypairs_list)

    @tags(type='negative', net='no')
    def test_get_deleted_keypair_fails(self):
        """
        Verify that get keypair by name doesn't work.

        Using the get_keyapir call from keypair client,
        passing in the name as the parameter and expecting ItemNotFound.

         The following assertions occur:
            - Expecting the ItemNotFound Exception to be raised
        """
        with self.assertRaises(ItemNotFound):
            self.keypairs_client.get_keypair(self.name)

    @tags(type='negative', net='no')
    def test_delete_deleted_keypair_fails(self):
        """
        Verify that delete keypair by name doesn't work.

        Using the delete_keypair call from keypair client,
        passing in the name as the parameter and expecting ItemNotFound.

         The following assertions occur:
            - Expecting the ItemNotFound Exception to be raised
        """
        with self.assertRaises(ItemNotFound):
            self.keypairs_client.delete_keypair(self.name)
