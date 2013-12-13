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
import string
from datetime import datetime
from dateutil.parser import parse as parse_iso8601

from cloudroast.meniscus.fixtures import (PublishingFixture,
                                          RSyslogPublishingFixture)
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)


class PositiveDatasetList(DatasetList):
    def _get_syslog_accepted_punctuation(self):
        chars_to_remove = [':', '[']
        syslog_punctuation = [char for char in string.punctuation
                              if char not in chars_to_remove]
        return ''.join(syslog_punctuation)

    def __init__(self):

        syslog_punctuation = self._get_syslog_accepted_punctuation()

        current_time = datetime.now().isoformat()
        # Use default values
        self.append_new_dataset('valid_host', {'host': None})
        self.append_new_dataset('valid_pname', {'pname': None})
        self.append_new_dataset('valid_time', {'time': current_time})

        # Host
        self.append_new_dataset('host_255_in_length', {'host': 'a' * 255})
        self.append_new_dataset('host_ascii_uppercase',
                                {'host': string.ascii_uppercase})
        self.append_new_dataset('host_ascii_lowercase',
                                {'host': string.ascii_lowercase})
        self.append_new_dataset('host_punctuation',
                                {'host': syslog_punctuation})

        # Pname
        self.append_new_dataset('pname_48_in_length', {'pname': 'a' * 48})
        self.append_new_dataset('pname_ascii_lowercase',
                                {'pname': string.ascii_lowercase})
        self.append_new_dataset('pname_ascii_uppercase',
                                {'pname': string.ascii_uppercase})
        self.append_new_dataset('pname_punctuation',
                                {'pname': syslog_punctuation})

        # Native
        self.append_new_dataset('native_empty_dict', {'native': {}})


class NegativeDatasetList(DatasetList):
    def __init__(self):
        self.append_new_dataset('native_array', {'native': []})
        self.append_new_dataset('native_string', {'native': ''})
        self.append_new_dataset('native_int', {'native': 0})
        self.append_new_dataset('native_float', {'native': 0.0})


@DataDrivenFixture
class PublishingHttpAPI(PublishingFixture):

    @tags(type='positive')
    @data_driven_test(PositiveDatasetList())
    def ddtest_valid_http_publishing(self, tenant_id, tenant_token=None,
                                     host=None, pname=None, time=None,
                                     native=None):
        if not time:
            time = str(datetime.utcnow().isoformat())

        resp = self.publish_behaviors.publish_overriding_config(
            tenant_id=tenant_id, tenant_token=tenant_token,
            host=host, pname=pname, time=time, native=native)
        self.assertEqual(resp.status_code, 204, resp.text)

    @tags(type='negative')
    @data_driven_test(NegativeDatasetList())
    def ddtest_invalid_http_publishing(self, tenant_id, tenant_token=None,
                                       host=None, pname=None, time=None,
                                       native=None):
        resp = self.publish_behaviors.publish_overriding_config(
            tenant_id=tenant_id, tenant_token=tenant_token,
            host=host, pname=pname, time=time, native=native)
        self.assertEqual(resp.status_code, 400, resp.text)

    def test_http_publish_and_verify_in_storage(self):
        """ Test verifying that we can retrieve some of the messages that we
        send through the http endpoint.
        """
        new_time = str(datetime.utcnow().isoformat())

        resp = self.publish_behaviors.publish_overriding_config(time=new_time)
        self.assertEqual(resp.status_code, 204, resp.text)

        msgs = self.publish_behaviors.get_messages_by_timestamp(
            timestamp=new_time, num_messages=1)

        # Verify that the one message that we sent made it through
        self.assertEqual(len(msgs), 1)


@DataDrivenFixture
class PublishingSyslogAPI(RSyslogPublishingFixture):

    @tags(type='positive')
    @data_driven_test(PositiveDatasetList())
    def ddtest_valid_syslog_publishing(self, host=None, pname=None, time=None,
                                       native=None):

        # Dealing with syslog-ng oddity documented in #161
        if not host:
            host = 'nohost'

        time = datetime.now().isoformat()
        # Syslog-ng only uses 3 decimal places
        time = time[:-3]

        result = self.rsyslog_client.send(
            priority=6, timestamp=time, app_name=pname, host_name=host,
            msg=native)

        # Sockets return None when they successfully deliver message
        self.assertIsNone(result)

        # Make sure the index exists before we continue
        self.assertTrue(self.es_client.has_index(self.tenant_id))

        msgs = self.publish_behaviors.get_messages_by_timestamp(
            timestamp=time, num_messages=1)

        self.assertEqual(len(msgs), 1)

        # This will work for now, but we need to write a model for this soon.
        msg = msgs[0]
        msg_time = parse_iso8601(msg.get('time'))
        expected_time = parse_iso8601('{0}+0'.format(time))
        self.assertEqual(msg.get('pri'), 'info')
        self.assertEqual(msg_time, expected_time)
        self.assertEqual(msg.get('pname'), pname or '-')
        self.assertEqual(msg.get('host'), host)
