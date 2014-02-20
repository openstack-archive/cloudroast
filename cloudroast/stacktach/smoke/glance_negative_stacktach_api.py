from cloudroast.stacktach.fixtures import StackTachFixture


class GlanceStackTachTest(StackTachFixture):

    @classmethod
    def setUpClass(cls):
        super(GlanceStackTachTest, cls).setUpClass()
        cls.service = 'glance'

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
        self.assertTrue('BAD REQUEST' in response.reason,
                        msg="Expected the request to fail for reason: "
                            "Bad Request, but it didn't")
