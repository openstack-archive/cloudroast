"""
Copyright 2014 Rackspace

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
from cloudcafe.cloudkeep.cli.clients import SecretsCLIClient, OrdersCLIClient
from cloudcafe.cloudkeep.cli.behaviors import (
    SecretsCLIBehaviors, OrdersCLIBehaviors)
from cloudroast.cloudkeep.barbican.fixtures import BarbicanFixture


class BarbicanCLIFixture(BarbicanFixture):
    CLIENT_TYPE = None
    BEHAVIOR_TYPE = None

    @classmethod
    def setUpFixture(cls, client_type, behavior_type):
        cls.client = client_type(
            url=cls.cloudkeep.base_url,
            api_version=cls.cloudkeep.api_version,
            auth_endpoint=cls.keystone.authentication_endpoint,
            username=cls.keystone.username,
            password=cls.keystone.password,
            tenant_id=cls.keystone.tenant_name)
        cls.behavior = behavior_type(client=cls.client, config=cls.cloudkeep)

    @classmethod
    def setUpClass(cls, keystone_config=None):
        super(BarbicanCLIFixture, cls).setUpClass(keystone_config)
        cls.setUpFixture(cls.CLIENT_TYPE, cls.BEHAVIOR_TYPE)

    def tearDown(self):
        self.behavior._delete_all_created_entities()
        super(BarbicanCLIFixture, self).tearDown()


class SecretsCLIFixture(BarbicanCLIFixture):
    CLIENT_TYPE = SecretsCLIClient
    BEHAVIOR_TYPE = SecretsCLIBehaviors


class OrdersCLIFixture(BarbicanCLIFixture):
    CLIENT_TYPE = OrdersCLIClient
    BEHAVIOR_TYPE = OrdersCLIBehaviors
