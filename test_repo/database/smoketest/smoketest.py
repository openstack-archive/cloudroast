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

import unittest
from test_repo.database.fixtures import DBaaSFixture
from test_repo.database import dbaas_util as testutil


class SmokeTest(DBaaSFixture):
    # @classmethod
    # def setUpClass(cls):
    #     """
    #     Creating an instance for smoke testing
    #
    #     """
    #     super(SmokeTest, cls).setUpClass()
    #     cls.database = cls.client.reddwarfclient
    #     cls.version_url = cls.version_url

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for smoke testing

        """
        tc_name = "Create Instance"

        super(SmokeTest, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient
        if cls.stability_mode == 'True':
            cls.stability_mode = True
        else:
            cls.stability_mode = False
        cls.NAME = "qe-smoke"
        cls.FLAVOR = 4
        cls.VOLUME = 1
        try:
            instance = cls.dbaas.instances.create(
                name=cls.NAME,
                flavor_id=cls.FLAVOR,
                volume={"size": cls.VOLUME},
                databases=[{"databases": [{"name": "databaseA"}],
                            "name": "dbuser1",
                            "password": "password"}])
            httpCode = testutil.get_last_response_code(cls.dbaas)
            if httpCode != '200':
                raise Exception(
                    "Create instance failed with code %s" % httpCode)
            cls.instance_id = instance.id
            #status = instance.status
            testutil.waitForActive(cls.dbaas, instanceId=cls.instance_id)
            if cls.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if cls.stability_mode:
                testutil.write_to_error_report(cls.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        #Delete the instance ID created for test if active
        status = testutil.getInstanceStatus(cls.dbaas, cls.instance_id)
        if testutil.isInstanceActive(cls.dbaas, instanceStatus=status):
            cls.dbaas.instances.get(cls.instance_id).delete()

    def setUp(self):
        """
        Run this setup for each test to ensure an active instance is available

        """
        super(SmokeTest, self).setUp()

        tc_name = "Create Instance"
        instance_status = testutil.getInstanceStatus(
            self.dbaas,
            instanceId=self.instance_id)

        if testutil.isInstanceActive(self.dbaas,
                                     instanceStatus=instance_status) is False:
            #start a new instance and set the global instance ID
            NAME = "qe-smoke"
            FLAVOR = 4
            VOLUME = 1
            try:
                instance = self.dbaas.instances.create(
                    name=NAME,
                    flavor_id=FLAVOR,
                    volume={"size": VOLUME},
                    databases=[{"databases": [{"name": "databaseA"}],
                                "name": "dbuser1",
                                "password": "password"}])
                httpCode = testutil.get_last_response_code(self.dbaas)
                if httpCode != '200':
                    raise Exception(
                        "Create instance failed with code %s" % httpCode)
                self.instance_id = instance.id
                testutil.waitForActive(self.dbaas, instanceId=self.instance_id)
                if self.stability_mode:
                    testutil.write_to_report(tc_name, tc_pass=True)
            except Exception as e:
                if self.stability_mode:
                    testutil.write_to_error_report(self.instance_id, repr(e))
                    testutil.write_to_report(tc_name, tc_pass=False)
                raise

    def test_list_instances(self):
        """
        Test listing all instances

        """
        tc_name = "List Instances"
        try:
            instancesList = self.dbaas.instances.list()
            self.assertIsNotNone(instancesList)
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_list_instance_details(self):
        """
        Test listing all instance details

        """
        tc_name = "List Instance Details"

        str_flavor_size = str(self.FLAVOR)

        try:
            instance = self.dbaas.instances.get(self.instance_id)
            self.assertIsNotNone(instance)
            exp_flavor_bookmark_link = '%s/flavors/%s'.format(self.version_url,
                                                              str_flavor_size)
            exp_flavor_self_link = '%s/%s/flavors/%s'.format(self.host_url,
                                                             self.tenant_id,
                                                             str_flavor_size)
            exp_instance_bookmark_link = '%s/instances/%s'.format(
                self.version_url,
                self.instance_id)
            exp_instance_self_link = '%s/%s/instances/%s'.format(
                self.host_url,
                self.tenant_id,
                self.instance_id)

            act_flavor_links = instance.flavor['links']
            act_flavor_bookmark_link = None
            act_flavor_self_link = None
            for link_type in act_flavor_links:
                if link_type['rel'] == 'self':
                    act_flavor_self_link = link_type['href']
                else:
                    act_flavor_bookmark_link = link_type['href']

            act_links = instance.links
            act_instance_bookmark_link = None
            act_instance_self_link = None
            for link_type in act_links:
                if link_type['rel'] == 'self':
                    act_instance_self_link = link_type['href']
                else:
                    act_instance_bookmark_link = link_type['href']

            self.assertIsNotNone(instance,
                                 "Expected not none, Actual %s" % instance)
            self.assertIsNotNone(instance.hostname,
                                 "Expected not none, Actual %s" %
                                 instance.hostname)
            self.assertIsNotNone(instance.volume['used'],
                                 "Expected not none, Actual %s" %
                                 instance.volume['used'])
            self.assertEqual(self.NAME, instance.name,
                             "Expected %s , Actual %s"
                             % (self.NAME, instance.name))
            self.assertEqual(self.VOLUME, instance.volume['size'],
                             "Expected %s , Actual %s"
                             % (self.VOLUME, instance.volume['size']))
            self.assertEqual(str_flavor_size, instance.flavor['id'],
                             "Expected %s , Actual %s"
                             % (str_flavor_size, instance.flavor['id']))
            self.assertEqual(exp_flavor_self_link,
                             act_flavor_self_link,
                             "Expected %s , Actual %s"
                             % (exp_flavor_self_link, act_flavor_self_link))
            self.assertEqual(exp_flavor_bookmark_link,
                             act_flavor_bookmark_link,
                             "Expected %s , Actual %s"
                             % (exp_flavor_bookmark_link,
                                act_flavor_bookmark_link))

            self.assertEqual(exp_instance_bookmark_link,
                             act_instance_bookmark_link,
                             "Expected %s , Actual %s"
                             % (exp_instance_bookmark_link,
                                act_instance_bookmark_link))
            self.assertEqual(exp_instance_self_link,
                             act_instance_self_link,
                             "Expected %s , Actual %s"
                             % (
                                 exp_instance_self_link,
                                 act_instance_self_link))

            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_list_flavors(self):
        """
        Test listing flavors

        """

        tc_name = "List Flavors"

        # instance STATE constants
        expectedFlavorRamName = {512: "512MB Instance",
                                 1024: "1GB Instance",
                                 2048: "2GB Instance",
                                 4096: "4GB Instance",
                                 8192: "8GB Instance",
                                 16384: "16GB Instance"}
        try:
            flavorList = self.dbaas.flavors.list()
            #create dict of actual flavors to compare against
            actualFlavorRamName = {}
            self.assertIsNotNone(flavorList, "Error: no flavors returned")
            for flavor in flavorList:
                self.assertIsNotNone(flavor.id, "Error: flavor id is None")
                self.assertIsNotNone(flavor.links,
                                     "Error: flavor links is None")
                self.assertIsNotNone(flavor.name, "Error: flavor name is None")
                self.assertIsNotNone(flavor.ram, "Error: flavor ram is None")
                actualFlavorRamName[flavor.ram] = str(flavor.name)

            self.assertEqual(expectedFlavorRamName, actualFlavorRamName,
                             "Flavors expected %s | Actual were %s"
                             % (expectedFlavorRamName, actualFlavorRamName))
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_flavors_by_get(self):
        """
        test_flavors_by_get

        """

        tc_name = "List Flavors By Get"

        try:
            # pull flavors list
            flavors = self.dbaas.flavors.list()
            self.assertIsNotNone(flavors, "Error: no flavors returned")

            # list each flavor
            for i in xrange(1, len(flavors) + 1):
                flavor = self.dbaas.flavors.get(i)
                self.assertIsNotNone(flavor, "Error: flavor id does not exist")
                self.assertIsNotNone(flavor.id, "Error: flavor id is None")
                self.assertIsNotNone(flavor.links,
                                     "Error: flavor links is None")
                self.assertIsNotNone(flavor.name, "Error: flavor name is None")
                self.assertIsNotNone(flavor.ram, "Error: flavor ram is None")
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_resize_instance(self):
        """
        test resize of instance

        """

        tc_name = "Resize Instance"

        next_flavor = 1
        final_flavor = 2

        try:
            self.dbaas.instances.resize_instance(self.instance_id, next_flavor)
            status = testutil.getInstanceStatus(self.dbaas, self.instance_id)

            self.assertEqual(status, "RESIZE",
                             "Error: instance is not RESIZE, it is: %s" %
                             status)
            testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

            #get the new flavorId
            flavorId = self.dbaas.instances.get(self.instance_id).flavor["id"]
            self.assertEqual(str(next_flavor), flavorId,
                             "Error: Flavors do not match: %s != %s"
                             % (next_flavor, flavorId))

            self.dbaas.instances.resize_instance(self.instance_id,
                                                 final_flavor)
            status = testutil.getInstanceStatus(self.dbaas, self.instance_id)
            self.assertEqual(status, "RESIZE",
                             "Error: instance is not RESIZE, it is: %s" %
                             status)
            testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

            #get the new flavorId
            flavorId = self.dbaas.instances.get(self.instance_id).flavor["id"]
            self.assertEqual(str(final_flavor), flavorId,
                             "Error: Flavors do not match: %s != %s"
                             % (final_flavor, flavorId))
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_restart_instance(self):
        """
        test restart of instance

        """

        tc_name = "Restart Instance"

        try:
            # restart the instance
            self.dbaas.instances.restart(self.instance_id)
            status = testutil.getInstanceStatus(self.dbaas, self.instance_id)

            # check interim status of REBOOT
            self.assertEqual(status,
                             "REBOOT",
                             "Error: instance is not REBOOT, it is: %s" %
                             status)
            testutil.waitForActive(self.dbaas, instanceId=self.instance_id)
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_resize_volume(self):
        """
        Test Resize volume

        """

        tc_name = "Resize Volume"
        resize_vol = 6

        try:
            self.dbaas.instances.resize_volume(self.instance_id, resize_vol)
            status = testutil.getInstanceStatus(self.dbaas, self.instance_id)

            # check interim status of RESIZE
            self.assertEqual(status,
                             "RESIZE",
                             "Error: instance is not RESIZE, it is: %s" %
                             status)

            testutil.waitForActive(self.dbaas, instanceId=self.instance_id)

            #Get the new volume size
            volume_size = self.dbaas.instances.get(self.instance_id).volume[
                "size"]
            self.assertEqual(resize_vol, volume_size,
                             "Error: Flavors do not match: %s != %s"
                             % (resize_vol, volume_size))
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_create_database(self):
        """
        Test to create a database

        """

        tc_name = "Create Database"

        db_name = "qe-smoke-db005"
        db_body = [{"name": db_name}]

        try:
            self.dbaas.databases.create(self.instance_id, db_body)

            db_list = self.dbaas.databases.list(
                self.dbaas.instances.get(self.instance_id))
            self.assertEqual(len(db_list), 2)

            foundDB = False
            for db in db_list:
                if db.name == db_name:
                    foundDB = True
            self.assertTrue(foundDB)

            self.dbaas.databases.delete(self.instance_id, db_name)

            db_list = self.dbaas.databases.list(
                self.dbaas.instances.get(self.instance_id))
            self.assertEqual(len(db_list), 1)
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_create_user(self):
        """
        Test to create a new user

        """

        tc_name = "Create User"

        db_name = "smoke_create_user"
        db_body = [{"name": db_name}]
        user_name = "smoke_user"
        user_body = [{"databases": db_body, "name": user_name,
                      "password": "password"}]

        try:
            self.dbaas.users.create(self.instance_id, user_body)
            # the user name and the database it's assigned to
            user_list = self.dbaas.users.list(
                self.dbaas.instances.get(self.instance_id))
            for user in user_list:
                self.assertEqual(user.name, user_name,
                                 "Error: incorrect database user name")
                for db in user.databases:
                    #print("DB found for this user: %r" % (database["name"]))
                    self.assertEqual(db["name"], db_name,
                                     "Error: incorrect database name")

            # delete the user
            self.dbaas.users.delete(self.instance_id, user_name)

            user_list = self.dbaas.users.list(
                self.dbaas.instances.get(self.instance_id))
            self.assertEqual(len(user_list), 0)
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    def test_enable_root(self):
        """
        Test to enable root on an instance

        """

        tc_name = "Enable Root"

        try:
            self.assertFalse(self.dbaas.root.is_root_enabled(self.instance_id))

            # now enable root for the instance
            user_name, user_password = self.dbaas.root.create(self.instance_id)

            self.assertEqual(user_name, 'root', "Error: user name is not root")
            self.assertIsNotNone(user_password, "Error: root password is None")

            # finally, verify root has been enabled for the instance
            self.assertTrue(self.dbaas.root.is_root_enabled(self.instance_id),
                            "Error: root is not enabled")
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise

    @unittest.skip("Not running this test as part of smokes")
    def test_delete_active_instances(self):
        instances = self._get_all_instances()
        for instance in instances:
            try:
                instance.delete()
            except:
                continue
            next_marker = instances.next
            while next_marker is not None:
                instances = self._get_all_instances()
                for instance in instances:
                    try:
                        instance.delete()
                    except:
                        continue
                next_marker = instances.next

    @unittest.skip("Version feature needs auth to work...could be bug")
    def test_list_versions(self):
        """
        Tests the list versions api

        """
        tc_name = "Test List Versions"
        try:
            versions = self.dbaas.versions.index(self.version_url)
            self.assertEquals(len(versions), 1,
                              "Get an unexpected number of versions back %s" %
                              len(versions))
            version_details = self.dbaas.versions.index(
                ''.join(self.version_url, versions[0]))
            last_result_code = testutil.get_last_response_code(self.dbaas)
            self.assertTrue(last_result_code == 200,
                            "Expected http result code %s: Got %s" % (
                                last_result_code, 200))
            self.assertTrue(version_details.id == 'v1.0',
                            "Expected http result code %s: Got %s" % (
                                version_details.id, 'v1.0'))
            self.assertTrue(version_details.status == 'CURRENT',
                            "Expected http result code %s: Got %s" % (
                                version_details.status, 'CURRENT'))
            if self.stability_mode:
                testutil.write_to_report(tc_name, tc_pass=True)
        except Exception as e:
            if self.stability_mode:
                testutil.write_to_error_report(self.instance_id, repr(e))
                testutil.write_to_report(tc_name, tc_pass=False)
            raise
