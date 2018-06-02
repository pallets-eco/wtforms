from collections import OrderedDict
import io
import re

from setuptools import setup, find_packages

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

with io.open("wtforms/__init__.py", "rt", encoding="utf8") as f:
    version = re.search(r"__version__ = \'(.*?)\'", f.read()).group(1)

setup(
    name="WTForms",
    version=version,
    url="https://wtforms.readthedocs.io/",
    project_urls=OrderedDict(
        (
            ("Documentation", "https://wtforms.readthedocs.io/"),
            ("Code", "https://github.com/wtforms/wtforms"),
            ("Issue tracker", "https://github.com/wtforms/wtforms/issues"),
        )
    ),
    license="BSD",
    maintainer="WTForms team",
    maintainer_email="davidism+wtforms@gmail.com",
    description=(
        "A flexible forms validation and rendering library for Python"
        " web development."
    ),
    long_description=readme,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    extras_require={"locale": ["Babel"]},
)
