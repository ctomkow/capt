#!/usr/bin/env python3

# Craig Tomkow
# June 28, 2018
#
# Unit tests for capt.py

# system imports
import unittest
import logging

# local imports
from capt import capt
from unittest.mock import patch

class test_capt(unittest.TestCase):


    def setUp(self):

        self.test_logger = capt.capt.set_logger(self, 'test_logger', logging.DEBUG)
        self.proc_dict = {'test_code_upgrade': 'yes'}
        self.devices = ['10.10.10.10']

    @patch('builtins.input', return_value='yes')
    def test_config_validated(self, input):

        for i in range(-1,8):
            if i <= 0 or i >= 6:
                self.assertFalse(capt.capt.config_validated(
                    self, self.proc_dict, self.devices, i, self.test_logger))
            if i >= 1 and i <= 5:
                self.assertTrue(capt.capt.config_validated(
                        self, self.proc_dict, self.devices, 5, self.test_logger))


if __name__ == '__main__':
    unittest.main()