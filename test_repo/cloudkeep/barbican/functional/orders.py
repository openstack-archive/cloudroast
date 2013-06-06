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
from test_repo.cloudkeep.barbican.fixtures import OrdersFixture


class OrdersAPI(OrdersFixture):

    def test_create_order_with_null_mime_type(self):
        """ Covers issue where you attempt to create an order with the
        mime_type attribute set to null and the request appears to fail
        without a status code.
        - Reported in Barbican GitHub Issue #92
        """
        resp = self.behaviors.create_order(
            mime_type=None,
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp['status_code'], 400, 'Returned bad status code')

    def test_create_order_wout_name(self):
        """ When you attempt to create an order without the name attribute the
         request appears to fail without a status code.
        - Reported in Barbican GitHub Issue #93
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=None,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp['status_code'], 202, 'Returned bad status code')

    def test_create_order_with_invalid_mime_type(self):
        """ Covers defect where you attempt to create an order with an invalid
         mime_type and the request fails without a status code.
        - Reported in Barbican GitHub Issue #92
        """
        resp = self.behaviors.create_order(
            mime_type="trace/boom",
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp['status_code'], 400, 'Returned bad status code')
