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
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.designate.config import DesignateConfig
from cloudcafe.designate.config import MarshallingConfig
from cloudcafe.designate.v1.domain_api.client import DomainAPIClient
from cloudcafe.designate.v1.server_api.client import ServerAPIClient
from cloudcafe.designate.behaviors import DomainBehaviors
from cloudcafe.designate.behaviors import ServerBehaviors


class DesignateFixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        super(DesignateFixture, cls).setUpClass()
        cls.designate_config = DesignateConfig()
        cls.marshalling = MarshallingConfig()

        v1_client_args = [cls.designate_config.url_v1,
                          cls.marshalling.serializer,
                          cls.marshalling.deserializer]

        cls.domain_client = DomainAPIClient(*v1_client_args)
        cls.server_client = ServerAPIClient(*v1_client_args)

        cls.domain_behaviors = DomainBehaviors(cls.domain_client)
        cls.server_behaviors = ServerBehaviors(cls.server_client)

        # ensure at least one server exists; else, server delete tests will
        # fail since the api prevents us from deleting the last remaining
        # server. And no domains can be created without at least one server.
        cls.server_behaviors.create_server()


class DomainsFixture(DesignateFixture):

    def tearDown(self):
        self.domain_behaviors.delete_created_domains()
        self.server_behaviors.delete_created_servers()
        super(DomainsFixture, self).tearDown()


class ServersFixture(DesignateFixture):

    def tearDown(self):
        self.server_behaviors.delete_created_servers()
        super(ServersFixture, self).tearDown()
