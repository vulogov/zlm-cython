##
##
##
import zlm_python

class Daemon(zlm_python.ZLM_Metric_Collector):
    description = "Test clock collector"
    _collector = "clock_collector"
    def collector(self):
        import time
        stamp = time.time()
