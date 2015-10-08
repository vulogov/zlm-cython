##
## Access to Zabbix server through Zabbix API
## Dependencies:
##              pyzabbix
##

class Federation_Config_File:
    def __init__(self, name=None, cfg_path="/usr/local/etc", default_config_filename="zabbix_federation.cfg"):
        self.name = name
        self.cfg_path = cfg_path
        self.default_config_filename=default_config_filename
        self.reloadConfig()
    def reloadConfig(self):
        from ConfigParser import SafeConfigParser
        self.path = "%s/%s"%(self.cfg_path, self.default_config_filename)
        self.cfg  = SafeConfigParser()
        self.isReady = False
        if len(self.cfg.read(self.path)) != 0:
            self.isReady = True
            if self.name:
                self._cfg = self.cfg.items(self.name)
            else:
                self._cfg = None
                self.isReady = False
    def servers(self):
       return self.cfg.sections()
    def __getitem__(self, _key):
        for key, val in self._cfg:
            key = key.lower()
            if key == _key:
                return val
        return None
    def URL(self):
        return self["url"]
    def USERNAME(self):
        return self["username"]
    def PASSWORD(self):
        return self["password"]

class DataAggregators:
    def _f(self, res, fun):
        c = []
        for i in res.values():
            c.append(float(i))
        return fun(c)
    def MAX(self, res):
        return self._f(res, max)
    def MIN(self, res):
        return self._f(res, min)
    def SUM(self, res):
        return self._f(res, sum)
    def AVG(self, res):
        c = []
        for i in res.values():
            c.append(float(i))
        return (sum(c)/len(c))


class Federation_Server(DataAggregators):
    def __init__(self, name, **kw):
        if not kw.has_key("cfg_path"):
            kw["cfg_path"] = "/usr/local/etc"
        if not kw.has_key("default_config_filename"):
            kw["default_config_filename"] = "zabbix_federation.cfg"
        self.cfg = Federation_Config_File(name, kw["cfg_path"], kw["default_config_filename"])
        if not self.cfg.URL() or not self.cfg.USERNAME() or not self.cfg.PASSWORD():
            raise ValueError, "Federation Server %s isn't properly configured"%name
        self.login()
    def login(self):
        from pyzabbix import ZabbixAPI, ZabbixAPIException
        self.z = ZabbixAPI(self.cfg.URL())
        try:
            self.z.timeout = float(self.cfg["timeout"])
        except:
            self.z.timeout = 5.0
        self.z.login(self.cfg.USERNAME(),self.cfg.PASSWORD())
    def __getitem__(self, item):
        try:
            ix = item.index(":")
        except KeyboardInterrupt:
            return None
        _host = item[:ix]
        _item = item[ix+1:]
        try:
            hostinfo = self.z.host.get(filter={"host": _host})[0]
        except:
            return None
        if hostinfo["name"] != _host and int(hostinfo["available"]) != 1 and int(hostinfo["maintenance_status"]) != 0 and int(hostinfo["status"]) != 0:
            return None
        hostid = hostinfo["hostid"]
        try:
            iteminfo = self.z.item.get(hostids=hostid, search={"name":_item})[0]
        except:
            return None
        return iteminfo
    def _execFunction(self, h_res, fun):
        import time
        if not fun:
            return h_res
        if type(fun) == type(""):
            _fun = getattr(self, fun)
            _par = (h_res,)
        else:
            _fun = fun
            _par = (h_res,)
        return {time.time():apply(_fun, _par)}
    def history(self, item, interval, t_shift=None, fun=None, _iteminfo=None):
        import time
        from ZLM_Interval import calcInterval
        if _iteminfo:
            iteminfo = _iteminfo
        else:
            iteminfo = self[item]
        if not iteminfo:
            return []
        itemid = iteminfo["itemid"]
        _interval = calcInterval(interval, t_shift)
        _from = _interval["l_stamp"]
        _to = _interval["h_stamp"]
        _limit=str(_interval["limit"])
        _history=int(iteminfo["value_type"])
        history = self.z.history.get(itemits=itemid, time_from=_from, time_till=_to, limit=_limit, history=_history, output="extend", sortfield="clock")
        ret = {}
        if _history == 0:
            conv_fun = float
        elif _history == 3:
            conv_fun = int
        else:
            conf_fun = str
        for i in history:
            try:
                ret[float(i["clock"])] = conv_fun(i["value"])
            except:
                continue
        if not fun:
            return ret
        return self._execFunction(ret, fun)



if __name__ == "__main__":
    c = Federation_Server("zabbix-251")
    print c.history("zabbix-251:Context switches", "#1000", "12h")
    #print c.history("zabbix-251:Context switches", "#1000", "12h", "AVG")
    #print c.history("zabbix-251:Context switches", "#1000", "12h", "SUM")
    #print c.history("zabbix-251:Context switches", "#1000", "12h", "MIN")
    #c = Federation_Config_File()
    #print c.servers()