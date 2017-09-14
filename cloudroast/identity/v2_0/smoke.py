from cloudroast.identity.v2_0.fixtures import IdentityBaseTestFixture


class BaseIdentityServiceSmoke(object):
    GET_TENANTS_STATUS_CODE = 200
    GET_TENANT_BY_NAME_STATUS_CODE = 200
    GET_TENANT_BY_ID_STATUS_CODE = 200
    GET_ROLES_FOR_TENANT_STATUS_CODE = 200
    GET_USER_BY_NAME_STATUS_CODE = 200
    GET_USER_BY_ID_STATUS_CODE = 200
    GET_ROLES_FOR_USER_STATUS_CODE = 200
    TOKEN_IS_VALID_STATUS_CODE = 200

    def test_get_tenants(self):
        r = self.identity.client.get_tenants()
        self.assertEqual(r.status_code, self.GET_TENANTS_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_tenant_by_name(self):
        tenant_name = self.identity.tenant_name
        r = self.identity.client.get_tenant_by_name(tenant_name)
        self.assertEqual(r.status_code, self.GET_TENANT_BY_NAME_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_tenant_by_id(self):
        tenant_id = self.identity.tenant_id
        r = self.identity.client.get_tenant_by_id(tenant_id)
        self.assertEqual(r.status_code, self.GET_TENANT_BY_ID_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_roles_for_tenant(self):
        user_id = self.identity.user_id
        tenant_id = self.identity.tenant_id
        self.assertTrue(self.identity.access_data)
        r = self.identity.client.get_user_roles(tenant_id, user_id)
        self.assertEqual(r.status_code, self.GET_ROLES_FOR_TENANT_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_user_by_name(self):
        user_name = self.identity.username
        r = self.identity.client.get_user_by_name(user_name)
        self.assertEqual(r.status_code, self.GET_USER_BY_NAME_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_user_by_id(self):
        user_id = self.identity.user_id
        r = self.identity.client.get_user_by_id(user_id)
        self.assertEqual(r.status_code, self.GET_USER_BY_ID_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_get_roles_for_user(self):
        user_id = self.identity.user_id
        r = self.identity.client.get_user_global_roles(user_id)
        self.assertEqual(r.status_code, self.GET_ROLES_FOR_USER_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")

    def test_token_is_present(self):
        # this test will fail if authentication fails
        self.assertIsNotNone(
            self.identity.client.token, "No token id in auth response")

    def test_token_is_valid(self):
        r = self.identity.client.validate_token(self.identity.client.token)
        self.assertEqual(r.status_code, self.TOKEN_IS_VALID_STATUS_CODE)
        if r.ok:
            self.assertIsNotNone(r.entity, "Invalid body in response")


class IdentityServiceSmoke(IdentityBaseTestFixture, BaseIdentityServiceSmoke):
    GET_TENANTS_STATUS_CODE = 200
    GET_TENANT_BY_NAME_STATUS_CODE = 200
    GET_TENANT_BY_ID_STATUS_CODE = 404
    GET_ROLES_FOR_TENANT_STATUS_CODE = 404
    GET_USER_BY_NAME_STATUS_CODE = 404
    GET_USER_BY_ID_STATUS_CODE = 404
    GET_ROLES_FOR_USER_STATUS_CODE = 404
    TOKEN_IS_VALID_STATUS_CODE = 403

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
