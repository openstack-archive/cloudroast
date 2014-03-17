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

import unittest2 as unittest
from unittest2.suite import TestSuite

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.flavors_api.config import FlavorsConfig

from cloudroast.compute.fixtures import ComputeFixture

flavors_config = FlavorsConfig()
resize_enabled = flavors_config.resize_enabled


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(ResizeServerBurnIn("test_resize_server"))
    suite.addTest(ResizeServerBurnIn("test_resize_server_confirm"))
    return suite


@unittest.skipUnless(
    resize_enabled, 'Resize not enabled for this flavor class.')
class ResizeServerBurnIn(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ResizeServerBurnIn, cls).setUpClass()
        resp = cls.server_behaviors.create_active_server()
        cls.server = resp.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='burn-in', net='no')
    def test_resize_server(self):
        self.server_behaviors.resize_and_await(
            self.server.id, self.flavor_ref_alt)

    @tags(type='burn-in', net='no')
    def test_resize_server_confirm(self):
        self.servers_client.confirm_resize(self.server.id)
        self.server_behaviors.wait_for_server_status(self.server.id, 'ACTIVE')
