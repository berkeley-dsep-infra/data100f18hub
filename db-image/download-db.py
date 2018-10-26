#!/usr/bin/env python
# vim: set et sw=4 ts=4:
"""
Ensure a database file has been downloaded onto the host.

Runs every 15m and only relies on the standard library.
"""
import os
import time
from urllib.request import urlretrieve

assert 'DB_URL' in os.environ
assert 'DB_PATH' in os.environ

HZ=900

def make_parent_dir(filename):
    parent_dir = os.path.dirname(filename)
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

def main():
    db_url  = os.environ['DB_URL']
    db_path = os.environ['DB_PATH']

    make_parent_dir(db_path)

    while True:
        if os.path.exists(db_path):
            print("{} exists".format(db_path))
        else:
            print("{} does not exist. downloading".format(db_path))
            (filename, headers) = urlretrieve(db_url, db_path)
            print("downloaded {}".format(filename))
        time.sleep(HZ)

if __name__ == '__main__':
    main()
