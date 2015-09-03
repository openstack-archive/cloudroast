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

from IPy import IP
import re
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.extensions.ip_associations_api.composites \
    import IPAssociationsComposite
from cloudcafe.networking.networks.extensions.ip_addresses_api.composites \
    import IPAddressesComposite
from cloudcafe.networking.networks.extensions.security_groups_api.composites \
    import SecurityGroupsComposite
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.scenario.common import \
    ScenarioMixin


class SharedIPsTest(NetworkingComputeFixture, ScenarioMixin):

    """
    """

    PRIVATE_KEY_PATH = '/root/pkey'

    @classmethod
    def setUpClass(cls):
        super(SharedIPsTest, cls).setUpClass()
        cls.shared_ips = IPAddressesComposite()
        cls.ip_associations = IPAssociationsComposite()
        cls.security_groups = SecurityGroupsComposite()

    def _create_isolated_network(self):
        network, subnet = self._create_network_with_subnet('isolated',
                                                           self.base_cidr)
        self.isolated_network = network
        self.isolated_subnet = subnet

    def _get_ip_zone_near_option_hint(self, marker):
        return {"different_host": marker.entity.id,
                "public_ip_zone:near": marker.entity.id}

    def _create_web_servers(self):
        self.master = self._create_server('master', [self.isolated_network])
        self.slave = self._create_server(
            'slave', [self.isolated_network],
            scheduler_hints=self._get_ip_zone_near_option_hint(self.master))
        self.client = self._create_server('client', [self.isolated_network])
        self.shared_ip = self._create_shared_ip([self.master.entity.id,
                                                 self.slave.entity.id])
        self._associate_shared_ip(self.shared_ip, self.master)
        self._associate_shared_ip(self.shared_ip, self.slave)
        ssh_client = self._get_remote_client(self.master).ssh_client
        self._configure_web_server(self.master,
                                   self._get_server_ip(self.slave),
                                   ssh_client)
        ssh_client = self._get_remote_client(self.slave).ssh_client
        self._configure_web_server(self.slave,
                                   self._get_server_ip(self.master),
                                   ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

        # Copy the private key of the keypair created previously to the slave
        # server. This will enable failing and restoring interfaces in the
        # master slave
        ssh_client = self._get_remote_client(self.client).ssh_client
        remote_file_path = '/root/pkey'
        self._transfer_private_key_to_vm(ssh_client, self.keypair.private_key,
                                         remote_file_path)
        self.ssh_command_stub = ('ssh -o UserKnownHostsFile=/dev/null '
                                 '-o StrictHostKeyChecking=no -i {} root@')
        self.ssh_command_stub = self.ssh_command_stub.format(remote_file_path)

    def _get_server_ip(self, server):
        raise NotImplementedError

    def _get_server_interface(self):
        raise NotImplementedError

    def _create_shared_ip(self, instances):
        raise NotImplementedError

    def _get_master_vip_port_id(self):
        raise NotImplementedError

    def _create_shared_ip_with_net_id(self, net_id, ip_version, instances_ids):
        resp = self.shared_ips.client.create_ip_address(
            network_id=net_id, version=ip_version, device_ids=instances_ids)
        msg = "Shared ip create returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        self.assertEqual(resp.status_code, 200, msg)
        shared_ip = resp.entity
        msg = "Shared ip create returned unexpected network_id: {}"
        msg = msg.format(shared_ip.network_id)
        self.assertEqual(shared_ip.network_id, net_id, msg)
        msg = "Shared ip create returned unexpected version: {}"
        msg = msg.format(shared_ip.version)
        self.assertEqual(shared_ip.version, ip_version, msg)
        return shared_ip

    def _get_sed_command_for_haresources(self, master_name, shared_address):
        cmd = ("sed -e 's/xxxx/{} {}/' haresources "
               ">/etc/heartbeat/haresources").format(master_name,
                                                     shared_address)
        return cmd

    def _configure_web_server(self, server, other_ip_address, ssh_client):
        # This method assumes that heartbeat and apache are pre-installed
        self._execute_ssh_command(ssh_client,
                                  'cp authkeys /etc/heartbeat/authkeys')
        self._execute_ssh_command(ssh_client,
                                  'chmod 600 /etc/heartbeat/authkeys')
        shared_address = IP(self.shared_ip.address).strNormal()
        master_name = self.master.entity.name.replace('_', '-')
        cmd = self._get_sed_command_for_haresources(master_name,
                                                    shared_address)
        self._execute_ssh_command(ssh_client, cmd)
        cmd = "sed -e '/ucast/s/xxxx/{} {}/' ha.cf > ha1.cf".format(
            self._get_server_interface(), other_ip_address)
        self._execute_ssh_command(ssh_client, cmd)
        cmd = "sed -e 's/master/{}/' ha1.cf > ha2.cf".format(master_name)
        self._execute_ssh_command(ssh_client, cmd)
        slave_name = self.slave.entity.name.replace('_', '-')
        cmd = ("sed -e 's/slave/{}/' ha2.cf "
               ">/etc/heartbeat/ha.cf").format(slave_name)
        self._execute_ssh_command(ssh_client, cmd)
        self._execute_ssh_command(
            ssh_client, 'echo $(hostname) > /var/www/html/index.html')
        self._restart_linux_service(
            ssh_client, 'heartbeat',
            'Starting High-Availability services: Done')
        self._restart_linux_service(
            ssh_client, 'apache2',
            '* Restarting web server apache2\n   ...done.')

    def _restart_linux_service(self, ssh_client, service, expected_response):
        cmd = 'service {} restart'.format(service)
        response = ssh_client.execute_command(cmd)
        if expected_response not in response.stdout:
            msg = 'Unexpected response received restarting service {}: {}'
            msg = msg.format(service, response.stdout)
            self.fail(msg)

    def _associate_shared_ip(self, shared_ip, instance):
        resp = self.ip_associations.client.create_ip_association(
            instance.entity.id, self.shared_ip.id)
        msg = "Shared ip associate returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        self.assertEqual(resp.status_code, 200, msg)
        msg = "Shared ip associate returned unexpected ip address: {}"
        msg = msg.format(resp.entity.address)
        self.assertEqual(resp.entity.address, self.shared_ip.address, msg)

    def _execute_command_remotely(self, remote_instance_address, command,
                                  ssh_client):
        ssh_cmd = '{}{} {}'.format(
            self.ssh_command_stub, remote_instance_address, command)
        return self._execute_ssh_command(ssh_client, ssh_cmd)

    def _turn_interface_off(self, interface, ssh_client):
        ifconfig_cmd = 'ifconfig {} down'.format(interface)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, ifconfig_cmd,
            ssh_client)

    def _turn_interface_on(self, interface, ssh_client):
        ifconfig_cmd = 'ifconfig {} up'.format(interface)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, ifconfig_cmd,
            ssh_client)

    def _get_curl_command(self):
        raise NotImplementedError

    def _mark_resources_to_keep_on_failure(self):
        self.failed_servers.extend(self.delete_servers)
        self.failed_networks.extend(self.delete_networks)
        self.failed_subnets.extend(self.delete_subnets)

    def _do_get_from_shared_ip(self, server):
        cmd = self._get_curl_command()
        for i in range(3):
            ssh_client = self._get_remote_client(self.client).ssh_client
            response = ssh_client.execute_command(cmd)
            if not response.stderr:
                self.assertEqual(response.stdout.strip(),
                                 server.entity.name.replace('_', '-'))
                return
            else:
                if 'port 80: No route to host' in response.stderr:
                    time.sleep(60)
                else:
                    msg = ('Unexpected error when executing GET from shared '
                           'ip: {}'.format(response.stderr))
                    self.fail(msg)
        self._mark_resources_to_keep_on_failure()
        self.fail('Timed out executing GET from shared ip. No route to host')

    def _fail_interface_listening_to_slave(self):
        raise NotImplementedError

    def _restore_interface_listening_to_slave(self):
        raise NotImplementedError

    def _test_failover(self):
        # Verify master is receiving requests sent to shared ip
        self._do_get_from_shared_ip(self.master)

        # Fail master's interface used to listen to slave and verify slave
        # responds to requests
        self._fail_interface_listening_to_slave()
        self._do_get_from_shared_ip(self.slave)

        # Restore master's interface to listen to slave  and verify it responds
        # to requests
        self._restore_interface_listening_to_slave()
        self._do_get_from_shared_ip(self.master)

    def _test_execute(self):
        self._create_isolated_network()
        self._create_keypair()
        self._create_web_servers()
        self._test_failover()


