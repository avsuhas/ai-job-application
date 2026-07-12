"""Tests for job discovery: sources, normalization, dedup, adapters, service."""

import json

import httpx
import pytest
import respx

from job_platform.jobs.deduplicator import deduplicate
from job_platform.jobs.models import Job
from job_platform.jobs.normalizer import html_to_text, infer_country, normalize_job
from job_platform.jobs.service import DiscoveryService, SearchFilters, matches_filters
from job_platform.jobs.sources import CompanySource, detect_ats, load_company_sources

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/exampleco/jobs"
LEVER_URL = "https://api.lever.co/v0/postings/othercorp"


@pytest.fixture
def greenhouse_payload(fixtures_dir):
    return json.loads((fixtures_dir / "jobs" / "greenhouse_board.json").read_text())


@pytest.fixture
def lever_payload(fixtures_dir):
    return json.loads((fixtures_dir / "jobs" / "lever_postings.json").read_text())


def gh_source() -> CompanySource:
    return CompanySource(
        id="exampleco", name="ExampleCo", career_url="https://boards.greenhouse.io/exampleco"
    )


def lever_source() -> CompanySource:
    return CompanySource(
        id="othercorp", name="OtherCorp", career_url="https://jobs.lever.co/othercorp"
    )


class TestSources:
    def test_detect_greenhouse(self):
        assert detect_ats("https://boards.greenhouse.io/exampleco") == ("greenhouse", "exampleco")

    def test_detect_lever(self):
        assert detect_ats("https://jobs.lever.co/othercorp/") == ("lever", "othercorp")

    def test_detect_unknown(self):
        assert detect_ats("https://careers.example.com") == ("", "")

    def test_load_company_sources(self, tmp_path):
        path = tmp_path / "companies.json"
        path.write_text(json.dumps([{"id": "a", "name": "A", "enabled": False}]))
        sources = load_company_sources(path)
        assert sources[0].id == "a"
        assert sources[0].enabled is False

    def test_missing_companies_file_returns_empty(self, tmp_path):
        assert load_company_sources(tmp_path / "nope.json") == []


class TestNormalizer:
    def test_html_to_text(self):
        assert html_to_text("<p>Build in <b>Python</b>.</p><p>Now.</p>") == "Build in Python.\nNow."

    def test_infer_country_from_state(self):
        assert infer_country("Austin, TX") == "United States"

    def test_infer_country_from_name(self):
        assert infer_country("Berlin, Germany") == "Germany"
        assert infer_country("Remote - USA") == "United States"

    def test_normalize_assigns_stable_id_and_remote(self):
        job = Job(
            id="", company="A", title="  Backend   Engineer ", location="Remote - US",
            url="https://x/1", job_id="9",
        )
        first = normalize_job(job)
        second = normalize_job(job)
        assert first.id == second.id
        assert first.id.startswith("job_")
        assert first.title == "Backend Engineer"
        assert first.remote_status == "remote"


class TestDeduplicator:
    def test_same_job_id_deduped(self):
        a = Job(id="1", company="A", title="X", job_id="42", url="https://a/1")
        b = Job(id="2", company="A", title="X renamed", job_id="42", url="https://a/2")
        assert len(deduplicate([a, b])) == 1

    def test_same_url_deduped(self):
        a = Job(id="1", company="A", title="X", url="https://a/1")
        b = Job(id="2", company="A", title="Y", url="https://a/1/")
        assert len(deduplicate([a, b])) == 1

    def test_company_title_location_deduped(self):
        a = Job(id="1", company="A", title="X", location="Austin", url="https://a/1")
        b = Job(id="2", company="A", title="x", location="austin", url="https://a/2")
        assert len(deduplicate([a, b])) == 1

    def test_different_jobs_kept(self):
        a = Job(id="1", company="A", title="X", location="Austin", url="https://a/1")
        b = Job(id="2", company="A", title="Y", location="Austin", url="https://a/2")
        assert len(deduplicate([a, b])) == 2


