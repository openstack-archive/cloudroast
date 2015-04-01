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

from cafe.drivers.unittest.decorators import tags

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.instance_actions.api.test_rebuild_server \
    import RebuildServerTests, RebuildBaseFixture
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture


class ServerFromVolumeV1RebuildTests(ServerFromVolumeV1Fixture,
                                     RebuildBaseFixture,
                                     RebuildServerTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates a keypair.
            - Creates an active server.
            - Rebuilds and waits for server to be active again.
        """
        super(ServerFromVolumeV1RebuildTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.rebuild_and_await()

    @tags(type='smoke', net='yes')
    def test_rebuilt_volume_server_disk_size(self):
        """
        Verify the size of the virtual disk after the server rebuild.

        Will get the remote instance of the server and pull the disk info
        from the server to validate the disk size is correct.

        The following assertions occur:
            - The disk size is equal to defined size at rebuild.
        """
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, password=self.password,
            key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.volume_size,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.volume_size, disk_size))
