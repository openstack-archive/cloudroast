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

import time
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.database.config import DBaaSConfig
from cloudcafe.database.behaviors import DatabaseAPI_Behaviors
from cloudcafe.database.client import DBaaSAPIClient
from cloudcafe.identity.v2_0.tokens_api.client import TokenAPI_Client
from cloudcafe.identity.v2_0.tokens_api.behaviors import TokenAPI_Behaviors
from cloudcafe.identity.v2_0.tokens_api.config import TokenAPI_Config


class DBaaSFixture(BaseTestFixture):
    """
    @summary: Fixture for any DBaaS tests..

    """

    @classmethod
    def setUpClass(cls):
        super(DBaaSFixture, cls).setUpClass()
        cls.dbaas_config = DBaaSConfig()
        cls.behavior = DatabaseAPI_Behaviors()
        cls.stability_mode = cls.dbaas_config.stability_mode
        cls.version_url = cls.dbaas_config.version_url
        cls.graphite_endpoint = cls.dbaas_config.graphite_endpoint
        cls.perf_server = cls.dbaas_config.perf_server
        cls.perf_server_user = cls.dbaas_config.perf_server_user
        cls.perf_server_password = cls.dbaas_config.perf_server_password
        cls.host_url = cls.dbaas_config.host
        cls.tenant_id = cls.dbaas_config.tenant_id
        cls.service_url = '{0}/{1}'.format(cls.dbaas_config.host,
                                           cls.tenant_id)

        identity_config = TokenAPI_Config()
        token_client = TokenAPI_Client(identity_config.endpoint,
                                       identity_config.serialize_format,
                                       identity_config.deserialize_format)
        token_behaviors = TokenAPI_Behaviors(token_client)
        access_data = token_behaviors.get_access_data(
            identity_config.username,
            identity_config.password,
            identity_config.tenant_name)
        dbaas_service = access_data.get_service(identity_config.endpoint)
        cls.auth_url = "{0}/v2.0/tokens".format(identity_config.endpoint)
        #check for role
        rp_admin_user = cls.dbaas_config.rp_admin_user
        creator_user = cls.dbaas_config.creator_user
        observer_user = cls.dbaas_config.observer_user
        mgmt_username = cls.dbaas_config.mgmt_username

        if mgmt_username:
            username = cls.dbaas_config.mgmt_username
            api_key = cls.dbaas_config.mgmt_api_key
            mgmt_tenant_id = cls.dbaas_config.mgmt_tenant_id
            mgmt_auth_url = "{0}/v2.0/tokens".format(
                cls.dbaas_config.mgmt_base_url)
            mgmt_auth_strategy = "keystone"
            mgmt_service_url = "{0}/{1}".format(
                cls.dbaas_config.mgmt_host,
                mgmt_tenant_id)

            cls.mgmt_client = \
                DBaaSAPIClient(username,
                               cls.host_url,
                               api_key,
                               None,
                               mgmt_tenant_id,
                               auth_url=mgmt_auth_url,
                               service_url=mgmt_service_url,
                               auth_strategy=mgmt_auth_strategy,
                               insecure=True,
                               serialize_format=
                               identity_config.serialize_format,
                               deserialize_format=
                               identity_config.deserialize_format)

        if creator_user:
            username = cls.dbaas_config.creator_user
            api_key = cls.dbaas_config.creator_pw
            cls.creator_client = \
                DBaaSAPIClient(username,
                               cls.host_url,
                               api_key,
                               None,
                               cls.tenant_id,
                               auth_url=cls.auth_url,
                               service_url=cls.service_url,
                               auth_strategy="keystone",
                               insecure=True,
                               serialize_format=
                               identity_config.serialize_format,
                               deserialize_format=
                               identity_config.deserialize_format)

        if rp_admin_user:
            username = cls.dbaas_config.rp_admin_user
            api_key = cls.dbaas_config.rp_admin_pw
            cls.admin_client = \
                DBaaSAPIClient(username,
                               cls.host_url,
                               api_key,
                               None,
                               cls.tenant_id,
                               auth_url=cls.auth_url,
                               service_url=cls.service_url,
                               auth_strategy="keystone",
                               insecure=True,
                               serialize_format=
                               identity_config.serialize_format,
                               deserialize_format=
                               identity_config.deserialize_format)

        if observer_user:
            username = cls.dbaas_config.observer_user
            api_key = cls.dbaas_config.observer_pw
            cls.observer_client = \
                DBaaSAPIClient(username,
                               cls.host_url,
                               api_key,
                               None,
                               cls.tenant_id,
                               auth_url=cls.auth_url,
                               service_url=cls.service_url,
                               auth_strategy="keystone",
                               insecure=True,
                               serialize_format=
                               identity_config.serialize_format,
                               deserialize_format=
                               identity_config.deserialize_format)

        #default
        username = identity_config.username
        api_key = identity_config.password
        cls.client = \
            DBaaSAPIClient(username,
                           cls.host_url,
                           api_key,
                           None,
                           cls.tenant_id,
                           auth_url=cls.auth_url,
                           service_url=cls.service_url,
                           auth_strategy="keystone",
                           insecure=True,
                           serialize_format=
                           identity_config.serialize_format,
                           deserialize_format=
                           identity_config.deserialize_format)

    @classmethod
    def tearDownClass(cls):
        super(DBaaSFixture, cls).tearDownClass()

    def setUp(self):
        super(DBaaSFixture, self).setUp()

    def tearDown(self):
        super(DBaaSFixture, self).tearDown()

    class Role():
        admin = "cdb:admin"
        creator = "cdb:creator"
        observer = "cdb:observer"
