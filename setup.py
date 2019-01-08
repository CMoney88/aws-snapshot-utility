from setuptools import setup

setup(
    name='aws-snapshot-utility',
    version='0.1',
    author='Cameron Dobbs',
    author_email='cmdobbs888@gmail.com',
    description='AWS Snapshot Utility is a CLI tool to manage AWS EC2 snapshots',
    license='GPLv3+',
    packages=['shotty'],
    url="https://github.com/CMoney88/aws-snapshot-utility",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
    ''', #looks in shotty file, looks at shotty module, and goes to cli function
)
