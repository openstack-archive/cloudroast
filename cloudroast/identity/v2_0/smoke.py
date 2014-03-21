from cloudroast.identity.v2_0.fixtures import IdentityBaseTestFixture


class BaseIdentityServiceSmoke(object):
    get_tenants_status_code = 200
    get_tenant_by_name_status_code = 200
    get_tenant_by_id_status_code = 200
    get_roles_for_tenant_status_code = 200
    get_user_by_name_status_code = 200
    get_user_by_id_status_code = 200
    get_roles_for_user_status_code = 200
    token_is_valid_status_code = 200

    def test_get_tenants(self):
        r = self.identity.client.get_tenants()
        self.assertTrue(r.status_code == self.get_tenants_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_tenant_by_name(self):
        tenant_name = self.identity.tenant_name
        r = self.identity.client.get_tenant_by_name(tenant_name)
        self.assertTrue(r.status_code == self.get_tenant_by_name_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_tenant_by_id(self):
        tenant_id = self.identity.tenant_id
        r = self.identity.client.get_tenant_by_id(tenant_id)
        self.assertTrue(r.status_code == self.get_tenant_by_id_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_roles_for_tenant(self):
        user_id = self.identity.user_id
        tenant_id = self.identity.tenant_id
        self.assertTrue(self.identity.access_data)
        r = self.identity.client.get_user_roles(tenant_id, user_id)
        self.assertTrue(r.status_code == self.get_roles_for_tenant_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_user_by_name(self):
        user_name = self.identity.username
        r = self.identity.client.get_user_by_name(user_name)
        self.assertTrue(r.status_code == self.get_user_by_name_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_user_by_id(self):
        user_id = self.identity.user_id
        r = self.identity.client.get_user_by_id(user_id)
        self.assertTrue(r.status_code == self.get_user_by_id_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_roles_for_user(self):
        user_id = self.identity.user_id
        r = self.identity.client.get_user_global_roles(user_id)
        self.assertTrue(r.status_code == self.get_roles_for_user_status_code,
                        "Status Code Fail:{0}".format(r.status_code))
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_token_is_present(self):
        # this test will fail if authentication fails
        self.assertIsNotNone(
            self.identity.client.token,
            "No token id was present in auth response")

    def test_token_is_valid(self):
        r = self.identity.client.validate_token(self.identity.client.token)
        self.assertEquals(
            r.status_code, self.token_is_valid_status_code,
            "Unable to successfully validate token")
        if r.ok:
            self.assertIsNotNone(
                r.entity, "Unable to deserialize token validation response")


class IdentityServiceSmoke(IdentityBaseTestFixture, BaseIdentityServiceSmoke):
    get_tenants_status_code = 200
    get_tenant_by_name_status_code = 200
    get_tenant_by_id_status_code = 404
    get_roles_for_tenant_status_code = 404
    get_user_by_name_status_code = 404
    get_user_by_id_status_code = 404
    get_roles_for_user_status_code = 404
    token_is_valid_status_code = 403

    @classmethod
    def setUpClass(cls):
        super(IdentityServiceSmoke, cls).setUpClass()
        cls.identity = cls.user_identity


class AdminIdentityServiceSmoke(
        IdentityBaseTestFixture, BaseIdentityServiceSmoke):
    @classmethod
    def setUpClass(cls):
        super(AdminIdentityServiceSmoke, cls).setUpClass()
        cls.identity = cls.admin_identity
