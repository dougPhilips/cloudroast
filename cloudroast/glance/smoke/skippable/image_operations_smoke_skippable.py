"""
Copyright 2015 Rackspace

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

import unittest

from cloudcafe.glance.config import ImagesConfig

from cloudroast.glance.fixtures import ImagesFixture

images_config = ImagesConfig()


@unittest.skipUnless(images_config.allow_post_images,
                     'Functionality disabled with provided endpoint')
class ImageOperationsSmokeSkippable(ImagesFixture):

    @classmethod
    def setUpClass(cls):
        super(ImageOperationsSmokeSkippable, cls).setUpClass()
        cls.registered_images = cls.images.behaviors.register_new_images(
            count=2)

    def test_register_image(self):
        """
        @summary: Register an image

        1) Register an image
        2) Verify that the response code is 201
        3) Add the image to the resource pool for deletion
        """

        resp = self.images.client.register_image()
        self.assertEqual(resp.status_code, 201,
                         self.status_code_msg.format(201, resp.status_code))
        image = resp.entity
        self.resources.add(image.id_, self.images.client.delete_image)

    @unittest.skipUnless(images_config.allow_put_image_file,
                         'Functionality disabled with provided endpoint')
    def test_store_image_file(self):
        """
        @summary: Store an image file data

        1) Store an image file data passing the image id and file data
        2) Verify that the response code is 204
        """

        image = self.registered_images.pop()
        file_data = self.images.behaviors.read_data_file(
            self.images.config.test_file)

        resp = self.images.client.store_image_file(image.id_, file_data)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

    @unittest.skipUnless(images_config.allow_put_image_file and
                         images_config.allow_get_image_file,
                         'Functionality disabled with provided endpoint')
    def test_get_image_file(self):
        """
        @summary: Get an image file data

        1) Store an image file data passing the image id and file data
        2) Verify that the response code is 204
        3) Get the image file data passing the image id
        4) Verify that the response code is 200
        """

        image = self.registered_images.pop()
        file_data = self.images.behaviors.read_data_file(
            self.images.config.test_file)

        resp = self.images.client.store_image_file(image.id_, file_data)
        self.assertEqual(resp.status_code, 204,
                         self.status_code_msg.format(204, resp.status_code))

        resp = self.images.client.get_image_file(image.id_)
        self.assertEqual(resp.status_code, 200,
                         self.status_code_msg.format(200, resp.status_code))