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

from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudroast.compute.fixtures import ComputeAdminFixture


class MigrateServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(MigrateServerTests, cls).setUpClass()
        blockstorage_config = BlockStorageConfig()
        blockstorage_endpoint = cls.access_data.get_service(
            blockstorage_config.identity_service_name).get_endpoint(
            blockstorage_config.region)
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name, cls.keypairs_client.delete_keypair)
        cls.response, cls.volume_id = cls.server_behaviors.boot_volume(cls.key)
        cls.server = cls.response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.resources.add(cls.volume_id.id_,
                          cls.blockstorage_client.delete_volume)

    def test_migrate_server(self):
        self.admin_servers_client.migrate_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        self.admin_servers_client.confirm_resize(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, NovaServerStatusTypes.ACTIVE)
