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

from cloudroast.compute.functional.servers.actions.test_change_password \
    import ChangeServerPasswordTests, ChangePasswordBaseFixture
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeV2ChangePasswordTests(ServerFromVolumeV2Fixture,
                                            ChangeServerPasswordTests,
                                            ChangePasswordBaseFixture):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2ChangePasswordTests, cls).setUpClass()
        cls.create_server()
        cls.change_password()
