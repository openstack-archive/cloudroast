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
import hmac
import json
from calendar import timegm
from datetime import datetime, timedelta
from hashlib import sha1

from cloudroast.objectstorage.fixtures import ObjectStorageFixture

INVALID_SIG = 'abcdef'
INVALID_EXPIRES = 'abcdef'


class SwiftInfoTest(ObjectStorageFixture):
    """
    Tests Swift http://<swift-endpoint>/info API call.

    Preconditions: Swift info is enabled in Swift's proxy config.
    """

    def get_sig(self, expires):
        """
        Generate a sig for the /info call.

        @param expires: Unix timestamp for when the sig should expire.
        @type  expires: int

        @return: A hexdigest string of the HMAC-SHA1 (RFC 2104) for the
                 /info call.
        @rtype: string
        """
        key = self.objectstorage_api_config.get('info_admin_key', '')
        method = 'GET'
        path = '/info'
        hmac_body = '%s\n%s\n%s' % (method, expires, path)
        sig = hmac.new(key, hmac_body, sha1).hexdigest()
        return sig

    def get_expires(self):
        """
        Returns a Unix timestamp in the future.

        @return: timestamp 1 hour in the future.
        @rtype: integer
        """
        future = datetime.now() + timedelta(hours=1)
        return timegm(future.utctimetuple())

    def get_expired_expires(self):
        """
        Returns a Unix timestamp in the past.

        @return: timestamp 1 hour in the past.
        @rtype: integer
        """
        past = datetime.now() + timedelta(hours=-1)
        return timegm(past.utctimetuple())

    @ObjectStorageFixture.required_features('info')
    def test_info(self):
        """
        Scenario: Make a call to /info.

        Expected Results: Swift info should be returned.  Within the info
                          returned, at a minimum, should contain a 'swift'
                          section.  Within the 'swift' section, there should
                          be a 'version' key/value pair.
                          Additionally, there should be no 'admin' section.
        """
        response = self.client.get_swift_info()
        self.assertEqual(
            200,
            response.status_code,
            "info call should return status code 200, received {}"
            .format(response.status_code))
        self.assertEqual(
            'application/json; charset=UTF-8',
            response.headers.get('content-type'),
            "info call should return data in json format, recieved {}"
            .format(response.headers.get('content-type')))
        info = json.loads(response.content)
        self.assertTrue(
            'swift' in info,
            'Info returned should contain a "swift" category')
        self.assertTrue(
            'version' in info['swift'],
            '"swift" section should contain a "version"')
        self.assertTrue(
            'admin' not in info,
            'Info returned should not contain a "admin" category')

    @ObjectStorageFixture.required_features('info')
    def test_admin_info_when_disabled(self):
        """
        Scenario: Make a admin call to /info.

        Expected Results: Swift info should not be returned.
        """
        expires = self.get_expires()
        params = {
            'swiftinfo_sig': self.get_sig(expires),
            'swiftinfo_expires': expires}
        response = self.client.get_swift_info(params=params)
        self.assertEqual(
            403,
            response.status_code,
            "info call should return status code 403, received {}"
            .format(response.status_code))

    @ObjectStorageFixture.required_features('info')
    def test_admin_info_fails_with_invalid_sig(self):
        """
        Scenario: Make a admin call to /info with an invalid signature.

        Expected Results: A HTTP 403 should be returned.
        """
        params = {
            'swiftinfo_sig': INVALID_SIG,
            'swiftinfo_expires': self.get_expires}
        response = self.client.get_swift_info(params=params)
        self.assertEqual(
            403,
            response.status_code,
            "info call should return status code 403, received {}"
            .format(response.status_code))

    @ObjectStorageFixture.required_features('info')
    def test_admin_info_fails_with_invalid_expires(self):
        """
        Scenario: Make a admin call to /info with an invalid expires.

        Expected Results: A HTTP 403 should be returned.
        """
        params = {
            'swiftinfo_sig': self.get_sig(INVALID_EXPIRES),
            'swiftinfo_expires': INVALID_EXPIRES}
        response = self.client.get_swift_info(params=params)
        self.assertEqual(
            403,
            response.status_code,
            "info call should return status code 403, received {}"
            .format(response.status_code))

    @ObjectStorageFixture.required_features('info')
    def test_admin_info_fails_with_expired_expires(self):
        """
        Scenario: Make a admin call to /info with an invalid expires.

        Expected Results: A HTTP 403 should be returned.
        """
        expired = self.get_expired_expires()
        params = {
            'swiftinfo_sig': self.get_sig(expired),
            'swiftinfo_expires': expired}
        response = self.client.get_swift_info(params=params)
        self.assertEqual(
            403,
            response.status_code,
            "info call should return status code 403, received {}"
            .format(response.status_code))
