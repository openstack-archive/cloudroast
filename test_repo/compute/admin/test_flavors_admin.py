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

from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeAdminFixture

class FlavorsAdminTest(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(FlavorsAdminTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(FlavorsAdminTest, cls).tearDownClass()

    def test_create_delete_flavors(self):
        self.admin_flavors_client.create_flavor(name='test2', ram='128', vcpus='1',
                                                disk='10', id='99', is_public=True)
        self.admin_flavors_client.delete_flavor('99')