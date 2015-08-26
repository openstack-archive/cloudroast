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

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import DataDrivenFixture, \
    data_driven_test
from cloudroast.networking.networks.fixtures \
    import NetworkingSecurityGroupsFixture
from cloudcafe.networking.networks.extensions.security_groups_api.constants \
    import SecurityGroupsErrorTypes, SecurityGroupsResponseCodes


LONG_DESCRIPTION_DATA = 'Long Security Group Test text description' * 10
LONG_NAME_DATA = 'Long Security Group Test text name name name' * 10


# Creating data sets for data driven testing
data_set_list = DatasetList()
data_set_list.append_new_dataset(
    name='w_name',
    data_dict={"name": 'test_secgroup_name_update'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_description',
    data_dict={"description": 'Security Group updated description'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_name_and_description',
    data_dict={"name": 'test_secgroup_name_update',
               "description": 'Security Group updated description'},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])
data_set_list.append_new_dataset(
    name='w_blank_name_and_description',
    data_dict={"name": '', "expected_name": '', "description": '',
               "expected_description": '', "use_false_values": True},
    tags=['sec_group', 'post', 'positive', 'rbac_creator'])


# Data set for negative testing
data_set_list_negative = DatasetList()

# Testing with other tenant_id in the request body
data_set_list_negative.append_new_dataset(
    name='w_other_tenant_id',
    data_dict={"name": 'test_secgroup_update_neg', "tenant_id": False,
               "http_status": 'BAD_REQUEST',
               "test_desc": 'another tenant ID on the request body',
               "error_type": 'HTTP_BAD_REQUEST'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_invalid_tenant_id',
    data_dict={"name": 'test_secgroup_update_neg', "tenant_id": '555555',
               "http_status": 'BAD_REQUEST',
               "test_desc": 'invalid tenant ID on the request body',
               "error_type": 'HTTP_BAD_REQUEST'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_blank_tenant_id',
    data_dict={"name": 'test_secgroup_update_neg', "tenant_id": '',
               "use_false_values": True,
               "http_status": 'BAD_REQUEST',
               "test_desc": 'invalid tenant ID on the request body',
               "error_type": 'HTTP_BAD_REQUEST'},
    tags=['sec_group', 'post', 'negative', 'rbac_creator'])

# Bug fix available on Neutron .224
data_set_list_negative.append_new_dataset(
    name='w_long_description',
    data_dict={"name": 'test_secgroup_create_neg',
               "http_status": 'BAD_REQUEST',
               "test_desc": 'description longer than 255 chars',
               "error_type": 'HTTP_BAD_REQUEST',
               "description": LONG_DESCRIPTION_DATA},
    tags=['bug', 'post', 'negative', 'rbac_creator'])
data_set_list_negative.append_new_dataset(
    name='w_long_name',
    data_dict={"name": 'test_secgroup_create_neg',
               "http_status": 'BAD_REQUEST',
               "test_desc": 'name longer than 255 chars',
               "name": LONG_NAME_DATA},
    tags=['bug', 'post', 'negative', 'rbac_creator'])


@DataDrivenFixture
class SecurityGroupUpdateTest(NetworkingSecurityGroupsFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(SecurityGroupUpdateTest, cls).setUpClass()
        cls.expected_secgroup = cls.get_expected_secgroup_data()
        cls.expected_secgroup.name = 'test_secgroup_update'
        cls.expected_secgroup.description = 'testing security group update'
        cls.expected_secrule = cls.get_expected_secrule_data()

    def setUp(self):
        self.secgroup = self.create_test_secgroup(self.expected_secgroup)
        self.expected_secrule.security_group_id = self.secgroup.id
        secrule1 = self.create_test_secrule(self.expected_secrule)
        secrule2 = self.create_test_secrule(self.expected_secrule)
        self.expected_secgroup.security_group_rules = [secrule1, secrule2]

        # Checking the security rule is in the group
        resp = self.sec.behaviors.get_security_group(
            security_group_id=self.secgroup.id)
        self.assertFalse(resp.failures)
        self.secgroup = resp.response.entity

        # Check the Security Group response
        self.assertSecurityGroupResponse(self.expected_secgroup, self.secgroup,
                                         check_exact_name=False)

    def tearDown(self):
        self.expected_secgroup.security_group_rules = []
        self.secGroupCleanUp()

    @data_driven_test(data_set_list)
    def ddtest_security_group_update(self, name=None,
                                     expected_name=None,
                                     description=None,
                                     expected_description=None,
                                     tenant_id=None,
                                     use_false_values=False):
        """
        @summary: Updating a Security Group
        """
        expected_secgroup = self.secgroup
        request_kwargs = dict(security_group_id=expected_secgroup.id)

        if name or use_false_values:
            request_kwargs['name'] = name
            expected_secgroup.name = name
        if description or use_false_values:
            request_kwargs['description'] = description
            expected_secgroup.description = description
        if tenant_id is True:
            request_kwargs['tenant_id'] = self.user.tenant_id
        elif tenant_id or use_false_values:
            request_kwargs['tenant_id'] = None

        resp = self.sec.behaviors.update_security_group(**request_kwargs)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        updated_secgroup = resp.response.entity

        if expected_name or use_false_values:
            expected_secgroup.name = expected_name
        if expected_description or use_false_values:
            expected_secgroup.description = expected_description

        # Check the Security Group response
        self.assertSecurityGroupResponse(expected_secgroup, updated_secgroup)

    @data_driven_test(data_set_list_negative)
    def ddtest_security_group_update_negative(self, name=None,
                                              description=None,
                                              tenant_id=None,
                                              use_false_values=False,
                                              http_status=None,
                                              test_desc=None,
                                              error_type=None):
        """
        @summary: Negative test updating a Security Group
        """
        expected_secgroup = self.secgroup
        request_kwargs = dict(security_group_id=expected_secgroup.id,
                              raise_exception=False)

        if name or use_false_values:
            request_kwargs['name'] = name
        if description or use_false_values:
            request_kwargs['description'] = description
        if tenant_id is False:
            request_kwargs['tenant_id'] = self.alt_user.tenant_id
        elif tenant_id or use_false_values:
            request_kwargs['tenant_id'] = tenant_id

        resp = self.sec.behaviors.update_security_group(**request_kwargs)

        # Security Group create should be unavailable
        msg = ('(negative) Updating a Security Group with '
               '{test_description}').format(test_description=test_desc)
        status_code = getattr(SecurityGroupsResponseCodes, http_status)
        if error_type:
            error_type = getattr(SecurityGroupsErrorTypes, error_type)
        self.assertNegativeResponse(
            resp=resp, status_code=status_code, msg=msg,
            delete_list=self.delete_secgroups,
            error_type=error_type)
