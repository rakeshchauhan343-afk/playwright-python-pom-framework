import allure
import pytest
from playwright.sync_api import expect

from pages.dashboard_page import DashboardPage
from pages.my_info_page import MyInfoPage
from utils.console_reporter import print_test_step
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.title("Admin can save My Info Personal Details")
@allure.description("Verify an authenticated Admin can open My Info and save Personal Details.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("My Info")
@allure.story("Personal Details")
@pytest.mark.ui
@pytest.mark.my_info
@pytest.mark.regression
@pytest.mark.e2e
def test_admin_can_save_my_info_personal_details(authenticated_page):
    """Open My Info and verify that Personal Details can be saved."""
    my_info_page = MyInfoPage(authenticated_page)

    with allure.step("Step 1 - Login to OrangeHRM"):
        print_test_step(1, "Login")
        logger.info("Authentication completed through the storage-state fixture")
        DashboardPage(authenticated_page).expect_loaded()

    with allure.step("Step 2 - Open My Info"):
        print_test_step(2, "Open My Info")
        logger.info("Opening the My Info menu")
        my_info_page.open_my_info()

    with allure.step("Step 3 - Verify Personal Details page"):
        print_test_step(3, "Verify Personal Details page")
        my_info_page.expect_personal_details_page()

    with allure.step("Step 4 - Verify Save button"):
        print_test_step(4, "Verify Save button is visible and enabled")
        expect(my_info_page.personal_details_save_button()).to_be_visible()
        expect(my_info_page.personal_details_save_button()).to_be_enabled()

    with allure.step("Step 5 - Click Save"):
        print_test_step(5, "Click Save")
        my_info_page.click_save()

    with allure.step("Step 6 - Verify save success"):
        print_test_step(6, "Verify successful save message")
        my_info_page.expect_save_successful()