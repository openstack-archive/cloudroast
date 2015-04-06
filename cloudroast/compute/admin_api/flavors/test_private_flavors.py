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


class PrivateFlavorTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A private flavor with a name starting with 'flavor', 64MB of RAM,
              1 vcpu, 10GB disk space
        The configured tenant is granted access to the flavor.
        """
        super(PrivateFlavorTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=False).entity
        cls.admin_flavors_client.add_tenant_access(
            flavor_id=cls.flavor.id, tenant=cls.user_config.tenant_id)

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the cleanup of any generated resources

        The following resources are deleted during this tear down:
            - The private flavor created in the setup
        """
        super(PrivateFlavorTest, cls).tearDownClass()
        cls.admin_flavors_client.delete_flavor(cls.flavor.id)

    @tags(type='positive', net='no')
    def test_create_server_with_private_flavor(self):
        """
        Test that a private flavor can be used to create an instance

        Create an instance using the private flavor id created during Setup.
        Wait for that instance to become active.
        This test will succeed if:
            - An instance is successfully created on the private flavor
        """
        resp = self.server_behaviors.create_active_server(
            flavor_ref=self.flavor.id)
        server = resp.entity
        self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='positive', net='no')
    def test_list_private_flavor(self):
        """
        Test that a private flavor appears in a list of flavors for the tenant

        Get a list of flavors. Validate that the previously created flavor,
        which should be private and the test user should have access to, is
        listed.
        This test will succeed if:
            - The test user is able to receive a detailed list of flavors
            - The private flavor created in setup is found in the list of
              flavors
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertIn(self.flavor, flavors)

    @tags(type='positive', net='no')
    def test_get_private_flavor(self):
        """
        Test that a private server can be viewed by a tenant with permissions

        Validate that the detailed information of the private flavor created
        during setup can be accessed.
        This test will succeed if:
            - The test user is able to receive details about the private flavor
              created during setup.
            - The status code of the request is 200
        """
        response = self.flavors_client.get_flavor_details(self.flavor.id)
        self.assertEqual(response.status_code, 200)


class PrivateFlavorNegativeTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A private flavor with a name starting with 'flavor', 64MB of RAM,
              1 vcpu, 10GB disk space
        """
        super(PrivateFlavorNegativeTest, cls).setUpClass()
        cls.flavor_name = rand_name('flavor')
        cls.flavor = cls.admin_flavors_client.create_flavor(
            name=cls.flavor_name, ram='64', vcpus='1', disk='10',
            is_public=False).entity

    @tags(type='negative', net='no')
    def test_create_server_without_flavor_permissions_fails(self):
        """
        Test that a user without permissions cannot use a private flavor

        Validate that you receive an 'Bad Request' error when you attempt
        to create an instance as a user who does not have access permissions
        for the flavor.
        This test will succeed if:
            - The create instance request raises a 'Bad Request' error
        """
        with self.assertRaises(BadRequest):
            resp = self.server_behaviors.create_active_server(
                flavor_ref=self.flavor.id)
            server = resp.entity
            self.resources.add(server.id, self.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_private_flavor_not_listed_without_permissions(self):
        """
        Test that a user without permissions cannot list a private flavor

        Get a list of servers. Validate that the previously created flavor,
        which should be private and the test user should not have access to, is
        not listed.
        This test will succeed if:
            - The test user is able to receive a detailed list of flavors
            - The private flavor created in setup is not found in the list of
              flavors
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertNotIn(self.flavor, flavors)

    @tags(type='negative', net='no')
    def test_get_private_flavor_fails_without_permissions(self):
        """
        Test that a user without permissions cannot view a private flavor

        Validate that you receive an 'Item Not Found' error when a user
        attempts to access a private flavor on which they have not been
        granted access.
        This test will succeed if:
            - The get flavor details request raises an 'Item Not Found' error
        """
        with self.assertRaises(ItemNotFound):
            self.flavors_client.get_flavor_details(self.flavor.id)
