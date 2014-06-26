from cloudroast.stacktach.fixtures import StackTachFixture


class GlanceStackTachTest(StackTachFixture):

    @classmethod
    def setUpClass(cls):
        super(GlanceStackTachTest, cls).setUpClass()
        cls.service = 'glance'
        cls.event_type = 'image.create'
        cls.event_id = (cls.stacktach_behavior
                        .get_event_id_from_event_type_details(
                            event_type=cls.event_type,
                            service=cls.service))

    def test_get_event_names(self):
        """
        @summary: Verify that Get Event Names returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_event_names(service=self.service))

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)

    def wip_test_get_host_names(self):
        """
        @summary: Verify that Get Host Names returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_host_names(service=self.service))
        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.host_name)

    def test_get_watch_events(self):
        """
        @summary: Verify that Get Watch Events returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_watch_events(deployment_id='0',
                                      service=self.service))
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", 200,
                                         response.status_code, response.reason,
                                         response.content))

    def test_get_event_id_details(self):
        """
        @summary: Verify that Get Event ID Details returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_event_id_details(event_id=self.event_id,
                                          service=self.service))

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.category)
            self.assertIsNotNone(element.publisher)
            self.assertIsNotNone(element.event_id)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.service)
            self.assertIsNotNone(element.when)
            self.assertIsNotNone(element.host_name)
            self.assertIsNotNone(element.state)
            self.assertIsNotNone(element.deployment)
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.request_id)
            self.assertIsNotNone(element.actual_event)

    def test_get_events_for_uuid(self):
        """
        @summary: Verify that Get Events For UUID returns 200 Success response
        """
        uuid = (self.stacktach_behavior
                .get_uuid_from_event_id_details(service=self.service,
                                                event_id=self.event_id))
        response = (self.stacktach_client
                    .get_events_for_uuid(uuid=uuid, service=self.service))

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_id)
            self.assertIsNotNone(element.when)
            self.assertIsNotNone(element.deployment)
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.host_name)
            self.assertIsNotNone(element.state)

    def test_get_image_events_report_no_escaped_json(self):
        """
        @summary: Verify that the "nova usage audit" does not contain
            double encoded json
        """
        report_id = (self.stacktach_behavior
                     .get_report_id_by_report_name('image events audit'))
        response = (self.stacktach_client
                    .get_report_details(report_id))
        self.assertNotIn('\\', response.json(),
                         self.msg.format("Double encoded json",
                                         "No backslashes",
                                         "Backslashes",
                                         "Escaped characters",
                                         response.json()))

    def _verify_success_code_and_entity_len(self, response,
                                            expected_success_code=200):
        self.assertEqual(response.status_code, expected_success_code,
                         self.msg.format("status code", expected_success_code,
                                         response.status_code, response.reason,
                                         response.content))
        self.assertGreaterEqual(len(response.entity), 1,
                                msg="The response content is blank")
