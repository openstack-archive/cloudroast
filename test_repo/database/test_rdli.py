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


# from proboscis.asserts import assert_false
# from proboscis import test
from proboscis import TestPlan

def load_tests(loader, config=None, stuff=None):

    # @test
    # def test_hi():
    #     assert_false("hi")

    from reddwarf.tests.config import CONFIG
    CONFIG.load_from_file("/Users/nath5505/dbaas/test-qa.conf")
    from proboscis.decorators import DEFAULT_REGISTRY
    plan = TestPlan.create_from_registry(DEFAULT_REGISTRY)
    return plan.create_test_suite(config, loader)

