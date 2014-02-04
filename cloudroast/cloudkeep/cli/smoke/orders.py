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
from cloudroast.cloudkeep.cli.fixtures import OrdersCLIFixture


class OrdersCLISmokeTests(OrdersCLIFixture):

    @tags('smoke', 'cli')
    def test_create_order(self):
        hateos_ref, resp = self.behavior.create(name='test')
        self.assertEqual(resp.return_code, 0)
        self.assertGreater(len(hateos_ref), 0)

    @tags('smoke', 'cli')
    def test_delete_order(self):
        hateos_ref, resp = self.behavior.create(name='test', clean=False)
        resp = self.client.delete(hateos_ref)
        self.assertEqual(resp.return_code, 0)

    @tags('smoke', 'cli')
    def test_get_order(self):
        hateos_ref, resp = self.behavior.create(name='test')
        self.assertEqual(resp.return_code, 0)

        get_resp = self.client.get(hateos_ref)
        order = get_resp.entity

        self.assertIsNotNone(order)
        self.assertEqual(order.status, 'ACTIVE')

    @tags('smoke', 'cli')
    def test_get_order_list(self):
        # Create 10 orders to capture
        for i in range(10):
            hateos_ref, resp = self.behavior.create(name='test')
            self.assertEqual(resp.return_code, 0)

        resp = self.client.list_orders()
        orders_list = resp.entity

        self.assertIsNotNone(orders_list)
        self.assertEqual(len(orders_list), 10)
