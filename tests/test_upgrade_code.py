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
        self.loopback_ipv4_address = "127.0.0.1"

    def test_ping(self):

        self.assertTrue(upgrade_code.ping(self, self.loopback_ipv4_address, self.test_logger))





if __name__ == '__main__':
    unittest.main()
