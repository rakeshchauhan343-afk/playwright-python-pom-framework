import html
import json
import os
import platform
import re
import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any, Generator

import pytest
import allure
from pytest_metadata.plugin import metadata_key
from playwright.sync_api import (
    APIRequestContext,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)
from pytest_html import extras

from pages.base_page import BasePage
from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from config.settings import ORANGEHRM_PASSWORD, ORANGEHRM_USERNAME
from utils.config_reader import get_base_url, get_environment_name, get_timeout
from utils.console_reporter import print_test_result
from utils.logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parent
playwright_version = version("playwright")
environment_name = get_environment_name()
logger = get_logger(__name__)
SESSION_START: float | None = None
REPORT_COUNTS = {"passed": 0, "failed": 0, "skipped": 0, "errors": 0}
COUNTED_NODEIDS: set[str] = set()
DEFAULT_REPORT_STEPS = {
    "test_user_can_log_in_to_orangehrm": (
        "Step 1 - Open OrangeHRM",
        "Step 2 - Enter Username",
        "Step 3 - Enter Password",
        "Step 4 - Click Login",
        "Step 5 - Verify Dashboard",
    ),
    "test_admin_user_search_and_open_add_user": (
        "Step 1 - Login",
        "Step 2 - Open Admin",
        "Step 3 - Enter Username",
        "Step 4 - Select User Role",
        "Step 5 - Enter Employee Name",
        "Step 6 - Select Status",
        "Step 7 - Click Search",
        "Step 8 - Click Add",
        "Step 9 - Verify Add User Page",
    ),
}


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
    group.addoption(
        "--pom-video",
        action="store",
        default="off",
        choices=("on", "off"),
        help="Record videos and retain them for failed tests.",
    )
    group.addoption(
        "--pom-refresh-auth",
        action="store_true",
        default=False,
        help="Regenerate auth/storage_state.json before authenticated tests.",
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
    COUNTED_NODEIDS.clear()
    for key in REPORT_COUNTS:
        REPORT_COUNTS[key] = 0
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
                "Pytest": pytest.__version__,
                "Playwright": playwright_version,
                "Operating system": platform.platform(),
                "Environment": environment_name,
            }
        )


def pytest_html_report_title(report: Any) -> None:
    report.title = "Playwright Python Automation Test Report"


def pytest_html_results_summary(
    prefix: list[Any], summary: list[Any], postfix: list[Any]
) -> None:
    prefix.append(
        "<style>"
        ".qa-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));"
        "gap:10px;margin:18px 0}.qa-summary div{background:#f4f7fa;border-left:4px solid #64748b;"
        "padding:12px 14px;border-radius:4px}.qa-summary strong,.qa-summary span{display:block}."
        "qa-summary span{font-size:1.45em;font-weight:700;margin-top:4px}.qa-summary .passed{border-color:#16803c}."
        ".qa-summary .failed{border-color:#c62828}.qa-summary .skipped{border-color:#b7791f}."
        ".qa-summary .error{border-color:#7c3aed}.qa-steps{white-space:pre-line;min-width:260px}."
        ".qa-failure{margin-top:12px;padding:12px;border:1px solid #c62828;background:#fff7f7}."
        ".qa-failure pre{white-space:pre-wrap;overflow:auto;margin-bottom:0}"
        "</style>"
    )
    passed = REPORT_COUNTS["passed"]
    failed = REPORT_COUNTS["failed"]
    skipped = REPORT_COUNTS["skipped"]
    errors = REPORT_COUNTS["errors"]
    total = passed + failed + skipped + errors
    pass_percentage = (passed / total * 100) if total else 0
    duration = time.perf_counter() - SESSION_START if SESSION_START else 0.0
    summary.append(
        '<section class="qa-summary">'
        f'<div><strong>Total Tests</strong><span>{total}</span></div>'
        f'<div class="passed"><strong>Passed</strong><span>{passed}</span></div>'
        f'<div class="failed"><strong>Failed</strong><span>{failed}</span></div>'
        f'<div class="skipped"><strong>Skipped</strong><span>{skipped}</span></div>'
        f'<div class="error"><strong>Error</strong><span>{errors}</span></div>'
        f'<div><strong>Total Execution Time</strong><span>{duration:.2f}s</span></div>'
        f'<div><strong>Pass Percentage</strong><span>{pass_percentage:.1f}%</span></div>'
        "</section>"
    )


