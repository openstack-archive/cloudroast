from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cloudcafe.compute.common.exceptions import ItemNotFound
from cloudroast.compute.fixtures import (ComputeFixture,
                                         FlavorIdNegativeDataList)


@DataDrivenFixture
class FuzzFlavorsAPI(ComputeFixture):

    @data_driven_test(dataset_source=FlavorIdNegativeDataList())
    @tags(type='negative')
    def ddtest_negative_get_flavor(self, flavor_id=None):
        with self.assertRaises(ItemNotFound):
            self.flavors_client.get_flavor_details(flavor_id)

