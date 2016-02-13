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


class MaxMind(Geo):
    import geoip2.database
    """ Set the path to your Maxmind Country geo data file """
    MAXMIND_COUNTRY = './data/GeoLite2-Country.mmdb'

    reader = geoip2.database.Reader(MAXMIND_COUNTRY)

    def __init__(self, ip):
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


class DbIP(Geo):
    import geo_db
    DBIP_COUNTRY = './data/dbip-country.csv'

    database = geo_db.DbIP(DBIP_COUNTRY)

    def __init__(self, ip):
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


def main(args):
    dbs = [MaxMind, DbIP]
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