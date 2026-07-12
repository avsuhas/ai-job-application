"""Safety-state detection: CAPTCHA, login walls, MFA prompts (docs/06).

Pure functions over extracted page content so they are unit-testable without
a browser. The engine pauses on any positive signal — it never attempts to
solve a CAPTCHA, log in, or complete MFA automatically.
"""

from __future__ import annotations

from pydantic import BaseModel

from job_platform.browser.models import PageState, SafetySignals

_CAPTCHA_MARKERS = (
    "g-recaptcha",
    "grecaptcha",
    "h-captcha",
    "hcaptcha",
    "cf-turnstile",
    "recaptcha",
    "are you a robot",
    "confirm you are human",
    "verify you are human",
    "security check",
)

_LOGIN_MARKERS = (
    "sign in",
    "log in",
    "login",
    "forgot password",
    "create an account to continue",
)

_MFA_MARKERS = (
    "two-factor",
    "two factor",
    "2-step verification",
    "multi-factor",
    "verification code",
    "one-time passcode",
    "one-time code",
    "authenticator app",
)


class PageContent(BaseModel):
    """Minimal extraction the detectors operate on."""

    text: str = ""
    html_classes: str = ""
    iframe_titles: list[str] = []
    has_password_field: bool = False
    has_one_time_code_field: bool = False


def detect_signals(content: PageContent) -> SafetySignals:
    text = content.text.lower()
    classes = content.html_classes.lower()
    iframes = " ".join(content.iframe_titles).lower()

    captcha = any(m in classes or m in text or m in iframes for m in _CAPTCHA_MARKERS)
    mfa = content.has_one_time_code_field or any(m in text for m in _MFA_MARKERS)
    # A password field plus login language means a login wall; an MFA page
    # is not a login wall even though both block progress.
    login = (
        content.has_password_field
        and any(m in text for m in _LOGIN_MARKERS)
        and not mfa
    )
    return SafetySignals(captcha=captcha, login=login, mfa=mfa)


def state_for_signals(signals: SafetySignals) -> PageState:
    if signals.captcha:
        return PageState.CAPTCHA_DETECTED
    if signals.mfa:
        return PageState.MFA_REQUIRED
    if signals.login:
        return PageState.LOGIN_REQUIRED
    return PageState.READY
