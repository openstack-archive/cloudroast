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

import os
import time
import paramiko
import test_repo.database.perf.perf_parser as parser
from test_repo.database.fixtures import DBaaSFixture
from test_repo.database import dbaas_util as testutil


class PerfTest(DBaaSFixture):

    @classmethod
    def setUpClass(cls):
        super(PerfTest, cls).setUpClass()
        cls.client = cls.dbaas_provider.client.reddwarfclient
        cls.fh = open('perf_results.log', "w")

    @classmethod
    def tearDownClass(cls):
        pass

    def connection(self, host, uname, pw):
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(hostname=host,
                          username=uname,
                          password=pw)
        return sshClient

    def run_command(self, conn, command):
        self.fh.write(command + "\n")
        stdin, stdout, stderr = conn.exec_command(command)
        stdin.close()
        for line in stdout.read().splitlines():
            self.fh.write(line + "\n")
        for line in stderr.read().splitlines():
            self.fh.write(line + "\n")

    def test_performance(self):

        #Create the Instance to use
        self.fh.write("Creating the perf instance\n")
        instance_id = testutil.create_perf_instance(self.client)
        instance_hostname = testutil.getInstanceHostname(self.client, instance_id)
        self.fh.write("Connecting to the perf server %s\n" % self.config.dbaas.perf_server)
        conn = self.connection(host=self.config.dbaas.perf_server,
                               uname=self.config.dbaas.perf_server_user,
                               pw=self.config.dbaas.perf_server_password)

        time.sleep(5)
        iuser_name = "perfUser"
        iuser_password = "password2"
        idb_name = "perfDB"

        #Commands
        prep = 'sysbench --test=oltp --oltp-table-size=2000000 --mysql-user=' \
               + iuser_name + ' --mysql-password=' \
               + iuser_password + ' --mysql-host=' \
               + instance_hostname + ' --mysql-database=' \
               + idb_name + ' --mysql-table-engine=innodb prepare'
        runtest = 'sysbench --max-time=3600 --num-threads=124 --max-requests=2000000 --test=oltp --mysql-user=' + \
                  iuser_name + ' --mysql-password=' + \
                  iuser_password + ' --mysql-host=' + \
                  instance_hostname + ' --mysql-database=' + \
                  idb_name + ' run'
        cleanup = 'sysbench --test=oltp --mysql-user=' + \
                  iuser_name + ' --mysql-host=' + \
                  instance_hostname + ' --mysql-password=' + \
                  iuser_password + ' --mysql-database=' + \
                  idb_name + ' cleanup'

        self.run_command(conn, prep)
        self.run_command(conn, runtest)
        self.run_command(conn, cleanup)

        conn.close()

        #Delete the instance
        self.fh.write("Deleting the perf instance\n")
        status = testutil.getInstanceStatus(self.client, instance_id)
        if testutil.isInstanceActive(self.client, instanceStatus=status):
            self.client.instances.get(instance_id).delete()

        self.fh.close()

    def test_xecuteLog2Graphite(self):

        parse = parser.perf_parser('perf_results.log')
        data_dict = parse.parse_log()
        tps = str(data_dict['transactions per sec'])

        # conn = self.connection(host=self.config.database.perf_server,
        #                        uname=self.config.database.perf_server_user,
        #                        pw=self.config.database.perf_server_password)

        # Pull the Graphite endpoint from the config.py conf file reader
        graphiteEndpoint = self.config.dbaas.graphite_endpoint
        graphiteEndpoint = graphiteEndpoint.rstrip("\n")
        geList = graphiteEndpoint.split(".")
        env = None
        # strip out the actual environment so you can update the right graph
        for each in geList:
            if each.startswith('lon'):
                env = 'lon'
            if each.startswith('dfw'):
                env = 'dfw'
            if each.startswith('ord'):
                env = 'ord'
                break

        if env is not None:
        # Put together the string that will post these results to Graphite
            cmd = 'echo "' + env + '.performance.tps  ' \
                  + tps \
                  + ' `date +%s`" | nc ops-n01.qa.ord1.clouddb.rackspace.net 2003 -q 2'
            #self.run_command(conn, cmd)
            #conn.close()
            os.system(cmd)