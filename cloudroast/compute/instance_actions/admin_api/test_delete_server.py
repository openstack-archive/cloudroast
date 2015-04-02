"""
Copyright 2015 Rackspace

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

from cloudroast.compute.fixtures import ComputeAdminFixture
from cloudroast.compute.instance_actions.api.test_delete_server import \
    DeleteServersTest


class DeleteServerAsAdminTests(ComputeAdminFixture,
                               DeleteServersTest):
    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create a server from server behaviors.
            - Deletes the same server in setup.

        """
        super(DeleteServerAsAdminTests, cls).setUpClass()

        # Create Active server as standard User
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

        # Delete the server as an admin
        cls.resp = cls.admin_servers_client.delete_server(cls.server.id)
        cls.admin_server_behaviors.wait_for_server_to_be_deleted(cls.server.id)
