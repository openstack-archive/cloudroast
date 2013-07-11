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

import base64
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.models.metadata import Metadata
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeFixture


class ServersTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServersTest, cls).setUpClass()
        cls.file_contents = 'This is a test file.'
        cls.personality = [{'path': '/root/.csivh',
                            'contents': base64.b64encode(cls.file_contents)}]
        cls.meta = {'meta_key_1': 'meta_value_1', 'meta_key_2': 'meta_value_2'}
        cls.accessIPv4 = '192.168.32.16'
        cls.accessIPv6 = '3ffe:1900:4545:3:200:f8ff:fe21:67cf'

    @classmethod
    def tearDownClass(cls):
        super(ServersTest, cls).tearDownClass()

    def _assert_server_details(self, server, expected_name,
                               expected_accessIPv4, expected_accessIPv6,
                               expected_flavor):
        self.assertEqual(expected_accessIPv4, server.accessIPv4,
                         msg="AccessIPv4 did not match")
        self.assertEqual(expected_accessIPv6, server.accessIPv6,
                         msg="AccessIPv6 did not match")
        self.assertEqual(expected_name, server.name,
                         msg="Server name did not match")
        self.assertEqual(self.image_ref, server.image.id,
                         msg="Image id did not match")
        self.assertEqual(expected_flavor, server.flavor.id,
                         msg="Flavor id did not match")
        self.assertTrue(server.created is not None,
                        msg="Server created date was not set")
        self.assertTrue(server.updated is not None,
                        msg="Server updated date was not set")
        self.assertGreaterEqual(server.updated, server.created,
                                msg="Server updated date was before the created date")
        self.assertEqual(self.meta, Metadata._obj_to_dict(server.metadata),
                         msg="Metadata did not match")

    def _assert_public_address_is_valid(self, addresses):

        self.assertTrue(len(addresses.public.addresses) == 2,
                        msg="Server does not have a Public IPs set")
        ipv4_public_address = None
        ipv6_public_address = None
        if self.config.misc.serializer == "xml":
            for address in addresses.public.addresses:
                if address.version == '4':
                    ipv4_public_address = address
                else:
                    ipv6_public_address = address
            self.assertTrue(ipv4_public_address.version == '4' and
                            ipv4_public_address.addr is not None,
                            msg="Server does not have a Public IPv4 set")
            self.assertTrue(ipv6_public_address.version == '6' and
                            ipv6_public_address.addr is not None,
                            msg="Server does not have a Public IPv6 set")
        else:
            for address in addresses.public.addresses:
                if address.version == 4:
                    ipv4_public_address = address
                else:
                    ipv6_public_address = address
                self.assertTrue(ipv4_public_address.version == 4 and
                                ipv4_public_address.addr is not None,
                                msg="Server does not have a Public IPv4 set")
                self.assertTrue(ipv6_public_address.version == 6 and
                                ipv6_public_address.addr is not None,
                                msg="Server does not have a Public IPv6 set")

    @tags(type='positive', net='yes')
    def test_create_server_with_admin_password(self):
        """
        If an admin password is provided on server creation, the server's root
        password should be set to that password.
        """
        name = rand_name("testserver")
        admin_password = 'oldslice129690TuG72Bgj2'
        create_server_response = self.servers_client.create_server(name, self.image_ref, self.flavor_ref, admin_pass=admin_password)
        created_server = create_server_response.entity

        self.assertEqual(admin_password, created_server.admin_pass,
                         msg='Verify that given adminPass equals with actual one')
        active_server = self.server_behaviors.wait_for_server_status(created_server.id, NovaServerStatusTypes.ACTIVE)


    @tags(type='positive', net='no')
    def test_create_server_with_image_and_flavor_self_link(self):
        """Create a server using image and flavor self links"""
        name = rand_name("testserver")
        image = self.images_client.get_image(self.image_ref)
        image_self_link = image.entity.id
        flavor = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor_self_link = flavor.entity.id

        create_server_response = self.servers_client.create_server(name,
                                                                   image_self_link,
                                                                   flavor_self_link)
        created_server = create_server_response.entity
        #Verify the parameters are correct in the initial response
        self.assertTrue(created_server.id is not None,
                        msg="The server id was not set in response")
        self.assertTrue(created_server.admin_pass is not None,
                        msg="Admin password was not set in response")
        self.assertTrue(created_server.links is not None,
                        msg="Server links were not set in response")

        '''Wait for the server to become active'''
        active_server_response = self.server_behaviors.wait_for_server_status(created_server.id,
                                                                              NovaServerStatusTypes.ACTIVE)
        active_server = active_server_response.entity
        get_server_info_response = self.servers_client.get_server(created_server.id)
        get_server_info = get_server_info_response.entity

        '''Verify that the image Id of the image ref link which is used to create server
        is same as the image id of the created server'''
        self.assertEqual(get_server_info.image.id, self._parse_link_to_retrieve_id(image_self_link),
                         msg="The image does not match to the image mentioned during create")

        '''Verify that the flavor Id of the flavor ref link which is used to create server
        is same as the flavor id of the created server'''
        self.assertEqual(get_server_info.flavor.id, self._parse_link_to_retrieve_id(flavor_self_link),
                         msg="The flavor does not match to the flavor mentioned during create")

        self.servers_client.delete_server(active_server.id)

    def _parse_link_to_retrieve_id(self, ref):
        temp = ref.rsplit('/')
        #Return the last item, which is the image id
        return temp[len(temp) - 1]

    @tags(type='positive', net='no')
    def test_create_server_with_image_and_flavor_bookmark_link(self):
        """Create a server using image and flavor bookmark links"""
        name = rand_name("testserver")
        image = self.images_client.get_image(self.image_ref)
        image_bookmark_link = image.entity.links.links.get('bookmark')
        flavor = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor_bookmark_link = flavor.entity.links.links.get('bookmark')
        create_server_response = self.servers_client.create_server(name,
                                                                   image_bookmark_link,
                                                                   flavor_bookmark_link)
        created_server = create_server_response.entity

        '''Verify the parameters are correct in the initial response'''
        self.assertTrue(created_server.id is not None,
                        msg="The server id was not set in the response")
        self.assertTrue(created_server.admin_pass is not None,
                        msg="Admin password was not set in the response")
        self.assertTrue(created_server.links is not None,
                        msg="Server links were not set in the response")

        '''Wait for the server to become active'''
        active_server_response = self.server_behaviors.wait_for_server_status(created_server.id,
                                                                              NovaServerStatusTypes.ACTIVE)
        active_server = active_server_response.entity
        get_server_info_response = self.servers_client.get_server(created_server.id)
        get_server_info = get_server_info_response.entity
        '''Verify that the correct image and flavor refs were used'''
        self.assertEqual(get_server_info.image.id, self._parse_link_to_retrieve_id(image_bookmark_link),
                         msg="The image does not match to the image mentioned during create")
        self.assertEqual(get_server_info.flavor.id, self._parse_link_to_retrieve_id(flavor_bookmark_link),
                         msg="The flavor does not match to the flavor mentioned during create")

        self.servers_client.delete_server(active_server.id)

    @tags(type='positive', net='no')
    def test_update_server_using_server_self_link(self):
        """Update a server using the server self link"""
        name = rand_name("testserver")
        stored_name = name
        '''Create an active server'''
        active_server_response = self.server_behaviors.create_active_server()
        active_server = active_server_response.entity
        '''Need to ensure there is atleast one second gap between creating and
        updating a server. The test failed once without the sleep.'''
        time.sleep(1)
        '''Some processing'''
        link = str(active_server.links.self)
        link_list = link.split('/')
        server_id = link_list[6]
        '''Use server self link to update the server'''
        updated_server_response = self.servers_client.update_server(server_id,
                                                                    name,
                                                                    accessIPv4=self.accessIPv4,
                                                                    accessIPv6=self.accessIPv6)
        updated_server = updated_server_response.entity
        self.server_behaviors.wait_for_server_status(updated_server.id, NovaServerStatusTypes.ACTIVE)

        '''Verify the name and access ips of the server have changed'''
        get_server_info = self.servers_client.get_server(updated_server.id)
        self.assertEqual(stored_name, get_server_info.entity.name,
                         msg="The name was not updated")
        self.assertEqual(self.accessIPv4, get_server_info.entity.accessIPv4,
                         msg="AccessIPv4 was not updated")
        self.assertEqual(self.accessIPv6, get_server_info.entity.accessIPv6,
                         msg="AccessIPv6 was not updated")
        self.assertEqual(active_server.created, get_server_info.entity.created,
                         msg="The creation date was updated")
        self.assertTrue(active_server.updated != get_server_info.entity.updated,
                        msg="Server %s updated time did not change after a modification to the server." % updated_server.id)

        self.servers_client.delete_server(get_server_info.entity.id)

    @tags(type='positive', net='no')
    def test_update_server_using_server_bookmark_link(self):
        """Update a server using the server bookmark link"""
        name = rand_name("testserver")
        stored_name = name
        #        Create an active server
        active_server_response = self.server_behaviors.create_active_server()
        active_server = active_server_response.entity
        '''Need to ensure there is atleast one second gap between creating
        and updating a server. The test failed once without the sleep.'''
        time.sleep(1)
        #Some processing
        link = str(active_server.links.bookmark)
        link_list = link.split('/')
        server_id = link_list[5]
        '''Use server bookmark's link to update the server'''
        updated_server_response = self.servers_client.update_server(server_id,
                                                                    name,
                                                                    accessIPv4=self.accessIPv4,
                                                                    accessIPv6=self.accessIPv6)
        updated_server = updated_server_response.entity
        self.server_behaviors.wait_for_server_status(updated_server.id, NovaServerStatusTypes.ACTIVE)

        '''Verify the name and access ips of the server have changed'''
        get_server_info = self.servers_client.get_server(updated_server.id)
        self.assertEqual(stored_name, get_server_info.entity.name,
                         msg="The name was not updated")
        self.assertEqual(self.accessIPv4, get_server_info.entity.accessIPv4,
                         msg="AccessIPv4 was not updated")
        self.assertEqual(self.accessIPv6, get_server_info.entity.accessIPv6,
                         msg="AccessIPv6 was not updated")
        self.assertEqual(active_server.created, get_server_info.entity.created,
                         msg="The creation date was updated")
        self.assertTrue(active_server.updated != get_server_info.entity.updated,
                        msg="Server %s updated time did not change after a modification to the server." % updated_server.id)

        self.servers_client.delete_server(get_server_info.entity.id)
