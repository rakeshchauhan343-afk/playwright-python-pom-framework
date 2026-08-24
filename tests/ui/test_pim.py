import allure

from pages.pim_page import PimPage
from utils.console_reporter import print_test_step
from utils.logger import get_logger

logger = get_logger(__name__)


@allure.title("Admin can delete an employee from PIM")
@allure.description("Verify an authenticated Admin can delete an employee from the PIM Employee List.")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("PIM")
@allure.story("Employee deletion")
def test_admin_can_delete_employee_from_pim(logged_in_page):
    """Delete the first available employee and verify the deletion."""
    pim_page = PimPage(logged_in_page)

    with allure.step("Step 1 - Login to OrangeHRM"):
        print_test_step(1, "Login")
        logger.info("Login completed through the shared logged_in_page fixture")

    with allure.step("Step 2 - Open PIM"):
        print_test_step(2, "Open PIM")
        logger.info("Opening the PIM menu")
        pim_page.open_pim()

    with allure.step("Step 3 - Verify PIM Employee List"):
        print_test_step(3, "Verify PIM page and Employee List")
        logger.info("Verifying PIM page and Employee List are visible")
        pim_page.expect_employee_list_visible()

    with allure.step("Step 4 - Scroll Employee List"):
        print_test_step(4, "Scroll Employee List")
        logger.info("Scrolling to the employee rows")
        pim_page.scroll_employee_list()

    with allure.step("Step 5 - Click Delete for an employee"):
        print_test_step(5, "Click Delete")
        employee_row = pim_page.first_employee_row()
        logger.info("Deleting the first employee shown in the Employee List")
        pim_page.delete_employee(employee_row)

    with allure.step("Step 6 - Verify delete confirmation"):
        print_test_step(6, "Verify delete confirmation popup")
        logger.info("Verifying the delete confirmation popup")
        pim_page.expect_delete_confirmation_visible()

    with allure.step("Step 7 - Confirm deletion"):
        print_test_step(7, "Click Yes, Delete")
        logger.info("Confirming employee deletion")
        pim_page.confirm_delete()

    with allure.step("Step 8 - Verify employee is deleted"):
        print_test_step(8, "Verify employee is deleted")
        logger.info("Verifying the success notification and removed employee row")
        pim_page.expect_employee_deleted(employee_row)