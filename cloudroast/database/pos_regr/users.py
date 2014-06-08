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


class TestUsers(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(TestUsers, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient
        NAME = "qe-user-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = cls.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = cls.behavior.get_last_response_code(cls.dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        cls.instance_id = instance.id
        status, elapsed_time = cls.behavior.wait_for_active(
            cls.dbaas,
            instanceId=cls.instance_id)
        assert(status == "ACTIVE")

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """

        #Delete the instance ID created for test if active
        if cls.instance_id is not None:
            status = cls.behavior.get_instance_status(
                cls.dbaas,
                instanceId=cls.instance_id)
            if cls.behavior.is_instance_active(cls.dbaas,
                                               instanceStatus=status):
                cls.dbaas.instances.get(cls.instance_id).delete()

    def test_create_user_req_params(self):
        _user = []
        _user_name = "F343jasdf"
        _user.append({"name": _user_name,
                      "password": "password"})

        self.dbaas.users.create(self.instance_id, _user)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)
        self.assertTrue(self.behavior.get_instance_status(
            self.dbaas,
            instanceId=self.instance_id) == 'ACTIVE',
            "Instance is not in Active statue")
        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        #TODO: need to verify this list later...
        _users = self.dbaas.users.list(
            self.dbaas.instances.get(self.instance_id))
        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Did not find our user name: %s in the list."
            % _user_name)

        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Delete error: Found user name: %s in the list."
            % _user_name)

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

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)
        self.assertTrue(
            self.behavior.get_instance_status(
                self.dbaas,
                instanceId=self.instance_id) == 'ACTIVE',
            "Instance is not in Active statue")
        #Get the instance and check user dbs
        _users = self.dbaas.users.list(
            self.dbaas.instances.get(self.instance_id))
        for _user in _users:
            self.assertEqual(_user.databases, _databases)
            #try to find our user in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Did not find our user name: %s in the list."
            % _user_name)
        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Delete error: Found user name: %s in the list."
            % _user_name)

    def test_create_multi_user_with_multi_db(self):
        _db_name1 = "multi_user_with_multi-database"
        _db_name2 = "multi_user_with_multi-db2"
        _databases = [dict(name=_db_name1),
                      {"name": _db_name2}]

        _test_users = [{"name": "F343jasdf_",
                        "password": "password",
                        "databases": _databases},
                       dict(name="403F23F343jasdf",
                            password="password",
                            databases=_databases),
                       dict(name="easy_user_name",
                            password="password",
                            databases=_databases)]

        self.dbaas.users.create(self.instance_id, _test_users)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)

        self.assertTrue(self.behavior.get_instance_status(
            self.dbaas,
            instanceId=self.instance_id) == 'ACTIVE',
            "Instance is not in Active statue")
        #Get the instance and check user dbs
        _user_list = self.dbaas.users.list(
            self.dbaas.instances.get(self.instance_id))
        for _user in _user_list:
            self.assertEqual(_user.databases, _databases)
            #try to find our user in the list
            self.assertTrue(self.behavior.found_resource(
                self.dbaas,
                instanceId=self.instance_id,
                userName=_user.name),
                "Did not find our user name: %s in the list."
                % _user.name)
            self.dbaas.users.delete(self.instance_id, _user.name)
            self.assertFalse(
                self.behavior.found_resource(
                    self.dbaas,
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

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)

        _test_user[0]['password'] = "newpassword"
        self.dbaas.users.change_passwords(self.instance_id, _test_user)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        self.dbaas.users.delete(self.instance_id, _user_name)
        self.assertFalse(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Delete error: Found user name: %s in the list."
            % _user_name)

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

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)

        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)

        #Validate access to the databases just created
        for _test_user in _test_users:
            _username = _test_user['name']
            _db_access_list = self.dbaas.users.list_access(self.instance_id,
                                                           _username)
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
                self.dbaas.users.revoke(self.instance_id, _username,
                                        _db['name'])
                httpCode = self.behavior.get_last_response_code(self.dbaas)
                self.assertTrue(httpCode == '202',
                                "Create instance failed with code %s"
                                % httpCode)
                db_count -= 1
                _db_access_list = self.dbaas.users.list_access(
                    self.instance_id, _username)
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
                httpCode = self.behavior.get_last_response_code(self.dbaas)
                self.assertTrue(httpCode == '202',
                                "Create instance failed with code %s"
                                % httpCode)
                db_count += 1
                _db_access_list = self.dbaas.users.list_access(
                    self.instance_id, _username)
                self.assertEqual(
                    len(_db_access_list), db_count,
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
        self.assertFalse(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            userName=_user_name),
            "Delete error: Found user name: %s in the list."
            % _user_name)

    def _user_list_from_names(self, user_names):
        return [{"name": name,
                 "password": "password",
                 "databases": []} for name in user_names]

    def _test_access(self, users, databases, expected_response="200"):
        """ Verify that each user in the list has access to each database in
            the list."""
        for user in users:
            access = None
            try:
                access = self.dbaas.users.list_access(
                    self.instance_id, user)
                print access
                self.assertEqual(200, self.dbaas.last_http_code,
                                 "Expected: %r does not match actual: %r " %
                                 (200, self.dbaas.last_http_code))
            except self.failureException:
                self.assertEqual(404, self.dbaas.last_http_code)
            finally:
                self.assertEqual(expected_response,
                                 self.behavior.get_last_response_code(),
                                 "Expected: %r does not match actual: %r " %
                                 (expected_response,
                                  self.behavior.get_last_response_code()))
            if access is not None:
                access = [db.name for db in access]
                self.assertEqual(set(access), set(databases))

    def _reset_access(self, users, databases, ghost_dbs):
        for user in users:
            for database in databases + ghost_dbs:
                try:
                    self.dbaas.users.revoke(self.instance_id, user, database)
                    self.assertTrue(
                        self.behavior.get_last_response_code() in [202, 404])
                except self.failureException:
                    # This is all right here, since we're resetting.
                    pass
        self._test_access(users, [])
