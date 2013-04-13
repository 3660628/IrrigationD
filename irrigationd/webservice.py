from bottle import run, route, get, post, request, response
import threading
import logging
import time

class WebService(threading.Thread):
    def __init__(self, ic):
        self.ic = ic
        threading.Thread.__init__(self)

    def run(self):
        self.setName("WEBSVC")
        logging.info("Starting WebService Plugin")
        while self.ic.shutdown == False:
            time.sleep(1)
            #try:
            self.server()
            #except Exception:
                #logging.critical("WS Exception: {0}".format(e), exc_info=1)

    def server(self):
        @route('/')
        def index():
            return ("Cortana Irrigation Controller")

        @route('/status')
        def status():
            return self.ic.status

        @post('/cycle')
        def cycle():
            temp = request.json
            cycle = {}
            for key, value in temp.iteritems():
                cycle[int(key)] = int(value)
            if self.ic.cycle(cycle) is True:
                return request.json
            else:
                return "ERROR"

        @get('/cycle')
        def cyclestate():
            return self.ic.status

        @route('/off')
        def off():
            if self.ic.cycle('off') is True:
                return "off"

        run(host='0.0.0.0', port=8087, quiet=True)

