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


class TestCreateInstances(DBaaSFixture):
    instance_id = None
    tiny_instance_id = None
    sml_instance_id = None
    med_instance_id = None
    lrg_instance_id = None
    xlrg_instance_id = None
    xxlrg_instance_id = None
    multi_dbs_instance_id = None
    req_params_instance_id = None
    multi_users_instance_id = None
    all_instances = [instance_id,
                     tiny_instance_id,
                     sml_instance_id,
                     med_instance_id,
                     lrg_instance_id,
                     xlrg_instance_id,
                     xxlrg_instance_id,
                     multi_dbs_instance_id,
                     req_params_instance_id,
                     multi_users_instance_id]

    dbaas = None
    stability_mode = False

    def _check_instance_attribs(self,
                                instance,
                                exp_flavor,
                                exp_vol,
                                exp_name):
        self.assertEqual(instance.flavor['id'],
                         str(exp_flavor),
                         "Expected %s | Actual %s" % (str(exp_flavor),
                                                      instance.flavor['id']))
        self.assertEqual(instance.volume['size'],
                         exp_vol,
                         "Expected %s | Actual %s" % (exp_vol,
                                                      instance.volume['size']))
        self.assertEqual(instance.name,
                         exp_name,
                         "Expected %s | Actual %s" % (exp_name,
                                                      instance.name))

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for smoke testing

        """
        super(TestCreateInstances, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        #Delete the instance ID created for test if active
        dbaas = cls.dbaas
        for instance_id in cls.all_instances:
            if instance_id is not None:
                status = cls.behavior.get_instance_status(
                    dbaas,
                    instanceId=instance_id)
                if cls.behavior.is_instance_active(dbaas,
                                                   instanceStatus=status):
                    dbaas.instances.get(instance_id).delete()

    def tearDown(self):
        """
        Tearing down: Deleting the instance if in active state

        """
        self.tearDownClass()

    def test_create_tiny_instance(self):
        """
        Creating a tiny instance (512M)

        """

        NAME = "qe-tiny-instance"
        FLAVOR = 1
        VOLUME = 20
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        # such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(self.dbaas,
                                                     instanceId=instance.id),
                        "Did not find our instance id: %s in the list."
                        % instance.id)

    def test_create_small_instance(self):
        """
        Creating a small instance (1G)

        """
        #print (self.instance_id)
        NAME = "qe-small-instance"
        FLAVOR = 2
        VOLUME = 40
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.sml_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        # such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(self.dbaas,
                                                     instanceId=instance.id),
                        "Did not find our instance id: %s in the list."
                        % instance.id)

    def test_create_medium_instance(self):
        """
        Creating a medium instance (2G)

        """
        NAME = "qe-medium-instance"
        FLAVOR = 3
        VOLUME = 75
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.med_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        # such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(self.dbaas,
                                                     instanceId=instance.id),
                        "Did not find our instance id: %s in the list."
                        % instance.id)

    def test_create_large_instance(self):
        """
        Creating a 4G instance

        """

        NAME = "qe-large-instance"
        FLAVOR = 4
        VOLUME = 100
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.lrg_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(self.dbaas,
                                                     instanceId=instance.id),
                        "Did not find our instance id: %s in the list."
                        % instance.id)

    def test_create_xlarge_instance(self):
        """
        Creating an 8G instance

        """
        NAME = "qe-xlarge-instance"
        FLAVOR = 5
        VOLUME = 125
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.xlrg_instance_id_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=instance.id),
            "Did not find our instance id: %s in the list." % instance.id)

    def test_create_xxlarge_instance(self):
        """
        Creating an 16G instance

        """
        NAME = "qe-xxlarge-instance"
        FLAVOR = 6
        VOLUME = 150
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.xxlrg_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=instance.id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=instance.id),
            "Did not find our instance id: %s in the list." % instance.id)

    def test_create_2_dbs_instance(self):
        """
        Creating 2 dbs instance

        """
        NAME = "qe-2dbs-instance"
        FLAVOR = 1
        VOLUME = 10

        databases = [{"name": "firstdb",
                      "character_set": "latin2",
                      "collate": "latin2_general_ci"}, {"name": "db2"}]
        users = [{"name": "lite",
                  "password": "litepass",
                  "databases": [{"name": "firstdb"},
                                {"name": "db2"}]}]

        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=databases,
            users=users)
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.multi_dbs_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=instance.id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(self.behavior.found_resource(
            self.dbaas,
            instanceId=instance.id),
            "Did not find our instance id: %s in the list." % instance.id)

    def test_create_2_users_instance(self):
        """
        Creating a 2 user instance

        """
        NAME = "qe-2users-instance"
        FLAVOR = 1
        VOLUME = 10

        databases = [{"name": "firstdb",
                      "character_set": "latin2",
                      "collate": "latin2_general_ci"}]
        users = [{"name": "lite",
                  "password": "litepass",
                  "databases": [{"name": "firstdb"}]},
                 {"name": "lite1",
                  "password": "litepass1",
                  "databases": [{"name": "firstdb"}]}]

        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=databases,
            users=users)
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.multi_users_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=instance.id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(
            self.behavior.found_resource(self.dbaas, instanceId=instance.id),
            "Did not find our instance id: %s in the list." % instance.id)

    def test_create_required_params_instance(self):
        """
        Creating an required param instance

        """
        NAME = "qe-req-params-instance"
        FLAVOR = 1
        VOLUME = 10
        instance = self.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.req_params_instance_id = instance.id
        self.assertTrue(httpCode == '200',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=instance.id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        #Get the instance and check instance attribs:
        #such as the flavor / volume size
        instance = self.dbaas.instances.get(instance)
        self._check_instance_attribs(instance, FLAVOR, VOLUME, NAME)

        #try to find our instance in the list
        self.assertTrue(
            self.behavior.found_resource(self.dbaas, instanceId=instance.id),
            "Did not find our instance id: %s in the list." % instance.id)


class test_resize_instances(DBaaSFixture):
    instance_id = None
    dbaas = None

    class FlavorTypes():
        tiny = 1
        small = 2
        med = 3
        large = 4
        xlarge = 5
        xxlarge = 6

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for smoke testing

        """
        tc_name = "Create Instance"
        super(test_resize_instances, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient

        NAME = "qe-resize_instances"
        FLAVOR = 1
        VOLUME = 10
        instance = test_resize_instances.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = cls.behavior.get_last_response_code(test_resize_instances
        .dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        test_resize_instances.instance_id = instance.id
        status, elapsed_time = cls.behavior.wait_for_active(
            test_resize_instances.dbaas,
            instanceId=test_resize_instances.instance_id)
        assert (status == "ACTIVE")

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        instance_id = test_resize_instances.instance_id
        dbaas = test_resize_instances.dbaas
        #Delete the instance ID created for test if active
        if instance_id is not None:
            status = cls.behavior.get_instance_status(dbaas,
                                                      instanceId=instance_id)
            if cls.behavior.is_instance_active(dbaas, instanceStatus=status):
                dbaas.instances.get(instance_id).delete()

    def test_resize_to_med_instance(self):
        """
        Resize an instance to 2G

        """

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.med)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        newFlavorSize = self.dbaas.instances.get(self.instance_id).flavor['id']
        self.assertTrue(newFlavorSize ==
                        str(self.FlavorTypes.med),
                        "Unexpected flavor size for resize: %s"
                        % newFlavorSize)

        #Resize back to tiny
        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.tiny)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

    def test_resize_to_large_instance(self):
        """
        Resize the instance to 4G

        """
        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.large)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        newFlavorSize = self.dbaas.instances.get(self.instance_id).flavor['id']
        self.assertTrue(newFlavorSize == str(self.FlavorTypes.large),
                        "Unexpected flavor size for resize: %s"
                        % newFlavorSize)

        #Resize back to tiny
        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.tiny)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

    def test_resize_to_xlarge_instance(self):
        """
        Resize the instance to 8G

        """

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.xlarge)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        newFlavorSize = self.dbaas.instances.get(self.instance_id).flavor['id']
        self.assertTrue(newFlavorSize == str(self.FlavorTypes.xlarge),
                        "Unexpected flavor size for resize: %s"
                        % newFlavorSize)

        #Resize back to tiny
        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.tiny)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

    def test_resize_to_xxlarge_instance(self):
        """
        Resize the instance to 16G

        """

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.xxlarge)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)

        newFlavorSize = self.dbaas.instances.get(self.instance_id).flavor['id']
        self.assertTrue(newFlavorSize == str(self.FlavorTypes.xxlarge),
                        "Unexpected flavor size for resize: %s"
                        % newFlavorSize)

        #Resize back to tiny
        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_instance(self.instance_id,
                                                 self.FlavorTypes.tiny)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)


