from cloudroast.stacktach.fixtures import StackTachDBFixture


class GlanceStackTachDBTest(StackTachDBFixture):

    def test_list_images(self):
        """
        @summary: Verify that list images returns 200 Success response
        """
        response = self.stacktach_dbclient.list_images()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.assertGreaterEqual(len(response.entity), 1,
                                msg="The response content is blank")
        for element in response.entity:
            self.assertIsNotNone(element.id_)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.created_at)
            self.assertIsNotNone(element.size)
            self.assertIsNotNone(element.last_raw)

    def test_list_image_deletes(self):
        """
        @summary: Verify that list ImageDeletes returns 200 Success response
        """
        response = self.stacktach_dbclient.list_image_deletes()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.assertGreaterEqual(len(response.entity), 1,
                                msg="The response content is blank")
        for element in response.entity:
            self.assertIsNotNone(element.id_)
            self.assertIsNotNone(element.raw)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.deleted_at)

    def test_list_image_exists(self):
        """
        @summary: Verify that list ImageExists returns 200 Success response
        """
        response = self.stacktach_dbclient.list_image_exists()
        self.assertEqual(response.status_code, 200,
                         self.msg.format("status code", "200",
                                         response.status_code,
                                         response.reason,
                                         response.content))
        self.assertGreaterEqual(len(response.entity), 1,
                                msg="The response content is blank")
        for element in response.entity:
            self.assertIsNotNone(element.id_)
            self.assertIsNotNone(element.uuid)
            self.assertIsNotNone(element.created_at)
            self.assertIsNotNone(element.audit_period_beginning)
            self.assertIsNotNone(element.audit_period_ending)
            self.assertIsNotNone(element.status)
            self.assertIsNotNone(element.raw)
            self.assertIsNotNone(element.send_status)
            self.assertIsNotNone(element.owner)
            self.assertIsNotNone(element.size)
            self.assertIsNotNone(element.message_id)
            self.assertIsNotNone(element.received)
