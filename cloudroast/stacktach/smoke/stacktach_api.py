from cloudroast.stacktach.fixtures import StackTachFixture


class StackTachTest(StackTachFixture):

    @classmethod
    def setUpClass(cls):
        super(StackTachTest, cls).setUpClass()
        cls.service = 'nova'

    def test_get_event_names(self):
        """
        @summary: Verify that Get Event Names
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_event_names()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_host_names(self):
        """
        @summary: Verify that Get Host Names
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_host_names()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_deployments(self):
        """
        @summary: Verify that Get Deployments
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_deployments()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_timings_summary(self):
        """
        @summary: Verify that Get Timings Summary
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_timings_summary()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_kpi(self):
        """
        @summary: Verify that Get KPI
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_kpi()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_watch_events(self):
        """
        @summary: Verify that Get Watch Events
                  returns 2xx Success response (eg: 200 ok)
        """

        response = (self.stacktach_client
                    .get_watch_events(deployment_id='1',
                                      service=self.service))
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_event_id_details(self):
        """
        @summary: Verify that Get Event ID Details
                  returns 2xx Success response (eg: 200 ok)
        """

        response = (self.stacktach_client
                    .get_event_id_details(event_id=self.event_id,
                                          service=self.service))
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_timings_for_event_name(self):
        """
        @summary: Verify that Get Timings For Event
                  returns 2xx Success response (eg: 200 ok)
        """

        response = (self.stacktach_client
                    .get_timings_for_event_name("compute.instance.reboot"))
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))

    def test_get_reports(self):
        """
        @summary: Verify that Get Reports
                  returns 2xx Success response (eg: 200 ok)
        """

        response = self.stacktach_client.get_reports()
        self.assertTrue(response.ok,
                        self.msg.format("status code", "2xx Success response",
                                        response.status_code, response.reason,
                                        response.content))
