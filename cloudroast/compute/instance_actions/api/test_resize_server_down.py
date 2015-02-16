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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors, \
    NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()

flavors_config = FlavorsConfig()
resize_enabled = flavors_config.resize_enabled

can_resize = (
    resize_enabled
    and hypervisor not in [ComputeHypervisors.IRONIC,
                           ComputeHypervisors.LXC_LIBVIRT,
                           ComputeHypervisors.ON_METAL])


class ResizeServerDownConfirmTests(object):

    compute_config = ComputeConfig()
    hypervisor = compute_config.hypervisor.lower()

    @tags(type='positive', net='no')
    def test_verify_confirm_resize_response(self):
        pass

    @tags(type='positive', net='no')
    def test_server_properties_after_resize(self):
        self.assertEqual(self.server.flavor.id, self.resized_flavor.id)

    @tags(type='positive', net='yes')
    def test_resized_server_vcpus(self):
        """Verify the number of vCPUs matches the value of the new flavor"""

        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        server_actual_vcpus = remote_client.get_number_of_cpus()
        self.assertEqual(
            server_actual_vcpus, self.resized_flavor.vcpus,
            msg="Expected number of vcpus to be {0}, was {1}.".format(
                self.resized_flavor.vcpus, server_actual_vcpus))

    @tags(type='positive', net='yes')
    @unittest.skipIf(
        hypervisor == ComputeHypervisors.KVM,
        'Resize down is not supported by the desired hypervisor or driver.')
    def test_created_server_disk_size(self):
        """Verify the size of the virtual disk matches that of the flavor"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        disk_size = remote_client.get_disk_size(
            self.servers_config.instance_disk_path)
        self.assertEqual(disk_size, self.resized_flavor.disk,
                         msg="Expected disk to be {0} GB, was {1} GB".format(
                             self.resized_flavor.disk, disk_size))

    @tags(type='positive', net='yes')
    def test_can_log_into_resized_server(self):
        """Tests that we can log into the server after resizing"""
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, config=self.servers_config, key=self.key.private_key)
        self.assertTrue(remote_client.can_authenticate(),
                        msg="Cannot connect to server using public ip")

    @tags(type='positive', net='yes')
    def test_server_ram_after_resize(self):
        """The server's RAM and should be modified to that of the new flavor"""

        remote_instance = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        margin = (int(self.resized_flavor.ram) * .1)
        lower_limit = int(self.resized_flavor.ram) - margin
        server_ram_size = int(remote_instance.get_allocated_ram())
        self.assertTrue((int(self.resized_flavor.ram) == server_ram_size
                         or lower_limit <= server_ram_size),
                        msg='Ram size after confirm-resize did not match.'
                            'Expected ram size : %s, Actual ram size : %s' %
                            (self.resized_flavor.ram, server_ram_size))

    @tags(type='positive', net='no')
    def test_resized_server_instance_actions(self):
        """Verify the correct actions are logged during a confirmed resize."""

        actions = self.servers_client.get_instance_actions(
            self.server.id).entity

        # Verify the resize action is listed
        self.assertTrue(any(a.action == 'resize' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'resize']
        self.assertEquals(len(filtered_actions), 1)

        resize_action = filtered_actions[0]
        self.validate_instance_action(
            resize_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
            self.resize_resp.headers['x-compute-request-id'])

        # Verify the confirm resize action is listed
        self.assertTrue(any(a.action == 'confirmResize' for a in actions))
        filtered_actions = [a for a in actions if a.action == 'confirmResize']
        self.assertEquals(len(filtered_actions), 1)

        resize_action = filtered_actions[0]
        self.validate_instance_action(
            resize_action, self.server.id, self.compute.user.user_id,
            self.compute.user.project_id,
            self.confirm_resize_resp.headers['x-compute-request-id'])


class ResizeDownConfirmBaseFixture(object):

    @classmethod
    def resize_down_and_confirm(self):
        server_to_resize = self.server
        # resize server and confirm
        self.resize_resp = self.servers_client.resize(
            server_to_resize.id, self.flavor_ref)
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.confirm_resize_resp = self.servers_client.confirm_resize(
            server_to_resize.id)
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.ACTIVE)
        resized_server_response = self.servers_client.get_server(
            server_to_resize.id)

        self.server = resized_server_response.entity
        self.server.admin_pass = server_to_resize.admin_pass
        self.resized_flavor = self.flavors_client.get_flavor_details(
            self.flavor_ref).entity


@unittest.skipUnless(
    resize_enabled,
    'Resize is not supported by the desired hypervisor or driver.')
class ServerFromImageResizeServerDownConfirmTests(
        ServerFromImageFixture,
        ResizeServerDownConfirmTests,
        ResizeDownConfirmBaseFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageResizeServerDownConfirmTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(flavor_ref=cls.flavor_ref_alt, key_name=cls.key.name)
        cls.resize_down_and_confirm()
