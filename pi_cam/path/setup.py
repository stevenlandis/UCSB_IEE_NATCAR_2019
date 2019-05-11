from distutils.core import setup, Extension
import numpy.distutils.misc_util

setup(
    ext_modules=[Extension("path", ["path.c"])],
    include_dirs=numpy.get_include())
# setup(
#     ext_modules=[Extension("path", ["path.c"])],
#     include_dirs=numpy.distutils.misc_util.get_numpy_include_dirs())