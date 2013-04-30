from test_repo.objectstorage.fixtures import ObjectStorageFixture

STATUS_CODE_MSG = '{method} expected status code {expected}' \
    ' received status code {received}'
HDR_MSG = 'expected header {header} received {received}'
CONTENT_TYPE_MSG = 'expected content type {expected}' \
    ' received {received}'


class AccountSmokeTest(ObjectStorageFixture):
    def test_view_account_metada(self):
        response = self.client.retrieve_account_metadata()

        method = 'retrieve account metadata'
        expected = 204
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_non_empty_account(self):
        response = self.client.list_containers()

        method = 'list containers non empty account'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_format_json_query_parameter(self):
        format_ = {'format': 'json'}
        response = self.client.list_containers(params=format_)

        method = 'list containers with format json query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_format_xml_query_parameter(self):
        format_ = {'format': 'xml'}
        response = self.client.list_containers(params=format_)

        method = 'list containers with format xml query parameter'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_accept_header(self):
        headers = {'Accept': '*/*'}
        response = self.client.list_containers(headers=headers)

        method = 'list containers with accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_text_accept_header(self):
        headers = {'Accept': 'text/plain'}
        response = self.client.list_containers(headers=headers)

        method = 'list containers with text accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_json_accept_header(self):
        headers = {'Accept': 'application/json'}
        response = self.client.list_containers(headers=headers)

        method = 'list containers with json accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_application_xml_accept_header(self):
        headers = {'Accept': 'application/xml'}
        response = self.client.list_containers(headers=headers)

        method = 'list containers with application/xml accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_text_xml_accept_header(self):
        headers = {'Accept': 'text/xml'}
        response = self.client.list_containers(headers=headers)

        method = 'list containers with text/xml accept header'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    """4.1.1.2. Controlling a Large List of Containers"""
    def test_container_list_with_limit_query_parameter(self):
        limit = {'limit': '10'}
        response = self.client.list_containers(params=limit)

        method = 'list containers with limit query paramater'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_marker_query_parameter(self):
        marker = {'marker': 'a'}
        response = self.client.list_containers(params=marker)

        method = 'list containers with marker query paramater'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_limit_and_marker_query_parameters(self):
        limit_marker = {'limit': '3', 'marker': 'a'}
        response = self.client.list_containers(params=limit_marker)

        method = 'list containers with limit and marker query paramaters'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_limit_marker_format_json(self):
        limit_marker_format = {'limit': '3', 'marker': 'a', 'format': 'json'}
        response = self.client.list_containers(params=limit_marker_format)

        method = 'list containers with limit, marker and format' \
            ' query paramaters'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))

    def test_container_list_with_limit_marker_format_xml(self):
        limit_marker_format = {'limit': '3', 'marker': 'a', 'format': 'xml'}
        response = self.client.list_containers(params=limit_marker_format)

        method = 'list containers with limit, marker and format xml' \
            ' query paramaters'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method, expected=expected, received=str(received)))
