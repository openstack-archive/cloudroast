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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import ComputeHypervisors, \
    NovaServerStatusTypes
from cloudcafe.compute.config import ComputeConfig
from cloudcafe.compute.flavors_api.config import FlavorsConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()

flavors_config = FlavorsConfig()
resize_up_enabled = (flavors_config.resize_up_enabled
                     if flavors_config.resize_up_enabled is not None
                     else flavors_config.resize_enabled)

can_resize = (
    resize_up_enabled
    and hypervisor not in [ComputeHypervisors.IRONIC,
                           ComputeHypervisors.LXC_LIBVIRT])


class ResizeServerDataIntegrityTests(object):

    @tags(type='smoke', net='yes')
    def test_active_file_inject_during_resize(self):
        """
        Injecting a file during a resize should be successful.

        Resize a server and wait until it enters task state 'resize_migrating'.
        Get a remote instance client for the server and use it to inject a file
        with the name 'tst.txt', the contents 'content' and the file path
        found in the test configuration. Confirm the resize by waiting for it
        to reach status 'VERIFY_RESIZE'. Wait for the server to enter 'ACTIVE'
        state. Get a remote client for the server, validate that the file
        injected during resize exists on the server and has the correct
        contents.

        The following assertions occur:
            - The file injected while the server was resizing is found on the
              server and has the expected contents.
        """
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
            file_content="content",
            file_path=self.servers_config.default_file_path).content
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
            file_path='{0}/tst.txt'.format(
                self.servers_config.default_file_path)).content
        self.assertEqual(prototype_file, file,
                         msg="File does not match prototype one")


@unittest.skipUnless(
    can_resize, 'Resize not enabled due to the flavor class or hypervisor.')
class ServerFromImageResizeServerUpConfirmTests(ServerFromImageFixture,
                                                ResizeServerDataIntegrityTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that set up the necessary resources for testing

        The following resources are created during this set up:
            - A keypair with a random name starting with 'key'
            - A server with the following settings:
                - The keypair previously created
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ServerFromImageResizeServerUpConfirmTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
