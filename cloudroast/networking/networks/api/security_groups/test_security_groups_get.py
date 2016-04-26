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


class SecurityGroupGetTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupGetTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_get'
        cls.expected_secgroup.description = 'testing security groups gets'
        cls.expected_secrule = cls.get_expected_secrule_data()

    def setUp(self):
        super(SecurityGroupGetTest, self).setUp()
        self.secgroup = self.create_test_secgroup(self.expected_secgroup)
        self.expected_secrule.security_group_id = self.secgroup.id

    def tearDown(self):
        self.secGroupCleanUp()
        super(SecurityGroupGetTest, self).tearDown()

    @tags('sec_group')
    def test_security_group_get(self):
        expected_secgroup = self.secgroup
        request_kwargs = dict(security_group_id=expected_secgroup.id)
        resp = self.sec.behaviors.get_security_group(**request_kwargs)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secgroup = resp.response.entity

        # Check the Security Group response
        self.assertSecurityGroupResponse(expected_secgroup, secgroup)

    @tags('sec_group')
    def test_security_group_list(self):
        resp = self.sec.behaviors.list_security_groups()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secgroup_list = resp.response.entity

        msg = ('Security group:\n{0}\n\nmissing in expected security group '
            'list:\n{1}').format(self.secgroup, secgroup_list)
        self.assertIn(self.secgroup, secgroup_list, msg)

    @tags('sec_group')
    def test_security_group_w_rule_get(self):
        expected_secgroup = self.secgroup

        # Creating a security rule
        secrule = self.create_test_secrule(self.expected_secrule)
        expected_secgroup.security_group_rules = [secrule]
        request_kwargs = dict(security_group_id=expected_secgroup.id)

        # Checking the security rule is in the group
        resp = self.sec.behaviors.get_security_group(**request_kwargs)
        self.assertFalse(resp.failures)
        secgroup = resp.response.entity

        # Check the Security Group response
        self.assertSecurityGroupResponse(expected_secgroup, secgroup)
