'''base class for transports'''

import time
import threading

import sistats

class Checker(object):
    '''base class to check for stats'''

    def __init__(self):
        self.last_vals = {}
        self.last_time = 0.0
        self.check_time = 0.0

    def check_stats(self, name, function, delta_calculator=None):
        '''check stats for *name* using *function* if it's not the
        first time and *delta_calculator* is not None, calculate delta
        too'''

        try:
            data = function()
            self.send_stats(name, data)

            if name in self.last_vals and delta_calculator is not None:
                old = self.last_vals[name]
                delta = delta_calculator(old, data)

                self.send_delta_stats(name, delta)

            self.last_vals[name] = data
        except Exception as error:
            print "error fetching data from", name, error

    def send_stats(self, name, data):
        '''send stats somewhere'''
        raise NotImplementedError()

    def send_delta_stats(self, name, data):
        '''send delta stats somewhere'''
        raise NotImplementedError()

    def check(self):
        '''check for stats'''
        self.last_time = self.check_time
        self.check_time = time.time()

        self.check_stats("cpu", sistats.get_cpu_stats,
                            sistats.get_cpu_stats_delta)
        self.check_stats("mem", sistats.get_mem_stats,
                            sistats.get_mem_stats_delta)
        self.check_stats("net", sistats.get_net_stats,
                            sistats.get_net_stats_delta)
        self.check_stats("disk", sistats.get_disk_stats,
                            sistats.get_disk_stats_delta)
        self.check_stats("fs", sistats.get_fs_stats,
                            sistats.get_fs_stats_delta)

    def on_exit(self):
        '''cleanup resources'''
        pass

class ConsoleChecker(Checker):
    '''checker class that sends the stats to the console'''

    def __init__(self):
        Checker.__init__(self)

    def send_stats(self, name, data):
        '''send stats somewhere'''
        sistats.pretty_print(name, data)

    def send_delta_stats(self, name, data):
        '''send delta stats somewhere'''
        sistats.pretty_print(name + " diff", data)

    def on_exit(self):
        '''cleanup resources'''
        print "closing"

class ThreadChecker(threading.Thread):
    '''class to check for stats on a thread'''

    def __init__(self, checker, check_interval=10):
        threading.Thread.__init__(self)
        self.check_interval = check_interval
        self.checker = checker
        self.quit = False

    def stop(self):
        '''call it to exit after the next check'''
        self.quit = True

    def run(self):
        '''main thread function'''
        while not self.quit:
            self.checker.check()
            time.sleep(self.check_interval)

        self.checker.on_exit()

def main_loop(checker, check_interval=10):
    '''create a thread checker and wait till ctrl + c'''
    listener = ThreadChecker(checker, check_interval)

    try:
        print "starting checker, press ctrl + c to stop"
        listener.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "ctrl + c detected, asking checker to stop"
        listener.stop()

    print "waiting for it to finish"
    listener.join()
    print "exiting"

def main():
    '''main function if this module is called, starts a mqtt listener'''
    checker = ConsoleChecker()
    main_loop(checker)

if __name__ == "__main__":
    main()

