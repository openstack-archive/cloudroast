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
from cloudcafe.compute.common.types import VncConsoleTypes
from test_repo.compute.fixtures import ComputeFixture


class ServerVncConsoleTests(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerVncConsoleTests, cls).setUpClass()
        response = cls.server_behaviors.create_active_server()
        cls.server = response.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_get_xvpvnc_console(self):
        resp = self.vnc_client.get_vnc_console(
            self.server.id, VncConsoleTypes.XVPVNC)
        self.assertEqual(resp.status_code, 200)

        console = resp.entity
        self.assertEqual(console.type, VncConsoleTypes.XVPVNC)
        self.assertIsNotNone(console.url)

    @tags(type='smoke', net='no')
    def test_get_novnc_console(self):
        resp = self.vnc_client.get_vnc_console(
            self.server.id, VncConsoleTypes.NOVNC)
        self.assertEqual(resp.status_code, 200)

        console = resp.entity
        self.assertEqual(console.type, VncConsoleTypes.NOVNC)
        self.assertIsNotNone(console.url)
