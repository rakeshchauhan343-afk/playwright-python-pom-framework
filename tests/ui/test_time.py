import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.time_page import TimePage
from utils.console_reporter import print_test_step
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.title("Admin can open the employee timesheet")
@allure.description("Verify an authenticated Admin can open Time and view the employee timesheet.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Time")
@allure.story("Employee timesheet")
@pytest.mark.ui
@pytest.mark.time
@pytest.mark.regression
@pytest.mark.e2e
def test_admin_can_open_employee_timesheet(authenticated_page):
    """Open Time and verify that the employee Timesheet page is displayed."""
    time_page = TimePage(authenticated_page)

    with allure.step("Step 1 - Login to OrangeHRM"):
        print_test_step(1, "Login")
        logger.info("Authentication completed through the storage-state fixture")
        DashboardPage(authenticated_page).expect_loaded()

    with allure.step("Step 2 - Open Time"):
        print_test_step(2, "Open Time")
        logger.info("Opening the Time menu")
        time_page.open_time()

    with allure.step("Step 3 - Verify Time page"):
        print_test_step(3, "Verify Time page")
        time_page.expect_time_page()

    with allure.step("Step 4 - Click View"):
        print_test_step(4, "Click View")
        time_page.click_view()

    with allure.step("Step 5 - Verify Timesheet page"):
        print_test_step(5, "Verify Timesheet page")
        time_page.expect_timesheet_page()