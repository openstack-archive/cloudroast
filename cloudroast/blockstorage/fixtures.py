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

from cafe.drivers.unittest.fixtures import BaseTestFixture


class BaseBlockstorageTestFixture(BaseTestFixture):

    @staticmethod
    def add_cleanup(obj_ref, function, *args, **kwargs):
        """ Attempts to use the appropriate add cleanup method.

        Automatically used addClassCleanup if called from a classmethod,
        or addCleanup if called from an instance method"""
        try:
            obj_ref.addCleanup(function, *args, **kwargs)
        except TypeError:
            obj_ref.addClassCleanup(function, *args, **kwargs)

    def assertExactResponseStatus(
            self, requests_response_object, expected_status, msg=None):
        std_msg = "Received status code {0} != {1}".format(
            requests_response_object.status_code, expected_status)

        if str(expected_status) != str(requests_response_object.status_code):
            self.fail(self._formatMessage(msg, std_msg))

    def assertResponseStatusInRange(
            self, requests_response_object, expected_status_range_start=200,
            expected_status_range_end=299, msg=None):
        """Note: Both start and end range are inclusive"""

        std_msg = "Received status code {0} not in range {1}-{2}".format(
            requests_response_object.status_code, expected_status_range_start,
            expected_status_range_end)

        expected_range = [str(i) for i in range(
            expected_status_range_start, expected_status_range_end + 1)]
        response_code = str(requests_response_object.status_code).lower()

        if response_code not in expected_range:
            self.fail(self._formatMessage(msg, std_msg))

    def assertResponseIsDeserialized(self, requests_response_object, msg=None):
        if requests_response_object.entity is None:
                std_msg = "Request failed, unable to deserialize response"
                self.fail(self._formatMessage(msg, std_msg))

    def assertResponseDeserializedAndOk(
            self, requests_response_object, msg=None):
        if not requests_response_object.ok:
            std_msg = "Received status code {0} not in range 200-299".format(
                requests_response_object.status_code)
            self.fail(self._formatMessage(msg, std_msg))
        self.assertResponseIsDeserialized(requests_response_object, msg=msg)
