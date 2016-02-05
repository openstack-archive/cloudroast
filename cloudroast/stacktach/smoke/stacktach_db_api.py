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
from datetime import datetime, timedelta

from cloudcafe.common.tools.time import string_to_datetime
from cloudroast.stacktach.fixtures import StackTachDBFixture


class StackTachDBTest(StackTachDBFixture):

    def test_list_launches(self):
        """
        @summary: Verify that List Launches records
            returns 200 Success response
        """
        response = self.stacktach_dbclient.list_launches()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launches_entity_attribute_values(response.entity)

    def test_list_deletes(self):
        """
        @summary: Verify that List Deletes records
                  returns 200 Success response
        """
        response = self.stacktach_dbclient.list_deletes()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_deletes_entity_attribute_values(response.entity)

    def test_list_exists(self):
        """
        @summary: Verify that List Exists records
                  returns 200 Success response
        """
        response = self.stacktach_dbclient.list_exists()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_exists_entity_attribute_values(response.entity)

    def test_get_launch(self):
        """
        @summary: Verify that Get Launch record by event id
                  returns 200 Success response
        """
        response = self.stacktach_dbclient.list_launches()
        event_id = response.entity[0].id_

        response = self.stacktach_dbclient.get_launch(event_id)
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launch_entity_attribute_values(response.entity)

    def test_get_delete(self):
        """
        @summary: Verify that Get Delete record by event id
                  returns 200 Success response
        """
        response = self.stacktach_dbclient.list_deletes()
        event_id = response.entity[0].id_

        response = self.stacktach_dbclient.get_delete(event_id)
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_delete_entity_attribute_values(response.entity)

    def test_get_exist(self):
        """
        @summary: Verify that Get Exist record by event id
                  returns 200 Success response
             1.  List all exists
             2.  Get the first exists entry's exists id
             4.  Check for exists id
        """
        response = self.stacktach_dbclient.list_exists()
        exists_id = response.entity[0].id_

        response = self.stacktach_dbclient.get_exist(exists_id)
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_exist_entity_attribute_values(response.entity)

    def test_get_launches_by_date_min(self):
        """
        @summary: Verify that Get Launches by minimum date
                  returns 200 Success response
        """
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min(launched_at_min=date_min))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launches_entity_attribute_values(response.entity)

    def test_get_launches_by_date_max(self):
        """
        @summary: Verify that Get Launches by maximum date
                  returns 200 Success response
            1.  Get Launches for the past few days
            2.  Iterate through the list to look for a non null launched_at
            3.  Add 1 day to the launched at for maximum date filter
        """

        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min(launched_at_min=date_min))

        for launch in response.entity:
            if launch.launched_at is not None:
                launched_at = str(launch.launched_at)
                break
        # Microseconds may or may not be returned
        date_obj = string_to_datetime(launched_at)
        date_max = date_obj + timedelta(days=1)
        response = (self.stacktach_db_behavior
                    .list_launches_by_date_max(launched_at_max=date_max))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launches_entity_attribute_values(response.entity)

    def test_get_launches_by_date_min_and_max(self):
        """
        @summary: Verify that Get Launches by minimum and maximum date
                  returns 200 Success response
        """
        date_max = datetime.utcnow()
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))

        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min_and_date_max(
                        launched_at_min=date_min,
                        launched_at_max=date_max))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launches_entity_attribute_values(response.entity)

    def test_get_deletes_by_date_min(self):
        """
        @summary: Verify that Get Deletes by minimum date
                  returns 200 Success response
        """
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min(deleted_at_min=date_min))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_deletes_entity_attribute_values(response.entity)

    def test_get_deletes_by_date_max(self):
        """
        @summary: Verify that Get Deletes by maximum date
                  returns 200 Success response
            1.  Get Deletes for the past few days
            2.  Choose the first deleted at for maximum date filter
        """

        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min(deleted_at_min=date_min))

        deleted_at = response.entity[0].deleted_at
        # Microseconds may or may not be returned
        date_max = string_to_datetime(deleted_at)
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_max(deleted_at_max=date_max))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_deletes_entity_attribute_values(response.entity)

    def test_get_deletes_by_date_min_and_max(self):
        """
        @summary: Verify that Get Deletes by minimum and maximum date
                  returns 200 Success response
        """
        date_max = datetime.utcnow()
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))

        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min_and_date_max(
                        deleted_at_min=date_min,
                        deleted_at_max=date_max))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_deletes_entity_attribute_values(response.entity)

    def test_list_launches_for_uuid(self):
        """
        @summary: Verify that List Launches by uuid
                  returns 200 Success response
        """
        date_max = datetime.utcnow()
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))

        response = (self.stacktach_db_behavior
                    .list_launches_by_date_min_and_date_max(
                        launched_at_min=date_min,
                        launched_at_max=date_max))
        uuid = response.entity[0].instance
        response = (self.stacktach_db_behavior
                    .list_launches_for_uuid(instance=uuid))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_launches_entity_attribute_values(response.entity)

    def test_list_deletes_for_uuid(self):
        """
        @summary: Verify that List Deletes by uuid
                  returns 200 Success response
        """
        date_max = datetime.utcnow()
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))

        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min_and_date_max(
                        deleted_at_min=date_min,
                        deleted_at_max=date_max))
        uuid = response.entity[0].instance
        response = (self.stacktach_db_behavior
                    .list_deletes_for_uuid(instance=uuid))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_deletes_entity_attribute_values(response.entity)

    def test_list_exists_for_uuid(self):
        """
        @summary: Verify that List Exists by uuid
                  returns 200 Success response
             1.  Find a server that was deleted 2 days ago
             2.  End of audit period was x days_passed where x is configurable.
             3.  Check for exists event
        """
        date_max = datetime.utcnow() - timedelta(days=2)
        date_min = datetime.utcnow() - timedelta(days=int(self.days_passed))
        self.verify_list_exist_for_deleted_uuid_from_range(date_min, date_max)

    def verify_list_exist_for_deleted_uuid_from_range(self, date_min, date_max):
        """
        @summary: Verify that List Exists by uuid
                  returns 200 Success response for
                  the audit period.
             1.  Begining of audit period is date_min. (I.e., 30 days ago)
             2.  End of audit period is date_max. (I.e., 1 day ago)
             3.  Check for exists event
        """
        response = (self.stacktach_db_behavior
                    .list_deletes_by_date_min_and_date_max(
                        deleted_at_min=date_min, deleted_at_max=date_max))

        self.assertGreater(len(response.entity), 0,
                msg="There were not any deleted instances found between {0} "
                "and {1}".format(date_min, date_max))

        uuid = response.entity[0].instance

        response = (self.stacktach_db_behavior
                    .list_exists_for_uuid(instance=uuid))

        self.assertGreater(len(response.entity), 0, msg="There were not any "
                "exists events for deleted instance {0}".format(uuid))

        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.verify_exists_entity_attribute_values(response.entity)

    def test_list_exists_for_uuid_previous_day(self):
        """
        @summary: Verify that List Exists by uuid
                  returns 200 Success response for
                  recent instances.
             1.  Find a server that was deleted 24 and 48 hours ago.
             2.  Check for exists event
        """
        date_max = datetime.utcnow() - timedelta(days=1)
        date_min = datetime.utcnow() - timedelta(days=2)
        self.verify_list_exist_for_deleted_uuid_from_range(date_min, date_max)


    def verify_launch_entity_attribute_values(self, entity):
        """
        @summary: Verify all attributes of a server launch is NOT None
        """
        self.assertIsNotNone(entity.id_)
        self.assertIsNotNone(entity.request_id)
        self.assertIsNotNone(entity.instance)
        self.assertIsNotNone(entity.tenant)
        self.assertIsNotNone(entity.os_distro)
        self.assertIsNotNone(entity.os_version)
        self.assertIsNotNone(entity.instance_type_id)
        self.assertIsNotNone(entity.instance_flavor_id)
        self.assertIsNotNone(entity.launched_at)
        self.assertIsNotNone(entity.os_architecture)
        self.assertIsNotNone(entity.rax_options)

    def verify_launches_entity_attribute_values(self, response_entity):
        """
        @summary: Verify all attributes of the server launches list is NOT None
        """
        self.assertGreaterEqual(len(response_entity), 1,
                                msg="The response content is blank")
        for element in response_entity:
            self.verify_launch_entity_attribute_values(element)

    def verify_exist_entity_attribute_values(self, entity):
        """
        @summary: Verify all attributes of a server exist is NOT None
        """
        self.assertIsNotNone(entity.id_)
        self.assertIsNotNone(entity.raw)
        self.assertIsNotNone(entity.message_id)
        self.assertIsNotNone(entity.instance)
        self.assertIsNotNone(entity.instance_type_id)
        self.assertIsNotNone(entity.instance_flavor_id)
        self.assertIsNotNone(entity.launched_at)
        self.assertIsNotNone(entity.tenant)
        self.assertIsNotNone(entity.status)
        self.assertIsNotNone(entity.send_status)
        self.assertIsNotNone(entity.received)
        self.assertIsNotNone(entity.os_distro)
        self.assertIsNotNone(entity.os_architecture)
        self.assertIsNotNone(entity.os_version)
        self.assertIsNotNone(entity.rax_options)
        self.assertIsNotNone(entity.audit_period_beginning)
        self.assertIsNotNone(entity.audit_period_ending)
        self.assertIsNotNone(entity.bandwidth_public_out)

    def verify_exists_entity_attribute_values(self, response_entity):
        """
        @summary: Verify all attributes of the server exists list is NOT None
        """
        self.assertGreaterEqual(len(response_entity), 1,
                                msg="The response content is blank")
        for element in response_entity:
            self.verify_exist_entity_attribute_values(element)

    def verify_delete_entity_attribute_values(self, entity):
        """
        @summary: Verify all attributes of a server delete is NOT None
        """
        self.assertIsNotNone(entity.id_)
        self.assertIsNotNone(entity.raw)
        self.assertIsNotNone(entity.instance)
        self.assertIsNotNone(entity.deleted_at)
        self.assertIsNotNone(entity.launched_at)

    def verify_deletes_entity_attribute_values(self, response_entity):
        """
        @summary: Verify all attributes of the server delete list is NOT None
        """
        self.assertGreaterEqual(len(response_entity), 1,
                                msg="The response content is blank")
        for element in response_entity:
            self.verify_delete_entity_attribute_values(element)
