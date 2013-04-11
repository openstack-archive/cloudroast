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

        #Add configs here...update ccengine/domain/configuration.py to get these configs
        cls.stability_mode = cls.dbaas_config.stability_mode
        cls.version_url = cls.dbaas_config.version_url
        cls.graphite_endpoint = cls.dbaas_config.graphite_endpoint
        cls.perf_server = cls.dbaas_config.perf_server
        cls.perf_server_user = cls.dbaas_config.perf_server_user
        cls.perf_server_password = cls.dbaas_config.perf_server_password
        cls.host_url = cls.dbaas_config.host
        cls.tenant_id = cls.dbaas_config.tenant_id
        cls.service_url = cls.dbaas_config.host + "/" + cls.tenant_id

        identity_config = TokenAPI_Config()
        token_client = TokenAPI_Client(identity_config.endpoint,
                                       'json', 'json')
        token_behaviors = TokenAPI_Behaviors(token_client)
        access_data = token_behaviors.get_access_data(identity_config.username,
                                                      identity_config.password,
                                                      identity_config.tenant_name)
        dbaas_service = access_data.get_service(identity_config.endpoint)
        cls.auth_url = identity_config.endpoint + "/v2.0/tokens"
        #check for role
        rp_admin_user = cls.dbaas_config.rp_admin_user
        creator_user = cls.dbaas_config.creator_user
        observer_user = cls.dbaas_config.observer_user
        mgmt_username = cls.dbaas_config.mgmt_username

        #TODO: Need to fix this...
        #ah_dict = {EngineConfig.SECTION_NAME: {'serializer': 'xml', 'deserializer': 'xml'}}
        #ah_config = cls.dbaas_config.mcp_override(ah_dict)

        #dbaas_atom_hopper_url = ah_config.compute_api.atom_hopper_url + '/database/events'
        # if cls.dbaas_config.atom_hopper_url is not None:
        #     dbaas_atom_hopper_url = cls.dbaas_config.atom_hopper_url + '/database/events'
        #     cls.dbaas_atomhopper_provider = AtomHopperProvider(dbaas_atom_hopper_url, ah_config)

        if mgmt_username:
            username = cls.dbaas_config.mgmt_username
            api_key = cls.dbaas_config.mgmt_api_key
            mgmt_tenant_id = cls.dbaas_config.mgmt_tenant_id
            mgmt_auth_url = cls.dbaas_config.mgmt_base_url + "/v2.0/tokens"
            mgmt_auth_strategy = "keystone"
            mgmt_service_url = cls.dbaas_config.mgmt_host + "/" + mgmt_tenant_id
            cls.mgmt_client = DBaaSAPIClient(username,
                                             cls.host_url,
                                             api_key,
                                             None,
                                             mgmt_tenant_id,
                                             auth_url=mgmt_auth_url,
                                             service_url=mgmt_service_url,
                                             auth_strategy=mgmt_auth_strategy,
                                             insecure=True,
                                             serialize_format=identity_config.serialize_format,
                                             deserialize_format=identity_config.deserialize_format)

        if creator_user:
            username = cls.dbaas_config.creator_user
            api_key = cls.dbaas_config.creator_pw
            cls.creator_client = DBaaSAPIClient(username,
                                                cls.host_url,
                                                api_key,
                                                None,
                                                cls.tenant_id,
                                                auth_url=cls.auth_url,
                                                service_url=cls.service_url,
                                                auth_strategy="keystone",
                                                insecure=True,
                                                serialize_format=identity_config.serialize_format,
                                                deserialize_format=identity_config.deserialize_format)

        if rp_admin_user:
            username = cls.dbaas_config.rp_admin_user
            api_key = cls.dbaas_config.rp_admin_pw
            cls.admin_client = DBaaSAPIClient(username,
                                              cls.host_url,
                                              api_key,
                                              None,
                                              cls.tenant_id,
                                              auth_url=cls.auth_url,
                                              service_url=cls.service_url,
                                              auth_strategy="keystone",
                                              insecure=True,
                                              serialize_format=identity_config.serialize_format,
                                              deserialize_format=identity_config.deserialize_format)

        if observer_user:
            username = cls.dbaas_config.observer_user
            api_key = cls.dbaas_config.observer_pw
            cls.observer_client = DBaaSAPIClient(username,
                                                 cls.host_url,
                                                 api_key,
                                                 None,
                                                 cls.tenant_id,
                                                 auth_url=cls.auth_url,
                                                 service_url=cls.service_url,
                                                 auth_strategy="keystone",
                                                 insecure=True,
                                                 serialize_format=identity_config.serialize_format,
                                                 deserialize_format=identity_config.deserialize_format)

        #default
        username = identity_config.username
        api_key = identity_config.password
        cls.client = DBaaSAPIClient(username,
                                    cls.host_url,
                                    api_key,
                                    None,
                                    cls.tenant_id,
                                    auth_url=cls.auth_url,
                                    service_url=cls.service_url,
                                    auth_strategy="keystone",
                                    insecure=True,
                                    serialize_format=identity_config.serialize_format,
                                    deserialize_format=identity_config.deserialize_format)

    @classmethod
    def tearDownClass(cls):
        super(DBaaSFixture, cls).tearDownClass()

    def setUp(self):
        super(DBaaSFixture, self).setUp()

    def tearDown(self):
        super(DBaaSFixture, self).tearDown()

    def get_last_response_code(self):
        resp, body = self.dbaas.client.last_response
        return str(resp.status)

    def getInstanceStatus(self, instanceId=None):
        _instance = self.dbaas.instances.get(instanceId)
        return _instance.status

    def isInstanceActive(self, instanceStatus=None, instanceId=None):
        if instanceStatus is not None:
            return instanceStatus == 'ACTIVE'
        if instanceId is not None:
            return self.getInstanceStatus(instanceId) == 'ACTIVE'
        return False

    def get_all_instances(self):
        return self.dbaas.instances.list()

    def get_active_instance(self):
        """
        return the instance if it already exists, or find and return an active
        one , or create one for use here
        """
        if self.instance is not None:
            if self.getInstanceStatus(self.instance.id) is "ACTIVE":
                return self.instance
        else:
            instances = self.get_all_instances()
            for instance in instances:
                if instance.status == "ACTIVE":
                    return instance
                    # No active instances returned, so go make one
        instance = self.create_active_instance(name="qe-get-active-instance",
                                               flavor_id=1,
                                               volume={"size": 1})
        return instance

    def create_active_instance(self, name, flavor_id, volume, databases=None,
                               users=None):
        """ Create an instance and make sure it becomes Active """
        # create instance
        self.instance = self.dbaas.instances.create(name, flavor_id,
                                                    volume, databases,
                                                    users)
        # Public API - verify response for create instance
        self.assertEqual(str(self.get_last_response_code()), "200",
                         "Error: unexpected resp code for create instance")
        self.assertEqual(self.instance.flavor["id"], str(flavor_id),
                         "Error: incorrect flavor id")
        self.assertEqual(self.instance.name, name,
                         "Error: incorrect instance name")
        self.assertEqual(self.instance.status, "BUILD",
                         "Error: instance is not in BUILD")
        self.assertEqual(self.instance.volume["size"], volume["size"],
                         "Error: incorrect volume size")

        # wait for instance to become Active
        self.wait_for_active(self.instance.id)
        time.sleep(5)

        # Public API - verify response for list instance
        instance_details = self.dbaas.instances.get(self.instance)
        self.assertEqual(str(self.get_last_response_code()), "200",
                         "Error: unexpected resp code for list instance")
        self.assertEqual(instance_details.flavor["id"], str(flavor_id),
                         "Error: incorrect flavor id")
        self.assertEqual(instance_details.name, name,
                         "Error: incorrect instance name")
        self.assertEqual(instance_details.status, "ACTIVE",
                         "Error: instance is not Active")
        self.assertEqual(instance_details.volume["size"], volume["size"],
                         "Error: incorrect volume size")
        return self.instance

    def delete_instance(self, instanceId):
        self.dbaas.instances.delete(instanceId)
        delete_response = self.dbaas.instances.get(instanceId)
        print delete_response

    def _user_list_from_names(self, usernames):
        return [{"name": name,
                 "password": "password",
                 "databases": []} for name in usernames]

    def _test_access(self, users, databases, expected_response="200"):
        """ Verify that each user in the list has access to each database in
            the list."""
        for user in users:
            access = None
            try:
                access = self.reddwarf_client.users.list_access(self.instance.id, user)
                print access
                self.assertEqual(200, self.reddwarf_client.last_http_code,
                                 "Expected: %r does not match actual: %r " %
                                 (200, self.reddwarf_client.last_http_code))
            except self.failureException:
                self.assertEqual(404, self.reddwarf_client.last_http_code)
            finally:
                self.assertEqual(expected_response, self.get_last_response_code(),
                                 "Expected: %r does not match actual: %r " %
                                 (expected_response, self.get_last_response_code()))
            if access is not None:
                access = [db.name for db in access]
                self.assertEqual(set(access), set(databases))

    def _reset_access(self):
        for user in self.users:
            for database in self.databases + self.ghostdbs:
                try:
                    self.reddwarf_client.users.revoke(self.instance.id, user, database)
                    self.assertTrue(self.get_last_response_code() in [202, 404])
                except self.failureException:
                    # This is all right here, since we're resetting.
                    pass
        self._test_access(self.users, [])

    class Role():
        admin = "cdb:admin"
        creator = "cdb:creator"
        observer = "cdb:observer"