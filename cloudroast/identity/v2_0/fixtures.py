from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.identity.composites import (
    IdentityServiceComposite, AdminIdentityServiceComposite)


class IdentityBaseTestFixture(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(IdentityBaseTestFixture, cls).setUpClass()
        cls.user_identity = IdentityServiceComposite()
        cls.user_identity.authenticate()
        cls.user_identity.load_extensions()
        cls.admin_identity = AdminIdentityServiceComposite()
        cls.admin_identity.authenticate()
        cls.admin_identity.load_extensions()
