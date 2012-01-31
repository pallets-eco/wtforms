import os

def messages_path():
    """
    Determine the path to the 'messages' directory as best possible.
    """
    module_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(module_path), 'messages')


def get_builtin_gnu_translations(languages=None):
    """
    Get a gettext.GNUTranslations object pointing at the
    included translation files.
    """
    import gettext
    return gettext.translation('wtforms', messages_path(), languages)
