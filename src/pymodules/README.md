## List of example modules

### ZBX_time - VERY basic module which demonstrates that the module and some of ot's functionality is working

* main

Parameters:
    None

Returns:
    Timestamp (float)
    
A very disappointing target at the first place. First time it is called, it returns a timestamp and 
cache it in Global Namespace. All consequitive calls will return that timestamp. Demonstrates of how to use 
Global NameCache

* rrd

Parameters:
    None
    
Returns:
    Maximum size of rrd database. 
    
Demonstrating on how to access to the zlm_cython.ini configuration file through Global Namespace

* true_stamp

Parameters:
    None
    
Returns:
    A "true" unix timestamp (float)
    
 