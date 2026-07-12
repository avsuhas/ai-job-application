"""Unit tests for navigation policy and safety detection (no browser needed)."""

from job_platform.browser.detection import PageContent, detect_signals, state_for_signals
from job_platform.browser.models import PageState
from job_platform.browser.navigation import NavigationPolicy


class TestNavigationPolicy:
    def test_application_url_and_host_allowed(self):
        policy = NavigationPolicy.for_application("https://jobs.example.com/apply/42")
        assert policy.is_allowed("https://jobs.example.com/apply/42")
        assert policy.is_allowed("https://jobs.example.com/apply/42/step2")

    def test_known_ats_domains_allowed(self):
        policy = NavigationPolicy.for_application("https://careers.example.com/jobs/1")
        assert policy.is_allowed("https://boards.greenhouse.io/exampleco/jobs/1")
        assert policy.is_allowed("https://exampleco.myworkdayjobs.com/en-US/careers")

    def test_unrelated_domains_blocked(self):
        policy = NavigationPolicy.for_application("https://careers.example.com/jobs/1")
        assert not policy.is_allowed("https://evil.example.net/phish")
        assert not policy.is_allowed("https://google.com")

    def test_lookalike_domain_blocked(self):
        policy = NavigationPolicy.for_application("https://careers.example.com/jobs/1")
        assert not policy.is_allowed("https://notgreenhouse.io.evil.com/x")
        assert not policy.is_allowed("https://fakegreenhouse.io/x")

    def test_non_http_schemes_blocked(self):
        policy = NavigationPolicy.for_application("https://careers.example.com/jobs/1")
        assert not policy.is_allowed("javascript:alert(1)")
        assert not policy.is_allowed("file:///etc/passwd")

    def test_local_files_only_when_explicitly_allowed(self):
        blocked = NavigationPolicy.for_application("https://x.example.com/1")
        allowed = NavigationPolicy.for_application(
            "https://x.example.com/1", allow_local_files=True
        )
        assert not blocked.is_allowed("file:///tmp/form.html")
        assert allowed.is_allowed("file:///tmp/form.html")


class TestSafetyDetection:
    def test_captcha_detected_from_class(self):
        signals = detect_signals(PageContent(html_classes="g-recaptcha challenge"))
        assert signals.captcha
        assert state_for_signals(signals) == PageState.CAPTCHA_DETECTED

    def test_captcha_detected_from_text(self):
        signals = detect_signals(PageContent(text="Please confirm you are human."))
        assert signals.captcha

    def test_login_detected(self):
        signals = detect_signals(
            PageContent(text="Sign in to your account. Forgot password?",
                        has_password_field=True)
        )
        assert signals.login
        assert state_for_signals(signals) == PageState.LOGIN_REQUIRED

    def test_password_without_login_language_is_not_login_wall(self):
        signals = detect_signals(PageContent(text="Create your profile", has_password_field=True))
        assert not signals.login

    def test_mfa_detected_and_wins_over_login(self):
        signals = detect_signals(
            PageContent(
                text="Enter the verification code we sent. Sign in.",
                has_password_field=True,
                has_one_time_code_field=True,
            )
        )
        assert signals.mfa
        assert not signals.login
        assert state_for_signals(signals) == PageState.MFA_REQUIRED

    def test_clean_page_is_ready(self):
        signals = detect_signals(PageContent(text="Tell us about your experience"))
        assert state_for_signals(signals) == PageState.READY
