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
import unittest

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import DataDrivenFixture, \
    data_driven_test, tags
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures \
    import NetworkingSecurityGroupsFixture
from cloudcafe.networking.networks.extensions.security_groups_api.constants \
    import SecurityGroupsErrorTypes, SecurityGroupsResponseCodes


# Creating data sets for data driven testing
data_set_list = DatasetList()
data_set_list.append_new_dataset(
    name='',
    data_dict={},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_icmp',
    data_dict={'protocol': 'icmp'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_tcp',
    data_dict={'protocol': 'tcp'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_udp',
    data_dict={'protocol': 'udp'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_ethertype_ipv4',
    data_dict={'ethertype': 'IPv4'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_ethertype_ipv6',
    data_dict={'ethertype': 'IPv6'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_icmp_and_port_ranges',
    data_dict={'protocol': 'icmp', 'port_range_min': 0,
               'port_range_max': 255},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_icmp',
    data_dict={'protocol': 'icmp'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_icmp_and_port_range_min',
    data_dict={'protocol': 'icmp', 'port_range_min': 2},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_tcp_and_port_ranges',
    data_dict={'protocol': 'tcp', 'port_range_min': 0,
               'port_range_max': 65535},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_protocol_udp_and_port_ranges',
    data_dict={'protocol': 'udp', 'port_range_min': 0,
               'port_range_max': 65535},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_remote_ip_prefix_ipv4',
    data_dict={'remote_ip_prefix': '192.168.86.0/24'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_remote_ip_prefix_ipv6',
    data_dict={"ethertype": 'IPv6', "remote_ip_prefix": 'fd00:d9f1:d355::/64'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])


# Data set for negative testing
data_set_list_negative = DatasetList()

# This test is only to be used to check if the egress rules are OFF
data_set_list_negative.append_new_dataset(
    name='w_direction_egress',
    data_dict={'direction': 'egress',
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Non-ingress rules are not currently supported',
               'error_type': 'EGRESS_SECURITY_GROUP_RULES_NOT_ENABLED'},
    tags=['sec_group_egress_off'])
data_set_list_negative.append_new_dataset(
    name='w_invalid_protocol',
    data_dict={'protocol': 'invalid_protocol',
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Protocol should be icmp, tcp or udp',
               'error_type': 'SECURITY_GROUP_RULE_INVALID_PROTOCOL'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_invalid_ethertype',
    data_dict={'ethertype': 'invalid_ethertype',
               'http_status': 'BAD_REQUEST',
               'test_desc': 'testing with invalid ethertype (valid:IPv4/IPv6)',
               'error_type': 'SECURITY_GROUP_RULE_INVALID_ETHERTYPE'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_port_ranges_and_protocol_missing',
    data_dict={'port_range_min': 1, 'port_range_max': 255,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Must also specify protocol if port range given',
               'error_type': 'SECURITY_GROUP_PROTOCOL_REQUIRED_WITH_PORTS'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_protocol_icmp_and_port_max_out_of_range',
    data_dict={'protocol': 'icmp', "port_range_min": 1,
               'port_range_max': 65535,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Invalid ICMP port_range_max value, must be 0-255',
               'error_type': 'SECURITY_GROUP_INVALID_ICMP_VALUE'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_protocol_tcp_and_port_max_out_of_range',
    data_dict={'protocol': 'tcp', 'port_range_min': 1,
               'port_range_max': 65536,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Invalid value for port',
               'error_type': 'SECURITY_GROUP_INVALID_PORT_VALUE'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_protocol_udp_and_port_max_out_of_range',
    data_dict={'protocol': 'udp', 'port_range_min': 1,
               'port_range_max': 65536,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Invalid value for port',
               'error_type': 'SECURITY_GROUP_INVALID_PORT_VALUE'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_remote_ip_prefix_ipv6_and_ipv4_ethertype',
    data_dict={'remote_ip_prefix': 'fd00:d9f1:d355::/64',
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Etherytype IPv4 does not match remote_ip_prefix IPv6',
               'error_type': 'INVALID_INPUT'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_remote_ip_prefix_ipv4_and_ipv6_ethertype',
    data_dict={'ethertype': 'IPv6', 'remote_ip_prefix': '192.168.86.0/24',
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Etherytype IPv6 does not match remote_ip_prefix IPv4',
               'error_type': 'INVALID_INPUT'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_remote_group_id',
    data_dict={'remote_group_id': True,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'Remote groups are not currently supported',
               'error_type': 'INVALID_INPUT'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])

# With bug, http response should be 400 instead of 500
data_set_list_negative.append_new_dataset(
    name='w_protocol_icmp_and_port_range_max',
    data_dict={'protocol': 'icmp', 'port_range_max': 200,
               'http_status': 'BAD_REQUEST',
               'test_desc': 'ICMP requires port_range_min when port_range_max given',
               'error_type': 'SECURITY_GROUP_MISSING_ICMP_TYPE'},
    tags=['bug'])


@DataDrivenFixture
class SecurityGroupRuleCreateTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupRuleCreateTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_rule_create'
        cls.expected_secgroup.description = 'testing security rules creates'

    def setUp(self):
        self.secgroup = self.create_test_secgroup(self.expected_secgroup)
        self.expected_secrule = self.get_expected_secrule_data()
        self.expected_secrule.security_group_id = self.secgroup.id

    def tearDown(self):
        self.secGroupCleanUp()

    @data_driven_test(data_set_list)
    def ddtest_security_group_rule_create(self,
                                          security_group_id=None,
                                          direction=None,
                                          ethertype=None,
                                          port_range_min=None,
                                          port_range_max=None,
                                          protocol=None,
                                          remote_group_id=None,
                                          remote_ip_prefix=None,
                                          use_false_values=False):
        """
        @summary: Creating a Security Group Rule
        """
        expected_secrule = self.expected_secrule
        request_kwargs = dict(
            security_group_id=expected_secrule.security_group_id)

        properties = ['security_group_id', 'direction', 'ethertype',
                      'port_range_min', 'port_range_max', 'remote_ip_prefix']

        for prop_name in properties:
            prop_value = eval(prop_name)
            if prop_value is not None:
                request_kwargs[prop_name] = prop_value
                setattr(expected_secrule, prop_name, prop_value)

        if protocol is not None:
            request_kwargs['protocol'] = protocol
            expected_secrule.protocol = protocol.upper()
        if remote_group_id is not None:
            if remote_group_id == True:
                remote_group_id = expected_secrule.security_group_id
            request_kwargs['remote_group_id'] = remote_group_id
            expected_secrule.remote_group_id = remote_group_id

        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_secgroups_rules.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secrule = resp.response.entity

        # Check the Security Group Rule response
        self.assertSecurityGroupRuleResponse(expected_secrule, secrule)

    @data_driven_test(data_set_list_negative)
    def ddtest_security_group_rule_create_negative(self,
                                                   security_group_id=None,
                                                   direction=None,
                                                   ethertype=None,
                                                   port_range_min=None,
                                                   port_range_max=None,
                                                   protocol=None,
                                                   remote_group_id=None,
                                                   remote_ip_prefix=None,
                                                   use_false_values=False,
                                                   http_status=None,
                                                   test_desc=None,
                                                   error_type=None):
        """
        @summary: Negative test creating a Security Group Rule
        """
        expected_secrule_data = self.expected_secrule
        request_kwargs = dict(
            security_group_id=expected_secrule_data.security_group_id,
            raise_exception=False)

        properties = ['security_group_id', 'direction', 'ethertype',
                      'port_range_min', 'port_range_max', 'protocol',
                      'remote_group_id', 'remote_ip_prefix',
                      'remote_ip_prefix']

        for prop_name in properties:
            prop_value = eval(prop_name)
            if prop_value is not None:
                request_kwargs[prop_name] = prop_value

        if use_false_values:
            request_kwargs['protocol'] = protocol

        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)

        # Security Group create should be unavailable
        msg = ('(negative) Creating a Security Group Rule where '
               '{test_description}').format(test_description=test_desc)
        status_code = getattr(SecurityGroupsResponseCodes, http_status)
        if error_type:
            error_type = getattr(SecurityGroupsErrorTypes, error_type)
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=msg,
            delete_list=self.delete_secgroups_rules,
            error_type=error_type)
