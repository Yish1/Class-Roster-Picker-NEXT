import gettext
import os
from typing import Callable


def init_gettext(language_value: str = 'zh_CN') -> Callable[[str], str]:
    """Initialize gettext and return the _ translator function.

    Fallback to zh_CN if the target language fails.
    """
    localedir1 = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    try:
        translate = gettext.translation(domain=f"{language_value}", localedir=localedir1, languages=[f"{language_value}"])
        return translate.gettext
    except Exception:
        try:
            translate = gettext.translation(domain="zh_CN", localedir=localedir1, languages=["zh_CN"])
            return translate.gettext
        except Exception:
            # last resort: identity
            return lambda s: s


