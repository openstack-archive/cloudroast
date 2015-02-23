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
    tags=['dev', 'post', 'positive', 'rbac_creator'])


# Data set for negative testing
data_set_list_negative = DatasetList()

# Testing with other tenant_id in the request body
data_set_list_negative.append_new_dataset(
    name='w_other_tenant_id',
    data_dict={"name": 'test_secgroup_create_neg', "tenant_id": False,
    "http_status": 'BAD_REQUEST',
    "test_desc": 'with another tenant ID on the request body',
    "error_type": 'HTTP_BAD_REQUEST'},
    tags=['smoke', 'post', 'negative', 'rbac_creator'])


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

    @tags('leosdev')
    def test_secrule_dev(self):
        print self.secgroup
        print self.expected_secrule

    @data_driven_test(data_set_list)
    def ddtest_security_group_rule_create(self, direction=None,
                                     ethertype=None,
                                     port_range_min=None,
                                     port_range_max=None,
                                     protocol=None,
                                     remote_group_id=None,
                                     remote_ip_prefix=None,
                                     tenant_id=None,
                                     use_false_values=False):
        """
        @summary: Creating a Security Group Rule
        """
        expected_secrule = self.expected_secrule
        request_kwargs = dict(
            security_group_id=expected_secrule.security_group_id)

#        if name or use_false_values:
#            request_kwargs['name'] = name
#            expected_secgroup.name = name
#        if description or use_false_values:
#            request_kwargs['description'] = description
#            expected_secgroup.description = description
#        if tenant_id == True:
#            request_kwargs['tenant_id'] = self.user.tenant_id
#        elif tenant_id or use_false_values:
#            request_kwargs['tenant_id'] = None
        print request_kwargs
        resp = self.sec.behaviors.create_security_group_rule(**request_kwargs)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_secgroups_rules.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        secrule = resp.response.entity

#        if expected_name or use_false_values:
#            expected_secgroup.name = expected_name
#        if expected_description or use_false_values:
#            expected_secgroup.description = expected_description

        # Check the Security Group Rule response
        self.assertSecurityGroupRuleResponse(expected_secrule, secrule)

#    @data_driven_test(data_set_list_negative)
#    def ddtest_security_group_create_negative(self, name=None,
#                                              expected_name=None,
#                                              description=None,
#                                              expected_description=None,
#                                              tenant_id=None,
#                                              security_group_rules=None,
#                                              use_false_values=False,
#                                              http_status=None,
#                                              test_desc=None,
#                                              error_type=None):
#        """
#        @summary: Negative test creating a Security Group
#        """
#        secgroup_data = self.expected_secgroup
#        request_kwargs = dict(
#            name=secgroup_data.name,
#            description=secgroup_data.description,
#            raise_exception=False)
#
#        if name or use_false_values:
#            request_kwargs['name'] = name
#        if description or use_false_values:
#            request_kwargs['description'] = description
#        if tenant_id == False:
#            request_kwargs['tenant_id'] = self.alt_user.tenant_id
#        elif tenant_id or use_false_values:
#            request_kwargs['tenant_id'] = tenant_id
#        print request_kwargs
#
#        print secgroup_data
#        resp = self.sec.behaviors.create_security_group(**request_kwargs)
#        print resp
#        # Security Group create should be unavailable
#        msg = ('(negative) Creating a Security Group with '
#               '{test_description}').format(test_description=test_desc)
#        status_code = getattr(SecurityGroupsResponseCodes, http_status)
#        if error_type:
#            error_type = getattr(SecurityGroupsErrorTypes, error_type)
#        self.assertNegativeResponse(
#            resp=resp, status_code=status_code, msg=msg,
#            delete_list=self.delete_secgroups,
#            error_type=error_type)
