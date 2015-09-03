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
import time

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

    Child classes can over-ride the definition of constant NAMES_PREFIX, that
    is used by methods that create resources like networks or instances
    """

    NAMES_PREFIX = 'neutron_scenario'

    @classmethod
    def _create_network_with_subnet(cls, name, cidr, allocation_pools=None,
                                    gateway_ip=None):
        create_name = '{}_{}'.format(rand_name(cls.NAMES_PREFIX), name)
        network = cls.net.behaviors.networks_behaviors.create_network(
            name=create_name,
            use_exact_name=True).response.entity
        cls.delete_networks.append(network.id)
        subnet = cls.net.behaviors.subnets_behaviors.create_subnet(
            network.id, name=create_name, ip_version=cls.ip_version,
            cidr=cidr, allocation_pools=allocation_pools,
            gateway_ip=gateway_ip, use_exact_name=True).response.entity
        cls.delete_subnets.append(subnet.id)
        return network, subnet

    @classmethod
    def _create_server(cls, name, isolated_networks_to_connect=None,
                       public_and_service=True, security_groups=None,
                       scheduler_hints=None):
        isolated_networks_to_connect = isolated_networks_to_connect or []
        security_groups = security_groups or []
        networks = [{'uuid': net.id} for net in isolated_networks_to_connect]
        if public_and_service:
            networks.append({'uuid': cls.public_network_id})
            networks.append({'uuid': cls.service_network_id})
        nova_secgroups = [{"name": secgroup.name} for secgroup in
                          security_groups]
        server = cls.compute.servers.behaviors.create_active_server(
            name='{}_{}'.format(rand_name(cls.NAMES_PREFIX), name),
            key_name=cls.keypair.name, networks=networks,
            security_groups=nova_secgroups,
            scheduler_hints=scheduler_hints).entity
        cls.delete_servers.append(server.id)
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
        cls.keypair = cls.compute.keypairs.client.create_keypair(name).entity
        cls.resources.add(name, cls.compute.keypairs.client.delete_keypair)

    @classmethod
    def _get_remote_client(cls, server):
        ip_address = cls.compute.servers.behaviors.get_public_ip_address(
            server.entity)
        remote_client = \
            cls.compute.servers.behaviors.get_remote_instance_client(
                server.entity,
                ip_address=ip_address, username='root',
                key=cls.keypair.private_key,
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

    @classmethod
    def _create_empty_security_group(cls, name):
        """
        @summary: Creates an empty security group
        @param name: A string that will be part of the security group name
        @type secgroup_id: string
        @return: security group
        @rtype: security group entity
        """
        sg_name = '{}_{}'.format(rand_name(cls.NAMES_PREFIX), name)
        sg_desc = sg_name + " description"
        resp = cls.security_groups.client.create_security_group(
            name=sg_name, description=sg_desc)
        msg = "Security group create returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        assert resp.status_code == 201, msg
        secgroup = resp.entity
        cls.delete_secgroups.append(secgroup.id)
        msg = ("Security group create returned unexpected security group "
               "name: {}")
        msg = msg.format(secgroup.name)
        assert secgroup.name == sg_name, msg
        msg = ("Security group create returned unexpected security group "
               "description: {}")
        assert secgroup.description == sg_desc, msg
        return secgroup

    @classmethod
    def _get_port_id_owned_by_instance_on_net(cls, instance_id, net_id):
        """
        @summary: Gets the uuid of the port owned by the specified instance on
         the specified network
        @return: port uuid
        @rtype: string
        """
        resp = cls.net.ports.client.list_ports(device_id=instance_id,
                                               network_id=net_id)
        msg = "Ports list returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        assert resp.status_code == 200, msg
        ports = resp.entity
        msg = ("Ports list returned unexpected number of ports given provided "
               "filter. Expected 1 port, {0} returned")
        msg = msg.format(len(ports))
        assert len(ports) == 1, msg
        return ports[0].id

    def _update_port_secgroups(self, port_id, security_groups_ids):
        resp = self.net.ports.client.update_port(
            port_id, security_groups=security_groups_ids)
        msg = "Port security groups update returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        self.assertEqual(resp.status_code, 200, msg)
        msg = "Port list of security group of unexpected length: {}"
        msg = msg.format(len(resp.entity.security_groups))
        self.assertEqual(len(resp.entity.security_groups),
                         len(security_groups_ids), msg)
        msg = "Missing security group after port update: {}"
        for secgroup_id in security_groups_ids:
            self.assertIn(secgroup_id, resp.entity.security_groups,
                          msg.format(secgroup_id))
        time.sleep(self.security_groups.config.data_plane_delay)

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
