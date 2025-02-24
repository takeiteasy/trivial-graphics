#!/usr/bin/env python

# fix building inside a virtualbox VM
# http://bugs.python.org/issue8876#msg208792
try:
    import os
    del os.link
except:
    pass

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# get our version but don't import it
# or we'll need our dependencies already installed
# https://github.com/todddeluca/happybase/commit/63573cdaefe3a2b98ece87e19d9ceb18f00bc0d9
with open('trivial/version.py', 'r') as f:
    exec(f.read())

setup(
    name='trivial',
    version=__version__,
    description='Pythonic OpenGL Bindings',
    license='BSD',
    author='George Watson',
    url='https://github.com/takeiteasy/trivial-graphics',
    install_requires=[
        # due to bugs in 1.9, we MUST use <1.9 (1.8) or some version after the issue is fixed
	# it is unclear which version fixed it, lets just be safe and say 1.13.X (which is latest minor version)
        # https://github.com/numpy/numpy/issues/5224
        'numpy>=1.13.0',
        'pyopengl',
        'pillow',
        'pyglsl>=0.0.6',
    ],
    tests_require=[],
    extras_require={
        'quickwindow': ['quickwindow'],
        'accelerate': ['pyopengl-accelerate'],
        'slimrr': ['slimrr'],
    },
    platforms=['any'],
    packages=[
        'trivial',
        'trivial.buffer',
        'trivial.shader',
    ],
    classifiers=[
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
