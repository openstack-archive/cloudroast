from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import tags, DataDrivenClass

from cloudcafe.identity.v3.config import (
    ServiceAdmin, IdentityAdmin, UserAdmin, UserManage, DefaultUser)
from cloudroast.identity.v3.fixture import IdentityV3Fixture


class UserDataset(DatasetList):

    def __init__(self):
        test_cases = [
            {"name": "ServiceAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": ServiceAdmin}},
            {"name": "IdentityAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": IdentityAdmin}},
            {"name": "UserAdmin", "data": {
                "get_service_catalog_resp": 200,
                "user_config": UserAdmin}},
            {"name": "UserManage", "data": {
                "get_service_catalog_resp": 200,
                "user_config": UserManage}},
            {"name": "DefaultUser", "data": {
                "get_service_catalog_resp": 200,
                "user_config": DefaultUser}}]
        for test_case in test_cases:
            self.append_new_dataset(test_case["name"], test_case["data"])


@DataDrivenClass(UserDataset())
class TestCatalog(IdentityV3Fixture):
    """
    @summary Test to verify that the catalog information is retrieved based on
    the user token that is passed in
    """
    get_service_catalog_resp = None
    user_config = None

    @tags('positive', type='regression')
    def test_get_service_catalog(self):
        """ Retrieves the catalog information with all different clients """
        resp = self.v3_composite.apis.catalog.client.get_catalog()
        self.assertEqual(resp.status_code, self.get_service_catalog_resp)

        if self.get_service_catalog_resp == 200:

            self.assertEqual("{0}/auth/catalog".format(
                self.v3_composite.ident_config.global_authentication_endpoint),
                resp.entity.links.self_)

            # Catalog verification
            for catalog in resp.entity.catalog:
                self.assertIsNotNone(
                    catalog.type,
                    msg='Catalog expected type received {0}'.format(
                        catalog.type))
                for service in catalog.endpoints:
                    self.assertIsNotNone(
                        service.interface,
                        msg='Service interface expected received {0}'.format(
                            service.interface))
                    self.assertIsNotNone(
                        service.url,
                        msg='Service url expected received {0}'.format(
                            service.url))
                    self.assertIsNotNone(
                        service.id,
                        msg='Service id expected received {0}'.format(
                            service.id))

    @tags('positive', type='regression')
    def test_list_users(self):
        """ List users is not listed as one of the call for MVP """
        resp = self.v3_composite.apis.users.client.list_users()
        self.assertEqual(resp.status_code, 403)
