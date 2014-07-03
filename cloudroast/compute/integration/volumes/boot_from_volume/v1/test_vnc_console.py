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

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.instance_actions.api.test_vnc_console import \
    ServerVncConsoleTests


class ServerFromVolumeV1VncConsoleTests(ServerFromVolumeV1Fixture,
                                        ServerVncConsoleTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1VncConsoleTests, cls).setUpClass()
        cls.create_server()
