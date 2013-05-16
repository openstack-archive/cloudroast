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
from cloudcafe.meniscus.tenant_api.client import \
    TenantClient, ProducerClient, ProfileClient, HostClient
from cloudcafe.meniscus.config import \
    MarshallingConfig, MeniscusConfig, TenantConfig, PairingConfig,\
    CorrelationConfig
from cloudcafe.meniscus.tenant_api.behaviors \
    import TenantBehaviors, ProducerBehaviors, ProfileBehaviors, HostBehaviors
from cloudcafe.meniscus.coordinator_api.client import PairingClient
from cloudcafe.meniscus.coordinator_api.behaviors import PairingBehaviors
from cloudcafe.meniscus.correlator_api.client import PublishingClient
from cloudcafe.meniscus.correlator_api.behaviors import PublishingBehaviors
from cloudcafe.meniscus.status_api.client import WorkerStatusClient


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
        super(ProducerFixture, self).tearDown()


class ProfileFixture(ProducerFixture):

    @classmethod
    def setUpClass(cls):
        super(ProfileFixture, cls).setUpClass()

        cls.profile_client = ProfileClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            tenant_id=cls.tenant_id,
            producer_id=None,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.profile_behaviors = ProfileBehaviors(
            tenant_client=cls.tenant_client,
            producer_client=cls.producer_client,
            profile_client=cls.profile_client,
            db_client=cls.cleanup_client,
            tenant_config=cls.tenant_config)

    def setUp(self):
        super(ProfileFixture, self).setUp()
        resp = self.producer_behaviors.create_producer()
        self.producer_id = resp['producer_id']
        self.profile_client.producer_id = self.producer_id

    def tearDown(self):
        for profile_id in self.profile_behaviors.profiles_created:
            self.profile_behaviors.delete_profile(profile_id, False)

        super(ProfileFixture, self).tearDown()


class HostFixture(ProfileFixture):

    @classmethod
    def setUpClass(cls):
        super(HostFixture, cls).setUpClass()

        cls.host_client = HostClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            tenant_id=cls.tenant_id,
            profile_id=None,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.host_behaviors = HostBehaviors(
            tenant_client=cls.tenant_client,
            producer_client=cls.producer_client,
            profile_client=cls.profile_client,
            host_client=cls.host_client,
            db_client=cls.cleanup_client,
            tenant_config=cls.tenant_config)

    def setUp(self):
        super(HostFixture, self).setUp()

        resp = self.profile_behaviors.create_new_profile(
            producer_ids=[self.producer_id])
        self.profile_id = resp['profile_id']
        self.host_client.profile_id = self.profile_id

    def tearDown(self):
        for host_id in self.host_behaviors.hosts_created:
            self.host_behaviors.delete_host(host_id, False)

        super(HostFixture, self).tearDown()


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


class PublishingFixture(PairingFixture):

    @classmethod
    def setUpClass(cls):
        super(PublishingFixture, cls).setUpClass()
        cls.correlate_config = CorrelationConfig()
        cls.publish_client = PublishingClient(
            url='http://192.168.1.3:8080',
            api_version=cls.meniscus_config.api_version,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.publish_behaviors = PublishingBehaviors(
            publish_client=cls.publish_client,
            correlation_config=cls.correlate_config)

    def setUp(self):
        super(PublishingFixture, self).setUp()
        # We always need to tenant location to publish to
        self.tenant_id, resp = self.tenant_behaviors.create_tenant()
        self.assertEqual(resp.status_code, 201)

        # We also always need the tenant token from the created tenant
        resp = self.tenant_client.get_tenant(self.tenant_id)
        self.assertEqual(resp.status_code, 200)
        self.tenant_token = str(resp.entity[0].token.valid)
