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

from cloudroast.meniscus.fixtures import PublishingFixture
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)


class PositiveDatasetList(DatasetList):
    def __init__(self):
        current_time = datetime.now().isoformat()
        # Use default values
        self.append_new_dataset('valid_host', {'host': None})
        self.append_new_dataset('valid_pname', {'pname': None})
        self.append_new_dataset('valid_time', {'time': current_time})

        # Host
        self.append_new_dataset('host_255_in_length', {'host': 'a' * 255})
        self.append_new_dataset('host_ascii_letters',
                                {'host': string.ascii_letters})
        self.append_new_dataset('host_punctuation',
                                {'host': string.punctuation})
        self.append_new_dataset('host_all_printable_characters',
                                {'host': string.printable})

        # Pname
        self.append_new_dataset('pname_255_in_length', {'pname': 'a' * 255})
        self.append_new_dataset('pname_ascii_letters',
                                {'pname': string.ascii_letters})
        self.append_new_dataset('pname_punctuation',
                                {'pname': string.punctuation})
        self.append_new_dataset('pname_all_printable_characters',
                                {'pname': string.printable})

        # Native
        self.append_new_dataset('native_empty_dict', {'native': {}})


class NegativeDatasetList(DatasetList):
    def __init__(self):
        self.append_new_dataset('native_array', {'native': []})
        self.append_new_dataset('native_string', {'native': ''})
        self.append_new_dataset('native_int', {'native': 0})
        self.append_new_dataset('native_float', {'native': 0.0})


@DataDrivenFixture
class PublishingAPI(PublishingFixture):

    @tags(type='positive')
    @data_driven_test(PositiveDatasetList())
    def ddtest_valid_publishing(self, tenant_id, tenant_token=None,
                                host=None, pname=None, time=None,
                                native=None):
        resp = self.publish_behaviors.publish_overriding_config(
            tenant_id=tenant_id, tenant_token=tenant_token,
            host=host, pname=pname, time=time, native=native)
        self.assertEqual(resp.status_code, 204, resp.text)

    @tags(type='negative')
    @data_driven_test(NegativeDatasetList())
    def ddtest_invalid_publishing(self, tenant_id, tenant_token=None,
                                  host=None, pname=None, time=None,
                                  native=None):
        resp = self.publish_behaviors.publish_overriding_config(
            tenant_id=tenant_id, tenant_token=tenant_token,
            host=host, pname=pname, time=time, native=native)
        self.assertEqual(resp.status_code, 400, resp.text)
