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

import re
import unittest2 as unittest
from urlparse import urlparse

from cafe.drivers.unittest.decorators import tags
from test_repo.compute.fixtures import ComputeFixture


class TestLinks(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(TestLinks, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestLinks, cls).tearDownClass()

    @tags(type='positive', net='no')
    def test_verify_server_self_link(self):
        """Verify that a server self link has the correct format"""
        self.server_resp = self.server_behaviors.create_active_server()
        self.server_id = self.server_resp.entity.id
        self.resources.add(self.server_id, self.servers_client.delete_server)
        server_self_link = self.server_resp.entity.links.self
        self.assertTrue(self._has_version(server_self_link))

        get_server_resp = self.servers_client.get_server(server_self_link)
        self.assertEqual(self.server_id, get_server_resp.entity.id)

    @tags(type='positive', net='no')
    @unittest.skip('V1 Bug:D-03447')
    def test_verify_server_bookmark_link(self):
        """Verify that server bookmark link is a link with no version number"""
        self.server_resp = self.server_behaviors.create_active_server()
        self.server_id = self.server_resp.entity.id
        self.resources.add(self.server_id, self.servers_client.delete_server)
        server_bookmark_link = self.server_resp.entity.links.bookmark

        self.assertFalse(self._has_version(server_bookmark_link))

        retrieved_server = self.servers_client.get_server(server_bookmark_link)
        self.assertEqual(self.server_id, retrieved_server.entity.id)

    @tags(type='positive', net='no')
    def test_verify_flavor_self_link(self):
        """Verify that flavor self link is a full url with a version number"""
        flavor_resp = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor_self_link = flavor_resp.entity.links.self

        self.assertTrue(self._has_version(flavor_self_link))
        # Verify that the same flavor can be retrieved using the flavor self link
        retrieved_flavor_resp = self.flavors_client.get_flavor_details(str(flavor_self_link))
        self.assertEqual(retrieved_flavor_resp.entity.id, flavor_resp.entity.id)
        self.assertEqual(retrieved_flavor_resp.entity.ram, flavor_resp.entity.ram)
        self.assertEqual(retrieved_flavor_resp.entity.swap, flavor_resp.entity.swap)

    @tags(type='positive', net='no')
    @unittest.skip('V1 Bug:D-03447')
    def test_verify_flavor_bookmark_link(self):
        """Verify that flavor bookmark link is a permanent link with no version number"""
        flavor_resp = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor_bookmark_link = flavor_resp.entity.links.bookmark

        self.assertFalse(self._has_version(flavor_bookmark_link))
        retrieved_flavor_resp = self.flavors_client.get_flavor_details(flavor_bookmark_link)
        self.assertEqual(retrieved_flavor_resp.entity.id, flavor_resp.entity.id)
        self.assertEqual(retrieved_flavor_resp.entity.ram, flavor_resp.entity.ram)
        self.assertEqual(retrieved_flavor_resp.entity.swap, flavor_resp.entity.swap)

    @tags(type='positive', net='no')
    def test_image_self_link_during_get_image(self):
        """Verify that image self link is a full url with a version number"""
        image_resp = self.images_client.get_image(self.image_ref)
        image_self_link = image_resp.entity.links.self

        self.assertTrue(self._has_version(image_self_link))

        # Verify that the same image can be retrieved using the image self link
        retrieved_image_with_self_link = self.images_client.get_image(image_self_link)
        self.assertEqual(retrieved_image_with_self_link.entity.id, image_resp.entity.id)

    @tags(type='positive', net='no')
    @unittest.skip('V1 Bug:D-03447')
    def test_image_bookmark_link_during_get_image(self):
        """Verify that image bookmark link is a permanent link with no version number"""
        image_resp = self.images_client.get_image(self.image_ref)
        image_bookmark_link = image_resp.entity.links.bookmark

        self.assertFalse(self._has_version(image_bookmark_link))

        # Verify that the same image can be retrieved using the image bookmark link
        retrieved_image_with_bookmark_link = self.images_client.get_image(image_bookmark_link)
        self.assertEqual(retrieved_image_with_bookmark_link.entity.id, image_resp.entity.id)

    def _has_version(self, link):
        return re.search('^/v+\d', urlparse(link).path) is not None

    def _parse_ref_to_retrieve_id(self, ref):
        temp = ref.rsplit('/')
        #Return the last item, which is the image id
        return temp[len(temp) - 1]
