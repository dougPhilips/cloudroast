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

import calendar
import time
import unittest2 as unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.images.common.types import TaskStatus, TaskTypes
from cloudroast.images.fixtures import ImagesFixture


class TestCreateImportTask(ImagesFixture):

    @tags(type='smoke')
    @unittest.skip('Bug, Redmine #4241')
    def test_create_import_task(self):
        """
        @summary: Create import task

        1) Create import task
        2) Verify that the response code is 201
        3) Verify that the task properties are returned correctly
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        task_creation_time_in_sec = calendar.timegm(time.gmtime())
        self.assertEqual(response.status_code, 201)

        task = response.entity

        errors = self.images_behavior.validate_task(task)

        self._validate_specific_task_properties(
            task, task_creation_time_in_sec)

        self.assertListEqual(errors, [])

    @tags(type='positive', regression='true')
    def test_attempt_duplicate_import_task(self):
        """
        @summary: Attempt to create a duplicate of the same import take

        1) Create import task
        2) Verify that the response code is 201
        3) Create another import take with the same input properties
        4) Verify that the response code is 201
        5) Verify that the first import task is not the same as the second
        import task
        """

        input_ = {'image_properties': {},
                  'import_from': self.import_from,
                  'import_from_format': self.import_from_format}

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        task = response.entity

        response = self.images_client.create_task(
            input_=input_, type_=TaskTypes.IMPORT)
        self.assertEqual(response.status_code, 201)

        alt_task = response.entity

        self.assertNotEqual(task, alt_task)

    def _validate_specific_task_properties(self, task,
                                           task_creation_time_in_sec):
        """
        @summary: Validate that the created task contains the expected
        properties
        """

        errors = []

        get_created_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.created_at)
        get_updated_at_delta = self.images_behavior.get_creation_delta(
            task_creation_time_in_sec, task.updated_at)

        if task.status != TaskStatus.PENDING:
            errors.append(self.error_msg.format(
                'status', TaskStatus.PENDING, task.status))
        if get_created_at_delta > self.max_created_at_delta:
            errors.append(self.error_msg.format(
                'created_at delta', self.max_created_at_delta,
                get_created_at_delta))
        if task.input_.image_properties != {}:
            errors.append(self.error_msg.format(
                'image_properties', not {}, task.input_.image_properties))
        if task.input_.import_from != self.import_from:
            errors.append(self.error_msg.format(
                'import_from', self.import_from, task.input_.import_from))
        if task.input_.import_from_format != self.import_from_format:
            errors.append(self.error_msg.format(
                'import_from_format', self.import_from_format,
                task.input_.import_from_format))
        if get_updated_at_delta > self.max_updated_at_delta:
            errors.append(self.error_msg.format(
                'updated_at delta', self.max_updated_at_delta,
                get_updated_at_delta))
        if task.type_ != TaskTypes.IMPORT:
            errors.append(self.error_msg.format(
                'type_', TaskTypes.IMPORT, task.type_))
        if task.result is not None:
            errors.append(self.error_msg.format(
                'result', None, task.result))
        if task.owner != self.user_config.tenant_id:
            errors.append(self.error_msg.format(
                'owner', self.user_config.tenant_id, task.owner))

        self.assertListEqual(errors, [])