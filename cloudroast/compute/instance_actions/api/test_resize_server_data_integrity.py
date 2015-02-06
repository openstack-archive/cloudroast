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
                           ComputeHypervisors.LXC_LIBVIRT])


class ResizeServerDataIntegrityTests(object):

    @tags(type='smoke', net='yes')
    def test_active_file_inject_during_resize(self):
        server_to_resize = self.server
        # resize server and wait for task resize migrate
        self.resize_resp = self.servers_client.resize(
            server_to_resize.id, self.flavor_ref_alt)
        self.server_behaviors.wait_for_server_task_state(
            self.server.id, 'resize_migrating',
            self.servers_config.server_build_timeout)
        # Inject sample file
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        prototype_file = remote_client.create_file(
            file_name='tst.txt',
            file_content="content").content
        # Confirm Resize and wait for Active Server status
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.VERIFY_RESIZE)

        self.confirm_resize_resp = self.servers_client.confirm_resize(
            server_to_resize.id)
        self.server_behaviors.wait_for_server_status(
            server_to_resize.id, NovaServerStatusTypes.ACTIVE)

        # Check if the file exist after resize confirm
        remote_client = self.server_behaviors.get_remote_instance_client(
            self.server, self.servers_config, key=self.key.private_key)
        file = remote_client.get_file_details(
            file_path='/root/tst.txt').content
        self.assertEqual(prototype_file, file,
                         msg="File does not match prototype one")


@unittest.skipUnless(
    resize_enabled, 'Resize not enabled for this flavor class.')
class ServerFromImageResizeServerUpConfirmTests(ServerFromImageFixture,
                                                ResizeServerDataIntegrityTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageResizeServerUpConfirmTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
