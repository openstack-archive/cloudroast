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
from os import path

from cafe.drivers.unittest.decorators import tags
from cloudcafe.cloudkeep.common.states import OrdersStates
from cloudroast.cloudkeep.client_lib.fixtures import OrdersFixture


class OrdersAPI(OrdersFixture):

    @tags(type='positive')
    def test_create_order(self):
        resp = self.cl_behaviors.create_and_check_order()
        self.assertEqual(resp.get_status_code, 200)

        order = resp.get_resp.entity
        secret = order.secret

        self.assertEqual(order.status, OrdersStates.ACTIVE)
        self.assertEqual(secret.name, self.config.name)
        self.assertEqual(secret.algorithm, self.config.algorithm)
        self.assertEqual(secret.bit_length, self.config.bit_length)
        self.assertEqual(secret.mode, self.config.mode)

    @tags(type='positive')
    def test_get_order(self):
        resp = self.barb_behaviors.create_order_from_config()
        self.assertEqual(resp.status_code, 202)

        order = self.cl_client.get_order(resp.ref)
        self.assertIsNotNone(order)
        self.assertEqual(order.status, OrdersStates.ACTIVE)
        self.assertIn('http', order.order_ref)
        self.assertIn('http', order.secret_ref)

    @tags(type='positive')
    def test_get_secret_referenced_from_order(self):
        resps = self.cl_behaviors.create_and_check_order()
        order_resp = resps.get_resp
        self.assertIsNotNone(order_resp)
        self.assertEqual(order_resp.status_code, 200)

        order = order_resp.entity

        secret_id = path.split(order.secret_href)[-1]
        secret_resp = self.secrets_client.get_secret(secret_id)
        self.assertEqual(secret_resp.status_code, 200)
        self.assertIsNotNone(secret_resp.entity)
        self.assertEqual(secret_resp.entity.name, self.config.name)

    @tags(type='positive')
    def test_delete_order(self):
        resp = self.barb_behaviors.create_order_from_config()
        self.assertEqual(resp.status_code, 202)

        self.cl_behaviors.delete_order(resp.ref)
        # Deleting here because using two different behaviors
        self.barb_behaviors.remove_from_created_orders(order_id=resp.id)

        get_resp = self.barb_client.get_order(resp.id)
        self.assertEqual(get_resp.status_code, 404)

    @tags(type='positive')
    def test_list_orders(self):
        resp = self.barb_behaviors.create_order_from_config()
        self.assertEqual(resp.status_code, 202)

        order_list = self.cl_client.list_orders(limit=1, offset=0)
        self.assertEqual(len(order_list), 1)
