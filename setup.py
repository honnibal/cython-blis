#!/usr/bin/env python
from __future__ import print_function
import os
from os import path
import subprocess
import sys
import contextlib
from distutils.command.build_ext import build_ext
from distutils.sysconfig import get_python_inc
import platform

try:
    from setuptools import Extension, setup
except ImportError:
    from distutils.core import Extension, setup


PWD = path.dirname(path.realpath(__file__))
BLIS_LIB_DIR = path.join(PWD, 'blis', '_ext')

PACKAGES = [
    'blis',
    'blis.tests'
]


MOD_NAMES = [
    'blis.blis'
]


# By subclassing build_extensions we have the actual compiler that will be used which is really known only after finalize_options
# http://stackoverflow.com/questions/724664/python-distutils-how-to-get-a-compiler-that-is-going-to-be-used
compile_options =  {'msvc'  : ['/Ox', '/EHsc'],
                    'other' : ['-O2', '-fPIC', '-Wno-strict-prototypes', '-Wno-unused-function',
                               '-std=c11']}
link_options    =  {'msvc'  : [],
                    'other' : ['-std=c11', '-fPIC']}

class build_ext_options:
    def build_options(self):
        for e in self.extensions:
            e.extra_compile_args.extend(compile_options.get(
                self.compiler.compiler_type, compile_options['other']))
        for e in self.extensions:
            e.extra_link_args.extend(link_options.get(
                self.compiler.compiler_type, link_options['other']))

            import platform, subprocess


class build_ext_subclass(build_ext, build_ext_options):
    def build_extensions(self):
        build_ext_options.build_options(self)
        build_ext.build_extensions(self)

    def run(self):
        make_blis(path.join(PWD, 'blis', '_src'), BLIS_LIB_DIR)
        # can't use super() here because _build is an old style class in 2.7
        build_ext.run(self)


def make_blis(blis_dir, out_dir):
    if os.path.exists(os.path.join(out_dir, 'lib', 'libblis.a')):
        os.unlink(os.path.join(out_dir, 'lib', 'libblis.a'))
    march = get_processor_info()
    if march in [b'haswell', b'broadwell', b'kaby lake', b'skylake']:
        march = 'haswell'
    elif march == [b'ivy bridge', b'sandy bridge', b'sandybridge']:
        march = 'sandybridge'
    elif march not in (b'piledriver', b'bulldozer', b'carrizo'):
        march = 'reference'
    shared_lib_loc = os.path.join(out_dir, 'lib', ('libblis-0.2.2-53-%s.a' % march))
    if os.path.exists(shared_lib_loc):
        print("Linking to pre-built static library: %s" % shared_lib_loc)
        os.symlink(str(shared_lib_loc), os.path.join(out_dir, 'lib', 'libblis.a'))
        return

    print("Compiling Blis (takes 60 to 120 seconds)")
    configure_cmd = ['./configure']
    configure_cmd.extend(['-i', '64'])
    configure_cmd.extend(['-p', out_dir])
    configure_cmd.extend(['--disable-cblas'])
    configure_cmd.extend(['-t', 'openmp'])
    configure_cmd.append(march)
    print(configure_cmd)
    output = open(os.devnull, 'wb')
    if subprocess.call(configure_cmd, cwd=blis_dir, stdout=output, stderr=output) != 0:
        raise EnvironmentError("Error calling 'configure' for BLIS")
    make_cmd = ['make', '-j3']
    print(make_cmd)
    if subprocess.call(make_cmd, stdout=output, stderr=output, cwd=blis_dir) != 0:
        raise EnvironmentError("Error calling 'make' for BLIS")
    make_cmd.append('install')
    if subprocess.call(make_cmd, stdout=output, stderr=output, cwd=blis_dir) != 0:
        raise EnvironmentError("Error calling 'make install' for BLIS")


def get_processor_info():
    command = 'gcc -march=native -Q --help=target | grep march'
    info = subprocess.check_output(command, shell=True)
    march = info.strip().split()[-1]
    return march



def generate_cython(root, source):
    print('Cythonizing sources')
    p = subprocess.call([sys.executable,
                         os.path.join(root, 'bin', 'cythonize.py'),
                         source])
    if p != 0:
        raise RuntimeError('Running cythonize failed')


def is_source_release(path):
    return os.path.exists(os.path.join(path, 'PKG-INFO'))


def clean(path):
    for name in MOD_NAMES:
        name = name.replace('.', '/')
        for ext in ['.so', '.html', '.cpp', '.c']:
            file_path = os.path.join(path, name + ext)
            if os.path.exists(file_path):
                os.unlink(file_path)


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


@contextlib.contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    try:
        os.chdir(new_dir)
        sys.path.insert(0, new_dir)
        yield
    finally:
        del sys.path[0]
        os.chdir(old_dir)


def setup_package():
    root = os.path.abspath(os.path.dirname(__file__))

    if len(sys.argv) > 1 and sys.argv[1] == 'clean':
        return clean(root)

    with chdir(root):
        with open(os.path.join(root, 'blis', 'about.py')) as f:
            about = {}
            exec(f.read(), about)

        with open(os.path.join(root, 'README.rst')) as f:
            readme = f.read()

        include_dirs = [
            get_python_inc(plat_specific=True),
            os.path.join(root, 'include')]

        ext_modules = []
        for mod_name in MOD_NAMES:
            mod_path = mod_name.replace('.', '/') + '.c'
            ext_modules.append(
                Extension(mod_name, [mod_path],
                    include_dirs=include_dirs,
                    extra_compile_args=['-fopenmp'],
                    extra_link_args=[
                        '-fopenmp',
                        path.join(BLIS_LIB_DIR, 'lib', 'libblis.a')
                    ],
                ))

        if not is_source_release(root):
            generate_cython(root, 'blis')

        src_files = package_files(path.join('blis', '_src'))
        ext_files = package_files(path.join('blis', '_ext'))
        setup(
            name=about['__title__'],
            zip_safe=True,
            packages=PACKAGES,
            package_data={'': ['*.c', '*.pyx', '*.pxd'] +ext_files + src_files},
            description=about['__summary__'],
            long_description=readme,
            author=about['__author__'],
            author_email=about['__email__'],
            version=about['__version__'],
            url=about['__uri__'],
            license=about['__license__'],
            ext_modules=ext_modules,
            classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Console',
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: MIT License',
                'Operating System :: POSIX :: Linux',
                'Operating System :: MacOS :: MacOS X',
                'Operating System :: Microsoft :: Windows',
                'Programming Language :: Cython',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Topic :: Scientific/Engineering'],
            cmdclass = {
                'build_ext': build_ext_subclass},
        )


if __name__ == '__main__':
    setup_package()
