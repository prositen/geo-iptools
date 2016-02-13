import csv
import ipaddress
import math

__author__ = 'Anna'


class GeoItem(object):
    def __init__(self, start, end, data):
        self.start = ipaddress.ip_address(start)
        self.end = ipaddress.ip_address(end)
        self.data = data
        self.version = self.start.version

    def __lt__(self, other):
        if self.version == other.version:
            return self.start < other.start
        else:
            return self.version < other.version

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

    def __len__(self):
        return len(self.ip)

    def lookup(self, ip):
        ip = ipaddress.ip_address(ip)
        return self.lookup_rec(GeoItem(ip, ip, None))

    def lookup_rec(self, ip, start=0, end=None, maxiter=None):
        if maxiter == 0:
            return ""
        if end is None:
            end = len(self)
            maxiter = math.ceil(math.log(end, 2))

        mid = start + ((end - start) // 2)
        mid_item = self.ip[mid]

        if mid_item.contains(ip):
            return mid_item
        elif mid == start:
            if self.ip[end].contains(ip):
                return self.ip[end]
            return ""
        elif mid == end:
            if self.ip[start].contains(ip):
                return self.ip[start]
            return ""
        elif ip < mid_item:
            return self.lookup_rec(ip, start, mid-1, maxiter-1)
        else:
            return self.lookup_rec(ip, mid+1, end, maxiter-1)


class DbIP(GeoDb):

    def read(self):
        """Format is "start","end","country code" """
        reader = csv.reader(open(self.file, 'r'))
        for row in reader:
            try:
                self.ip.append(GeoItem(row[0], row[1], row[2]))
            except ValueError:
                pass
