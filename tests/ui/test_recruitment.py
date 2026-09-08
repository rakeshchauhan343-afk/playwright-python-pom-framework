import allure
import pytest

from pages.dashboard_page import DashboardPage
from pages.recruitment_page import RecruitmentPage
from utils.console_reporter import print_test_step
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.title("Admin can open Add Candidate from Recruitment")
@allure.description(
    "Verify an authenticated Admin can open Recruitment and display the Add Candidate form."
)
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Recruitment")
@allure.story("Add Candidate navigation")
@pytest.mark.ui
@pytest.mark.recruitment
@pytest.mark.regression
@pytest.mark.e2e
def test_admin_can_open_add_candidate_from_recruitment(authenticated_page):
    """Open Recruitment and verify the Add Candidate form is displayed."""
    recruitment_page = RecruitmentPage(authenticated_page)

    with allure.step("Step 1 - Login to OrangeHRM"):
        print_test_step(1, "Login")
        logger.info("Authentication completed through the storage-state fixture")
        DashboardPage(authenticated_page).expect_loaded()

    with allure.step("Step 2 - Open Recruitment"):
        print_test_step(2, "Open Recruitment")
        logger.info("Opening the Recruitment menu")
        recruitment_page.open_recruitment()

    with allure.step("Step 3 - Verify Recruitment and Candidates"):
        print_test_step(3, "Verify Recruitment page and Candidates tab")
        recruitment_page.expect_candidates_page()

    with allure.step("Step 4 - Click Add"):
        print_test_step(4, "Click Add")
        recruitment_page.click_add()

    with allure.step("Step 5 - Verify Add Candidate page"):
        print_test_step(5, "Verify Add Candidate page")
        recruitment_page.expect_add_candidate_page()