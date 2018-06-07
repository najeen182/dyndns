"""Deal with different kind of names (FQDNs (Fully Qualified Domain Names),
record and zone names)

``record_name`` + ``zone_name`` = ``fqdn``

"""

from jfddns.validate import JfErr
import binascii
import dns.name
import re


def validate_hostname(hostname):
    if hostname[-1] == ".":
        # strip exactly one dot from the right, if present
        hostname = hostname[:-1]
    if len(hostname) > 253:
        raise JfErr(
            'The hostname "{}..." is longer than 253 characters.'
            .format(hostname[:10])
        )

    labels = hostname.split(".")

    tld = labels[-1]
    if re.match(r"[0-9]+$", tld):
        raise JfErr(
            'The TLD "{}" of the hostname "{}" must be not all-numeric.'
            .format(tld, hostname)
        )

    allowed = re.compile(r"(?!-)[a-z0-9-]{1,63}(?<!-)$", re.IGNORECASE)
    for label in labels:
        if not allowed.match(label):
            raise JfErr(
                'The label "{}" of the hostname "{}" is invalid.'
                .format(label, hostname)
            )

    return str(dns.name.from_text(hostname))


def validate_tsig_key(tsig_key):
    try:
        dns.tsigkeyring.from_text({'tmp.org.': tsig_key})
        return tsig_key
    except binascii.Error:
        raise JfErr('Invalid tsig key: "{}"'.format(tsig_key))


class Zone(object):

    def __init__(self, zone_name, tsig_key):
        self.zone_name = validate_hostname(zone_name)
        self.tsig_key = validate_tsig_key(tsig_key)

    def split_fqdn(self, fqdn):
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = validate_hostname(fqdn)
        record_name = fqdn.replace(self.zone_name, '')
        if len(record_name) > 0 and len(record_name) < len(fqdn):
            return (record_name, self.zone_name)

    def build_fqdn(self, record_name):
        record_name = validate_hostname(record_name)
        return record_name + self.zone_name


class Zones(object):

    def __init__(self, zones_config):
        self.zones = {}
        for zone_config in zones_config:
            zone = Zone(
                zone_name=zone_config['name'],
                tsig_key=zone_config['tsig_key']
            )
            self.zones[zone.zone_name] = zone

    def split_fqdn(self, fqdn):
        """Split hostname into record_name and zone_name
        for example: www.example.com -> www. example.com.
        """
        fqdn = validate_hostname(fqdn)
        for zone_name, zone in self.zones.items():
            record_name = fqdn.replace(zone.zone_name, '')
            if len(record_name) > 0 and len(record_name) < len(fqdn):
                return (record_name, zone.zone_name)
        return False

    def get_zone_by_name(self, zone_name):
        zone_name = validate_hostname(zone_name)
        if zone_name in self.zones:
            return self.zones[validate_hostname(zone_name)]
        else:
            raise JfErr('Unkown zone"{}'.format(zone_name))


class Fqdn(object):

    def __init__(self, zones, fqdn=None, zone_name=None, record_name=None):
        self.fqdn = None
        """The Fully Qualified Domain Name (e. g. ``www.example.com.``)"""

        self.zone_name = None
        """The zone name (e. g. ``example.com.``)"""

        self.record_name = None
        """The name resource record (e. g. ``www.``)"""

        if fqdn and zone_name and record_name:
            raise JfErr('Specify "fqdn" or "zone_name" and "record_name".')

        self.zones = zones

        if fqdn:
            self.fqdn = fqdn
            split = self.zones.split_fqdn(fqdn)
            if split:
                self.record_name = split[0]
                self.zone_name = split[1]

        if not fqdn and zone_name and record_name:
            self.record_name = validate_hostname(record_name)
            self.zone_name = validate_hostname(zone_name)
            zone = self.zones.get_zone_by_name(self.zone_name)
            self.fqdn = zone.build_fqdn(self.record_name)

        if not self.record_name:
            return JfErr('Value "record_name" is required.')

        if not self.zone_name:
            return JfErr('Value "zone_name" is required.')
