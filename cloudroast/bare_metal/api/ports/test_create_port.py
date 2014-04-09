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


class CreatePortTest(BareMetalFixture):

    @classmethod
    def setUpClass(cls):
        super(CreatePortTest, cls).setUpClass()
        cls._create_chassis()
        cls._create_node()
        cls._create_port()

    def test_create_port_response_code(self):
        """Verify that the response code for the create port
        request is correct.
        """
        self.assertEqual(self.create_port_resp.status_code, 201)

    def test_created_port_properties(self):
        """Verify that the properties provided to the create port request
        are reflected in the created port.
        """
        self.assertEqual(self.port.address, self.mac_address)
        self.assertEqual(self.port.node_uuid, self.node.uuid)
        self.assertEqual(self.port.extra, self.port_extra)

    def test_new_port_in_list_of_ports(self):
        """Verify that the newly created port exists in the
        list of ports.
        """
        existing_ports = self.ports_client.list_ports().entity
        port_uuids = [port.uuid for port in existing_ports]
        self.assertIn(self.port.uuid, port_uuids)

    def test_new_port_in_detailed_list_of_ports(self):
        """Verify that the newly created port exists in the
        detailed list of ports.
        """
        existing_ports = self.ports_client.list_ports_with_detail().entity
        port_uuids = [port.uuid for port in existing_ports]
        self.assertIn(self.port.uuid, port_uuids)

    def test_get_port(self):
        """Verify the details returned by a get port request match
        the expected values.
        """
        resp = self.ports_client.get_port(self.port.uuid)
        self.assertEqual(resp.status_code, 200)

        port = resp.entity
        self.assertEqual(port.address, self.mac_address)
        self.assertEqual(self.port.node_uuid, self.node.uuid)
        self.assertEqual(self.port.extra, self.port_extra)

    def test_list_ports_by_node(self):
        """Verify that all ports assigned to a node are returned."""
        ports = self.nodes_client.list_ports_for_node(self.node.uuid).entity
        port_uuids = [port.uuid for port in ports]
        self.assertIn(self.port.uuid, port_uuids)
