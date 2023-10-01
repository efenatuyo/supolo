from setuptools import setup, find_packages

setup(
    name='supolo',
    version='1.2.2',
    description='A fast discord nuke bot based package',
    author='Xolo',
    url='https://github.com/efenatuyo/supolo',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
    ],
)
