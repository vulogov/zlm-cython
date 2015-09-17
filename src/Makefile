all: zlm_python.so

zlm_python_pyx.c: zlm_python.pyx
	cython -o zlm_python_pyx.c zlm_python.pyx

zlm_python_pyx.o: zlm_python_pyx.c
	gcc -g -fPIC -c -I$(ZBX_DIR)/include $(XML2_INC) $(PY_INC) -o zlm_python_pyx.o zlm_python_pyx.c
zlm_python.o: zlm_python.c
	gcc -g -fPIC -c -I$(ZBX_DIR)/include $(XML2_INC) $(PY_INC) -o zlm_python.o zlm_python.c


zlm_python.so: zlm_python_pyx.o zlm_python.o
	gcc -shared -o zlm_python.so zlm_python_pyx.o zlm_python.o  $(PY_LIB)
