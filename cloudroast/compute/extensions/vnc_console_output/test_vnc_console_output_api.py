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
import unittest2 as unittest

from cloudcafe.compute.servers_api.config import ServersConfig
from cloudroast.compute.fixtures import CreateServerFixture


class VncConsoleOutputTests(CreateServerFixture):

    timeout = ServersConfig().server_boot_timeout

    def test_get_console_output(self):
        expected_console_output_length = 100
        console = self.vnc_console_output_client.get_vnc_console_output(
            self.created_server.id, expected_console_output_length).entity

        #Retry getting console output, as the server might take some
        #time to boot up and then log to output stream.
        start = int(time.time())
        while console.output in ["0", None]:
            console = self.vnc_console_output_client.get_vnc_console_output(
                self.created_server.id, expected_console_output_length).entity
            if int(time.time() - start) >= self.timeout:
                break

        self.assertNotIn(console.output, ["0", None],
                         "No Console Output")
        self.assertTrue(len(console.output.split("\n"))
                        <= expected_console_output_length,
                        "Console output length is not matching the "
                        "expected length.")
