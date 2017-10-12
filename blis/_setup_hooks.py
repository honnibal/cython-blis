def build_ext_pre_hook(cmd):
    print(cmd.extensions)

class ExtensionBuilder(distutils.command.build_ext.build_ext):
    def build_extensions(self):
        compiler = self.get_compiler_name()
        arch = self.get_arch_name()
        self.extensions = self.get_extensions(SRC, INCLUDE)
        print(compiler, arch)
        cflags, ldflags = self.get_flags(arch=arch, compiler=compiler)
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

    def get_extensions(self, src_dir, include_dir):
        if os.path.exists(include_dir):
            shutil.rmtree(include_dir)
        if use_cython:
            print("Calling Cython")
            subprocess.check_call([sys.executable, 'bin/cythonize.py'], env=os.environ)
        arch = self.get_arch_name()
        compiler = self.get_compiler_name()
        c_sources = get_c_sources(os.path.join(src_dir, arch))
        if not c_sources:
            print("Missing source files from", src_dir, arch)
            sys.exit(1)
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


