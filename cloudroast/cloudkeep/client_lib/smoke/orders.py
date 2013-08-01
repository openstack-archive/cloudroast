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
from cloudcafe.cloudkeep.common.states import OrdersStates
from cloudroast.cloudkeep.client_lib.fixtures import OrdersFixture


class OrdersAPI(OrdersFixture):

    @tags(type='positive')
    def test_create_order(self):
        """Covers creating an order with the barbicanclient library."""
        resp = self.cl_behaviors.create_and_check_order()
        self.assertEqual(resp.get_status_code, 200,
                         'Returned unexpected response code')

    @tags(type='positive')
    def test_create_order_metadata(self):
        """Covers creating an order with barbicanclient library and checking
        the metadata of the order.
        """
        resp = self.cl_behaviors.create_and_check_order(
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp.get_status_code, 200,
                         'Returned unexpected response code')

        order = resp.entity
        secret = order.secret

        self.assertEqual(order.status, OrdersStates.ACTIVE)
        self.assertEqual(secret['mime_type'], self.config.mime_type)
        self.assertEqual(secret['name'], self.config.name)
        self.assertEqual(secret['algorithm'], self.config.algorithm)
        self.assertEqual(secret['bit_length'], self.config.bit_length)
        self.assertEqual(secret['cypher_type'], self.config.cypher_type)

    @tags(type='positive')
    def test_get_order_by_href(self):
        """Covers getting an order by href with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Barbican returned unexpected response code')

        order = self.cl_client.get_order(resp.ref)
        self.assertIsNotNone(order)

    @tags(type='positive')
    def test_get_order_by_id(self):
        """Covers getting an order by id with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Barbican returned unexpected response code')

        order = self.cl_client.get_order_by_id(resp.id)
        self.assertIsNotNone(order)

    @tags(type='positive')
    def test_order_get_secret(self):
        """Covers getting a secret using the order get method."""
        resps = self.barb_behaviors.create_and_check_order()
        order_resp = resps.get_resp
        secret_resp = self.secrets_client.get_secret(
            ref=order_resp.entity.secret_href)

        self.assertEqual(resps.create_resp.status_code, 202,
                         'Barbican returned unexpected response code')
        self.assertEqual(order_resp.status_code, 200,
                         'Barbican returned unexpected response code')
        self.assertEqual(secret_resp.status_code, 200,
                         'Barbican returned unexpected response code')

        order = self.cl_client.get_order(order_resp.url)
        secret = order.get_secret()
        self.assertEqual(secret.id, secret_resp.entity.get_id(),
                         'Secrets do not match')

    @tags(type='positive')
    def test_delete_order_by_href(self):
        """Covers deleting an order by href with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Returned unexpected response code')

        self.cl_behaviors.delete_order(resp.ref)
        # Deleting here because using two different behaviors
        self.barb_behaviors.remove_from_created_orders(order_id=resp.id)

        get_resp = self.barb_client.get_order(resp.id)
        self.assertEqual(get_resp.status_code, 404,
                         'Should have failed with 404')

    @tags(type='positive')
    def test_delete_order_by_id(self):
        """Covers deleting an order by id with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Returned unexpected response code')

        self.cl_behaviors.delete_order_by_id(resp.id)
        # Deleting here because using two different behaviors
        self.barb_behaviors.remove_from_created_orders(
            order_id=resp.id)

        get_resp = self.barb_client.get_order(resp.id)
        self.assertEqual(get_resp.status_code, 404,
                         'Should have failed with 404')

    @tags(type='positive')
    def test_list_orders(self):
        """Covers listing orders with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Returned unexpected response code')

        list_tuple = self.cl_client.list_orders(limit=10, offset=0)
        orders = list_tuple[0]
        self.assertGreater(len(orders), 0)

    @tags(type='positive')
    def test_list_orders_by_href(self):
        """Covers listing orders by href with barbicanclient library."""
        resp = self.barb_behaviors.create_order_from_config(
            use_expiration=False)
        self.assertEqual(resp.status_code, 202,
                         'Barbican returned unexpected response code')

        list_tuple = self.cl_client.list_orders_by_href()
        orders = list_tuple[0]
        self.assertGreater(len(orders), 0)
