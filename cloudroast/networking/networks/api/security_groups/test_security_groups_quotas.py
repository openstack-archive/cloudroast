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

from cafe.drivers.unittest.decorators import tags

from cloudroast.networking.networks.fixtures \
    import NetworkingSecurityGroupsFixture
from cloudcafe.networking.networks.extensions.security_groups_api.constants \
    import SecurityGroupsErrorTypes, SecurityGroupsResponseCodes


class SecurityGroupsQuotasTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupsQuotasTest, cls).setUpClass()

        # Setting up
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_quotas'
        cls.expected_secrule = cls.get_expected_secrule_data()

    def tearDown(self):
        self.secGroupCleanUp()

    @tags('quotas')
    def test_rules_per_group(self):
        """
        @summary: Testing security rules quota per group
        """
        secgroup = self.create_test_secgroup(self.expected_secgroup)
        expected_secrule = self.expected_secrule
        expected_secrule.security_group_id = secgroup.id
        rules_per_group = self.sec.config.max_rules_per_secgroup
        num = rules_per_group
        self.create_n_security_rules_per_group(expected_secrule, num)

        msg = ('Successfully created the expected security rules per group '
            'allowed by the quota of {0}').format(rules_per_group)
        self.fixture_log.debug(msg)

        # Checking the quota is enforced
        request_kwargs = dict(
            security_group_id=expected_secrule.security_group_id,
            raise_exception=False)
        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)

        neg_msg = ('(negative) Creating a security rule over the group quota'
                   ' of {0}').format(rules_per_group)
        status_code = SecurityGroupsResponseCodes.CONFLICT
        error_type = SecurityGroupsErrorTypes.OVER_QUOTA
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

    @tags('quotas')
    def test_groups_per_tenant(self):
        """
        @summary: Testing security groups quota per tenant
        """
        expected_secgroup = self.expected_secgroup
        groups_per_tenant = self.sec.config.max_secgroups_per_tenant
        num = groups_per_tenant
        self.create_n_security_groups(expected_secgroup, num)

        msg = ('Successfully created the expected security groups per tenant '
            'allowed by the quota of {0}').format(groups_per_tenant)
        self.fixture_log.debug(msg)

        # Checking the quota is enforced
        request_kwargs = dict(
            name=expected_secgroup.name,
            description=expected_secgroup.description,
            raise_exception=False)
        resp = self.sec.behaviors.create_security_group(**request_kwargs)

        neg_msg = ('(negative) Creating a security group over the tenant quota'
                   ' of {0}').format(groups_per_tenant)
        status_code = SecurityGroupsResponseCodes.CONFLICT
        error_type = SecurityGroupsErrorTypes.OVER_QUOTA
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

    @tags('quotas')
    def test_rules_per_tenant(self):
        """
        @summary: Testing security rules quota per tenant
        """
        expected_secgroup = self.expected_secgroup
        expected_secrule = self.expected_secrule
        groups_per_tenant = self.sec.config.max_secgroups_per_tenant
        rules_per_tenant = self.sec.config.max_rules_per_tenant
        rules_per_group = rules_per_tenant / groups_per_tenant

        secgroups = self.create_n_security_groups_w_n_rules(
            expected_secgroup, expected_secrule, groups_per_tenant,
            rules_per_group)

        msg = ('Successfully created the expected security rules per tenant '
            'allowed by the quota of {0}').format(rules_per_tenant)
        self.fixture_log.debug(msg)

        # Checking the quota is enforced
        request_kwargs = dict(
            security_group_id=secgroups[0].id,
            raise_exception=False)
        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)

        neg_msg = ('(negative) Creating a security rule over the tenant quota'
                   ' of {0}').format(rules_per_tenant)
        status_code = SecurityGroupsResponseCodes.CONFLICT
        error_type = SecurityGroupsErrorTypes.OVER_QUOTA
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

    def create_n_security_groups_w_n_rules(self, expected_secgroup,
                                           expected_secrule, groups_num,
                                           rules_num):
        """
        @summary: Creating n security groups with n rules
        """
        secgroups = self.create_n_security_groups(expected_secgroup,
                                                  groups_num)
        for group in secgroups:
            expected_secrule.security_group_id = group.id
            self.create_n_security_rules_per_group(expected_secrule, rules_num)

        return secgroups

    def create_n_security_groups(self, expected_secgroup, num):
        """
        @summary: Creating n security groups
        """
        secgroups = []

        for x in range(num):
            log_msg = 'Creating security group {0}'.format(x + 1)
            self.fixture_log.debug(log_msg)
            name = 'security_test_group_n_{0}'.format(x + 1)
            expected_secgroup.name = name
            secgroup = self.create_test_secgroup(expected_secgroup)
            secgroups.append(secgroup)

        msg = 'Successfully created {0} security groups'.format(num)
        self.fixture_log.debug(msg)
        return secgroups

    def create_n_security_rules_per_group(self, expected_secrule, num):
        """
        @summary: Creating n security rules within a security group and
            verifying they are created successfully
        """
        request_kwargs = dict(
            security_group_id=expected_secrule.security_group_id,
            raise_exception=False)

        for x in range(num):
            log_msg = 'Creating rule {0}'.format(x + 1)
            self.fixture_log.debug(log_msg)
            resp = self.sec.behaviors.create_security_group_rule(
                **request_kwargs)

            # Fail the test if any failure is found
            self.assertFalse(resp.failures)
            secrule = resp.response.entity

            # Check the Security Group Rule response
            self.assertSecurityGroupRuleResponse(expected_secrule, secrule)

        msg = ('Successfully created {0} security rules at security group '
            '{1}').format(num, expected_secrule.security_group_id)
        self.fixture_log.debug(msg)
