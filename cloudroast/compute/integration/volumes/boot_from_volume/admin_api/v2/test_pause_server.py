"""
Copyright 2014 Rackspace

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

from cloudcafe.compute.composites import ComputeAdminComposite

from cloudroast.compute.instance_actions.admin_api.test_pause_server import \
    PauseServerTests, NegativePauseServerTests
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeV2PauseTests(ServerFromVolumeV2Fixture,
                                   PauseServerTests,
                                   NegativePauseServerTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2PauseTests, cls).setUpClass()
        cls.compute_admin = ComputeAdminComposite()
        cls.admin_servers_client = cls.compute_admin.servers.client
        cls.admin_server_behaviors = cls.compute_admin.servers.behaviors
        cls.create_server()
