import json
import platform
import re
import time
from pathlib import Path
from typing import Any

import pytest
import allure
from pytest_metadata.plugin import metadata_key
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright
from pytest_html import extras

from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from config.settings import ORANGEHRM_PASSWORD, ORANGEHRM_URL, ORANGEHRM_USERNAME
from utils.config_reader import get_base_url, get_timeout
from utils.console_reporter import print_test_result
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parent
logger = get_logger(__name__)
SESSION_START: float | None = None
REPORT_COUNTS = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("playwright")
    group.addoption(
        "--pom-browser",
        action="store",
        default="chromium",
        choices=("chromium", "firefox", "webkit"),
        help="Browser engine to use.",
    )
    group.addoption(
        "--pom-headed",
        action="store_true",
        default=False,
        help="Run the selected browser with a visible window.",
    )
    group.addoption(
        "--pom-base-url",
        action="store",
        default=None,
        help="Override the configured application base URL.",
    )
    group.addoption(
        "--pom-tracing",
        action="store",
        default="on",
        choices=("on", "off"),
        help="Capture Playwright traces for failed tests.",
    )


@pytest.fixture(autouse=True)
def allure_test_metadata(request: pytest.FixtureRequest) -> None:
    browser_name = request.config.getoption("--pom-browser")
    headed = request.config.getoption("--pom-headed") or request.config.getoption(
        "--headed", default=False
    )
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    tracing = request.config.getoption("--pom-tracing")

    allure.dynamic.parameter("Browser", browser_name)
    allure.dynamic.parameter("Execution mode", "headed" if headed else "headless")
    allure.dynamic.parameter("Application URL", _safe_url(base_url))
    allure.dynamic.parameter("Playwright tracing", tracing)


def pytest_sessionstart(session: pytest.Session) -> None:
    global SESSION_START
    SESSION_START = time.perf_counter()
    results_dir = session.config.getoption("--alluredir", default=None)
    if not results_dir:
        return

    environment_path = Path(results_dir) / "environment.properties"
    environment_path.parent.mkdir(parents=True, exist_ok=True)
    browser_name = session.config.getoption("--pom-browser")
    headed = session.config.getoption("--pom-headed") or session.config.getoption(
        "--headed", default=False
    )
    base_url = session.config.getoption("--pom-base-url") or get_base_url()
    tracing = session.config.getoption("--pom-tracing")
    environment_path.write_text(
        "\n".join(
            (
                f"Browser={browser_name}",
                f"Execution mode={'headed' if headed else 'headless'}",
                f"Application URL={_safe_url(base_url)}",
                f"Playwright tracing={tracing}",
                f"Python={platform.python_version()}",
                f"Operating system={platform.platform()}",
            )
        ),
        encoding="utf-8",
    )


def pytest_configure(config: pytest.Config) -> None:
    browser_name = config.getoption("--pom-browser")
    headed = config.getoption("--pom-headed") or config.getoption(
        "--headed", default=False
    )
    base_url = config.getoption("--pom-base-url") or get_base_url()
    tracing = config.getoption("--pom-tracing")
    metadata = config.stash.get(metadata_key, None)
    if metadata is not None:
        metadata.update(
            {
                "Browser": browser_name,
                "Execution mode": "headed" if headed else "headless",
                "Application URL": _safe_url(base_url),
                "Playwright tracing": tracing,
                "Python": platform.python_version(),
                "Operating system": platform.platform(),
            }
        )


def pytest_html_results_summary(
    prefix: list[Any], summary: list[Any], postfix: list[Any]
) -> None:
    passed = REPORT_COUNTS["passed"]
    failed = REPORT_COUNTS["failed"]
    skipped = REPORT_COUNTS["skipped"]
    errors = REPORT_COUNTS["errors"]
    total = passed + failed + skipped + errors
    summary.append(
        f"<p><strong>Framework summary:</strong> {total} total, {passed} passed, "
        f"{failed} failed, {skipped} skipped, {errors} errors.</p>"
    )


def pytest_html_results_table_row(report: pytest.TestReport, cells: list[Any]) -> None:
    for path, label, artifact_type in getattr(report, "report_artifacts", []):
        if path.exists():
            if artifact_type == "image":
                report.extras.append(extras.image(str(path), name=label))
            else:
                report.extras.append(extras.url(path.as_uri(), name=label))


