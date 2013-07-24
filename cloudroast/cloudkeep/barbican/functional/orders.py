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
from uuid import uuid4
from sys import maxint

from cloudroast.cloudkeep.barbican.fixtures import OrdersFixture, \
    OrdersPagingFixture
from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools import randomstring


class OrdersAPI(OrdersFixture):

    def check_expiration_iso8601_timezone(self, timezone, offset):
        """ Creates an order with an expiration for the timezone and
        offset and checks that the creation succeeds and the expiration
        is correct.
        """
        one_day_ahead = (datetime.today() + timedelta(days=1))
        timestamp = '{time}{timezone}'.format(
            time=one_day_ahead,
            timezone=timezone)

        resp = self.behaviors.create_order_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp.status_code, 202)

        order = self.orders_client.get_order(resp.id).entity
        exp = datetime.strptime(order.secret.expiration,
                                '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(exp, one_day_ahead + timedelta(hours=offset),
                         'Response didn\'t return the expected time')

    def check_invalid_expiration_timezone(self, timezone):
        """ Creates an order with an expiration for the given invalid
        timezone and checks that the creation fails.
        """
        timestamp = '{time}{timezone}'.format(
            time=(datetime.today() + timedelta(days=1)),
            timezone=timezone)

        resp = self.behaviors.create_order_overriding_cfg(
            expiration=timestamp)
        self.assertEqual(resp.status_code, 400)

    @tags(type='negative')
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
        self.assertEqual(resp.status_code, 400, 'Returned bad status code')

    @tags(type='negative')
    def test_create_order_with_empty_mime_type(self):
        """ Covers case of creating an order with an empty String as the
        mime type. Should return 400.
        """
        resp = self.behaviors.create_order(
            mime_type='',
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp.status_code, 400, 'Returned bad status code')

    @tags(type='positive')
    def test_create_order_wout_name(self):
        """ When you attempt to create an order without the name attribute the
         request appears to fail without a status code.
        - Reported in Barbican GitHub Issue #93
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='positive')
    def test_create_order_w_empty_name(self):
        """ Covers case of creating an order with an empty String as the name
        attribute.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name='',
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='negative')
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
        self.assertEqual(resp.status_code, 400, 'Returned bad status code')

    @unittest2.skip('Issue #140')
    @tags(type='positive')
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

        secret_ref = resps.get_resp.entity.secret_href
        secret_resp = self.secrets_client.get_secret(ref=secret_ref,
                                                     mime_type='text/plain')
        self.assertEqual(secret_resp.status_code, 200,
                         'Returned bad status code')

    @tags(type='negative')
    def test_get_order_that_doesnt_exist(self):
        """
        Covers case of getting a non-existent order. Should return 404.
        """
        resp = self.orders_client.get_order('not_an_order')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='negative')
    def test_delete_order_that_doesnt_exist(self):
        """
        Covers case of deleting a non-existent order. Should return 404.
        """
        resp = self.orders_client.delete_order('not_an_order')
        self.assertEqual(resp.status_code, 404, 'Should have failed with 404')

    @tags(type='positive')
    def test_create_order_w_expiration(self):
        """
        Covers creating order with expiration.
        """
        resp = self.behaviors.create_order_from_config(use_expiration=True)
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='negative')
    def test_create_order_w_invalid_expiration(self):
        """
        Covers creating order with expiration that has already passed.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            expiration='2000-01-10T14:58:52.546795')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_null_entries(self):
        """
        Covers creating order with all null entries.
        """
        resp = self.behaviors.create_order()
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_empty_entries(self):
        """ Covers case of creating an order with empty Strings for all
        entries. Should return a 400.
        """
        resp = self.behaviors.create_order(name='', expiration='',
                                           algorithm='', cypher_type='',
                                           mime_type='')
        self.assertEqual(resp.status_code, 400,
                         'Should have failed with 400')

    @tags(type='positive')
    def test_create_order_w_empty_checking_name(self):
        """ When an order is created with an empty name attribute, the
        system should return the secret's UUID on a get. Extends coverage of
        test_create_order_w_empty_name. Assumes that the order status will be
        active and not pending.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name='',
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)

        get_resp = self.orders_client.get_order(resp.id)
        order = get_resp.entity
        secret_id = order.get_secret_id()
        secret = get_resp.entity.secret
        self.assertEqual(secret.name, secret_id,
                         'Name did not match secret\'s UUID')

    @tags(type='positive')
    def test_create_order_wout_name_checking_name(self):
        """ When an order is created with a null name attribute, the
        system should return the secret's UUID on a get. Extends coverage of
        test_create_order_wout_name. Assumes that the order status will be
        active and not pending.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=None,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type)

        get_resp = self.orders_client.get_order(resp.id)
        order = get_resp.entity
        secret_id = order.get_secret_id()
        secret = get_resp.entity.secret
        self.assertEqual(secret.name, secret_id,
                         'Name did not match secret\'s UUID')

    @tags(type='positive')
    def test_create_order_with_long_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #131
        """
        self.check_expiration_iso8601_timezone('-05:00', 5)
        self.check_expiration_iso8601_timezone('+05:00', -5)

    @unittest2.skip('Issue #135')
    @tags(type='positive')
    def test_create_order_with_short_expiration_timezone(self):
        """ Covers case of a timezone being added to the expiration.
        The server should convert it into zulu time.
        - Reported in Barbican GitHub Issue #135
        """
        self.check_expiration_iso8601_timezone('-01', 1)
        self.check_expiration_iso8601_timezone('+01', -1)

    @unittest2.skip('Issue #134')
    @tags(type='negative')
    def test_create_order_with_bad_expiration_timezone(self):
        """ Covers case of a malformed timezone being added to the expiration.
        - Reported in Barbican GitHub Issue #134
        """
        self.check_invalid_expiration_timezone('-5:00')

    @tags(type='positive')
    def test_create_order_w_128_bit_length(self):
        """Covers case of creating an order with a 128 bit length."""
        resps = self.behaviors.create_and_check_order(bit_length=128)
        self.assertEqual(resps.create_resp.status_code,
                         202, 'Returned bad status code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 128)

    @tags(type='positive')
    def test_create_order_w_192_bit_length(self):
        """Covers case of creating an order with a 192 bit length."""
        resps = self.behaviors.create_and_check_order(bit_length=192)
        self.assertEqual(resps.create_resp.status_code,
                         202, 'Returned bad status code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 192)

    @tags(type='positive')
    def test_create_order_w_256_bit_length(self):
        """Covers case of creating an order with a 256 bit length."""
        resps = self.behaviors.create_and_check_order(bit_length=256)
        self.assertEqual(resps.create_resp.status_code,
                         202, 'Returned bad status code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(resps.get_resp.status_code, 200)
        self.assertIs(type(secret.bit_length), int)
        self.assertEqual(secret.bit_length, 256)

    @tags(type='positive')
    def test_order_and_secret_metadata_same(self):
        """ Covers checking that secret metadata from a get on the order and
        secret metadata from a get on the secret are the same. Assumes
        that the order status will be active and not pending.
        """
        resp = self.behaviors.create_and_check_order()
        order = resp.get_resp.entity
        order_metadata = order.secret
        secret_ref = order.secret_href
        secret_resp = self.secrets_client.get_secret(ref=secret_ref)
        secret_metadata = secret_resp.entity

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

    @tags(type='negative')
    def test_creating_order_w_invalid_bit_length(self):
        """ Cover case of creating an order with a bit length that is not
        an integer. Should return 400.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            bit_length='not-an-int')
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_order_w_negative_bit_length(self):
        """ Covers case of creating an order with a bit length that is
        negative. Should return 400.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            bit_length=-1)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_creating_order_wout_bit_length(self):
        """Covers case where order is created without bit length.
        Should return 400.
        - Reported in Barbican GitHub Issue #156
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            cypher_type=self.config.cypher_type,
            bit_length=None)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_create_order_w_cbc_cypher_type(self):
        """Covers case of creating an order with a cbc cypher type."""
        resp = self.behaviors.create_order_overriding_cfg(cypher_type='cbc')
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='positive')
    def test_create_order_w_aes_algorithm(self):
        """Covers case of creating an order with an aes algorithm."""
        resp = self.behaviors.create_order_overriding_cfg(algorithm='aes')
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='positive')
    def test_create_order_w_app_octet_stream_mime_type(self):
        """Covers case of creating an order with an application/octet-stream
        mime type.
        """
        resp = self.behaviors.create_order_overriding_cfg(
            mime_type='application/octet-stream')
        self.assertEqual(resp.status_code, 202, 'Returned bad status code')

    @tags(type='positive')
    def test_create_order_w_alphanumeric_name(self):
        """Covers case of creating an order with an alphanumeric name."""
        name = randomstring.get_random_string(prefix='1a2b')
        resps = self.behaviors.create_and_check_order(name=name)
        self.assertEqual(resps.create_resp.status_code, 202,
                         'Returned bad status code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_create_order_w_punctuation_in_name(self):
        """Covers case of creating order with miscellaneous punctuation and
        symbols in the name.
        """
        name = '~!@#$%^&*()_+`-={}[]|:;<>,.?"'
        resps = self.behaviors.create_and_check_order(name=name)
        self.assertEqual(resps.create_resp.status_code, 202,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_create_order_w_uuid_as_name(self):
        """Covers case of creating an order with a random uuid as the name."""
        uuid = str(uuid4())
        resps = self.behaviors.create_and_check_order(name=uuid)
        self.assertEqual(resps.create_resp.status_code, 202,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(secret.name, uuid, 'Secret name is not correct')

    @tags(type='positive')
    def test_create_order_w_name_of_len_255(self):
        """Covers case of creating an order with a 255 character name."""
        name = randomstring.get_random_string(size=255)
        resps = self.behaviors.create_and_check_order(name=name)
        self.assertEqual(resps.create_resp.status_code, 202,
                         'Returned unexpected response code')

        secret = resps.get_resp.entity.secret
        self.assertEqual(secret.name, name, 'Secret name is not correct')

    @tags(type='positive')
    def test_order_hostname_response(self):
        """Covers case of checking that hostname of order_ref is the same
        as the configured hostname.
        - Reported in Barbican GitHub Issue #182
        """
        create_resp = self.behaviors.create_order_from_config()
        self.assertEqual(create_resp.status_code, 202,
                         'Returned unexpected response code')

        # Get secret using returned secret_ref
        ref_get_resp = self.orders_client.get_order(
            ref=create_resp.ref)
        self.assertEqual(ref_get_resp.status_code, 200,
                         'Returned unexpected response code')

        # Get secret using secret id and configured base url
        config_get_resp = self.orders_client.get_order(
            order_id=create_resp.id)
        self.assertEqual(config_get_resp.status_code, 200,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_update_order(self):
        """Covers case of putting to an order. Should return 405."""
        resp = self.behaviors.create_order_from_config()
        put_resp = self.orders_client.update_order(
            order_id=resp.id,
            mime_type=self.config.mime_type,
            data='test-update-order')
        self.assertEqual(put_resp.status_code, 405,
                         'Should have failed with 405')

    @tags(type='negative')
    def test_create_order_w_plain_text(self):
        """Covers case of creating order with plain text.
        Should return 400."""
        resp = self.behaviors.create_order_w_plain_text(
            plain_text='test-create-order-w-plain-text',
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type,
            expiration=None)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_empty_plain_text(self):
        """Covers case of creating order with an empty String as plain text.
        Should return 400."""
        resp = self.behaviors.create_order_w_plain_text(
            plain_text='',
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type,
            expiration=None)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_oversized_plain_text(self):
        """Covers case of creating an order with a value larger than the 10k
        limit for the secret plain text attribute. Should return 400.
        """
        data = bytearray().zfill(10001)

        resp = self.behaviors.create_order_w_plain_text(
            plain_text=str(data),
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            bit_length=self.config.bit_length,
            cypher_type=self.config.cypher_type,
            expiration=None)

        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_wout_algorithm(self):
        """Covers case where order is created without an algorithm.
        Should return 400.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=None,
            cypher_type=self.config.cypher_type,
            bit_length=self.config.bit_length)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_wout_cypher_type(self):
        """Covers case where order is created without a cypher type.
        Should return 400.
        """
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=self.config.name,
            algorithm=self.config.algorithm,
            cypher_type=None,
            bit_length=self.config.bit_length)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='positive')
    def test_create_order_w_large_string_as_name(self):
        """Covers case of creating an order with a large String value as
        the name."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_order_overriding_cfg(name=large_string)
        self.assertEqual(resp.status_code, 202,
                         'Returned unexpected response code')

    @tags(type='negative')
    def test_create_order_w_large_string_values(self):
        """Covers case of creating an order with large String values.
        Should return 400."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_order(
            mime_type=self.config.mime_type,
            name=large_string,
            algorithm=large_string,
            cypher_type=large_string)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_large_bit_length(self):
        """Covers case of creating an order with a large integer as
        the bit length. Should return 400."""
        resp = self.behaviors.create_order_overriding_cfg(bit_length=maxint)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_large_string_as_bit_length(self):
        """Covers case of creating secret with a large String as
        the bit length. Should return 400."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_order_overriding_cfg(
            bit_length=large_string)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_large_string_as_mime_type(self):
        """Covers case of creating secret with a large String as
        the bit length. Should return 400."""
        large_string = str(bytearray().zfill(10001))
        resp = self.behaviors.create_order_overriding_cfg(
            mime_type=large_string)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_int_as_name(self):
        """Covers case of creating an order with an integer as the name.
        Should return 400."""
        resp = self.behaviors.create_order_overriding_cfg(name=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_int_as_mime_type(self):
        """Covers case of creating an order with an integer as the mime type.
        Should return 400."""
        resp = self.behaviors.create_order_overriding_cfg(mime_type=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_int_as_algorithm(self):
        """Covers case of creating an order with an integer as the algorithm.
        Should return 400."""
        resp = self.behaviors.create_order_overriding_cfg(algorithm=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')

    @tags(type='negative')
    def test_create_order_w_int_as_cypher_type(self):
        """Covers case of creating an order with an integer as the cypher type.
        Should return 400."""
        resp = self.behaviors.create_order_overriding_cfg(cypher_type=400)
        self.assertEqual(resp.status_code, 400, 'Should have failed with 400')
