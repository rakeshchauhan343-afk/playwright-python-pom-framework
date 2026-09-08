import allure
import pytest

from api.employee_api_client import EmployeeApiClient
from pages.pim_page import PimPage
from tests.api.test_employee_api import unique_employee_data


@pytest.mark.hybrid
@pytest.mark.destructive
@allure.feature("Employee API and UI")
@allure.story("API setup and UI verification")
@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.pim
def test_api_created_employee_is_visible_in_pim(employee_api: EmployeeApiClient, authenticated_page):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None
    try:
        with allure.step("Create employee through the API"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_employee_number = employee_api.assert_employee_response(created)["data"]["empNumber"]

        with allure.step("Open PIM and search for the API-created employee"):
            pim_page = PimPage(authenticated_page)
            pim_page.open_pim()
            pim_page.expect_employee_list_visible()
            pim_page.search_employee(first_name)
            pim_page.expect_employee_visible(first_name)
    finally:
        if created_employee_number is not None:
            with allure.step("Clean up API-created employee"):
                deleted = employee_api.delete_employee(int(created_employee_number))
                assert deleted.status in (200, 204), deleted.text()


@pytest.mark.hybrid
@pytest.mark.destructive
@allure.feature("Employee API and UI")
@allure.story("UI update and API verification")
@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.critical
@pytest.mark.pim
def test_ui_employee_update_is_verified_by_api(employee_api: EmployeeApiClient, authenticated_page):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None
    try:
        with allure.step("Create employee through the API"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_employee_number = employee_api.assert_employee_response(created)["data"]["empNumber"]

        with allure.step("Update employee through the PIM UI"):
            pim_page = PimPage(authenticated_page)
            pim_page.open_pim()
            pim_page.expect_employee_list_visible()
            pim_page.search_employee(first_name)
            row = pim_page.employee_rows.filter(has_text=first_name).first
            pim_page.edit_employee(row)
            edit_form = authenticated_page.locator(".oxd-input-group").filter(has_text="First Name").first
            if edit_form.count() == 0 or not edit_form.is_visible():
                pytest.skip("Configured account cannot edit employee details in the demo environment")
            pim_page.update_first_name(f"UiUpdated{first_name}")

        with allure.step("Verify the UI update through the API"):
            employees = employee_api.list(limit=50)
            employee_api.assert_status(employees)
            rows = employee_api.assert_json_keys(employees, "data")["data"]
            assert any(
                row.get("empNumber") == created_employee_number
                and row.get("firstName") == f"UiUpdated{first_name}"
                for row in rows
            )
    finally:
        if created_employee_number is not None:
            with allure.step("Clean up API-created employee"):
                deleted = employee_api.delete_employee(int(created_employee_number))
                assert deleted.status in (200, 204), deleted.text()