def pytest_terminal_summary(
    terminalreporter: Any,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    duration = time.perf_counter() - SESSION_START if SESSION_START else 0.0
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    skipped = len(terminalreporter.stats.get("skipped", []))
    errors = len(terminalreporter.stats.get("error", []))
    total = passed + failed + skipped + errors
    terminalreporter.write_sep("=", "EXECUTION SUMMARY")
    terminalreporter.write_line(f"Total: {total}")
    terminalreporter.write_line(f"Passed: {passed}")
    terminalreporter.write_line(f"Failed: {failed}")
    terminalreporter.write_line(f"Skipped: {skipped}")
    terminalreporter.write_line(f"Errors: {errors}")
    terminalreporter.write_line(f"Duration: {duration:.2f}s")


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(request: pytest.FixtureRequest, playwright_instance: Playwright) -> Browser:
    browser_name = request.config.getoption("--pom-browser")
    browser_type = getattr(playwright_instance, browser_name)
    headed = request.config.getoption("--pom-headed") or request.config.getoption(
        "--headed", default=False
    )
    logger.info("Launching %s (headless=%s)", browser_name, not headed)
    instance = browser_type.launch(headless=not headed)
    yield instance
    instance.close()


@pytest.fixture
def context(request: pytest.FixtureRequest, browser: Browser) -> BrowserContext:
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    (PROJECT_ROOT / "traces").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "reports").mkdir(parents=True, exist_ok=True)
    browser_context = browser.new_context(base_url=base_url)
    browser_context.set_default_timeout(get_timeout())
    tracing_enabled = request.config.getoption("--pom-tracing") == "on"
    if tracing_enabled:
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield browser_context

    report = getattr(request.node, "rep_call", None)
    if tracing_enabled and report and report.failed:
        trace_path = PROJECT_ROOT / "traces" / f"{_safe_name(request.node.nodeid)}.zip"
        try:
            browser_context.tracing.stop(path=str(trace_path))
            logger.info("Saved trace: %s", trace_path)
            _attach_file(trace_path, "Playwright trace", allure.attachment_type.ZIP)
            _record_artifact(report, trace_path, "Playwright trace", "trace")
        except Exception as error:
            logger.warning("Could not save Playwright trace: %s", error)
    elif tracing_enabled:
        browser_context.tracing.stop()
    if report and report.failed:
        _attach_file(PROJECT_ROOT / "reports" / "framework.log", "Framework log", allure.attachment_type.TEXT)
    browser_context.close()


@pytest.fixture
def page(request: pytest.FixtureRequest, context: BrowserContext) -> Page:
    browser_page = context.new_page()
    yield browser_page

    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        (PROJECT_ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
        screenshot_path = PROJECT_ROOT / "screenshots" / f"{_safe_name(request.node.nodeid)}.png"
        try:
            browser_page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info("Saved screenshot: %s", screenshot_path)
            _attach_file(screenshot_path, "Failure screenshot", allure.attachment_type.PNG)
            _record_artifact(report, screenshot_path, "Failure screenshot", "image")
        except Exception as error:
            logger.warning("Could not save failure screenshot: %s", error)
    browser_page.close()


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)
    with allure.step("Open OrangeHRM and log in"):
        login_page.open(ORANGEHRM_URL)
        login_page.login(ORANGEHRM_USERNAME, ORANGEHRM_PASSWORD)
        dashboard_page.expect_loaded()
    return page


@pytest.fixture
def base_page(page: Page) -> BasePage:
    return BasePage(page)


@pytest.fixture
def user_data() -> dict[str, Any]:
    data_path = PROJECT_ROOT / "test_data" / "users.json"
    with data_path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    report = pytest.TestReport.from_item_and_call(item, call)
    setattr(item, f"rep_{call.when}", report)
    if call.when == "call":
        setattr(item, "rep_call", report)
        print_test_result(item.name, report.passed)
        if report.passed:
            REPORT_COUNTS["passed"] += 1
        elif report.skipped:
            REPORT_COUNTS["skipped"] += 1
        else:
            REPORT_COUNTS["failed"] += 1


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _safe_url(value: str) -> str:
    return re.sub(
        r"([?&](?:token|password|secret|key)=[^&]*)",
        r"\1=***",
        value,
        flags=re.IGNORECASE,
    )


def _record_artifact(
    report: pytest.TestReport,
    path: Path,
    label: str,
    artifact_type: str,
) -> None:
    artifacts = getattr(report, "report_artifacts", [])
    artifacts.append((path, label, artifact_type))
    report.report_artifacts = artifacts


def _attach_file(path: Path, name: str, attachment_type: allure.attachment_type) -> None:
    if path.exists():
        allure.attach.file(str(path), name=name, attachment_type=attachment_type)
