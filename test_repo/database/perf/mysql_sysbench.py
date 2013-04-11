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


class PerfTest(DBaaSFixture):

    @classmethod
    def setUpClass(cls):
        super(PerfTest, cls).setUpClass()
        cls.client = cls.client.reddwarfclient
        cls.fh = open(cls.dbaas_config.path_to_perf_log, "w")

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
        instance_id = self.behavior.create_perf_instance(self.client)
        instance_hostname = self.behavior.get_instance_hostname(
            self.client,
            instance_id)
        self.fh.write("Connecting to the perf server %s\n" %
                      self.config.dbaas.perf_server)
        conn = self.connection(host=self.config.dbaas.perf_server,
                               uname=self.config.dbaas.perf_server_user,
                               pw=self.config.dbaas.perf_server_password)

        time.sleep(5)
        iuser_name = "perfUser"
        iuser_password = "password2"
        idb_name = "perfDB"

        #Commands
        prep = "{0}{1}{2}{3}{4}{5}{6}{7}{8}".format(
            'sysbench --test=oltp --oltp-table-size=2000000 --mysql-user=',
            iuser_name,
            ' --mysql-password=',
            iuser_password,
            ' --mysql-host=',
            instance_hostname,
            ' --mysql-database=',
            idb_name,
            ' --mysql-table-engine=innodb prepare')
        runtest = "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
            'sysbench --max-time=3600 --num-threads=124 ',
            '--max-requests=2000000 --test=oltp --mysql-user=',
            iuser_name,
            ' --mysql-password=',
            iuser_password,
            ' --mysql-host=',
            instance_hostname,
            ' --mysql-database=',
            idb_name,
            ' run')
        cleanup = "{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}".format(
            'sysbench --test=oltp --mysql-user=',
            iuser_name,
            ' --mysql-host=',
            instance_hostname,
            ' --mysql-password=',
            iuser_password,
            ' --mysql-database=',
            idb_name,
            ' cleanup')

        self.run_command(conn, prep)
        self.run_command(conn, runtest)
        self.run_command(conn, cleanup)

        conn.close()

        #Delete the instance
        self.fh.write("Deleting the perf instance\n")
        status = self.behavior.get_instance_status(self.client, instance_id)
        if self.behavior.is_instance_active(self.client,
                                            instanceStatus=status):
            self.client.instances.get(instance_id).delete()

        self.fh.close()

    def test_xecuteLog2Graphite(self):

        parse = parser.perf_parser('perf_results.log')
        data_dict = parse.parse_log()
        tps = str(data_dict['transactions per sec'])

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
            cmd = "{0}{1}{2}{3}{4}{5}".format(
                'echo "',
                env,
                '.performance.tps  ',
                tps,
                ' `date +%s`" '
                '| nc ops-n01.qa.ord1.clouddb.rackspace.net 2003 -q 2')
            os.system(cmd)
