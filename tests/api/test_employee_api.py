import uuid

import allure
import pytest

from api.employee_api_client import EmployeeApiClient


def unique_employee_data() -> tuple[str, str, str]:
    suffix = uuid.uuid4().hex[:8]
    numeric_employee_id = str(int(suffix, 16))[:8]
    return f"Api{suffix}", "Automation", numeric_employee_id


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee lifecycle")
@pytest.mark.sanity
@pytest.mark.integration
def test_employee_list_has_expected_response_shape(employee_api: EmployeeApiClient):
    with allure.step("Request employee collection"):
        response = employee_api.list(limit=1)

    with allure.step("Validate response status and schema"):
        employee_api.assert_status(response)
        body = employee_api.assert_json_keys(response, "data", "meta")
        assert isinstance(body["data"], list)
        assert isinstance(body["meta"], dict)


@pytest.mark.api
@pytest.mark.destructive
@allure.feature("Employee API")
@allure.story("Employee lifecycle")
@pytest.mark.integration
@pytest.mark.critical
def test_employee_can_be_created_and_deleted(employee_api: EmployeeApiClient):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None
    try:
        with allure.step("Create a unique employee through the API"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_body = employee_api.assert_employee_response(created)
            created_employee_number = created_body["data"].get("empNumber")
            assert created_employee_number is not None

        with allure.step("Verify the created employee through the API"):
            employees = employee_api.list(limit=50)
            employee_api.assert_status(employees)
            employee_rows = employee_api.assert_json_keys(employees, "data")["data"]
            assert any(row.get("empNumber") == created_employee_number for row in employee_rows)
    finally:
        if created_employee_number is not None:
            with allure.step("Delete API-created employee data"):
                deleted = employee_api.delete_employee(int(created_employee_number))
                assert deleted.status in (200, 204), deleted.text()