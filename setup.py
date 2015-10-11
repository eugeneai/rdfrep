import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    'Chameleon',
    'rdflib',
    'pyramid-chameleon',
    'rdflib-kyotocabinet'
    ]

setup(name='rdfrep',
      version='0.0',
      description='rdfrep',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      dependency_links = ['https://github.com/RDFLib/rdflib-kyotocabinet/tarball/master#egg=rdflib-kyotocabinet-0.1'],
      tests_require=requires,
      test_suite="rdfrep",
      entry_points="""\
      [paste.app_factory]
      main = rdfrep:main
      """,
      )
