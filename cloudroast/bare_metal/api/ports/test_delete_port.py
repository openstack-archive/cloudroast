"""
Copyright 2014 Rackspace

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

from cloudroast.bare_metal.fixtures import BareMetalFixture


class DeletePortTest(BareMetalFixture):

    @classmethod
    def setUpClass(cls):
        super(DeletePortTest, cls).setUpClass()
        cls._create_chassis()
        cls._create_node()
        cls._create_port()
        cls.delete_port_resp = cls.ports_client.delete_port(cls.port.uuid)

    def test_delete_port_response_code(self):
        """Verify that the response code for the delete port
        request is correct.
        """
        self.assertEqual(self.delete_port_resp.status_code, 204)

    def test_cannot_get_deleted_port(self):
        """Verify that a request fails when the details
        of a deleted port are requested.
        """
        resp = self.ports_client.get_port(self.port.uuid)
        self.assertEqual(resp.status_code, 404)

    def test_deleted_port_not_in_list_of_ports(self):
        """Verify that a deleted port does not exist in the
        list of all ports.
        """
        existing_ports = self.ports_client.list_ports().entity
        port_uuids = [port.uuid for port in existing_ports]
        self.assertNotIn(self.port.uuid, port_uuids)
