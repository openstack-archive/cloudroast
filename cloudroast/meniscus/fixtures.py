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
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.meniscus.common.cleanup_client import MeniscusDbClient
from cloudcafe.meniscus.version_api.client import VersionClient
from cloudcafe.meniscus.tenant_api.client import TenantClient, ProducerClient
from cloudcafe.meniscus.config import \
    MarshallingConfig, MeniscusConfig, TenantConfig, PairingConfig,\
    CorrelationConfig
from cloudcafe.meniscus.tenant_api.behaviors import (TenantBehaviors,
                                                     ProducerBehaviors)
from cloudcafe.meniscus.coordinator_api.client import PairingClient
from cloudcafe.meniscus.coordinator_api.behaviors import PairingBehaviors
from cloudcafe.meniscus.correlator_api.client import PublishingClient
from cloudcafe.meniscus.correlator_api.behaviors import PublishingBehaviors
from cloudcafe.meniscus.status_api.client import WorkerStatusClient
from cloudcafe.meniscus.status_api.behaviors import StatusAPIBehaviors


class MeniscusFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(MeniscusFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.meniscus_config = MeniscusConfig()
        cls.cleanup_client = MeniscusDbClient(cls.meniscus_config.db_host,
                                              cls.meniscus_config.db_name,
                                              cls.meniscus_config.db_username,
                                              cls.meniscus_config.db_password)


class VersionFixture(MeniscusFixture):

    @classmethod
    def setUpClass(cls):
        super(VersionFixture, cls).setUpClass()
        cls.client = VersionClient(
            url=cls.meniscus_config.base_url,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)


class TenantFixture(MeniscusFixture):

    @classmethod
    def setUpClass(cls):
        super(TenantFixture, cls).setUpClass()
        cls.tenant_config = TenantConfig()
        cls.tenant_client = TenantClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.tenant_behaviors = TenantBehaviors(cls.tenant_client,
                                               cls.cleanup_client,
                                               cls.tenant_config)

    @classmethod
    def tearDownClass(cls):
        cls.tenant_behaviors.remove_created_tenants()
        super(TenantFixture, cls).tearDownClass()


class ProducerFixture(TenantFixture):

    @classmethod
    def setUpClass(cls):
        super(ProducerFixture, cls).setUpClass()

        cls.tenant_id, resp = cls.tenant_behaviors.create_tenant()
        cls.producer_client = ProducerClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            tenant_id=cls.tenant_id,
            use_alternate=False,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.producer_behaviors = ProducerBehaviors(
            tenant_client=cls.tenant_client,
            producer_client=cls.producer_client,
            db_client=cls.cleanup_client,
            tenant_config=cls.tenant_config)

    def tearDown(self):
        for producer_id in self.producer_behaviors.producers_created:
            self.producer_behaviors.delete_producer(producer_id, False)
        self.producer_behaviors.producers_created = []
        super(ProducerFixture, self).tearDown()


class PairingFixture(TenantFixture):

    @classmethod
    def setUpClass(cls):
        super(PairingFixture, cls).setUpClass()
        cls.pairing_config = PairingConfig()
        cls.pairing_client = PairingClient(
            url=cls.pairing_config.coordinator_base_url,
            api_version=cls.meniscus_config.api_version,
            auth_token=cls.pairing_config.api_secret,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.pairing_behaviors = PairingBehaviors(cls.pairing_client,
                                                 cls.cleanup_client,
                                                 cls.pairing_config)

    def tearDown(self):
        self.pairing_behaviors.remove_created_workers()
        super(PairingFixture, self).tearDown()


class StatusFixture(PairingFixture):

    @classmethod
    def setUpClass(cls):
        super(StatusFixture, cls).setUpClass()
        cls.status_client = WorkerStatusClient(
            url=cls.pairing_config.coordinator_base_url,
            api_version=cls.meniscus_config.api_version,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.status_behaviors = StatusAPIBehaviors(
            status_client=cls.status_client,
            pairing_config=cls.pairing_config)


class PublishingFixture(ProducerFixture):

    @classmethod
    def setUpClass(cls):
        super(PublishingFixture, cls).setUpClass()
        cls.correlate_config = CorrelationConfig()
        cls.publish_client = PublishingClient(
            url=cls.correlate_config.correlator_base_url,
            api_version=cls.meniscus_config.api_version,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.publish_behaviors = PublishingBehaviors(
            publish_client=cls.publish_client,
            correlation_config=cls.correlate_config)

    def setUp(self):
        super(PublishingFixture, self).setUp()

        # We always need the tenant token from the created tenant
        resp = self.tenant_client.get_tenant(self.tenant_id)
        self.assertEqual(resp.status_code, 200)
        self.tenant_token = str(resp.entity[0].token.valid)

        # Force setting id and token on the behavior
        self.publish_behaviors.tenant_id = self.tenant_id
        self.publish_behaviors.tenant_token = self.tenant_token
