import os
from setuptools import setup


pypi_name = 'hightime'


def get_version():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(script_dir, pypi_name, 'VERSION')
    return read_contents(version_path).strip()


setup(
    name=pypi_name,
    zip_safe=True,
    version=get_version(),
    description='Hightime Python API',
    author='National Instruments',
    author_email="opensource@ni.com",
    url="https://github.com/ni/hightime",
    maintainer="National Instruments",
    maintainer_email="opensource@ni.com",
    keywords=[pypi_name],
    license='MIT',
    include_package_data=True,
    packages=[pypi_name],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    package_data={pypi_name: ['VERSION']},
)
