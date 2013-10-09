from cloudroast.stacktach.fixtures import StackTachFixture


class StackTachTest(StackTachFixture):

    @classmethod
    def setUpClass(cls):
        super(StackTachTest, cls).setUpClass()
        cls.service = 'nova'

    def test_get_kpi_for_invalid_tenant_id(self):
        """
        @summary: Verify that Get KPI For an Invalid Tenant ID fails
        """

        response = self.stacktach_client.get_kpi_for_tenant_id("aa")
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertGreaterEqual(len(resp_entity_obj), 1,
                                msg="The response content is blank")
        for element in resp_entity_obj:
            self.assertIsNotNone(getattr(element, "Error"))
            self.assertIsNotNone(getattr(element, "Message"))

    def test_watch_events_with_invalid_deployment(self):
        """
        @summary: Verify that Get Watch Events with
            Invalid Deployment ID fails
        """

        response = (self.stacktach_client
                    .get_watch_events(service=self.service,
                                      deployment_id='aa'))
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertIsNone(resp_entity_obj,
                          msg="The response entity is not NONE")

    def test_get_invalid_event_id_details(self):
        """
        @summary: Verify that a Get on Invalid Event ID Details fails
        """

        response = (self.stacktach_client
                    .get_event_id_details(event_id='aa',
                                          service=self.service))
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertIsNone(resp_entity_obj,
                          msg="The response entity is not NONE")

    def test_get_timings_for_invalid_event_name(self):
        """
        @summary: Verify that a Get on Timings For Invalid Event passes,
            but has the entity length 0 as its not a valid event name.
        """

        response = (self.stacktach_client.get_timings_for_event_name("123"))
        self.assertTrue(response.ok,
                        self.msg.format("status code",
                                        "Not a 2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))
        resp_entity_obj = response.entity
        self.assertEqual(len(resp_entity_obj), 0,
                         msg="The response entity is not Empty")

    def test_get_timings_for_invalid_uuid(self):
        """
        @summary: Verify that a Get on Timings For Invalid UUID fails
        """

        response = (self.stacktach_client.get_timings_for_uuid(uuid="aa"))
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertGreaterEqual(len(resp_entity_obj), 1,
                                msg="The response content is blank")
        for element in resp_entity_obj:
            self.assertIsNotNone(getattr(element, "Error"))
            self.assertIsNotNone(getattr(element, "Message"))

    def test_get_events_for_invalid_uuid(self):
        """
        @summary: Verify that a Get on Events For Invalid UUID fails
        """

        response = (self.stacktach_client
                    .get_events_for_uuid(service=self.service,
                                         uuid="aa"))
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertGreaterEqual(len(resp_entity_obj), 1,
                                msg="The response content is blank")
        for element in resp_entity_obj:
            self.assertIsNotNone(getattr(element, "Error"))
            self.assertIsNotNone(getattr(element, "Message"))

    def test_get_events_for_invalid_request_id(self):
        """
        @summary: Verify that a Get on Events For Invalid Request ID fails
        """

        response = (self.stacktach_client
                    .get_events_for_request_id(request_id="aa"))
        self.assertFalse(response.ok,
                         self.msg.format("status code",
                                         "Not a 2xx Success response",
                                         response.status_code, response.reason,
                                         response.content))
        resp_entity_obj = response.entity
        self.assertGreaterEqual(len(resp_entity_obj), 1,
                                msg="The response content is blank")
        for element in resp_entity_obj:
            self.assertIsNotNone(getattr(element, "Error"))
            self.assertIsNotNone(getattr(element, "Message"))
