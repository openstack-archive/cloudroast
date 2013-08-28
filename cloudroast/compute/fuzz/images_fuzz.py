from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import (ComputeFixture,
                                         ImageIdNegativeDataList,
                                         ServerIdNegativeDataList)


@DataDrivenFixture
class FuzzImageAPI(ComputeFixture):

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_get_image(self, image_id=None):
        with self.assertRaises(ItemNotFound):
            self.images_client.get_image(image_id)

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_delete_image(self, image_id=None):
        with self.assertRaises(ItemNotFound):
            self.images_client.delete_image(image_id)

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_create_image(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.create_image(server_id, 'test')