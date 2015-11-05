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
import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudcafe.compute.config import ComputeConfig

from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


class MigrateServerTest(object):

    @tags(type='smoke', net='no')
    def test_migrate_server(self):
        """
        Verify that a server can be migrated successfully.

        Get the server that was created in setup and use it to call migrate
        server and waits for status verify resize, once it confirms
        the resize, it will see if the original host is different from the
        current.

        The following assertions occur:
            - The list flavors with detail request raises a 'Bad Request'
              error when given an invalid value for the minimum disk size.
        """

        # Get Admin Server details before migrate
        server_before_migrate = self.admin_servers_client.get_server(
            self.server.id).entity

        # Migrate and wait for ACTIVE status
        self.admin_servers_client.migrate_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        self.admin_servers_client.confirm_resize(self.server.id)
        server_after_migrate = (
            self.admin_server_behaviors.wait_for_server_status(
                self.server.id, NovaServerStatusTypes.ACTIVE).entity)

        # Check that compute node is changed
        self.assertNotEqual(
            server_before_migrate.host, server_after_migrate.host,
            msg="Host not changed after migration for instance {uuid}, "
                "source host is {host_before}, "
                "destination host is {host_after}".format(
                    host_before=server_before_migrate.host,
                    host_after=server_after_migrate.host,
                    uuid=self.server.id))


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC],
    'Migrate server not supported in current configuration.')
class ServerFromImageMigrateTests(ServerFromImageFixture,
                                  MigrateServerTest):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are accessed from a parent class:
            - An instance from ServerFromImageMigrateTests.

        The following resources are created during this setup:
            - Create a server from server behaviors.
            - Initializes compute admin
            - Initializes server behaviors

        """
        super(ServerFromImageMigrateTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
