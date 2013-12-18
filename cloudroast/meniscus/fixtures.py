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
from cafe.engine.clients.elasticsearch import BaseElasticSearchClient
from cafe.resources.rsyslog.client import RSyslogClient
from cloudcafe.meniscus.common.cleanup_client import MeniscusDbClient
from cloudcafe.meniscus.version_api.client import VersionClient
from cloudcafe.meniscus.tenant_api.client import TenantClient, ProducerClient
from cloudcafe.meniscus.config import (MarshallingConfig, MeniscusConfig,
                                       TenantConfig, CorrelationConfig,
                                       StorageConfig)
from cloudcafe.meniscus.tenant_api.behaviors import (TenantBehaviors,
                                                     ProducerBehaviors)
from cloudcafe.meniscus.correlator_api.client import PublishingClient
from cloudcafe.meniscus.correlator_api.behaviors import PublishingBehaviors
from cloudcafe.meniscus.status_api.client import WorkerStatusClient


class MeniscusFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(MeniscusFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.meniscus_config = MeniscusConfig()
        cls.storage_config = StorageConfig()
        cls.cleanup_client = MeniscusDbClient(cls.meniscus_config.db_host,
                                              cls.meniscus_config.db_name,
                                              cls.meniscus_config.db_username,
                                              cls.meniscus_config.db_password)

        # ElasticSearch client
        es_servers = [cls.storage_config.address]
        cls.es_client = BaseElasticSearchClient(servers=es_servers)


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
                                               cls.tenant_config,
                                               cls.es_client)

        cls.tenant_id, resp = cls.tenant_behaviors.create_tenant()
        cls.es_client.index = [cls.tenant_id]
        # Connect ElasticSearch Client
        cls.es_client.connect(bulk_size=1)

    @classmethod
    def tearDownClass(cls):
        cls.tenant_behaviors.remove_created_tenants()
        super(TenantFixture, cls).tearDownClass()


class ProducerFixture(TenantFixture):

    @classmethod
    def setUpClass(cls):
        super(ProducerFixture, cls).setUpClass()

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
            tenant_config=cls.tenant_config,
            es_client=cls.es_client)

    def tearDown(self):
        for producer_id in self.producer_behaviors.producers_created:
            self.producer_behaviors.delete_producer(producer_id, False)
        self.producer_behaviors.producers_created = []
        super(ProducerFixture, self).tearDown()


class StatusFixture(VersionFixture):

    @classmethod
    def setUpClass(cls):
        super(StatusFixture, cls).setUpClass()
        cls.status_client = WorkerStatusClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)


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
            correlation_config=cls.correlate_config,
            storage_client=cls.es_client)

    def setUp(self):
        super(PublishingFixture, self).setUp()

        # We always need the tenant token from the created tenant
        resp = self.tenant_client.get_tenant(self.tenant_id)
        self.assertEqual(resp.status_code, 200)
        self.tenant_token = str(resp.entity[0].token.valid)

        # Force setting id and token on the behavior
        self.publish_behaviors.tenant_id = self.tenant_id
        self.publish_behaviors.tenant_token = self.tenant_token


class RSyslogPublishingFixture(PublishingFixture):

    def setUp(self):
        super(RSyslogPublishingFixture, self).setUp()
        syslog_endpoint = self.correlate_config.syslog_endpoint
        tenant_info = {
            'meniscus': {
                'token': self.tenant_token, 'tenant': self.tenant_id
            }
        }

        self.rsyslog_client = RSyslogClient(host=syslog_endpoint,
                                            default_sd=tenant_info)
        self.rsyslog_client.connect()

    def tearDown(self):
        self.rsyslog_client.close()