class TestFilters:
    def make(self, **kw):
        defaults = dict(id="1", company="A", title="Backend Engineer",
                        description="Python and Kafka", country="United States",
                        location="Austin, TX", remote_status="unknown", url="https://a/1")
        defaults.update(kw)
        return Job(**defaults)

    def test_keyword_filter(self):
        assert matches_filters(self.make(), SearchFilters(keywords=["backend"]))
        assert not matches_filters(self.make(), SearchFilters(keywords=["compiler"]))

    def test_excluded_keywords(self):
        assert not matches_filters(
            self.make(title="Backend Intern"), SearchFilters(excluded_keywords=["intern"])
        )

    def test_country_filter(self):
        assert matches_filters(self.make(), SearchFilters(countries=["United States"]))
        assert not matches_filters(self.make(), SearchFilters(countries=["Germany"]))

    def test_remote_filter(self):
        assert not matches_filters(self.make(), SearchFilters(remote_only=True))
        assert matches_filters(self.make(remote_status="remote"), SearchFilters(remote_only=True))


class TestDiscoveryService:
    @respx.mock
    async def test_greenhouse_discovery_end_to_end(self, greenhouse_payload):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        result = await DiscoveryService().discover([gh_source()])
        assert len(result.jobs) == 3
        job = next(j for j in result.jobs if j.job_id == "4001")
        assert job.company == "ExampleCo"
        assert job.title == "Senior Backend Engineer"
        assert job.country == "United States"
        assert "Python" in job.description and "<" not in job.description
        assert job.ats == "greenhouse"
        assert result.outcomes[0].job_count == 3

    @respx.mock
    async def test_lever_discovery_end_to_end(self, lever_payload):
        respx.get(LEVER_URL).mock(return_value=httpx.Response(200, json=lever_payload))
        result = await DiscoveryService().discover([lever_source()])
        assert len(result.jobs) == 2
        remote = next(j for j in result.jobs if j.job_id == "abc-123")
        assert remote.remote_status == "remote"
        assert remote.employment_type == "Full-time"
        onsite = next(j for j in result.jobs if j.job_id == "def-456")
        assert onsite.country == "Canada"

    @respx.mock
    async def test_multi_source_with_filters(self, greenhouse_payload, lever_payload):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        respx.get(LEVER_URL).mock(return_value=httpx.Response(200, json=lever_payload))
        filters = SearchFilters(keywords=["backend"], excluded_keywords=["intern"])
        result = await DiscoveryService().discover([gh_source(), lever_source()], filters)
        titles = {j.title for j in result.jobs}
        assert titles == {"Senior Backend Engineer"} or all("Backend" in t for t in titles)
        assert all("intern" not in j.title.lower() for j in result.jobs)

    @respx.mock
    async def test_failed_source_reports_error_without_breaking_others(
        self, greenhouse_payload
    ):
        respx.get(GREENHOUSE_URL).mock(return_value=httpx.Response(200, json=greenhouse_payload))
        respx.get(LEVER_URL).mock(return_value=httpx.Response(500))
        result = await DiscoveryService().discover([gh_source(), lever_source()])
        assert len(result.jobs) == 3
        lever_outcome = next(o for o in result.outcomes if o.source_id == "othercorp")
        assert lever_outcome.error is not None
        assert "500" in lever_outcome.error

    async def test_unsupported_source_reports_actionable_error(self):
        custom = CompanySource(id="c", name="Custom", career_url="https://careers.custom.com")
        result = await DiscoveryService().discover([custom])
        assert result.jobs == []
        assert "No supported ATS adapter" in result.outcomes[0].error

    async def test_disabled_sources_are_skipped(self):
        disabled = CompanySource(
            id="d", name="D", career_url="https://boards.greenhouse.io/d", enabled=False
        )
        result = await DiscoveryService().discover([disabled])
        assert result.jobs == []
        assert result.outcomes == []
