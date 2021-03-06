# pylint: disable=too-many-public-methods,fixme

import os
import shutil
import unittest

from dsvbrowser import create_app


class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.test_path = os.path.dirname(os.path.realpath(__file__))
        self.test_instance_path = os.path.join(self.test_path, 'test_instance')
        self.instance_path = os.path.join(self.test_path, 'instance')
        shutil.copytree(self.test_instance_path, self.instance_path)

        self.app = create_app(self.instance_path)

    def tearDown(self):
        shutil.rmtree(self.instance_path)
