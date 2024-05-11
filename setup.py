from setuptools import setup, find_packages
import os

version = os.getenv('PACKAGE_VERSION', '0.1.0') 

setup(
    name='hydrate-minio-weaviate',
    version=version,
    packages=find_packages(),
    description='A package to fetch, store, and process documents using MinIO and Weaviate.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='David Cannan',
    author_email='cdaprod@cdaprod.dev',
    url='https://github.com/Cdaprod/hydrate',
    install_requires=[
        'requests',
        'minio',
        'weaviate-client',
        'pydantic',
        'unstructured',
        'io',
        'tempfile',
        're',
        'dotenv'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)