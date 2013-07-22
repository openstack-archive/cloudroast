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
import httplib
import unittest2 as unittest

from cloudcafe.compute.common.types import ConsoleTypes
from cloudroast.compute.fixtures import CreateServerFixture


class ConsoleServerTests(CreateServerFixture):

    @classmethod
    def setUpClass(cls):
        super(ConsoleServerTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    def test_get_console(self):
        console = self.servers_client.get_console(
            self.server.id, ConsoleTypes.NOVNC).entity
        connection = httplib.HTTPConnection(console.url)
        connection.request('HEAD', '/')
        response = connection.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(console.type, ConsoleTypes.NOVNC)

    def test_get_console_output(self):
        expected_console_output_length = 100
        console = self.servers_client.get_console_output(
            self.server.id, expected_console_output_length).entity
        self.assertTrue(console.output is not None)
        self.assertTrue(len(console.output) <= expected_console_output_length,
                        "Console output length is not matching the "
                        "required length.")
