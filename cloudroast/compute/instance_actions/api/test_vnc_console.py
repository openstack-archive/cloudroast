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
from cloudcafe.compute.common.types import ComputeHypervisors, \
    VncConsoleTypes
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ServerFromImageFixture

compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.IRONIC],
    'Get VNC console not supported in current configuration.')
class ServerVncConsoleTests(object):

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


class ServerFromImageVncConsoleTests(ServerFromImageFixture,
                                     ServerVncConsoleTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageVncConsoleTests, cls).setUpClass()
        cls.create_server()
