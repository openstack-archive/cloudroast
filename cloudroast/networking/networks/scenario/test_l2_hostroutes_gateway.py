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

from IPy import IP
import re

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudroast.networking.networks.fixtures import NetworksScenarioFixture
from cloudcafe.compute.common.types import InstanceAuthStrategies

NAMES_PREFIX = 'l2_hostroutes_gateway'
PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'


class Instance(object):

    def __init__(self, entity, isolated_ips, remote_client):
        self.entity = entity
        for network_name, ip in isolated_ips.items():
            setattr(self, network_name, ip)
        self.remote_client = remote_client


class L2HostroutesGatewayTest(NetworksScenarioFixture):

    """
    This test verifies that host routes specified for Neutron subnets allow
    vm's to route data traffic between said subnets. In doing so, operations
    on the three basic Neutron abstractions are exercised: networks, subnets
    and ports.

    The following is the scenario outline:
    1. Two networks / subnets are created with non overlapping cidr's. One of
       the networks is considered the 'origin' and the other is considered the
       'destination'.
    2. A 'router' vm is created and connected to both networks, 'origin' and
       'destination'.
    3. The 'origin' subnet is updated with a host route specifying the
       'router's port on that subnet as the nexthop for the 'destination'
       network.
    4. A vm is created and connected only to the 'origin' network.
    5. A vm is created and connected only to the 'destination' network.
    6. ip forwarding is enabled in the 'router' vm
    7. The test verifies that the vm connected only to the 'origin' network
       can ping the the vm connected only to the 'destination' network.
    8. The test verifies that the vm connected only to the 'destination'
       network cannot ping the vm connected to the 'origin' network.
    """

    PING_COMMAND = 'ping -c 3 {}'
    ip_version = 4
    base_cidr = '172.16.0.0/24'

    @classmethod
    def setUpClass(cls):
        super(L2HostroutesGatewayTest, cls).setUpClass()
        cls.network_with_route = None
        cls.subnet_with_route = None
        cls.destination_network = None
        cls.destination_subnet = None
        cls.keypair = None
        cls.router = None
        cls.origin = None
        cls.destination = None

    def _create_networks(self):
        network, subnet = self._create_network_with_subnet('destination',
                                                           self.base_cidr)
        self.destination_network = network
        self.destination_subnet = subnet

        # Create a network and subnet with explicit allocation pools
        ip_base_cidr = IP(self.base_cidr)
        next_cidr_1st_ip = ip_base_cidr[0].ip + len(ip_base_cidr)
        next_cidr = IP('{}/{}'.format(str(next_cidr_1st_ip),
                                      str(ip_base_cidr.prefixlen())))
        allocation_pools = [{"start": str(IP(next_cidr[1].ip)),
                             "end": str(IP(next_cidr[-2].ip))}]
        network, subnet = self._create_network_with_subnet(
            'with_route', str(next_cidr), allocation_pools)
        self.network_with_route = network
        self.subnet_with_route = subnet

    def _create_network_with_subnet(self, name, cidr, allocation_pools=None):
        create_name = '{}_{}'.format(rand_name(NAMES_PREFIX), name)
        network, _ = self.networks_behaviors.create_network(
            name=create_name,
            use_exact_name=True)
        self.resources.add(network.id, self.networks_client.delete_network)
        subnet, _ = self.subnets_behaviors.create_subnet(
            network.id, name=create_name, ip_version=self.ip_version,
            cidr=cidr, allocation_pools=allocation_pools,
            use_exact_name=True)
        self.resources.add(subnet.id, self.subnets_client.delete_subnet)

        # If allocation pools were explicitely requested, confirm they were
        # created correctly
        if allocation_pools:
            msg = ("Explicit allocation pools requested in subnet creation "
                   "could not be confirmed in Neutron response")
            expected_allocation_pools = set(
                tuple(x.items()) for x in allocation_pools)
            for pool in subnet.allocation_pools:
                self.assertTrue(tuple(pool.items()) in
                                expected_allocation_pools, msg)
        return network, subnet

    def _create_keypair(self):
        name = rand_name(NAMES_PREFIX)
        self.keypair = self.keypairs_client.create_keypair(name).entity
        self.resources.add(name, self.keypairs_client.delete_keypair)

    def _create_router(self):
        # TODO remove return and self.destination_network from call to
        # _create_server
        self.router = self._create_server('router', [self.network_with_route,
                                                     self.destination_network])
        return

        # Attach router to a port in the destination network
        port, _ = self.ports_behaviors.create_port(
            self.destination_network.id,
            name='{}_{}'.format(rand_name(NAMES_PREFIX), 'attached_port'),
            device_id=self.router.entity.id, use_exact_name=True)
        self.resources.add(port.id, self.ports_client.delete_port)
        msg = ("Port not attached to nova instance after port creation. Port "
               "creation request specified instance uuid in device_id "
               "attribute")
        self.assertEqual(self.router.entity.id, port.device_id, msg)
        # TODO get instance details and confirm port was attached. ssh into
        # instance and confirm new interface is found with ifconfig

    def _enable_ip_forwarding(self, ssh_client):
        # Always accept loopback traffic
        ssh_client.execute_command('iptables -A INPUT -i lo -j ACCEPT')

        # Allow established connections, and those not coming from the outside
        ssh_client.execute_command(
            'iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
        ssh_client.execute_command(
            'iptables -A INPUT -m state --state NEW ! -i eth3 -j ACCEPT')
        ssh_client.execute_command(
            ('iptables -A FORWARD -i eth3 -o eth2 -m state --state '
             'ESTABLISHED,RELATED -j ACCEPT'))

        # Allow outgoing connections from the network with routes side
        ssh_client.execute_command(
            'iptables -A FORWARD -i eth2 -o eth3 -j ACCEPT')

        # Masquerade
        ssh_client.execute_command(
            'iptables -t nat -A POSTROUTING -o eth3 -j MASQUERADE')

        # Don't forward from the destination network to the network with routes
        ssh_client.execute_command(
            'iptables -A FORWARD -i eth3 -o eth2 -j REJECT')

        # Enable ip forwarding
        ssh_client.execute_command('echo 1 > /proc/sys/net/ipv4/ip_forward')

    def _create_communicating_servers(self):
        self.origin = self._create_server('origin', [self.network_with_route])
        self.destination = self._create_server('destination',
                                               [self.destination_network])

        # Confirm routes are setup correctly in origin server
        destination = self.destination_subnet.cidr[
            :self.destination_subnet.cidr.rindex('/')]
        route_cmd = 'route -n | grep {}'.format(destination)
        route = self.origin.remote_client.ssh_client.execute_command(
            route_cmd).stdout.split(' ')
        msg = "Expected route was not found in 'origin' server"
        self.assertEqual(destination, route[0], msg)
        self.assertIn(
            getattr(self.router, self.network_with_route.name),
            route, msg)

        # Confirm routes are setup correctly in destination server
        origin = self.subnet_with_route.cidr[
            :self.subnet_with_route.cidr.rindex('/')]
        route_cmd = 'route -n | grep {}'.format(origin)
        route = self.destination.remote_client.ssh_client.execute_command(
            route_cmd).stdout
        msg = "Unexpected route was found in 'destination' server"
        self.assertFalse(route, msg)

    def _create_server(self, name, isolated_networks_to_connect):
        networks = []
        for network in isolated_networks_to_connect:
            networks.append({'uuid': network.id})
        networks.append({'uuid': self.publicnet_id})
        networks.append({'uuid': self.servicenet_id})
        server = self.server_behaviors.create_active_server(
            name='{}_{}'.format(rand_name(NAMES_PREFIX), name),
            key_name=self.keypair.name,
            networks=networks).entity
        self.resources.add(server.id, self.servers_client.delete_server)
        isolated_ips = self._get_server_isolated_ips(
            server, isolated_networks_to_connect)
        public_ip = self.server_behaviors.get_public_ip_address(server)
        remote_client = self.server_behaviors.get_remote_instance_client(
            server, ip_address=public_ip, username='root',
            key=self.keypair.private_key,
            auth_strategy=InstanceAuthStrategies.KEY)
        return Instance(server, isolated_ips, remote_client)

    def _get_server_isolated_ips(self, server, isolated_networks):
        ips = {}
        for net in isolated_networks:
            ips[net.name] = getattr(server.addresses,
                                    net.name).addresses[0].addr
        return ips

    def _set_host_routes(self):
        self.subnets_client.update_subnet(
            self.subnet_with_route.id,
            host_routes=[{"destination": self.destination_subnet.cidr,
                          "nexthop": getattr(self.router,
                                             self.network_with_route.name)}])

    def _ping(self, ssh_client, ip_address):
        ping_cmd = self.PING_COMMAND.format(ip_address)
        output = ssh_client.execute_command(ping_cmd)
        try:
            packet_loss_percent = re.search(PING_PACKET_LOSS_REGEX,
                                            output.stdout).group(1)
        except Exception:
            return False
        return packet_loss_percent != '100'

    def _verify_expected_connectivity(self):
        msg = ("Connectivity doesn't exist between two instances in two "
               "separate isolated networks connected with a router. Host "
               "routes were set up to enable this connectivity")
        self.assertTrue(self._ping(
            self.origin.remote_client.ssh_client,
            getattr(self.destination, self.destination_network.name)), msg)
        msg = ("Connectivity exists unexpectedly between two instances in two "
               "separate isolated networks connected with a router. Host "
               "routes were not set up to enable this connectivity")
        self.assertFalse(self._ping(
            self.destination.remote_client.ssh_client,
            getattr(self.origin, self.network_with_route.name)), msg)

    @tags(type='positive', net='yes')
    def test_execute(self):
        self._create_networks()
        self._create_keypair()
        self._create_router()
        self._set_host_routes()
        self._create_communicating_servers()
        self._enable_ip_forwarding(self.router.remote_client.ssh_client)
        self._verify_expected_connectivity()
