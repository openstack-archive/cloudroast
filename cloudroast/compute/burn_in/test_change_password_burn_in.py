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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import ComputeHypervisors
from cloudcafe.compute.common.types import NovaServerStatusTypes as \
    ServerStates
from cloudcafe.compute.config import ComputeConfig
from cloudroast.compute.fixtures import ComputeFixture


compute_config = ComputeConfig()
hypervisor = compute_config.hypervisor.lower()


@unittest.skipIf(
    hypervisor in [ComputeHypervisors.KVM, ComputeHypervisors.QEMU],
    'Change password not supported in current configuration.')
class ChangePasswordBurnIn(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(ChangePasswordBurnIn, cls).setUpClass()
        resp = cls.server_behaviors.create_active_server()
        cls.server = resp.entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='burn-in', net='no')
    def test_change_password(self):
        new_password = "p@ssw0Rd"

        self.servers_client.change_password(self.server.id, new_password)
        self.server_behaviors.wait_for_server_status(self.server.id,
                                                     ServerStates.ACTIVE)
