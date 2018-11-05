#!/usr/bin/env python
# vim: set et sw=4 ts=4:
"""
Ensure a database file has been downloaded onto the host.

Runs every 15m and only relies on the standard library.
"""
import os
import time
from urllib.request import urlretrieve

assert 'DB_URLS' in os.environ
assert 'DB_DIR'  in os.environ

HZ=900

def db_path(db_dir, db_url):
    fname = os.path.basename(db_url)
    return os.path.join(db_dir, fname)

def main():
    db_urls = os.environ['DB_URLS'].split(';')
    db_dir  = os.environ['DB_DIR']

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    while True:
        for db_url in db_urls:
            filename = db_path(db_dir, db_url)

            if os.path.exists(filename):
                print("{} exists".format(filename))
                continue

            print("{} does not exist. downloading".format(filename))
            (filename, headers) = urlretrieve(db_url, filename)
            print("downloaded {}".format(filename))
        time.sleep(HZ)

if __name__ == '__main__':
    main()
