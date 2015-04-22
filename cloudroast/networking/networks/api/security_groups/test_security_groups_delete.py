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


class SecurityGroupDeleteTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupDeleteTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_delete'
        cls.expected_secgroup.description = 'testing security groups delete'
        cls.expected_secrule = cls.get_expected_secrule_data()

    def setUp(self):
        self.secgroup = self.create_test_secgroup(self.expected_secgroup,
                                                  delete=False)
        self.expected_secrule.security_group_id = self.secgroup.id

    def tearDown(self):
        self.secGroupCleanUp()

    @tags('sec_group')
    def test_security_group_delete(self):
        expected_secgroup = self.secgroup

        request_kwargs = dict(security_group_id=expected_secgroup.id)
        resp = self.sec.behaviors.delete_security_group(**request_kwargs)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

        # Checking the security group was deleted
        resp = self.sec.behaviors.get_security_group(**request_kwargs)

        neg_msg = ('(negative) Getting a deleted security group')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

    @tags('sec_group')
    def test_security_group_w_rule_delete(self):
        expected_secgroup = self.secgroup

        # Creating a security rule
        secrule = self.create_test_secrule(self.expected_secrule, delete=False)
        request_kwargs = dict(security_group_id=expected_secgroup.id)

        # Checking the security group and rule are there
        resp = self.sec.behaviors.get_security_group(**request_kwargs)
        self.assertFalse(resp.failures)

        resp = self.sec.behaviors.get_security_group_rule(
            security_group_rule_id=secrule.id)
        self.assertFalse(resp.failures)

        # Deleting the security group
        resp = self.sec.behaviors.delete_security_group(**request_kwargs)
        self.assertFalse(resp.failures)

        # Checking the security group was deleted
        resp = self.sec.behaviors.get_security_group(**request_kwargs)

        neg_msg = ('(negative) Getting a deleted security group')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

        # Checking the security group rule was deleted
        resp = self.sec.behaviors.get_security_group_rule(
            security_group_rule_id=secrule.id)
        neg_msg = ('(negative) Getting a deleted security group rule')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_RULE_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

    @tags('sec_group')
    def test_deleting_previously_deleted_security_group(self):
        """
        Testing the HTTP response when trying to delete an already
        deleted security group
        """
        expected_secgroup = self.secgroup

        # Creating a security rule
        secrule = self.create_test_secrule(self.expected_secrule, delete=False)
        request_kwargs = dict(security_group_id=expected_secgroup.id)

        # Checking the security rule is in the group
        resp = self.sec.behaviors.get_security_group(**request_kwargs)
        self.assertFalse(resp.failures)

        # Deleting the security group
        resp = self.sec.behaviors.delete_security_group(**request_kwargs)
        self.assertFalse(resp.failures)

        # Checking the security group was deleted
        resp = self.sec.behaviors.get_security_group(**request_kwargs)

        neg_msg = ('(negative) Getting a deleted security group')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)

        # Trying to delete the security group a second time
        resp = self.sec.behaviors.delete_security_group(**request_kwargs)
        neg_msg = ('(negative) Deleting a deleted security group')
        status_code = SecurityGroupsResponseCodes.NOT_FOUND
        error_type = SecurityGroupsErrorTypes.SECURITY_GROUP_NOT_FOUND
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=neg_msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)
