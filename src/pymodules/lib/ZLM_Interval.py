##
## Calculating the time intervals for Zabbix
##

def calcSeconds(secs):
    q = secs[-1].lower()
    m = None
    if q == "m":
        m = 60
    elif q == "h":
        m = 3600
    elif q == "d":
        m = 86400
    elif q == "w":
        m = 604800
    else:
        m = None
    if m != None:
        return float(secs[:-1])*m
    return float(secs)

def calcNSamples(data):
    if data[0] == "#":
        return (0, int(data[1:]))
    return (int(data), 1)


##
## calcInterval()
## Calculating intervals for Zabbix history queries
## Parameters:
##      interval        -   interval between high and low boundartis of the sample
##                          ether #<seconds> or [<secs>, <mins>m, <days>d, <weeks>w]
##      t_shift         -   timeshift as [<secs>, <mins>m, <days>d, <weeks>w]
##      interval_range  -   default range of interval between high and low
##
def calcInterval(interval, t_shift=None, interval_range=0):
    import time
    if t_shift:
        shift_secs = calcSeconds(t_shift)
    else:
        shift_secs = 0.0
    h_stamp = time.time()-shift_secs
    q = interval[-1].lower()
    if q in ["m", "h", "d", "w"] and interval[0] != "#":
        delta = calcSeconds(interval)
        limit = 1
    else:
        delta, limit = calcNSamples(interval)
    if interval_range == 0 and delta == 0:
        interval_range = 86400
    l_stamp = time.time()-delta-interval_range-shift_secs
    return {"h_stamp":h_stamp, "l_stamp":l_stamp, "limit": limit, "delta":delta}

def printInterval(interval, t_shift=None, interval_range=0):
    import time
    print "Interval %s %s %d"%(interval, t_shift, interval_range)
    print "Stamp",time.ctime(time.time())
    d = calcInterval(interval, t_shift, interval_range)
    print "High-range",time.ctime(d["h_stamp"])
    print "Low-range",time.ctime(d["l_stamp"])
    print "Limit",d["limit"]
    print "Delta",d["delta"]

if __name__ == '__main__':
    printInterval("60")
    printInterval("#10")
    printInterval("60", "1m")
