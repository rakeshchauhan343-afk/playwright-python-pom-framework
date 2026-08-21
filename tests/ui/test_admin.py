import allure

from pages.admin_page import AdminPage
from pages.dashboard_page import DashboardPage
from utils.console_reporter import print_test_step


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
        print_test_step(1, "Login")
        DashboardPage(logged_in_page).expect_loaded()

    with allure.step("Step 2 - Open Admin"):
        print_test_step(2, "Open Admin")
        admin_page.open_admin()

    with allure.step("Step 3 - Enter Username"):
        print_test_step(3, "Enter Username")
        admin_page.enter_username(search_data["username"])

    with allure.step("Step 4 - Select User Role"):
        print_test_step(4, "Select User Role")
        admin_page.select_user_role(search_data["user_role"])

    with allure.step("Step 5 - Enter Employee Name"):
        print_test_step(5, "Enter Employee Name")
        admin_page.enter_employee_name(search_data["employee_name"])

    with allure.step("Step 6 - Select Status"):
        print_test_step(6, "Select Status")
        admin_page.select_status(search_data["status"])

    with allure.step("Step 7 - Click Search"):
        print_test_step(7, "Click Search")
        admin_page.click_search()
        admin_page.verify_search_result(search_data["username"])

    with allure.step("Step 8 - Click Add"):
        print_test_step(8, "Click Add")
        admin_page.click_add()

    with allure.step("Step 9 - Verify Add User Page"):
        print_test_step(9, "Verify Add User Page")
        admin_page.verify_add_user_page()
