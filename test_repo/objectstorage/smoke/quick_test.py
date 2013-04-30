from test_repo.objectstorage.fixtures import ObjectStorageFixture


class QuickTest(ObjectStorageFixture):
    def test_create_container(self):
        response = self.client.create_container('quick_test_container')
        self.assertTrue(response.ok)

        response = self.client.delete_container('quick_test_container')
        self.assertTrue(response.ok)
