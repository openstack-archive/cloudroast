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

import unittest

import IPy

from cafe.drivers.unittest.decorators import tags
from cloudcafe.networking.networks.common.constants \
    import NeutronResponseCodes
from cloudcafe.networking.networks.config import NetworkingSecondUserConfig
from cloudroast.networking.networks.fixtures import NetworkingAPIFixture


class SubnetsGetTest(NetworkingAPIFixture):

    @tags(type='smoke', rbac='observer')
    def test_list_subnets(self):
        """
        @summary: Get subnets test (list)
        """
        resp = self.subnets.behaviors.list_subnets()

        # Fail the test if any failure is found
        self.assertFalse(resp.failures)

    @tags(type='negative', rbac='observer', quark='yes')
    def test_hidden_subnets_public_private(self):
        """
        @summary: Testing public and service net (private) networks are NOT
            shown in the subnets list response
        """

        msg = '(negative) Listing subnets on public network'
        resp = self.subnets.behaviors.list_subnets(
            network_id=self.public_network_id, raise_exception=False)

        # HTTP 200 response expected with empty entity list
        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.LIST_SUBNETS, msg=msg,
            entity=[])

        msg = '(negative) Listing subnets on service network'
        resp = self.subnets.behaviors.list_subnets(
            network_id=self.service_network_id, raise_exception=False)

        self.assertNegativeResponse(
            resp=resp, status_code=NeutronResponseCodes.LIST_SUBNETS, msg=msg,
            entity=[])
