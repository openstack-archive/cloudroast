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
from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture

from cloudcafe.compute.datasets import ComputeDatasets
from cloudcafe.compute.common.exceptions import Forbidden

from cloudroast.compute.fixtures import ServerFromImageFixture
from cloudroast.compute.fixtures import ServerFromVolumeV1Fixture
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class FlavorsNegativeTests(object):

    @data_driven_test(ComputeDatasets.flavors())
    def ddtest_resize_flavors(self, flavor):
        """Try to resize with all flavor from general list flavors"""
        with self.assertRaises(Forbidden):
            self.servers_client.resize(self.server.id, self.flavor_ref_alt)


@DataDrivenFixture
class ServerFromImageResizeNegativeFlavorTests(ServerFromImageFixture,
                                               FlavorsNegativeTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromImageResizeNegativeFlavorTests, cls).setUpClass()
        cls.create_server()


@DataDrivenFixture
class ServerFromVolumeV1ResizeNegativeFlavorTests(ServerFromVolumeV2Fixture,
                                                  FlavorsNegativeTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV1ResizeNegativeFlavorTests, cls).setUpClass()
        cls.create_server()


@DataDrivenFixture
class ServerFromVolumeV2ResizeNegativeFlavorTests(ServerFromVolumeV1Fixture,
                                                  FlavorsNegativeTests):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2ResizeNegativeFlavorTests, cls).setUpClass()
        cls.create_server()
