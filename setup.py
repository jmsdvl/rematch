import re
from setuptools import setup, find_packages

packages = [
    'rematch',
]

with open('rematch/__init__.py', 'r') as fp:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fp.read(), re.MULTILINE).group(1)

with open('README.md', 'r') as fp:
    readme = fp.read()


setup(
        name='rematch',
        version=version,
        description='NFA based regular expression matching engine.',
        long_description=readme,

        author='John M Still',
        author_email='john@jmsdvl.com',

        packages=packages,
        entry_points={
            "console_scripts": [
                "rematch=rematch.cli:cli",
            ]
        },
)
