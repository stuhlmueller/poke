#!/usr/bin/python

"""
Indefinitely reads in pickled data from sys.in and stores it in a
database.
"""

from datetime import datetime
import cPickle as pickle
import db
import logging
import settings
import sys
import sys
import time

def timestamp():
    return long(datetime.now().strftime("%H%M%S")) * 10**6

def main():
    logger = logging.getLogger('poke-receiver')
    logger.addHandler(logging.FileHandler(settings.LOGFILE_RECEIVER)) 
    logger.setLevel(logging.INFO)    
    logger.info("receiver.py started")
    conn = db.connect(settings.DATABASE)
    run = True
    i = timestamp()
    while run:
        i += 1
        try:
            data = pickle.load(sys.stdin)
        except EOFError:
            run = False
        except pickle.UnpicklingError:
            logger.error("couldn't unpickle sys.stdin, ignoring...")
        else:            
            db.store(conn, data, i)
            logger.info("data stored: %s %s" % (i, data))
        if i % settings.DB_COMPRESSION_INTERVAL == 0:
            db.compress(conn, i)
            conn.close()
            try:
                time.sleep(settings.DB_COMPRESSION_SLEEP)
            except KeyboardInterrupt:
                run = False
            else:
                conn = db.connect(settings.DATABASE)
                logger.info("db compressed, reconnected")
    conn.close()

main()
