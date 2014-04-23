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
        cls.delete_node_resp = cls.nodes_client.delete_node(cls.node.uuid)

    def test_delete_node_response_code(self):
        """Verify that the response code for the delete node
        request is correct.
        """
        self.assertEqual(self.delete_node_resp.status_code, 204)

    def test_cannot_get_deleted_node(self):
        """Verify that a request fails when the details
        of a deleted node are requested.
        """
        resp = self.nodes_client.get_node(self.node.uuid)
        self.assertEqual(resp.status_code, 404)

    def test_deleted_node_not_in_list_of_nodes(self):
        """Verify that a deleted node does not exist in the
        list of all nodes.
        """
        existing_nodes = self.nodes_client.list_nodes().entity
        node_uuids = [node.uuid for node in existing_nodes]
        self.assertNotIn(self.node.uuid, node_uuids)
