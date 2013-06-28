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
from cloudcafe.cloudkeep.barbican.orders.models.order import Order
from test_repo.cloudkeep.barbican.fixtures import OrdersFixture


class OrdersAPI(OrdersFixture):

    def test_create_order(self):
        resp = self.behaviors.create_order_from_config()
        self.assertEqual(resp['status_code'], 202)

    def test_get_order_metadata(self):
        """ Checks metadata of secret created by order. Assumes that the
        order status will be active and not pending.
        """
        resps = self.behaviors.create_and_check_order(
            mime_type="application/octet-stream",
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        create_resp = resps['create_resp']
        self.assertEqual(create_resp['status_code'], 202)

        ord_resp = resps['get_order_resp']
        self.assertEqual(ord_resp.status_code, 200)
        self.assertEqual(ord_resp.entity.status, 'ACTIVE')

        metadata = ord_resp.entity.secret
        self.assertEqual(metadata.name, self.config.name)
        self.assertEqual(metadata.cypher_type, self.config.cypher_type)
        self.assertEqual(metadata.algorithm, self.config.algorithm)
        self.assertEqual(metadata.bit_length, self.config.bit_length)

    def test_get_order(self):
        # Create an order to get
        resp = self.behaviors.create_order_from_config()
        self.assertEqual(resp['status_code'], 202)

        # Verify Creation
        get_resp = self.orders_client.get_order(resp['order_id'])
        order = get_resp.entity
        order_status = (order.status == Order.STATUS_ACTIVE or
                        order.status == Order.STATUS_PENDING)

        self.assertEqual(get_resp.status_code, 200)
        self.assertIsNotNone(order.secret_href)
        self.assertTrue(order_status)

    def test_delete_order(self):
        # Create an order to delete
        resp = self.behaviors.create_order_from_config()
        self.assertEqual(resp['status_code'], 202)

        del_resp = self.behaviors.delete_order(resp['order_id'])
        self.assertEqual(del_resp.status_code, 200)

    def test_get_orders(self):
        # Create 10 orders
        for i in range(0, 11):
            self.behaviors.create_order_from_config()

        resp = self.orders_client.get_orders()
        order_group = resp.entity
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(order_group.orders), 10)
