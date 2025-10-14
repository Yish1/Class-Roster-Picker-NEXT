import gettext
import os
from typing import Callable

# module-level current translator function (defaults to identity)
_current_gettext: Callable[[str], str] = lambda s: s


def _(s: str) -> str:
    """Translate string using the currently selected translator.

    This function is safe to import as the global `_` in other modules
    and will reflect language changes at runtime because it delegates
    to the module-level `_current_gettext`.
    """
    return _current_gettext(s)


def init_gettext(language_value: str = 'zh_CN') -> Callable[[str], str]:
    """Initialize gettext for the given language and set it as current.

    Returns the gettext function for convenience. On failure, falls back
    to zh_CN and finally to identity.
    """
    localedir1 = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'locale')
    global _current_gettext
    try:
        translate = gettext.translation(domain=f"{language_value}", localedir=localedir1, languages=[f"{language_value}"])
        _current_gettext = translate.gettext
    except Exception:
        try:
            translate = gettext.translation(domain="zh_CN", localedir=localedir1, languages=["zh_CN"])
            _current_gettext = translate.gettext
        except Exception:
            _current_gettext = lambda s: s
    return _current_gettext


def set_language(language_value: str) -> Callable[[str], str]:
    """Change current language at runtime and return the new gettext function."""
    return init_gettext(language_value)


