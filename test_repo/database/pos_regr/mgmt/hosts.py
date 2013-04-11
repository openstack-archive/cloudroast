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


class test_hosts(DBaaSFixture):
    instance_id = None
    dbaas = None

    @classmethod
    def setUpClass(cls):
        """
        Creating an instance for database testing

        """
        super(test_hosts, cls).setUpClass()
        cls.mgmt_dbaas = cls.dbaas_provider.mgmt_client.reddwarfclient
        cls.mgmt_dbaas.authenticate()

        NAME = "qe-mgmt-hosts-testing"
        FLAVOR = 1
        VOLUME = 1
        instance = test_hosts.mgmt_dbaas.instances.create(
            name=NAME,
            flavor_id=FLAVOR,
            volume={"size": VOLUME})
        httpCode = cls.behavior.get_last_response_code(test_hosts.mgmt_dbaas)
        if httpCode != '200':
            raise Exception("Create instance failed with code %s" % httpCode)
        cls.instance_id = instance.id
        #status = instance.status
        cls.behavior.wait_for_active(test_hosts.mgmt_dbaas,
                                     instanceId=test_hosts.instance_id)

        instance_details = test_hosts.mgmt_dbaas.management.show(instance)
        httpCode = cls.behavior.get_last_response_code(test_hosts.mgmt_dbaas)
        if httpCode != '200':
            raise Exception("List instance details failed with code %s" %
                            httpCode)
        cls.host = instance_details.server["host"]

    @classmethod
    def tearDownClass(cls):
        """
        Tearing down: Deleting the instance if in active state

        """

        #Delete the instance ID created for test if active
        if test_hosts.instance_id is not None:
            status = cls.behavior.get_instance_status(
                test_hosts.mgmt_dbaas,
                instanceId=test_hosts.instance_id)
            if cls.behavior.is_instance_active(test_hosts.mgmt_dbaas,
                                               instanceStatus=status):
                test_hosts.mgmt_dbaas.instances.get(
                    test_hosts.instance_id).delete()

    def test_list_all_compute_hosts(self):
        try:
            _hosts = self.mgmt_dbaas.hosts.index()
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List all compute hosts failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        self.assertIs(type(_hosts), list,
                      "Expected %r , Actual %r" %
                      (list, type(_hosts)))
        for host in _hosts:
            self.fixture_log.debug("\tHost: %r" %
                                   host)
            self.fixture_log.debug("\t\tHost name: %r" %
                                   host.name)
            self.fixture_log.debug("\t\tHost instance count: %r" %
                                   host.instanceCount)
            self.assertIs(type(host.name), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(host.name)))
            self.assertIs(type(host.instanceCount), int,
                          "Expected %r , Actual %r" %
                          (int, type(host.instanceCount)))

    def test_list_all_instances_for_host(self):
        try:
            _host_details = self.mgmt_dbaas.hosts.get(self.host)
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List all instances for a host failed with code %s"
                            % httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        self.fixture_log.debug("\tHost details: %r" %
                               _host_details)
        self.fixture_log.debug("\t\tHost name: %r" %
                               _host_details.name)
        self.fixture_log.debug("\t\tHost total RAM: %r" %
                               _host_details.totalRAM)
        self.fixture_log.debug("\t\tHost used RAM: %r" %
                               _host_details.usedRAM)
        self.fixture_log.debug("\t\tHost percent used: %r" %
                               _host_details.percentUsed)
        self.fixture_log.debug("\t\tHost instances: %r" %
                               _host_details.instances)
        self.assertIs(type(_host_details.name), unicode,
                      "Expected %r , Actual %r" %
                      (unicode, type(_host_details.name)))
        self.assertIs(type(_host_details.totalRAM), int,
                      "Expected %r , Actual %r" %
                      (int, type(_host_details.totalRAM)))
        self.assertIs(type(_host_details.usedRAM), int,
                      "Expected %r , Actual %r" %
                      (int, type(_host_details.usedRAM)))
        self.assertIs(type(_host_details.percentUsed), int,
                      "Expected %r , Actual %r" %
                      (int, type(_host_details.percentUsed)))
        instance_found = False
        for inst in _host_details.instances:
            self.fixture_log.debug("\tInstance: %r" %
                                   inst)
            self.fixture_log.debug("\t\tInstance id: %r" %
                                   (inst["id"]))
            self.fixture_log.debug("\t\tInstance name: %r" %
                                   (inst["name"]))
            self.fixture_log.debug("\t\tInstance server ID: %r" %
                                   (inst["server_id"]))
            self.fixture_log.debug("\t\tInstance status: %r" %
                                   (inst["status"]))
            self.fixture_log.debug("\t\tInstance tenant ID: %r" %
                                   (inst["tenant_id"]))
            self.assertIs(type(inst), dict,
                          "Expected %r , Actual %r" %
                          (dict, type(inst)))
            self.assertIs(type(inst["id"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["id"])))
            self.assertIs(type(inst["name"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["name"])))
            self.assertIs(type(inst["server_id"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["server_id"])))
            self.assertIs(type(inst["status"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["status"])))
            self.assertIs(type(inst["tenant_id"]), unicode,
                          "Expected %r , Actual %r" %
                          (unicode, type(inst["tenant_id"])))
            if not instance_found:
                if inst["id"] == self.instance_id:
                    instance_found = True
                    self.fixture_log.debug("\t\tTest instance %r found!" %
                                           self.instance_id)
        self.assertTrue(instance_found,
                        "\t\tError: test instance %r was not found!" %
                        self.instance_id)

        # find out number of instances for host
        try:
            _hosts = self.mgmt_dbaas.hosts.index()
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '200',
                            "List all compute hosts failed with code %s" %
                            httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise

        self.assertIs(type(_hosts), list,
                      "Expected %r , Actual %r" %
                      (list, type(_hosts)))
        instance_count = 0
        for host in _hosts:
            if host.name == _host_details.name:
                instance_count = host.instanceCount
                break
        self.fixture_log.debug("\tHost %r has %r instances" %
                               (_host_details.name,
                                len(_host_details.instances)))
        self.assertEqual(len(_host_details.instances),
                         instance_count,
                         "Expected inst count %r , Actual inst count %r" %
                         (instance_count, len(_host_details.instances)))

    def test_update_all_instances_on_host(self):
        # TODO: To property test this call, a new sneaky pete image has to be
        #       available in the apt repo to update the instances with.
        #       If not available, instances will not be updated.
        # This test case will only verify the requested call's response code,
        # and nothing more for now.
        try:
            self.mgmt_dbaas.hosts.update_all(self.host)
            httpCode = self.behavior.get_last_response_code(self.mgmt_dbaas)
            self.assertTrue(httpCode == '202',
                            "Update all instances on host failed with code %s"
                            % httpCode)
            self.fixture_log.debug("\tUpdate all instances on host code: %r" %
                                   httpCode)
        except Exception as e:
            self.fixture_log.debug("\tException: %r" % e)
            raise
