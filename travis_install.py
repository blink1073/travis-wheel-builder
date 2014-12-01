import os
import re

# Travis install phase
WHEEL_SITE = "http://travis-wheels.scikit-image.org"
BLAS_LAPACK_DEBS = "libblas-dev liblapack-dev libatlas3gf-base"
ENV = os.environ
PYVER = ENV['TRAVIS_PYTHON_VERSION']

# Packages known to need numpy
NEEDS_NUMPY = "scipy matplotlib pillow h5py scikit-learn"
# Packages known to need scipy
NEEDS_SCIPY = "scikit-learn"


def apt_install(*pkgs):
    """Install packages using apt"""
    os.system('sudo apt-get install %s' % ' '.join(pkgs))


def pipi(*args):
    """Install package from the wheel site or on PyPI"""
    os.system('pip install -timeout=60 -f %s %s' %
              (WHEEL_SITE, ' '.join(args)))


def pipw(*args):
    """Create a wheel for a package in the WHEELHOUSE"""
    os.system('pip wheel -w %s %s' %
              (ENV['WHEELHOUSE'], ' '.join(args)))


# Install the packages we need to build wheels
pipi('wheel', ENV['PRE_BUILD'])


for pkg_spec in ENV['TO_BUILD'].split():
    # Get package name from package spec
    # e.g. "matplotlib" from "matplotlib==1.3.1"
    pkg_name = re.split('\W', pkg_spec)[0]

    if pkg_name in 'numpy scipy'.split():
        apt_install(BLAS_LAPACK_DEBS, 'gfortran')

    # Some packages need numpy.
    # NUMPY_VERSION specifies a specific version
    if pkg_name in NEEDS_NUMPY.split():
        if "NUMPY_VERSION" in ENV:
            pipi('numpy==%s' % ENV['NUMPY_VERSION'])
        else:
            pipi('numpy')

    if pkg_name in NEEDS_SCIPY.split():
        pipi('scipy')

    if pkg_name == 'matplotlib':
        apt_install('libpng-dev libfreetype6-dev')
        # Python 3.2 only compiles up to 1.3.1
        if pkg_name == pkg_spec and PYVER == "3.2":
            pkg_spec = "matplotlib==1.3.1"

    elif pkg_name in 'pillow tifffile'.split():
        apt_install('libtiff4-dev libwebp-dev')

    elif pkg_name == 'h5py':
        apt_install('libhdf5-serial-dev')

    elif pkg_name in 'cvxopt scikit-learn'.split():
        apt_install(BLAS_LAPACK_DEBS)

    # scipy needs -v flag otherwise travis times out for lack of output
    if pkg_name == 'scipy':
        pipw('-v', pkg_spec)
    else:
        pipw(pkg_spec)
