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
from cafe.drivers.unittest.decorators import memoized
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.objectstorage.composites import ObjectStorageComposite


class ObjectStorageUser(object):
    def __init__(self, name, id_, password):
        self.name = name
        self.id_ = id_
        self.passwd = password
        self.token = None
        self.storage_url = None
        self.client = None
        self.behaviors = None
        self.roles = []


class ObjectStorageFixture(BaseTestFixture):
    """
    @summary: Base fixture for objectstorage tests
    """

    @classmethod
    @memoized
    def required_version(cls, *required_versions):
        """
        Test decorator to skip tests if the version of swift does not
        match the required version provided.  If unable to retrieve the
        version, the default behavior will be to run the test.
        Configuration of what version swift is running can be done from the
        objectstorage config file.

        Note: "lambda func: func" is from the Python unit tests example
              "25.3.6. Skipping tests and expected failures":

        def skipUnlessHasattr(obj, attr):
            if hasattr(obj, attr):
                return lambda func: func

            return unittest.skip("{!r} doesn't have {!r}".format(obj, attr))

        http://docs.python.org/2/library/unittest.html

        @param required_version: condition and version required to run the
                                 test. examples:
                                    '=1.11.0.54' - run if swift version is ==
                                    '1.11.0.54'  - same as above
                                    '<1.11.0.54' - run if swift version is <
                                    '>1.11.0.54' - run if swift version is >
        @type required_version: string
        @return: a function indicating either to run or skip the test
                 based on the results of the version comparison.
        @rtype: function
        """

        def decorator(func):
            # TODO: This is not ideal, should change this to support
            # multiple versions
            required_version = required_versions[0]
            objectstorage_api_config = ObjectStorageComposite().config
            behaviors = ObjectStorageComposite().behaviors

            swift_version = objectstorage_api_config.version
            if not swift_version and objectstorage_api_config.use_swift_info:
                info = behaviors.get_swift_info()
                swift_version = info.get(
                    'swift', {'version': None}).get('version', None)

            if not swift_version:
                return func

            if required_version.startswith('<'):
                required_version = required_version.lstrip('<')
                compare_func = lambda sv, tv: sv < tv
                extra_message = ' less than'
            elif required_version.startswith('>'):
                required_version = required_version.lstrip('>')
                compare_func = lambda sv, tv: sv > tv
                extra_message = ' greater than'
            else:
                required_version = required_version.lstrip('=')
                compare_func = lambda sv, tv: sv.startswith(tv)
                extra_message = ''

            if compare_func(swift_version, required_version):
                func

            setattr(func, '__unittest_skip__', True)
            setattr(
                func, '__unittest_skip_why__',
                'swift running version {0}, requires version{1}: {2}'.format(
                    swift_version, extra_message, required_version))
            return func
        return decorator

    @classmethod
    @memoized
    def required_features(cls, *required_features):
        """
        Test decorator to skip tests if features are not configured in swift.
        Configuration of what features are enabled can be done from the
        objectstorage config file.

        Note: "lambda func: func" is from the Python unit tests example
              "25.3.6. Skipping tests and expected failures":

        def skipUnlessHasattr(obj, attr):
            if hasattr(obj, attr):
                return lambda func: func
            return unittest.skip("{!r} doesn't have {!r}".format(obj, attr))

        http://docs.python.org/2/library/unittest.html
        """

        def decorator(func):
            objectstorage_api_config = ObjectStorageComposite().config
            behaviors = ObjectStorageComposite().behaviors

            features = behaviors.get_configured_features()

            if features == objectstorage_api_config.ALL_FEATURES:
                return func

            if features == objectstorage_api_config.NO_FEATURES:
                setattr(func, '__unittest_skip__', True)
                setattr(func, '__unittest_skip_why__', 'Skipping All Features')

            features = features.split()
            missing_reqs = False
            for req in required_features:
                if req not in features:
                    missing_reqs = True
                    break

            if missing_reqs:
                setattr(func, '__unittest_skip__', True)
                setattr(
                    func, '__unittest_skip_why__',
                    'requires features: {0}'.format(
                        ', '.join(required_features)))

            return func
        return decorator

    @classmethod
    def setUpClass(cls):
        super(ObjectStorageFixture, cls).setUpClass()
        object_storage_api = ObjectStorageComposite()

        cls.auth_info = object_storage_api.auth_info
        cls.objectstorage_api_config = object_storage_api.config
        cls.storage_url = object_storage_api.storage_url
        cls.auth_token = object_storage_api.auth_token
        cls.base_container_name = (
            cls.objectstorage_api_config.base_container_name)
        cls.client = object_storage_api.client
        cls.behaviors = object_storage_api.behaviors

    def create_temp_container(self, descriptor='', headers=None):
        """
        Creates a temporary container, which will be deleted upon cleanup.

        rtype:   string
        returns: The name of the container created.
        """
        container_name = \
            self.behaviors.generate_unique_container_name(descriptor)
        self.client.create_container(container_name, headers=headers)
        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])
        return container_name
