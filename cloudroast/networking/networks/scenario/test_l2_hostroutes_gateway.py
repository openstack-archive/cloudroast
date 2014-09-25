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
import os
import re

from cafe.drivers.unittest.decorators import tags
from cafe.engine.config import EngineConfig
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import InstanceAuthStrategies
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture

NAMES_PREFIX = 'l2_hostroutes_gateway'
PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'


class Instance(object):

    def __init__(self, entity, isolated_ips, remote_client):
        self.entity = entity
        for network_name, ip in isolated_ips.items():
            setattr(self, network_name, ip)
        self.remote_client = remote_client


class L2HostroutesGatewayMixin(object):

    """
    This class provides utility methods for the test classes in this module
    """

    @classmethod
    def _create_network_with_subnet(cls, name, cidr, allocation_pools=None,
                                    gateway_ip=None):
        create_name = '{}_{}'.format(rand_name(NAMES_PREFIX), name)
        network = cls.networks_behaviors.create_network(
            name=create_name,
            use_exact_name=True).response.entity
        cls.delete_networks.append(network.id)
        subnet = cls.subnets_behaviors.create_subnet(
            network.id, name=create_name, ip_version=cls.ip_version,
            cidr=cidr, allocation_pools=allocation_pools,
            gateway_ip=gateway_ip, use_exact_name=True).response.entity
        cls.delete_subnets.append(subnet.id)
        return network, subnet

    @classmethod
    def _create_server(cls, name, isolated_networks_to_connect,
                       public_and_service=True):
        networks = [{'uuid': net.id} for net in isolated_networks_to_connect]
        if public_and_service:
            networks.append({'uuid': cls.public_network_id})
            networks.append({'uuid': cls.service_network_id})
        server = cls.server_behaviors.create_active_server(
            name='{}_{}'.format(rand_name(NAMES_PREFIX), name),
            key_name=cls.keypair.name,
            networks=networks).entity
        cls.resources.add(server.id, cls.servers_client.delete_server)
        isolated_ips = cls._get_server_isolated_ips(
            server, isolated_networks_to_connect)
        remote_client = None
        if public_and_service:
            public_ip = cls.server_behaviors.get_public_ip_address(server)
            remote_client = cls.server_behaviors.get_remote_instance_client(
                server, ip_address=public_ip, username='root',
                key=cls.keypair.private_key,
                auth_strategy=InstanceAuthStrategies.KEY)
        return Instance(server, isolated_ips, remote_client)

    @classmethod
    def _get_server_isolated_ips(cls, server, isolated_networks):
        ips = {}
        for net in isolated_networks:
            ips[net.name] = getattr(server.addresses,
                                    net.name).addresses[0].addr
        return ips

    @classmethod
    def _create_keypair(cls):
        name = rand_name(NAMES_PREFIX)
        cls.keypair = cls.keypairs_client.create_keypair(name).entity
        cls.resources.add(name, cls.keypairs_client.delete_keypair)

    def _next_sequential_cidr(self, cidr):
        """
        @summary: Computes the next sequential contiguous cidr to the one
          provided as input. Both cidr's will have the same prefix size
        @param cidr: A cidr that will be used as the base to compute the next
          contiguous one
        @type cidr: IPy.IP
        @return: next contigous cidr
        @rtype: IPy.IP
        """
        next_cidr_1st_ip = cidr[0].ip + len(cidr)
        return IP('{}/{}'.format(str(next_cidr_1st_ip),
                                 str(cidr.prefixlen())))


