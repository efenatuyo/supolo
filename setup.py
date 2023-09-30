from setuptools import setup, find_packages

setup(
    name='supolo',
    version='1.0.0',
    description='A fast discord nuke bot based package',
    author='Xolo',
    url='https://github.com/efenatuyo/supolo',
    packages=find_packages(),
    install_requires=[
        'aiohttp',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='Apache License 2.0',
)
