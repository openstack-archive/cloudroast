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
from cloudcafe.compute.common.datagen import rand_name
from cloudcafe.compute.common.equality_tools import EqualityTools
from test_repo.compute.fixtures import ComputeFixture


class ResizeServerUpRevertTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ResizeServerUpRevertTests, cls).setUpClass()
        response = cls.compute_provider.create_active_server()
        cls.server = response.entity
        cls.remote_instance = cls.compute_provider.get_remote_instance_client(cls.server)
        file_name = rand_name('file') + '.txt'
        file_content = 'This is a test file'
        cls.file_details = cls. remote_instance.create_file(file_name, file_content)
        response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(ResizeServerUpRevertTests, cls).tearDownClass()

    @tags(type='smoke', net='yes')
    def test_ram_and_disk_size_on_resize_up_server_revert(self):
        """
        The server's RAM and disk space should return to its original
        values after a resize is reverted
        """
        server_response = self.compute_provider.create_active_server()
        server_to_resize = server_response.entity
        self.resources.add(server_to_resize.id, self.servers_client.delete_server)
        remote_instance = self.compute_provider.get_remote_instance_client(server_to_resize)
        file_name = rand_name('file') + '.txt'
        file_content = 'This is a test file'
        file_details = remote_instance.create_file(file_name, file_content)

        #resize server and revert
        self.servers_client.resize(server_to_resize.id, self.flavor_ref_alt)
        self.compute_provider.wait_for_server_status(server_to_resize.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.servers_client.revert_resize(server_to_resize.id)
        reverted_server_response = self.compute_provider.wait_for_server_status(server_to_resize.id, NovaServerStatusTypes.ACTIVE)
        reverted_server = reverted_server_response.entity
        flavor_response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = flavor_response.entity

        '''Verify that the server resize was reverted '''
        public_address = self.compute_provider.get_public_ip_address(reverted_server)
        reverted_server.adminPass = server_to_resize.adminPass
        remote_instance = self.compute_provider.get_remote_instance_client(reverted_server, public_address)
        actual_file_content = remote_instance.get_file_details(file_details.name)

        '''Verify that the file content does not change after resize revert'''
        self.assertEqual(actual_file_content, file_details, msg="file changed after resize revert")

        self.assertEqual(self.flavor_ref, reverted_server.flavor.id,
                         msg="Flavor id not reverted")
        lower_limit = int(flavor.ram) - (int(flavor.ram) * .1)
        server_ram_size = int(remote_instance.get_ram_size_in_mb())
        self.assertTrue(int(flavor.ram) == server_ram_size or lower_limit <= server_ram_size,
                        msg="Ram size after revert did not match.Expected ram size : %s, Actual ram size : %s" % (flavor.ram, server_ram_size))

        self.assertTrue(EqualityTools.are_sizes_equal(flavor.disk, remote_instance.get_disk_size_in_gb(), 0.5),
                        msg="Disk size %s after revert did not match %s" % (remote_instance.get_disk_size_in_gb(), flavor.disk))

    def _assert_server_details(self, server, expected_name, expected_accessIPv4, expected_accessIPv6, expected_id, expected_image_ref):
        self.assertEqual(expected_accessIPv4, server.accessIPv4,
                         msg="AccessIPv4 did not match")
        self.assertEqual(expected_accessIPv6, server.accessIPv6,
                         msg="AccessIPv6 did not match")
        self.assertEquals(self.config.nova.tenant_id, server.tenant_id,
                          msg="Tenant id did not match")
        self.assertEqual(expected_name, server.name,
                         msg="Server name did not match")
        self.assertTrue(server.host_id is not None,
                        msg="Host id was not set")
        self.assertEqual(expected_image_ref, server.image.id,
                         msg="Image id did not match")
        self.assertEqual(self.flavor_ref, server.flavor.id,
                         msg="Flavor id did not match")
        self.assertEqual(expected_id, server.id, msg="Server id did not match")