def pytest_html_results_table_header(cells: list[Any]) -> None:
    cells.insert(1, "<th class='sortable'>Test Status</th>")
    cells.insert(2, "<th class='sortable'>Test Module</th>")
    cells.insert(3, "<th class='sortable'>Browser</th>")
    cells.insert(4, "<th class='sortable'>Environment</th>")
    cells.insert(5, "<th>Execution Date/Time</th>")
    cells.insert(6, "<th>Test Steps</th>")


def pytest_html_results_table_html(report: pytest.TestReport, data: list[str]) -> None:
    if report.failed:
        data.append(
            "<div class='qa-failure'>"
            f"<strong>Failure details</strong><pre>{html.escape(report.longreprtext)}</pre>"
            "</div>"
        )


def pytest_html_results_table_row(report: pytest.TestReport, cells: list[Any]) -> None:
    test_module = Path(str(report.fspath)).name if report.fspath else ""
    browser_name = getattr(report, "browser_name", "")
    environment = getattr(report, "environment_name", environment_name)
    execution_time = getattr(report, "execution_datetime", "")
    steps = getattr(report, "report_steps", "")
    cells.insert(1, f"<td>{html.escape(report.outcome.title())}</td>")
    cells.insert(2, f"<td>{html.escape(test_module)}</td>")
    cells.insert(3, f"<td>{html.escape(browser_name)}</td>")
    cells.insert(4, f"<td>{html.escape(environment)}</td>")
    cells.insert(5, f"<td>{html.escape(execution_time)}</td>")
    cells.insert(6, f"<td class='qa-steps'>{steps or 'No captured steps'}</td>")
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


@pytest.fixture(scope="session")
def auth_state(request: pytest.FixtureRequest, browser: Browser) -> Path:
    """Reuse a valid state or create the canonical authenticated state."""
    state_path = PROJECT_ROOT / "auth" / "storage_state.json"
    base_url = request.config.getoption("--pom-base-url") or get_base_url()

    refresh_requested = request.config.getoption("--pom-refresh-auth")
    if not refresh_requested and _auth_state_is_valid(browser, base_url, state_path):
        logger.info("Reusing authenticated browser state: %s", state_path)
        return state_path

    _create_auth_state(browser, base_url, state_path)
    return state_path


@pytest.fixture
def api_request_context(request: pytest.FixtureRequest, playwright_instance: Playwright) -> Generator[APIRequestContext, None, None]:
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    request_context = playwright_instance.request.new_context(base_url=base_url)
    yield request_context
    request_context.dispose()


