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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.extensions.security_groups_api.constants \
    import SecurityGroupsErrorTypes, SecurityGroupsResponseCodes

from cloudroast.networking.networks.fixtures \
    import NetworkingSecurityGroupsFixture


class SecurityGroupRuleDeleteTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupRuleDeleteTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secrule_delete'
        cls.expected_secgroup.description = 'testing security rules delete'
        cls.expected_secrule = cls.get_expected_secrule_data()

    def setUp(self):
        self.secgroup = self.create_test_secgroup(self.expected_secgroup)
        self.expected_secrule.security_group_id = self.secgroup.id
        self.secrule = self.create_test_secrule(self.expected_secrule)

    def tearDown(self):
        self.secGroupCleanUp()

    @tags('sec_group')
    def test_security_group_rule_delete(self):
        """
        @summary: Testing deleting a security group rule
        """
        secrule = self.secrule
        request_kwargs = dict(security_group_rule_id=secrule.id)

        # Checking the security group rule was added to the group
        resp = self.sec.behaviors.get_security_group(
            security_group_id=secrule.security_group_id)
        self.assertFalse(resp.failures)
        secgroup = resp.response.entity

        msg = ('Security group rule:\n{0}\n\nmissing in expected security '
               'group rules list:\n{1}').format(secrule,
                                                secgroup.security_group_rules)
        self.assertIn(secrule, secgroup.security_group_rules, msg)

        # Deleting the security rule
        resp = self.sec.behaviors.delete_security_group_rule(**request_kwargs)
        self.assertFalse(resp.failures)

        # Checking the security rule was deleted
        resp = self.sec.behaviors.get_security_group_rule(**request_kwargs)

        neg_msg = ('(negative) Getting a deleted security rule')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_RULE_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups_rules,
            error_type=error_type)

        # Checking the security rule is not in the group anymore
        resp = self.sec.behaviors.get_security_group(
            security_group_id=secrule.security_group_id)
        self.assertFalse(resp.failures)
        secgroup = resp.response.entity

        msg = ('Deleted security group rule:\n{0}\n\nstill present in security'
               ' group rules list:\n{1}').format(secrule,
                                                 secgroup.security_group_rules)
        self.assertNotIn(secrule, secgroup.security_group_rules, msg)
