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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.networking.fixtures import NetworkingFixture


class NetworksTest(NetworkingFixture):

    @tags(type='positive', net='yes')
    def test_create_network(self):
        """
        Creates a network and verifies name in response is the expectec one
        """
        name = rand_name('test_network')
        response = self.nets_subnets_ports_client.create_network(name)
        network = response.entity
        self.resource.add(network.id,
                          self.nets_subnets_ports_client.delete_network)
        self.assertEqual(name, network.name)
