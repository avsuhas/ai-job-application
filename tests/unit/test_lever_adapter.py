"""Independent unit test gate for the Lever adapter (docs/17 Phase 13
Expansion Rule: every adapter passes its own detection/classification/
identity/field/submission/confirmation tests — no inherited trust)."""

from job_platform.ats.base import AdapterStatus, CapabilityLevel, PageType
from job_platform.ats.greenhouse import GreenhouseAdapter, default_registry
from job_platform.ats.lever import LeverAdapter
from job_platform.browser.models import (
    FieldType,
    FormAction,
    FormField,
    PageSnapshot,
    SafetySignals,
)


def field(field_id, label="", field_type=FieldType.TEXT, **kw) -> FormField:
    return FormField(field_id=field_id, label=label, field_type=field_type,
                     selector=f"#{field_id}", **kw)


def lever_snapshot(**overrides) -> PageSnapshot:
    defaults = dict(
        url="https://jobs.lever.co/othercorp/abc123def456789a",
        title="OtherCorp - Backend Engineer",
        heading="Backend Engineer",
        fields=[
            field("name", "Full name"),
            field("email", "Email", FieldType.EMAIL),
            field("phone", "Phone", FieldType.PHONE),
            field("org", "Current company"),
            field("resume", "Resume/CV", FieldType.FILE),
            field("urls[LinkedIn]", "LinkedIn URL", FieldType.URL),
        ],
        actions=[
            FormAction(action_id="btn-submit", type="submit",
                       label="Submit application", selector="#btn-submit"),
        ],
    )
    defaults.update(overrides)
    return PageSnapshot(**defaults)


class TestLeverDetection:
    def test_domain_detection(self):
        result = LeverAdapter().detect("https://jobs.lever.co/othercorp/abc")
        assert result.detected_ats == "lever"
        assert result.confidence >= 95
        assert "domain_pattern" in result.detection_methods

    def test_eu_domain_detection(self):
        result = LeverAdapter().detect("https://jobs.eu.lever.co/othercorp/abc")
        assert result.confidence >= 95

    def test_page_signature_without_domain(self):
        snapshot = lever_snapshot(url="https://careers.othercorp.com/apply")
        result = LeverAdapter().detect(snapshot.url, snapshot)
        assert result.confidence >= 90
        assert "page_signature" in result.detection_methods

    def test_embedded_iframe_detection(self):
        snapshot = lever_snapshot(
            url="https://careers.othercorp.com/x",
            frames=["Application https://jobs.lever.co/othercorp/abc"],
        )
        result = LeverAdapter().detect("https://careers.othercorp.com/x", snapshot)
        assert result.confidence >= 85
        assert "embedded_iframe" in result.detection_methods

    def test_unrelated_page_not_detected(self):
        snapshot = PageSnapshot(url="https://other.example.com", title="Careers",
                                fields=[field("q", "Search")])
        assert LeverAdapter().detect("https://other.example.com", snapshot).confidence == 0


class TestAdapterIsolation:
    """The Expansion Rule: adapters must not cross-match each other."""

    def test_greenhouse_does_not_match_lever_page(self):
        snapshot = lever_snapshot(url="https://careers.othercorp.com/apply")
        # Greenhouse signature needs first_name/last_name; Lever has `name`.
        assert GreenhouseAdapter().detect(snapshot.url, snapshot).confidence == 0

    def test_lever_does_not_match_greenhouse_page(self):
        gh = PageSnapshot(
            url="https://boards.greenhouse.io/x/jobs/1",
            title="Job Application for Backend Engineer at ExampleCo",
            fields=[field("first_name"), field("last_name"),
                    field("email", field_type=FieldType.EMAIL)],
        )
        assert LeverAdapter().detect(gh.url, gh).confidence == 0

    def test_registry_routes_each_platform_to_its_adapter(self):
        registry = default_registry()
        assert registry.resolve("https://jobs.lever.co/x/abc").adapter_id == "lever"
        assert (
            registry.resolve("https://boards.greenhouse.io/x/jobs/1").adapter_id
            == "greenhouse"
        )
        assert registry.resolve("https://careers.unknown.com/9").adapter_id is None

    def test_registry_lists_both_adapters(self):
        ids = {a.metadata.adapter_id for a in default_registry().list_adapters()}
        assert ids == {"greenhouse", "lever"}


class TestLeverClassification:
    def test_application_form(self):
        result = LeverAdapter().classify_page(lever_snapshot())
        assert result.page_type == PageType.APPLICATION_FORM
        assert result.confidence >= 90

    def test_confirmation_page(self):
        snapshot = PageSnapshot(
            url="https://jobs.lever.co/x/abc/thanks",
            title="Application submitted",
            heading="Thank you for applying to OtherCorp",
        )
        assert LeverAdapter().classify_page(snapshot).page_type == PageType.CONFIRMATION

    def test_closed_page(self):
        snapshot = PageSnapshot(url="https://jobs.lever.co/x/abc",
                                heading="This role is no longer accepting applications")
        assert (
            LeverAdapter().classify_page(snapshot).page_type
            == PageType.APPLICATION_CLOSED
        )

    def test_captcha_page(self):
        snapshot = lever_snapshot(signals=SafetySignals(captcha=True))
        assert LeverAdapter().classify_page(snapshot).page_type == PageType.CAPTCHA


class TestLeverIdentity:
    def test_identity_from_title_and_url(self):
        identity = LeverAdapter().extract_job_identity(lever_snapshot())
        assert identity.company == "Othercorp"
        assert identity.title == "Backend Engineer"
        assert identity.job_id == "abc123def456789a"
        assert identity.confidence >= 90

    def test_identity_falls_back_to_heading(self):
        snapshot = PageSnapshot(
            url="https://jobs.lever.co/acme/deadbeefdeadbeef",
            title="Apply", heading="Staff Engineer",
        )
        identity = LeverAdapter().extract_job_identity(snapshot)
        assert identity.company == "Acme"
        assert identity.title == "Staff Engineer"


class TestLeverFieldMapping:
    def test_known_lever_fields(self):
        adapter = LeverAdapter()
        assert adapter.classify_field(field("name")).semantic_type == "personal.full_name"
        assert adapter.classify_field(field("org")).semantic_type == \
            "employment.current_company"
        linkedin = adapter.classify_field(field("urls[LinkedIn]", field_type=FieldType.URL))
        assert linkedin.semantic_type == "links.linkedin"
        assert linkedin.confidence == 98
        resume = adapter.classify_field(field("resume", field_type=FieldType.FILE))
        assert resume.semantic_type == "documents.resume"

    def test_custom_card_defers_to_generic(self):
        assert LeverAdapter().classify_field(field("cards[abc][0]", "Why us?")) is None


class TestLeverSubmissionAndConfirmation:
    def test_submit_control_by_id(self):
        control = LeverAdapter().identify_submission_control(lever_snapshot())
        assert control.action_id == "btn-submit"

    def test_confirmation_verified(self):
        snapshot = PageSnapshot(
            url="https://jobs.lever.co/x/abc/thanks",
            heading="Thank you for applying to OtherCorp",
        )
        result = LeverAdapter().verify_confirmation(snapshot)
        assert result.confirmed

    def test_application_page_not_confirmed(self):
        assert not LeverAdapter().verify_confirmation(lever_snapshot()).confirmed

    def test_metadata_is_beta_simulated(self):
        meta = LeverAdapter().metadata
        assert meta.status == AdapterStatus.BETA
        assert meta.capabilities["submission"] == CapabilityLevel.SIMULATED_ONLY
