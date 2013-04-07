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
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.datagen import rand_name
from test_repo.compute.fixtures import ComputeFixture



class RebuildServerTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebuildServerTests, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.metadata = {'key': 'value'}
        cls.name = rand_name('testserver')
        file_contents = 'Test server rebuild.'
        personality = [{'path': '/etc/rebuild.txt',
                        'contents': base64.b64encode(file_contents)}]
        cls.password = 'rebuild'

        rebuilt_server_response = cls.servers_client.rebuild(cls.server.id,
                                                             cls.image_ref_alt,
                                                             name=cls.name,
                                                             metadata=cls.metadata,
                                                             personality=personality,
                                                             admin_pass=cls.password)
        cls.rebuilt_server_response = cls.server_behaviors.wait_for_server_status(cls.server.id,
                                                                                  NovaServerStatusTypes.ACTIVE)

    @classmethod
    def tearDownClass(cls):
        super(RebuildServerTests, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_verify_rebuild_server_response(self):
        #Verify the properties in the initial response are correct
        rebuilt_server = self.rebuilt_server_response.entity

        if rebuilt_server.addresses.public is not None:
            v4_address = rebuilt_server.addresses.public.ipv4
            v6_address = rebuilt_server.addresses.public.ipv6
            self.assertEqual(v4_address, self.server.accessIPv4,
                             msg="AccessIPv4 did not match")
            self.assertEqual(v6_address, self.server.accessIPv6,
                             msg="AccessIPv6 did not match")

        self.assertEqual(rebuilt_server.name, self.name,
                         msg="Server name did not match")
        self.assertTrue(rebuilt_server.hostId is not None,
                        msg="Host id was not set")
        self.assertEqual(rebuilt_server.image.id, self.image_ref_alt,
                         msg="Image id did not match")
        self.assertEqual(rebuilt_server.flavor.id, self.flavor_ref,
                         msg="Flavor id did not match")
        self.assertEqual(rebuilt_server.id, self.server.id, msg="Server id did not match")

        self.assertEqual(rebuilt_server.links.bookmark, self.server.links.bookmark, msg="Bookmark links do not match")
        self.assertEqual(self.server.links.self, self.rebuilt_server_response['location'],
                         msg="Location url did not match a valid link for the server")
        self.assertEqual(rebuilt_server.metadata.key, 'value')
        self.assertEqual(rebuilt_server.created, self.server.created,
                         msg="Server Created date changed after rebuild")
        self.assertTrue(rebuilt_server.updated != self.server.updated,
                        msg="Server Updated date not changed after rebuild")
        self.assertEquals(rebuilt_server.addresses, self.server.addresses,
                          msg="Server IP addresses changed after rebuild")

    @tags(type='smoke', net='yes')
    def test_can_log_into_server_after_rebuild(self):
        server = self.rebuilt_server_response.entity
        rebuilt_server = self.rebuilt_server_response.entity
        public_address = self.server_behaviors.get_public_ip_address(rebuilt_server)
        server.adminPass = self.password
        remote_instance = self.server_behaviors.get_remote_instance_client(server, public_address)
        self.assertTrue(remote_instance.can_connect_to_public_ip(),
                        msg="Could not connect to server (%s) using new admin password %s" % (public_address, server.adminPass))
