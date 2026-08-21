import allure

from pages.admin_page import AdminPage
from pages.dashboard_page import DashboardPage


@allure.title("Admin can search for a system user and open Add User")
@allure.description("Verify an Admin user can search System User records and open the Add User form.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("User Management")
@allure.story("Admin System User Search")
def test_admin_user_search_and_open_add_user(logged_in_page, user_data):
    """Search for the configured System User and open the Add User form."""
    admin_page = AdminPage(logged_in_page)
    search_data = user_data["admin_search"]

    with allure.step("Step 1 - Login to OrangeHRM"):
        DashboardPage(logged_in_page).expect_loaded()

    with allure.step("Step 2 - Open Admin"):
        admin_page.open_admin()

    with allure.step("Step 3 - Search System User"):
        admin_page.enter_username(search_data["username"])
        admin_page.select_user_role(search_data["user_role"])
        admin_page.enter_employee_name(search_data["employee_name"])
        admin_page.select_status(search_data["status"])
        admin_page.click_search()

    with allure.step("Step 4 - Verify Search Result"):
        admin_page.verify_search_result(search_data["username"])

    with allure.step("Step 5 - Click Add User"):
        admin_page.click_add()

    with allure.step("Step 6 - Verify Add User Page"):
        admin_page.verify_add_user_page()