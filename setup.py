from setuptools import setup, find_packages
import os

version = '1.0'

requires = [
      'setuptools',
      # -*- Extra requirements: -*-
      'Paste',
]

tests_requires = requires + ['WebTest', 'nose']

setup(name='sc.s17.proxy',
      version=version,
      description="""A wsgi proxy that pass REMOTE_USER environment variable
                     to the backend as something like HTTP_X_REMOTE_USER""",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      keywords='web pyramid pylons wsgi login repozo.who',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.s17'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_requires,
      test_suite="sc.s17.proxy",
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = sc.s17.proxy:main
      """,
      )
