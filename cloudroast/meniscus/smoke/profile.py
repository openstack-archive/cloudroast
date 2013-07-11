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
from cloudroast.meniscus.fixtures import ProfileFixture


class TestProfiles(ProfileFixture):

    def test_create_profile(self):
        result = self.profile_behaviors.create_new_profile()
        self.assertEqual(result['request'].status_code, 201)

    def test_delete_profile(self):
        result = self.profile_behaviors.create_new_profile()
        created_id = result['profile_id']

        resp = self.profile_behaviors.delete_profile(created_id)
        self.assertEqual(resp.status_code, 200)

    def test_get_profile(self):
        profile_results = self.profile_behaviors.create_new_profile()
        profile_id = profile_results['profile_id']
        profile_resp = self.profile_client.get_profile(profile_id)
        profile = profile_resp.entity

        self.assertEqual(profile_resp.status_code, 200,
                         'Status code should have been 200 OK')
        self.assertIsNotNone(profile)
        self.assertEqual(profile.name, self.tenant_config.profile_name)

    def test_get_all_profiles(self):
        req_one = self.profile_behaviors.create_new_profile()
        req_two = self.profile_behaviors.create_new_profile(name='pro2')

        profile_id_one = req_one['profile_id']
        profile_id_two = req_two['profile_id']

        profile_res_one = self.profile_client.get_profile(profile_id_one)
        profile_res_two = self.profile_client.get_profile(profile_id_two)

        profile_list_req = self.profile_client.get_all_profiles()
        profile_list = profile_list_req.entity

        profile_one_name = profile_res_one.entity.name
        profile_two_name = profile_res_two.entity.name

        self.assertEqual(2, len(profile_list))
        self.assertEqual(profile_one_name, self.tenant_config.profile_name)
        self.assertEqual(profile_two_name, 'pro2')

    def test_update_profile(self):
        initial_profile_results = self.profile_behaviors.create_new_profile()
        created_id = initial_profile_results['profile_id']

        # Update
        update_profile_results = self.profile_client.update_profile(
            id=created_id,
            name='updated_profile')

        self.assertEqual(update_profile_results.status_code, 200,
                         'Should have been 200 OK')

        updated_results = self.profile_client.get_profile(created_id)
        updated_name = updated_results.entity.name

        self.assertEqual(updated_name, 'updated_profile')

    def test_unlink_producer_update_profile(self):
        initial_profile_results = self.profile_behaviors.create_new_profile()
        created_id = initial_profile_results['profile_id']
        update_profile_results = self.profile_client.update_profile(
            id=created_id,
            name='updated_profile',
            producer_ids=[])
        self.assertEqual(update_profile_results.status_code, 200,
                         'Should have been 200 OK')

        updated_results = self.profile_client.get_profile(created_id)
        profile = updated_results.entity

        self.assertEqual(profile.name, 'updated_profile')
        self.assertEqual(len(profile.event_producers), 0,
                         'event producer size is 0')
