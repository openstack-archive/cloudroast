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


class ServerSecurityGroupTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerSecurityGroupTest, cls).setUpClass()
        cls.security_group = cls.security_groups_client.create_security_group(
            name='test', description='test group').entity
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='positive', net='no')
    def test_add_security_group_to_server(self):
        self.servers_client.add_security_group(
            self.server.id, self.security_group.name)
        security_groups_of_server = self.servers_client.list_security_groups(
            self.server.id).entity
        self.assertIn(str(self.security_group.id),
                      [group.id for group in security_groups_of_server],
                      "Expected security group is not present in server.")

    @classmethod
    def tearDownClass(cls):
        super(ServerSecurityGroupTest, cls).tearDownClass()
        cls.server_behaviors.wait_for_server_to_be_deleted(cls.server.id)
        cls.security_groups_client.delete_security_group(cls.security_group.id)