class SharedIPsTestPublicNetworkIPv4(SharedIPsTest):

    """
    """

    NAMES_PREFIX = 'shared_ips_pnet_ipv4'

    @classmethod
    def setUpClass(cls):
        super(SharedIPsTestPublicNetworkIPv4, cls).setUpClass()

        # Get a base cidr for test from the configuration file
        cls.base_cidr = ''.join(
            [cls.net.subnets.config.ipv4_prefix, '/',
             str(cls.net.subnets.config.ipv4_suffix)])
        cls.ip_version = IP(cls.base_cidr).version()

    def _get_server_ip(self, server):
        return server.entity.addresses.public.ipv4

    def _get_server_interface(self):
        return 'eth0'

    def _create_shared_ip(self, instances_ids):
        return self._create_shared_ip_with_net_id(
            self.public_network_id, self.ip_version, instances_ids)

    def _get_master_vip_port_id(self):
        return self._get_port_id_owned_by_instance_on_net(
            self.master.entity.id, self.public_network_id)

    def _get_curl_command(self):
        url = 'http://{}'.format(self.shared_ip.address)
        return 'curl --silent --show-error {}'.format(url)

    def _fail_interface_listening_to_slave(self):
        ssh_client = self._get_remote_client(self.client).ssh_client
        interface = self._get_server_interface()
        # Remember default ipv4 route
        output = self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4,
            'route | grep default', ssh_client)
        self.gateway_ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)[0]

        self._turn_interface_off(interface, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

    def _restore_interface_listening_to_slave(self):
        ssh_client = self._get_remote_client(self.client).ssh_client
        interface = self._get_server_interface()
        self._turn_interface_on(interface, ssh_client)

        # Restore default ipv4 route
        route_cmd = 'route add default gw {}'.format(self.gateway_ipv4)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, route_cmd, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

    @tags(type='positive', net='yes')
    def test_execute_pnet_ipv4(self):
        self._test_execute()


class SharedIPsTestIsolatedNetwork(SharedIPsTest):

    """
    """

    NAMES_PREFIX = 'shared_ips_isolated'

    @classmethod
    def setUpClass(cls):
        super(SharedIPsTestIsolatedNetwork, cls).setUpClass()

        # Get a base cidr for test from the configuration file
        cls.base_cidr = ''.join(
            [cls.net.subnets.config.ipv4_prefix, '/',
             str(cls.net.subnets.config.ipv4_suffix)])
        cls.ip_version = IP(cls.base_cidr).version()

    def _get_server_ip(self, server):
        return getattr(server, self.isolated_network.name)

    def _get_server_interface(self):
        return 'eth2'

    def _create_shared_ip(self, instances_ids):
        return self._create_shared_ip_with_net_id(self.isolated_network.id,
                                                  self.ip_version,
                                                  instances_ids)

    def _get_master_vip_port_id(self):
        return self._get_port_id_owned_by_instance_on_net(
            self.master.entity.id, self.isolated_network.id)

    def _get_curl_command(self):
        url = 'http://{}'.format(self.shared_ip.address)
        return 'curl --silent --show-error {}'.format(url)

    def _fail_interface_listening_to_slave(self):
        ssh_client = self._get_remote_client(self.client).ssh_client
        interface = self._get_server_interface()
        self._turn_interface_off(interface, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, 'ifconfig eth0:0 down',
            ssh_client)

    def _restore_interface_listening_to_slave(self):
        ssh_client = self._get_remote_client(self.client).ssh_client
        interface = self._get_server_interface()
        self._turn_interface_on(interface, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

    @tags(type='positive', net='yes')
    def test_execute_isolated_net(self):
        self._test_execute()


class SharedIPsTestPublicNetworkIPv6(SharedIPsTest):

    """
    """

    NAMES_PREFIX = 'shared_ips_pnet_ipv6'

    @classmethod
    def setUpClass(cls):
        super(SharedIPsTestPublicNetworkIPv6, cls).setUpClass()

        # Get a base cidr for test from the configuration file
        cls.base_cidr = ''.join(
            [cls.net.subnets.config.ipv6_prefix, '/',
             str(cls.net.subnets.config.ipv6_suffix)])
        cls.ip_version = IP(cls.base_cidr).version()

    def _get_server_ip(self, server):
        return server.entity.addresses.public.ipv4

    def _get_server_interface(self):
        return 'eth0'

    def _create_shared_ip(self, instances_ids):
        return self._create_shared_ip_with_net_id(
            self.public_network_id, self.ip_version, instances_ids)

    def _get_master_vip_port_id(self):
        return self._get_port_id_owned_by_instance_on_net(
            self.master.entity.id, self.public_network_id)

    def _get_curl_command(self):
        url = '{}'.format(self.shared_ip.address)
        return 'curl --silent --show-error -g [{}]'.format(url)

    def _get_sed_command_for_haresources(self, master_name, shared_address):
        cmd = ("sed -e 's_xxxx/24_{} IPv6addr::{}/64/eth0_' haresources "
               ">/etc/heartbeat/haresources").format(master_name,
                                                     shared_address)
        return cmd

    def _fail_interface_listening_to_slave(self):
        ssh_client = self._get_remote_client(self.client).ssh_client
        interface = self._get_server_interface()
        # Remember default ipv4 route
        output = self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, 'route | grep default',
            ssh_client)
        self.gateway_ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)[0]

        self._turn_interface_off(interface, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

    def _restore_interface_listening_to_slave(self):
        split = self.shared_ip.address.split(':')
        network_prefix = '{}:{}:{}:{}::'.format(split[0], split[1], split[2],
                                                split[3])
        interface = self._get_server_interface()
        ssh_client = self._get_remote_client(self.client).ssh_client

        # Restore ipv6 routes
        route_cmd = 'route -A inet6 add {}/64 metric 256 dev {}'.format(
            network_prefix, interface)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, route_cmd, ssh_client)
        route_cmd = 'route -A inet6 add ::/0 gw {}1 metric 1024'.format(
            network_prefix)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, route_cmd, ssh_client)

        self._turn_interface_on(interface, ssh_client)

        # Restore default ipv4 route
        route_cmd = 'route add default gw {}'.format(self.gateway_ipv4)
        self._execute_command_remotely(
            self.master.entity.addresses.private.ipv4, route_cmd, ssh_client)

        # Wait for cluster to stabilize
        time.sleep(60)

    @tags(type='positive', net='yes')
    def test_execute_pnet_ipv6(self):
        self._test_execute()


class SharedIPsCleanup(NetworkingComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(SharedIPsCleanup, cls).setUpClass()
        cls.shared_ips = IPAddressesComposite()

    def test_cleanup_shared_ips(self):
        resp = self.shared_ips.client.list_ip_addresses(type_='shared')
        msg = "Shared ips list returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        self.assertEqual(resp.status_code, 200, msg)
        list_shared_ips = resp.entity
        for ip in list_shared_ips:
            resp = self.shared_ips.client.delete_ip_address(ip.id)
            msg = "Shared ip delete returned unexpected status code: {}"
            msg = msg.format(resp.status_code)
            self.assertEqual(resp.status_code, 204, msg)
