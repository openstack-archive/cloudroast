from cloudroast.stacktach.fixtures import StackTachFixture, StackTachDBFixture


class StackTachTest(StackTachFixture, StackTachDBFixture):

    @classmethod
    def setUpClass(cls):
        super(StackTachTest, cls).setUpClass()
        cls.service = 'nova'

    def test_get_event_names(self):
        """
        @summary: Verify that Get Event Names returns 200 Success response
        """
        response = self.stacktach_client.get_event_names()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)

    def test_get_host_names(self):
        """
        @summary: Verify that Get Host Names returns 200 Success response
        """
        response = self.stacktach_client.get_host_names()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.host_name)

    def test_get_deployments(self):
        """
        @summary: Verify that Get Deployments returns 200 Success response
        """
        response = self.stacktach_client.get_deployments()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.id)
            self.assertIsNotNone(element.name)

    def test_get_timings_summary(self):
        """
        @summary: Verify that Get Timings Summary returns 200 Success response
        """
        response = self.stacktach_client.get_timings_summary()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.count)
            self.assertIsNotNone(element.minimum)
            self.assertIsNotNone(element.maximum)
            self.assertIsNotNone(element.average)

    def test_get_kpi(self):
        """
        @summary: Verify that Get KPI returns 200 Success response
        """
        response = self.stacktach_client.get_kpi()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.timing)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.deployment)

    def test_get_kpi_for_tenant_id(self):
        """
        @summary: Verify that Get KPI For Tenant ID
                  returns 200 Success response
        @note:  This test requires that the tenant_id has been actively
                creating usage during the current audit period
        """

        tenant_id = (self.stacktach_db_behavior
                     .get_active_tenant_id_from_launches())
        response = self.stacktach_client.get_kpi_for_tenant_id(tenant_id)
        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.timing)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.deployment)

    def test_get_watch_events(self):
        """
        @summary: Verify that Get Watch Events returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_watch_events(deployment_id='0',
                                      service=self.service))
        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_id)
            self.assertIsNotNone(element.routing_key_type)
            self.assertIsNotNone(element.when_date)
            self.assertIsNotNone(element.when_time)
            self.assertIsNotNone(element.deployment)
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.uuid)

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

    def test_get_timings_for_event_name(self):
        """
        @summary: Verify that Get Timings For Event
            returns 200 Success response
        """
        response = (self.stacktach_client
                    .get_timings_for_event_name("compute.instance.reboot"))

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.timing)

    def test_get_timings_for_uuid(self):
        """
        @summary: Verify that Get Timings For UUID returns 200 Success response
        """

        uuid = (self.stacktach_behavior
                .get_uuid_from_event_id_details(service=self.service,
                                                event_id=self.event_id))
        response = self.stacktach_client.get_timings_for_uuid(uuid=uuid)

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.state)
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.timing)

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

    def test_get_events_for_request_id(self):
        """
        @summary: Verify that Get Events For Request ID
            returns 200 Success response
        """
        request_id = (self.stacktach_behavior
                      .get_request_id_from_event_id_details(
                          service=self.service, event_id=self.event_id))
        response = (self.stacktach_client
                    .get_events_for_request_id(request_id=request_id))

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.event_id)
            self.assertIsNotNone(element.when)
            self.assertIsNotNone(element.deployment)
            self.assertIsNotNone(element.event_name)
            self.assertIsNotNone(element.host_name)
            self.assertIsNotNone(element.state)

    def test_get_reports(self):
        """
        @summary: Verify that Get Reports
                  returns 200 Success response
        """
        response = self.stacktach_client.get_reports()

        self._verify_success_code_and_entity_len(response)
        for element in response.entity:
            self.assertIsNotNone(element.report_id)
            self.assertIsNotNone(element.start)
            self.assertIsNotNone(element.end)
            self.assertIsNotNone(element.created)
            self.assertIsNotNone(element.name)
            self.assertIsNotNone(element.version)

    def test_get_nova_usage_report_no_escaped_json(self):
        """
        @summary: Verify that the "nova usage audit" does not contain
            double encoded json
        """
        report_id = (self.stacktach_behavior
                     .get_report_id_by_report_name('nova usage audit'))
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
