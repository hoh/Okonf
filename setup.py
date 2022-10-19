from setuptools import setup

setup(name='Okonf',
      version='0.2.2',
      description='Asynchronous configuration management based on Python Asyncio',
      long_description=open('README.md').read(),
      author='Hugo Herter',
      author_email='@hugoherter.com',
      url='https://github.com/hoh/Okonf/',
      packages=['okonf', 'okonf.connectors', 'okonf.facts'],
      entry_points={'console_scripts': ['okonf=okonf.__main__:app']},
      install_requires=['asyncssh', 'aiohttp', 'colorama', 'typer'],
      extras_require={'lxd': ['pylxd']},
      license='Apache License 2.0',
      keywords="configuration management",
      classifiers=['Development Status :: 2 - Pre-Alpha',
                   'Environment :: Console',
                   'Programming Language :: Python :: 3',
                   'Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Intended Audience :: Information Technology',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: Apache Software License',
                   'Topic :: System :: Installation/Setup',
                   'Topic :: System :: Systems Administration',
                   ],
)