"""
Copyright 2015 Rackspace

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

from cafe.drivers.unittest.decorators import tags
from cloudroast.compute.fixtures import ComputeFixture


class LimitsTest(ComputeFixture):

    @tags(type='smoke', net='no', test='test')
    def test_list_limits(self):
        """
        This will call the get limits and ensure that the absolute and rate
        limits are populated as expected.

        Request a list of available limits, ensure that the request is
        successful and that the absolute and rate limits are populated as
        expected.

        The following assertions occur:
            - 200 status code from the get_limits call
            - The body of the response code is not None
            - The number of rate limits is as expected
            - The expected rate limits are populated
            - The expected absolute limits are populated
        """

        expected_rate_limits_count = 10
        rate_limits_list = []
        vir_int_uri_verbs = []
        si_uri_verbs = []
        all_uri_verbs = []
        errors = []

        response = self.limits_client.get_limits()
        self.assertEqual(response.status_code, 200,
                         'Unexpected status code returned. '
                         'Expected: {0} Received: '
                         '{1}'.format(200, response.status_code))
        self.assertIsNotNone(response.entity,
                             'The expected limit response '
                             'body was not populated as expected')

        absolute_limits = response.entity.absolute_limits
        rate_limits = response.entity.rate_limits
        self.assertEqual(
            len(rate_limits), expected_rate_limits_count,
            'The number of rate limits received was not as expected')

        for limit in rate_limits:
            rate_limits_list.append(
                {'uri': limit.uri, 'verb': limit.limits[0].verb})

        for rate_limit in rate_limits_list:
            if rate_limit['uri'] == '*':
                all_uri_verbs.append(rate_limit['verb'])
            if rate_limit['uri'] == '/servers/{id}/os-virtual-interfacesv2':
                vir_int_uri_verbs.append(rate_limit['verb'])
            if rate_limit['uri'] == '/servers/{id}/rax-si-image-schedule':
                si_uri_verbs.append(rate_limit['verb'])
            if rate_limit['uri'] == '/os-networksv2':
                if rate_limit['verb'] != 'POST':
                    errors.append(
                        'The rate limits POST action was not populated for '
                        'the /os-networksv2 uri as expected')
            if rate_limit['uri'] == '/servers':
                if rate_limit['verb'] != 'POST':
                    errors.append(
                        'The rate limits POST action was not populated for '
                        'the /servers uri as expected')
        if 'POST' not in all_uri_verbs:
            errors.append(
                'The POST action was not populated for the * uri rate limit '
                'as expected')
        if 'GET' not in all_uri_verbs:
            errors.append(
                'The GET action was not populated for the * uri rate limit '
                'as expected')
        if 'DELETE' not in vir_int_uri_verbs:
            errors.append(
                'The DELETE action was not populated for the '
                '/servers/{id}/os-virtual-interfacesv2 uri rate limit as '
                'expected')
        if 'POST' not in vir_int_uri_verbs:
            errors.append(
                'The POST action was not populated for the '
                '/servers/{id}/os-virtual-interfacesv2 uri rate limit as '
                'expected')
        if 'GET' not in vir_int_uri_verbs:
            errors.append(
                'The GET action was not populated for the '
                '/servers/{id}/os-virtual-interfacesv2 uri rate limit as '
                'expected')
        if 'POST' not in si_uri_verbs:
            errors.append(
                'The POST action was not populated for the '
                '/servers/{id}/rax-si-image-schedule uri rate limit as '
                'expected')
        if 'GET' not in si_uri_verbs:
            errors.append(
                'The GET action was not populated for the '
                '/servers/{id}/rax-si-image-schedule uri rate limit as '
                'expected')
        if 'DELETE' not in si_uri_verbs:
            errors.append(
                'The DELETE action was not populated for the '
                '/servers/{id}/rax-si-image-schedule uri rate limit as '
                'expected')

        if not hasattr(absolute_limits, 'max_image_meta'):
            errors.append(
                'The expected absolute limit max_image_meta absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'max_personality'):
            errors.append(
                'The expected absolute limit max_personality absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'max_personality_size'):
            errors.append(
                'The expected absolute limit max_personality_size absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_sec_group_rules'):
            errors.append(
                'The expected absolute limit max_sec_group_rules absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_sec_groups'):
            errors.append(
                'The expected absolute limit max_sec_groups absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'max_server_meta'):
            errors.append(
                'The expected absolute limit max_server_meta absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_cores'):
            errors.append(
                'The expected absolute limit max_total_cores absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_floating_ips'):
            errors.append(
                'The expected absolute limit max_total_floating_ips absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_floating_ips'):
            errors.append(
                'The expected absolute limit max_total_floating_ips absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_instances'):
            errors.append(
                'The expected absolute limit max_total_instances absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_keypairs'):
            errors.append(
                'The expected absolute limit max_total_keypairs absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_private_networks'):
            errors.append(
                'The expected absolute limit max_total_private_networks '
                'absolute limit was not populated as expected')
        if not hasattr(absolute_limits, 'max_total_ram_size'):
            errors.append(
                'The expected absolute limit max_total_ram_size absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'total_cores_used'):
            errors.append(
                'The expected absolute limit total_cores_used absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'total_floating_ips_used'):
            errors.append(
                'The expected absolute limit total_floating_ips_used absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'total_instances_used'):
            errors.append(
                'The expected absolute limit total_instances_used absolute '
                'limit was not populated as expected')
        if not hasattr(absolute_limits, 'total_private_networks_used'):
            errors.append(
                'The expected absolute limit total_private_networks_used '
                'absolute limit was not populated as expected')
        if not hasattr(absolute_limits, 'total_ram_used'):
            errors.append(
                'The expected absolute limit total_ram_used absolute limit '
                'was not populated as expected')
        if not hasattr(absolute_limits, 'total_sec_groups_used'):
            errors.append(
                'The expected absolute limit total_sec_groups_used absolute '
                'limit was not populated as expected')

        self.assertEqual(
            errors, [],
            ('Unexpected errors received. Expected: No errors '
             'Received: {0}').format(errors))
