import distutils.core
import Cython.Build
import Cython.Distutils
import os.path

def cython():
    os.environ['CFLAGS'] = '-O3 -pg'
    distutils.core.setup(
            name = "PySega emulator",
            ext_modules = Cython.Build.cythonize(["pysega/**/*.pyx","pysega/**/*.py"], exclude=['pysega/__main__.py'], language='c'),
            py_modules = ['run_pysega', 'pysega.__main__', 'pysega.__init__'] + ['pysega.%s.__init__'%(x) for x in ['audio','graphics','memory','cpu' ]],
            packages=['.'],
            package_data={'': ['pysega/graphics/palette.*.dat']},
    )

def cython_extra_args():
    sources = []
    search_dir = 'pysega'
    for root, dirs, files in os.walk(search_dir):
        for f in files:
            if os.path.splitext(f)[1] == '.py':
                sources.append(os.path.join(root, f))

    print sources

    distutils.core.setup(
            name = "PySega emulator",
            ext_modules = [distutils.extension.Extension(
                            'test', 
                            sources, 
                            extra_compile_args=['-O3', '-pg'],
                            language='c')],
            cmdclass = {'build_ext': Cython.Distutils.build_ext},
            py_modules = ['run_pysega', 'pysega.__main__', 'pysega.__init__'] + ['pysega.%s.__init__'%(x) for x in ['audio','graphics','memory','cpu' ]],
            packages=['.'],
            package_data={'': ['pysega/graphics/palette.*.dat']},
    )


def source_only():
    distutils.core.setup(
            name = "PySega emulator scripts",
            version='0.1',
            packages=['.',
                      'pysega',
                      'pysega.audio',
                      'pysega.cpu',
                      'pysega.graphics',
                      'pysega.memory',
                      'pysega.test',
                      ],
            package_dir={'pysega': 'pysega'},
            package_data={'': ['pysega/graphics/palette.*.dat']},
    )

cython()
#source_only()
#cython_extra_args()
