#!/usr/bin/env python3

import argparse
import ipaddress
import sys
from flask import Flask, request
from flask import render_template
from iptools import DbIP, MaxMind, DigitalElement, Software77

app = Flask(__name__)
__author__ = 'anna'

DBS = [DbIP, MaxMind, DigitalElement, Software77]


@app.route('/ip', methods=['GET', 'POST'])
def lookup_ip():
    if request.method == 'POST':
        ips = list()
        if 'iplist' in request.form and len(request.form['iplist']):
            ips = [ip for ip in request.form['iplist'].split('\n') if len(ip.strip())]
        elif 'ipfile' in request.files:
            ips = request.files['ipfile'].readlines()

        lookup = dict()
        for ip in ips:
            try:
                ip = ip.decode()
            except AttributeError:
                pass
            ip = ip.strip()
            if ip not in lookup:
                ip_as_ip = ipaddress.ip_address(ip)
                lookup[ip] = dict()
                lookup[ip]['meta'] = dict()
                lookup[ip]['meta']['occurrences'] = 1
                lookup[ip]['meta']['ip_as_int'] = int(ip_as_ip)
                lookup[ip]['meta']['dbs_agree'] = True
                country = None
                for db in DBS:
                    dbinfo = db(ip)
                    if country is not None and dbinfo.country() != country:
                        lookup[ip]['meta']['dbs_agree'] = False
                    country = dbinfo.country()
                    lookup[ip][db.name()] = dbinfo
                    try:
                        lookup[ip]['meta']['connection_speed'] = dbinfo.connection_speed()
                    except AttributeError:
                        pass
                if lookup[ip]['meta']['dbs_agree']:
                    lookup[ip]['meta']['country'] = country

            else:
                lookup[ip]['meta']['occurrences'] += 1
        filters = list()
        if 'filter' in request.form and len(request.form['filter']):
            delete_list = list()
            filters = request.form['filter'].split(',')
            for ip, info in lookup.items():
                if info['meta']['dbs_agree']:
                    if info['meta']['country'] in filters:
                        delete_list.append(ip)
            for ip in delete_list:
                del lookup[ip]

        return render_template('ip.html.j2',
                               dbs=[(db.name(), db.version()) for db in DBS],
                               ipinfo=lookup,
                               filter=','.join(filters))

    return render_template('ip.html.j2')


def setup(sys_args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, help='Port', default = 5001)
    parser.add_argument('--debug', action='store_true', default=False)
    parsed_args = parser.parse_args(sys_args)

    for db in DBS:
        print("Setting up", db.name())
        db.setup()
    return parsed_args

if __name__ == '__main__':
    args = setup(sys.argv[1:])
    app.run('0.0.0.0', port=args.port, debug=args.debug)
