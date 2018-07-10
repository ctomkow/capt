#!/usr/bin/env python3

# Craig Tomkow
# June 28, 2018
#
# Unit tests for capt.py

# system imports
import unittest
import logging
from unittest.mock import patch

# local imports
from .context import capt
from capt.capt import Capt
# from package.module import class

class test_capt(unittest.TestCase):


    def setUp(self):

        self.test_logger = Capt.set_logger(self, 'test_logger', logging.DEBUG)
        self.empty_dict = {}
        self.one_dict = {'code_upgrade': 'yes'}
        self.two_dict = {'code_upgrade': 'yes', 'test_code_upgrade': 'yes'}
        self.one_bad_dict = {'fail': 'yes'}
        self.one_test_dict = {'test_code_upgrade': 'yes'}
        self.devices = ['10.10.10.10']

    def test_set_logger(self):

        self.assertTrue(Capt.set_logger(self, 'T.E.S.T', logging.INFO))

    def test_valid_proc_num(self):

        self.assertFalse(Capt.valid_proc_num(self, self.empty_dict, self.test_logger))
        self.assertFalse(Capt.valid_proc_num(self, self.two_dict, self.test_logger))
        self.assertTrue(Capt.valid_proc_num(self, self.one_dict, self.test_logger))

    def test_valid_concurrent_num(self):

        for i in range(-1,8):
            if i <= 0 or i >= 6:
                self.assertFalse(Capt.valid_concurrent_num(self, i, self.test_logger))
            if i >= 1 and i <= 5:
                self.assertTrue(Capt.valid_concurrent_num(self, i, self.test_logger))

    @patch('builtins.input', return_value='yes')
    def test_valid_proc_type(self, input):

        self.assertFalse(Capt.valid_proc_type(self, self.empty_dict, self.devices, self.test_logger))
        self.assertFalse(Capt.valid_proc_type(self, self.one_bad_dict, self.devices, self.test_logger))
        self.assertTrue(Capt.valid_proc_type(self, self.one_dict, self.devices, self.test_logger))
        self.assertTrue(Capt.valid_proc_type(self, self.one_test_dict, self.devices, self.test_logger))

    @patch('builtins.input', return_value='x')
    def test_valid_proc_type_a(self, input):

        self.assertFalse(Capt.valid_proc_type(self, self.one_dict, self.devices, self.test_logger))
        self.assertFalse(Capt.valid_proc_type(self, self.one_test_dict, self.devices, self.test_logger))

    @patch('builtins.input', return_value='')
    def test_valid_proc_type_b(self, input):

        self.assertFalse(Capt.valid_proc_type(self, self.one_dict, self.devices, self.test_logger))
        self.assertFalse(Capt.valid_proc_type(self, self.one_test_dict, self.devices, self.test_logger))


if __name__ == '__main__':
    unittest.main()
