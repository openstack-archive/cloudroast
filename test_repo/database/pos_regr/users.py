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


class test_users(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(test_users, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient
        NAME = "qe-user-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = test_users.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = testutil.get_last_response_code(test_users.dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        test_users.instance_id = instance.id
        testutil.waitForActive(test_users.dbaas, instanceId=test_users.instance_id)

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """

        #Delete the instance ID created for test if active
        if test_users.instance_id is not None:
            status = testutil.getInstanceStatus(test_users.dbaas, instanceId=test_users.instance_id)
            if testutil.isInstanceActive(test_users.dbaas, instanceStatus=status):
                test_users.dbaas.instances.get(test_users.instance_id).delete()

    def test_create_user_req_params(self):
        _user = []
        _user_name = "F343jasdf"
        _user.append({"name": _user_name,
                      "password": "password"})

        self.dbaas.users.create(self.instance_id, _user)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        testutil.waitForActive(self.dbaas, instanceId=self.instance_id)
        self.assertTrue(testutil.getInstanceStatus(self.dbaas, instanceId=self.instance_id) == 'ACTIVE',
                        "Instance is not in Active statue")
        #Get the instance and check instance attribs: such as the flavor / volume size
        #TODO: need to verify this list later...
        _users = self.dbaas.users.list(self.dbaas.instances.get(self.instance_id))
        #try to find our instance in the list
        self.assertTrue(testutil.found_resource(self.dbaas,
                                                instanceId=self.instance_id,
                                                userName=_user_name),
                        "Did not find our user name: %s in the list." % _user_name)

        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(testutil.found_resource(self.dbaas,
                                                 instanceId=self.instance_id,
                                                 userName=_user_name),
                         "Delete error: Found user name: %s in the list." % _user_name)

    def test_create_user_with_multi_db(self):
        _db_name1 = "user_with_multi-database"
        _db_name2 = "user_with_multi-db2"
        _databases = [{"name": _db_name1},
                      {"name": _db_name2}]

        _user = []
        _user_name = "F343jasdf"
        _user.append({"name": _user_name,
                      "password": "password",
                      "databases": _databases})

        self.dbaas.users.create(self.instance_id, _user)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        testutil.waitForActive(self.dbaas, instanceId=self.instance_id)
        self.assertTrue(testutil.getInstanceStatus(self.dbaas,
                                                   instanceId=self.instance_id) == 'ACTIVE',
                        "Instance is not in Active statue")
        #Get the instance and check user dbs
        _users = self.dbaas.users.list(self.dbaas.instances.get(self.instance_id))
        for _user in _users:
            self.assertEqual(_user.databases, _databases)
            #try to find our user in the list
        self.assertTrue(testutil.found_resource(self.dbaas,
                                                instanceId=self.instance_id,
                                                userName=_user_name),
                        "Did not find our user name: %s in the list." % _user_name)
        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(testutil.found_resource(self.dbaas,
                                                 instanceId=self.instance_id,
                                                 userName=_user_name),
                         "Delete error: Found user name: %s in the list." % _user_name)

    def test_create_multi_user_with_multi_db(self):
        _db_name1 = "multi_user_with_multi-database"
        _db_name2 = "multi_user_with_multi-db2"
        _databases = [dict(name=_db_name1),
                      {"name": _db_name2}]

        _test_users = [{"name": "F343jasdf_",
                        "password": "password",
                        "databases": _databases},
                       dict(name="403F23F343jasdf", password="password", databases=_databases),
                       dict(name="easy_user_name", password="password", databases=_databases)]

        self.dbaas.users.create(self.instance_id, _test_users)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

        self.assertTrue(testutil.getInstanceStatus(self.dbaas,
                                                   instanceId=self.instance_id) == 'ACTIVE',
                        "Instance is not in Active statue")
        #Get the instance and check user dbs
        _user_list = self.dbaas.users.list(self.dbaas.instances.get(self.instance_id))
        for _user in _user_list:
            self.assertEqual(_user.databases, _databases)
            #try to find our user in the list
            self.assertTrue(testutil.found_resource(self.dbaas,
                                                    instanceId=self.instance_id,
                                                    userName=_user.name),
                            "Did not find our user name: %s in the list." % _user.name)
            self.dbaas.users.delete(self.instance_id, _user.name)
            self.assertFalse(testutil.found_resource(self.dbaas,
                                                     instanceId=self.instance_id,
                                                     userName=_user.name),
                             "Delete error: Found user name: %s in the list." % _user.name)

    def test_change_user_pw(self):
        """
        Changes the password of a user
        Issue: You cannot verify the new password since that is
        never returned from the server.
        @return:
        """
        _db_name1 = "test_change_user_pw"
        _db_name2 = "test_change_user_pw2"
        _databases = [{"name": _db_name1},
                      {"name": _db_name2}]

        _test_user = []
        _user_name = "F343jasdf1234"
        _test_user.append({"name": _user_name,
                           "password": "password",
                           "databases": _databases})

        self.dbaas.users.create(self.instance_id, _test_user)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

        _test_user[0]['password'] = "newpassword"
        self.dbaas.users.change_passwords(self.instance_id, _test_user)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(testutil.found_resource(self.dbaas,
                                                 instanceId=self.instance_id,
                                                 userName=_user_name),
                         "Delete error: Found user name: %s in the list." % _user_name)

    def test_user_access(self):
        _db_name1 = "test_user_access-database"
        _db_name2 = "test_user_access-db2"
        _databases = [{"name": _db_name1},
                      {"name": _db_name2}]

        _test_users = []
        _user_name = "F343jasdfasdf"
        _test_users.append({"name": _user_name,
                            "password": "password",
                            "databases": _databases})

        self.dbaas.users.create(self.instance_id, _test_users)

        httpCode = testutil.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

        #Validate access to the databases just created
        for _test_user in _test_users:
            _username = _test_user['name']
            _db_access_list = self.dbaas.users.list_access(self.instance_id, _username)
            #create a dict to compare with
            _db_actual_list = []
            for db_list in _db_access_list:
                _db_actual = {'name': db_list.name}
                _db_actual_list.append(_db_actual)
            self.assertEqual(_databases, _db_actual_list,
                             "Expected %s | Actual %s"
                             % (_databases, _db_actual_list))

        #Revoke access to the dbs
        db_count = 2
        for _test_user in _test_users:
            _username = _test_user['name']
            for _db in _databases:
                self.dbaas.users.revoke(self.instance_id, _username, _db['name'])
                httpCode = testutil.get_last_response_code(self.dbaas)
                self.assertTrue(httpCode == '202',
                                "Create instance failed with code %s" % httpCode)
                db_count -= 1
                _db_access_list = self.dbaas.users.list_access(self.instance_id, _username)
                self.assertEqual(len(_db_access_list), db_count)
                _db_actual_list = []
                for db_list in _db_access_list:
                    _db_actual = {'name': db_list.name}
                    _db_actual_list.append(_db_actual)
                self.assertNotEqual(_databases, _db_actual_list,
                                    "Expected %s | Actual %s"
                                    % (_databases, _db_actual_list))
            #Grant access to the dbs
        db_count = 0
        for _test_user in _test_users:
            _username = _test_user['name']
            for _db in _databases:
                _db_list = [_db['name']]
                self.dbaas.users.grant(self.instance_id, _username, _db_list)
                httpCode = testutil.get_last_response_code(self.dbaas)
                self.assertTrue(httpCode == '202',
                                "Create instance failed with code %s" % httpCode)
                db_count += 1
                _db_access_list = self.dbaas.users.list_access(self.instance_id, _username)
                self.assertEqual(len(_db_access_list), db_count,
                                 "Expected database count %s, Actual DBs found %s"
                                 % (db_count, _db_access_list))
                _db_actual_list = []
                for db_list in _db_access_list:
                    _db_actual = {'name': db_list.name}
                    _db_actual_list.append(_db_actual)
                if db_count != 2:
                    self.assertNotEqual(_databases, _db_actual_list,
                                        "Expected %s | Actual %s"
                                        % (_databases, _db_actual_list))
                else:
                    self.assertEqual(_databases, _db_actual_list,
                                     "Expected %s | Actual %s"
                                     % (_databases, _db_actual_list))

        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(testutil.found_resource(self.dbaas,
                                                 instanceId=self.instance_id,
                                                 userName=_user_name),
                         "Delete error: Found user name: %s in the list." % _user_name)