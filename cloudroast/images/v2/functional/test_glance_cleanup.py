"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.decorators import tags
from cloudroast.images.fixtures import ObjectStorageIntegrationFixture


class TestImagesCleanUp(ObjectStorageIntegrationFixture):

    @tags(type='glance-cleanup')
    def test_images_cleanup(self):
        """
        @summary: Cleanup images - Delete all servers for primary and alternate
        users, Delete all containers and files for primary and second users,
        Delete all images for all users
        """

        # Delete are servers for the primary user
        count = 1
        response = self.servers_client.list_servers()
        servers = response.entity
        print '{0} server(s) for primary user'.format(len(servers))
        for server in servers:
            self.servers_client.delete_server(server_id=server.id)
            print '{0} - deleted {1}'.format(count, server.id)
            count += 1

        # Delete all servers for the alternate user
        count = 1
        response = self.alt_servers_client.list_servers()
        servers = response.entity
        print '{0} server(s) for alternate user'.format(len(servers))
        for server in servers:
            self.alt_servers_client.delete_server(server_id=server.id)
            print '{0} - deleted {1}'.format(count, server.id)
            count += 1

        # Delete all containers and objects for the primary user
        count = 1
        format_ = {"format": "json"}
        files = self.images_config.do_not_delete_files
        response = self.object_storage_client.list_containers(params=format_)
        self.assertEqual(response.status_code, 200)
        containers = response.entity
        print '{0} container(s) for primary user'.format(len(containers))
        for container in containers:
            response = self.object_storage_client.list_objects(
                container_name=container.name, params=format_)
            self.assertEqual(response.status_code, 200)
            objects = response.entity
            if container.name == 'test_container_segments':
                print '{0} - ignored {1}'.format(count, container.name)
                count += 1
            elif (container.name != self.images_config.export_to and
                  container.name != self.images_config.alt_export_to):
                for object_ in objects:
                    response = self.object_storage_client.delete_object(
                        container_name=container.name,
                        object_name=object_.name)
                    self.assertEqual(response.status_code, 204)
                response = self.object_storage_client.delete_container(
                    container_name=container.name)
                self.assertEqual(response.status_code, 204)
                print '{0} - deleted {1}'.format(count, container.name)
                count += 1
            else:
                for object_ in objects:
                    if object_.name not in files:
                        response = self.object_storage_client.delete_object(
                            container_name=container.name,
                            object_name=object_.name)
                        self.assertEqual(response.status_code, 204)
                print '{0} - cleared {1}'.format(count, container.name)
                count += 1

        # Delete all containers and objects for the alternate user
        count = 1
        format_ = {"format": "json"}
        files = self.images_config.do_not_delete_files
        response = self.alt_object_storage_client.list_containers(
            params=format_)
        self.assertEqual(response.status_code, 200)
        containers = response.entity
        print '{0} container(s) for alternate user'.format(len(containers))
        for container in containers:
            response = self.alt_object_storage_client.list_objects(
                container_name=container.name, params=format_)
            self.assertEqual(response.status_code, 200)
            objects = response.entity
            if container.name == 'test_container_segments':
                print '{0} - ignored {1}'.format(count, container.name)
                count += 1
            elif (container.name != self.images_config.export_to and
                  container.name != self.images_config.alt_export_to):
                for object_ in objects:
                    response = self.alt_object_storage_client.delete_object(
                        container_name=container.name,
                        object_name=object_.name)
                    self.assertEqual(response.status_code, 204)
                response = self.alt_object_storage_client.delete_container(
                    container_name=container.name)
                self.assertEqual(response.status_code, 204)
                print '{0} - deleted {1}'.format(count, container.name)
                count += 1
            else:
                for object_ in objects:
                    if object_.name not in files:
                        response = (
                            self.alt_object_storage_client.delete_object(
                                container_name=container.name,
                                object_name=object_.name))
                        self.assertEqual(response.status_code, 204)
                print '{0} - cleared {1}'.format(count, container.name)
                count += 1

        # Delete all images for every user
        for user in self.user_list:
            user_behavior = self.user_list[user][self.BEHAVIOR]
            user_client = self.user_list[user][self.CLIENT]
            count = 1
            owner = self.user_list[user][self.ACCESS_DATA].token.tenant.id_
            images = user_behavior.list_images_pagination(owner=owner)
            print '{0} image(s) for {1}'.format(len(images), user)
            for image in images:
                if image.name != 'donotdelete':
                    response = user_client.update_image(
                        image.id_, replace={'protected': False})
                    self.assertEqual(response.status_code, 200)
                    response = user_client.delete_image(image.id_)
                    self.assertEqual(response.status_code, 204)
                    print '{0} - deleted {1}'.format(count, image.id_)
                    count += 1
        images = user_behavior.list_images_pagination(owner=owner)
        self.assertLessEqual(len(images), 1)
