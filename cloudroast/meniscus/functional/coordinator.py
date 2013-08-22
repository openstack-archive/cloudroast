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

from uuid import uuid4
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cloudroast.meniscus.fixtures import StatusFixture


class CoordinatorPositiveHostnameDatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositiveHostnameDatasetList, self).__init__()
        self.append_new_dataset('number_str', {'hostname': '1234'})
        self.append_new_dataset('uuid', {'hostname': str(uuid4())})
        self.append_new_dataset('255_len', {'hostname': 'a' * 255})
        self.append_new_dataset('fqdn', {'hostname': 'rackspace.com'})
        self.append_new_dataset('subdomain',
                                {'hostname': 'www.rackspace.com'})
        self.append_new_dataset('http_scheme',
                                {'hostname': 'http://www.rackspace.com'})


class CoordinatorPositiveIpv4DatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositiveIpv4DatasetList, self).__init__()
        self.append_new_dataset('zeros', {'ip_v4': '0.0.0.0'})
        self.append_new_dataset('max', {'ip_v4': '255.255.255.255'})


class CoordinatorPositiveIpv6DatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositiveIpv6DatasetList, self).__init__()
        ipv6_zeros = '0000:0000:0000:0000:0000:0000:0000:0000'
        ipv6_max = 'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff'
        self.append_new_dataset('zeros', {'ip_v6': ipv6_zeros})
        self.append_new_dataset('max', {'ip_v6': ipv6_max})
        self.append_new_dataset('combine_zero_sections',
                                {'ip_v6': 'ffff:fff::ffff:ff:ffff'})
        self.append_new_dataset('combine_all_leading_groups',
                                {'ip_v6': '::1'})
        self.append_new_dataset('combine_leading_leading',
                                {'ip_v6': 'ffff:fff:0:0:0:ffff:ff:ffff'})


class CoordinatorPositiveOsTypeDatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositiveOsTypeDatasetList, self).__init__()
        self.append_new_dataset('len_255', {'os_type': 'a' * 255})
        self.append_new_dataset('ascii_letters',
                                {'os_type': string.ascii_letters})
        self.append_new_dataset('ascii_numbers',
                                {'os_type': '0123456789'})
        self.append_new_dataset('ascii_punctuation',
                                {'os_type': string.punctuation})


class CoordinatorPositivePersonalityDatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositivePersonalityDatasetList, self).__init__()
        self.append_new_dataset('correlation',
                                {'personality': 'correlation'})
        self.append_new_dataset('normalization',
                                {'personality': 'normalization'})
        self.append_new_dataset('storage',
                                {'personality': 'storage'})


class CoordinatorPositiveStatusDatasetList(DatasetList):
    def __init__(self):
        super(CoordinatorPositiveStatusDatasetList, self).__init__()
        self.append_new_dataset('new', {'status': 'new'})


@DataDrivenFixture
class CoordinatorAPI(StatusFixture):

    def _positive_pair_worker(self, hostname=None, ip_v4=None, ip_v6=None,
                              personality=None, status=None, os_type=None):
        orig_resp = self.pairing_behaviors.pair_worker_from_config(
            hostname=hostname, ip_v4=ip_v4, ip_v6=ip_v6,
            personality=personality, status=status, os_type=os_type)
        self.assertEqual(orig_resp.status_code, 202)

        worker_id = orig_resp.entity.worker_id

        resp = self.status_client.get_worker_status(worker_id=worker_id)
        self.assertEqual(resp.status_code, 200)
        return resp

    @tags(type='positive')
    @data_driven_test(CoordinatorPositiveHostnameDatasetList())
    def ddtest_positive_pair_worker_with_hostname(self, hostname):
        resp = self._positive_pair_worker(hostname=hostname)
        self.assertEqual(resp.entity.hostname, hostname)

    @tags(type='positive')
    @data_driven_test(CoordinatorPositiveIpv4DatasetList())
    def ddtest_positive_pair_worker_with_ipv4(self, ip_v4):
        resp = self._positive_pair_worker(ip_v4=ip_v4)
        self.assertEqual(resp.entity.ip_v4, ip_v4)

    @tags(type='positive')
    @data_driven_test(CoordinatorPositiveIpv6DatasetList())
    def ddtest_positive_pair_worker_with_ipv6(self, ip_v6):
        resp = self._positive_pair_worker(ip_v6=ip_v6)
        self.assertEqual(resp.entity.ip_v6, ip_v6)

    @tags(type='positive')
    @data_driven_test(CoordinatorPositiveStatusDatasetList())
    def ddtest_positive_pair_worker_with_status(self, status):
        resp = self._positive_pair_worker(status=status)
        self.assertEqual(resp.entity.status, status)

    @tags(type='positive')
    @data_driven_test(CoordinatorPositiveOsTypeDatasetList())
    def ddtest_positive_pair_worker_with_os_type(self, os_type):
        resp = self._positive_pair_worker(os_type=os_type)
        self.assertEqual(resp.entity.system_info.os_type, os_type)
