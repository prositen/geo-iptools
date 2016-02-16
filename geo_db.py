from bisect import bisect_left
import csv
import ipaddress

__author__ = 'Anna'


class GeoItem(object):
    def __init__(self, start, end=None, data=None):
        ipstart = ipaddress.ip_address(start)
        self.start = int(ipstart)
        if end:
            self.end = int(ipaddress.ip_address(end))
        else:
            self.end = self.start
        self.data = data
        self.version = ipstart.version

    def __lt__(self, other):
        if self.version == other.version:
            return self.start < other.start and self.end < other.end
        else:
            return self.version < other.version

    def __eq__(self, other):
        return self.contains(other)

    def contains(self, other):
        """
        Ugly hack to see if either range is contained in the other
        :param other:
        :return:
        """
        if self.version == other.version:
            if (self.start <= other.start and self.end >= other.end) or (other.start <= self.start and other.end >= self.end):
                return True
        return False

    def __str__(self):
        return "{0}-{1} {2}".format(self.start, self.end, self.data)


class GeoDb(object):
    """ Do a binary search through a list of IP ranges.

    """
    def read(self):
        pass

    def __init__(self, file):
        self.file = file
        self.ip = list()
        self.read()

    def lookup(self, x):
        """Locate the leftmost value exactly equal to x"""
        ip = GeoItem(ipaddress.ip_address(x))
        i = bisect_left(self.ip, ip)
        if i != len(self.ip) and self.ip[i] == ip:
            return self.ip[i]
        return ""


class DbIP(GeoDb):

    def read(self):
        """Format is "start","end","country code" """
        with open(self.file, 'r') as fh:
            reader = csv.reader(fh)
            for row in reader:
                try:
                    self.ip.append(GeoItem(row[0], row[1], row[2]))
                except ValueError:
                    pass
