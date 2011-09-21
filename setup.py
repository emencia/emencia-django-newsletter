import os
from setuptools import setup, find_packages

version = '0.3.dev'

setup(name='emencia.django.newsletter',
      version=version,
      description="A Django app for sending newsletter by email to a contact list.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      keywords='django, newsletter, mailing',
      classifiers=[
          'Framework :: Django',
          'Programming Language :: Python',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: BSD License',
          'Development Status :: 5 - Production/Stable',
          'Topic :: Software Development :: Libraries :: Python Modules',],

      author='Fantomas42',
      author_email='fantomas42@gmail.com',
      url='http://emencia.fr',

      license='BSD License',
      packages=find_packages(exclude=['demo']),
      namespace_packages=['emencia', 'emencia.django'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'html2text',
                        'python-dateutil==1.5',
                        'BeautifulSoup',
                        'django-tagging',
                        'vobject',
                        'xlwt',
                        'xlrd'])
