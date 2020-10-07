from setuptools import setup
from setuptools.command.develop import develop as BaseDevelop
from setuptools.command.sdist import sdist as BaseSDist

try:
    from wheel.bdist_wheel import bdist_wheel as BaseBDistWheel
except ImportError:
    BaseBDistWheel = None


class CompileCatalogMixin:
    """Compile MO files with Babel's ``compile_catalog`` command. This
    happens after installing in development mode, or before building
    sdist and wheel.
    """

    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)

    def run(self):
        is_develop = isinstance(self, Develop)

        if not is_develop:
            self.run_command("compile_catalog")

        super().run()

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


# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="WTForms",
    install_requires=["MarkupSafe"],
    cmdclass=command_classes,
)
