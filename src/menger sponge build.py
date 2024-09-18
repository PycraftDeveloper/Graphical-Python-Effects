from setuptools import setup
from Cython.Build import cythonize
import numpy as np

setup(
    ext_modules = cythonize("menger_sponge.pyx"),
    include_dirs=[np.get_include()]
)