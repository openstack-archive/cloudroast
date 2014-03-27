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
from cloudroast.compute.fixtures import ComputeFixture


class BootInvalidValues(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(BootInvalidValues, cls).setUpClass()
        cls.err_msg = ""

    @tags(type='smoke', net='yes')
    def test_for_invalid_device_name_should_not_be_created(self):
        try:
            boot_from_block = {'volume_id': None,
                               'del_on_termination': None,
                               'device_name': 'XXX',
                               'type': None}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[35:41], "Boot s", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because devcie was invalid")

    @tags(type='smoke', net='yes')
    def test_for_invalid_type_value_should_not_be_created(self):
        try:
            boot_from_block = {'volume_id': None,
                               'del_on_termination': None,
                               'device_name': None,
                               'type': 'XXX'}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[2:7], "Block", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)

        self.fail("Test case should have failed because type was invalid")

    @tags(type='smoke', net='yes')
    def test_for_invalid_del_on_term_should_not_be_created(self):
        try:
            boot_from_block = {'volume_id': None,
                               'del_on_termination': 'XXX',
                               'device_name': None,
                               'type': None}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[2:7], "Block", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because delete on",
                  " termination was invalid")

    @tags(type='smoke', net='yes')
    def test_for_invalid_volume_id_should_not_be_created(self):
        try:
            boot_from_block = {'volume_id': 'XXX',
                               'del_on_termination': None,
                               'device_name': None,
                               'type': None}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[35:41], "failed", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because volume id was invalid")

    @tags(type='smoke', net='yes')
    def test_for_invalid_flavor_should_not_be_created(self):
        try:
            self.response = self.server_behaviors.create_active_server(
                flavor_ref='XXX')
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[2:11], "Invalid f",
                             self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because flavor was invalid")

    @tags(type='smoke', net='yes')
    def test_for_deleted_volume_should_not_be_created(self):
        try:
            boot_from_block = {
                'volume_id': '33ac75ff-4bd8-4640-82b9-1f023d4e2cfd',
                'del_on_termination': None,
                'device_name': None,
                'type': None}
            self.response = self.server_behaviors.create_active_server(
                boot_from_block=boot_from_block)
        except Exception as self.err_msg:
            self.assertEqual(str(self.err_msg)[35:41], "failed", self.err_msg)
        else:
            self.server = self.response.entity
            self.resources.add(self.server.id,
                               self.servers_client.delete_server)
        self.fail("Test case should have failed because volume was deleted")
