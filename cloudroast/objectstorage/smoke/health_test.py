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
from cloudroast.objectstorage.fixtures import ObjectStorageFixture


class HealthTest(ObjectStorageFixture):
    def test_health_check(self):
        """
        scenario:
            Make a call to the swift healthcheck middleware

        expected result:
            Status code 200
        """
        response = self.client.health_check()
        self.assertEqual(
            response.status_code,
            200,
            msg=("health check call expected status code '200' received"
                 " '{0}'".format(response.status_code)))
