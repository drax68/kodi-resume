##### XBMC Resume by Matt Huisman #####

import threading

# A timer thread to call a function at a set interval
class Timer(threading.Thread):
    def __init__(self, interval, function, continuous=False):
        super(Timer, self).__init__()
        
        self._interval = int(interval)
        self._function = function
        self._continuous = continuous
        self._stop = threading.Event()
        self._resetted = True
        
    # Changes the time between ticks
    def setInterval(self, interval):
        self._interval = interval
        self.reset()

    # Stops the timer
    def stop(self):
        self._continuous = False
        self._stop.set()

    # Starts the timer
    def run(self):
        while True:
            self._loop()
            self.reset()
            if ( not self._continuous ): break

    # Loop until tick
    def _loop(self):
        while ( self._resetted ):
            self._resetted = False
            self._stop.wait(self._interval)

        if ( not self._stop.isSet() ):
            self._function()
        self._stop.set()

    # Reset timer
    def reset(self):
        self._resetted = True
        self._stop.set()
        self._stop.clear()