@pytest.fixture
def authenticated_api_request_context(
    request: pytest.FixtureRequest,
    playwright_instance: Playwright,
    auth_state: Path,
) -> Generator[APIRequestContext, None, None]:
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    request_context = playwright_instance.request.new_context(
        base_url=base_url,
        storage_state=str(auth_state),
        extra_http_headers={"Accept": "application/json"},
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def employee_api(authenticated_api_request_context: APIRequestContext):
    from api.employee_api_client import EmployeeApiClient

    return EmployeeApiClient(authenticated_api_request_context)


@pytest.fixture
def authenticated_page(
    request: pytest.FixtureRequest,
    browser: Browser,
    auth_state: Path,
) -> Generator[Page, None, None]:
    """Provide a fresh page backed by the generated authenticated state."""
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    authenticated_context = browser.new_context(
        base_url=base_url,
        storage_state=str(auth_state),
    )
    authenticated_context.set_default_timeout(get_timeout())
    authenticated_browser_page = authenticated_context.new_page()
    authenticated_browser_page.goto(base_url, wait_until="domcontentloaded")
    DashboardPage(authenticated_browser_page).expect_loaded()
    yield authenticated_browser_page
    authenticated_browser_page.close()
    authenticated_context.close()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def dashboard_page(page: Page) -> DashboardPage:
    return DashboardPage(page)


@pytest.fixture
def pim_page(page: Page):
    from pages.pim_page import PimPage

    return PimPage(page)


@pytest.fixture
def mock_route(page: Page):
    """Register a route that can fulfill, delay, continue, or abort requests."""
    registered_patterns: list[str] = []

    def register(
        url_pattern: str,
        *,
        status: int = 200,
        body: Any = None,
        headers: dict[str, str] | None = None,
        delay_ms: int = 0,
        action: str = "fulfill",
    ) -> None:
        if action not in {"fulfill", "continue", "abort"}:
            raise ValueError("action must be fulfill, continue, or abort")

        def handler(route) -> None:
            if action == "continue":
                route.continue_()
            elif action == "abort":
                route.abort()
            else:
                if delay_ms:
                    page.wait_for_timeout(delay_ms)
                fulfill_kwargs: dict[str, Any] = {
                    "status": status,
                    "headers": headers or {"content-type": "application/json"},
                }
                if body is not None:
                    fulfill_kwargs["json"] = body
                route.fulfill(**fulfill_kwargs)

        page.route(url_pattern, handler)
        registered_patterns.append(url_pattern)

    yield register
    for pattern in registered_patterns:
        page.unroute(pattern)
@pytest.fixture
def context(request: pytest.FixtureRequest, browser: Browser) -> BrowserContext:
    base_url = request.config.getoption("--pom-base-url") or get_base_url()
    (PROJECT_ROOT / "traces").mkdir(parents=True, exist_ok=True)
    (PROJECT_ROOT / "reports").mkdir(parents=True, exist_ok=True)
    video_enabled = request.config.getoption("--pom-video") == "on"
    video_dir = PROJECT_ROOT / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    video_files_before = set(video_dir.glob("*.webm"))
    browser_context = browser.new_context(
        base_url=base_url,
        record_video_dir=str(video_dir) if video_enabled else None,
    )
    browser_context.set_default_timeout(get_timeout())
    tracing_enabled = request.config.getoption("--pom-tracing") == "on"
    if tracing_enabled:
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield browser_context

    report = getattr(request.node, "rep_call", None)
    if tracing_enabled and report and report.failed:
        trace_path = PROJECT_ROOT / "traces" / f"{_safe_name(request.node.nodeid)}.zip"
        if not getattr(request.node, "trace_saved", False):
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
    if report and report.failed and video_enabled:
        for video_path in video_dir.glob("*.webm"):
            if video_path not in video_files_before:
                _attach_file(video_path, "Failure video", allure.attachment_type.WEBM)
                _record_artifact(report, video_path, "Failure video", "video")


@pytest.fixture
def page(request: pytest.FixtureRequest, context: BrowserContext) -> Page:
    browser_page = context.new_page()
    console_messages: list[str] = []
    failed_requests: list[str] = []
    browser_page.on(
        "console",
        lambda message: console_messages.append(f"[{message.type}] {message.text}"),
    )
    browser_page.on(
        "requestfailed",
        lambda failed_request: failed_requests.append(
            f"{failed_request.method} {failed_request.url}"
            f" - {failed_request.failure or 'unknown failure'}"
        ),
    )
    yield browser_page

    report = getattr(request.node, "rep_call", None)
    if report and report.failed and not getattr(request.node, "screenshot_saved", False):
        (PROJECT_ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
        screenshot_path = PROJECT_ROOT / "screenshots" / f"{_safe_name(request.node.nodeid)}.png"
        try:
            browser_page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info("Saved screenshot: %s", screenshot_path)
            _attach_file(screenshot_path, "Failure screenshot", allure.attachment_type.PNG)
            _record_artifact(report, screenshot_path, "Failure screenshot", "image")
        except Exception as error:
            logger.warning("Could not save failure screenshot: %s", error)
    if report and report.failed and (console_messages or failed_requests):
        diagnostics_path = PROJECT_ROOT / "reports" / "diagnostics" / (
            f"{_safe_name(request.node.nodeid)}.txt"
        )
        diagnostics_path.parent.mkdir(parents=True, exist_ok=True)
        diagnostics_path.write_text(
            "Console messages:\n"
            + ("\n".join(console_messages) or "None")
            + "\n\nFailed requests:\n"
            + ("\n".join(failed_requests) or "None")
            + "\n",
            encoding="utf-8",
        )
        _attach_file(diagnostics_path, "Console and network diagnostics", allure.attachment_type.TEXT)
        _record_artifact(report, diagnostics_path, "Console and network diagnostics", "text")
    browser_page.close()


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)
    with allure.step("Open OrangeHRM and log in"):
        login_page.open(get_base_url())
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[Any]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{call.when}", report)
    if call.when == "call":
        report.browser_name = item.config.getoption("--pom-browser")
        report.environment_name = environment_name
        report.execution_datetime = datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )
        report.report_steps = _steps_html(getattr(report, "capstdout", ""))
        if not report.report_steps:
            report.report_steps = "<br>".join(
                html.escape(step)
                for step in DEFAULT_REPORT_STEPS.get(item.name, ())
            )
        captured_output = getattr(report, "capstdout", "")
        report.extras = getattr(report, "extras", [])
        if captured_output:
            report.extras.append(extras.text(captured_output, name="Test steps and logs"))
        framework_log = PROJECT_ROOT / "reports" / "framework.log"
        if framework_log.exists():
            report.extras.append(
                extras.text(framework_log.read_text(encoding="utf-8"), name="Framework log")
            )
        if item.nodeid not in COUNTED_NODEIDS:
            _count_report(report)
            COUNTED_NODEIDS.add(item.nodeid)
        if report.failed:
            _capture_failure_artifacts(item, report)
    elif report.failed and item.nodeid not in COUNTED_NODEIDS:
        REPORT_COUNTS["errors"] += 1
        COUNTED_NODEIDS.add(item.nodeid)
    elif report.skipped and item.nodeid not in COUNTED_NODEIDS:
        REPORT_COUNTS["skipped"] += 1
        COUNTED_NODEIDS.add(item.nodeid)
    if call.when == "call":
        setattr(item, "rep_call", report)
        print_test_result(item.name, report.passed)


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def _auth_state_is_valid(browser: Browser, base_url: str, state_path: Path) -> bool:
    if not state_path.is_file():
        return False

    validation_context = None
    try:
        validation_context = browser.new_context(
            base_url=base_url,
            storage_state=str(state_path),
        )
        validation_context.set_default_timeout(get_timeout())
        validation_page = validation_context.new_page()
        validation_page.goto(base_url, wait_until="domcontentloaded")
        DashboardPage(validation_page).expect_loaded()
        return True
    except Exception as error:
        logger.info("Stored authentication is unavailable and will be refreshed: %s", error)
        return False
    finally:
        if validation_context is not None:
            validation_context.close()


