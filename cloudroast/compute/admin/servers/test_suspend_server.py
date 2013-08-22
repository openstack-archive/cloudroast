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

from cloudcafe.compute.common.types import NovaServerStatusTypes \
    as ServerStates
from cloudroast.compute.fixtures import ComputeAdminFixture


class SuspendServerTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(SuspendServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def test_suspend_resume_server(self):
        self.admin_servers_client.suspend_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.SUSPENDED)
        self.admin_servers_client.resume_server(self.server.id)
        self.admin_server_behaviors.wait_for_server_status(
            self.server.id, ServerStates.ACTIVE)
