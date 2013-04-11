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

import time
from datetime import datetime
from test_repo.database.fixtures import DBaaSFixture
from test_repo.database import dbaas_util as testutil


class UsageTest(DBaaSFixture):

    #TODO: all smoke testing against this instance ID
    #test_instances = []
    #instance_id = None
    #client = None
    #stability_mode = False
    #instance = None
    gone = True
    ONEMIN = 6
    AHDELAY = 60
    MAXDELTA = 30
    NUM_INSTS = 10
    dateFormat = "%Y-%m-%dT%H:%M:%SZ"
    instance_id_list = []
    starttime_list = []


    @classmethod
    def setUpClass(cls):
        """ Creating instances for usage testing """
        tc_name = "Create Instance"
        inst_pre = 'qe_usage_cls_cafe'
        super(UsageTest, cls).setUpClass()
        cls.client = cls.dbaas_provider.client.reddwarfclient
        cls.mgmt_client = cls.dbaas_provider.mgmt_client.reddwarfclient
        cls.mgmt_client.authenticate()
        for i in range(cls.NUM_INSTS):
            inst_name = inst_pre + "_" + str(i + 1).zfill(2)
            cls.starttime_list.append(datetime.utcnow())
            testInstance = cls.client.instances.create(
                name=inst_name,
                flavor_id=2,
                volume={"size": 2},
                databases=[{"name": "db_name"}])
            httpCode = testutil.get_last_response_code(cls.client)
            if httpCode != '200':
                raise Exception("Create instance failed with code %s" % httpCode)
            #print("Test Create active inst: %s" % testInstance)
            cls.instance_id_list.append(testInstance.id)
            #print("inst id create: [%r] - %r" % (i, cls.instance_id_list[i]))
        testutil.wait_for_all_active(cls.client, cls.instance_id_list)


    @classmethod
    def tearDownClass(cls):
        """ Tearing down: Deleting the instance if in active state """
        status = None
        #Delete the instances created for test if active
        for inst_id in cls.instance_id_list:
            status = testutil.getInstanceStatus(cls.client, inst_id)
            if testutil.isInstanceActive(cls.client, instanceStatus=status):
                #print("tearDownClass - Deleting: %r" %
                #      cls.client.instances.get(inst_id).id)
                cls.client.instances.get(inst_id).delete()

    def test_usage_00_forever(self):
        """ Create one instance and never delete it """
        tc_name = "Usage 00 tests"
        tc_num = 00
        instance_id = self.instance_id_list[0]
        print("inst id create: [%r] - %r" % (tc_num, self.instance_id_list[tc_num]))
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.instance_id_list.remove(instance_id)

    def test_usage_01_delete_after_create(self):
        """ Delete one instance after 10 minutes """
        tc_name = "Usage 01 tests"
        tc_num = 01
        instance_id = self.instance_id_list[0]
        # Sleep for 10 minutes
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # delete the ACTIVE instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_02_resize_flavor_up(self):
        """ Dynamically increase the memory size of an instance """
        tc_name = "Usage 02 tests"
        tc_num = 02
        NEW_FLAVOR_UP = 4
        instance_id = self.instance_id_list[0]
        # insure instance was ACTIVE for 10 minutes
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # resize the instance UP
        rootAction = "reddwarf.instance.modify_flavor"
        response = self.client.instances.resize_instance(instance_id,
                                                         NEW_FLAVOR_UP)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "202",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "202"))
        #wait for it to return to Active
        testutil.wait_for_status(self.client, instance_id, "RESIZE")
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        startTime = datetime.utcnow()
        # AH Event Sent - Check instance as a result of RESIZE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
        self.instance = self.client.instances.get(instance_id)
        self.assertEqual(str(NEW_FLAVOR_UP), self.instance.flavor["id"],
                         "Error: Expected flavor of: %r != Actual flavor: %r"
                         % (str(NEW_FLAVOR_UP), self.instance.flavor["id"]))
        time.sleep(5 * self.ONEMIN)
        # Capture the duration and delete the instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - startTime
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check instance data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_03_resize_flavor_down(self):
        """ Dynamically decrease the memory size of an instance """
        tc_name = "Usage 03 tests"
        tc_num = 03
        NEW_FLAVOR_DOWN = 1
        instance_id = self.instance_id_list[0]
        # insure instance was ACTIVE for 10 minutes
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # resize the instance DOWN
        rootAction = "reddwarf.instance.modify_flavor"
        response = self.client.instances.resize_instance(instance_id,
                                                         NEW_FLAVOR_DOWN)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "202",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "202"))
        testutil.wait_for_status(self.client, instance_id, "RESIZE")
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        startTime = datetime.utcnow()
        # AH Event Sent - Check instance as a result of RESIZE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
        self.instance = self.client.instances.get(instance_id)
        self.assertEqual(str(NEW_FLAVOR_DOWN), self.instance.flavor["id"],
                         "Error: Expected flavor of: %r != Actual flavor: %r"
                         % (str(NEW_FLAVOR_DOWN), self.instance.flavor["id"]))
        time.sleep(5 * self.ONEMIN)
        # Capture the duration and delete the instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - startTime
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check instance data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_04_resize_volume_up(self):
        """ Dynamically increase the storage size of an instance """
        tc_name = "Usage 04 tests"
        tc_num = 04
        NEW_VOLUME = 4
        instance_id = self.instance_id_list[0]
        # insure instance was ACTIVE for 10 minutes
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # resize the volume UP
        rootAction = "reddwarf.instance.modify_volume"
        response = self.client.instances.resize_volume(instance_id,
                                                         NEW_VOLUME)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "202",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "202"))
        testutil.wait_for_status(self.client, instance_id, "RESIZE")
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        startTime = datetime.utcnow()
        # AH Event Sent - Check instance as a result of RESIZE
        time.sleep(self.AHDELAY * 2)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
        self.instance = self.client.instances.get(instance_id)
        self.assertEqual(NEW_VOLUME, self.instance.volume["size"],
                         "Error: Expected flavor of: %r != Actual flavor: %r"
                         % (NEW_VOLUME, self.instance.volume["size"]))
        time.sleep(5 * self.ONEMIN)
        # Capture the duration and delete the instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - startTime
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check instance data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_05_restart_mysql(self):
        """ Restart MySQL then Delete one instance after 10 minutes """
        tc_name = "Usage 05 tests"
        tc_num = 05
        instance_id = self.instance_id_list[0]
        self.client.instances.restart(instance_id)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "202",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "202"))
        # check interim status of REBOOT
        testutil.wait_for_status(self.client, instance_id, "REBOOT")
        # wait for active, ensure time elapsed, record the duration
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # delete the ACTIVE instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_06_resize_reboot_volume_up(self):
        """ Resize the Volume Storage and then reboot, ensure only two AH events """
        tc_name = "Usage 06 tests"
        tc_num = 06
        NEW_VOLUME = 6
        instance_id = self.instance_id_list[0]
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 10 * self.ONEMIN > running_time:
            time.sleep((10 * self.ONEMIN) - running_time)
        # resize the instance UP
        rootAction = "reddwarf.instance.modify_volume"
        response = self.client.instances.resize_volume(instance_id,
                                                       NEW_VOLUME)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "202",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "202"))
        testutil.wait_for_status(self.client, instance_id, "RESIZE")
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        startTime = datetime.utcnow()
        # AH Event Sent - Check instance as a result of RESIZE
        time.sleep(self.AHDELAY * 2)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
        self.instance = self.client.instances.get(instance_id)
        # confirm the new flavor
        self.assertEqual(NEW_VOLUME, self.instance.volume["size"],
                         "Error: Expected flavor of: %r != Actual flavor: %r"
                         % (NEW_VOLUME, self.instance.volume["size"]))
        time.sleep(2 * self.ONEMIN)
        # restart the instance
        self.mgmt_client.management.reboot(instance_id)
        self.assertEqual(str(testutil.get_last_response_code(self.client)), "200",
                         "Error: Resize instance. Unexpected resp code: %r != %r"
                         % (str(testutil.get_last_response_code(self.client)), "200"))
        testutil.wait_for_status(self.client, instance_id, "REBOOT")
        status, elapsed_time = testutil.waitForActive(self.client,
                                                      instanceId=instance_id)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id, status, elapsed_time))
        time.sleep(2 * self.ONEMIN)
        # Capture the duration and delete the instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - startTime
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check instance data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_07_identical_create(self):
        """ Create two identical instances, ensure separate AH events """
        tc_name = "Usage 07 tests"
        tc_num = 07
        instance_id = self.instance_id_list[0]
        inst_name = self.client.instances.get(instance_id).name
        # Create duplicate instance
        startTime1 = datetime.utcnow()
        instance_id1, elapsed_time = testutil.create_active_instance(
            self.client,
            name=inst_name,
            flavor_id=2,
            volume={"size": 2},
            databases=[{"name": "db_name"}])
        httpCode = testutil.get_last_response_code(self.client)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id,
                                self.client.instances.get(instance_id).status,
                                elapsed_time))
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 3 * self.ONEMIN > running_time:
            time.sleep((3 * self.ONEMIN) - running_time)
        self.client.instances.get(instance_id1).delete()
        rootAction = "reddwarf.instance.delete"
        duration1 = datetime.utcnow() - startTime1
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList1 = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id1)
        single_event1 = [event for event in AHEventsList1
                         if event.rootAction == rootAction].pop()
        self.assertEqual(single_event1.resourceId, instance_id1,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event1.resourceId, instance_id1))
        testutil.valid_duration(duration1, single_event1, self.dateFormat)
        # delete the ACTIVE instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def test_usage_08_duplicate_create(self):
        """ Delete one instance then recreate it, ensure separate AH events """
        tc_name = "Usage 08 tests"
        tc_num = 8
        instance_id = self.instance_id_list[0]
        inst_name = self.client.instances.get(instance_id).name
        # delete the existing instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
        # now create an exact duplicate instance
        startTime1 = datetime.utcnow()
        instance_id1, elapsed_time = testutil.create_active_instance(
            self.client,
            name=inst_name,
            flavor_id=2,
            volume={"size": 2},
            databases=[{"name": "db_name"}])
        httpCode = testutil.get_last_response_code(self.client)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        self.fixture_log.debug("Inst: %r is: %r after: %r seconds" %
                               (instance_id,
                                self.client.instances.get(instance_id).status,
                                elapsed_time))
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 5 * self.ONEMIN > running_time:
            time.sleep((5 * self.ONEMIN) - running_time)
        # delete the ACTIVE instance
        if testutil.getInstanceStatus(self.client, instance_id1) == "ACTIVE":
            self.client.instances.get(instance_id1).delete()
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        rootAction = "reddwarf.instance.delete"
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id1)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id1,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id1))
        testutil.valid_duration(duration, single_event, self.dateFormat)

    def _usage_09_exists(self):
        """ Delete one instance after enough time for exists event """
        tc_name = "Usage 01 tests"
        tc_num = 01
        instance_id = self.instance_id_list[0]
        running_time = (datetime.utcnow() - self.starttime_list[tc_num]).seconds
        if 60 * self.ONEMIN > running_time:
            time.sleep((60 * self.ONEMIN) - running_time)
            # delete the ACTIVE instance
        if testutil.getInstanceStatus(self.client, instance_id) == "ACTIVE":
            self.client.instances.get(instance_id).delete()
            self.instance_id_list.remove(instance_id)
        duration = datetime.utcnow() - self.starttime_list[tc_num]
        rootAction = "reddwarf.instance.exists"
        # AH Event Sent - Check AH data data AFTER the DELETE
        time.sleep(self.AHDELAY)
        AHEventsList = self.dbaas_atomhopper_provider.events_by_resourceId(instance_id)
        single_event = [event for event in AHEventsList
                        if event.rootAction == rootAction].pop()
        self.assertEqual(single_event.resourceId, instance_id,
                         'AH resourceID:%r != created instanceID:%r'
                         % (single_event.resourceId, instance_id))
        testutil.valid_duration(duration, single_event, self.dateFormat)
