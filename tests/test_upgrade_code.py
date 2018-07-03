# system imports
import unittest
import logging

# local imports
from capt.capt import capt
from capt.upgrade_code import upgrade_code
# from package.module import class


class test_upgrade_code(unittest.TestCase):

    def setUp(self):

        self.test_logger = capt.set_logger(self, 'test_logger', logging.DEBUG)
        self.loopback = "127.0.0.1"
        self.blackhole = "203.0.113.0" # reserved for documentation (0.0.0.0 is localhost on linux)

        self.test_list1 = ['a', 'b']
        self.test_list2 = ['b', 'c']
        self.test_list3 = ['d']
        self.test_list4 = ['d', 'e']

    def test_ping(self):

        self.assertTrue(upgrade_code.ping(self, self.loopback, self.test_logger))
        self.assertFalse(upgrade_code.ping(self, self.blackhole, self.test_logger))

    def test_compare_list(self):

        result1, result2 = upgrade_code.compare_list(self, self.test_list1, self.test_list2, self.test_logger)
        self.assertTrue(result1.pop() == 'a')
        self.assertTrue(result2.pop() == 'c')

        result1, result2 = upgrade_code.compare_list(self, self.test_list3, self.test_list4, self.test_logger)
        self.assertFalse(result1) # empty string
        self.assertTrue(result2.pop() == 'e')


if __name__ == '__main__':
    unittest.main()
