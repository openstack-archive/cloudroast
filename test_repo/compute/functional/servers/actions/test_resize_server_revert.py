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
from test_repo.compute.fixtures import ComputeFixture


class ResizeServerUpRevertTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ResizeServerUpRevertTests, cls).setUpClass()
        server_response = cls.server_behaviors.create_active_server()
        server_to_resize = server_response.entity
        cls.resources.add(server_to_resize.id, cls.servers_client.delete_server)

        # resize server and confirm
        cls.servers_client.resize(server_to_resize.id, cls.flavor_ref_alt)
        cls.server_behaviors.wait_for_server_status(server_to_resize.id,
                                                    NovaServerStatusTypes.VERIFY_RESIZE)

        cls.servers_client.revert_resize(server_to_resize.id)
        cls.server_behaviors.wait_for_server_status(server_to_resize.id,
                                                    NovaServerStatusTypes.ACTIVE)
        resized_server_response = cls.servers_client.get_server(server_to_resize.id)
        cls.server = resized_server_response.entity
        cls.server.admin_pass = server_to_resize.admin_pass
        cls.flavor = cls.flavors_client.get_flavor_details(cls.flavor_ref).entity

    @classmethod
    def tearDownClass(cls):
        super(ResizeServerUpRevertTests, cls).tearDownClass()

    @tags(type='smoke', net='no')
    def test_server_properties_after_resize(self):
        self.assertEqual(self.flavor_ref, self.server.flavor.id)

    @tags(type='smoke', net='yes')
    def test_resize_reverted_server_vcpus(self):
        """Verify the number of vCPUs reported matches the amount set by the original flavor"""

        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         config=self.servers_config)
        server_actual_vcpus = remote_client.get_number_of_vcpus()
        self.assertEqual(server_actual_vcpus, self.flavor.vcpus,
                         msg="Expected number of vcpus to be {0}, was {1}.".format(
                             self.flavor.vcpus, server_actual_vcpus))

    @tags(type='smoke', net='yes')
    def test_resize_reverted_server_disk_size(self):
        """Verify the size of the virtual disk matches the size set by the original flavor"""
        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         config=self.servers_config)
        disk_size = remote_client.get_disk_size_in_gb(self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.flavor.disk, disk_size))

    @tags(type='smoke', net='yes')
    def test_can_log_into_resize_reverted_server(self):
        """Tests that we can log into the created server after reverting the resize"""
        remote_client = self.server_behaviors.get_remote_instance_client(self.server,
                                                                         config=self.servers_config)
        self.assertTrue(remote_client.can_connect_to_public_ip(),
                        msg="Cannot connect to server using public ip")

    @tags(type='smoke', net='yes')
    def test_ram_after_resize_revert(self):
        """The server's RAM should still be set to the amount from the original flavor"""

        remote_instance = self.server_behaviors.get_remote_instance_client(self.server,
                                                                           self.servers_config)
        lower_limit = int(self.flavor.ram) - (int(self.flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_ram_size_in_mb())
        self.assertTrue(int(self.flavor.ram) == server_ram_size or lower_limit <= server_ram_size,
                        msg="Ram size after confirm-resize did not match. Expected ram size : %s, Actual ram size : %s" %
                            (self.flavor.ram, server_ram_size))
