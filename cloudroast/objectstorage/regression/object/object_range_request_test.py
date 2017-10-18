"""
Copyright 2017 Rackspace

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

from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.objectstorage.objectstorage_api.common.constants import \
    Constants
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectDatasetList


CONTAINER_NAME = 'object_range_request_test_container'
CONTENT_MSG = 'expected {0} in the content body. received {1}'
CONTENT_TYPE_MSG = 'expected content_type {0} received {1}'
MULTIPART = "multipart/byteranges;boundary="


@DataDrivenFixture
class ObjectRangeRequestTest(ObjectStorageFixture):

    def setUp(self):
        super(ObjectRangeRequestTest, self).setUp()
        self.object_name = Constants.VALID_OBJECT_NAME

    def get_boundary(self, content_type_header):
        """
        returns the boundary from the multipart content-type header:
        "multipart/byteranges;boundary=examplemsgboundary"
        """
        boundary = ''
        header_tokens = content_type_header.split(";boundary=")

        try:
            boundary = header_tokens[1]
        except IndexError, error:
            self.fail(
                msg='content-type header: "{0}" could not be parsed.'
                    ' error: {1}'.format(
                        str(content_type_header),
                        error))

        return boundary

    def parse_msg(self, content, boundary):
        """
        splits the content body using the boundary returned in the
        multipart content-type header and returns the data
        """
        multipart_content = {}

        try:
            split_body = content.split("--{0}".format(boundary))
        except AttributeError, error:
            self.fail("body cannot be split on boundary."
                      " error: {0}".format(error))

        i = 1
        end = len(split_body) - 1

        try:
            while i < end:
                multipart_content['value{0}'.format(i)] = \
                    split_body[i].split('\r\n\r\n')[1].strip('\r\n')
                i += 1
        except AttributeError, error:
            self.error("error parsing content. error: {0}".format(error))

        return multipart_content

    @data_driven_test(ObjectDatasetList())
    def ddtest_basic_object_range_request(self, object_type, generate_object):
        """
        Scenario:
            Perform a get with various range request headers.

        Expected Results:
            The data returned should be within the range specified.
        """
        container_name = self.create_temp_container(descriptor=CONTAINER_NAME)
        # Check the object type, if it's a DLO/SLO we need to generate more
        # data due to minimum segment lengths.
        if object_type == "standard":
            obj_data = "grok_one drok_two"
        else:
            obj_data = ''.join(["grok_{0}/".format(x) for x in range(
                1000000)])

        generate_object(container_name, self.object_name, data=obj_data)

        headers = {'Range': 'bytes=-3'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        if object_type == "standard":
            self.assertEqual(response.content, "two",
                             msg=CONTENT_MSG.format("two",
                                                    str(response.content)))
        else:
            self.assertEqual(response.content, "99/",
                             msg=CONTENT_MSG.format("99/",
                                                    str(response.content)))

        headers = {'Range': 'bytes=0-3'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        # In this case the content should be the same for all object types
        self.assertEqual(response.content, "grok",
                         msg=CONTENT_MSG.format("grok", str(response.content)))

        headers = {'Range': 'bytes=4-4'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        # In this case the content should be the same for all object types
        self.assertEqual(response.content, "_",
                         msg=CONTENT_MSG.format("_", str(response.content)))

        # Splitting up the requests based on object type due to the size of
        # DLOs and SLOs making this case difficult to handle otherwise.
        if object_type == "standard":
            headers = {'Range': 'bytes=9-'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(response.content, "drok_two",
                             msg=CONTENT_MSG.format("drok_two",
                                                    str(response.content)))
        else:
            headers = {'Range': 'bytes=11888878-'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(response.content, "grok_999999/",
                             msg=CONTENT_MSG.format("grok_999999/",
                                                    str(response.content)))

    @unittest.skip('JIRA Bug https://jira.rax.io/browse/STORDEV-189')
    @data_driven_test(ObjectDatasetList())
    def ddtest_multi_part_range_request(self, object_type, generate_object):
        """
        Scenario:
            Perform a get with various multi-part range request headers.

        Expected Results:
            The data returned should be a multi-part message within the
            range specified.
            The content type should be "multipart/byteranges" and should
            contain a delimiter.
            the body should be separated by this delimiter and the data
            in the body should be in order.
        """
        container_name = self.create_temp_container(descriptor=CONTAINER_NAME)
        # Check the object type, if it's a DLO/SLO we need to generate more
        # data due to minimum segment lengths.
        if object_type == "standard":
            obj_data = "grok_one drok_two"
        else:
            obj_data = ''.join(["grok_{0}/".format(x) for x in range(
                1000000)])

        generate_object(container_name, self.object_name, data=obj_data)

        headers = {'Range': 'bytes=0-3,-3'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        content_type = response.headers.get('content-type')

        self.assertTrue(str(content_type).startswith(MULTIPART))

        boundary = self.get_boundary(content_type)

        self.assertNotEqual(boundary, '')

        parsed_content = self.parse_msg(response.content, boundary)

        if object_type == "standard":
            self.assertEqual("grok", parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
            self.assertEqual("two", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("two",
                                                    str(response.content)))
        else:
            self.assertEqual("grok", parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
            # This assertion will fail whenever the DLO/SLO bug for multipart
            # range requests is resolved (JIRA STORDEV-189).
            self.assertEqual("two", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("two",
                                                    str(response.content)))

        headers = {'Range': 'bytes=-3,0-3'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        content_type = response.headers.get('content-type')

        self.assertTrue(str(content_type).startswith(MULTIPART))

        boundary = self.get_boundary(content_type)

        self.assertNotEqual(boundary, '')

        parsed_content = self.parse_msg(response.content, boundary)

        if object_type == "standard":
            self.assertEqual("two", parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("two",
                                                    str(response.content)))
            self.assertEqual("grok", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
        else:
            # This assertion will fail whenever the DLO/SLO bug for multipart
            # range requests is resolved (JIRA STORDEV-189).
            self.assertEqual("two", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("two",
                                                    str(response.content)))
            self.assertEqual("grok", parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))

        headers = {'Range': 'bytes=9-,0-3'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        content_type = response.headers.get('content-type')

        self.assertTrue(str(content_type).startswith(MULTIPART))

        boundary = self.get_boundary(content_type)

        self.assertNotEqual(boundary, '')

        parsed_content = self.parse_msg(response.content, boundary)

        if object_type == "standard":
            self.assertEqual("drok_two",
                             parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("drok_two",
                                                    str(response.content)))
            self.assertEqual("grok", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
        else:
            # This assertion will fail whenever the DLO/SLO bug for multipart
            # range requests is resolved (JIRA STORDEV-189).
            self.assertEqual("drok_two",
                             parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("drok_two",
                                                    str(response.content)))
            self.assertEqual("grok", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))

        headers = {'Range': 'bytes=0-3,5-7,9-12'}
        response = self.client.get_object(container_name,
                                          self.object_name,
                                          headers=headers)

        content_type = response.headers.get('content-type')

        self.assertTrue(str(content_type).startswith(MULTIPART))

        boundary = self.get_boundary(content_type)

        self.assertNotEqual(boundary, '')

        parsed_content = self.parse_msg(response.content, boundary)

        if object_type == "standard":
            self.assertEqual("grok",
                             parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
            self.assertEqual("one", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("one",
                                                    str(response.content)))
            self.assertEqual("drok", parsed_content.get('value3'),
                             msg=CONTENT_MSG.format("drok",
                                                    str(response.content)))
        else:
            self.assertEqual("grok",
                             parsed_content.get('value1'),
                             msg=CONTENT_MSG.format("grok",
                                                    str(response.content)))
            # This assertion will fail whenever the DLO/SLO bug for multipart
            # range requests is resolved (JIRA STORDEV-189).
            self.assertEqual("one", parsed_content.get('value2'),
                             msg=CONTENT_MSG.format("one",
                                                    str(response.content)))
            # This assertion will fail whenever the DLO/SLO bug for multipart
            # range requests is resolved (JIRA STORDEV-189).
            self.assertEqual("drok", parsed_content.get('value3'),
                             msg=CONTENT_MSG.format("drok",
                                                    str(response.content)))

    @data_driven_test(ObjectDatasetList())
    def ddtest_range_request_with_bad_ranges(
            self, object_type, generate_object):
        """
        Scenario:
            Perform a get with various range request headers not specified
            in the docs.

        Expected Results:
            The request should return data without breaking.
        """
        container_name = self.create_temp_container(descriptor=CONTAINER_NAME)
        if object_type == "standard":
            obj_data = "grok_one drok_two"
        else:
            obj_data = ''.join(["grok_{0}/".format(x) for x in range(
                1000000)])

        generate_object(container_name, self.object_name, data=obj_data)

        headers = {'Range': 'bytes=foobar'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=4'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=7-1'}
        response = self.client.get_object(
            container_name,
            self.object_name,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        if object_type == "standard":
            headers = {'Range': 'bytes=-160-5'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                obj_data,
                response.content,
                msg=CONTENT_MSG.format(
                    obj_data,
                    str(response.content)))
        else:
            headers = {'Range': 'bytes=-12888890-11888860'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                obj_data,
                response.content,
                msg=CONTENT_MSG.format(
                    obj_data,
                    str(response.content)))

        if object_type == "standard":
            headers = {'Range': 'bytes=5-160'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                "one drok_two",
                response.content,
                msg=CONTENT_MSG.format(
                    "one drok_two",
                    str(response.content)))
        else:
            headers = {'Range': 'bytes=11888866-12888890'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                "grok_999998/grok_999999/",
                response.content,
                msg=CONTENT_MSG.format(
                    "grok_999998/grok_999999/",
                    str(response.content)))

        if object_type == "standard":
            headers = {'Range': 'bytes=-160-160'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                obj_data,
                response.content,
                msg=CONTENT_MSG.format(
                    obj_data,
                    str(response.content)))
        else:
            headers = {'Range': 'bytes=-12888890-12888890'}
            response = self.client.get_object(
                container_name,
                self.object_name,
                headers=headers)

            self.assertEqual(
                obj_data,
                response.content,
                msg=CONTENT_MSG.format(
                    obj_data,
                    str(response.content)))