class test_resize_volume_instances(DBaaSFixture):
    instance_id = None
    dbaas = None

    class ResizeUpSizes():
        origLevel = 10
        lev1 = 20
        lev2 = 80
        lev3 = 150

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for smoke testing

        """

        super(test_resize_volume_instances, cls).setUpClass()
        cls.dbaas = cls.client.reddwarfclient

        NAME = "qe-resize_instances"
        FLAVOR = 1
        VOLUME = test_resize_volume_instances.ResizeUpSizes.origLevel
        instance = test_resize_volume_instances.dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME},
            databases=[{"databases": [{"name": "databaseA"}],
                        "name": "dbuser1",
                        "password": "password"}])
        httpCode = cls.behavior.get_last_response_code(
            test_resize_volume_instances.dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        test_resize_volume_instances.instance_id = instance.id
        #status = instance.status
        status, elapsed_time = cls.behavior.wait_for_active(
            test_resize_volume_instances.dbaas,
            instanceId=test_resize_volume_instances.instance_id)
        assert(status == "ACTIVE")

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """
        instance_id = test_resize_volume_instances.instance_id
        dbaas = test_resize_volume_instances.dbaas
        #Delete the instance ID created for test if active
        if instance_id is not None:
            status = cls.behavior.get_instance_status(dbaas,
                                                      instanceId=instance_id)
            if cls.behavior.is_instance_active(dbaas, instanceStatus=status):
                dbaas.instances.get(instance_id).delete()

    def test_resize_volume_instance(self):
        """
        Resize the volume of an instance

        """

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_volume(self.instance_id,
                                               self.ResizeUpSizes.lev1)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)
        newVolume = self.dbaas.instances.get(self.instance_id).volume['size']
        self.assertTrue(newVolume == self.ResizeUpSizes.lev1,
                        "Expected new volume size %s: Got %s "
                        % (self.ResizeUpSizes.lev1, newVolume))

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_volume(self.instance_id,
                                               self.ResizeUpSizes.lev2)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)
        newVolume = self.dbaas.instances.get(self.instance_id).volume['size']
        self.assertTrue(newVolume == self.ResizeUpSizes.lev2,
                        "Expected new volume size %s: Got %s "
                        % (self.ResizeUpSizes.lev2, newVolume))

        if self.behavior.is_instance_active(self.dbaas,
                                            instanceId=self.instance_id):
            self.dbaas.instances.resize_volume(self.instance_id,
                                               self.ResizeUpSizes.lev3)

        httpCode = self.behavior.get_last_response_code(self.dbaas)
        self.assertTrue(httpCode == '202',
                        "Create instance failed with code %s" % httpCode)
        status, elapsed_time = self.behavior.wait_for_active(
            self.dbaas,
            instanceId=self.instance_id)
        self.assertEqual(status,
                         'ACTIVE',
                         "Instance fell into state: %s" % status)
        newVolume = self.dbaas.instances.get(self.instance_id).volume['size']
        self.assertTrue(newVolume == self.ResizeUpSizes.lev3,
                        "Expected new volume size %s: Got %s "
                        % (self.ResizeUpSizes.lev3, newVolume))
