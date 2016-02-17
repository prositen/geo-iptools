#!/usr/bin/env python3
import fileinput
import sys


class Geo(object):

    def country(self):
        return None

    @staticmethod
    def version():
        return None

    @staticmethod
    def name():
        return "Geo"

    @staticmethod
    def setup():
        pass


class MaxMind(Geo):
    """ Set the path to your Maxmind Country geo data file """
    MAXMIND_COUNTRY = './data/GeoLite2-Country.mmdb'
    reader = None

    def __init__(self, ip):
        if self.reader is None:
            self.setup()
        try:
            self.response = self.reader.country(ip)
        except ValueError:
            self.response = None

    def country(self):
        try:
            code = self.response.country.iso_code
            if code is None:
                code = '?'
            return code
        except AttributeError:
            return '?'

    @staticmethod
    def version():
        return "February 2016"

    @staticmethod
    def name():
        return "Maxmind"

    @staticmethod
    def setup():
        import geoip2.database
        MaxMind.reader = geoip2.database.Reader(MaxMind.MAXMIND_COUNTRY)


class DbIP(Geo):
    DBIP_COUNTRY = './data/dbip-country-v4.csv'
    database = None

    def __init__(self, ip):
        if self.database is None:
            self.setup()
        self.data = self.database.lookup(ip)

    def country(self):
        try:
            return self.data.data
        except AttributeError:
            return '?'

    @staticmethod
    def version():
        return "February 2016"

    @staticmethod
    def name():
        return "DbIP"

    @staticmethod
    def setup():
        import geo_db
        DbIP.database = geo_db.DbIP(DbIP.DBIP_COUNTRY)


class DigitalElement(Geo):
    DE_COUNTRY = './data/geodb.csv.20160211122650'
    database = None

    def __init__(self, ip):
        if self.database is None:
            self.setup()
        self.data = self.database.lookup(ip)

    def country(self):
        try:
            return self.data.data['country']
        except AttributeError:
            return '?'

    def connection_speed(self):
        try:
            return self.data.data['connection_speed']
        except AttributeError:
            return '?'

    @staticmethod
    def version():
        return "2016-02-11"

    @staticmethod
    def name():
        return "Digital Element"

    @staticmethod
    def setup():
        import geo_db
        DigitalElement.database = geo_db.DigitalElement(DigitalElement.DE_COUNTRY)


class Software77(Geo):
    FILENAME = "./data/IpToCountry.csv"
    database = None

    def __init__(self, ip):
        if self.database is None:
            self.setup()
        self.data = self.database.lookup(ip)

    def country(self):
        try:
            return self.data.data
        except AttributeError:
            return '?'

    @staticmethod
    def version():
        return "2016-02-15"

    @staticmethod
    def name():
        return "Software 77"

    @staticmethod
    def setup():
        import geo_db
        Software77.database = geo_db.Software77(Software77.FILENAME)


def main(args):
    dbs = [MaxMind, DbIP, DigitalElement, Software77]
    ip_to_response = dict()
    for ip in fileinput.input(args, openhook=fileinput.hook_compressed):
        try:
            ip = ip.decode()
        except AttributeError:
            pass
        ip = ip.strip()
        if ip not in ip_to_response:
            ip_to_response[ip] = dict()
            for db in dbs:
                ip_to_response[ip][db.name()] = db(ip)

    print("ip", ",".join([db.name() for db in dbs]), sep=',')
    for ip, value in ip_to_response.items():
        print(ip, ",".join([value[db.name()].country() for db in dbs]), sep=',')


if __name__ == '__main__':
    main(sys.argv[1:])