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
from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudroast.objectstorage.generators import ObjectDatasetList
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTAINER_NAME = 'object_regression'
CONTENT_MSG = 'expected {0} in the content body. recieved {1}'
CONTENT_TYPE_MSG = 'expected content_type {0} recieved {1}'
MULTIPART = "multipart/byteranges"


@DataDrivenFixture
class ObjectRangeRequestTest(ObjectStorageFixture):

    def setUp(self):
        super(ObjectRangeRequestTest, self).setUp()
        self.container_name = self.create_temp_container(
            descriptor=CONTAINER_NAME)

    def parse_msg(self, response):
        response_dict = {}
        i = 1

        try:
            temp_type = \
                response.headers.get('content-type').split(";boundary=")
            content_type = temp_type[0]
            boundary = temp_type[1]
            response_dict['boundary'] = boundary
            response_dict['content_type'] = content_type
            split_body = response.content.split("--{0}".format(boundary))
            end = len(split_body) - 1

            while(i < end):
                response_dict['value{0}'.format(i)] = \
                    split_body[i].split('\r\n\r\n')[1].strip('\r\n')
                i += 1
        except:
            return {}

        return response_dict

    @data_driven_test(ObjectDatasetList())
    def ddtest_basic_object_range_request(self):
        obj_data = "grok_one drok_two"

        headers = {'Content-Length': str(len(obj_data))}
        self.behaviors.create_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers,
            data=obj_data)

        headers = {'Range': 'bytes=-3'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(response.content, "two",
                         msg=CONTENT_MSG.format("two", str(response.content)))

        headers = {'Range': 'bytes=0-3'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(response.content, "grok",
                         msg=CONTENT_MSG.format("grok", str(response.content)))

        headers = {'Range': 'bytes=4-4'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(response.content, "_",
                         msg=CONTENT_MSG.format("_", str(response.content)))

        headers = {'Range': 'bytes=9-'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            response.content,
            "drok_two",
            msg=CONTENT_MSG.format(
                "drok_two",
                str(response.content)))

    @data_driven_test(ObjectDatasetList())
    def ddtest_multi_part_range_request(self):
        obj_data = "grok_one drok_two"

        headers = {'Content-Length': str(len(obj_data))}
        self.behaviors.create_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers,
            data=obj_data)

        headers = {'Range': 'bytes=0-3,-3'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        parsed_msg = self.parse_msg(response)

        self.assertEqual(
            MULTIPART,
            parsed_msg.get('content_type'),
            msg=CONTENT_TYPE_MSG.format(
                MULTIPART,
                str(parsed_msg.get('content_type'))))
        self.assertTrue(parsed_msg.get('boundary') in response.content)
        self.assertEqual("grok", parsed_msg.get('value1'),
                         msg=CONTENT_MSG.format("grok", str(response.content)))
        self.assertEqual("two", parsed_msg.get('value2'),
                         msg=CONTENT_MSG.format("two", str(response.content)))

        headers = {'Range': 'bytes=-3,0-3'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        parsed_msg = self.parse_msg(response)

        self.assertEqual(
            MULTIPART,
            parsed_msg.get('content_type'),
            msg=CONTENT_TYPE_MSG.format(
                MULTIPART,
                str(parsed_msg.get('content_type'))))
        self.assertTrue(parsed_msg.get('boundary') in response.content)
        self.assertEqual("two", parsed_msg.get('value1'),
                         msg=CONTENT_MSG.format("two", str(response.content)))
        self.assertEqual("grok", parsed_msg.get('value2'),
                         msg=CONTENT_MSG.format("grok", str(response.content)))

        headers = {'Range': 'bytes=9-,0-3'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        parsed_msg = self.parse_msg(response)

        self.assertEqual(
            MULTIPART,
            parsed_msg.get('content_type'),
            msg=CONTENT_TYPE_MSG.format(
                MULTIPART,
                str(parsed_msg.get('content_type'))))
        self.assertTrue(parsed_msg.get('boundary') in response.content)
        self.assertEqual(
            "drok_two",
            parsed_msg.get('value1'),
            msg=CONTENT_MSG.format(
                "drok_two",
                str(response.content)))
        self.assertEqual("grok", parsed_msg.get('value2'),
                         msg=CONTENT_MSG.format("grok", str(response.content)))

        headers = {'Range': 'bytes=0-3,5-7,9-12'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        parsed_msg = self.parse_msg(response)

        self.assertEqual(
            MULTIPART,
            parsed_msg.get('content_type'),
            msg=CONTENT_TYPE_MSG.format(
                MULTIPART,
                str(parsed_msg.get('content_type'))))
        self.assertTrue(parsed_msg.get('boundary') in response.content)
        self.assertEqual("grok", parsed_msg.get('value1'),
                         msg=CONTENT_MSG.format("grok", str(response.content)))
        self.assertEqual("one", parsed_msg.get('value2'),
                         msg=CONTENT_MSG.format("one", str(response.content)))
        self.assertEqual("drok", parsed_msg.get('value3'),
                         msg=CONTENT_MSG.format("drok", str(response.content)))

    @data_driven_test(ObjectDatasetList())
    def ddtest_range_request_with_bad_ranges(self):
        obj_data = "grok_one drok_two"

        headers = {'Content-Length': str(len(obj_data))}
        self.behaviors.create_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers,
            data=obj_data)

        headers = {'Range': 'bytes=foobar'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=4'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=7-1'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=-160-5'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))

        headers = {'Range': 'bytes=5-160'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            "one drok_two",
            response.content,
            msg=CONTENT_MSG.format(
                "one drok_two",
                str(response.content)))

        headers = {'Range': 'bytes=-160-160'}
        response = self.client.get_object(
            self.container_name,
            self.behaviors.VALID_OBJECT_NAME,
            headers=headers)

        self.assertEqual(
            obj_data,
            response.content,
            msg=CONTENT_MSG.format(
                obj_data,
                str(response.content)))
