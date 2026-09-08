import uuid

import allure
import pytest

from api.employee_api_client import EmployeeApiClient
from utils.logger import get_logger

logger = get_logger(__name__)


def unique_employee_data() -> tuple[str, str, str]:
    suffix = uuid.uuid4().hex[:8]
    numeric_employee_id = str(int(suffix, 16))[:8]
    return f"Api{suffix}", "Automation", numeric_employee_id


def cleanup_employee(employee_api: EmployeeApiClient, employee_number: int | None) -> None:
    if employee_number is None:
        return

    with allure.step(f"Clean up employee {employee_number}"):
        logger.info("Deleting employee %s via API cleanup", employee_number)
        response = employee_api.delete_employee(employee_number)
        assert response.status in (200, 204, 404), f"Cleanup delete failed for {employee_number}: {response.text()}"


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee listing")
@allure.title("GET employee list returns the expected payload structure")
@pytest.mark.sanity
@pytest.mark.integration
def test_employee_list_has_expected_response_shape(employee_api: EmployeeApiClient):
    with allure.step("Request employee collection"):
        logger.info("Listing employees with limit=1")
        response = employee_api.list(limit=1)

    with allure.step("Validate response status and schema"):
        employee_api.assert_status(response)
        body = employee_api.assert_json_keys(response, "data", "meta")
        assert isinstance(body["data"], list)
        assert isinstance(body["meta"], dict)


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee creation")
@allure.title("POST create employee returns the created employee record")
@pytest.mark.integration
def test_create_employee_returns_created_record(employee_api: EmployeeApiClient):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None

    try:
        with allure.step(f"Create employee {first_name} {last_name} with employee ID {employee_id}"):
            logger.info("Creating employee: %s %s (%s)", first_name, last_name, employee_id)
            response = employee_api.create(first_name, last_name, employee_id)

        with allure.step("Validate created employee response"):
            employee_api.assert_status(response, 200)
            body = employee_api.assert_employee_response(response)
            created_employee_number = body["data"].get("empNumber")
            assert created_employee_number is not None
            assert body["data"].get("firstName") == first_name
            assert body["data"].get("lastName") == last_name
    finally:
        cleanup_employee(employee_api, int(created_employee_number) if created_employee_number else None)


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee retrieval")
@allure.title("GET employee returns the saved employee details")
@pytest.mark.integration
def test_get_employee_returns_employee_details(employee_api: EmployeeApiClient):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None

    try:
        with allure.step("Create a unique employee for retrieval testing"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_employee_number = employee_api.assert_employee_response(created)["data"].get("empNumber")
            assert created_employee_number is not None

        with allure.step(f"GET employee {created_employee_number}"):
            logger.info("Retrieving employee %s", created_employee_number)
            response = employee_api.get_employee(int(created_employee_number))

        with allure.step("Validate fetched employee data"):
            employee_api.assert_status(response, 200)
            body = employee_api.assert_employee_response(response)
            employee_data = body["data"]
            assert employee_data.get("empNumber") == created_employee_number
            assert employee_data.get("firstName") == first_name
            assert employee_data.get("lastName") == last_name
    finally:
        cleanup_employee(employee_api, int(created_employee_number) if created_employee_number else None)


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee update")
@allure.title("PUT update employee changes the stored values")
@pytest.mark.integration
@pytest.mark.critical
def test_update_employee_updates_details(employee_api: EmployeeApiClient):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None
    updated_first_name = f"Updated{first_name}"
    updated_last_name = f"{last_name}Updated"

    try:
        with allure.step("Create a unique employee for update testing"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_employee_number = employee_api.assert_employee_response(created)["data"].get("empNumber")
            assert created_employee_number is not None

        with allure.step(f"Update employee {created_employee_number} via PUT"):
            logger.info("Updating employee %s to %s %s", created_employee_number, updated_first_name, updated_last_name)
            response = employee_api.update(
                int(created_employee_number),
                firstName=updated_first_name,
                lastName=updated_last_name,
                    employeeId=employee_id,
            )

        with allure.step("Validate the update response"):
            employee_api.assert_status(response, 200)
            body = employee_api.assert_employee_response(response)
            employee_data = body["data"]
            assert employee_data.get("empNumber") == created_employee_number
            assert employee_data.get("firstName") == updated_first_name
            assert employee_data.get("lastName") == updated_last_name
    finally:
        cleanup_employee(employee_api, int(created_employee_number) if created_employee_number else None)


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Employee deletion")
@allure.title("DELETE employee removes the employee record")
@pytest.mark.integration
@pytest.mark.critical
def test_delete_employee_removes_record(employee_api: EmployeeApiClient):
    first_name, last_name, employee_id = unique_employee_data()
    created_employee_number = None

    try:
        with allure.step("Create a unique employee for deletion testing"):
            created = employee_api.create(first_name, last_name, employee_id)
            employee_api.assert_status(created, 200)
            created_employee_number = employee_api.assert_employee_response(created)["data"].get("empNumber")
            assert created_employee_number is not None

        with allure.step(f"DELETE employee {created_employee_number}"):
            logger.info("Deleting employee %s", created_employee_number)
            response = employee_api.delete_employee(int(created_employee_number))

        with allure.step("Validate delete response and follow-up lookup"):
            assert response.status in (200, 204), f"Delete returned unexpected status {response.status}"
            follow_up = employee_api.get_employee(int(created_employee_number))
            assert follow_up.status in (404, 400, 422), (
                f"Delete did not remove employee {created_employee_number}: {follow_up.status} {follow_up.text()}"
            )
    finally:
        cleanup_employee(employee_api, int(created_employee_number) if created_employee_number else None)


@pytest.mark.api
@allure.feature("Employee API")
@allure.story("Negative path")
@allure.title("GET employee with an invalid ID returns a not found response")
@pytest.mark.negative
@pytest.mark.integration
def test_get_employee_with_invalid_id_returns_not_found(employee_api: EmployeeApiClient):
    invalid_employee_id = 999999999

    with allure.step(f"Request employee {invalid_employee_id} that should not exist"):
        logger.info("Querying nonexistent employee ID %s", invalid_employee_id)
        response = employee_api.get_employee(invalid_employee_id)

    with allure.step("Validate negative response"):
        assert response.status in (404, 422), f"Expected not-found response for missing employee, got {response.status}"
        payload = response.json()
        assert payload.get("error") or payload.get("message") or payload.get("data") is None