class L2HostroutesGatewayTest(NetworkingComputeFixture,
                              L2HostroutesGatewayMixin):

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
        cls.servers_client = cls.compute.servers.client
        cls.keypairs_client = cls.compute.keypairs.client
        cls.server_behaviors = cls.compute.servers.behaviors
        cls.subnets_client = cls.net.subnets.client
        cls.networks_behaviors = cls.net.behaviors.networks_behaviors
        cls.subnets_behaviors = cls.net.behaviors.subnets_behaviors
        cls.ports_behaviors = cls.net.behaviors.ports_behaviors

    def _create_networks(self):
        network, subnet = self._create_network_with_subnet('destination',
                                                           self.base_cidr)
        msg = ("Subnet found with non null gateway_ip attribute. Subnets "
               "should be created with null gateway_ip attribute by "
               "default")
        self.assertFalse(subnet.gateway_ip, msg)
        self.destination_network = network
        self.destination_subnet = subnet

        # Create a network and subnet with explicit allocation pools
        next_cidr = self._next_sequential_cidr(IP(self.base_cidr))
        allocation_pools = [{"start": str(IP(next_cidr[1].ip)),
                             "end": str(IP(next_cidr[-2].ip))}]
        network, subnet = self._create_network_with_subnet(
            'with_route', str(next_cidr), allocation_pools)
        msg = ("Explicit allocation pools requested in subnet creation "
               "could not be confirmed in Neutron response")
        expected_allocation_pools = set(
            tuple(x.items()) for x in allocation_pools)
        for pool in subnet.allocation_pools:
            self.assertTrue(tuple(pool.items()) in
                            expected_allocation_pools, msg)
        self.network_with_route = network
        self.subnet_with_route = subnet

    def _create_router(self):
        # TODO remove return and self.destination_network from call to
        # _create_server when dev team completes functionallity to attach vif's
        # to nova instances using device_id during port create / update
        self.router = self._create_server('router', [self.network_with_route,
                                                     self.destination_network])
        return

        # Attach router to a port in the destination network
        port = self.ports_behaviors.create_port(
            self.destination_network.id,
            name='{}_{}'.format(rand_name(NAMES_PREFIX), 'attached_port'),
            device_id=self.router.entity.id,
            use_exact_name=True).response.entity
        self.delete_ports.append(port.id)
        msg = ("Port not attached to nova instance after port creation. Port "
               "creation request specified instance uuid in device_id "
               "attribute")
        self.assertEqual(self.router.entity.id, port.device_id, msg)
        # TODO get instance details and confirm port was attached. ssh into
        # instance and confirm new interface is found with ifconfig. This will
        # be added when dev team completes functionallity to attach vif's
        # to nova instances using device_id during port create / update

    def _enable_ip_forwarding(self, ssh_client):
        commands = [
            'iptables -A INPUT -i lo -j ACCEPT',
            'iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT',
            'iptables -A INPUT -m state --state NEW ! -i eth3 -j ACCEPT',
            ('iptables -A FORWARD -i eth3 -o eth2 -m state --state '
             'ESTABLISHED,RELATED -j ACCEPT'),
            'iptables -A FORWARD -i eth2 -o eth3 -j ACCEPT',
            'iptables -t nat -A POSTROUTING -o eth3 -j MASQUERADE',
            'iptables -A FORWARD -i eth3 -o eth2 -j REJECT',
            'echo 1 > /proc/sys/net/ipv4/ip_forward']
        for cmd in commands:
            msg = 'Error executing remote shell command: {}'.format(cmd)
            stderr = ssh_client.execute_command(cmd).stderr
            self.assertFalse(stderr, '{}. Error was: {}'.format(msg, stderr))

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


