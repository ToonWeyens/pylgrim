try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(
  name = 'pylgrim',
  packages = ['pylgrim'], # this must be the same as the name above
  version = '0.1',
  description = 'Elementary shortest path problems (with resource constraints)',
  author = 'Toon Weyens',
  author_email = 'weyenst@gmail.com',
  url = 'https://github.com/exteris/pylgrim', # use the URL to the github repo
  download_url = 'https://github.com/exteris/pylgrim/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['espp', 'espprc', 'shortest-path', 'graph', 'python'], # arbitrary keywords
  install_requires = [],
  requires = ['networkx'],
  classifiers = [],
)
