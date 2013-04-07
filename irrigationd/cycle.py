from datetime import datetime, timedelta
from time import sleep



class IrrigationCycle(object):
    def __init__(self, ctl, cycleinfo={}):
        self.ctl = ctl
        self._cycleinfo = cycleinfo
        self._stages = []
        self.start_ts = None
        self.finish_ts = None
        for zone in sorted(cycleinfo.keys()):
          self._stages.append(Stage(self.ctl, zone, cycleinfo[zone]))

    def check_cycle(self):
        if self.finish_ts is None:
            if self._next_stage_status("InProgress") is None:
                self.startnext()
            else:
                current = self._next_stage_status("InProgress")
                if current.fulfilled:
                    current.complete()

    def startnext(self):
        if self.status == "NotStarted":
                    self.start_ts = datetime.now()
        stage = self._next_stage_status("NotStarted")
        if stage is None:
            self._complete()
        else:
            stage.start()

    @property
    def status(self):
        if self.start_ts is None and self.finish_ts is None:
            return "NotStarted"
        elif self.finish_ts is None:
            return "InProgress"
        elif self.start_ts is not None and self.finish_ts is not None:
            return "Completed"


    def _complete(self):
        if self.finish_ts is None:
            self.finish_ts = datetime.now()

    def _next_stage_status(self, status):
        return next((x for x in self._stages if x.status == status), None)



    @property
    def current_stage(self):
        for stage in self._stages:
            if state.status == "InProgress":
                return stage
        else:
            return None

class Stage(object):
    def __init__(self, ctl, zone, duration):
        self.ctl = ctl
        self.zone = int(zone)
        self.duration = int(duration)
        self.start_ts = None
        self.finish_ts = None

    @property
    def status(self):
        if self.start_ts is None and self.finish_ts is None:
            return "NotStarted"
        elif self.finish_ts is None:
            return "InProgress"
        elif self.start_ts is not None and self.finish_ts is not None:
            return "Completed"

    def complete(self):
        self.finish_ts = datetime.now()
        self.ctl.set_zone(self.zone, "off")

    def start(self):
        self.start_ts = datetime.now()
        self.ctl.set_zone(self.zone, "on")

    @property
    def fulfilled(self):
        if self.status == "InProgress":
            if self.elapsed >= self.duration:
                return True
            else:
                return False
        elif self.status == "NotStarted":
            return False
        elif self.status == "Completed":
            return True
        else:
            raise Exception("Not sure how we ended up here...")

    @property
    def elapsed(self):
        if not self.start_ts:
            raise Exception("NotStarted")
        else:
            return round(((datetime.now() - self.start_ts).seconds / 60.0), 2)

