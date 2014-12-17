"""
Copyright 2014 Rackspace

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

import multiprocessing
from multiprocessing import Queue
import time
from time import time as real_time

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.common.clients.ping import PingClient

from cloudroast.compute.fixtures import ComputeAdminFixture


def live_migrate_server(admin_servers_client,
                        admin_server_behaviors,
                        server_id):
    """Verify the server completes the live migration."""

    name = multiprocessing.current_process().name
    print name, 'Starting live migrate'
    admin_servers_client.live_migrate_server(
        server_id, block_migration=True, disk_over_commit=False)
    admin_server_behaviors.wait_for_server_status(
        server_id, NovaServerStatusTypes.ACTIVE)
    print name, 'Live Migrate Finished'
    time.sleep(10)


def pinger(ip, delta):
    name = multiprocessing.current_process().name
    print name, 'Starting pinging ', ip
    ping_resp = PingClient.ping_until_unreachable(
        ip, timeout=600, interval_time=1)
    if ping_resp is None:
        t0 = real_time()
        PingClient.ping_until_reachable(ip, timeout=60, interval_time=1)
        time_pass = real_time() - t0
        delta.put(time_pass)
    else:
        delta.put(0)


class LiveMigratation(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(LiveMigratation, cls).setUpClass()
        cls.delta = Queue()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.ping_ip = cls.get_ip_address_for_communication(cls.server)
        # Stating Live migrate and Pinger Processes
        live_migrate = multiprocessing.Process(name='live_migrate start',
                                               target=live_migrate_server,
                                               args=(cls.admin_servers_client,
                                                     cls.admin_server_behaviors,
                                                     cls.server.id, ))
        live_migrate.daemon = True
        ping_process = multiprocessing.Process(name='ping worker',
                                               target=pinger,
                                               args=(cls.ping_ip, cls.delta, ))
        ping_process.daemon = False
        ping_process.start()
        time.sleep(1)
        live_migrate.start()

        # Ping wait for live migrate to finish
        print "is ping acting?", ping_process.is_alive()
        live_migrate.join()
        print "is ping acting?", ping_process.is_alive()

        # Finish ping here if live migrate is finished
        print "is live migrate still migrating?", live_migrate.is_alive()
        if live_migrate.is_alive() is False:
            ping_process.terminate()
            print "Stopping ping worker"

    @tags(type='smoke', net='no')
    def test_live_migrate_server(self):
        assert int(self.delta.get()) < 5
