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
from cloudroast.compute.fixtures import ComputeAdminFixture


class CreateFlavorTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the neccesary resources for testing

        The following resources are created during this setup:
            - A public flavor with a name starting with 'flavor', 64MB of RAM,
              1 vcpu, 10GB disk space
        """
        super(CreateFlavorTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=True).entity

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the cleanup of any generated resources

        The following resources are deleted during this tear down:
            - The public flavor created in the setup
        """
        super(CreateFlavorTest, cls).tearDownClass()
        cls.admin_flavors_client.delete_flavor(cls.flavor.id)

    @tags(type='positive', net='no')
    def test_create_server_from_new_flavor(self):
        """
        Test that a newly created flavor can be used to create an instance

        Create an instance using the flavor id created during Setup. Wait for
        that instance to become active.
        This test will be successful if:
            - The instance successfully builds in less than configured timeout
              time
        """
        resp = self.server_behaviors.create_active_server(
            flavor_ref=self.flavor.id)
        server = resp.entity
        self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_create_flavor_with_duplicate_id(self):
        """
        Test that a new flavor cannot be created with an in use flavor id

        Validate that you receive an 'Action in Progress' error when a user
        attempts to create a flavor with a previously used ID value.
        This test will be successful if:
            - The create flavor request raises a 'Action in Progress' error
        """
        with self.assertRaises(ActionInProgress):
            self.admin_flavors_client.create_flavor(
                name=self.flavor_name, ram='64', vcpus='1', disk='10',
                id=self.flavor.id, is_public=True)
