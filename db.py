#!/usr/bin/python

"""
Tools for storing pickled, indexed data points in a sqlite table.
"""

import cPickle as pickle
import logging
import os
import settings
import sqlite3
import time

logger = logging.getLogger('poke-db')
logger.addHandler(logging.FileHandler(settings.LOGFILE_DB)) 
logger.setLevel(logging.INFO)
    
def connect(db_file):
    return sqlite3.connect(db_file)

def reset(db_file):
    if os.path.exists(db_file):
        os.remove(db_file)
    conn = connect(db_file)
    c = conn.cursor()
    c.execute('''create table results (trans text, ind real)''')
    conn.commit()
    c.close()    
    return conn

def store(conn, data, index):
    try:
        t = (pickle.dumps(data), index)
    except pickle.PicklingError:
        logger.warn("can't pickle object: %s" % data)
    else:
        try:
            c = conn.cursor()
            c.execute("""insert into results values (?, ?)""", t)
            conn.commit()
            c.close()
        except sqlite3.OperationalError:
            logger.info("db locked, ignoring datapoint...")

def getdata(conn):
    try:
        c = conn.cursor()
        vals = list(c.execute("select * from results"))
        c.close()
    except sqlite3.DatabaseError:
        logger.warn("database access error, skipping...")
    else:
        return unpickle_all(vals)

def unpickle_all(vals):    
    for (r, i) in vals:
        try:
            yield i, pickle.loads(r.encode('utf-8'))
        except pickle.UnpicklingError:
            logger.warn("pickle couldn't decode row: %s" % r)
            yield i, "err"

def show(conn):
     for (r, i) in getdata(conn):
        logger.info(r, i)

def compress(conn, index):
    try:
        c = conn.cursor()
        t = (index-500,)
        c.execute("delete from results where ind < ?", t)
        conn.commit()
        c.close()
    except sqlite3.OperationalError:
        logger.info("db locked, not compressing...")

def test():
    conn = reset("/tmp/dbtest.sqlite")
    store(conn, "foo", 1)
    store(conn, "bar", 2)
    show(conn)
    conn.close()
    conn = connect("/tmp/dbtest.sqlite")
    store(conn, "baz", 3)
    show(conn)
    conn.close()

if __name__ == "__main__":
    test()
