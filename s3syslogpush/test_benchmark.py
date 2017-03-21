from .main import process_file
from multiprocessing import Pool
from threading import RLock
import time

def test_benchmark():
    start = time.time()
    error, (in_event_count, out_event_count, error_count) = process_file('test_data/demo_data_deviceeventlog.json', 'test_data')
    end = time.time()

    total_time = end - start
    total_events = (in_event_count + out_event_count + error_count )
    print("")
    print("Single Core Test:")
    print("Processed {0} events in {1:.2f} seconds".format(total_events, total_time))
    print("{0:.2f} events per second".format(total_events/total_time))

    assert error == None
    assert in_event_count == 5263
    assert out_event_count == 9584
    assert error_count == 32


class Callback(object):
    def __init__(self, in_filename, out_filename):
        self.args = in_filename, out_filename

        self.valid = False
        self.error = None
        self.result = None

        self._lock = RLock()
        self.total_events = 0

    def __call__(self, *args, **kwargs):
        # Note that this gets run in the apply_async callback thread *not* the main thread
        self.error, self.result = args[0]

        with self._lock:
            self.total_events += self.result[0] + self.result[1] + self.result[2]


def test_multicore():
    pool = Pool(processes=4)

    args = 'test_data/demo_data_deviceeventlog.json', 'test_data'

    cb = Callback(*args)
    start = time.time()

    for i in range(100):
        pool.apply_async(process_file, args=args, callback=cb)

    pool.close()
    pool.join()

    end = time.time()

    total_time = end - start
    total_events = cb.total_events
    print("")
    print("4 Core Test:")
    print("Processed {0} events in {1:.2f} seconds".format(total_events, total_time))
    print("{0:.2f} events per second".format(total_events / total_time))
    assert total_events == 1487900


