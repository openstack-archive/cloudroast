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

from cloudcafe.compute.composites import ComputeAdminComposite
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.integration.volumes.boot_from_volume.admin_api \
    .test_server_live_migration import LiveMigratationServerTests


class ServerFromImageLiveMigrateTests(ServerFromVolumeV1Fixture,
                                      LiveMigratationServerTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Create an active server.
        """
        super(ServerFromImageLiveMigrateTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
