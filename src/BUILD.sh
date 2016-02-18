#!/bin/bash

echo "Building pyzabbix environment"
export XML2_INC=`xml2-config --cflags`

if [ -z $XML2_INC ]; then
    echo "xml2-devel package not installed"
    exit 1
fi

export PY_INC=`python-config --includes`
if [ -z "$PY_INC" ]; then
    echo "python-devel package not installed"
    exit 1
fi

export PY_LIB=`python-config --libs`
if [ -z "$PY_LIB" ]; then
    echo "python-devel package not installed"
    exit 1
fi

export ZBX_DIR=`find ../.. -type d -name zabbix-*|head -1`
if [ -z "$ZBX_DIR" ]; then
    echo "No Zabbix source tree found in $HOME"
    exit 1
else
    echo "Will compile against Zabbix from $ZBX_DIR"
fi

echo "Checking if Sorce tree was configured"

if [ -f $ZBX_DIR/include/config.h ]; then
    echo "Zabbix source tree already configured" ;
else
    echo  "Configuring Zabbix "; (cd $ZBX_DIR; ./configure --quiet --enable-agent; cd -);
fi

echo -n "Building python.cfg "
echo -n "PYTHONPATH=" > python.cfg
python -c "import sys; print ':'.join(sys.path)" >> python.cfg
echo -n "PYTHONLIB=" >> python.cfg
ldd `type -p python`|grep python|cut -f 3 -d " " >> python.cfg
if [ -s python.cfg ]; then
   echo " ok"
else
   echo "fail"
   exit 1
fi

echo "Building python.so"
set -x

make -e all

set +x

