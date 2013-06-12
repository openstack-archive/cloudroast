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


class test_usage_retention(DBaaSFixture):
    mgmt_client = None

    @classmethod
    def setUpClass(cls):
        """
        Setup DBaaS mgmt client access

        """
        super(test_usage_retention, cls).setUpClass()
        cls.mgmt_client = cls.dbaas_provider.mgmt_client.reddwarfclient
        cls.mgmt_client.authenticate()

    @classmethod
    def tearDownClass(cls):
        """
        Setup DBaaS mgmt client access

        """
        pass

    def test_listusage_all(self):
        listOfRetentionObj = self.mgmt_client.usage.index().items
        self.assertIsNotNone(listOfRetentionObj, "No retention record to list")

    def test_listusage_allwlimit(self):

        lt = 50
        listOfRetentionObj = self.mgmt_client.usage.index(limit=lt).items
        count = 0
        for ro in listOfRetentionObj:
            count += 1
        self.assertEqual(count, lt,
                         "Error: Records listed is not equal to the set limit")

    def test_listusage_instance(self):
        listOfRetentionObj = self.mgmt_client.usage.index(limit=1).items
        length_of_records = len(listOfRetentionObj)
        self.assertEqual(length_of_records, 1,
                         "Expected records %s, Actual records %s"
                         % (1, length_of_records))
        retention_record = listOfRetentionObj[0]
        resource_Id = retention_record.resourceId
        self.assertIsNotNone(resource_Id, "Expected not None resource ID")
        retention = self.mgmt_client.usage.instance(resource_Id).items
        self.assertIsNotNone(retention, "Expected not None resource")

    def test_listusage_instance_limit(self):
        listOfRetentionObj = self.mgmt_client.usage.index(limit=1).items
        length_of_records = len(listOfRetentionObj)
        self.assertEqual(length_of_records, 1,
                         "Expected records %s, Actual records %s"
                         % (1, length_of_records))
        resource_id = listOfRetentionObj[0].id
        retention = self.mgmt_client.usage.instance(resource_id,
                                                    limit=50).items
        self.assertIsNotNone(retention, "Expected not None resource")

    def test_listusage_user(self):
        listOfRetentionObj = self.mgmt_client.usage.index(limit=1).items
        length_of_records = len(listOfRetentionObj)
        self.assertEqual(length_of_records, 1,
                         "Expected records %s, Actual records %s"
                         % (1, length_of_records))
        user = listOfRetentionObj[0].tenantId
        self.assertIsNotNone(user, "Got None for user")
        retention = self.mgmt_client.usage.account(user).items
        self.assertIsNotNone(retention, "Got None for retention")

    def test_listusage_user_limit(self):
        listOfRetentionObj = self.mgmt_client.usage.index(limit=1).items
        user = listOfRetentionObj[0].tenantId
        retention = self.mgmt_client.usage.account(user, limit=50).items
        self.assertIsNotNone(retention, "Got None for retention")

    def test_listusage_badlimit(self):
        try:
            self.mgmt_client.usage.index(limit=-5)
        except Exception as e:
            http_code = self.behavior.get_last_response_code(self.mgmt_client)
            self.assertEqual(http_code, '400', e.message)

    def test_listusage_badmarker(self):
        try:
            self.mgmt_client.usage.index(marker="foo")
        except Exception as e:
            http_code = self.behavior.get_last_response_code(self.mgmt_client)
            self.assertEqual(http_code, '400', e.message)
