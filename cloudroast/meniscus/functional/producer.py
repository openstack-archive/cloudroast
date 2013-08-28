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
from uuid import uuid4
from cafe.drivers.unittest.decorators import tags
from cloudroast.meniscus.fixtures import ProducerFixture


class TenantAPIProducer(ProducerFixture):

    @tags(type='positive')
    def test_create_producer_with_only_required(self):
        """
        Only name and pattern should be required to create a producer
        """
        resp = self.producer_behaviors.create_producer(
            name=self.tenant_config.producer_name,
            pattern=self.tenant_config.producer_pattern)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_create_producer_with_uuid_name(self):
        """
        Attempting to create producer with uuid for the name
        """
        resp = self.producer_behaviors.create_producer(
            name=str(uuid4()),
            pattern=self.tenant_config.producer_pattern)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

        resp = self.producer_client.get_producer(resp['producer_id'])
        self.assertEqual(resp.status_code, 200)

    @tags(type='positive')
    def test_create_producer_with_durable_set_true(self):
        """
        Make sure we can create a producer with durable set true
        """
        resp = self.producer_behaviors.create_producer(
            name=self.tenant_config.producer_name,
            pattern=self.tenant_config.producer_pattern,
            durable=True)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_create_producer_with_durable_set_false(self):
        """
        Make sure we can create a producer with durable set false
        """
        resp = self.producer_behaviors.create_producer(
            name=self.tenant_config.producer_name,
            pattern=self.tenant_config.producer_pattern,
            durable=False)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_create_producer_with_encrypted_set_true(self):
        """
        Make sure we can create a producer with encrypted set true
        """
        resp = self.producer_behaviors.create_producer(
            name=self.tenant_config.producer_name,
            pattern=self.tenant_config.producer_pattern,
            encrypted=True)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_create_producer_with_encrypted_set_false(self):
        """
        Make sure we can create a producer with encrypted set false
        """
        resp = self.producer_behaviors.create_producer(
            name=self.tenant_config.producer_name,
            pattern=self.tenant_config.producer_pattern,
            encrypted=False)

        self.assertIsNotNone(resp['producer_id'])
        self.assertEqual(resp['request'].status_code, 201)

    @tags(type='positive')
    def test_update_producer_name(self):
        """
        Updating a producer's name
        """
        resp = self.producer_behaviors.create_producer_from_cfg()
        producer_id = resp['producer_id']
        print resp['request'].text
        self.assertIsNotNone(producer_id)
        self.assertEqual(resp['request'].status_code, 201)

        pattern = self.tenant_config.producer_pattern
        resp = self.producer_client.update_producer(producer_id=producer_id,
                                                    name='new_name',
                                                    pattern=pattern)
        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        self.assertEqual(resp.entity.name, 'new_name')

    @tags(type='positive')
    def test_update_producer_durable_w_true(self):
        """
        Updating a producer's durable with True
        """
        resp = self.producer_behaviors.create_producer_from_cfg()
        producer_id = resp['producer_id']
        self.assertIsNotNone(producer_id)
        self.assertEqual(resp['request'].status_code, 201)

        pattern = self.tenant_config.producer_pattern
        name = self.tenant_config.producer_name
        resp = self.producer_client.update_producer(producer_id=producer_id,
                                                    durable=True,
                                                    pattern=pattern,
                                                    name=name)
        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        self.assertTrue(resp.entity.durable)

    @tags(type='positive')
    def test_update_producer_durable_w_false(self):
        """
        Updating a producer's durable with False
        """
        resp = self.producer_behaviors.create_producer_from_cfg()
        producer_id = resp['producer_id']
        self.assertIsNotNone(producer_id)
        self.assertEqual(resp['request'].status_code, 201)

        pattern = self.tenant_config.producer_pattern
        name = self.tenant_config.producer_name
        resp = self.producer_client.update_producer(producer_id=producer_id,
                                                    durable=False,
                                                    pattern=pattern,
                                                    name=name)
        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        self.assertFalse(resp.entity.durable)

    @tags(type='positive')
    def test_update_producer_encrypted_w_true(self):
        """
        Updating a producer's encrypted with True
        """
        resp = self.producer_behaviors.create_producer_from_cfg()
        producer_id = resp['producer_id']
        self.assertIsNotNone(producer_id)
        self.assertEqual(resp['request'].status_code, 201)

        pattern = self.tenant_config.producer_pattern
        name = self.tenant_config.producer_name
        resp = self.producer_client.update_producer(producer_id=producer_id,
                                                    encrypted=True,
                                                    pattern=pattern,
                                                    name=name)
        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        self.assertTrue(resp.entity.encrypted)

    @tags(type='positive')
    def test_update_producer_encrypted_w_false(self):
        """
        Updating a producer's encrypted with False
        """
        resp = self.producer_behaviors.create_producer_from_cfg()
        producer_id = resp['producer_id']
        self.assertIsNotNone(producer_id)
        self.assertEqual(resp['request'].status_code, 201)

        pattern = self.tenant_config.producer_pattern
        name = self.tenant_config.producer_name
        resp = self.producer_client.update_producer(producer_id=producer_id,
                                                    encrypted=False,
                                                    pattern=pattern,
                                                    name=name)
        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        self.assertFalse(resp.entity.encrypted)
