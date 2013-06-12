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


class TestDatabases(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(TestDatabases, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient
        NAME = "qe-database-testing"
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
        #status = instance.status
        status, elapsed_time = cls.behavior.wait_for_active(
            cls.dbaas,
            instanceId=cls.instance_id)
        assert status == "ACTIVE"

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
                cls.dbaas.instances.get(
                    cls.instance_id).delete()

    def test_create_db_singular(self):
        db_name = "1234FiRstdb"
        _databases = [{"name": db_name,
                       "character_set": "latin2",
                       "collate": "latin2_general_ci"}]

        self.dbaas.databases.create(self.instance_id, _databases)
        http_code = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(http_code == '202',
                        "Create instance failed with code %s" % http_code)

        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)

        self.assertTrue(self.behavior.get_instance_status(
            self.dbaas,
            instanceId=self.instance_id) == 'ACTIVE',
            "Instance is not in Active statue")

        #Get the instance and check instance attribs:
        # such as the flavor / volume size
        _databases = self.dbaas.databases.list(
            self.dbaas.instances.get(self.instance_id))
        self.assertTrue(len(_databases) == 1,
                        "Expected 1 database: Got: %s " % len(_databases))

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            databaseName=db_name),
            "Did not find our database name: %s in the list."
            % db_name)
        self.dbaas.databases.delete(self.instance_id, db_name)
        self.assertFalse(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            databaseName=db_name),
            "Delete error: Found database name: %s in the list."
            % db_name)

    def test_create_db_multiple(self):
        db_name = "firstdb"
        db_name2 = "secdb"
        db_name3 = "thirddb"
        _databases = [{"name": db_name,
                       "character_set": "latin2",
                       "collate": "latin2_general_ci"},
                      {"name": db_name2},
                      {"name": db_name3}]

        self.dbaas.databases.create(self.instance_id, _databases)
        http_code = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(http_code == '202',
                        "Create instance failed with code %s" % http_code)

        self.behavior.wait_for_active(self.dbaas, instanceId=self.instance_id)

        self.assertTrue(self.behavior.get_instance_status(
            self.dbaas,
            instanceId=self.instance_id) == 'ACTIVE',
            "Instance is not in Active statue")

        #Get the instance and check instance attribs:
        # such as the flavor / volume size
        _databases = self.dbaas.databases.list(
            self.dbaas.instances.get(self.instance_id))
        self.assertTrue(len(_databases) == 3,
                        "Expected 3 dbs: Got: %s " % len(_databases))

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=self.instance_id,
            databaseName=db_name3),
            "Did not find our database name: %s in the list."
            % db_name3)
        for _db in _databases:
            self.dbaas.databases.delete(self.instance_id, _db.name)
            self.assertFalse(self.behavior.found_resource(
                self.dbaas,
                instanceId=self.instance_id,
                databaseName=_db.name),
                "Delete error: Found database name: %s in the list."
                % _db.name)
