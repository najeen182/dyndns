from jfddns import update_dns_record
from jfddns.validate import JfErr
import os
import unittest
from unittest import mock
import _helper


class TestFunctionUpdateDnsRecord(unittest.TestCase):

    def setUp(self):
        os.environ['JFDDNS_CONFIG_FILE'] = _helper.config_file

    def assertRaisesMsg(self, kwargs, msg):
        with self.assertRaises(JfErr) as cm:
            update_dns_record(**kwargs)
        self.assertEqual(str(cm.exception), msg)

    def test_not_all_three_fqdn_etc(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'fqdn': 'a', 'zone_name': 'b',
             'record_name': 'c'},
            'Specify "fqdn" or "zone_name" and "record_name".'
        )

    def test_ip_1_invalid(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'fqdn': 'www.example.com',
             'ip_1': 'lol'},
            'Invalid ip address "lol"',
        )

    def test_ip_2_invalid(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'fqdn': 'www.example.com',
             'ip_2': 'lol'},
            'Invalid ip address "lol"',
        )

    def test_both_ip_same_version(self):
        self.assertRaisesMsg(
            {'secret': '12345678', 'fqdn': 'www.example.com',
             'ip_1': '1.2.3.4', 'ip_2': '1.2.3.4'},
            'The attribute "ipv4" is already set and has the value "1.2.3.4".',
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    def test_ipv4_update(self, Resolver, Update, tcp):
        resolver = Resolver.return_value
        resolver.query.side_effect = [['1.2.3.4'], ['1.2.3.5']]
        update = Update.return_value
        result = update_dns_record(secret='12345678', fqdn='www.example.com',
                                   ip_1='1.2.3.5')
        self.assertEqual(
            result,
            'UPDATED fqdn: www.example.com. old_ip: 1.2.3.4 new_ip: 1.2.3.5',
        )
        update.delete.assert_called_with('www.example.com.', 'a')
        update.add.assert_called_with('www.example.com.', 300, 'a', '1.2.3.5')


if __name__ == '__main__':
    unittest.main()