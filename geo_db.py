from bisect import bisect_left
import csv
import ipaddress
import os

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


def comment_stripper(iterator):
    for line in iterator:
        if line[:1] == '#':
            continue
        if not line.strip():
            continue
        yield line


class Software77(GeoDb):

    def read(self):
        """Form is start, end, registry, assigned, country code 2, country code 3, country name"""
        with open(self.file, 'r') as fh:
            reader = csv.reader(comment_stripper(fh))
            for row in reader:
                try:
                    self.ip.append(GeoItem(int(row[0]), int(row[1]), row[4]))
                except ValueError as e:
                    print(e)
                    pass


class FileDb(GeoDb):
    """
    Based on http://www.grantjenks.com/wiki/random/python_binary_search_file_by_line
    """

    def read(self):
        pass

    @staticmethod
    def key(line):
        return GeoItem(line)

    def lookup(self, x):
        ip = GeoItem(ipaddress.ip_address(x))
        # Must be greater than the maximum length of any line.
        max_line_len = 200

        start = pos = 0
        end = os.path.getsize(self.file)
        with open(self.file, 'rb') as fh:
            # Limit the number of times we binary search.
            for rpt in range(200):
                last = pos
                pos = (start + end) // 2
                fh.seek(pos-max_line_len)

                # Move the cursor to a newline boundary.
                fh.readline()

                line = fh.readline()
                linevalue = self.key(line)
                if linevalue == ip or pos == last:
                    # Seek back until we no longer have a match.
                    while True:
                        fh.seek(-max_line_len, 1)
                        fh.readline()
                        if ip != self.key(fh.readline()):
                            break

                    # Seek forward to the first match.
                    for rpt2 in range(max_line_len):
                        line = fh.readline()
                        linevalue = self.key(line)
                        if ip == linevalue:
                            return linevalue
                    else:
                        # No match was found.
                        return ""

                elif linevalue < ip:
                    start = fh.tell()
                else:
                    assert linevalue > ip
                    end = fh.tell()
            else:
                raise RuntimeError('binary search failed')


class DigitalElement(FileDb):

    @staticmethod
    def key(line):
        """
        Format: start, end, region code, connection speed, city code, country, ?, carrier
        :param line:
        :return:
        """
        try:
            line = line.decode()
        except AttributeError:
            pass
        fields = line.split(';')
        try:
            country = fields[5].upper()
            if country == 'UK':
                country = 'GB'
            return GeoItem(fields[0], fields[1], {'country': country,
                                                  'connection_speed': fields[3],
                                                  'carrier': fields[7]})
        except IndexError:
            print(line)
