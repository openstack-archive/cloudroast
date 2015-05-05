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
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes, NeutronErrorTypes
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture


class ServersBootTestWithNetworkIPv6(NetworkingComputeFixture):

    @tags('servers', 'positive', 'rbac_creator')
    def test_server_boot_w_ipv6_network_id(self):
        """
        @summary: Booting a server with network id from a network with an
                  IPv6 subnet
        """
        network = self.create_network()
        subnet = self.create_subnet(network_id=network.id, ip_version=6)

        network_ids = [self.public_network_id, self.service_network_id,
                       network.id]
        resp = self.net.behaviors.create_networking_server(
            network_ids=network_ids)
        server = resp.entity
        self.delete_servers.append(server.id)

        # Check Public, Servicenet and Isolated networks on server
        self.assertServerNetworkByName(server=server, network_name='public',
                                       ipv4=True, ipv6=True)
        self.assertServerNetworkByName(server=server, network_name='private',
                                       ipv4=True, ipv6=False)
        self.assertServerNetworkByName(server=server,
                                       network_name=network.name, ipv4=False,
                                       ipv6=True, ipv4_cidr=subnet.cidr)

        # Check the server has the expected ports
        publicnet_port = self.ports.behaviors.list_ports(
            device_id=server.id, network_id=self.public_network_id)
        servicenet_port = self.ports.behaviors.list_ports(
            device_id=server.id, network_id=self.service_network_id)
        isolatednet_port = self.ports.behaviors.list_ports(
            device_id=server.id, network_id=network.id)

        results = []
        failure_msg = ('Unable to get server {0} port for network {1}. '
                       'Failures: {2}.')
        if publicnet_port.failures:
            msg = failure_msg.format(server.id, self.public_network_id,
                                     publicnet_port.failures)
            results.append(msg)
        if servicenet_port.failures:
            msg = failure_msg.format(server.id, self.service_network_id,
                                     servicenet_port.failures)
            results.append(msg)
        if isolatednet_port.failures:
            msg = failure_msg.format(server.id, network.id,
                                     isolatednet_port.failures)
            results.append(msg)

        # Fail the test if any failure is found
        self.assertFalse(results)
