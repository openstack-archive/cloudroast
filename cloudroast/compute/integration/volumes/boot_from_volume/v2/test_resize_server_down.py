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

from cloudroast.compute.functional.servers.actions.test_resize_server_down \
    import ResizeServerDownConfirmTests, ResizeDownConfirmBaseFixture
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeV2ResizeDownConfirmTests(ServerFromVolumeV2Fixture,
                                               ResizeServerDownConfirmTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2ResizeDownConfirmTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(flavor_ref=cls.flavor_ref_alt, key_name=cls.key.name)
        ResizeDownConfirmBaseFixture.resize_down_and_confirm(fixture=cls)
