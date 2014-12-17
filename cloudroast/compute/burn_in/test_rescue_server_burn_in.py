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

from unittest.suite import TestSuite

from cafe.drivers.unittest.decorators import tags

from cloudroast.compute.fixtures import ComputeFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(RescueServerBurnIn("test_rescue_server"))
    suite.addTest(RescueServerBurnIn("test_unrescue_server"))
    return suite


class RescueServerBurnIn(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(RescueServerBurnIn, cls).setUpClass()
        resp = cls.server_behaviors.create_active_server()
        cls.server = resp.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='burn-in', net='no')
    def test_rescue_server(self):
        self.rescue_client.rescue(self.server.id)
        self.server_behaviors.wait_for_server_status(
            self.server.id, 'RESCUE')

    @tags(type='burn-in', net='no')
    def test_unrescue_server(self):
        self.rescue_client.unrescue(self.server.id)
        self.server_behaviors.wait_for_server_status(
            self.server.id, 'ACTIVE')
