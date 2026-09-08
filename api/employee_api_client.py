from typing import Any

from playwright.sync_api import APIResponse

from .base_api_client import BaseApiClient


class EmployeeApiClient(BaseApiClient):
    """OrangeHRM employee API operations used by API and hybrid tests."""

    EMPLOYEES_PATH = "/web/index.php/api/v2/pim/employees"

    def list(self, limit: int = 50, offset: int = 0) -> APIResponse:
        return self.get(self.EMPLOYEES_PATH, params={"limit": limit, "offset": offset})

    def get_employee(self, employee_number: int) -> APIResponse:
        return self.get(f"{self.EMPLOYEES_PATH}/{employee_number}")

    def create(self, first_name: str, last_name: str, employee_id: str) -> APIResponse:
        return self.post(
            self.EMPLOYEES_PATH,
            data={
                "firstName": first_name,
                "lastName": last_name,
                "employeeId": employee_id,
            },
        )

    def update(self, employee_number: int, **fields: Any) -> APIResponse:
        return self.put(f"{self.EMPLOYEES_PATH}/{employee_number}", data=fields)

    def patch_employee(self, employee_number: int, **fields: Any) -> APIResponse:
        return self.patch(f"{self.EMPLOYEES_PATH}/{employee_number}", data=fields)

    def delete_employee(self, employee_number: int) -> APIResponse:
        return self.delete(self.EMPLOYEES_PATH, data={"ids": [employee_number]})

    @staticmethod
    def assert_employee_response(response: APIResponse) -> dict[str, Any]:
        body = BaseApiClient.assert_json_keys(response, "data")
        assert isinstance(body["data"], dict), "Expected employee response data to be an object"
        return body