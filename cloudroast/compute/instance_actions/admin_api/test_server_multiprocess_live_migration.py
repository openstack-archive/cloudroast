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


def test_live_migrate_server(admin_servers_client, admin_server_behaviors,
                             server_id, status_timeout):
    """Verify the server completes the live migration."""
    admin_servers_client.live_migrate_server(
        server_id, block_migration=True, disk_over_commit=False)
    admin_server_behaviors.wait_for_server_status(
        server_id, NovaServerStatusTypes.ACTIVE)
    # Make sure we give additional time to restore the connectivity
    # in case missing after the server reached active status
    time.sleep(status_timeout)


def pinger(ip, delta, connection_timeout):
    """
    Pinger function which is responsible for connectivity check starting before
    migrate starts and finishing 10 seconds after migrate finished
    If we do not get connectivity lost at all we put 0 for the delta
    otherwise we calculate the delta time without connectivity
    """
    ping_resp = PingClient.ping_until_unreachable(
        ip, timeout=connection_timeout, interval_time=1)
    if ping_resp is None:
        t0 = real_time()
        ping_reach = PingClient.ping_until_reachable(
            ip, timeout=connection_timeout, interval_time=1)
        time_pass = real_time() - t0
        print time_pass
        delta.put(time_pass)
    else:
        delta.put(0)


class LiveMigratation(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(LiveMigratation, cls).setUpClass()
        cls.fixture_log.debug("Multiprocessing Live Migrate Test started")
        cls.delta = Queue()
        cls.ping_timeout = cls.servers_config.connection_timeout
        cls.status_timeout = cls.servers_config.server_status_interval
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)
        cls.ping_ip = cls.get_ip_address_for_communication(cls.server)
        # Define Live migrate and Pinger Processes
        live_migrate = multiprocessing.Process(name='live_migrate start',
                                               target=test_live_migrate_server,
                                               args=(cls.admin_servers_client,
                                                     cls.admin_server_behaviors,
                                                     cls.server.id,
                                                     cls.status_timeout))

        ping_process = multiprocessing.Process(name='ping worker',
                                               target=pinger,
                                               args=(cls.ping_ip,
                                                     cls.delta,
                                                     cls.ping_timeout))
        # Starting Live migrate and Pinger Processes
        ping_process.daemon = False
        ping_process.start()
        time.sleep(1)
        live_migrate.start()

        # Join in order ping process to wait for live migrate to finish
        live_migrate.join()

        # Finish ping here if live migrate is finished
        cls.fixture_log.debug("if live migrate still migrating we will stop"
                              "the ping worker")
        if live_migrate.is_alive() is False:
            ping_process.terminate()
            cls.fixture_log.debug("Stopping ping worker")

    @tags(type='smoke', net='no')
    def test_live_migrate_server(self):
        """
        If delta was never set that means the instance never get the
        connectivity back after active status was reached, if the assertion
        fails that means we eventually get back the connectivity but not in
        the allocated ping timeout
        """
        if self.delta.empty():
            self.fail("We never get the connectivity back after live migrate")
        else:
            assert int(self.delta.get()) < self.ping_timeout
