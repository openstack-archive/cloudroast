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
import os

from cafe.engine.config import EngineConfig
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import InstanceAuthStrategies

PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'


class Instance(object):

    def __init__(self, entity, isolated_ips, remote_client=None):
        self.entity = entity
        for network_name, ip in isolated_ips.items():
            setattr(self, network_name, ip)
        self.remote_client = remote_client


class ScenarioMixin(object):

    """
    This class provides utility methods for networking scenario tests
    """

    @classmethod
    def _create_network_with_subnet(cls, name, cidr, allocation_pools=None,
                                    gateway_ip=None):
        create_name = '{}_{}'.format(rand_name(cls.NAMES_PREFIX), name)
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
    def _create_server(cls, name, isolated_networks_to_connect=None,
                       public_and_service=True, security_groups=None):
        isolated_networks_to_connect = isolated_networks_to_connect or []
        security_groups = security_groups or []
        networks = [{'uuid': net.id} for net in isolated_networks_to_connect]
        if public_and_service:
            networks.append({'uuid': cls.public_network_id})
            networks.append({'uuid': cls.service_network_id})
        nova_secgroups = [{"name": secgroup.name} for secgroup in
                          security_groups]
        server = cls.server_behaviors.create_active_server(
            name='{}_{}'.format(rand_name(cls.NAMES_PREFIX), name),
            key_name=cls.keypair.name, networks=networks,
            security_groups=nova_secgroups).entity
        cls.resources.add(server.id, cls.servers_client.delete_server)
        isolated_ips = cls._get_server_isolated_ips(
            server, isolated_networks_to_connect)
        return Instance(server, isolated_ips)

    @classmethod
    def _get_server_isolated_ips(cls, server, isolated_networks):
        ips = {}
        for net in isolated_networks:
            ips[net.name] = getattr(server.addresses,
                                    net.name).addresses[0].addr
        return ips

    @classmethod
    def _create_keypair(cls):
        name = rand_name(cls.NAMES_PREFIX)
        cls.keypair = cls.keypairs_client.create_keypair(name).entity
        cls.resources.add(name, cls.keypairs_client.delete_keypair)

    @classmethod
    def _get_remote_client(cls, server):
        remote_client = cls.server_behaviors.get_remote_instance_client(
            server.entity,
            ip_address=cls.server_behaviors.get_public_ip_address(
                server.entity),
            username='root', key=cls.keypair.private_key,
            auth_strategy=InstanceAuthStrategies.KEY)
        return remote_client

    @classmethod
    def _transfer_private_key_to_vm(cls, ssh_client, private_key,
                                    remote_file_path):
        pkey_file_path = os.path.join(EngineConfig().temp_directory, 'pkey')
        with open(pkey_file_path, "w") as private_key_file:
            private_key_file.write(private_key)
        ssh_client.transfer_file_to(pkey_file_path, remote_file_path)
        error = ssh_client.execute_command(
            'chmod 600 {}'.format(remote_file_path)).stderr
        msg = ('Error changing access permission to private key file in '
               'gateway server')
        assert not error, msg

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
        next_cidr_1st_ip = cidr[-1].ip + 1
        return IP('{}/{}'.format(str(next_cidr_1st_ip),
                                 str(cidr.prefixlen())))

    def _execute_ssh_command(self, ssh_client, cmd):
        response = ssh_client.execute_command(cmd)

        # The only acceptable error message is the addition of the destination
        # ip address to the known hosts list. Otherwise, fail the test
        if (response.stderr and
            ('Warning: Permanently added' not in response.stderr or
             'to the list of known hosts' not in response.stderr)):
            msg = 'Error executing command in test instance over ssh: {}'
            msg = msg.format(response.stderr)
            self.fail(msg)

        # Command execution succeeded
        return response.stdout
