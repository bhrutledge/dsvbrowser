import os
import unittest

from tab2html import app, models


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_nonblank_lines(self):
        input_lines = ['one\n', '\n', 'two\n', 'three\n', 'four\n', '\n']
        expected_lines = ['one', 'two', 'three', 'four']
        
        nonblank_lines = list(models.nonblank_lines(input_lines))
        self.assertEqual(nonblank_lines, expected_lines)


if __name__ == '__main__':
    unittest.main()