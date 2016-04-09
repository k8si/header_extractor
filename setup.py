from setuptools import setup, find_packages

setup(name='header_extractor',
      author='k8si',
      author_email='ksilvers@cs.umass.edu',
      packages=find_packages(),
      package_data={'': ['*.jar']},
      install_requires=[
            'bibtexparser',
            'beautifulsoup4'
      ])
