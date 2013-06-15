import datetime
import logging
import lockfile
import os, sys, threading

def now_str():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

CRITICAL_SECTION = threading.Lock()

class Lock(object):
    """Local implementation class for wrapping the locking mechanism
    needed to protect resources that can't handle concurrent use.

    NB - the implementation of lockfile.FileLock appears to ignore
    request from the same process, it's only a cross process locking
    mechanism.  Therefore, we include a semaphore to provide redundant
    protection and protect any attempts in the same process as well.

    """
    lockdir = '/var/lock'

    def __init__(self, filename='UNNAMED_LOCKFILE'):
            self.lockfile =\
                lockfile.FileLock(os.path.join(self.lockdir,filename))
            self.semaphore = threading.Semaphore()

    def acquire(self, timeout=None):
        logging.debug("Attempt to acquire lock %s from PID %d at %s",
                      self.lockfile.path, os.getpid(), now_str())
        try:
            CRITICAL_SECTION.acquire()
            self.lockfile.acquire(timeout)
            self.semaphore.acquire()
        finally:
            CRITICAL_SECTION.release()
        logging.debug("Successful acquisition of lock %s from PID %d at %s",
                      self.lockfile.path, os.getpid(), now_str())

    def release(self):
        try:
            CRITICAL_SECTION.acquire()
            self.semaphore.release()
            self.lockfile.release()
        finally:
            CRITICAL_SECTION.release()
        logging.debug("Released lock %s from PID %d at %s",
                      self.lockfile.path, os.getpid(), now_str())

    def break_lock(self):
        try:
            CRITICAL_SECTION.acquire()
            self.lockfile.break_lock()
            self.semaphore.release()
        finally:
            CRITICAL_SECTION.release()
        logging.debug("Broke lock %s from PID %d at %s",
                      self.lockfile.path, os.getpid(), now_str())

    def is_locked(self):
        return self.lockfile.is_locked()

    def __del__(self):
        if self.lockfile.is_locked():  # pragma: no cover
            print >> sys.stderr, "WARNING: found lockfile '%s' still "\
                "locked during garbage collection, assuming it's owned "\
                "by another process" %\
                self.lockfile.path
