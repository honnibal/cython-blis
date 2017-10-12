import os
import os.path
import sys
import platform
import shutil
import subprocess
import numpy
import json
from setuptools import Extension

try:
    import cython
    use_cython = True
except ImportError:
    use_cython = False

PWD = os.path.join(os.path.dirname(__file__))
SRC = os.path.join(PWD, 'ext_src_files')
INCLUDE = os.path.join(PWD, 'blis/include')
ARCH = os.environ.get('BLIS_ARCH', 'reference')
COMPILER = os.environ.get('BLIS_COMPILER', 'gcc')

def on_setup(config):
    pass

def build_ext_pre_hook(cmd):
    compiler = 'gcc' #get_compiler_name(cmd)
    arch = get_arch_name()
    needs_stub = cmd.extensions[0]._needs_stub
    print('Needs stub', repr(needs_stub))
    cmd.extensions = get_extensions(SRC, INCLUDE, compiler, arch)
    cmd.extensions[0]._needs_stub = needs_stub
    cflags, ldflags = get_flags(arch=arch, compiler=compiler)
    for e in cmd.extensions:
        e.extra_compile_args = list(cflags)
        e.extra_link_args = list(ldflags)
    return cmd
 

def get_extensions(src_dir, include_dir, compiler, arch):
    if os.path.exists(include_dir):
        shutil.rmtree(include_dir)
    if use_cython:
        print("Calling Cython")
        subprocess.check_call([sys.executable, 'bin/cythonize.py'], env=os.environ)
    c_sources = get_c_sources(os.path.join(src_dir, arch))
    if compiler == 'msvc':
        shutil.copytree(os.path.join(PWD, 'blis', 'arch-includes', 'msvc-reference'), include_dir) 
    else:
        shutil.copytree(os.path.join(PWD, 'blis', 'arch-includes', arch), include_dir) 

    print("Getting extensions (Shouldn't build yet?)")
    return [
        Extension("blis.blis", ["blis/blis.c"] + c_sources,
                  include_dirs=[numpy.get_include(), include_dir],
                  undef_macros=["FORTIFY_SOURCE"])
    ]


def get_c_sources(start_dir):
    c_sources = []
    excludes = ['old', 'attic', 'broken', 'tmp', 'test',
                'cblas', 'other']
    for path, subdirs, files in os.walk(start_dir):
        for exc in excludes:
            if exc in path:
                break
        else:
            for name in files:
                if name.endswith('.c'):
                    c_sources.append(os.path.join(path, name))
    return c_sources

   
def get_arch_name():
    if 'BLIS_ARCH' in os.environ:
        return os.environ['BLIS_ARCH']
    processor = platform.processor()
    if processor == 'x86_64':
        return 'haswell' # Best guess?
    else:
        return 'reference'


def get_compiler_name(cmd):
    if 'BLIS_COMPILER' in os.environ:
        return os.environ['BLIS_COMPILER']
    name = cmd.compiler.compiler_type
    if name.startswith('msvc'):
        return 'msvc'
    elif name not in ('gcc', 'clang', 'icc'):
        return 'gcc'
    else:
        return name

def get_flags(arch='haswell', compiler='gcc'):
    flags = json.load(open('compilation_flags.json'))
    if compiler != 'msvc':
        cflags = flags['cflags'].get(compiler, {}).get(arch, [])
        cflags += flags['cflags']['common']
    else:
        cflags = flags['cflags']['msvc']
    if compiler != 'msvc':
        ldflags = flags['ldflags'].get(compiler, [])
        ldflags += flags['ldflags']['common']
    else:
        ldflags = flags['ldflags']['msvc']
    return cflags, ldflags


