#!/usr/bin/python

"""
Restarts church-loop.ss whenever the monitored Church file changes.
"""

from pytools import run_async
from pytools.async import AsyncThread
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import logging
import settings
import time
import sys

logger = logging.getLogger('poke-observer')
logger.addHandler(logging.FileHandler(settings.LOGFILE_OBSERVER))
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


def file_nonempty(filename):
    s = open(filename).read()
    if s.strip():
        return True
    else:
        return False


class ChurchProcess(object):

    def __init__(self):
        self.thread = None

    def start(self):
        if file_nonempty(settings.CHURCH_INPUT_FILE):
            self.thread = AsyncThread(settings.MAKE_SCHEME_COMMAND("./church-loop.ss"))
            self.thread.start()
        else:
            logger.info("input file empty, skipping church-loop...")
    
    def stop(self):
        if self.thread:
            self.thread.stop()
    
    def restart(self):
        self.stop()
        self.start()

    def show_status(self):
        if self.thread:
            out = self.thread.out.read_new()
            err = self.thread.err.read_new()
            if out.strip():
                logger.info(out)
            if err.strip():
                logger.info(err)        

        
class ModifiedEventHandler(FileSystemEventHandler):

    def __init__(self):
        self.churchProcess = ChurchProcess()
        self.churchProcess.start()
        
    def on_modified(self, event):
        super(ModifiedEventHandler, self).on_modified(event)
        if not event.is_directory:
            logger.info("file modified: %s" % event.src_path)
            self.churchProcess.restart()
            logger.info("process restart initiated.")

    def show_process_status(self):
        self.churchProcess.show_status()


def start_observer():
    event_handler = ModifiedEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=settings.CHURCH_INPUT_FILE, recursive=False)
    observer.start()
    logger.info("observer started.")
    try:
        while True:
            event_handler.show_process_status()
            time.sleep(settings.OBSERVER_SLEEP)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_observer()
