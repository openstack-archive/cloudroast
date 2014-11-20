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
from cloudcafe.networking.networks.common.models.response.network \
    import Network
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class NetworkCreateTest(NetworkingAPIFixture):

    @classmethod
    def setUpClass(cls):
        """Setting up test data"""
        super(NetworkCreateTest, cls).setUpClass()

        # Data for creating networks and asserting responses
        cls.network_data = dict(
            status='ACTIVE', subnets=[],
            name='test_net_create', admin_state_up=None,
            tenant_id=cls.net.networking_auth_composite().tenant_id,
            shared=False)

    @tags(type='smoke', rbac='creator')
    def test_network_create(self):
        """
        @summary: Creating a network
        """
        expected_network = Network(**self.network_data)

        # Creating network
        resp = self.networks.behaviors.create_network(
            name=expected_network.name, use_exact_name=True,
            raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @tags(type='negative', rbac='creator')
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

    @tags(type='positive', rbac='creator')
    def test_network_create_w_admin_state_up_true(self):
        """
        @summary: Creating a network with the admin_state_up attribute as true
        """
        expected_network = Network(**self.network_data)
        expected_network.admin_state_up = True

        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=expected_network.name,
            admin_state_up=expected_network.admin_state_up,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @tags(type='positive', rbac='creator')
    def test_network_create_w_admin_state_up_false(self):
        """
        @summary: Creating a network with the admin_state_up attribute as false
        """
        expected_network = Network(**self.network_data)
        expected_network.admin_state_up = False

        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=expected_network.name,
            admin_state_up=expected_network.admin_state_up,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @tags(type='positive', rbac='creator')
    def test_network_create_w_tenant_id(self):
        """
        @summary: Creating a network with the tenant_id
        """
        expected_network = Network(**self.network_data)

        # Creating expected network
        resp = self.networks.behaviors.create_network(
            name=expected_network.name,
            tenant_id=expected_network.tenant_id,
            use_exact_name=True, raise_exception=False)
        if resp.response.entity and hasattr(resp.response.entity, 'id'):
            self.delete_networks.append(resp.response.entity.id)

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)
        network = resp.response.entity

        # Check the Network response
        self.assertNetworkResponse(expected_network, network)

    @unittest.skipIf(not NetworkingSecondUserConfig().tenant_id,
                     'Missing secondary networking user in config file')
    @tags(type='negative', alt_user='yes', rbac='creator')
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
                         NeutronResponseCodes.FORBIDDEN, msg)
        self.assertIsNone(resp.response.entity, 'Unexpected entity')
        self.assertTrue(resp.failures, 'Missing expected failures')
