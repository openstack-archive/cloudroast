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

from netaddr import IPAddress, IPNetwork
import re
import time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.networking.networks.extensions.security_groups_api.composites \
    import SecurityGroupsComposite
from cloudroast.networking.networks.fixtures import NetworkingComputeFixture
from cloudroast.networking.networks.scenario.common import ScenarioMixin

PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'
IP_FMT = '{}/{}'


class SecurityGroupsTest(NetworkingComputeFixture,
                         ScenarioMixin):

    """
    This test class verifies that the data plane exhibits the behavior
    specified by one or more security groups applied to ports. Each test case
    in this class (methods starting with "_test_") creates and applies security
    groups and rules to ports of a "listener" instance. Once this is done, the
    test case generates network traffic from a "sender" and/or an
    "other_sender" instances. The test case then verifies that only the
    expected traffic reaches the "listener" instance ports, according to the
    rules in the assigned security groups

    This class cannot be executed directly by the CloudCafe runner. Child
    classes, with appropriately named test cases, have to invoke the methods
    starting with "_test_" in this class

    It is assumed that the Linux image used for the test instances use tcp port
    22 for ssh and the default user is root
    """

    NC_OUTPUT_FILE = '/root/nc-output-'
    NC_OUTPUT = 'XXXXX'
    PRIVATE_KEY_PATH = '/root/pkey'

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsTest, cls).setUpClass()
        cls.security_groups = SecurityGroupsComposite()

        # Create the instances for the test cases
        cls._create_keypair()
        cls.open_loginable_secgroup = cls._create_open_loginable_secgroup()
        cls.sender = cls._create_server('sender')
        cls.listener = cls._create_server('listener')
        cls.other_sender = cls._create_server('other-sender')
        cls.sender.remote_client = cls._get_remote_client(cls.sender)
        cls.other_sender.remote_client = cls._get_remote_client(
            cls.other_sender)
        cls.listener.remote_client = None
        cls._transfer_private_key_to_vm(cls.sender.remote_client.ssh_client,
                                        cls.keypair.private_key,
                                        cls.PRIVATE_KEY_PATH)
        cls._transfer_private_key_to_vm(
            cls.other_sender.remote_client.ssh_client,
            cls.keypair.private_key,
            cls.PRIVATE_KEY_PATH)
        cls.listener_port_id = cls._get_listener_port_id()

    @classmethod
    def _get_listener_port_id(cls):
        """
        @summary: Gets the uuid of the listener instance port on public net
        @return: uuid of listener instance port on public net
        @rtype: string
        """
        resp = cls.net.ports.client.list_ports(
            device_id=cls.listener.entity.id, network_id=cls.public_network_id)
        msg = "Ports list returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        assert resp.status_code == 200, msg
        ports = resp.entity
        msg = ("Ports list returned unexpected number of ports given provided "
               "filter. Expected 1 port, {0} returned")
        msg = msg.format(len(ports))
        assert len(ports) == 1, msg
        return ports[0].id

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
    def _create_security_group_rule(cls, secgroup_id, direction, ethertype,
                                    **kwargs):
        """
        @summary: Creates a security group rule
        @param secgroup_id: The uuid of the security group the created rule
          will be part of
        @type secgroup_id: string
        @param direction: 'ingress' or 'egress'
        @type direction: string
        @param ethertype: 'IPv4' or 'IPv6'
        @type ethertype: string
        @param kwargs: Other attributes to be assigned to the security group
          rule per the Neutron API: 'port_range_min', 'port_range_max',
          'protocol', 'remote_group_id', 'remote_ip_prefix'
        @type kwargs: dictionary
        @return: security group rule
        @rtype: security group rule entity
        """
        resp = cls.security_groups.client.create_security_group_rule(
            secgroup_id, direction, ethertype, **kwargs)
        msg = "Security group rule create returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        assert resp.status_code == 201, msg
        secgroup_rule = resp.entity
        cls.delete_secgroups_rules.append(secgroup_rule.id)
        msg = ("Security group rule create returned unexpected security group "
               "id: {}")
        msg = msg.format(secgroup_rule.security_group_id)
        assert secgroup_id == secgroup_rule.security_group_id, msg
        return secgroup_rule

    @classmethod
    def _create_loginable_secgroup_rules(cls, secgroup_id, ethertype,
                                         remote_ip_prefix=None):
        """
        @summary: Creates security group rules that allow ssh and ping
        @param secgroup_id: The uuid of the security group the created rules
          will be part of
        @type secgroup_id: string
        @param ethertype: 'IPv4' or 'IPv6'
        @type ethertype: string
        @param remote_ip_prefix: The ip address prefix that will be allowed to
          ssh and ping
        @type kwargs: string
        @return: security group rule
        @rtype: security group rule entity
        """
        rulesets = [
            dict(
                # ssh
                protocol='tcp',
                port_range_min=22,
                port_range_max=22,
                remote_ip_prefix=remote_ip_prefix,
            ),
            dict(
                # ping
                protocol='icmp',
                remote_ip_prefix=remote_ip_prefix,
            )
        ]

        return cls._create_secgroup_rules_from_rulesets(secgroup_id, ethertype,
                                                        rulesets)

    @classmethod
    def _create_secgroup_rules_from_rulesets(cls, secgroup_id, ethertype,
                                             rulesets):
        """
        @summary: Creates security group rules from a list of dictionaries
        @param secgroup_id: The uuid of the security group the created rules
          will be part of
        @type secgroup_id: string
        @param ethertype: 'IPv4' or 'IPv6'
        @type ethertype: string
        @param rulesets: A list of dictionaries, where each dictionary
          specifies one security group rule
        @type rulestes: list of ductionaries
        @return: security group rules
        @rtype: list of security group rule entities
        """
        rules = []
        msg_template = ("Security group rule create returned unexpected "
                        "direction attribute: {}")
        for ruleset in rulesets:
            for direction in ['ingress', ]:
                sg_rule = cls._create_security_group_rule(secgroup_id,
                                                          direction,
                                                          ethertype,
                                                          **ruleset)
                msg = msg_template.format(sg_rule.direction)
                assert direction == sg_rule.direction, msg
                rules.append(sg_rule)

        return rules

    @classmethod
    def _create_open_loginable_secgroup(cls, secgroup=None):
        """
        @summary: Creates a security group that allows ssh and ping from any
          source. If security group is passed as an argument, the rules of that
          groups are deleted and re-created
        @param secgroup: An existing security group
        @type secgroup: security group entity
        @return: security group
        @rtype: security group entity
        """
        if secgroup:
            resp = cls.security_groups.client.get_security_group(secgroup.id)
            msg = ("Security group rule show returned unexpected status "
                   "code: {}")
            msg = msg.format(resp.status_code)
            assert resp.status_code == 200, msg
            sg = resp.entity
            for rule in sg.security_group_rules:
                resp = cls.security_groups.client.delete_security_group_rule(
                    rule.id)
                msg = ("Security group rule delete returned unexpected status "
                       "code: {}")
                msg = msg.format(resp.status_code)
                assert resp.status_code == 204, msg
        else:
            sg = cls._create_empty_security_group(
                'open-loginable-secgroup')
        cls._create_loginable_secgroup_rules(sg.id, 'IPv4')
        cls._create_loginable_secgroup_rules(sg.id, 'IPv6')
        return sg

    def _ping(self, ssh_client, ip_address):
        ping_cmd = self.PING_COMMAND.format(ip_address)
        output = ssh_client.execute_command(ping_cmd)
        try:
            packet_loss_percent = re.search(PING_PACKET_LOSS_REGEX,
                                            output.stdout).group(1)
        except Exception:
            return False
        return packet_loss_percent != '100'

    def _ssh(self, ssh_client, ip_address, cmd):
        ssh_cmd = self.SSH_COMMAND.format(
            private_key_path=self.PRIVATE_KEY_PATH, ip_address=ip_address,
            command=cmd)
        return ssh_client.execute_command(ssh_cmd)

    def _verify_ssh_ping_not_allowed(self, ssh_client, ip_address):
        msg = ("Connectivity exists unexpectedly between two instances with "
               "a security group that forbids such connectivity")
        self.assertFalse(self._ping(ssh_client, ip_address), msg)
        response = self._ssh(ssh_client, ip_address, 'pwd')
        if (('port 22: Connection timed out' not in response.stderr) and
                ('port 22: No route to host' not in response.stderr)):
            self.fail(msg)

    def _verify_ssh_ping_allowed(self, ssh_client, ip_address):
        msg = ("Connectivity doesn't exist between two instances with a "
               "security group that allows such connectivity")
        self.assertTrue(self._ping(ssh_client, ip_address), msg)
        response = self._ssh(ssh_client, ip_address, 'pwd')
        self.assertEqual(response.stdout.strip(), '/root', msg)

    def _update_port_secgroups(self, security_groups_ids):
        resp = self.net.ports.client.update_port(
            self.listener_port_id, security_groups=security_groups_ids)
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

    def _verify_udp_communication(self, sender_client, port, is_open):
        netcat_sender = '{netcat_cmd} -z -v -u -w5 {ip_address} {port}'.format(
            netcat_cmd=self.NETCAT, ip_address=self.listener_port_ip,
            port=port)
        msg = 'Error executing netcat command in sender instance'
        response = sender_client.execute_command(netcat_sender).stderr
        self.assertIn('succeeded!', response, msg)
        cat_cmd = 'cat {}{}'.format(self.NC_OUTPUT_FILE, port)
        nc_output = self._ssh(self.sender.remote_client.ssh_client,
                              self.listener_port_ip, cat_cmd).stdout
        if is_open:
            msg = ('UDP port cannot be accessed with a security group that '
                   'allows access')
            self.assertIn(self.NC_OUTPUT, nc_output, msg)
        else:
            msg = ("UDP port can be accessed with a security group that "
                   "doesn't allow access")
            self.assertNotIn(self.NC_OUTPUT, nc_output, msg)

    def _create_secgroup_incremental_port(self, name, rulesets,
                                          num_rules=None):
        if not num_rules:
            num_rules = self.security_groups.config.max_rules_per_secgroup
        secgroup = self._create_empty_security_group(name)
        for i in xrange(num_rules):
            self._create_secgroup_rules_from_rulesets(secgroup.id,
                                                      self.ETHERTYPE,
                                                      rulesets)
            rulesets[0]['port_range_min'] += 1
            rulesets[0]['port_range_max'] += 1
        return secgroup

    def _test_no_access_ssh_ping(self):
        """
        This test case assigns a security group with no rules to one of the
        ports of "listener" instance. It is then verified that the resulting
        behavior in the data plane is that no traffic from any source can reach
        that port
        """
        secgroup = self._create_empty_security_group('no-access')
        self._update_port_secgroups([secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)
        self._verify_ssh_ping_not_allowed(self.sender.remote_client.ssh_client,
                                          self.listener_port_ip)

    def _test_ssh_ping_from_specific_address(self, remote_ip_prefix):
        """
        This test case creates and assigns a security group to one of the ports
        of "listener" instance that allows ssh and icmp traffic from the pnet
        address of "sender" instance. It is then verified that the resulting
        behavior in the data plane is that "sender" instance can ssh and ping
        "listener" and that "other_sender" cannot
        """
        # Set up security groups
        secgroup = self._create_empty_security_group(
            'loginable-secgroup-address')
        self._create_loginable_secgroup_rules(
            secgroup.id, self.ETHERTYPE, remote_ip_prefix=remote_ip_prefix)
        self._update_port_secgroups([secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)
        self.other_sender.remote_client = self._get_remote_client(
            self.other_sender)

        # Confirm listener instance can be pinged and sshed from sender
        # instance
        self._verify_ssh_ping_allowed(self.sender.remote_client.ssh_client,
                                      self.listener_port_ip)

        # Confirm listener instance cannot be pinged and sshed from
        # other_sender instance
        self._verify_ssh_ping_not_allowed(
            self.other_sender.remote_client.ssh_client, self.listener_port_ip)

    def _test_ssh_ping_from_cidr(self, cidr_str, other_sender_addr):
        """
        This test case creates and assigns a security group to one of the ports
        of "listener" instance that allows ssh and icmp traffic from the /30 or
        /125 cidr containing the pnet address of "sender" instance. It is then
        verified that the resulting behavior in the data plane is that "sender"
        instance can ssh and ping "listener" and that "other_sender" cannot (if
        it outside the cidr setup in the security group rule)
        """
        # Set up security groups
        cidr = IPNetwork(cidr_str).cidr
        remote_ip_prefix = str(cidr)
        secgroup = self._create_empty_security_group('loginable-secgroup-cidr')
        self._create_loginable_secgroup_rules(
            secgroup.id, self.ETHERTYPE, remote_ip_prefix=remote_ip_prefix)
        self._update_port_secgroups([secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)
        self.other_sender.remote_client = self._get_remote_client(
            self.other_sender)

        # Confirm listener instance can be pinged and sshed from sender
        # instance
        self._verify_ssh_ping_allowed(self.sender.remote_client.ssh_client,
                                      self.listener_port_ip)

        # If possible, confirm listener instance cannot be pinged and sshed
        # from other_sender instance
        if IPAddress(other_sender_addr) not in list(cidr):
            self._verify_ssh_ping_not_allowed(
                self.other_sender.remote_client.ssh_client,
                self.listener_port_ip)

    def _test_tcp_with_ports_range(self):
        """
        This test case creates and assigns a security group to one of the
        interfaces of "listener" instance that allows traffic to a range of TCP
        ports. It is then verified that the resulting behavior in the data
        plane is that sender" instance can send TCP traffic to the ports in
        "listener" within the specified range. It is also verified that
        "sender" cannot send traffic to TCP ports in "listener" outside the
        range
        """
        # Set up security groups
        secgroup = self._create_empty_security_group('tcp-port-range-secgroup')
        rulesets = [
            dict(
                protocol='tcp',
                port_range_min=self.OPEN_TCP_PORTS[0],
                port_range_max=self.OPEN_TCP_PORTS[-1],
            ),
        ]
        self._create_secgroup_rules_from_rulesets(secgroup.id, self.ETHERTYPE,
                                                  rulesets)
        self.open_loginable_secgroup = self._create_open_loginable_secgroup(
            self.open_loginable_secgroup)
        self._update_port_secgroups([secgroup.id,
                                     self.open_loginable_secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)

        # Confirm sender server can communicate with listener server over tcp
        # ports in self.OPEN_TCP_PORTS
        netcat_sender = '{} -z -v -w5 {}'.format(self.NETCAT,
                                                 self.listener_port_ip)
        for port in self.OPEN_TCP_PORTS:
            sender_cmd = '{} {}'.format(netcat_sender, port)
            expected_response = ('Connection to {} {} port [tcp/'.format(
                self.listener_port_ip, port))
            response = self.sender.remote_client.ssh_client.execute_command(
                sender_cmd).stderr
            self.assertIn(expected_response, response)
            self.assertIn('succeeded!', response)

        # Confirm sender server cannot communicate with listener server over
        # tcp ports in self.CLOSED_TCP_PORTS
        for port in self.CLOSED_TCP_PORTS:
            sender_cmd = '{} {}'.format(netcat_sender, port)
            expected_response = ('nc: connect to {} port {} (tcp) timed '
                                 'out').format(self.listener_port_ip, port)
            self.assertIn(
                expected_response,
                self.sender.remote_client.ssh_client.execute_command(
                    sender_cmd).stderr)

    def _test_udp_with_specific_port(self):
        """
        This test cases assigns two security groups to one of the interfaces of
        "listener" instance:

        1) The first security group (created by the test case) allows traffic
           to a specific UDP port. Once assigned to the interface, it is then
           verified that the resulting behavior in the data plane is that
           "sender" instance can send UDP traffic to the specified port in
           "listener". It is also verified that "sender" cannot send traffic to
           a different UDP port

        2) The second security group is used to carry out the verifications
           in the previous point. This security group enables ssh and ping
           inbound traffic to "listener" instance from any source. This
           enables "sender" to ssh to "listener" and verify that a signature
           pattern (self.NC_OUTPUT) was received (or not received) over a
           specific UDP port and written (or not written) to a file. This
           security group and its rules were originally created in the
           setUpClass method. This test case delete the rules and creates them
           again. By doing this, the proper working of a security group whose
           rules have been created, deleted and created again is verified
        """
        # Set up security groups
        secgroup = self._create_empty_security_group(
            'udp-specific-port-secgroup')
        rulesets = [
            dict(
                protocol='udp',
                port_range_min=self.OPEN_UDP_PORT,
                port_range_max=self.OPEN_UDP_PORT,
            ),
        ]
        self._create_secgroup_rules_from_rulesets(secgroup.id, self.ETHERTYPE,
                                                  rulesets)
        self.open_loginable_secgroup = self._create_open_loginable_secgroup(
            self.open_loginable_secgroup)
        self._update_port_secgroups([secgroup.id,
                                     self.open_loginable_secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)

        # Confirm sender server can communicate with listener server over udp
        # port self.OPEN_UDP_PORT
        self._verify_udp_communication(self.sender.remote_client.ssh_client,
                                       self.OPEN_UDP_PORT, True)

        # Confirm other sender server cannot communicate with listener server
        # over self.CLOSED_UPD_PORT
        self._verify_udp_communication(self.sender.remote_client.ssh_client,
                                       self.CLOSED_UPD_PORT, False)

    def _test_any_protocol(self, remote_ip_prefix):
        """
        This test case creates and assigns a security group to one of the ports
        of "listener" instance that allows traffic of any protocol from the
        pnet address of "sender" instance. It is then verified that the
        resulting behavior in the data plane is that "sender" instance can:

        1) Send tcp traffic to "listener" port 22 by ssh'ing into it
        2) Send icmp traffic to "listener" by pinging it
        3) Send udp traffic to a "listener" port

        It is also verified that "other_instance" cannot not do any of the
        above
        """
        # Set up security groups
        secgroup = self._create_empty_security_group(
            'any-protocol-secgroup')
        rulesets = [
            dict(
                protocol=None,
                remote_ip_prefix=remote_ip_prefix,
            ),
        ]
        self._create_secgroup_rules_from_rulesets(secgroup.id, self.ETHERTYPE,
                                                  rulesets)
        self._update_port_secgroups([secgroup.id])
        self.sender.remote_client = self._get_remote_client(self.sender)
        self.other_sender.remote_client = self._get_remote_client(
            self.other_sender)

        # Confirm sender instance can ping, ssh and send udp datagrams to
        # listener server
        self._verify_ssh_ping_allowed(self.sender.remote_client.ssh_client,
                                      self.listener_port_ip)
        self._verify_udp_communication(self.sender.remote_client.ssh_client,
                                       self.ANY_UPD_OPEN, True)

        # Confirm other_sender server cannot ping, ssh and send udp datagrams
        # to listener server
        self._verify_ssh_ping_not_allowed(
            self.other_sender.remote_client.ssh_client, self.listener_port_ip)
        self._verify_udp_communication(
            self.other_sender.remote_client.ssh_client, self.ANY_UDP_CLOSED,
            False)

    def _test_max_number_secgroups_per_port(self, remote_ip_prefix):
        """
        This test case creates and assigns to one of "listener" instance ports
        the maximum allowed number of security groups with the maximum allowed
        number of rules. It is then verified that the resulting data plane
        behavior is that "sender" instance can ssh, ping and send udp traffic
        to "listener" instance. It is deemed sufficient to verify the expected
        behavior for a selected number of security groups and rules. It is also
        verified that "other_sender" cannot send traffic to "listener".

        After the data plane checks, one more security group is created and
        assigned to the "listener" instance port. It is then verified that the
        API returns the expected error code
        """
        rulesets = [
            dict(
                protocol='udp',
                port_range_min=self.UDP_PORT_BASE_FOR_MAX,
                port_range_max=self.UDP_PORT_BASE_FOR_MAX,
                remote_ip_prefix=remote_ip_prefix,
            ),
        ]
        secgroups_ids = []
        max_number_secgroups = (
            self.security_groups.config.max_secgroups_per_port)
        for i in xrange(max_number_secgroups - 1):
            name = 'max-number-secgroup-{}'.format(str(i))
            secgroups_ids.append(self._create_secgroup_incremental_port(
                name, rulesets).id)
        secgroups_ids.append(self._create_secgroup_incremental_port(
            name,
            rulesets,
            self.security_groups.config.max_rules_per_secgroup - 2).id)
        self._create_loginable_secgroup_rules(
            secgroups_ids[-1], self.ETHERTYPE,
            remote_ip_prefix=remote_ip_prefix)

        # This assignment of security groups to port should succeed. It
        # assigns just the maximum allowed by quota
        self._update_port_secgroups(secgroups_ids)
        self.sender.remote_client = self._get_remote_client(self.sender)
        self.other_sender.remote_client = self._get_remote_client(
            self.other_sender)

        # Confirm sender instance can ping, ssh and send udp datagrams to
        # listener server
        self._verify_ssh_ping_allowed(self.sender.remote_client.ssh_client,
                                      self.listener_port_ip)
        self._verify_udp_communication(self.sender.remote_client.ssh_client,
                                       self.MAX_UDP_OPEN, True)

        # Confirm other_sender server cannot ping, ssh and send udp datagrams
        # to listener server
        self._verify_ssh_ping_not_allowed(
            self.other_sender.remote_client.ssh_client, self.listener_port_ip)
        self._verify_udp_communication(
            self.other_sender.remote_client.ssh_client, self.MAX_UDP_CLOSED,
            False)

        # Add one more security group to the list. This is one more that the
        # maximum per port
        name = 'max-number-secgroup-{}'.format(str(max_number_secgroups))
        secgroups_ids.append(self._create_secgroup_incremental_port(
            name, rulesets).id)

        # This assignment of security groups to port should raise exception
        # because we are over the quota
        with self.assertRaises(AssertionError) as exception_manager:
            self._update_port_secgroups(secgroups_ids)
        msg = ('Assignment of more security groups to a port than allowed '
               'by quota raised unexpected exception: {}')
        msg = msg.format(type(exception_manager.exception))
        self.assertIsInstance((exception_manager.exception,
                                   AssertionError), msg)
        msg = ('Assignment of more security groups to a port than allowed '
               'by quota did not return expected 409 response code')
        self.assertIn('409', str(exception_manager.exception), msg)


class SecurityGroupsTestIPv4(SecurityGroupsTest):

    """
    This class executes the test cases in SecurityGroupsTest for public net
    IPv4
    """

    PING_COMMAND = 'ping -c 3 {}'
    SSH_COMMAND = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} root@{ip_address} {command}')
    NAMES_PREFIX = 'security_groups_IPv4'
    ETHERTYPE = 'IPv4'
    NETCAT = 'nc'
    OPEN_TCP_PORTS = [91, 92, 93, ]
    CLOSED_TCP_PORTS = [94, 95, 96, ]
    OPEN_UDP_PORT = 97
    CLOSED_UPD_PORT = 98
    ANY_UPD_OPEN = 99
    ANY_UDP_CLOSED = 100
    UDP_PORT_BASE_FOR_MAX = 201
    MAX_UDP_OPEN = 220
    MAX_UDP_CLOSED = 221

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsTestIPv4, cls).setUpClass()
        cls.listener_port_ip = cls.listener.entity.addresses.public.ipv4

    @tags(type='negative', net='yes')
    def test_no_access_ssh_ping_ipv4(self):
        self._test_no_access_ssh_ping()

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_specific_address_ipv4(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv4, '32')
        self._test_ssh_ping_from_specific_address(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_cidr_ipv4(self):
        cidr_str = IP_FMT.format(
            self.sender.entity.addresses.public.ipv4, '30')
        other_sender_addr = self.other_sender.entity.addresses.public.ipv4
        self._test_ssh_ping_from_cidr(cidr_str, other_sender_addr)

    @tags(type='positive', net='yes')
    def test_tcp_with_ports_range_ipv4(self):
        self._test_tcp_with_ports_range()

    @tags(type='positive', net='yes')
    def test_udp_with_specific_port_ipv4(self):
        self._test_udp_with_specific_port()

    @tags(type='positive', net='yes')
    def test_any_protocol_ipv4(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv4, '32')
        self._test_any_protocol(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_max_number_secgroups_per_port_ipv4(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv4, '32')
        self._test_max_number_secgroups_per_port(remote_ip_prefix)


class SecurityGroupsTestIPv6(SecurityGroupsTest):

    """
    This class executes the test cases in SecurityGroupsTest for public net
    IPv6
    """

    PING_COMMAND = 'ping6 -c 3 {}'
    SSH_COMMAND = ('ssh -6 -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} root@{ip_address} {command}')
    NAMES_PREFIX = 'security_groups_IPv6'
    ETHERTYPE = 'IPv6'
    NETCAT = 'nc -6'
    OPEN_TCP_PORTS = [101, 102, 103, ]
    CLOSED_TCP_PORTS = [104, 105, 106, ]
    OPEN_UDP_PORT = 107
    CLOSED_UPD_PORT = 108
    ANY_UPD_OPEN = 109
    ANY_UDP_CLOSED = 110
    UDP_PORT_BASE_FOR_MAX = 201
    MAX_UDP_OPEN = 240
    MAX_UDP_CLOSED = 241

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsTestIPv6, cls).setUpClass()
        cls.listener_port_ip = cls.listener.entity.addresses.public.ipv6

    @tags(type='negative', net='yes')
    def test_no_access_ssh_ping_ipv6(self):
        self._test_no_access_ssh_ping()

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_specific_address_ipv6(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv6, '128')
        self._test_ssh_ping_from_specific_address(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_cidr_ipv6(self):
        cidr_str = IP_FMT.format(
            self.sender.entity.addresses.public.ipv6, '125')
        other_sender_addr = self.other_sender.entity.addresses.public.ipv6
        self._test_ssh_ping_from_cidr(cidr_str, other_sender_addr)

    @tags(type='positive', net='yes')
    def test_tcp_with_ports_range_ipv6(self):
        self._test_tcp_with_ports_range()

    @tags(type='positive', net='yes')
    def test_udp_with_specific_port_ipv6(self):
        self._test_udp_with_specific_port()

    @tags(type='positive', net='yes')
    def test_any_protocol_ipv6(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv6, '128')
        self._test_any_protocol(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_max_number_secgroups_per_port_ipv6(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.public.ipv6, '128')
        self._test_max_number_secgroups_per_port(remote_ip_prefix)


class SecurityGroupsTestServiceNet(SecurityGroupsTest):

    """
    This class executes the test cases in SecurityGroupsTest for service net
    IPv4
    """

    PING_COMMAND = 'ping -c 3 {}'
    SSH_COMMAND = ('ssh -o UserKnownHostsFile=/dev/null '
                   '-o StrictHostKeyChecking=no -o ConnectTimeout=60 '
                   '-i {private_key_path} root@{ip_address} {command}')
    NAMES_PREFIX = 'security_groups_servicenet'
    ETHERTYPE = 'IPv4'
    NETCAT = 'nc'
    OPEN_TCP_PORTS = [91, 92, 93, ]
    CLOSED_TCP_PORTS = [94, 95, 96, ]
    OPEN_UDP_PORT = 97
    CLOSED_UPD_PORT = 98
    ANY_UPD_OPEN = 99
    ANY_UDP_CLOSED = 100
    UDP_PORT_BASE_FOR_MAX = 201
    MAX_UDP_OPEN = 220
    MAX_UDP_CLOSED = 221

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsTestServiceNet, cls).setUpClass()
        cls.listener_port_ip = cls.listener.entity.addresses.private.ipv4

    @classmethod
    def _get_listener_port_id(cls):
        resp = cls.net.ports.client.list_ports(
            device_id=cls.listener.entity.id,
            network_id=cls.service_network_id)
        super(SecurityGroupsTestServiceNet, cls)._get_listener_port_id()
        msg = "Ports list returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        assert resp.status_code == 200, msg
        ports = resp.entity
        msg = ("Ports list returned unexpected number of ports given provided "
               "filter. Expected 1 port, {0} returned")
        msg = msg.format(len(ports))
        assert len(ports) == 1, msg
        return ports[0].id

    @tags(type='negative', net='yes')
    def test_no_access_ssh_ping_servicenet(self):
        self._test_no_access_ssh_ping()

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_specific_address_servicenet(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.private.ipv4, '32')
        self._test_ssh_ping_from_specific_address(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_ssh_ping_from_cidr_servicenet(self):
        cidr_str = IP_FMT.format(
            self.sender.entity.addresses.private.ipv4, '30')
        other_sender_addr = self.other_sender.entity.addresses.private.ipv4
        self._test_ssh_ping_from_cidr(cidr_str, other_sender_addr)

    @tags(type='positive', net='yes')
    def test_tcp_with_ports_range_servicenet(self):
        self._test_tcp_with_ports_range()

    @tags(type='positive', net='yes')
    def test_udp_with_specific_port_servicenet(self):
        self._test_udp_with_specific_port()

    @tags(type='positive', net='yes')
    def test_any_protocol_servicenet(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.private.ipv4, '32')
        self._test_any_protocol(remote_ip_prefix)

    @tags(type='positive', net='yes')
    def test_max_number_secgroups_per_port_servicenet(self):
        remote_ip_prefix = IP_FMT.format(
            self.sender.entity.addresses.private.ipv4, '32')
        self._test_max_number_secgroups_per_port(remote_ip_prefix)


class SecurityGroupsCleanup(NetworkingComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupsCleanup, cls).setUpClass()
        cls.security_groups = SecurityGroupsComposite()

    def test_cleanup_security_groups(self):
        resp = self.security_groups.client.list_security_groups()
        msg = "Security group list returned unexpected status code: {}"
        msg = msg.format(resp.status_code)
        self.assertEqual(resp.status_code, 200, msg)
        list_sec_groups = resp.entity
        for secgroup in list_sec_groups:
            resp = self.security_groups.client.delete_security_group(
                secgroup.id)
            msg = "Security group delete returned unexpected status code: {}"
            msg = msg.format(resp.status_code)
            self.assertEqual(resp.status_code, 204, msg)
