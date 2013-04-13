import threading
from datetime import datetime
import Queue
import redis
import logging
import sys
import time
from webservice import WebService
from cycle import IrrigationCycle, Stage
from bottle import run, route, get, post, request, response
from pyioboard import RelayBoard, IODummy

settings = {"serialport":'/dev/serial/by-id/usb-Microchip_Technology_Inc._CDC_RS-232_Emulation_Demo-if00',
            "gpios": [],
            "relays": [0, 1, 2, 3, 4, 5, 6, 7],
            }

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

class IrrigationController(object):
    def __init__(self, relayboard, settings):
        self.controllerlock = threading.Lock()
        self.cfg = settings
        self.relayboard = relayboard
        self._relay_state = {x: 'off' for x in self.cfg['relays']}
        self._reset_controller()
        self.threads = []
        self._current_cycle = None
        self.stopthreads = False
        self.shutdown = False
        self.start()


    def _reset_controller(self, refresh=True):
        if refresh is True:
            self.refresh_all()
        for relay in [x for x in self._relay_state.keys() if self._relay_state[x] == 'on']:
            self.relayboard.relay_set(relay, 'off')

    @property
    def status(self):
        status = {'relaystate': self._relay_state}
        if self._current_cycle is None:
            status['currentcycle'] = None
        else:
            status['currentcycle'] = self._current_cycle.status
        return status

    def refresh_all(self):
        with self.controllerlock:
            logging.info("Starting Refresh of all ports")
            for relay in self._relay_state.keys():
                self._relay_state[relay] = self.relayboard.relay_read(relay)
        logging.debug("Refresh Complete")


    def set_zone(self, zone, command):
        logging.debug("setting {0} to {1}".format(zone, command))
        with self.controllerlock:
            return self.relayboard.relay_set(zone, command)


    def cycle(self, cycleinfo):
        try:
            logging.info("Setting Cycle: {0}".format(cycleinfo))
            if cycleinfo != 'off':
                self._current_cycle = IrrigationCycle(self, cycleinfo=cycleinfo)
            else:
                self._current_cycle = None
                self._reset_controller(refresh=True)
            self.poll()
        except Exception as e:
            logging.critical("Error creating Cycle: {0}".format(e), exc_info=1)
            return False
        else:
            return True


    def poll(self):
        if self._current_cycle is None:
            logging.debug("No Cycle")
        else:
            logging.debug("Checking Cycle Progression")
            self._current_cycle.check_cycle()
            if self._current_cycle.status == "Completed":
                self._current_cycle = None
                self._reset_controller(refresh=True)


    def start(self):
        logging.debug("Main STARTING")
        self._spinup()
        logging.debug("Main LOOP STARTING")
        while self.shutdown == False:
            self._main_loop()
        logging.debug("Main LOOP STOPPING")
        self.cleanup()



    def _spinup(self):
        logging.info("Initializing Threads")
        ws = WebService(self)
        self.threads.append(ws)

        logging.info("Starting Threads")
        for thread in self.threads:
            thread.start()

    def _main_loop(self):
        if self.cycle is None:
            self._reset_controller(refresh=True)
            self.sleeptillminute()
        else:
            time.sleep(5)
        self.poll()

    def sleeptillminute(self):
        t = datetime.utcnow()
        sleeptime = 60 - (t.second + t.microsecond/1000000.0)
        time.sleep(sleeptime)

    def cleanup(self):
        logging.info("Cleaning up for shutdown")
        logging.info("Waiting for threads to exit")
        for thread in self.threads:
            if thread.name != 'WEBSERVICE':
                thread.join()
        logging.info("Done")
        sys.exit()




if __name__ == "__main__":
    with RelayBoard(settings['serialport']) as relayboard:
        try:
            rbc = IrrigationController(relayboard, settings)
        except KeyboardInterrupt:
            sys.exit(0)
