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
import unittest


class test_actions(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(test_actions, cls).setUpClass()
        cls.mgmt_dbaas = cls.dbaas_provider.mgmt_client.reddwarfclient
        cls.mgmt_dbaas.authenticate()

        NAME = "qe-mgmt-actions-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = test_actions.mgmt_dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = cls.behavior.get_last_response_code(test_actions.mgmt_dbaas)
        assert(httpCode != '200',
               "Create instance failed with code %s" % httpCode)
        cls.instance_id = instance.id
        cls.instance = instance
        cls.behavior.wait_for_active(test_actions.mgmt_dbaas,
                                     instanceId=test_actions.instance_id)

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        # Delete the instance ID created for test if active
        if test_actions.instance_id is not None:
            status = cls.behavior.get_instance_status(
                test_actions.mgmt_dbaas,
                instanceId=test_actions.instance_id)
            if cls.behavior.is_instance_active(test_actions.mgmt_dbaas,
                                               instanceStatus=status):
                test_actions.mgmt_dbaas.instances.get(
                    test_actions.instance_id).delete()

    def setUp(self):
        """
        Run this setup for each test to ensure an active instance is available

        """
        instance_status = self.behavior.get_instance_status(
            self.mgmt_dbaas,
            instanceId=self.instance_id)
        if (self.behavior.is_instance_active(
                self.mgmt_dbaas,
                instanceStatus=instance_status) is False):
            # delete non-Active instance
            test_actions.mgmt_dbaas.instances.get(self.instance_id).delete()
            # start a new instance and set the global instance ID
            NAME = "qe-mgmt-actions-testing"
            FLAVOR = 1
            VOLUME = 1
            try:
                instance = self.mgmt_dbaas.instances.create(
                    name=NAME,
                    flavor_id=FLAVOR,
                    volume={"size": VOLUME},
                    databases=[{"databases": [{"name": "databaseA"}],
                                "name": "dbuser1",
                                "password": "password"}])
                httpCode = self.behavior.get_last_response_code(
                    self.mgmt_dbaas)
                if httpCode != '200':
                    raise Exception("Create instance failed with code %s" %
                                    httpCode)
                self.instance_id = instance.id
                self.instance = instance
                self.behavior.wait_for_active(self.mgmt_dbaas,
                                              instanceId=self.instance_id)
            except Exception as e:
                self.fixture_log.debug("\tException: %r" % e)
                raise

    def test_reboot_instance(self):
        expected_status = "REBOOT"
        expected_status_found = False
        expected_task_desc = "No tasks for the instance."
        initial_updated = ""

        # list instance details and store updated time value
        instance_details = test_actions.mgmt_dbaas.management.show(
            self.instance)
        httpCode = self.behavior.get_last_response_code(
            test_actions.mgmt_dbaas)
        self.assertTrue(httpCode == '200',
                        "List instance details failed with code %s"
                        % httpCode)
        initial_updated = instance_details.updated
        self.fixture_log.debug("\t\tInstance %r initial update on %r" %
                               (instance_details.id, initial_updated))

        # call reboot instance
        try:
            self.mgmt_dbaas.management.reboot(self.instance_id)
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '202',
                            "Reboot instance failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        # check instance for Reboot status
        current_status, elapsed = self.behavior.wait_for_status(
            self.mgmt_dbaas,
            self.instance_id,
            expected_status)
        self.fixture_log.debug("\t\tInstance status encountered: %r" %
                               current_status)
        self.assertEqual(current_status, expected_status,
                         "Expected status %r , Actual status %r" %
                         (expected_status, current_status))
        if current_status == expected_status:
            expected_status_found = True
        self.fixture_log.debug("\t\tExpected status found? %r" %
                               expected_status_found)

        # verify it comes up in an Active state
        status, elapsed = self.behavior.wait_for_active(
            self.mgmt_dbaas,
            instanceId=self.instance_id)
        self.fixture_log.debug("\t\tInstance status encountered: %r" %
                               status)
        self.assertEqual(status, 'ACTIVE',
                         "Expected status %r , Actual status %r" %
                         ('ACTIVE', status))

        # make final checks
        self.assertTrue(expected_status_found,
                        "Expected status %r was not seen!" %
                        expected_status)
        instance_details = test_actions.mgmt_dbaas.management.show(
            self.instance)
        httpCode = self.behavior.get_last_response_code(
            test_actions.mgmt_dbaas)
        if httpCode != '200':
            raise Exception("List instance details failed with code %s" %
                            httpCode)
        self.assertTrue(initial_updated != instance_details.updated,
                        "Instance %r was not updated!" %
                        instance_details.id)
        self.fixture_log.debug("\t\tInstance %r final update on %r" %
                               (instance_details.id, instance_details.updated))

    @unittest.skip("Not implemented")
    def test_reset_instance_task_status(self):
        pass

    @unittest.skip("Not implemented")
    def test_migrate_instance(self):
        pass
