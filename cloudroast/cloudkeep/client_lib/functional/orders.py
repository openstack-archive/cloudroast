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
from unittest import skip
from requests.exceptions import MissingSchema

from barbicanclient.client import HTTPClientError as ClientException
from cafe.drivers.unittest.decorators import tags
from cloudcafe.cloudkeep.common.responses import CloudkeepResponse
from cloudcafe.cloudkeep.common.states import SecretsStates
from cloudroast.cloudkeep.client_lib.fixtures import OrdersFixture, \
    OrdersPagingFixture


class OrdersAPI(OrdersFixture):

    @tags(type='negative')
    def test_create_order_w_only_content_type(self):
        self.assertRaises(
            ClientException, self.cl_behaviors.create_order,
            payload_content_type=self.config.payload_content_type)

    @tags(type='negative')
    def test_create_order_w_null_values(self):
        self.assertRaises(ClientException, self.cl_behaviors.create_order)

    @tags(type='positive')
    def test_create_order_w_null_name(self):
        order = self.cl_behaviors.create_order(
            name=None,
            payload_content_type=self.config.payload_content_type,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            mode=self.config.mode)
        self.assertIsNotNone(order)
        self.assertIn('http', order)

    @tags(type='positive')
    def test_create_order_w_empty_name(self):
        """Covers creating order without an empty name."""
        order = self.cl_behaviors.create_order(
            name='',
            payload_content_type=self.config.payload_content_type,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            mode=self.config.mode)

        self.assertIsNotNone(order)
        self.assertIn('http', order)

    @tags(type='negative')
    def test_create_order_w_invalid_mime_type(self):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_order_overriding_cfg,
                          payload_content_type='crypto/boom')

    @tags(type='negative')
    def test_create_order_w_invalid_bit_length(self):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_order_overriding_cfg,
                          bit_length='not-an-int')

    @tags(type='negative')
    def test_create_order_w_negative_bit_length(self):
        self.assertRaises(ClientException,
                          self.cl_behaviors.create_order_overriding_cfg,
                          bit_length=-1)

    @tags(type='positive')
    def test_create_order_checking_secret_metadata(self):
        """ Assumes that the order status is active and not pending."""
        order_ref = self.cl_behaviors.create_order_from_config()
        order = self.cl_client.get_order(order_ref)

        # Retrieve automatically created secret metadata
        secret_id = CloudkeepResponse.get_id_from_ref(order.secret_ref)
        secret = self.secrets_client.get_secret(secret_id).entity

        self.assertIsNotNone(secret)
        self.assertEqual(secret.name, self.config.name)
        self.assertEqual(secret.mode, self.config.mode)
        self.assertEqual(secret.algorithm, self.config.algorithm)
        self.assertEqual(secret.bit_length, self.config.bit_length)
        self.assertEqual(secret.content_types.get('default'),
                         self.config.payload_content_type)

    @tags(type='negative')
    def test_delete_nonexistent_order(self):
        self.assertRaises(MissingSchema,
                          self.cl_behaviors.delete_order,
                          'not-an-href')

    @tags(type='negative')
    def test_get_nonexistent_order(self):
        self.assertRaises(MissingSchema,
                          self.cl_client.get_order,
                          'not-an-href')

    @skip('Not implemented')
    @tags(type='positive')
    def test_get_order_w_expiration(self):
        """ Assumes that order status is active and not pending."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=True)
        self.assertEqual(resp.status_code, 202)

        order_ref = resp.ref
        order = self.cl_client.get_order(href=order_ref)
        secret = order.secret
        self.assertIsNotNone(secret['expiration'])

class OrdersPagingAPI(OrdersPagingFixture):

    @tags(type='positive')
    def test_list_orders_limit_and_offset(self):
        # First set of orders
        order_group1 = self.cl_client.list_orders(limit=10, offset=0)

        # Second set of orders
        order_group2 = self.cl_client.list_orders(limit=10, offset=10)

        self._check_for_duplicates(group1=order_group1, group2=order_group2)
