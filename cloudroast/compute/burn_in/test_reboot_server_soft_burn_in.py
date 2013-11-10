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

from cloudroast.compute.fixtures import ComputeFixture
from cloudcafe.compute.common.types import NovaServerRebootTypes


class RebootServerSoftBurnIn(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RebootServerSoftBurnIn, cls).setUpClass()
        resp = cls.server_behaviors.create_active_server()
        cls.server = resp.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def test_reboot_server_soft(self):
        self.server_behaviors.reboot_and_await(
            self.server.id, NovaServerRebootTypes.SOFT)
