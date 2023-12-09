import unittest

from common import Defer

class TestCommon(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_config(self):
        self.c = 0 

        def add1():
            self.c += 1

        def add10():
            self.c += 10

        with Defer(add1):
            self.assertEqual(self.c, 0)

        with Defer(add1, add10) as defer:
            self.assertEqual(self.c, 1)
            print(defer)

        self.assertEqual(self.c, 12)

        with Defer() as defer:
            defer(add10)
            self.assertEqual(self.c, 12)

        self.assertEqual(self.c, 22)


if __name__ == '__main__':
    unittest.main()