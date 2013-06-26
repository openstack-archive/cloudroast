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
import unittest2
from datetime import datetime, timedelta
from test_repo.cloudkeep.barbican.fixtures import OrdersFixture


class OrdersAPI(OrdersFixture):

    def check_expiration_iso8601_timezone(self, timezone, offset):
        one_day_ahead = (datetime.today() + timedelta(days=1))
        timestamp = '{time}{timezone}'.format(
            time=one_day_ahead,
            timezone=timezone)

        resp = self.behaviors.create_order_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp['status_code'], 202)

        order = self.orders_client.get_order(resp['order_id']).entity
        exp = datetime.strptime(order.secret.expiration,
                                '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(exp, one_day_ahead + timedelta(hours=offset),
                         'Response didn\'t return the expected time')

    def check_invalid_expiration_timezone(self, timezone):
        timestamp = '{time}{timezone}'.format(
            time=(datetime.today() + timedelta(days=1)),
            timezone=timezone)

        resp = self.behaviors.create_order_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp['status_code'], 400)

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

    @unittest2.skip('Issue #140')
    def test_getting_secret_data_as_plain_text(self):
        """ Covers defect where you attempt to get secret information in
        text/plain, and the request fails to decrypt the information.
        - Reported in Barbican GitHub Issue #140
        """
        resps = self.behaviors.create_and_check_order(
            mime_type="text/plain",
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resps['get_secret_resp'].status_code, 200,
                         'Returned bad status code')

    def test_get_order_that_doesnt_exist(self):
        """
        Covers case of getting a non-existent order. Should return 404.
        """
        resp = self.orders_client.get_order('not_an_order')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    def test_delete_order_that_doesnt_exist(self):
        """
        Covers case of deleting a non-existent order. Should return 404.
        """
        resp = self.orders_client.delete_order('not_an_order')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    def test_order_paging_limit_and_offset(self):
        """
        Covers testing paging limit and offset attributes when getting orders.
        """
        # Create order pool
        for count in range(1, 20):
            self.behaviors.create_order_from_config()

        # First set of orders
        resp = self.orders_client.get_orders(limit=10, offset=0)
        ord_group1 = resp.entity

        # Second set of orders
        resp = self.orders_client.get_orders(limit=20, offset=10)
        ord_group2 = resp.entity

        duplicates = [order for order in ord_group1.orders
                      if order in ord_group2.orders]

        self.assertEqual(len(ord_group1.orders), 10)
        self.assertGreaterEqual(len(ord_group2.orders), 1)
        self.assertEqual(len(duplicates), 0,
                         'Using offset didn\'t return unique orders.')

    def test_find_a_single_order_via_paging(self):
        """
        Covers finding an order with paging.
        """
        resp = self.behaviors.create_order_from_config()
        for count in range(1, 11):
            self.behaviors.create_order_from_config()
        order = self.behaviors.find_order(resp['order_id'])
        self.assertIsNotNone(order, 'Couldn\'t find created order')

    def test_create_order_w_expiration(self):
        """
        Covers creating order with expiration.
        """
        resp = self.behaviors.create_order_from_config(use_expiration=True)
        self.assertEqual(resp['status_code'], 202, 'Returned bad status code')

    def test_create_order_w_invalid_expiration(self):
        """
        Covers creating order with expiration that has already passed.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            expiration='2000-01-10T14:58:52.546795')
        self.assertEqual(resp['status_code'], 400,
                         'Should have failed with 400')

    def test_create_order_w_null_entries(self):
        """
        Covers creating order with all null entries.
        """
        resp = self.behaviors.create_order()
        self.assertEqual(resp['status_code'], 400,
                         'Should have failed with 400')

    def test_create_order_wout_name_checking_name(self):
        """ When an order is created with an empty or null name attribute, the
        system should return the secret's UUID on a get. Extends coverage of
        test_create_order_wout_name. Assumes that the order status will be
        active and not pending.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name="",
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)

        get_resp = self.orders_client.get_order(resp['order_id'])
        secret_id = self.behaviors.get_id_from_ref(
            ref=get_resp.entity.secret_href)
        secret = get_resp.entity.secret
        self.assertEqual(secret.name, secret_id,
                         'Name did not match secret\'s UUID')

    def test_create_order_with_long_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #131
        """
        self.check_expiration_iso8601_timezone('-05:00', 5)
        self.check_expiration_iso8601_timezone('+05:00', -5)

    def test_create_order_with_short_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #135
        """
        self.check_expiration_iso8601_timezone('-01', 1)
        self.check_expiration_iso8601_timezone('+01', -1)

    def test_create_order_with_bad_expiration_timezone(self):
        """ Covers case of a malformed timezone being added to the expiration.
        - Reported in Barbican GitHub Issue #134
        """
        self.check_invalid_expiration_timezone('-5:00')

    def test_create_order_w_bit_length_str(self):
        """
        Covers case of creating an order with a bit length.
        """
        resps = self.behaviors.create_and_check_order(bit_length=128)
        secret = resps['get_order_resp'].entity.secret
        self.assertEqual(resps['get_order_resp'].status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 128)

    def test_order_and_secret_metadata_same(self):
        """ Covers checking that secret metadata from a get on the order and
        secret metadata from a get on the secret are the same. Assumes
        that the order status will be active and not pending.
        """
        resps = self.behaviors.create_and_check_order()

        order_metadata = resps['get_order_resp'].entity.secret
        secret_metadata = resps['get_secret_resp'].entity
        self.assertEqual(order_metadata.name, secret_metadata.name,
                         'Names were not the same')
        self.assertEqual(order_metadata.algorithm, secret_metadata.algorithm,
                         'Algorithms were not the same')
        self.assertEqual(order_metadata.bit_length, secret_metadata.bit_length,
                         'Bit lengths were not the same')
        self.assertEqual(order_metadata.expiration, secret_metadata.expiration,
                         'Expirations were not the same')
        self.assertEqual(order_metadata.mime_type, secret_metadata.mime_type,
                         'Mime types were not the same')
        self.assertEqual(order_metadata.plain_text, secret_metadata.plain_text,
                         'Plain texts were not the same')
        self.assertEqual(order_metadata.cypher_type,
                         secret_metadata.cypher_type,
                         'Cypher types were not the same')

    def test_creating_order_w_invalid_bit_length(self):
        """ Cover case of creating an order with a bit length that is not
        an integer. Should return 400.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            bit_length='not-an-int')
        self.assertEqual(resp['status_code'], 400,
                         'Should have failed with 400')

    def test_creating_order_w_negative_bit_length(self):
        """ Covers case of creating an order with a bit length that is
        negative. Should return 400.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            bit_length=-1)
        self.assertEqual(resp['status_code'], 400,
                         'Should have failed with 400')

    def test_creating_order_wout_bit_length(self):
        """Covers case where order creation fails when bit length is not
        provided.
        - Reported in Barbican GitHub Issue #156
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp['status_code'], 202, 'Returned bad status code')
