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
from cloudcafe.compute.common.exceptions import BadRequest
from test_repo.compute.fixtures import ComputeFixture


class ServerMissingParameterTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerMissingParameterTests, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        cls.server = server_response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='negative', net='no')
    def test_create_server_without_name(self):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                None, self.image_ref, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_image(self):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', None, self.flavor_ref)

    @tags(type='negative', net='no')
    def test_create_server_without_flavor(self):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server('test', self.image_ref, None)

    @tags(type='negative', net='no')
    def test_change_password_without_password(self):
        with self.assertRaises(BadRequest):
            self.servers_client.change_password(self.server.id, None)

    @tags(type='negative', net='no')
    def test_reboot_server_without_type(self):
        with self.assertRaises(BadRequest):
            self.servers_client.reboot(self.server.id, None)

    @tags(type='negative', net='no')
    def test_rebuild_server_without_name(self):
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, None, self.image_ref)

    @tags(type='negative', net='no')
    def test_rebuild_server_without_image(self):
        with self.assertRaises(BadRequest):
            self.servers_client.rebuild(self.server.id, 'test', None)

    @tags(type='negative', net='no')
    def test_resize_server_without_flavor(self):
        with self.assertRaises(BadRequest):
            self.servers_client.resize(self.server.id, None)

    @tags(type='negative', net='no')
    def test_create_image_without_name(self):
        with self.assertRaises(BadRequest):
            self.servers_client.create_image(self.server.id, None)
