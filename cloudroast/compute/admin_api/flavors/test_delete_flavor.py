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
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import ComputeAdminFixture


class DeleteFlavorTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the neccesary resources for testing

        The following resources are created during this setup:
            - A public flavor with a name starting with 'flavor', 64MB of RAM,
              1 vcpu, 10GB disk space
        The created flavor is then deleted.
        """
        super(DeleteFlavorTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=True).entity
        cls.admin_flavors_client.delete_flavor(cls.flavor.id)

    @tags(type='positive', net='no')
    def test_get_deleted_flavor(self):
        """
        Perform actions that allow for the cleanup of any generated resources

        Validate that the detailed information of the flavor created and
        deleted during setup can be accessed.
        """
        self.admin_flavors_client.get_flavor_details(self.flavor.id)

    @tags(type='negative', net='no')
    def test_create_server_from_deleted_flavor(self):
        """
        Test that a deleted flavor cannot be used to create an instance

        Validate that you receive an 'Bad Request' error when a user attempts
        to create an instance with a flavor created and deleted during setup.

        The following assertions occur:
            - The create instance requests raises a 'Bad Request' error
        """
        with self.assertRaises(BadRequest):
            self.server_behaviors.create_active_server(
                flavor_ref=self.flavor.id)

    @tags(type='negative', net='no')
    def test_delete_deleted_flavor_fails(self):
        """
        Test that a previously deleted flavor cannot be deleted

        Validate that you receive an 'Item Not Found' error when a user
        attempts to delete the flavor that was created and deleted during
        setup.

        The following assertions occur:
            - The delete flavor requests raises a 'Item not Found' error
        """
        with self.assertRaises(ItemNotFound):
            self.admin_flavors_client.delete_flavor(self.flavor.id)