def _create_auth_state(browser: Browser, base_url: str, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = state_path.with_name(f"{state_path.stem}.{os.getpid()}.tmp.json")
    auth_context = browser.new_context(base_url=base_url)
    auth_context.set_default_timeout(get_timeout())
    try:
        auth_page = auth_context.new_page()
        with allure.step("Generate authenticated Playwright storage state"):
            LoginPage(auth_page).open(base_url)
            LoginPage(auth_page).login(ORANGEHRM_USERNAME, ORANGEHRM_PASSWORD)
            DashboardPage(auth_page).expect_loaded()
            auth_context.storage_state(path=str(temporary_path))
        os.replace(temporary_path, state_path)
        logger.info("Saved authenticated browser state: %s", state_path)
    finally:
        auth_context.close()
        temporary_path.unlink(missing_ok=True)


def _steps_html(output: str) -> str:
    steps = []
    for line in output.splitlines():
        match = re.match(r"\s*\[STEP\s+(\d+)\]\s+(.+)", line)
        if match:
            steps.append(f"Step {match.group(1)} - {html.escape(match.group(2))}")
    return "<br>".join(steps)


def _count_report(report: pytest.TestReport) -> None:
    if report.passed:
        REPORT_COUNTS["passed"] += 1
    elif report.skipped:
        REPORT_COUNTS["skipped"] += 1
    elif report.failed:
        REPORT_COUNTS["failed"] += 1


def _capture_failure_artifacts(item: pytest.Item, report: pytest.TestReport) -> None:
    page = item.funcargs.get("page")
    if page is not None:
        screenshot_path = PROJECT_ROOT / "screenshots" / f"{_safe_name(item.nodeid)}.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            _attach_file(screenshot_path, "Failure screenshot", allure.attachment_type.PNG)
            _record_artifact(report, screenshot_path, "Failure screenshot", "image")
            item.screenshot_saved = True
        except Exception as error:
            logger.warning("Could not save failure screenshot: %s", error)

    context = item.funcargs.get("context")
    if context is not None and item.config.getoption("--pom-tracing") == "on":
        trace_path = PROJECT_ROOT / "traces" / f"{_safe_name(item.nodeid)}.zip"
        try:
            context.tracing.stop(path=str(trace_path))
            _attach_file(trace_path, "Playwright trace", allure.attachment_type.ZIP)
            _record_artifact(report, trace_path, "Playwright trace", "trace")
            item.trace_saved = True
        except Exception as error:
            logger.warning("Could not save Playwright trace: %s", error)


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
