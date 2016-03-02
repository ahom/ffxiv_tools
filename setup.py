from setuptools import setup

setup(
    name='ffxiv_tools',
    version='0.1',
    description='tools for ffxiv',
    url='http://github.com/ahom/ffxiv_tools',
    author='Antoine Hom',
    author_email='antoine.hom@gmail.com',
    license='MIT',
    packages=['ffxiv_tools'],
    entry_points={
        'console_scripts': ['ffxiv_tools=ffxiv_tools.cli:main'],
    },
    install_requires=[
        'binr',
        'bottle'
    ],
    zip_safe=False
)
