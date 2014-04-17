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

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.functional.servers.actions.test_reboot_server_soft \
    import RebootServerSoftTests
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture


class ServerFromVolumeV1RebootSoftTests(ServerFromVolumeV1Fixture,
                                        RebootServerSoftTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1RebootSoftTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
