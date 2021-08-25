"""
EECS 485 project 1 static site generator.

Andrew DeOrio <awdeorio@umich.edu>
"""

from setuptools import setup

setup(
    name='instagenerator',
    version='0.1.0',
    packages=['instagenerator'],
    include_package_data=True,
    install_requires=[
        'bs4',
        'click',
        'html5validator',
        'jinja2',
        'pycodestyle',
        'pydocstyle',
        'pylint',
        'pytest',
        'requests',
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'instagenerator = instagenerator.__main__:main'
        ]
    },
)
