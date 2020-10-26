from distutils.core import setup

# Taken from scikit-learn setup.py
DISTNAME = 'pysdr'
DESCRIPTION = 'A python wrapper for librtlsdr library Realtek RTL2832U based SDR\'s'
LONG_DESCRIPTION = open('README.md').read()
LONG_DESCRIPTION = 'Readme'
MAINTAINER = 'Mayank Kumar Pal'
MAINTAINER_EMAIL = 'mynkpl1998@gmail.com'
URL = 'https://github.com/mynkpl1998/pySDR'
VERSION = '0.1.0'

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
files = ["tests/*"]

setup(
    name=DISTNAME,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    #license=LICENSE,
    url=URL,
    version=VERSION,
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages=['pysdr', 'pysdr.tests'],
    install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
    ],
    #'package' package must contain files (see list above)
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data={'commpy': files},
    python_requires = '>=3.8',
    #'runner' is in the root.
    #scripts=["runner"],
    #test_suite='nose.collector',
    #tests_require=['nose'],

    #long_description=LONG_DESCRIPTION,
    #long_description_content_type="text/markdown",
)