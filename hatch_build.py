from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        from babel.messages.frontend import compile_catalog

        cmd = compile_catalog()
        cmd.directory = "src/wtforms/locale/"
        cmd.domain = "wtforms"
        cmd.statistics = True
        cmd.finalize_options()
        cmd.run()
