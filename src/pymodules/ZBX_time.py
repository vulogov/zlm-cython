import time
import zlm_python as zlm
def true_stamp(*args):
	return time.time()
def rrd(ns, *args):
	return ns.config["rrd"]["maxsize"]
def main(*args):
	ns = args[0]
	try:
		stamp = ns.stamp
	except:
		stamp = time.time()
		ns.stamp = stamp
	return stamp
