#!/usr/bin/python

WINDOWSIZE = 500

DB_COMPRESSION_INTERVAL = 10

DB_COMPRESSION_SLEEP = .1

OBSERVER_SLEEP = .2

LOGFILE_RECEIVER = '/tmp/poke-receiver.log'
LOGFILE_OBSERVER = '/tmp/poke-observer.log'
LOGFILE_UI = '/tmp/poke-ui.log'
LOGFILE_DB = '/tmp/poke-db.log'

DATABASE = "/tmp/pokestore.sqlite"

CHURCH_INPUT_FILE = "./input.church"

MAKE_SCHEME_COMMAND = lambda fn: ["vicare", "--r6rs-script", fn]
