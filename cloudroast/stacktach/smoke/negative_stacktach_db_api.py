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
from cloudroast.stacktach.fixtures import StackTachDBFixture


class StackTachDBTest(StackTachDBFixture):

    def test_get_invalid_launch(self):
        """
        @summary: Verify that Get an Invalid Launch ID fails
        """
        response = self.stacktach_dbclient.get_launch('aa')
        self._verify_error_code_and_entity_none(response, 404)

    def test_get_invalid_delete(self):
        """
        @summary: Verify that Get a Invalid Delete ID fails
        """
        response = self.stacktach_dbclient.get_delete('aa')
        self._verify_error_code_and_entity_none(response, 404)

    def test_get_invalid_exist(self):
        """
        @summary: Verify that Get Invalid Exist ID fails
        """
        response = self.stacktach_dbclient.get_exist('aa')
        self._verify_error_code_and_entity_none(response, 404)

    def test_get_launches_by_invalid_date_min(self):
        """
        @summary: Verify that Get Launches by invalid minimum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min(launched_at_min="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_get_launches_by_invalid_date_max(self):
        """
        @summary: Verify that Get Launches by invalid maximum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_max(launched_at_max="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_get_launches_by_invalid_date_min_and_invalid_date_max(self):
        """
        @summary: Verify that Get Launches by invalid minimum and
            invalid maximum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min_and_date_max(
                        launched_at_min="$#@!",
                        launched_at_max="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_get_deletes_by_invalid_date_min(self):
        """
        @summary: Verify that Get Deletes by invalid minimum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min(deleted_at_min="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_get_deletes_by_invalid_date_max(self):
        """
        @summary: Verify that Get Deletes by invalid maximum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_max(deleted_at_max="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_get_deletes_by_invalid_date_min_and_invalid_date_max(self):
        """
        @summary: Verify that Get Deletes by invalid minimum and
            invalid maximum date fails
        """
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min_and_date_max(
                        deleted_at_min="$#@!",
                        deleted_at_max="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_list_launches_for_invalid_uuid(self):
        """
        @summary: Verify that List Launches by uuid fails
        """
        response = (self.stacktach_db_behavior
                    .list_launches_for_uuid(instance="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_list_deletes_for_invalid_uuid(self):
        """
        @summary: Verify that List Deletes by uuid fails

        """
        response = (self.stacktach_db_behavior
                    .list_deletes_for_uuid(instance="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def test_list_exists_for_invalid_uuid(self):
        """
        @summary: Verify that List Exists by uuid fails

        """
        response = (self.stacktach_db_behavior
                    .list_exists_for_uuid(instance="$#@!"))
        self._verify_error_code_and_entity_none(response)

    def _verify_error_code_and_entity_none(self, response,
                                           expected_error_code=400):
        self.assertEqual(response.status_code, expected_error_code,
                         self.msg.format("status code", expected_error_code,
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.assertIsNone(response.entity, "The response entity is not NONE")
