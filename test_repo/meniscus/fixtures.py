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
from cloudcafe.meniscus.version_api.client import VersionClient
from cloudcafe.meniscus.tenant_api.client import \
    TenantClient, ProducerClient, ProfileClient, HostClient
from cloudcafe.meniscus.config import \
    MarshallingConfig, MeniscusConfig, TenantConfig
from cloudcafe.meniscus.tenant_api.behaviors \
    import TenantBehaviors, ProducerBehaviors, ProfileBehaviors, HostBehaviors


class MeniscusFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(MeniscusFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.meniscus_config = MeniscusConfig()


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
                                               cls.tenant_config)


class ProducerFixture(TenantFixture):

    @classmethod
    def setUpClass(cls):
        super(ProducerFixture, cls).setUpClass()

        cls.tenant_id, resp = cls.tenant_behaviors.create_tenant()
        cls.producer_client = ProducerClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            tenant_id=cls.tenant_id,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.producer_behaviors = ProducerBehaviors(
            tenant_client=cls.tenant_client,
            producer_client=cls.producer_client,
            tenant_config=cls.tenant_config)

    def tearDown(self):
        for producer_id in self.producer_behaviors.producers_created:
            self.producer_behaviors.delete_producer(producer_id, False)


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
