from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import (ComputeFixture,
                                         FlavorIdNegativeDataList,
                                         ImageIdNegativeDataList,
                                         ServerIdNegativeDataList)


@DataDrivenFixture
class FuzzServersAPI(ComputeFixture):

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_get_server(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.get_server(server_id)

    @data_driven_test(dataset_source=ServerIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_delete_server(self, server_id=None):
        with self.assertRaises(ItemNotFound):
            self.servers_client.delete_server(server_id)

    @data_driven_test(dataset_source=FlavorIdNegativeDataList())
    @tags(type='negative', net='no')
    def test_create_server_with_unknown_flavor(self, flavor_id):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', self.image_ref, flavor_id)

    @data_driven_test(dataset_source=ImageIdNegativeDataList())
    @tags(type='negative', net='no')
    def test_create_server_with_unknown_image(self, image_id):
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                'testserver', image_id, self.flavor_ref)