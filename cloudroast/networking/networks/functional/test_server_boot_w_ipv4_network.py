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
from cloudcafe.networking.networks.personas import ServerPersona
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class ServersBootTestWithNetworkIPv4(NetworkingComputeFixture):

    @tags('servers', 'positive', 'rbac_creator')
    def test_server_boot_w_ipv4_network_id(self):
        """
        @summary: Booting a server with network id from a network with an
                  IPv4 subnet
        """
        network = self.create_network()
        subnet = self.create_subnet(network_id=network.id, ip_version=4)

        network_ids = [self.public_network_id, self.service_network_id,
                       network.id]

        server = self.create_test_server(network_ids=network_ids)

        server_persona = ServerPersona(
            server=server, pnet=True, snet=True, inet=True, network=network,
            subnetv4=subnet, portv4=None, subnetv6=None, portv6=None,
            inet_port_count=1, snet_port_count=1, pnet_port_count=1,
            inet_fix_ipv4_count=1, inet_fix_ipv6_count=0,
            snet_fix_ipv4_count=1, snet_fix_ipv6_count=0,
            pnet_fix_ipv4_count=1, pnet_fix_ipv6_count=1)

        # Setting the isolated network port with updated device owner
        server_persona.portv4 = server_persona.inet_ports[0]

        self.assertServerPersonaNetworks(server_persona)
        self.assertServerPersonaPorts(server_persona)
        self.assertServerPersonaFixedIps(server_persona)
