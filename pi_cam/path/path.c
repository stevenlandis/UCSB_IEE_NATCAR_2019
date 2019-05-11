#include <Python.h>
#include <numpy/arrayobject.h>
#include <stdio.h>

static char module_docstring[] =
    "Fast line detection.";
static char fillSearch_docstring[] =
    "given a picture, calculate points";

static PyObject* path_fillSearch(PyObject* self, PyObject* args) {
    PyArrayObject* inArray;
    if (!PyArg_ParseTuple(args, "O!", &PyArrayType, &inArray)) {
        return NULL;
    }
    
    NpyIter* iter = NpyIter_New(inArray, NPY_ITER_READONLY, NPY_KEEPORDER, NPY_NO_CASTING, NULL);
    if (iter == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    NpyIter_Deallocate(in_iter);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pathMethods[] = {
    {"fillSearch", path_fillSearch, METH_VARARGS, fillSearch_docstring},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef path_module = {
   PyModuleDef_HEAD_INIT,
   "path",   /* name of module */
   module_docstring, /* module documentation, may be NULL */
   -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
   pathMethods
};


PyMODINIT_FUNC PyInit_path(void) {
    PyMODINIT_FUNC ret = PyModule_Create(&path_module);
    import_array();
    return ret;
}