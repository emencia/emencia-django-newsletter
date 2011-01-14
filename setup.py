from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='emencia.django.newsletter',
      version=version,
      description="A Django app for sending newsletter by email to a contact list.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      keywords='django, newsletter, mailing',
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: BSD License',
          'Framework :: Django',
          ],

      author='Fantomas42',
      author_email='fantomas42@gmail.com',
      url='http://emencia.fr',

      license='BSD License',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['emencia', 'emencia.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'html2text',
          'BeautifulSoup',
          'vobject',
          'xlwt',
          'xlrd',
          'tagging',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
