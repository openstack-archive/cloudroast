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
import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class NetworkCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(NetworkCreateTest, cls).setUpClass()

    def setUp(self):
        self.expected_network = self.get_expected_network_data()

    @tags('smoke', 'creator')
    def test_network_create(self):
        """
        @summary: Creating a network
        """
        # Creating network
        resp = self.networks.behaviors.create_network(
            name=self.expected_network.name, use_exact_name=True,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @tags('smoke', 'creator')
    def test_network_create_w_long_name(self):
        """
        @summary: Creating a network with a 40 char name
        """
        expected_network = self.expected_network
        expected_network.name = '1234567890123456789012345678901234567890'

        # Creating network with a 40 char name
        resp = self.networks.behaviors.create_network(
            name=expected_network.name, use_exact_name=True,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @unittest.skip('Needs RM10088 fix')
    @tags('negative', 'creator', 'quark')
    def test_network_create_w_long_name_trimming(self):
        """
        @summary: Creating a network with a 50 char name (name should be
            trimmed to 40 chars)
        """
        expected_network = self.expected_network
        expected_network.name = ('1234567890123456789012345678901234567890'
                                 '1234567890')

        # Creating network with a 40 char name
        resp = self.networks.behaviors.create_network(
            name=expected_network.name, use_exact_name=True,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Trimming should leave the name with 40 chars
        expected_network.name = '1234567890123456789012345678901234567890'

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @tags('negative', 'creator', 'quark')
    def test_network_create_w_shared(self):
        """
        @summary: Negative test creating a network with the shared attribute.
            This action should only be available at the admin API.
        """
        # Trying to create the expected network
        resp = self.networks.behaviors.create_network(
            shared=True, raise_exception=False)

        # Just in case the network gets created
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)
            self.failed_networks.append(resp.response.entity.id)

        # Network create should be unavailable with the shared attribute
        msg = ('Unexpected HTTP response {0} instead of the expected {1} '
               'while creating a network with the shared parameter').format(
                resp.response.status_code, NeutronResponseCodes.FORBIDDEN)
        self.assertEqual(resp.response.status_code,
                         NeutronResponseCodes.FORBIDDEN, msg)
        self.assertIsNone(resp.response.entity, 'Unexpected entity')
        self.assertTrue(resp.failures, 'Missing expected failures')

    @tags('positive', 'creator')
    def test_network_create_w_admin_state_up_true(self):
        """
        @summary: Creating a network with the admin_state_up attribute as true
        """
        # The expected network will always have the admin_state_up True
        admin_state_up = True

        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=self.expected_network.name,
            admin_state_up=admin_state_up,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @tags('positive', 'creator', 'quark')
    def test_network_create_w_admin_state_up_false(self):
        """
        @summary: Creating a network with the admin_state_up attribute as false
        """
        # The expected network will always have the admin_state_up True
        admin_state_up = False

        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=self.expected_network.name,
            admin_state_up=admin_state_up,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @tags('positive', 'creator')
    def test_network_create_w_tenant_id(self):
        """
        @summary: Creating a network with the tenant_id
        """
        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=self.expected_network.name,
            tenant_id=self.expected_network.tenant_id,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(self.expected_network, network)

    @unittest.skipIf(not NetworkingSecondUserConfig().tenant_id,
                     'Missing secondary networking user in config file')
    @tags('negative', 'alt_user', 'creator')
    def test_network_create_w_another_tenant_id(self):
        """
        @summary: Negative test creating a network under another tenant.
            This action should only be available at the admin API.
        """
        # Trying to create a network with another tenant_id
        resp = self.networks.behaviors.create_network(
            tenant_id=self.alt_user.tenant_id, raise_exception=False)

        # Just in case the network gets created
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)
            self.failed_networks.append(resp.response.entity.id)

        # Network create should be unavailable with another tenant ID
        msg = ('Unexpected HTTP response {0} instead of the expected {1} '
               'while creating a network with another tenant ID').format(
                resp.response.status_code, NeutronResponseCodes.FORBIDDEN)
        self.assertEqual(resp.response.status_code,
                         NeutronResponseCodes.BAD_REQUEST, msg)
        self.assertIsNone(resp.response.entity, 'Unexpected entity')
        self.assertTrue(resp.failures, 'Missing expected failures')

    @tags('negative', 'creator')
    def test_network_create_w_invalid_name(self):
        """
        @summary: Creating a network with invalid name
        """
        expected_network = self.expected_network
        expected_network.name = 'TestName2<script>alert(/xxs/);</script>'

        # Creating the subnet
        resp = self.networks.behaviors.create_network(
            name=expected_network.name,
            raise_exception=False, use_exact_name=True)

        # Network create with invalid name should be unavailable
        msg = '(negative) Network create with invalid name: {0}'.format(
            expected_network.name)

        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.BAD_REQUEST, msg=msg,
            delete_list=self.delete_subnets)
