from jfddns import \
    load_config, \
    update_dns_record
import os
import unittest
from unittest import mock
import _helper


class TestConfig(unittest.TestCase):

    def test_config(self):
        config = load_config(os.path.join(os.path.dirname(__file__), 'files',
                             'config.yml'))
        self.assertEqual(config['secret'], 12345678)


class TestFunctionUpdateDnsRecord(unittest.TestCase):

    @mock.patch('jfddns.config_file', '/tmp/jfddns-xxx.yml')
    def test_no_config_file(self):
        self.assertEqual(update_dns_record(), 'The configuration file '
                         '/tmp/jfddns-xxx.yml could not be found.')

    @mock.patch('jfddns.config_file', os.path.join(_helper.files_dir,
                'invalid-yaml.yml'))
    def test_config_invalid_yaml_format(self):
        self.assertEqual(update_dns_record(), 'The configuration file is in '
                         'a invalid YAML format.')

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_no_secret(self):
        self.assertEqual(
            update_dns_record(config={'lol': 'lol'}),
            'Your configuration must have a "secret" key, for example: '
            '"secret: VDEdxeTKH"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_invalid_secret(self):
        self.assertEqual(
            update_dns_record(config={'secret': 'ä'}),
            'The secret must be at least 8 characters long and may not '
            'contain any non-alpha-numeric characters.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_no_nameserver(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678'}),
            'Your configuration must have a "nameserver" key, '
            'for example: "nameserver: 127.0.0.1"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_no_zones(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1'}),
            'Your configuration must have a "zones" key.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zones_string(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': 'lol'}),
            'Your "zones" key must contain a list of zones.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zones_empty_list(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': []}),
            'You must have at least one zone configured, for example:'
            '"- name: example.com" and "twig_key: tPyvZA=="'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_no_name(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': [{'lol': '-'}]}),
            'Your zone dictionary must contain a key "name"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_invalid_zone_name(self):
        config = {'secret': '12345678', 'nameserver': '127.0.0.1',
                  'zones': [{'name': 'l o l'}]}
        self.assertEqual(
            update_dns_record(config=config),
            'Invalid zone name: l o l',
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_no_tsig_key(self):
        self.assertEqual(
            update_dns_record(config={'secret': '12345678',
                                      'nameserver': '127.0.0.1',
                                      'zones': [{'name': 'a'}]}),
            'Your zone dictionary must contain a key "tsig_key"'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_config_zone_invalid_tsig_key(self):
        config = {'secret': '12345678', 'nameserver': '127.0.0.1',
                  'zones': [{'name': 'a', 'tsig_key': 'xxx'}]}
        self.assertEqual(
            update_dns_record(config=config),
            'Invalid tsig key: xxx',
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_secret_not_matches(self):
        self.assertEqual(
            update_dns_record(secret='lol'),
            'You specified a wrong secret key.'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_not_all_three_fqdn_etc(self):
        self.assertEqual(
            update_dns_record(secret='12345678', fqdn='a', zone_name='b',
                              record_name='c'),
            'Specify “fqdn” or "zone_name" and "record_name".'
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_ip_1_invalid(self):
        self.assertEqual(
            update_dns_record(secret='12345678', fqdn='www.example.com',
                              ip_1='lol'),
            '"ip_1" is not a valid IP address.',
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_ip_2_invalid(self):
        self.assertEqual(
            update_dns_record(secret='12345678', fqdn='www.example.com',
                              ip_2='lol'),
            '"ip_2" is not a valid IP address.',
        )

    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_both_ip_same_version(self):
        self.assertEqual(
            update_dns_record(secret='12345678', fqdn='www.example.com',
                              ip_1='1.2.3.4', ip_2='1.2.3.4'),
            '"ip_1" and "ip_2" using the same ip version.',
        )

    @mock.patch('dns.query.tcp')
    @mock.patch('dns.update.Update')
    @mock.patch('dns.resolver.Resolver')
    @mock.patch('jfddns.config_file', _helper.config_file)
    def test_ipv4_update(self, Resolver, Update, tcp):
        result = update_dns_record(secret='12345678', fqdn='www.example.com',
                                   ip_1='1.2.3.5')

        self.assertEqual(result, 'ok')

        resolver = Resolver.return_value
        resolver.query.side_effect = [['1.2.3.4'], ['1.2.3.5']]
        update = Update.return_value
        update.delete.assert_called_with('www.')
        update.add.assert_called_with('www.', 300, 'a', '1.2.3.5')


if __name__ == '__main__':
    unittest.main()
