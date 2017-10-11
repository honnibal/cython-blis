#!/usr/bin/env python
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
from setuptools import setup
import shutil
import os
import os.path
import json

import numpy


def get_flags(arch='haswell', compiler='gcc'):
    flags = json.load(open('compilation_flags.json'))
    cflags = flags['cflags']['common']
    cflags += flags['cflags'].get(compiler, {}).get(arch, [])
    ldflags = flags['ldflags']['common']
    ldflags += flags['ldflags'].get(compiler, {}).get(arch, [])
    return cflags, ldflags


def get_c_sources(start_dir):
    c_sources = []
    excludes = ['old', 'attic', 'packv', 'scalv', 'cblas', 'other']
    for path, subdirs, files in os.walk(start_dir):
        for exc in excludes:
            if exc in path:
                break
        else:
            for name in files:
                if name.endswith('.c'):
                    c_sources.append(os.path.join(path, name))
    return c_sources



def build_extensions(src_dir, include_dir, compiler, arch):
    if os.path.exists(include_dir):
        shutil.rmtree(include_dir)
    c_sources = get_c_sources(os.path.join(src_dir, arch))
    cflags, ldflags = get_flags(compiler=compiler, arch='reference')
    shutil.copytree(os.path.join(PWD, 'blis', 'arch-includes', arch), include_dir) 
    return [
        Extension("blis.blis", ["blis/blis.pyx"] + c_sources,
                  include_dirs=[numpy.get_include(), include_dir],
                  extra_compile_args=cflags, extra_link_args=ldflags)
    ]


PWD = os.path.join(os.path.dirname(__file__))
SRC = os.path.join(PWD, 'ext_src_files')
INCLUDE = os.path.join(PWD, 'blis/include')
ARCH = os.environ.get('BLIS_ARCH', 'reference')
COMPILER = os.environ.get('BLIS_COMPILER', 'gcc')

setup(
    setup_requires=['pbr', 'numpy'],
    pbr=True,
    ext_modules=build_extensions(SRC, INCLUDE, COMPILER, ARCH),
)
