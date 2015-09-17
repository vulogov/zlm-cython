

#include "settings.h"


#include "sysinc.h"
#include "common.h"
#include "module.h"
#include "cfg.h"
#include "log.h"
#include <time.h>
#include <dlfcn.h>
#include <Python.h>
#include <frameobject.h>
#include "zlm_python_pyx.h"

#define BUFSIZE 4096

extern char *CONFIG_LOAD_MODULE_PATH;
char        *modpath;
char        *lib_path = NULL;
char        *python_path = NULL;
PyObject    *ctx;
/* the variable keeps timeout setting for item processing */
static int	item_timeout = 0;

/* extern int ZBX_startup(); */

int	zbx_module_python_ping(AGENT_REQUEST *request, AGENT_RESULT *result);
int	zbx_module_python_version(AGENT_REQUEST *request, AGENT_RESULT *result);
int	zbx_module_python_call_wrap(AGENT_REQUEST *request, AGENT_RESULT *result);
int zbx_set_return_value(AGENT_RESULT *result, PyObject *retvalue);

static ZBX_METRIC keys[] =
{
   {"python.ping",	0,		zbx_module_python_ping,	NULL},
   {"python.version",	0,		zbx_module_python_version, NULL},
   {"py",  		CF_HAVEPARAMS,	zbx_module_python_call_wrap, ""},
   {NULL}
};


void load_python_env_config(void)  {
    char conf_file[BUFSIZE];
    static struct cfg_line cfg[] = {
	    { "PYTHONPATH", &python_path, TYPE_STRING, PARM_MAND, 0, 0 },
	    { "PYTHONLIB", &lib_path, TYPE_STRING, PARM_MAND, 0, 0 },
	    { NULL },
    };
    zbx_snprintf(conf_file, BUFSIZE, "%s/python.cfg", CONFIG_LOAD_MODULE_PATH);
    parse_cfg_file(conf_file, cfg, ZBX_CFG_FILE_OPTIONAL, ZBX_CFG_STRICT);
}



int zbx_set_return_value(AGENT_RESULT *result, PyObject *ret) {
    char *cstrret;
    if (PyInt_Check(ret)) {
        SET_UI64_RESULT(result, PyLong_AsLong(ret));
    } else if (PyLong_Check(ret)) {
        SET_UI64_RESULT(result, PyLong_AsLong(ret));
    } else if (PyFloat_Check(ret)) {
        SET_DBL_RESULT(result, PyFloat_AsDouble(ret));
    } else if (PyString_Check(ret)) {
        PyArg_Parse(ret, "s", &cstrret);
        SET_STR_RESULT(result, strdup(cstrret));
    } else {
        SET_MSG_RESULT(result, strdup("Python returned unsupported value"));
        return SYSINFO_RET_FAIL;
    }
    return SYSINFO_RET_OK;
}

int	zbx_module_api_version() {
	return ZBX_MODULE_API_VERSION_ONE;
}

void	zbx_module_item_timeout(int timeout) {
	item_timeout = timeout;
}

ZBX_METRIC	*zbx_module_item_list() {
   return keys;
}

int	zbx_module_python_ping(AGENT_REQUEST *request, AGENT_RESULT *result) {
   /*PyGILState_STATE gstate;
   gstate = PyGILState_Ensure();*/
   if (Py_IsInitialized() != 0)
     SET_UI64_RESULT(result, 1);
   else
     SET_UI64_RESULT(result, 0);
   /* PyGILState_Release(gstate); */
   return SYSINFO_RET_OK;
}

int	zbx_module_python_version(AGENT_REQUEST *request, AGENT_RESULT *result) {
   
   /*PyGILState_STATE gstate;
   gstate = PyGILState_Ensure();*/
   SET_STR_RESULT(result, strdup(Py_GetVersion()));
   /* PyGILState_Release(gstate); */
   return SYSINFO_RET_OK;
}


