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

import random

from test_repo.database.fixtures import DBaaSFixture


class test_accounts(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(test_accounts, cls).setUpClass()
        cls.mgmt_dbaas = cls.dbaas_provider.mgmt_client.reddwarfclient
        cls.mgmt_dbaas.authenticate()

        NAME = "qe-mgmt-accounts-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = test_accounts.mgmt_dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = cls.behavior.get_last_response_code(test_accounts.mgmt_dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        cls.instance_id = instance.id
        #status = instance.status
        cls.behavior.wait_for_active(test_accounts.mgmt_dbaas,
                                     instanceId=test_accounts.instance_id)

        instance_details = test_accounts.mgmt_dbaas.management.show(instance)
        httpCode = cls.behavior.get_last_response_code(
            test_accounts.mgmt_dbaas)
        if httpCode != '200':
            raise Exception("List instance details failed with code %s" %
                            httpCode)
        cls.tenant_id = instance_details.tenant_id

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """

        #Delete the instance ID created for test if active
        if test_accounts.instance_id is not None:
            status = cls.behavior.get_instance_status(
                test_accounts.mgmt_dbaas,
                instanceId=test_accounts.instance_id)
            if cls.behavior.is_instance_active(test_accounts.mgmt_dbaas,
                                               instanceStatus=status):
                test_accounts.mgmt_dbaas.instances.get(
                    test_accounts.instance_id).delete()

    def test_list_all_active_accounts(self):
        try:
            _accounts = self.mgmt_dbaas.accounts.index()
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List all active accounts failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        self.assertIs(type(_accounts.accounts), list,
                      "Expected %r , Actual %r" %
                      (list, type(_accounts.accounts)))
        for acct in _accounts.accounts:
            self.fixture_log.debug("\tAccount: %r" % acct)
            self.fixture_log.debug("\t\tAccount ID: %r" % acct["id"])
            self.fixture_log.debug(
                "\t\tAccount number of instances: %r" % acct["num_instances"])
            self.assertIs(type(acct), dict,
                          "Expected %r , Actual %r" %
                          (dict, type(acct)))
            self.assertIs(type(acct["id"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(acct["id"])))
            self.assertIs(type(acct["num_instances"]), int,
                          "Expected %r , Actual %r" %
                          (int, type(acct["num_instances"])))

    def test_list_account_details(self):
        # get a list of all accounts
        try:
            _accounts = self.mgmt_dbaas.accounts.index()
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List all active accounts failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        # pick an account to get details on
        selected_acct = random.choice(_accounts.accounts)
        self.fixture_log.debug("\tSelected account: %r" % selected_acct["id"])
        num_instances = selected_acct["num_instances"]

        # show details of account
        try:
            _account_details = self.mgmt_dbaas.accounts.show(
                selected_acct["id"])
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List account details failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        self.fixture_log.debug("\t\tAccount ID: %r" % _account_details.id)
        self.assertEqual(selected_acct["id"], _account_details.id,
                         "Error: account %r was not found!" %
                         (selected_acct["id"]))
        instance_found = False
        for inst in _account_details.instances:
            self.fixture_log.debug("\tInstance: %r" % inst)
            self.fixture_log.debug("\t\tInstance host: %r" %
                                   (inst["host"]))
            self.fixture_log.debug("\t\tInstance ID: %r" %
                                   (inst["id"]))
            self.fixture_log.debug("\t\tInstance name: %r" %
                                   (inst["name"]))
            self.fixture_log.debug("\t\tInstance status: %r" %
                                   (inst["status"]))
            if not instance_found and (_account_details.id == self.tenant_id):
                if inst["id"] == self.instance_id:
                    instance_found = True
                    self.fixture_log.debug("\t\t\tFound test inst %r for %r" %
                                           (self.instance_id,
                                            _account_details.id))
            self.assertIs(type(inst["host"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["host"])))
            self.assertIs(type(inst["id"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["id"])))
            self.assertIs(type(inst["name"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["name"])))
            self.assertIs(type(inst["status"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["status"])))
        if _account_details.id == self.tenant_id:
            self.assertTrue(instance_found,
                            "Error: %r was not found!" % self.instance_id)
        self.assertEqual(num_instances, len(_account_details.instances),
                         "Expected %r instances , Found %r instances" %
                         (num_instances, len(_account_details.instances)))
