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
from test_repo.compute.fixtures import ComputeFixture


class ServerListTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerListTest, cls).setUpClass()
        # Creation of 3 servers needed for the tests
        active_server_response = cls.server_behaviors.create_active_server()
        cls.server = active_server_response.entity
        cls.resources.add(cls.server.id,
                          cls.servers_client.delete_server)

        active_server_response = cls.server_behaviors.create_active_server()
        cls.server_second = active_server_response.entity
        cls.resources.add(cls.server_second.id,
                          cls.servers_client.delete_server)

        active_server_response = cls.server_behaviors.create_active_server(
            image_ref=cls.image_ref_alt,
            flavor_ref=cls.flavor_ref_alt)
        cls.server_third = active_server_response.entity
        cls.resources.add(cls.server_third.id,
                          cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(ServerListTest, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_get_server(self):
        """Return the full details of a single server"""
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
        """All servers should be returned"""
        list_servers_response = self.servers_client.list_servers()
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertTrue(self.server.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='smoke', net='no')
    def test_list_servers_with_detail(self):
        """Return a detailed list of all servers"""
        list_servers_detail_response = self.servers_client.list_servers_with_detail()
        list_servers_detail = list_servers_detail_response.entity
        self.assertEqual(200, list_servers_detail_response.status_code)
        servers_lists = []
        for i in list_servers_detail:
            servers_lists.append(i.id)
        self.assertTrue(self.server.id in servers_lists,
                        msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.id in servers_lists,
                        msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.id in servers_lists,
                        msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='positive', net='no')
    def test_list_server_details_using_marker(self):
        """The list of servers should start from the provided marker"""
        list_server_detail_response = self.servers_client.list_servers_with_detail()
        list_server_detail = list_server_detail_response.entity
        first_server = list_server_detail[0]

        # Verify the list of servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers_with_detail(marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertTrue(first_server not in filtered_servers.entity,
                        msg="The server id used as marker found in the server list")

    @tags(type='positive', net='no')
    def test_list_servers_using_marker(self):
        """The list of servers should start from the provided marker"""
        list_server_info_response = self.servers_client.list_servers()
        list_server_info = list_server_info_response.entity
        first_server = list_server_info[0]

        # Verify the list of servers doesn't contain the server used as a marker
        params = first_server.id
        filtered_servers = self.servers_client.list_servers(marker=params)
        self.assertEqual(200, filtered_servers.status_code)
        self.assertTrue(first_server not in filtered_servers.entity,
                        msg="The server id used as marker found in the server list")

    @tags(type='positive', net='no')
    def test_list_server_with_detail_limit_results(self):
        """Verify only the expected number of results (with full details) are returned"""
        limit = 1
        params = limit
        server_with_limit = self.servers_client.list_servers_with_detail(limit=params)
        self.assertEqual(limit, len(server_with_limit.entity),
                         msg="The number of servers returned (%s) was more than the limit (%s)" % (len(server_with_limit.entity), limit))

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_image(self):
        """Filter the list of servers by image"""
        params = self.image_ref
        list_servers_response = self.servers_client.list_servers(image=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertTrue(self.server.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server.image.id)
        self.assertTrue(self.server_second.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server_second.image.id)
        self.assertTrue(self.server_third.min_details() not in
                        list_servers, msg="Server with id %s and image id %s was found in the list filtered by image id %s" % (self.server_third.id, self.server_third.image.id, self.image_ref))

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_flavor(self):
        """Filter the list of servers by flavor"""
        params = self.flavor_ref_alt
        list_servers_response = self.servers_client.list_servers(flavor=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)

        self.assertTrue(self.server.min_details() not in list_servers,
                        msg="Server with id %s and flavor id %s was found in the list filtered by flavor id %s" % (self.server.id, self.server.flavor.id, self.flavor_ref_alt))
        self.assertTrue(self.server_second.min_details() not in list_servers,
                        msg="Server with id %s and flavor id %s was found in the list filtered by flavor id %s" % (self.server_second.id, self.server_second.flavor.id, self.flavor_ref_alt))
        self.assertTrue(self.server_third.min_details() in list_servers,
                        msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_name(self):
        """ Filter the list of servers by name """
        params = self.server.name
        list_servers_response = self.servers_client.list_servers(name=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertTrue(self.server.min_details() in list_servers,
                        msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.min_details() not in list_servers,
                        msg="Server with id %s and name %s was found in the list filtered by name %s" % (self.server.id, self.server_second.name, self.server.name))
        self.assertTrue(self.server_third.min_details() not in list_servers,
                        msg="Server with id %s and name %s was found in the list filtered by name %s" % (self.server_third.id, self.server_third.name, self.server.name))

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_server_status(self):
        """ Filter the list of servers by server status """
        params = 'active'
        list_servers_response = self.servers_client.list_servers(status=params)
        list_servers = list_servers_response.entity
        self.assertEqual(200, list_servers_response.status_code)
        self.assertTrue(self.server.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.min_details() in
                        list_servers, msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='positive', net='no')
    def test_list_servers_filter_by_changes_since(self):
        """Filter the list of servers by changes-since"""
        change_time = self.server_second.created
        params = change_time
        servers = self.servers_client.list_servers(changes_since=params)
        self.assertEqual(200, servers.status_code)
        servers_ids_list = []
        for i in servers.entity:
            servers_ids_list.append(i.id)
        self.assertTrue(self.server.id not in servers_ids_list,
                        msg="Server with id %s was found in the list" % self.server.id)
        self.assertTrue(self.server_second.id in servers_ids_list,
                        msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.id in servers_ids_list,
                        msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_image(self):
        """Filter the detailed list of servers by image"""
        params = self.image_ref
        servers_response = self.servers_client.list_servers_with_detail(image=params)
        self.assertEqual(200, servers_response.status_code)
        servers_list = []
        for i in servers_response.entity:
            servers_list.append(i.id)
        self.assertTrue(self.server.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.id not in servers_list,
                        msg="Server with id %s and image id %s was found in the list filtered by image id %s" % (self.server_third.id, self.server_third.image.id, self.image_ref))

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_flavor(self):
        """Filter the detailed list of servers by flavor"""
        params = self.flavor_ref_alt
        filtered_servers_response = self.servers_client.list_servers_with_detail(flavor=params)
        filtered_servers = filtered_servers_response.entity
        self.assertEqual(200, filtered_servers_response.status_code)

        self.assertTrue(self.server not in filtered_servers,
                        msg="Server with id %s and flavor id %s was found in the list filtered by flavor id %s" % (self.server.id, self.server.flavor.id, self.flavor_ref_alt))
        self.assertTrue(self.server_second not in filtered_servers,
                        msg="Server with id %s and flavor id %s was found in the list filtered by flavor id %s" % (self.server_second.id, self.server.flavor.id, self.flavor_ref_alt))
        self.assertTrue(self.server_third in filtered_servers,
                        msg="Server with id %s was not found in the list" % self.server_third.id,)

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_name(self):
        """Filter the detailed list of servers by server name"""
        params = self.server.name
        filtered_servers_response = self.servers_client.list_servers_with_detail(name=params)
        filtered_servers = filtered_servers_response.entity
        self.assertEqual(200, filtered_servers_response.status_code)

        self.assertTrue(self.server in filtered_servers,
                        msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second not in filtered_servers,
                        msg="Server with id %s and name %s was found in the list filtered by name %s" % (self.server_second.id, self.server_second.name, self.server.name))
        self.assertTrue(self.server_third not in filtered_servers,
                        msg="Server with id %s and name %s was found in the list filtered by name %s" % (self.server_third.id, self.server_third.name, self.server.name))

    @tags(type='positive', net='no')
    def test_list_servers_detailed_filter_by_server_status(self):
        """Filter the detailed list of servers by server status"""
        params = 'active'
        filtered_servers_response = self.servers_client.list_servers_with_detail(status=params)
        filtered_servers = filtered_servers_response.entity
        self.assertEqual(200, filtered_servers_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertTrue(self.server.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server.id)
        self.assertTrue(self.server_second.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server_third.id)

    @tags(type='positive', net='no')
    @unittest.skip("Known issue")
    def test_list_servers_detailed_filter_by_changes_since(self):
        """Create a filter for the server with the second server created date"""
        change_time = self.server_second.created
        params = change_time

        # Filter the detailed list of servers by changes-since
        filtered_servers_response = self.servers_client.list_servers_with_detail(changes_since=params)
        filtered_servers = filtered_servers_response.entity
        self.assertEqual(200, filtered_servers_response.status_code)
        servers_list = []
        for i in filtered_servers:
            servers_list.append(i.id)
        self.assertTrue(self.server.id not in servers_list,
                        msg="Server with id %s was found in the list" % self.server.id)
        self.assertTrue(self.server_second.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server_second.id)
        self.assertTrue(self.server_third.id in servers_list,
                        msg="Server with id %s was not found in the list" % self.server_third.id)
