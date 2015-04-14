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


class ServersTest(NetworkingComputeFixture):

    @classmethod
    def setUpClass(cls):
        """Testing server instances"""
        super(ServersTest, cls).setUpClass()

    @tags('servers', 'positive', 'creator')
    def test_server_boot_w_ipv6_port_id(self):
        """
        @summary: Booting a server with port_id from an IPv6 port
        """
        network = self.create_network()
        subnet = self.create_subnet(network_id=network.id, ip_version=6)
        port = self.create_port(network_id=network.id)

        port_ids = [port.id]
        network_ids = [self.public_network_id, self.service_network_id]
        resp = self.net.behaviors.create_networking_server(
            network_ids=network_ids, port_ids=port_ids)
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

        # Check the server id is at the port device_id and the device_owner
        # is set to compute:None after the server is booted with the port
        expected_port = port
        expected_port.device_id = server.id
        expected_port.device_owner = 'compute:None'
        get_port_req = self.ports.behaviors.get_port(port_id=port.id)

        # Fail the test if any failure is found
        self.assertFalse(get_port_req.failures)
        updated_port = get_port_req.response.entity

        # Check the Port response
        self.assertPortResponse(expected_port, updated_port,
                                check_fixed_ips=True)
