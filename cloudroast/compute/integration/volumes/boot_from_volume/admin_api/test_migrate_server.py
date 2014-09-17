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
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture, \
    ServerFromVolumeV1Fixture


class MigrateVolumeServerTest(object):

    @tags(type='smoke', net='no')
    def test_migrate_server(self):
        """Verify that a server can be migrated successfully"""

        # Get Admin Server details before migrate
        server_before_migrate = self.admin_servers_client.get_server(
            self.server.id).entity

        # Migrate and wait for ACTIVE status
        self.admin_servers_client.migrate_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        self.admin_servers_client.confirm_resize(self.server.id)
        server_after_migrate = self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE).entity

        # Check that compute node is changed
        self.assertNotEqual(
            server_before_migrate.host, server_after_migrate.host,
            msg="Host is not changed after migration, source host is {0} "
                "destination host is {2}".format(
                    server_before_migrate.host, server_after_migrate.host))


class ServerFromVolumeV2MigrateTests(ServerFromVolumeV2Fixture,
                                     MigrateVolumeServerTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2MigrateTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()


class ServerFromVolumeV1MigrateTests(ServerFromVolumeV1Fixture,
                                     MigrateVolumeServerTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1MigrateTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
