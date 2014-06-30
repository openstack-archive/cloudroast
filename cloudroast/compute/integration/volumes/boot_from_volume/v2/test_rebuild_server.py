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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.functional.servers.actions.test_rebuild_server \
    import RebuildServerTests, RebuildBaseFixture
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeV2RebuildTests(ServerFromVolumeV2Fixture,
                                     RebuildServerTests,
                                     RebuildBaseFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2RebuildTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.rebuild_and_await()

    @tags(type='smoke', net='yes')
    def test_rebuilt_volume_server_disk_size(self):
        """Verify the size of the virtual disk after the server rebuild"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.volume_size,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.volume_size, disk_size))
