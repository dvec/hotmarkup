from setuptools import setup, find_packages
from os.path import join, dirname

with open(join(dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()


setup(
    name='hotmarkup',
    version='0.1.1',
    author="Anton Ugryumov",
    author_email='dvecend@gmail.com',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dvec/hotmarkup",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)