from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='emencia-django-newsletter',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Fantomas42',
      author_email='fantomas42@gmail.com',
      url='http://emencia.fr',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['emencia', 'emencia.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
