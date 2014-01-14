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


# TODO: Move this module into either a cloudcafe common location or opencafe
class DatasetGeneratorError(Exception):
    pass


class BaseDataset(object):
    """Collection of dataset generators for blockstorage-images integration
    data driven tests
    """

    @classmethod
    def _filter_model_list(cls, model_list, filter_dict=None):
        """Include only those models who match at least one criteria in the
        filter_dict dictionary
        """

        if not filter_dict:
            return model_list

        final_list = []
        for model in model_list:
            for k in filter_dict:
                if getattr(model, k) in filter_dict[k]:
                    final_list.append(model)
                    break

        return final_list
