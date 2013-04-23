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
from os import path
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.meniscus.version_api.client import VersionClient
from cloudcafe.meniscus.tenant_api.client import \
    TenantClient, ProducerClient, ProfileClient, HostClient
from cloudcafe.meniscus.config import \
    MarshallingConfig, MeniscusConfig, TenantConfig
from cloudcafe.compute.common.datagen import random_int


class MeniscusFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(MeniscusFixture, cls).setUpClass()
        cls.marshalling = MarshallingConfig()
        cls.meniscus_config = MeniscusConfig()

    def get_id(self, request):
        """
        Helper function to extract the producer id from location header
        """
        self.assertEqual(request.status_code, 201, 'Invalid response code')
        location = request.headers.get('location')
        extracted_id = int(path.split(location)[1])
        return extracted_id


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

    @classmethod
    def _create_tenant(cls):
        """
        Helper function for creating a tenant on a fixture
        @param cls:
        @return: Returns tuple with tenant_id and response object
        """
        tenant_id = random_int(1, 100000)
        resp = cls.tenant_client.create_tenant(tenant_id)
        return str(tenant_id), resp


class ProducerFixture(TenantFixture):

    @classmethod
    def setUpClass(cls):
        super(ProducerFixture, cls).setUpClass()

        cls.tenant_id, resp = cls._create_tenant()
        cls.producer_client = ProducerClient(
            url=cls.meniscus_config.base_url,
            api_version=cls.meniscus_config.api_version,
            tenant_id=cls.tenant_id,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)

    def setUp(self):
        self.producers_created = []

    def tearDown(self):
        for producer_id in self.producers_created:
            self._delete_producer(producer_id, False)

        self.producers_created = []

    def _create_producer(self, name=None, pattern=None, durable=None,
                         encrypted=None):
        """
        @summary: Helper function to create a producer for fixtures. All
        parameters set to None will be loaded from configuration file.
        @return: Dictionary with request object, and producer id
        """
        if name is None:
            name = self.tenant_config.producer_name
        if pattern is None:
            pattern = self.tenant_config.producer_pattern
        if durable is None:
            durable = self.tenant_config.producer_durable
        if encrypted is None:
            encrypted = self.tenant_config.producer_encrypted

        req = self.producer_client.create_producer(
            name=name, pattern=pattern, durable=durable, encrypted=encrypted)

        producer_id = self.get_id(req)

        self.producers_created.append(producer_id)

        return {
            'request': req,
            'producer_id': producer_id
        }

    def _delete_producer(self, producer_id, remove_from_array=True):
        response = self.producer_client.delete_producer(producer_id)
        self.assertEqual(200, response.status_code,
                         'Delete response code should have returned 200 OK.')

        if remove_from_array:
            self.producers_created.remove(producer_id)

        return response


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

    def setUp(self):
        super(ProfileFixture, self).setUp()
        self.producer_id = self._create_producer()['producer_id']
        self.profile_client.producer_id = self.producer_id

        self.profiles_created = []

    def tearDown(self):
        for profile_id in self.profiles_created:
            self._delete_profile(profile_id, False)

        self.profiles_created = []

        super(ProfileFixture, self).tearDown()

    def _create_new_profile(self, name=None, producer_ids=None):

        if name is None:
            name = self.tenant_config.profile_name
        if producer_ids is None:
            producer_ids = [self.producer_id]

        profile_req = self.profile_client.create_profile(
            name=name, producer_ids=producer_ids)
        profile_id = self.get_id(profile_req)

        self.assertEquals(201, profile_req.status_code,
                          'expected 201 Created Response Code')
        self.assertGreater(profile_id, 0, "Invalid profile ID")

        self.profiles_created.append(profile_id)

        return {
            'request': profile_req,
            'profile_id': profile_id
        }

    def _delete_profile(self, profile_id, remove_from_array=True):
        response = self.profile_client.delete_profile(profile_id)
        self.assertEqual(200, response.status_code,
                         'Delete response code should have returned 200 OK.')

        if remove_from_array:
            self.profiles_created.remove(profile_id)

        return response


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

    def setUp(self):
        super(HostFixture, self).setUp()

        self.profile_id = self._create_new_profile()['profile_id']
        self.host_client.profile_id = self.profile_id

        self.hosts_created = []

    def tearDown(self):
        for host_id in self.hosts_created:
            self._delete_host(host_id, False)

        self.hosts_created = []

        super(HostFixture, self).tearDown()

    def _delete_host(self, host_id, remove_from_array=True):
        response = self.host_client.delete_host(host_id)
        self.assertEqual(response.status_code, 200,
                         'Delete response code should have returned 200 OK.')

        if remove_from_array:
            self.hosts_created.remove(host_id)

        return response

    def _create_new_host(self, hostname=None, ip_v4=None, ip_v6=None,
                         profile_id=None):

        if hostname is None:
            hostname = self.tenant_config.hostname

        host_req = self.host_client.create_host(hostname=hostname,
                                                ip_v4=ip_v4,
                                                ip_v6=ip_v6,
                                                profile_id=profile_id)
        self.assertEqual(host_req.status_code, 201,
                         'Status code should have been 201 Created. ')

        host_id = self.get_id(host_req)
        self.assertGreater(host_id, 0, "Invalid producer ID")

        self.hosts_created.append(host_id)

        return {
            'request': host_req,
            'host_id': host_id
        }
