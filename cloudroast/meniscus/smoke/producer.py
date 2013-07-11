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
from cloudroast.meniscus.fixtures import ProducerFixture
from cloudcafe.compute.common.datagen import random_string


class TestProducer(ProducerFixture):

    def test_create_producer(self):
        result = self.producer_behaviors.create_producer()
        self.assertEqual(result['request'].status_code, 201)

    def test_delete_producer(self):
        result = self.producer_behaviors.create_producer()
        self.assertEqual(result['request'].status_code, 201)

        resp = self.producer_behaviors.delete_producer(result['producer_id'])
        self.assertEqual(resp.status_code, 200, 'Wrong status code on delete')

    def test_get_producer(self):
        result = self.producer_behaviors.create_producer()
        original_id = result['producer_id']

        resp = self.producer_client.get_producer(original_id)
        producer = resp.entity

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(producer.id, original_id)

    def test_get_all_producers(self):
        result = self.producer_behaviors.create_producer()
        id_1 = result['producer_id']
        result = self.producer_behaviors.create_producer(name=random_string())
        id_2 = result['producer_id']

        resp = self.producer_client.get_all_producers()
        producers = resp.entity

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(producers), 2)
        self.assertIn(True, [producer.id == id_1 for producer in producers])
        self.assertIn(True, [producer.id == id_2 for producer in producers])

    def test_update_producer(self):
        result = self.producer_behaviors.create_producer()
        producer_id = result['producer_id']

        update_name = random_string()
        resp = self.producer_client.update_producer(
            producer_id=producer_id,
            name=update_name)

        self.assertEqual(resp.status_code, 200)

        resp = self.producer_client.get_producer(producer_id)
        producer = resp.entity

        self.assertEqual(producer.name, update_name)
