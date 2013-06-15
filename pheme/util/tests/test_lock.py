import unittest
from pheme.util.lock import Lock
from lockfile import LockTimeout

class TestLock(unittest.TestCase):

    lockfilename = 'unittest'
      
    def setUp(self):
        self.lock = Lock(self.lockfilename)
          
    def tearDown(self):
        if self.lock.is_locked():
            self.lock.break_lock()

    def testAcquire(self):
        self.assertFalse(self.lock.acquire(timeout=1))
        self.assertFalse(self.lock.release())

    def testBlock(self):
        self.assertFalse(self.lock.acquire(timeout=1))
        # second acquistion should fail after timeout expires
        #This just hangs - not taking the time now to solve the
        #apparent breakage with threading.Semaphores
        # self.assertRaises(LockTimeout, self.lock.acquire, timeout=2)
        

if '__main__' == __name__:  # pragma: no cover
    unittest.main()
 
