import allure

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.console_reporter import mask_secret, print_test_header, print_test_step


@allure.title("OrangeHRM user can log in")
@allure.description("Verify a valid OrangeHRM user reaches the Dashboard.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Authentication")
@allure.story("OrangeHRM Login")
def test_user_can_log_in_to_orangehrm(page, user_data):
    """Verify a valid OrangeHRM user reaches the Dashboard."""
    print_test_header("OrangeHRM user can log in")
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)
    with allure.step("Step 1 - Open OrangeHRM"):
        login_page.open("/")
        print_test_step(1, f"Open URL: {page.url}")

    credentials = user_data["orangehrm_user"]
    with allure.step("Step 2 - Enter username"):
        print_test_step(2, f"Enter username: {credentials['username']}")
        login_page.enter_username(credentials["username"])
    with allure.step("Step 3 - Enter password"):
        print_test_step(3, f"Enter password: {mask_secret(credentials['password'])}")
        login_page.enter_password(credentials["password"])
    with allure.step("Step 4 - Click Login"):
        print_test_step(4, "Click Login")
        login_page.submit()

    with allure.step("Step 5 - Verify Dashboard"):
        print_test_step(5, "Verify Dashboard is visible")
        dashboard_page.expect_loaded()

    with allure.step("Step 6 - Verify successful login"):
        print_test_step(6, "Verify successful login URL")
        dashboard_page.expect_url()
