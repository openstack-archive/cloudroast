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
import unittest
from unittest import skipUnless

from cafe.drivers.unittest.decorators import tags
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools.check_dict import get_value

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
NOT_CONFIGURED_MSG = "this feature is not configured by default"

class TempUrl(ObjectStorageFixture):
    def _reset_default_key(self):
        response = None
        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        response = self.client.set_temp_url_key(headers=headers)
        time.sleep(
            float(self.objectstorage_api_config.tempurl_key_cache_time))
        return response

    @classmethod
    def setUpClass(cls):
        super(TempUrl, cls).setUpClass()
        cls.tempurl_key = cls.behaviors.VALID_TEMPURL_KEY

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

    def test_object_creation_via_tempurl(self):
        """
        Scenario:
            Create a 'PUT' TempURL.  Perform a HTTP PUT to the TempURL sending
            data for the object;.

        Expected Results:
            The object should be created containing the correct data.
        """
        container_name = self.create_temp_container('tempurl')
        object_name = self.behaviors.VALID_OBJECT_NAME

        tempurl_data = self.client.create_temp_url(
            'PUT',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        object_data = self.behaviors.VALID_OBJECT_DATA
        content_length = str(len(object_data))

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'X-Object-Meta-Foo': 'bar'}

        self.client.auth_off()

        params = {'temp_url_sig': tempurl_data['signature'],
                  'temp_url_expires': tempurl_data['expires']}
        response = self.client.put(
            tempurl_data['target_url'],
            params=params,
            headers=headers,
            data=object_data)

        self.client.auth_on()

        response = self.client.get_object(container_name, object_name)
        self.assertEqual(response.content, object_data)
        self.assertIn('x-object-meta-foo', response.headers, '')
        self.assertEqual(response.headers['x-object-meta-foo'], 'bar')

    def test_object_retrieval_via_tempurl(self):
        """
        Scenario:
            Create a 'GET' TempURL for an existing object.  Perform a HTTP GET
            to the TempURL.

        Expected Results:
            The object should be returned containing the correct data.
        """
        container_name = self.create_temp_container('tempurl')
        object_name = self.behaviors.VALID_OBJECT_NAME
        object_data = self.behaviors.VALID_OBJECT_DATA
        self.client.create_object(
            container_name,
            object_name,
            data=object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.client.auth_off()

        params = {'temp_url_sig': tempurl_data['signature'],
                  'temp_url_expires': tempurl_data['expires']}
        response = self.client.get(tempurl_data['target_url'], params=params)
        expected_disposition = 'attachment; filename="{0}"'.format(object_name)
        recieved_disposition = response.headers['content-disposition']

        self.client.auth_on()

        self.assertIn('content-disposition', response.headers, '')
        self.assertEqual(expected_disposition, recieved_disposition)

        self.assertEqual(
            response.content, object_data,
            'object should contain correct data.')

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
        object_name = '{0}/'.format(self.base_object_name)
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok)

        data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.assertIn('target_url', data.keys())
        self.assertIn('signature', data.keys())
        self.assertIn('expires', data.keys())

        self.client.auth_off()

        params = {'temp_url_sig': data['signature'],
                  'temp_url_expires': data['expires']}
        tempurl_get_response = self.client.get(
            data['target_url'], params=params)

        self.client.auth_on()

        disposition = \
            tempurl_get_response.headers['content-disposition'].split('=')

        self.assertEqual(object_name.split('/')[0], disposition[1].strip('"'))

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
        object_name = '{0}/foo'.format(self.base_object_name)
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        headers = {'X-Account-Meta-Temp-URL-Key': self.tempurl_key}
        set_key_response = self.client.set_temp_url_key(headers=headers)

        self.assertTrue(set_key_response.ok)

        data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.assertIn('target_url', data.keys())
        self.assertIn('signature', data.keys())
        self.assertIn('expires', data.keys())

        self.client.auth_off()

        params = {'temp_url_sig': data['signature'],
                  'temp_url_expires': data['expires']}
        tempurl_get_response = self.client.get(
            data['target_url'], params=params)

        self.client.auth_on()

        disposition = \
            tempurl_get_response.headers['content-disposition'].split('=')

        self.assertEqual(object_name.split('/')[1], disposition[1].strip('"'))

    def test_object_retrieval_with_filename_override(self):
        """
        Scenario:
            Create a 'GET' TempURL.  Download the object using the TempURL,
            adding the "filename" parameter to the query string where the
            filename added is made up of valid ascii characters.

        Expected Results:
            The response back should contain a 'Content-Disposition' header
            with the value set in the filename parameter.
        """
        container_name = self.create_temp_container('tempurl')

        object_name = self.behaviors.VALID_OBJECT_NAME
        object_name_override = '{0}.override'.format(object_name)
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.client.auth_off()

        params = {'temp_url_sig': tempurl_data['signature'],
                  'temp_url_expires': tempurl_data['expires'],
                  'filename': object_name_override}
        response = self.client.get(tempurl_data['target_url'], params=params)

        self.client.auth_on()

        self.assertIn(
            'content-disposition',
            response.headers,
            'response should contain "content-disposition" header.')
        self.assertEqual(
            'attachment; filename="{0}"'.format(object_name_override),
            response.headers['content-disposition'],
            'content-disposition header should contain correct filename.')

    def test_filename_override_containing_trailing_slash(self):
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
        container_name = self.create_temp_container('tempurl')

        object_name = self.behaviors.VALID_OBJECT_NAME
        object_name_override = \
            self.behaviors.VALID_OBJECT_NAME_WITH_TRAILING_SLASH
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400', self.tempurl_key)

        self.client.auth_off()

        params = {'temp_url_sig': tempurl_data['signature'],
                  'temp_url_expires': tempurl_data['expires'],
                  'filename': object_name_override}
        response = self.client.get(tempurl_data['target_url'], params=params)

        self.client.auth_on()

        self.assertIn(
            'content-disposition',
            response.headers,
            'response should contain "content-disposition" header.')
        self.assertEqual(
            'attachment; filename="{0}"'.format(object_name_override),
            response.headers['content-disposition'],
            'content-disposition header should contain correct filename.')

    def test_filename_override_containing_slash(self):
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
        container_name = self.create_temp_container('tempurl')

        object_name = self.behaviors.VALID_OBJECT_NAME
        object_name_override = \
            self.behaviors.VALID_OBJECT_NAME_WITH_SLASH
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        tempurl_data = self.client.create_temp_url(
            'GET',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.client.auth_off()

        params = {'temp_url_sig': tempurl_data['signature'],
                  'temp_url_expires': tempurl_data['expires'],
                  'filename': object_name_override}
        response = self.client.get(tempurl_data['target_url'], params=params)

        self.client.auth_on()

        self.assertIn(
            'content-disposition',
            response.headers,
            'response should contain "content-disposition" header.')
        self.assertEqual(
            'attachment; filename="{0}"'.format(object_name_override),
            response.headers['content-disposition'],
            'content-disposition header should contain correct filename.')

    @skipUnless(get_value('configured') == 'true', NOT_CONFIGURED_MSG)
    def test_tempurl_object_delete(self):
        """
        Note: -d configured=true will enable this test
        """
        container_name = self.create_temp_container('temp_url')
        object_name = self.base_object_name
        object_data = self.behaviors.VALID_OBJECT_DATA
        object_content_length = str(len(object_data))

        headers = {'Content-Length': object_content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}
        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        data = self.client.create_temp_url(
            'DELETE',
            container_name,
            object_name,
            '86400',
            self.tempurl_key)

        self.assertIn('target_url', data.keys())
        self.assertIn('signature', data.keys())
        self.assertIn('expires', data.keys())

        self.client.auth_off()

        params = {'temp_url_sig': data['signature'],
                  'temp_url_expires': data['expires']}
        delete_response = self.client.delete(
            data['target_url'],
            params=params)

        self.client.auth_on()

        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client.get_object(container_name, object_name)

        self.assertEqual(get_response.status_code, 404)
