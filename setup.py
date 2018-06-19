from collections import OrderedDict
import io

from setuptools import Command, find_packages, setup
from setuptools.command.develop import develop as BaseDevelop
from setuptools.command.sdist import sdist as BaseSDist

try:
    from wheel.bdist_wheel import bdist_wheel as BaseBDistWheel
except ImportError:
    BaseBDistWheel = None

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

version = "3.0.0.a0"


class CompileCatalogMixin(object):
    """Compile MO files with Babel's ``compile_catalog`` command. This
    happens after installing in development mode, or before building
    sdist and wheel.
    """

    def __init__(self, dist, **kw):
        # underlying commands are old-style classes on Python 2 :-(
        Command.__init__(self, dist, **kw)

    def run(self):
        is_develop = isinstance(self, Develop)

        if not is_develop:
            self.run_command("compile_catalog")

        super(CompileCatalogMixin, self).run()

        if is_develop and not self.uninstall:
            self.run_command("compile_catalog")


class Develop(CompileCatalogMixin, BaseDevelop):
    pass


class SDist(CompileCatalogMixin, BaseSDist):
    pass


command_classes = {"develop": Develop, "sdist": SDist}

if BaseBDistWheel:
    class BDistWheel(CompileCatalogMixin, BaseBDistWheel):
        pass

    command_classes["bdist_wheel"] = BDistWheel


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
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    setup_requires=["Babel"],
    install_requires=["MarkupSafe"],
    extras_require={"locale": ["Babel"]},
    cmdclass=command_classes,
)
