import allure
import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.leave_page import LeavePage
from utils.console_reporter import print_test_step
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.title("Admin can search the OrangeHRM Leave List")
@allure.description("Verify an authenticated Admin can open Leave List and perform a search.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Leave")
@allure.story("Leave List search")
@pytest.mark.ui
@pytest.mark.leave
@pytest.mark.regression
@pytest.mark.e2e
def test_admin_can_search_leave_list(authenticated_page):
    """Open Leave List from Dashboard and verify its search action completes."""
    leave_page = LeavePage(authenticated_page)

    with allure.step("Step 1 - Login to OrangeHRM"):
        print_test_step(1, "Login")
        logger.info("Authentication completed through the storage-state fixture")
        DashboardPage(authenticated_page).expect_loaded()

    with allure.step("Step 2 - Open Leave"):
        print_test_step(2, "Open Leave")
        leave_page.open_leave()

    with allure.step("Step 3 - Verify Leave page"):
        print_test_step(3, "Verify Leave page")
        expect(authenticated_page.get_by_role("heading", name="Leave", exact=True)).to_be_visible()

    with allure.step("Step 4 - Open Leave List"):
        print_test_step(4, "Click Leave List")
        leave_page.open_leave_list()

    with allure.step("Step 5 - Verify Leave List page"):
        print_test_step(5, "Verify Leave List page")
        expect(authenticated_page).to_have_url(leave_page.LEAVE_LIST_URL)

    with allure.step("Step 6 - Search Leave List"):
        print_test_step(6, "Click Search")
        leave_page.click_search()

    with allure.step("Step 7 - Verify search completed"):
        print_test_step(7, "Verify search results are displayed")
        leave_page.expect_search_completed()