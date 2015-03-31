"""
Copyright 2015 Rackspace

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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import Forbidden

from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture


class ServerFromVolumeV1CreateImageTests(ServerFromVolumeV1Fixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates an active server.
        """
        super(ServerFromVolumeV1CreateImageTests, cls).setUpClass()
        cls.create_server()
        cls.image_name = rand_name('image')
        cls.metadata = {'user_key1': 'value1',
                        'user_key2': 'value2'}

    @tags(type='smoke', net='no')
    def test_verify_create_glance_snapshot_is_disabled(self):
        """
        Verify a user can not take glance snapshot on BFV instance.

        Will try to create an image from the server and is expecting a
        "Forbidden" exception to be raised.

        The following assertions occur:
            - Expecting the Forbidden Exception to be raised.
        """
        with self.assertRaises(Forbidden):
            self.servers_client.create_image(
                self.server.id, self.image_name, metadata=self.metadata)
