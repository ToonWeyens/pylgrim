from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pylgrim",
    version="1.0.1",
    author="Toon Weyens",
    author_email="weyenst@gmail.com",
    description="Elementary shortest path problems, with or without resource constraints",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/ToonWeyens/pylgrim",
    packages=find_packages(),
    keywords = ['espp', 'espprc', 'shortest-path', 'graph', 'python'], # arbitrary keywords
    requires = ['networkx', 'logging', 'numpy', 'copy', 'collections', 'matplotlib', 'random', 'timeit'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
