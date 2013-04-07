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

import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerRebootTypes
from test_repo.compute.fixtures import ComputeFixture


class RebootServerSoftTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebootServerSoftTests, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(RebootServerSoftTests, cls).tearDownClass()

    @tags(type='smoke', net='yes')
    def test_reboot_server_soft(self):
        """ The server should be signaled to reboot gracefully """
        public_address = self.server_behaviors.get_public_ip_address(self.server)
        remote_instance = self.server_behaviors.get_remote_instance_client(self.server, public_address)
        uptime_start = remote_instance.get_uptime()
        start = time.time()

        self.server_behaviors.reboot_and_await(self.server.id, NovaServerRebootTypes.SOFT)
        remote_client = self.server_behaviors.get_remote_instance_client(self.server, public_address)
        finish = time.time()
        uptime_post_reboot = remote_client.get_uptime()
        self.assertLess(uptime_post_reboot, (uptime_start + (finish - start)))
