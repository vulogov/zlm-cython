##
## Access to Zabbix server through Zabbix API
## Dependencies:
##              pyzabbix
##

class Federation_Config_File:
    def __init__(self, name, cfg_path="/usr/local/etc", default_config_filename="zabbix_federation.cfg"):
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
            self._cfg = self.cfg.items(self.name)
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

class Federation_Server:
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
    def history(self, item, interval, t_shift=None):
        from ZLM_Interval import calcInterval
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
        itemid = iteminfo["itemid"]
        _interval = calcInterval(interval, t_shift)
        history = self.z.history.get(itemits=itemid, time_from=_interval["l_stamp"], time_till=_interval["h_stamp"], limit=str(_interval["limit"]), history=iteminfo["value_type"], output="extend", sortfield="clock")
        ret = {}
        for i in history:
            ret[float(i["clock"])] = i["value"]
        return ret


if __name__ == "__main__":
    c = Federation_Server("zabbix-251")
    print c.history("zabbix-251:Context switches", "3000")