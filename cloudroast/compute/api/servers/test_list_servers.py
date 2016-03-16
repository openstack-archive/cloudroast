"""
Copyright 2016 Rackspace

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
import cloudcafe.compute.common.exceptions as exceptions
from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaImageStatusTypes
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ServerListTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during the setup
            - Networking, default network from ComputeFixture
            - 2 servers with the same configuration (waits for active)
            - Image creation from first server (waits for active)
            - 3rd server from image created in step above (waits for active)
        """
        super(ServerListTest, cls).setUpClass()

        networks = None
        if cls.servers_config.default_network:
            networks = [{'uuid': cls.servers_config.default_network}]

        cls.name = rand_name("server")
        first_response = cls.servers_client.create_server(
            name=cls.name, image_ref=cls.image_ref,
            flavor_ref=cls.flavor_ref, networks=networks).entity
        cls.resources.add(first_response.id,
                          cls.servers_client.delete_server)

        cls.name = rand_name("server")
        second_response = cls.servers_client.create_server(
            name=cls.name, image_ref=cls.image_ref,
            flavor_ref=cls.flavor_ref, networks=networks).entity
        cls.resources.add(second_response.id,
                          cls.servers_client.delete_server)

        cls.server = cls.server_behaviors.wait_for_server_status(
            first_response.id, NovaServerStatusTypes.ACTIVE).entity
        cls.second_server = cls.server_behaviors.wait_for_server_status(
            second_response.id, NovaServerStatusTypes.ACTIVE).entity

        # Create a unique image
        other_image_name = rand_name('image')
        resp = cls.servers_client.create_image(
            cls.second_server.id, other_image_name)
        assert resp.status_code == 202
        cls.other_image_id = cls.parse_image_id(resp)
        cls.resources.add(cls.other_image_id, cls.images_client.delete_image)

        cls.image_behaviors.wait_for_image_status(
            cls.other_image_id, NovaImageStatusTypes.ACTIVE)

        cls.name = rand_name("server")
        third_response = cls.servers_client.create_server(
            name=cls.name, image_ref=cls.other_image_id,
            flavor_ref=cls.flavor_ref_alt, networks=networks).entity
        cls.resources.add(third_response.id,
                          cls.servers_client.delete_server)
        cls.third_server = cls.server_behaviors.wait_for_server_status(
            third_response.id, NovaServerStatusTypes.ACTIVE).entity

    @tags(type='smoke', net='no')
    def test_get_server(self):
        """
        Return the full details of a single server.

        It will take the first server created in setup and pulls the server
        details back; nothing is modified during this test.

        The following assertions occur:
            - 200 status code from http call.
            - Server name matches config.
            - Image id matches config.
            - Flavor id matches config.
        """
        server_info_response = self.servers_client.get_server(self.server.id)
        server_info = server_info_response.entity
        self.assertEqual(200, server_info_response.status_code)
        self.assertEqual(self.server.name, server_info.name,
                         msg="Server name did not match")
        self.assertEqual(self.image_ref, server_info.image.id,
                         msg="Image id did not match")
        self.assertEqual(self.flavor_ref, server_info.flavor.id,
                         msg="Flavor id did not match")

    @tags(type='smoke', net='no')
    def test_list_servers(self):
        """
        All 3 servers created in setup should be returned.

        The following assertions occur:
            - 200 status code from http call.
            - Server 1,2 and 3 are in the list returned in the response.
        """
        list_servers_response = self.servers_client.list_servers()
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), servers_list)
        self.assertIn(self.second_server.min_details(), servers_list)
        self.assertIn(self.third_server.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_all_tenants(self):
        """
        Verify that all tenants cannot be retrieved using a non-admin account.

        This will call the list_servers passing an integer value of 1 to the
        all_tenants parameter. This should return a 403 response code.

        The following assertions occur:
            - The response code returned is not a 403
        """
        all_tenants = 1
        params = all_tenants
        with self.assertRaises(exceptions.Forbidden):
            self.servers_client.list_servers(all_tenants=params)

    @tags(type='smoke', net='no')
    def test_list_servers_with_detail(self):
        """
        Details list of servers and verify they are in the list returned.

        After the list_servers_with_details is called, it grabs the entity,
        then iterates through the details and puts all the server ids into an
        array which then will look for the server ids in the list.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 id is contained in the list.
            - Server 2 id is contained in the list.
            - Server 3 id is contained in the list.
        """
        list_response = self.servers_client.list_servers_with_detail()
        list_servers_detail = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in list_servers_detail:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.second_server.id, servers_list)
        self.assertIn(self.third_server.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_server_details_using_marker(self):
        """
        The list of servers should start from the provided marker (server id).

        This gets all servers current in then compute instance with the call
        list_serveris_with_details. Grabs the first item in the list, takes
        the id and then calls the same list server with details with
        parameters being the id of the first server it just returned to
        ensure that the same server is not returned.

        The following assertions occur:
            - 200 status code from the http call.
            - The first server returned is not in the new list of entities.
        """
        list_response = self.servers_client.list_servers_with_detail()
        list_server_detail = list_response.entity
        first_server = list_server_detail[0]

        # Verify the servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers_with_detail(
            marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertNotIn(first_server, filtered_servers.entity)

    @tags(type='positive', net='no')
    def test_list_servers_using_marker(self):
        """
        The list of servers should start from the provided marker (server id).

        This gets all servers current in then compute instance with the call
        list_servers. Grabs the first item in the list, takes the id and then
        calls the same list server with details with parameters being the id
        of the first server it just returned to ensure that the same server
        is not returned.

        The following assertions occur:
            - 200 status code from the http call.
            - The first server returned is not in the new list of entities.
        """
        list_server_info_response = self.servers_client.list_servers()
        list_server_info = list_server_info_response.entity
        first_server = list_server_info[0]

        # Verify the servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers(
            marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertNotIn(first_server, filtered_servers.entity)

    @tags(type='positive', net='no')
    def test_list_server_with_detail_limit_results(self):
        """
        Verify the expected number of servers (1) are returned.

        This will call the list_servers_with_detail with a parameter of an
        1 (integer) being passed into the limit param. This should return
        only 1 entry in the list.

        The following assertions occur:
            - The len of the list returned is equal to the limit (1).
        """
        limit = 1
        params = limit
        response = self.servers_client.list_servers_with_detail(limit=params)
        servers = response.entity
        self.assertEqual(
            limit, len(response.entity),
            msg="({0}) servers returned. Expected {1} servers.".format(
                len(servers), limit))

    @tags(type='positive', net='no')
    def test_list_servers_with_detail_all_tenants(self):
        """
        Verify that all tenants cannot be retrieved using a non-admin account.

        This will call the list_servers_with_detail passing an integer value of
        1 to the all_tenants parameter. This should return a 403 response code.

        The following assertions occur:
            - The response code returned is not a 403
        """
        all_tenants = 1
        params = all_tenants
        with self.assertRaises(exceptions.Forbidden):
            self.servers_client.list_servers_with_detail(all_tenants=params)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_image(self):
        """
        Filter the list of servers by image that created the first 2 servers.

        This will call the list_servers with the image which is the primary
        image in the setup.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 and 2 are in the list.
            - Server 3 is NOT in the list.
        """
        params = self.image_ref
        list_servers_response = self.servers_client.list_servers(image=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertIn(self.server.min_details(), servers_list)
        self.assertIn(self.second_server.min_details(), servers_list)
        self.assertNotIn(self.third_server.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_flavor(self):
        """
        Filter the list of servers by flavor that created the 3rd server.

        This will call the list_servers with the alternate flavor that created
        the third server.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 and 2 are not in the list.
            - Server 3 is in the list.
        """
        params = self.flavor_ref_alt
        list_servers_response = self.servers_client.list_servers(flavor=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertNotIn(self.server.min_details(), servers_list)
        self.assertNotIn(self.second_server.min_details(), servers_list)
        self.assertIn(self.third_server.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_name(self):
        """
        Filter the list of servers by name, using server 1's name.

        This will call the list_servers with the server name that was created
        at startup.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 is in the list.
            - Server 2 and 3 are not in the list.
        """
        params = self.server.name
        list_servers_response = self.servers_client.list_servers(name=params)
        servers_list = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), servers_list)
        self.assertNotIn(self.second_server.min_details(), servers_list)
        self.assertNotIn(self.third_server.min_details(), servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_status(self):
        """
        Filter the list of servers by server status of active.

        This will call the list_servers with the status of active expecting
        all servers to be returned.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1, 2 and 3 are in the list.
        """
        params = 'active'
        list_servers_response = self.servers_client.list_servers(status=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertIn(self.server.min_details(), list_servers)
        self.assertIn(self.second_server.min_details(), list_servers)
        self.assertIn(self.third_server.min_details(), list_servers)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_changes_since(self):
        """
        Filter the list of servers by changes-since.

        This will call the list_servers with the expectation of all servers
        being returned in the list. The list will be of all servers but will
        go through then entries and pull the id into a list to compare against.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1, 2 and 3's ids are in the generated list.
        """
        params = self.server.created

        servers = self.servers_client.list_servers(changes_since=params)
        self.assertEqual(200, servers.status_code)
        servers_ids_list = []
        for i in servers.entity:
            servers_ids_list.append(i.id)
        self.assertIn(self.server.id, servers_ids_list)
        self.assertIn(self.second_server.id, servers_ids_list)
        self.assertIn(self.third_server.id, servers_ids_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_image(self):
        """
        Filter the list of servers with details by image.

        This will call the list_servers_with_detail with the image which is
        the primary image in the setup.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 and 2 are in the list.
            - Server 3 is NOT in the list.
        """
        params = self.image_ref
        list_response = self.servers_client.list_servers_with_detail(
            image=params)
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in list_response.entity:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.second_server.id, servers_list)
        self.assertNotIn(self.third_server.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_flavor(self):
        """
        Filter the list of servers with details by flavor.

        This will call the list_servers_with_detail with the alternate flavor
        that created the third server.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 and 2 are not in the list.
            - Server 3 is in the list.
        """
        params = self.flavor_ref_alt
        list_response = self.servers_client.list_servers_with_detail(
            flavor=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)

        self.assertNotIn(self.server, filtered_servers)
        self.assertNotIn(self.second_server, filtered_servers)
        self.assertIn(self.third_server, filtered_servers)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_name(self):
        """
        Filter the list of servers with detail by name.

        This will call the list_servers_with_details with the server name that
        was created at startup. Then it will get the details of the first
        server created during test set up and use that information to validate
        that a detailed list of servers respects the server name filter.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1 is in the list.
            - Server 2 and 3 are not in the list.
        """
        params = self.server.name
        list_response = self.servers_client.list_servers_with_detail(
            name=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)

        server_under_test = self.servers_client.get_server(
            self.server.id).entity

        self.assertIn(server_under_test, filtered_servers)
        self.assertNotIn(self.second_server, filtered_servers)
        self.assertNotIn(self.third_server, filtered_servers)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_status(self):
        """
        Filter the list of servers with details by server status of active.

        This will call the list_servers_with_detail with the status of active
        expecting all servers to be returned.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1, 2 and 3 are in the list.
        """
        params = 'active'
        list_response = self.servers_client.list_servers_with_detail(
            status=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.second_server.id, servers_list)
        self.assertIn(self.third_server.id, servers_list)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_changes_since(self):
        """
        Filter the list of servers with details by changes-since.

        This will call the list_servers_with_detail with the expectation of
        all servers being returned in the list. The list will be of all
        servers but will go through the entries and pull the id into a list
        to compare against.

        The following assertions occur:
            - 200 status code from the http call.
            - Server 1, 2 and 3's ids are in the generated list.
        """
        params = self.server.created

        # Filter the detailed list of servers by changes-since
        list_response = self.servers_client.list_servers_with_detail(
            changes_since=params)
        filtered_servers = list_response.entity
        self.assertEqual(200, list_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertIn(self.server.id, servers_list)
        self.assertIn(self.second_server.id, servers_list)
        self.assertIn(self.third_server.id, servers_list)
