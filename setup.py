import os
from setuptools.command.test import test
from setuptools import setup


class PyTest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


pypi_name = 'hightime'


def read_contents(file_to_read):
    with open(file_to_read, 'r') as f:
        return f.read()


def get_version():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(script_dir, pypi_name, 'VERSION')
    return read_contents(version_path).strip()


setup(
    name=pypi_name,
    zip_safe=True,
    version=get_version(),
    description='Hightime Python API',
    long_description=read_contents('README.md'),
    long_description_content_type='text/markdown',
    author='National Instruments',
    author_email="opensource@ni.com",
    url="https://github.com/ni/hightime",
    maintainer="National Instruments",
    maintainer_email="opensource@ni.com",
    keywords=[pypi_name],
    license='MIT',
    include_package_data=True,
    packages=[pypi_name],
    install_requires=[],
    tests_require=['pytest'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    cmdclass={'test': PyTest},
    package_data={pypi_name: ['VERSION']},
)
