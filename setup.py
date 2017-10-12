#!/usr/bin/env python
import shutil
import os
import os.path
import json
import distutils.command.build_ext
import subprocess
import sys
from setuptools import Extension, setup
import platform

import numpy

try:
    import cython
    use_cython = True
except ImportError:
    use_cython = False


class ExtensionBuilder(distutils.command.build_ext.build_ext):
    def build_extensions(self):
        self.extensions = self.get_extensions(SRC, INCLUDE)
        compiler = self.get_compiler_name()
        arch = self.get_arch_name()
        cflags, ldflags = self.get_flags(arch=arch, compiler=compiler)
        print(compiler, arch)
        print("CFLAGS", cflags)
        print("LDFLAGS", ldflags)
        for e in self.extensions:
            e.extra_compile_args = list(cflags)
            e.extra_link_args = list(ldflags)
        distutils.command.build_ext.build_ext.build_extensions(self)
    
    def get_arch_name(self):
        if 'BLIS_ARCH' in os.environ:
            return os.environ['BLIS_ARCH']
        processor = platform.processor()
        if processor == 'x86_64':
            return 'haswell' # Best guess?
        else:
            return 'reference'

    def get_compiler_name(self):
        if 'BLIS_COMPILER' in os.environ:
            return os.environ['BLIS_COMPILER']
        name = self.compiler.compiler_type
        if name.startswith('msvc'):
            return 'msvc'
        elif name not in ('gcc', 'clang', 'icc'):
            return 'gcc'
        else:
            return name
    
    def get_flags(self, arch='haswell', compiler='gcc'):
        flags = json.load(open('compilation_flags.json'))
        cflags = flags['cflags'].get(compiler, {}).get(arch, [])
        if compiler != 'msvc':
            cflags += flags['cflags']['common']
        ldflags = flags['ldflags'].get(compiler, [])
        if compiler != 'msvc':
            ldflags += flags['ldflags']['common']
        return cflags, ldflags

    def get_extensions(self, src_dir, include_dir):
        if os.path.exists(include_dir):
            shutil.rmtree(include_dir)
        if use_cython:
            print("Calling Cython")
            subprocess.check_call([sys.executable, 'bin/cythonize.py'], env=os.environ)
        arch = self.get_arch_name()
        compiler = self.get_compiler_name()
        c_sources = self.get_c_sources(os.path.join(src_dir, arch))
        shutil.copytree(os.path.join(PWD, 'blis', 'arch-includes', arch), include_dir) 
        if compiler == 'msvc':
            shutil.copyfile(
                os.path.join(PWD, 'blis', 'arch-includes', 'msvc9', 'stdint.h'),
                os.path.join(include_dir, 'stdint.h'))

        print("Getting extensions (Shouldn't build yet?)")
        return [
            Extension("blis.blis", ["blis/blis.c"] + c_sources,
                      include_dirs=[numpy.get_include(), include_dir],
                      undef_macros=["FORTIFY_SOURCE"])
        ]

    def get_c_sources(self, start_dir):
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


PWD = os.path.join(os.path.dirname(__file__))
SRC = os.path.join(PWD, 'ext_src_files')
INCLUDE = os.path.join(PWD, 'blis/include')
ARCH = os.environ.get('BLIS_ARCH', 'reference')
COMPILER = os.environ.get('BLIS_COMPILER', 'gcc')

setup(
    setup_requires=['numpy'],
    ext_modules=[Extension('blis.blis', ['blis/blis.pyx'])],
    cmdclass={'build_ext': ExtensionBuilder}
)
