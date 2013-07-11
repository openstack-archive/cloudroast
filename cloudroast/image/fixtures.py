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

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.images.v1_0.client import ImagesClient as ImagesV1Client
from cloudcafe.images.v2_0.client import ImageClient as ImagesV2Client


class ImageFixture(BaseTestFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageFixture, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(ImageFixture, cls).tearDownClass()
        cls.resources.release()


class ImageV1Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageFixture, cls).setUpClass()
        cls.api_client = ImagesV1Client()


class ImageV2Fixture(ImageFixture):
    @classmethod
    def setUpClass(cls):
        super(ImageFixture, cls).setUpClass()
        cls.api_client = ImagesV2Client()
