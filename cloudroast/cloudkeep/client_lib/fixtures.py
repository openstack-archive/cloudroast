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
from cloudroast.cloudkeep.barbican.fixtures import AuthenticationFixture
from cloudcafe.cloudkeep.barbican.version.client import VersionClient
from cloudcafe.cloudkeep.barbican.secrets.client import SecretsClient
from cloudcafe.cloudkeep.barbican.orders.client import OrdersClient
from cloudcafe.cloudkeep.barbican.secrets.behaviors import SecretsBehaviors
from cloudcafe.cloudkeep.barbican.orders.behaviors import OrdersBehavior
from cloudcafe.cloudkeep.config import CloudKeepAuthConfig
from cloudcafe.cloudkeep.client_lib.secrets.clients import \
    ClientLibSecretsClient
from cloudcafe.cloudkeep.client_lib.secrets.behaviors import \
    ClientLibSecretsBehaviors
from cloudcafe.cloudkeep.client_lib.orders.clients import \
    ClientLibOrdersClient
from cloudcafe.cloudkeep.client_lib.orders.behaviors import \
    ClientLibOrdersBehaviors
from cloudcafe.cloudkeep.config import (CloudKeepSecretsConfig,
                                        CloudKeepOrdersConfig)


class VersionFixture(AuthenticationFixture):

    @classmethod
    def setUpClass(cls):
        super(VersionFixture, cls).setUpClass()
        cls.client = VersionClient(
            url=cls.cloudkeep.base_url,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)


class SecretsFixture(AuthenticationFixture):

    @classmethod
    def setUpClass(cls):
        super(SecretsFixture, cls).setUpClass()
        cls.config = CloudKeepSecretsConfig()
        cls.identity_config = CloudKeepAuthConfig()
        auth_endpoint = '{0}/v2.0'.format(
            cls.identity_config.authentication_endpoint)

        cls.cl_client = ClientLibSecretsClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            auth_endpoint=auth_endpoint,
            user=cls.identity_config.username,
            password=cls.identity_config.password,
            tenant_name=cls.identity_config.tenant_name)

        cls.barb_client = SecretsClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)

        cls.barb_behaviors = SecretsBehaviors(
            client=cls.barb_client, config=cls.config)
        cls.cl_behaviors = ClientLibSecretsBehaviors(
            barb_client=cls.barb_client, cl_client=cls.cl_client,
            config=cls.config)

    def tearDown(self):
        self.cl_behaviors.delete_all_created_secrets()
        self.barb_behaviors.delete_all_created_secrets()
        super(SecretsFixture, self).tearDown()


class SecretsPagingFixture(SecretsFixture):

    @classmethod
    def setUpClass(cls):
        super(SecretsPagingFixture, cls).setUpClass()
        for count in range(20):
            cls.barb_behaviors.create_secret_from_config(use_expiration=False)

    def tearDown(self):
        """ Overrides superclass method so that secrets are not deleted
        between tests.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls.cl_behaviors.delete_all_created_secrets()
        cls.barb_behaviors.delete_all_created_secrets()
        super(SecretsPagingFixture, cls).tearDownClass()


class OrdersFixture(AuthenticationFixture):
    @classmethod
    def setUpClass(cls):
        super(OrdersFixture, cls).setUpClass()
        cls.config = CloudKeepOrdersConfig()
        cls.identity_config = CloudKeepAuthConfig()
        auth_endpoint = '{0}/v2.0'.format(
            cls.identity_config.authentication_endpoint)

        cls.cl_client = ClientLibOrdersClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.cloudkeep.tenant_id,
            auth_endpoint=auth_endpoint,
            user=cls.identity_config.username,
            password=cls.identity_config.password,
            tenant_name=cls.identity_config.tenant_name)

        cls.barb_client = OrdersClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)
        cls.secrets_client = SecretsClient(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            tenant_id=cls.tenant_id,
            token=cls.token,
            serialize_format=cls.marshalling.serializer,
            deserialize_format=cls.marshalling.deserializer)

        cls.barb_behaviors = OrdersBehavior(
            orders_client=cls.barb_client, secrets_client=cls.secrets_client,
            config=cls.config)
        cls.cl_behaviors = ClientLibOrdersBehaviors(
            barb_client=cls.barb_client, secrets_client=cls.secrets_client,
            cl_client=cls.cl_client, config=cls.config)

    def tearDown(self):
        self.cl_behaviors.delete_all_created_orders_and_secrets()
        self.barb_behaviors.delete_all_created_orders_and_secrets()
        super(OrdersFixture, self).tearDown()


class OrdersPagingFixture(OrdersFixture):

    @classmethod
    def setUpClass(cls):
        super(OrdersPagingFixture, cls).setUpClass()
        for count in range(20):
            cls.barb_behaviors.create_order_from_config(use_expiration=False)

    def tearDown(self):
        """ Overrides superclass method so that orders are not deleted
        between tests.
        """
        pass

    @classmethod
    def tearDownClass(cls):
        cls.cl_behaviors.delete_all_created_orders_and_secrets()
        cls.barb_behaviors.delete_all_created_orders_and_secrets()
        super(OrdersPagingFixture, cls).tearDownClass()
