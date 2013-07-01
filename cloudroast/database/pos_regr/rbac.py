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

import json

from test_repo.database.fixtures import DBaaSFixture


class RBACTest(DBaaSFixture):
    dbaas_admin = None
    dbaas_creator = None
    dbaas_observer = None
    admin_instance_id = None
    creator_instance_id = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for smoke testing

        """
        super(RBACTest, cls).setUpClass()

        cls.dbaas_admin = cls.admin_client.reddwarfclient
        cls.dbaas_admin.authenticate()
        resp, body = RBACTest.dbaas_admin.client.last_response
        j = json.loads(body)
        role = j['access']['user']['roles'][0]['name']
        assert (role == DBaaSFixture.Role.admin)

        cls.dbaas_creator = cls.creator_client.reddwarfclient
        cls.dbaas_creator.authenticate()
        resp, body = cls.dbaas_creator.client.last_response
        j = json.loads(body)
        roles = j['access']['user']['roles']
        role_found = False
        for role in roles:
            role_name = role['name']
            if role_name == DBaaSFixture.Role.creator:
                role_found = True
        assert role_found

        cls.dbaas_observer = cls.observer_client.reddwarfclient
        cls.dbaas_observer.authenticate()
        resp, body = cls.dbaas_observer.client.last_response
        j = json.loads(body)
        roles = j['access']['user']['roles']
        role_found = False
        for role in roles:
            role_name = role['name']
            if role_name == DBaaSFixture.Role.observer:
                role_found = True
        assert role_found

        try:
            cls.admin_instance_id, time = \
                cls.behavior.create_active_instance(cls.dbaas_admin)
        except BaseException as be:
            assert be is None
        try:
            cls.creator_instance_id, time = \
                cls.behavior.create_active_instance(cls.dbaas_creator)
        except BaseException as be:
            assert be is None

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        #Delete the instance ID created for test if active
        status = cls.behavior.get_instance_status(cls.dbaas_creator,
                                                  cls.creator_instance_id)
        if cls.behavior.is_instance_active(cls.dbaas_creator,
                                           instanceStatus=status):
            cls.dbaas_admin.instances.get(cls.creator_instance_id).delete()

        status = cls.behavior.get_instance_status(cls.dbaas_admin,
                                                  cls.admin_instance_id)
        if cls.behavior.is_instance_active(cls.dbaas_admin,
                                           instanceStatus=status):
            cls.dbaas_admin.instances.get(cls.admin_instance_id).delete()

    def test_rbac_database_admin_rights(self):

        db_name = "rpadm_DB"
        db_body = [{"name": db_name}]

        try:
            self.dbaas_admin.databases.create(self.admin_instance_id, db_body)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '202',
                            "Expected http code: %s | Actual http code: %s "
                            % ('202', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_admin.databases.list(
                self.dbaas_creator.instances.get(self.admin_instance_id))
            self.assertTrue(httpCode == '202',
                            "Expected http code: %s | Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_admin.databases.delete(self.admin_instance_id, db_name)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '202',
                            "Expected http code: %s | Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

    def test_rbac_users_admin_rights(self):

        db_name = "rp_db"
        db_body = [{"name": db_name}]
        user_name = "rp_user"
        user_body = [{"databases": db_body,
                      "name": user_name,
                      "password": "password"}]

        try:
            self.dbaas_admin.users.create(self.admin_instance_id, user_body)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '202',
                            "Users Create: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))
            self.dbaas_admin.users.list(
                self.dbaas_admin.instances.get(self.admin_instance_id))
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '200',
                            "Users list: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            self.dbaas_admin.users.delete(self.admin_instance_id, db_name)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '202',
                            "Users Delete: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))

            self.dbaas_admin.users.list_access(self.admin_instance_id,
                                               user_name)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '200',
                            "Users List Access: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            self.dbaas_admin.users.revoke(self.admin_instance_id, user_name,
                                          db_name)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '202',
                            "Users Revoke: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            _db_list = [db_name]
            self.dbaas_admin.users.grant(self.admin_instance_id, user_name,
                                         _db_list)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '202',
                            "Users Grant: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))

            user_body[0]['password'] = "newpassword"
            self.dbaas_admin.users.change_passwords(self.admin_instance_id,
                                                    user_body)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '202',
                            "Users Password Change: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))

        except Exception as e:
            self.fail(e)

    def test_rbac_flavors_admin_rights(self):

        expectedFlavorRamName = {512: "512MB Instance",
                                 1024: "1GB Instance",
                                 2048: "2GB Instance",
                                 4096: "4GB Instance",
                                 8192: "8GB Instance",
                                 16384: "16GB Instance"}
        try:
            flavorList = self.dbaas_admin.flavors.list()
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '200',
                            "Expected http code: %s | Actual http code: %s "
                            % ('200', httpCode))
            #print(flavorList)
            actualFlavorRamName = {}
            self.assertIsNotNone(flavorList, "Error: no flavors returned")
            for flavor in flavorList:
                self.assertIsNotNone(flavor.id, "Error: flavor id is None")
                self.assertIsNotNone(flavor.links,
                                     "Error: flavor links is None")
                self.assertIsNotNone(flavor.name, "Error: flavor name is None")
                self.assertIsNotNone(flavor.ram, "Error: flavor ram is None")
                actualFlavorRamName[flavor.ram] = str(flavor.name)

            self.assertEqual(expectedFlavorRamName,
                             actualFlavorRamName,
                             "Flavors expected %s | Actual were %s"
                             % (expectedFlavorRamName, actualFlavorRamName))
        except Exception as e:
            self.fail(e)

    def test_rbac_instance_admin_rights(self):

        next_flavor = 1
        final_flavor = 2
        resize_vol = 5

        try:
            # list instances
            instancesList = self.dbaas_admin.instances.list()
            self.assertIsNotNone(instancesList)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '200',
                            "DB List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
            # list instance details
            current_instance = self.dbaas_admin.instances.get(
                self.admin_instance_id)
            self.assertIsNotNone(current_instance)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '200',
                            "DB List Get Id:Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            #Enable root
            user_name, user_password = self.dbaas_admin.root.create(
                self.admin_instance_id)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '200',
                            "DB Enable Root: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
            self.assertEqual(user_name, 'root', "Error: user name is not root")
            self.assertIsNotNone(user_password, "Error: root password is None")

            # finally, verify root has been enabled for the instance
            self.assertTrue(
                self.dbaas_admin.root.is_root_enabled(self.admin_instance_id),
                "Error: root is not enabled")

            # resize instance
            self.dbaas_admin.instances.resize_instance(self.admin_instance_id,
                                                       next_flavor)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode ==
                            '202', "DB Resize: Expected http code: %s "
                                   "| Actual http code: %s "
                                   % ('202', httpCode))
            status = self.behavior.get_instance_status(self.dbaas_admin,
                                                       self.admin_instance_id)
            self.assertEqual(status, "RESIZE",
                             "Error: instance is not RESIZE, it is: %s"
                             % status)
            self.behavior.wait_for_active(self.dbaas_admin,
                                          instanceId=self.admin_instance_id)

            #get the new flavorId
            flavorId = self.dbaas_admin.instances.get(
                self.admin_instance_id).flavor["id"]
            self.assertEqual(str(next_flavor), flavorId,
                             "Error: Flavors do not match: %s != %s"
                             % (next_flavor, flavorId))
            #resize again
            self.dbaas_admin.instances.resize_instance(self.admin_instance_id,
                                                       final_flavor)
            status = self.behavior.get_instance_status(self.dbaas_admin,
                                                       self.admin_instance_id)
            self.assertEqual(status, "RESIZE",
                             "Error: instance is not RESIZE, it is: %s"
                             % status)
            self.behavior.wait_for_active(self.dbaas_admin,
                                          instanceId=self.admin_instance_id)

            #get the new flavorId
            flavorId = self.dbaas_admin.instances.get(
                self.admin_instance_id).flavor["id"]
            self.assertEqual(str(final_flavor), flavorId,
                             "Error: Flavors do not match: %s != %s"
                             % (final_flavor, flavorId))
            #restart instance
            self.dbaas_admin.instances.restart(self.admin_instance_id)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '202',
                            "DB Restart: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))
            status = self.behavior.get_instance_status(self.dbaas_admin,
                                                       self.admin_instance_id)
            self.assertEqual(status,
                             "REBOOT",
                             "Error: instance is not REBOOT, it is: %s"
                             % status)

            self.behavior.wait_for_active(self.dbaas_admin,
                                          instanceId=self.admin_instance_id)
            #resize instance volume
            self.dbaas_admin.instances.resize_volume(self.admin_instance_id,
                                                     resize_vol)
            httpCode = self.behavior.get_last_response_code(self.dbaas_admin)
            self.assertTrue(httpCode == '202',
                            "DB Reboot: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))
            status = self.behavior.get_instance_status(self.dbaas_admin,
                                                       self.admin_instance_id)
            self.assertEqual(status,
                             "RESIZE",
                             "Error: instance is not RESIZE, it is: %s"
                             % status)
            self.behavior.wait_for_active(self.dbaas_admin,
                                          instanceId=self.admin_instance_id)

            #Get the new volume size
            volume_size = self.dbaas_admin.instances.get(
                self.admin_instance_id).volume["size"]
            self.assertEqual(resize_vol, volume_size,
                             "Error: Flavors do not match: %s != %s"
                             % (resize_vol, volume_size))
        except Exception as e:
            self.fail(e)

    def test_rbac_database_creator_rights(self):

        db_name = "crt_DB"
        db_body = [{"name": db_name}]

        try:
            self.dbaas_creator.databases.create(self.creator_instance_id,
                                                db_body)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '202',
                            "DB Create: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_creator.databases.list(self.dbaas_creator.instances.get(
                self.creator_instance_id))
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "DB List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_creator.databases.delete(self.creator_instance_id,
                                                db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405',
                            "DB Delete: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

    def test_rbac_users_creator_rights(self):

        db_name = "rp_creator_db"
        db_body = [{"name": db_name}]
        user_name = "rp_creator_user"
        user_body = [{"databases": db_body, "name": user_name,
                      "password": "password"}]

        try:
            self.dbaas_creator.users.create(self.creator_instance_id,
                                            user_body)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '202',
                            "Expected http code: %s "
                            "| Actual http code: %s "
                            % ('202', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_creator.users.list(
                self.dbaas_creator.instances.get(self.creator_instance_id))
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "Expected http code: %s | Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_creator.users.delete(self.creator_instance_id, db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405', "Users Delete: Expected http "
                                               "code: %s | "
                                               "Actual http code: %s "
                                               % ('405', httpCode))
        try:
            self.dbaas_creator.users.list_access(self.creator_instance_id,
                                                 user_name)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "Users List Access: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_creator.users.revoke(self.creator_instance_id,
                                            user_name,
                                            db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405',
                            "Users Revoke: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
        try:
            _db_list = [db_name]
            self.dbaas_creator.users.grant(self.creator_instance_id,
                                           user_name,
                                           _db_list)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405',
                            "Users Grant: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
        try:
            user_body[0]['password'] = "newpassword"
            self.dbaas_creator.users.change_passwords(self.creator_instance_id,
                                                      user_body)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405',
                            "Users Password Change: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

    def test_rbac_flavors_creator_rights(self):

        expectedFlavorRamName = {512: "512MB Instance",
                                 1024: "1GB Instance",
                                 2048: "2GB Instance",
                                 4096: "4GB Instance",
                                 8192: "8GB Instance",
                                 16384: "16GB Instance"}
        try:
            flavorList = self.dbaas_creator.flavors.list()
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "DB Flavor List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
            #print(flavorList)
            actualFlavorRamName = {}
            self.assertIsNotNone(flavorList, "Error: no flavors returned")
            for flavor in flavorList:
                self.assertIsNotNone(flavor.id, "Error: flavor id is None")
                self.assertIsNotNone(flavor.links,
                                     "Error: flavor links is None")
                self.assertIsNotNone(flavor.name, "Error: flavor name is None")
                self.assertIsNotNone(flavor.ram, "Error: flavor ram is None")
                actualFlavorRamName[flavor.ram] = str(flavor.name)

            self.assertEqual(expectedFlavorRamName,
                             actualFlavorRamName,
                             "Flavors expected %s | Actual were %s"
                             % (expectedFlavorRamName, actualFlavorRamName))
        except Exception as e:
            self.fail(e)

    def test_rbac_instance_creator_rights(self):

        next_flavor = 1
        resize_vol = 5

        try:
            # list instances
            instancesList = self.dbaas_creator.instances.list()
            self.assertIsNotNone(instancesList)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "DB list: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
            # list instance details
            current_instance = self.dbaas_creator.instances.get(
                self.creator_instance_id)
            self.assertIsNotNone(current_instance)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "DB list get ID: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            try:
                #Enable root
                self.dbaas_creator.root.create(self.creator_instance_id)
                raise Exception
            except Exception as e:
                httpCode = self.behavior.get_last_response_code(
                    self.dbaas_creator)
                self.assertTrue(httpCode == '405',
                                "Enable root: Expected http code: %s "
                                "| Actual http code: %s "
                                % ('405', httpCode))

            self.dbaas_creator.root.is_root_enabled(self.creator_instance_id)
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '200',
                            "Expected http code: %s | Actual http code: %s "
                            % ('200', httpCode))

            try:
            # resize instance
                self.dbaas_creator.instances.resize_instance(
                    self.creator_instance_id,
                    next_flavor)
                raise Exception
            except Exception as e:
                httpCode = self.behavior.get_last_response_code(
                    self.dbaas_creator)
                self.assertTrue(httpCode == '405',
                                "Resize Instance: Expected http code: %s "
                                "| Actual http code: %s "
                                % ('405', httpCode))
            try:

                #restart instance
                self.dbaas_creator.instances.restart(self.creator_instance_id)
                raise Exception
            except Exception as e:
                httpCode = self.behavior.get_last_response_code(
                    self.dbaas_creator)
                self.assertTrue(httpCode == '405',
                                "Restart Instance: Expected http code: %s "
                                "| Actual http code: %s "
                                % ('405', httpCode))

            try:
                #resize instance volume
                self.dbaas_creator.instances.resize_volume(
                    self.creator_instance_id,
                    resize_vol)
                raise Exception
            except Exception as e:
                httpCode = self.behavior.get_last_response_code(
                    self.dbaas_creator)
                self.assertTrue(httpCode == '405',
                                "Resize Volume: Expected http code: %s "
                                "| Actual http code: %s "
                                % ('405', httpCode))

            #Delete an instance
            try:
                self.dbaas_creator.instances.get(
                    self.creator_instance_id).delete()
                raise Exception
            except Exception as e:
                httpCode = self.behavior.get_last_response_code(
                    self.dbaas_creator)
                self.assertTrue(httpCode == '405',
                                "DB Instance Delete: Expected http code: %s "
                                "| Actual http code: %s "
                                % ('405', httpCode))

        except Exception as e:
            self.fail(e)

    def test_rbac_database_observer_rights(self):

        db_name = "obs_DB"
        db_body = [{"name": db_name}]

        try:
            self.dbaas_observer.databases.create(self.creator_instance_id,
                                                 db_body)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "DB Create: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

        try:
            self.dbaas_observer.databases.list(
                self.dbaas_observer.instances.get(self.creator_instance_id))
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "DB List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_observer.databases.delete(self.creator_instance_id,
                                                 db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "DB Delete: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

    def test_rbac_users_observer_rights(self):

        db_name = "rp_users_observer_db"
        db_body = [{"name": db_name}]
        user_name = "rp_observer_user"
        user_body = [{"databases": db_body, "name": user_name,
                      "password": "password"}]

        try:
            self.dbaas_observer.users.create(self.creator_instance_id,
                                             user_body)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Users Create: Expected http code: %s |"
                            " Actual http code: %s "
                            % ('405', httpCode))

        try:
            self.dbaas_observer.users.list(
                self.dbaas_observer.instances.get(self.creator_instance_id))
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "Users List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_observer.users.delete(self.creator_instance_id, db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Expected http code: %s | Actual http code: %s "
                            % ('405', httpCode))
        try:
            self.dbaas_observer.users.list_access(self.creator_instance_id,
                                                  user_name)
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "Users List Access: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
        except Exception as e:
            self.fail(e)

        try:
            self.dbaas_observer.users.revoke(self.creator_instance_id,
                                             user_name,
                                             db_name)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Users Revoke: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
        try:
            _db_list = [db_name]
            self.dbaas_observer.users.grant(self.creator_instance_id,
                                            user_name,
                                            _db_list)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Users Grant: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
        try:
            user_body[0]['password'] = "newpassword"
            self.dbaas_observer.users.change_passwords(
                self.creator_instance_id,
                user_body)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Users Password Change: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

    def test_rbac_instance_observer_rights(self):

        next_flavor = 1
        resize_vol = 5

        try:
            # list instances
            self.dbaas_observer.instances.list()
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "DB list: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

            # list instance details
            self.dbaas_observer.instances.get(self.creator_instance_id)
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "DB list get ID: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))

        except Exception as e:
            self.fail(e)

        try:
            #Enable root
            self.dbaas_observer.root.create(self.creator_instance_id)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
            self.assertTrue(httpCode == '405',
                            "Enable root: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

        self.dbaas_observer.root.is_root_enabled(self.creator_instance_id)
        httpCode = self.behavior.get_last_response_code(self.dbaas_creator)
        self.assertTrue(httpCode == '200',
                        "Expected http code: %s | Actual http code: %s "
                        % ('200', httpCode))

        try:
            self.behavior.create_active_instance(self.dbaas_observer)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Instance Create: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

        try:
            self.dbaas_observer.instances.get(
                self.creator_instance_id).delete()
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Instance Delete: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

        try:
            # resize instance
            self.dbaas_observer.instances.resize_instance(
                self.creator_instance_id,
                next_flavor)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Resize Instance: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
        try:

            #restart instance
            self.dbaas_observer.instances.restart(self.creator_instance_id)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Restart Instance: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

        try:
            #resize instance volume
            self.dbaas_observer.instances.resize_volume(
                self.creator_instance_id,
                resize_vol)
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "Resize Volume: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))
            #Delete an instance
        try:
            self.dbaas_observer.instances.get(
                self.creator_instance_id).delete()
            raise Exception
        except Exception as e:
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '405',
                            "DB Instance Delete: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('405', httpCode))

    def test_rbac_flavors_observer_rights(self):

        expectedFlavorRamName = {512: "512MB Instance",
                                 1024: "1GB Instance",
                                 2048: "2GB Instance",
                                 4096: "4GB Instance",
                                 8192: "8GB Instance",
                                 16384: "16GB Instance"}
        try:
            flavorList = self.dbaas_observer.flavors.list()
            httpCode = self.behavior.get_last_response_code(
                self.dbaas_observer)
            self.assertTrue(httpCode == '200',
                            "DB Flavor List: Expected http code: %s "
                            "| Actual http code: %s "
                            % ('200', httpCode))
            #print(flavorList)
            actualFlavorRamName = {}
            self.assertIsNotNone(flavorList, "Error: no flavors returned")
            for flavor in flavorList:
                self.assertIsNotNone(flavor.id, "Error: flavor id is None")
                self.assertIsNotNone(flavor.links,
                                     "Error: flavor links is None")
                self.assertIsNotNone(flavor.name, "Error: flavor name is None")
                self.assertIsNotNone(flavor.ram, "Error: flavor ram is None")
                actualFlavorRamName[flavor.ram] = str(flavor.name)

            self.assertEqual(expectedFlavorRamName,
                             actualFlavorRamName,
                             "Flavors expected %s | Actual were %s"
                             % (expectedFlavorRamName, actualFlavorRamName))
        except Exception as e:
            self.fail(e)
