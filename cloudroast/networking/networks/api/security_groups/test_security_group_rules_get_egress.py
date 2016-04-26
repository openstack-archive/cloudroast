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


class SecurityGroupRuleGetTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupRuleGetTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_rule_get_egress'
        cls.expected_secgroup.description = 'testing security rules gets'
        cls.expected_secrule = cls.get_expected_secrule_data()
        cls.expected_secrule.direction = 'egress'

    def setUp(self):
        super(SecurityGroupRuleGetTest, self).setUp()
        self.secgroup = self.create_test_secgroup(self.expected_secgroup)
        self.expected_secrule.security_group_id = self.secgroup.id
        self.secrule = self.create_test_secrule(self.expected_secrule)

    def tearDown(self):
        self.secGroupCleanUp()
        super(SecurityGroupRuleGetTest, self).tearDown()

    @tags('sec_group_egress')
    def test_security_group_rule_get(self):
        expected_secrule = self.secrule

        request_kwargs = dict(security_group_rule_id=expected_secrule.id)
        resp = self.sec.behaviors.get_security_group_rule(**request_kwargs)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secrule = resp.response.entity

        # Check the Security Group response
        self.assertSecurityGroupRuleResponse(expected_secrule, secrule)

    @tags('sec_group_egress')
    def test_security_group_rule_list(self):
        resp = self.sec.behaviors.list_security_group_rules()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secrule_list = resp.response.entity

        msg = ('Security rule:\n{0}\n\nmissing in expected security rule '
               'list:\n{1}').format(self.secrule, secrule_list)
        self.assertIn(self.secrule, secrule_list, msg)
