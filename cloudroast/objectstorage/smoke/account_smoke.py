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

STATUS_CODE_MSG = ("{method} expected status code {expected}"
                   " received status code {received}")
CONTAINER_NAME = 'account_smoke_test_container'
C_TYPE_TEXT = 'text/plain; charset=utf-8'
C_TYPE_JSON = 'application/json; charset=utf-8'
C_TYPE_XML = 'application/xml; charset=utf-8'
HTTP_OK = 200


class AccountSmokeTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(AccountSmokeTest, cls).setUpClass()

        cls.container_names = ['a_{0}'.format(CONTAINER_NAME),
                               'b_{0}'.format(CONTAINER_NAME),
                               'c_{0}'.format(CONTAINER_NAME)]

        for container_name in cls.container_names:
            cls.client.create_container(container_name)

    @classmethod
    def tearDownClass(cls):
        super(AccountSmokeTest, cls).setUpClass()
        for container_name in cls.container_names:
            cls.behaviors.force_delete_containers([container_name])

    def test_container_list(self):
        response = self.client.list_containers()

        method = "list containers"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_format_json_query_parameter(self):
        format_ = {"format": "json"}
        response = self.client.list_containers(params=format_)

        method = "list containers using content-type json"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_JSON
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_format_xml_query_parameter(self):
        format_ = {"format": "xml"}
        response = self.client.list_containers(params=format_)

        method = "list containers using content-type xml"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_XML
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_accept_header(self):
        headers = {"Accept": "*/*"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept */*"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_text_accept_header(self):
        headers = {"Accept": "text/plain"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept text/plain"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_json_accept_header(self):
        headers = {"Accept": "application/json"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept application/json"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_JSON
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_xml_accept_header(self):
        headers = {"Accept": "application/xml"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept application/xml"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_XML
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_limit_query_parameter(self):
        limit = {"limit": "10"}
        response = self.client.list_containers(params=limit)

        method = "list containers using limit query parameter"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_marker_query_parameter(self):
        marker = {"marker": "a"}
        response = self.client.list_containers(params=marker)

        method = "list containers using marker query parameter"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_limit_and_marker_query_parameters(self):
        limit_marker = {"limit": "3", "marker": "a"}
        response = self.client.list_containers(params=limit_marker)

        method = "list containers using limit and marker query parameters"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_limit_marker_format_json(self):
        limit_marker_format = {"limit": "3", "marker": "a", "format": "json"}
        response = self.client.list_containers(params=limit_marker_format)

        method = "list containers using limit, marker, and format json query" \
            " parameters"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_JSON
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_container_list_with_limit_marker_format_xml(self):
        limit_marker_format = {"limit": "3", "marker": "a", "format": "xml"}
        response = self.client.list_containers(params=limit_marker_format)

        method = "list containers using limit, marker, and format xml query" \
            " parameters"
        expected = HTTP_OK
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        expected = C_TYPE_XML
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'x-account-object-count' header value expected: {0} received:"
            " {1}".format(expected, received))

    def test_metadata_retrieval_with_existing_account(self):
        response = self.client.get_account_metadata()

        method = "account metadata retrieval"
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        self.assertIn('x-account-bytes-used', response.headers)

        self.assertIn('date', response.headers)

        self.assertIn('x-timestamp', response.headers)

        self.assertIn('x-account-container-count', response.headers)

        self.assertIn('x-account-object-count', response.headers)

        expected = 'bytes'
        received = response.headers.get('accept-ranges')
        self.assertEqual(
            expected,
            received,
            msg="'accept-ranges' header value expected: {0} received"
            " {1}".format(expected, received))

        expected = 0
        received = int(response.headers.get('content-length', 0))
        self.assertEqual(
            expected,
            received,
            msg="'content-length' header value expected: {0} received:"
            " {1}".format(expected, received))

        expected = C_TYPE_TEXT
        received = response.headers.get('content-type')
        self.assertEqual(
            expected,
            received,
            msg="'content-type' header value expected: {0} received:"
            " {1}".format(expected, received))
