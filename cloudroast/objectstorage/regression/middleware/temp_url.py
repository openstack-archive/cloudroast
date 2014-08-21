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
import time

from unittest import skipUnless
from cafe.engine.http.client import HTTPClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools.check_dict import get_value

BASE_CONTAINER_NAME = 'tempurl'
CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
TEMPURL_KEY_LIFE = 20
EXPECTED_DISPOSITION = ("attachment; filename=\"{filename}\";"
                        " filename*=UTF-8\'\'{filename}")


class TempUrl(ObjectStorageFixture):
    def _reset_default_key(self):
        response = None
        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        response = self.client.set_temp_url_key(headers=headers)
        time.sleep(self.objectstorage_api_config.tempurl_key_cache_time)
        return response

    @classmethod
    def setUpClass(cls):
        super(TempUrl, cls).setUpClass()
        cls.key_cache_time = (
            cls.objectstorage_api_config.tempurl_key_cache_time)
        cls.http = HTTPClient()
        cls.tempurl_key = cls.behaviors.VALID_TEMPURL_KEY
        cls.object_name = cls.behaviors.VALID_OBJECT_NAME
        cls.obj_name_containing_trailing_slash = \
            cls.behaviors.VALID_OBJECT_NAME_WITH_TRAILING_SLASH
        cls.obj_name_containing_slash = \
            cls.behaviors.VALID_OBJECT_NAME_WITH_SLASH
        cls.object_data = cls.behaviors.VALID_OBJECT_DATA
        cls.content_length = str(len(cls.behaviors.VALID_OBJECT_DATA))

    def setUp(self):
        """
        Check if the TempURL has been changed, if so, change it back to
        the expected key and wait the appropriate amount of time to let the
        key propogate through the system.
        """
        super(TempUrl, self).setUp()

        if self.tempurl_key != self.behaviors.get_tempurl_key():
            response = self._reset_default_key()
            if not response.ok:
                raise Exception('Could not set TempURL key.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_object_creation_via_tempurl(self):
        """
        Scenario:
            Create a 'PUT' TempURL.  Perform a HTTP PUT to the TempURL sending
            data for the object;.

        Expected Results:
            The object should be created containing the correct data.
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        tempurl_data = self.client.create_temp_url(
            'PUT',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Meta-Foo': 'bar'}
        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires')}
        response = self.http.put(
            tempurl_data.get('target_url'),
            params=params,
            headers=headers,
            data=self.object_data)

        response = self.client.get_object(container_name, self.object_name)

        self.assertEqual(
            response.content,
            self.object_data,
            msg="object should contain correct data")
        self.assertIn(
            'x-object-meta-foo',
            response.headers,
            msg="x-object-meta-foo header was not set")
        self.assertEqual(
            response.headers['x-object-meta-foo'],
            'bar',
            msg="x-object-meta-foo header value is not bar")

    @ObjectStorageFixture.required_features('tempurl')
    def test_object_retrieval_via_tempurl(self):
        """
        Scenario:
            Create a 'GET' TempURL for an existing object.  Perform a HTTP GET
            to the TempURL.

        Expected Results:
            The object should be returned containing the correct data.
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        self.client.create_object(
            container_name,
            self.object_name,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires')}

        response = self.http.get(tempurl_data.get('target_url'), params=params)

        self.assertTrue(response.ok, 'object should be retrieved over tempurl')

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=self.object_name)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_object_retrieval_via_tempurl_content_disposition_inline(self):
        """
        Scenario:
            Create a 'GET' TempURL for an existing object.  Perform a HTTP GET
            to the TempURL.

        Expected Results:
            The object should be returned containing the correct data.
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        attachment_hdr = 'INLINE; FILENAME= "{0}"'.format(self.object_name)

        self.client.create_object(
            container_name,
            self.object_name,
            headers={'content-disposition': attachment_hdr},
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires')}

        response = self.http.get(tempurl_data.get('target_url'), params=params)
        self.assertTrue(response.ok, 'object should be retrieved over tempurl')

        expected_disposition = attachment_hdr
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_tempurl_content_disposition_filename_with_trailing_slash(self):
        """
        Scenario:
            Create a 'GET' TempURL for an object where the object name ends
            with a '/'.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with a value of the object name having the slash stripped out.
        """
        container_name = self.create_temp_container('temp_url')

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.obj_name_containing_trailing_slash,
            headers=headers,
            data=self.object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok, msg="tempurl key was not set")

        data = self.client.create_temp_url(
            'GET',
            container_name,
            self.obj_name_containing_trailing_slash,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': data.get('signature'),
                  'temp_url_expires': data.get('expires')}
        tempurl_get_response = self.http.get(
            data.get('target_url'), params=params)

        expected_filename = \
            self.obj_name_containing_trailing_slash.split('/')[0]

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=expected_filename)
        recieved_disposition = tempurl_get_response.headers.get(
            'content-disposition')

        self.assertIn(
            'content-disposition',
            tempurl_get_response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            tempurl_get_response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_tempurl_content_disposition_header_filename_with_trailing_slash(
            self):
        """
        Scenario:
            Create a 'GET' TempURL for an object where the object name ends
            with a '/'.

        Expected Results:
            content disposition should return as expressly set
        """
        container_name = self.create_temp_container('temp_url')

        content_disposition = 'Attachment; filename={0}'.format(
            self.obj_name_containing_trailing_slash)

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Disposition': content_disposition}
        self.client.create_object(
            container_name,
            self.obj_name_containing_trailing_slash,
            headers=headers,
            data=self.object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok, msg="tempurl key was not set")

        data = self.client.create_temp_url(
            'GET',
            container_name,
            self.obj_name_containing_trailing_slash,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': data.get('signature'),
                  'temp_url_expires': data.get('expires')}
        tempurl_get_response = self.http.get(
            data.get('target_url'), params=params)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        expected_disposition = content_disposition
        recieved_disposition = tempurl_get_response.headers.get(
            'content-disposition')

        self.assertIn(
            'content-disposition',
            tempurl_get_response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            tempurl_get_response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_tempurl_content_disposition_filename_containing_slash(self):
        """
        Scenario:
            Create a 'GET' TempURL for an object where the object name
            contains a '/'.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with a value of a substring of the object name consisting of the
            first character following the '/' to the end of the string.
        """
        container_name = self.create_temp_container('temp_url')

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.obj_name_containing_slash,
            headers=headers,
            data=self.object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok, msg="tempurl key was not set")

        data = self.client.create_temp_url(
            'GET',
            container_name,
            self.obj_name_containing_slash,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': data.get('signature'),
                  'temp_url_expires': data.get('expires')}
        tempurl_get_response = self.http.get(
            data.get('target_url'), params=params)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        expected_filename = \
            expected_filename = self.obj_name_containing_slash.split('/')[1]

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=expected_filename)
        recieved_disposition = tempurl_get_response.headers.get(
            'content-disposition')

        self.assertIn(
            'content-disposition',
            tempurl_get_response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            tempurl_get_response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_tempurl_content_disposition_header_filename_containing_slash(
            self):
        """
        Scenario:
            Create a 'GET' TempURL for an object where the object name
            contains a '/'.

        Expected Results:
            content disposition should return as expressly set
        """
        container_name = self.create_temp_container('temp_url')

        content_disposition = 'Attachment; filename={0}'.format(
            self.obj_name_containing_slash)

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Content-Disposition': content_disposition}
        self.client.create_object(
            container_name,
            self.obj_name_containing_slash,
            headers=headers,
            data=self.object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok, msg="tempurl key was not set")

        data = self.client.create_temp_url(
            'GET',
            container_name,
            self.obj_name_containing_slash,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': data.get('signature'),
                  'temp_url_expires': data.get('expires')}
        tempurl_get_response = self.http.get(
            data.get('target_url'), params=params)

        self.assertIn(
            'target_url',
            data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            data.keys(),
            msg='expires was not in the created tempurl')

        expected_disposition = content_disposition
        recieved_disposition = tempurl_get_response.headers.get(
            'content-disposition')

        self.assertIn(
            'content-disposition',
            tempurl_get_response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            tempurl_get_response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_object_retrieval_with_filename_override_param(self):
        """
        Scenario:
            Create a 'GET' TempURL.  Download the object using the TempURL,
            adding the "filename" parameter to the query string where the
            filename added is made up of valid ascii characters.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with the value set in the filename parameter.
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        object_name_override = '{0}.override'.format(self.object_name)

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.object_name,
            headers=headers,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires'),
                  'filename': object_name_override}
        response = self.http.get(tempurl_data.get('target_url'), params=params)

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=object_name_override)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_filename_override_param_containing_trailing_slash(self):
        """
        Scenario:
            Create a 'GET' TempURL.  Download the object using the TempURL,
            adding the "filename" parameter to the query string where the
            filename added is made up of valid ascii characters, including a
            trailing slash.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with the value set in the filename parameter (including the
            trailing slash).
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        object_name_override = self.obj_name_containing_trailing_slash

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.object_name,
            headers=headers,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires'),
                  'filename': object_name_override}
        response = self.http.get(tempurl_data.get('target_url'), params=params)

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=object_name_override)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    def test_filename_override_param_containing_slash(self):
        """
        Scenario:
            Create a 'GET' TempURL.  Download the object using the TempURL,
            adding the "filename" parameter to the query string where the
            filename added is made up of valid ascii characters, including a
            including a slash.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with the value set in the filename parameter (including the
            slash).
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        object_name_override = self.obj_name_containing_slash

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.object_name,
            headers=headers,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires'),
                  'filename': object_name_override}
        response = self.http.get(tempurl_data.get('target_url'), params=params)

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=object_name_override)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

    @ObjectStorageFixture.required_features('tempurl')
    @skipUnless(get_value('tempurl-methods') == 'delete',
                'tempurl must be configured to allow DELETE.')
    def test_tempurl_object_delete(self):
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.object_name,
            headers=headers,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'DELETE',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires')}
        delete_response = self.http.delete(
            tempurl_data.get('target_url'),
            params=params)

        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client.get_object(container_name, self.object_name)

        self.assertEqual(get_response.status_code, 404)

    @skipUnless(get_value('slow') == 'true', 'sleep for key change')
    @ObjectStorageFixture.required_features('tempurl')
    def test_object_retrieval_with_two_tempurl_keys(self):
        time.sleep(
            float(self.objectstorage_api_config.tempurl_key_cache_time))

        container_name = self.create_temp_container('temp_url')

        headers = {'Content-Length': self.content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            self.object_name,
            headers=headers,
            data=self.object_data)

        foo_key = '{0}_foo'.format(self.behaviors.VALID_TEMPURL_KEY)
        bar_key = '{0}_bar'.format(self.behaviors.VALID_TEMPURL_KEY)

        headers = {'X-Account-Meta-Temp-URL-Key': foo_key}
        set_foo_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_foo_key_response.ok)

        headers = {'X-Account-Meta-Temp-URL-Key-2': bar_key}
        set_bar_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_bar_key_response.ok)

        foo_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            foo_key)

        self.assertIn(
            'target_url',
            foo_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            foo_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            foo_data.keys(),
            msg='expires was not in the created tempurl')

        bar_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            bar_key)

        self.assertIn(
            'target_url',
            bar_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            bar_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            bar_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': foo_data.get('signature'),
                  'temp_url_expires': foo_data.get('expires')}
        foo_get_response = self.http.get(
            foo_data.get('target_url'), params=params)

        self.assertEqual(
            self.object_data,
            foo_get_response.content,
            msg='object data was changed')

        params = {'temp_url_sig': bar_data.get('signature'),
                  'temp_url_expires': bar_data.get('expires')}
        bar_get_response = self.http.get(
            bar_data.get('target_url'), params=params)

        self.assertEqual(
            self.object_data,
            bar_get_response.content,
            msg='object data was changed')

    @ObjectStorageFixture.required_features('tempurl')
    def test_tempurl_expiration(self):
        """
        Scenario:
            Create a 'GET' TempURL for an existing object.
            Perform a HTTP GET to the TempURL after the expiration time.

        Expected Results:
            The GET should fail.
        """
        container_name = self.create_temp_container(BASE_CONTAINER_NAME)

        self.client.create_object(
            container_name,
            self.object_name,
            data=self.object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            self.object_name,
            TEMPURL_KEY_LIFE,
            self.tempurl_key)

        self.assertIn(
            'target_url',
            tempurl_data.keys(),
            msg='target_url was not in the created tempurl')
        self.assertIn(
            'signature',
            tempurl_data.keys(),
            msg='signature was not in the created tempurl')
        self.assertIn(
            'expires',
            tempurl_data.keys(),
            msg='expires was not in the created tempurl')

        params = {'temp_url_sig': tempurl_data.get('signature'),
                  'temp_url_expires': tempurl_data.get('expires')}
        response = self.http.get(tempurl_data.get('target_url'), params=params)

        expected_disposition = 'attachment; filename="{0}"'.format(
            self.object_name)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertTrue(response.ok, 'object should be retrieved over tempurl')

        expected_disposition = EXPECTED_DISPOSITION.format(
            filename=self.object_name)
        recieved_disposition = response.headers.get('content-disposition')

        self.assertIn(
            'content-disposition',
            response.headers,
            msg='content-disposition was not found in response headers')
        self.assertEqual(
            expected_disposition,
            recieved_disposition,
            msg='expected {0} recieved {1}'.format(
                expected_disposition,
                recieved_disposition))
        self.assertEqual(
            response.content,
            self.object_data,
            'object should contain correct data.')

        time.sleep(int(TEMPURL_KEY_LIFE) + 60)

        response = self.http.get(tempurl_data.get('target_url'), params=params)

        self.assertEqual(
            response.status_code,
            401,
            msg='tempurl did not expire')
