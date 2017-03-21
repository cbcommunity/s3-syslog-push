from setuptools import setup

setup(
    name='s3-syslog-push',
    version='1.0',
    packages=['s3syslogpush'],
    url='https://github.com/cbcommunity/s3-syslog-push',
    license='MIT',
    author='Carbon Black Developer Network',
    author_email='dev-support@carbonblack.com',
    description=
    'Cb Defense Event Forwarder',
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='carbonblack bit9',
    entry_points = {
        'console_scripts': [ 's3-syslog-push = s3syslogpush.main:main' ],
    },
)
