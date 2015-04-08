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

import unittest

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.compute.instance_actions.api.test_rescue_server \
    import ServerRescueTests
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


@unittest.skip('Rescue not enabled for boot from volume')
class ServerFromVolumeV2RescueTests(ServerFromVolumeV2Fixture,
                                    ServerRescueTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - Creates a keypair.
            - Creates an active server.
            - Gets flavor details.
        """
        super(ServerFromVolumeV2RescueTests, cls).setUpClass()
        cls.key = cls.keypairs_client.create_keypair(rand_name("key")).entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.create_server(key_name=cls.key.name)
        flavor_response = cls.flavors_client.get_flavor_details(cls.flavor_ref)
        cls.flavor = flavor_response.entity
