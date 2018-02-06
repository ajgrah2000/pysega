import distutils.core
import Cython.Build

def cython():
    distutils.core.setup(
            name = "PySega emulator",
            ext_modules = Cython.Build.cythonize("pysega/**/*.py", exclude=['pysega/__main__.py'], language='c++'),
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
