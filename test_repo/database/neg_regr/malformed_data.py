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

from test_repo.database.fixtures import DBaaSFixture
from test_repo.database import dbaas_util as testutil


class TestMalformedData(DBaaSFixture):

    instance_id = None
    dbaas = None

    # @classmethod
    # def setUpClass(cls):
    #     """
    #     Creating an instance for database testing
    #
    #     """
    #     super(TestMalformedData, cls).setUpClass()
    #     cls.client_neg_testing = cls.dbaas_provider.client
    #     cls.auth_data = cls.dbaas_provider.auth_provider.authenticate()

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(TestMalformedData, cls).setUpClass()
        cls.client_neg_testing = cls.dbaas_provider.client
        cls.auth_data = cls.dbaas_provider.auth_provider.authenticate()
        cls.dbaas = cls.dbaas_provider.client.reddwarfclient
        NAME = "qe-database-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = cls.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = testutil.get_last_response_code(cls.dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        cls.instance_id = instance.id
        #status = instance.status
        testutil.waitForActive(cls.dbaas, instanceId=cls.instance_id)


    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        #Delete the instance ID created for test if active
        if cls.instance_id is not None:
            status = testutil.getInstanceStatus(cls.dbaas, instanceId=cls.instance_id)
            if testutil.isInstanceActive(cls.dbaas, instanceStatus=status):
                cls.dbaas.instances.get(cls.instance_id).delete()

    def test_bad_instance_data(self):
        try:
            self.dbaas.instances.create("bad_instance", 3, 3, databases="foo", users="bar")
        except Exception as e:
            httpCode = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(httpCode == '400',
                            "Create instance failed with code %s, excpetion %s"
                            % (httpCode, e.message))

    def test_bad_database_data(self):

        _bad_db_data = "{foo}"
        try:
            self.dbaas.databases.create(self.instance_id, _bad_db_data)
        except Exception as e:
            httpCode = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(httpCode == '400',
                            "Create instance failed with code %s, excpetion %s"
                            % (httpCode, e.message))

    def test_bad_user_data(self):

        _user = []
        _user_name = "F343jasdf"
        _user.append({"name12": _user_name,
                      "password12": "password"})
        try:
            self.dbaas.users.create(self.instance_id, _user)
        except Exception as e:
            httpCode = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(httpCode == '400',
                            "Create instance failed with code %s, excpetion %s"
                            % (httpCode, e.message))

    def test_bad_resize_instance_data(self):
        try:
            self.dbaas.instances.resize_instance(self.instance_id, "bad data")
        except Exception as e:
            httpCode = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(httpCode == '400',
                            "Create instance failed with code %s, excpetion %s"
                            % (httpCode, e.message))

    def test_bad_resize_vol_data(self):
        try:
            self.dbaas.instances.resize_volume(self.instance_id, "bad data")
        except Exception as e:
            httpCode = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(httpCode == '400',
                            "Create instance failed with code %s, excpetion %s"
                            % (httpCode, e.message))

    def test_bad_body_instance_create_no_data(self):
        auth_token = self.auth_data.token.id
        #do a crazy instance request to the server
        headers = {'X-Auth-Token': auth_token,
                   'Content-Type': 'application/json'}
        tenant_id = self.config.dbaas.tenant_id
        url = self.config.dbaas.host
        create_url = '%s/%s/instances' % (url, tenant_id)

        response = self.client_neg_testing.request('POST',
                                                   create_url,
                                                   headers=headers)
        self.assertEqual(response.status_code,
                         400,
                         "\nExpected http code %s, Actual http code %s \nREASON: %s"
                         % (400, response.status_code, response.reason))

    def test_bad_body_instance_create_bad_data(self):
        auth_token = self.auth_data.token.id
        #do a crazy instance request to the server
        headers = {'X-Auth-Token': auth_token,
                   'Content-Type': 'application/json'}
        tenant_id = self.config.dbaas.tenant_id
        url = self.config.dbaas.host
        create_url = '%s/%s/instances' % (url, tenant_id)

        response = self.client_neg_testing.request('POST',
                                                   create_url,
                                                   headers=headers,
                                                   data="bogus")
        self.assertEqual(response.status_code,
                         400,
                         "\nExpected http code %s, Actual http code %s \nREASON: %s"
                         % (400, response.status_code, response.reason))



