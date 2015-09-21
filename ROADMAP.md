ZLM-python is a Zabbix Loadable Module which embedding Python interpreter in Zabbix server proxy or an agent. 
You can create the snippets of the Python code, which will be executed inside the Zabbix execution context, giving 
  you access to internal Zabbix core functions and serious performance gain.

# 0.5

## Features

## Support of the Pyro

# 0.4 

Initial release of the ZLM-python module with Cython.

## Features 

* Single module acting as both Zabbix Loadable Module and Python module.
* Access to Zabbix core logging and process creation functions.
* Global namespace.
* Background "data collectors"
* Modules caching
* RRD in-memory internal storage based on namespace.

##Requirements 

* Cython verson 0.23.1 or newer
* Python2 version 2.6 or newer, with multiprocessing module
* Zabbix 2.2 or newer, with loadable modules support
* gcc, make
