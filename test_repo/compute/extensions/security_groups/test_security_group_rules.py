"""
Copyright 2013 Rackspace

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
from test_repo.compute.fixtures import ComputeFixture


class SecurityGroupRuleTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(SecurityGroupRuleTest, cls).setUpClass()
        cls.security_group = cls.security_groups_client.create_security_group(
            name='test', description='test group').entity

    @tags(type='positive', net='no')
    def test_create_security_group_rule(self):
        security_group_rule = self.security_group_rule_client.create_rule(
            from_port=80, ip_protocol='tcp', to_port=8080,
            parent_group_id=self.security_group.id, cidr='0.0.0.0/0',
            group_id=self.security_group.id).entity
        security_group_with_rule = self.security_groups_client.\
            get_security_group(self.security_group.id).entity
        self.assertIn(security_group_rule.id,
                      [rule.id for rule in security_group_with_rule.rules],
                      "Expected security rule is not present in"
                      " list of rules.")

    @tags(type='positive', net='no')
    def test_delete_security_group_rule(self):
        security_group_rule = self.security_group_rule_client.create_rule(
            from_port=80, ip_protocol='tcp', to_port=8080,
            parent_group_id=self.security_group.id, cidr='0.0.0.0/0',
            group_id=self.security_group.id).entity
        self.security_group_rule_client.delete_rule(security_group_rule.id)
        security_group_with_rule = self.security_groups_client.\
            get_security_group(self.security_group.id).entity
        self.assertNotIn(security_group_rule.id,
                         [rule.id for rule in security_group_with_rule.rules],
                         "Deleted security rule is still present"
                         " in list of rules.")

    @classmethod
    def tearDownClass(cls):
        super(SecurityGroupRuleTest, cls).tearDownClass()
        cls.security_groups_client.delete_security_group(cls.security_group.id)
