# see https://packaging.python.org/tutorials/packaging-projects/ for installation instructions:
#   * python setup.py sdist bdist_wheel
#   * twine upload dist/pylgrim-[VERSION]-py3-none-any.whl 
from setuptools import setup, find_packages

from pylgrim import __name__, __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name=__name__,
    version=__version__,
    author="Toon Weyens",
    author_email="weyenst@gmail.com",
    description="Elementary shortest path problems, with or without resource constraints",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ToonWeyens/pylgrim",
    packages=find_packages(),
    keywords = ['espp', 'espprc', 'shortest-path', 'graph', 'python'], # arbitrary keywords
    install_requires = ['networkx',
        'logging',
        'numpy',
        'matplotlib<3.3'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
