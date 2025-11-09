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

def get_locale_dir(language_value: str = 'zh_CN') -> Callable[[str], str]:

    # 第一优先级：绝对路径（当前工作目录）
    absolute_locale_dir = os.path.abspath(os.path.join(os.getcwd(), 'locale'))
    if os.path.isdir(absolute_locale_dir):
        localedir = absolute_locale_dir
    else:
        # 第二优先级：可执行文件所在目录
        exe_base_path = os.path.join(os.path.dirname(sys.executable), 'locale')
        if os.path.isdir(exe_base_path):
            localedir = exe_base_path
        else:
            # 第三优先级：AppData 目录
            appdata_locale_dir = os.path.join(os.getenv("LOCALAPPDATA", ""), "CRP_onefile", "locale")
            if os.path.isdir(appdata_locale_dir):
                localedir = appdata_locale_dir
            else:
                # 到这应该就寄了
                localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')

    return localedir

def init_gettext(language_value: str = 'zh_CN') -> Callable[[str], str]:
    """
    Initialize gettext for the given language and set it as current.

    Priority:
    1. Absolute locale directory (external override)
    2. Nuitka onefile unpacked path: AppData\Local\CRP_onefile\locale
    3. Fallback to zh_CN or identity.
    """
    localedir = get_locale_dir()

    log_print("使用的 i18n 目录:", localedir)

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


