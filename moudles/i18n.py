import gettext
import os, sys
from typing import Callable
from .logger_util import log_print

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
    # 检测是否在 Nuitka onefile 模式下运行
    if getattr(sys, "_MEIPASS", None):
        base_path = sys._MEIPASS
    elif getattr(sys, "frozen", False):
        # Nuitka 没有 _MEIPASS，但 frozen=True 说明是打包运行
        base_path = os.path.dirname(sys.executable)
    else:
        # 正常开发环境
        base_path = os.path.abspath(os.path.dirname(__file__))

    # locale 路径兼容开发与打包
    localedir = os.path.join(base_path, 'locale')
    log_print("i18n目录:", localedir)

    global _current_gettext
    try:
        translate = gettext.translation(domain=language_value, localedir=localedir, languages=[language_value])
        _current_gettext = translate.gettext
    except Exception:
        try:
            translate = gettext.translation(domain="zh_CN", localedir=localedir, languages=["zh_CN"])
            _current_gettext = translate.gettext
        except Exception:
            _current_gettext = lambda s: s

    return _current_gettext


def set_language(language_value: str) -> Callable[[str], str]:
    """Change current language at runtime and return the new gettext function."""
    return init_gettext(language_value)


