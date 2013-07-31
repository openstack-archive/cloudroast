"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.identity.fixtures import BaseIdentityAdminTest


class ServicesTest(BaseIdentityAdminTest):

    @classmethod
    def setUpClass(cls):
        super(ServicesTest, cls).setUpClass()
        cls.name = rand_name("service-test-")
        cls.type = rand_name("service-type-")
        cls.description = rand_name("service-desc-")

    def test_create_service(self):
        response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        service = response.entity
        self.addCleanup(self.tenant_client.delete_service, service.id_)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(service.name, self.name)
        self.assertEqual(service.type_, self.type)
        self.assertEqual(service.description, self.description)
        self.assertIsNotNone(service.id_)

    def test_create_service_by_unauthorized_user(self):
        response = self.demo_tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        self.assertEqual(response.status_code, 403)

    def test_create_service_with_request_without_token(self):
        response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description, requestslib_kwargs=self.auth_token)
        self.assertEqual(response.status_code, 400)

    def test_create_service_with_empty_name(self):
        """Can create a service with a blank name"""
        response = self.tenant_client.create_service(
            type_=self.type,
            description=self.description)
        service = response.entity
        self.addCleanup(self.tenant_client.delete_service, response.entity.id_)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(service.name)
        self.assertEqual(service.type_, self.type)
        self.assertEqual(service.description, self.description)

    def test_create_service_with_duplicate_data(self):
        """Can create two different services with the same name,
        type and description
        """
        first_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        first_service = first_response.entity
        self.assertEqual(first_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_service, first_service.id_)
        second_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        second_service = second_response.entity
        self.assertEqual(second_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_service, second_service.id_)
        self.assertNotEqual(first_service, second_service)
        self.assertEqual(second_service.name, first_service.name)
        self.assertEqual(second_service.type_, first_service.type_)
        self.assertEqual(first_service.description,
                         second_service.description)

    def test_list_services(self):
        create_response = self.tenant_client.create_service(
            name=self.name,
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(create_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_service, service.id_)
        list_services_response = self.tenant_client.list_services()
        services = list_services_response.entity
        self.assertEqual(list_services_response.status_code, 200)
        self.assertIn(service, services)

    def test_list_services_by_unauthorized_user(self):
        list_services_response = self.demo_tenant_client.list_services()
        self.assertEqual(list_services_response.status_code, 403)

    def test_list_services_with_request_without_token(self):
        list_services_response = self.tenant_client.list_services(
            requestslib_kwargs=self.auth_token)
        self.assertEqual(list_services_response.status_code, 401)
        self.assertIn("Could not find token, None.",
                      list_services_response.content)

    def test_delete_service(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(create_response.status_code, 200)
        delete_response = self.tenant_client.delete_service(
            service_id=service.id_)
        self.assertEqual(delete_response.status_code, 204)
        self.assertNotIn(service, self.tenant_client.list_services())

    def test_delete_service_by_unauthorized_user(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(create_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_service, service.id_)
        delete_response = self.demo_tenant_client.delete_service(
            service_id=service.id_)
        self.assertEqual(delete_response.status_code, 403)

    def test_delete_service_with_request_without_token(self):
        create_response = self.tenant_client.create_service(
            name=rand_name("service-test-"),
            type_=self.type,
            description=self.description)
        service = create_response.entity
        self.assertEqual(create_response.status_code, 200)
        self.addCleanup(self.tenant_client.delete_service, service.id_)
        delete_response = self.demo_tenant_client.delete_service(
            service_id=service.id_, requestslib_kwargs=self.auth_token)
        self.assertEqual(delete_response.status_code, 401)
        self.assertIn("Could not find token, None.", delete_response.content)

    def test_delete_non_existent_service(self):
        funky_service_id = "FUNKY_SERVICE_ID"
        delete_response = self.tenant_client.delete_service(
            service_id=funky_service_id)
        self.assertEqual(delete_response.status_code, 404)
        self.assertIn("Could not find service, {0}.".format(funky_service_id),
                      delete_response.content)
