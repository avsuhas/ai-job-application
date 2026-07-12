"""Unit tests for the ATS adapter contract, registry, and Greenhouse adapter
(docs/09) — no browser required."""

from job_platform.ats.base import AdapterStatus, CapabilityLevel, PageType
from job_platform.ats.greenhouse import GreenhouseAdapter, default_registry
from job_platform.ats.registry import ATSAdapterRegistry
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


def gh_snapshot(**overrides) -> PageSnapshot:
    defaults = dict(
        url="https://boards.greenhouse.io/exampleco/jobs/4001",
        title="Job Application for Backend Engineer at ExampleCo",
        heading="Backend Engineer",
        fields=[
            field("first_name", "First Name"),
            field("last_name", "Last Name"),
            field("email", "Email", FieldType.EMAIL),
            field("phone", "Phone", FieldType.PHONE),
        ],
        actions=[
            FormAction(action_id="submit_app", type="submit",
                       label="Submit Application", selector="#submit_app"),
        ],
    )
    defaults.update(overrides)
    return PageSnapshot(**defaults)


class TestGreenhouseDetection:
    def test_domain_detection_is_high_confidence(self):
        result = GreenhouseAdapter().detect("https://boards.greenhouse.io/x/jobs/1")
        assert result.detected_ats == "greenhouse"
        assert result.confidence >= 95
        assert "domain_pattern" in result.detection_methods

    def test_job_boards_subdomain_detected(self):
        result = GreenhouseAdapter().detect("https://job-boards.greenhouse.io/x/jobs/1")
        assert result.confidence >= 95

    def test_embedded_iframe_detection(self):
        snapshot = gh_snapshot(
            url="https://careers.example.com/jobs/1",
            frames=["Application form https://boards.greenhouse.io/embed/job_app?for=x"],
        )
        result = GreenhouseAdapter().detect("https://careers.example.com/jobs/1", snapshot)
        assert result.confidence >= 85
        assert "embedded_iframe" in result.detection_methods

    def test_page_signature_detection_without_domain(self):
        snapshot = gh_snapshot(url="https://careers.example.com/apply")
        result = GreenhouseAdapter().detect("https://careers.example.com/apply", snapshot)
        assert result.confidence >= 90
        assert "page_signature" in result.detection_methods

    def test_unrelated_page_not_detected(self):
        snapshot = PageSnapshot(url="https://other.example.com", title="Careers",
                                fields=[field("q", "Search")])
        result = GreenhouseAdapter().detect("https://other.example.com", snapshot)
        assert result.confidence == 0
        assert result.matched_adapter is None


class TestRegistry:
    def test_resolves_greenhouse_by_domain(self):
        resolution = default_registry().resolve("https://boards.greenhouse.io/x/jobs/1")
        assert resolution.adapter_id == "greenhouse"
        assert resolution.use_generic_fallback

    def test_unknown_site_falls_back_to_generic(self):
        resolution = default_registry().resolve("https://careers.unknown-ats.com/jobs/9")
        assert resolution.adapter_id is None
        assert resolution.use_generic_fallback

    def test_package_override_wins(self):
        resolution = default_registry().resolve(
            "https://careers.unknown-ats.com/jobs/9",
            override_adapter_id="greenhouse",
        )
        assert resolution.adapter_id == "greenhouse"
        assert resolution.detection.detection_methods == ["package_override"]

    def test_disabled_adapter_never_matches(self):
        registry = ATSAdapterRegistry()
        adapter = GreenhouseAdapter()
        adapter._metadata = adapter.metadata.model_copy(
            update={"status": AdapterStatus.DISABLED}
        )
        registry.register(adapter)
        resolution = registry.resolve("https://boards.greenhouse.io/x/jobs/1")
        assert resolution.adapter_id is None

    def test_metadata_declares_simulated_submission_only(self):
        meta = GreenhouseAdapter().metadata
        assert meta.status == AdapterStatus.BETA
        assert meta.capabilities["submission"] == CapabilityLevel.SIMULATED_ONLY


class TestGreenhouseClassification:
    def test_application_form_page(self):
        result = GreenhouseAdapter().classify_page(gh_snapshot())
        assert result.page_type == PageType.APPLICATION_FORM
        assert result.confidence >= 90

    def test_confirmation_page(self):
        snapshot = PageSnapshot(
            url="https://boards.greenhouse.io/x/confirmation",
            title="Job Application Confirmation",
            heading="Thank you for applying to ExampleCo",
        )
        result = GreenhouseAdapter().classify_page(snapshot)
        assert result.page_type == PageType.CONFIRMATION

    def test_closed_job_page(self):
        snapshot = PageSnapshot(
            url="https://boards.greenhouse.io/x/jobs/1",
            heading="This job is no longer open",
        )
        result = GreenhouseAdapter().classify_page(snapshot)
        assert result.page_type == PageType.APPLICATION_CLOSED

    def test_captcha_page(self):
        snapshot = gh_snapshot(signals=SafetySignals(captcha=True))
        assert GreenhouseAdapter().classify_page(snapshot).page_type == PageType.CAPTCHA


class TestJobIdentity:
    def test_identity_from_title_and_url(self):
        identity = GreenhouseAdapter().extract_job_identity(gh_snapshot())
        assert identity.company == "ExampleCo"
        assert identity.title == "Backend Engineer"
        assert identity.job_id == "4001"
        assert identity.confidence >= 90

    def test_fallback_to_heading(self):
        snapshot = PageSnapshot(url="https://x", title="Apply", heading="SRE Role")
        identity = GreenhouseAdapter().extract_job_identity(snapshot)
        assert identity.title == "SRE Role"
        assert identity.confidence < 60


class TestGreenhouseFieldMapping:
    def test_known_ids_classified_with_ats_confidence(self):
        adapter = GreenhouseAdapter()
        result = adapter.classify_field(field("first_name", "Vorname"))
        assert result.semantic_type == "personal.first_name"
        assert result.confidence == 98
        assert result.method == "ats_known_field_id"

        resume = adapter.classify_field(field("resume", "Attach", FieldType.FILE))
        assert resume.semantic_type == "documents.resume"

        gender = adapter.classify_field(field("gender", "Gender", FieldType.SELECT))
        assert gender.semantic_type == "demographic.gender"

    def test_custom_question_defers_to_generic(self):
        adapter = GreenhouseAdapter()
        custom = adapter.classify_field(
            field("job_application_answers_attributes_0_text_value", "Describe...")
        )
        assert custom is None


class TestSubmissionControl:
    def test_submit_app_control_identified(self):
        control = GreenhouseAdapter().identify_submission_control(gh_snapshot())
        assert control is not None
        assert control.action_id == "submit_app"

    def test_no_control_on_confirmation_page(self):
        snapshot = PageSnapshot(url="https://x", heading="Thank you for applying")
        assert GreenhouseAdapter().identify_submission_control(snapshot) is None


class TestConfirmationVerification:
    def test_confirmation_verified_from_heading(self):
        snapshot = PageSnapshot(
            url="https://boards.greenhouse.io/x/confirmation",
            heading="Thank you for applying to ExampleCo",
        )
        result = GreenhouseAdapter().verify_confirmation(snapshot)
        assert result.confirmed
        assert result.evidence

    def test_non_confirmation_page_not_verified(self):
        result = GreenhouseAdapter().verify_confirmation(gh_snapshot())
        assert not result.confirmed
