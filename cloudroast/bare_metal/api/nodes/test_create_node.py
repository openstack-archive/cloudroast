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


class CreateNodeTest(BareMetalFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateNodeTest, cls).setUpClass()
        cls._create_chassis()
        cls._create_node()

    def test_create_node_response_code(self):
        """Verify that the response code for the create node
        request is correct.
        """
        self.assertEqual(self.create_node_resp.status_code, 201)

    def test_created_node_properties(self):
        """Verify that the properties provided to the create node request
        are reflected in the created node.
        """
        self.assertEqual(self.node.driver, self.node_driver)
        self.assertEqual(self.node.chassis_uuid, self.chassis.uuid)
        self.assertEqual(self.node.properties, self.node_properties)
        self.assertEqual(self.node.driver_info, self.driver_info)
        self.assertEqual(self.node.extra, self.node_extra)

    def test_new_node_in_list_of_nodes(self):
        """Verify that the newly created node exists in the
        list of nodes.
        """
        existing_nodes = self.nodes_client.list_nodes().entity
        node_uuids = [node.uuid for node in existing_nodes]
        self.assertIn(self.node.uuid, node_uuids)

    def test_new_node_in_detailed_list_of_nodes(self):
        """Verify that the newly created node exists in the
        detailed list of nodes.
        """
        resp = self.nodes_client.list_nodes_with_details()
        existing_nodes = resp.entity
        node_uuids = [node.uuid for node in existing_nodes]
        self.assertIn(self.node.uuid, node_uuids)

    def test_get_node(self):
        """Verify the details returned by a get node request match
        the expected values.
        """
        resp = self.nodes_client.get_node(self.node.uuid)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(self.node.driver, self.node_driver)
        self.assertEqual(self.node.properties, self.node_properties)
        self.assertEqual(self.node.driver_info, self.driver_info)
        self.assertEqual(self.node.extra, self.node_extra)

    def test_list_nodes_by_chassis(self):
        """Verify that all nodes assigned to a chassis are returned."""
        resp = self.chassis_client.list_nodes_for_chassis(self.chassis.uuid)
        nodes = resp.entity
        node_uuids = [node.uuid for node in nodes]
        self.assertIn(self.node.uuid, node_uuids)
