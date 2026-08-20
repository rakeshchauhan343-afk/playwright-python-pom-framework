import json
import platform
import re
from pathlib import Path
from typing import Any

import pytest
import allure
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from pages.base_page import BasePage
from utils.config_reader import get_base_url, get_timeout
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parent
logger = get_logger(__name__)


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
    allure.dynamic.parameter("Application URL", base_url)
    allure.dynamic.parameter("Playwright tracing", tracing)


def pytest_sessionstart(session: pytest.Session) -> None:
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
                f"Application URL={base_url}",
                f"Playwright tracing={tracing}",
                f"Python={platform.python_version()}",
                f"Operating system={platform.platform()}",
            )
        ),
        encoding="utf-8",
    )


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
        browser_context.tracing.stop(path=str(trace_path))
        logger.info("Saved trace: %s", trace_path)
        _attach_file(trace_path, "Playwright trace", allure.attachment_type.ZIP)
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
        browser_page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info("Saved screenshot: %s", screenshot_path)
        _attach_file(screenshot_path, "Failure screenshot", allure.attachment_type.PNG)
    browser_page.close()


@pytest.fixture
def base_page(page: Page) -> BasePage:
    return BasePage(page)


@pytest.fixture
def user_data() -> dict[str, Any]:
    data_path = PROJECT_ROOT / "test_data" / "users.json"
    with data_path.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]) -> None:
    if call.when == "call":
        setattr(item, "rep_call", pytest.TestReport.from_item_and_call(item, call))


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _attach_file(path: Path, name: str, attachment_type: allure.attachment_type) -> None:
    if path.exists():
        allure.attach.file(str(path), name=name, attachment_type=attachment_type)