class GatewayPoliciesTest(NetworkingComputeFixture,
                          L2HostroutesGatewayMixin):

    """
    This class tests several Neutron policies regarding the assignment of
    gateways to networks / subnets and how that is translated to routes in vm's
    connected to those networks / subnets. The methods in this class each test
    one policy. Please refer to the docstring in each method for a description
    of the tested policy
    """

    ip_version = 4
    base_cidr = '172.16.0.0/24'

    @classmethod
    def setUpClass(cls):
        super(GatewayPoliciesTest, cls).setUpClass()
        cls.servers_client = cls.compute.servers.client
        cls.keypairs_client = cls.compute.keypairs.client
        cls.server_behaviors = cls.compute.servers.behaviors
        cls.subnets_client = cls.net.subnets.client
        cls.networks_behaviors = cls.net.behaviors.networks_behaviors
        cls.subnets_behaviors = cls.net.behaviors.subnets_behaviors
        cls.ports_behaviors = cls.net.behaviors.ports_behaviors

        # Create an access network and a gateway server to provide ssh access
        # to all the other servers created by test methods in this class
        cls._create_keypair()
        cls.access_network, cls.access_subnet = (
            cls._create_network_with_subnet('access', cls.base_cidr))
        cls.gateway = cls._create_server('gateway', [cls.access_network])

        # Copy the private key of the keypair created above to the gateway
        # server. Since all the server's in this class will be created with
        # this keypair, the gateway server will be able to execute commands
        # over ssh in all of them
        pkey_file_path = os.path.join(EngineConfig().temp_directory,
                                      'pkey')
        remote_file_path = '/root/pkey'
        with open(pkey_file_path, "w") as private_key_file:
            private_key_file.write(cls.keypair.private_key)
        cls.gateway.remote_client.ssh_client.transfer_file_to(
            pkey_file_path, remote_file_path)
        cls.gateway.remote_client.ssh_client.execute_command(
            'chmod 600 {}'.format(remote_file_path))

        # Create a ssh command stub that will be used in the gateway server to
        # execute commands remotely in the servers created by test methods in
        # this class
        cls.ssh_command_stub = ('ssh -o UserKnownHostsFile=/dev/null '
                                '-o StrictHostKeyChecking=no -i {} root@')
        cls.ssh_command_stub = cls.ssh_command_stub.format(remote_file_path)

    def test_vm_default_route_is_null(self):
        """
        This test verifies that a vm doesn't get a default route if it is
        connected to a subnet with no gateway_ip defined
        """
        vm = self._create_server('vm_with_null_default_route',
                                 [self.access_network],
                                 public_and_service=False)
        ssh_cmd = '{}{} {}'.format(self.ssh_command_stub,
                                   getattr(vm, self.access_network.name),
                                   'route | grep default')
        output = self.gateway.remote_client.ssh_client.execute_command(
            ssh_cmd).stdout
        msg = ('Unexpected default route was found in VM connected to network '
               'without a gateway defined')
        self.assertFalse(output, msg)

    def test_set_gateway_for_vm(self):
        """
        This test verifies that the gateway_ip set for an isolated network
        translates into a the default route in a vm connected to that network.
        It is also verified that only the first network's gateway_ip translates
        into a default route in the created vm
        """
        # Create two networks with explicit gateways
        nets = [None, None]
        cidr = IP(self.base_cidr)
        for i in xrange(2):
            cidr = self._next_sequential_cidr(cidr)
            allocation_pools = [{"start": str(IP(cidr[2].ip)),
                                 "end": str(IP(cidr[-2].ip))}]
            nets[i], _ = self._create_network_with_subnet(
                'with_gateway', str(cidr), allocation_pools=allocation_pools,
                gateway_ip=str(IP(cidr[1].ip)))
            if i == 0:
                expected_gateway_ip = str(IP(cidr[1].ip))

        # Create a vm connected to the two networks with gateways. It will also
        # be connected to the access network, so ssh to it is possible
        nets.append(self.access_network)
        vm = self._create_server('vm_with_default_route', nets,
                                 public_and_service=False)

        # Confirm vm got expected default route
        ssh_cmd = '{}{} {}'.format(self.ssh_command_stub,
                                   getattr(vm, self.access_network.name),
                                   'route | grep default')
        output = self.gateway.remote_client.ssh_client.execute_command(
            ssh_cmd).stdout
        msg = ('Expected default route not found in VM connected to network '
               'with gateway_ip defined')
        self.assertTrue(output, msg)
        msg = ('Default route in VM connected to network does not point to '
               'the gateway defined in the network it is connected to')
        self.assertIn(expected_gateway_ip, output, msg)

    def test_set_gateway_for_vm_with_host_routes(self):
        """
        This test verifies that defining a host route 0.0.0.0/0 for a network
        translates in a default route for vm's connected to that network
        """
        # Create a net and subnet. Define a 0.0.0.0/0 host route for the subnet
        cidr = self._next_sequential_cidr(IP(self.base_cidr))
        allocation_pools = [{"start": str(IP(cidr[2].ip)),
                             "end": str(IP(cidr[-2].ip))}]
        net, subnet = self._create_network_with_subnet(
            'hostroutes', str(cidr),
            allocation_pools=allocation_pools)
        expected_gateway_ip = str(IP(cidr[1].ip))
        self.subnets_client.update_subnet(
            subnet.id,
            host_routes=[{"destination": "0.0.0.0/0",
                          "nexthop": expected_gateway_ip}])

        # Create a vm connected to the network with the gateway. It will also
        # be connected to the access network, so ssh to it is possible
        vm = self._create_server('vm_with_default_route_hostroutes',
                                 [net, self.access_network],
                                 public_and_service=False)

        # Confirm vm got expected default route
        ssh_cmd = '{}{} {}'.format(self.ssh_command_stub,
                                   getattr(vm, self.access_network.name),
                                   'route | grep default')
        output = self.gateway.remote_client.ssh_client.execute_command(
            ssh_cmd).stdout
        msg = ('Expected default route not found in VM connected to network '
               'with gateway_ip defined with host routes')
        self.assertTrue(output, msg)
        msg = ('Default route in VM connected to network does not point to '
               'the gateway defined in the network it is connected to')
        self.assertIn(expected_gateway_ip, output, msg)

    def test_add_route_to_vm_with_host_routes(self):
        """
        This test verifies that defining a host route for a network translates
        to an additional route for vm's connected to that network. It is also
        tested that the vm doesn't get a default route
        """
        # Create a net and subnet. Define a host route for the subnet with
        # nexthop pointing to the .1 address in that subnet
        cidr = self._next_sequential_cidr(IP(self.base_cidr))
        allocation_pools = [{"start": str(IP(cidr[2].ip)),
                             "end": str(IP(cidr[-2].ip))}]
        net, subnet = self._create_network_with_subnet(
            'hostroutes', str(cidr),
            allocation_pools=allocation_pools)
        expected_nexthop = str(IP(cidr[1].ip))
        self.subnets_client.update_subnet(
            subnet.id,
            host_routes=[{"destination": str(cidr),
                          "nexthop": expected_nexthop}])

        # Create a vm connected to the network with the route. It will also
        # be connected to the access network, so ssh to it is possible
        vm = self._create_server('vm_with_default_route_hostroutes',
                                 [net, self.access_network],
                                 public_and_service=False)

        # Confirm vm got expected route
        range_origin = str(IP(cidr[0].ip))
        route_cmd = 'route -n | grep {}'.format(range_origin)
        ssh_cmd = '{}{} {}'.format(self.ssh_command_stub,
                                   getattr(vm, self.access_network.name),
                                   route_cmd)
        output = self.gateway.remote_client.ssh_client.execute_command(
            ssh_cmd).stdout.splitlines()
        msg = ('Expected route not found in VM connected to network with '
               'that route defined')
        for line in output:
            if (line[:len(range_origin)] == range_origin and
               expected_nexthop in line):
                break
        else:
            self.fail(msg)