int	zbx_module_python_call_wrap(AGENT_REQUEST *request, AGENT_RESULT *result) {
    int  i, retvalue_ret_code;
    PyObject* param;
    PyObject* ret;

    if ((request->nparam < 1) || (strlen(get_rparam(request, 0)) == 0))   {
        SET_MSG_RESULT(result, strdup("Invalid number of parameters."));
        return SYSINFO_RET_FAIL;
    }

    if ((param = PyTuple_New(request->nparam)) == NULL) {
        SET_MSG_RESULT(result, strdup("Can not allocate parameters PyObject."));
        return SYSINFO_RET_FAIL;
    }
    for (i=0;i<request->nparam;i++) {
        PyTuple_SET_ITEM(param,i,PyString_FromString(get_rparam(request, i)));
    }

    ret = ZBX_call(ctx, param);

    if (ret == NULL) {
        SET_MSG_RESULT(result, strdup("ZLM-python: Python code threw a traceback while inside the ZLM module. Contact developers."));
        PyErr_Print();
        return SYSINFO_RET_FAIL;
    }

    if (PyTuple_Check(ret) && PyTuple_Size(ret) == 3) {
        long wrapper_ret_code;
        wrapper_ret_code = PyLong_AsLong(PyTuple_GetItem(ret, 0));
        if ( wrapper_ret_code == 0 ) {
            retvalue_ret_code = SYSINFO_RET_FAIL;
            SET_MSG_RESULT(result, strdup(PyString_AsString(PyTuple_GetItem(ret, 1))));
        } else {
            retvalue_ret_code = zbx_set_return_value(result, PyTuple_GetItem(ret, 1));
        }
    } else {
        retvalue_ret_code = zbx_set_return_value(result, ret);
    }

    Py_DECREF(param);

    return retvalue_ret_code;
}



int	zbx_module_init() {
    PyObject *mod, *param, *fun;
    char error[MAX_STRING_LEN];
    char cmd[BUFSIZE];
    char *pythonpath;
    #if HAVE_SECURE_GETENV==1
        pythonpath=secure_getenv("PYTHONPATH");
    #else
        pythonpath=getenv("PYTHONPATH");
    #endif

    load_python_env_config();
    if (lib_path == NULL)
        return ZBX_MODULE_FAIL;
   
    if (pythonpath == NULL) {
        if (python_path == NULL) {
	        return ZBX_MODULE_FAIL;
        }
        modpath=malloc(strlen(CONFIG_LOAD_MODULE_PATH)+4096);
        zbx_snprintf(modpath, 4096, "%s/pymodules:%s/pymodules/lib:%s", CONFIG_LOAD_MODULE_PATH, CONFIG_LOAD_MODULE_PATH,python_path);
        free(python_path);
    } else  {
        modpath=malloc(strlen(CONFIG_LOAD_MODULE_PATH)+strlen(pythonpath)+4096);
        zbx_snprintf(modpath, 4096, "%s/pymodules:%s/pymodules/lib:%s", CONFIG_LOAD_MODULE_PATH, CONFIG_LOAD_MODULE_PATH, pythonpath);
    }


    if (dlopen(lib_path, RTLD_NOW | RTLD_NOLOAD | RTLD_GLOBAL) == NULL)   {
        free(lib_path);
        return ZBX_MODULE_FAIL;
    }
   
    /* We do not need those anymore */
    free(lib_path);
   
    /* Set-up Python environment */
    Py_SetProgramName("zlm_python");
    Py_InitializeEx(0);
    if (Py_IsInitialized() == 0) {
        /* Python initialization had failed */
        return ZBX_MODULE_FAIL;
    }
    PySys_SetPath(modpath);

    zabbix_log(LOG_LEVEL_WARNING, "Executing ZBX_startup");
    initzlm_python();
    ctx = ZBX_startup(CONFIG_LOAD_MODULE_PATH);
    return ZBX_MODULE_OK;
}

int	zbx_module_uninit() {
    ZBX_finish(ctx);
    Py_Finalize();
    return ZBX_MODULE_OK;
}
