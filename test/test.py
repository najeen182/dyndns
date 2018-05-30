import unittest
from jfddns import load_config, Validate, validate_args
import os


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__),
                             'config.yml'))
        self.assertEqual(config['secret'], 12345)


class TestValidate(unittest.TestCase):

    def setUp(self):
        self.v = Validate()

    def test_ipv4_valid(self):
        self.assertEqual(str(self.v.ipv4('192.168.2.3')), '192.168.2.3')

    def test_ipv4_invalid_string(self):
        self.assertFalse(self.v.ipv4('lol'))

    def test_ipv4_invalid_ipv6(self):
        self.assertFalse(self.v.ipv4('1::2'))

    def test_ipv6_valid(self):
        self.assertEqual(str(self.v.ipv6('1::2')), '1::2')

    def test_ipv6_invalid_string(self):
        self.assertFalse(self.v.ipv6('lol'))

    def test_ipv6_invalid_ipv6(self):
        self.assertFalse(self.v.ipv6('1.2.3.4'))

    def test_zone_valid(self):
        self.assertEqual(self.v.zone('github.com'), 'github.com')

    def test_record_valid(self):
        self.assertEqual(self.v.record('sub'), 'sub')


class TestFunctionValidateArgs(unittest.TestCase):

    def test_empty_dict(self):
        self.assertEqual(
            validate_args({}, {}),
            {'message': 'The arguments “record”, “zone” and “secret” are '
                        'required.'}
        )

    def test_no_ip(self):
        self.assertEqual(
            validate_args({'record': '1', 'zone': '2', 'secret': '3'}, {}),
            {'message': 'The argument “ipv4” or the argument “ipv6” is '
                        'required.'}

        )

    def test_wrong_secret(self):
        self.assertEqual(
            validate_args(
                {'record': '1', 'zone': '2', 'secret': '3', 'ipv6': '1::2'},
                {'secret': '4'}),
            {'message': 'You specified a wrong secret key.'}
        )


if __name__ == '__main__':
    unittest.main()
