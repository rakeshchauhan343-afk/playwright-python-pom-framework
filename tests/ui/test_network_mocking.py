import allure
import pytest
from playwright.sync_api import expect

from pages.base_page import BasePage


@pytest.mark.ui
@allure.feature("Network diagnostics")
@allure.story("Response mocking")
@pytest.mark.parametrize("status", [400, 500])
@pytest.mark.negative
@pytest.mark.integration
def test_mocked_api_failure_response(page, mock_route, status):
    mock_route("**/mock-api/failure", status=status, body={"error": "simulated"})
    page.goto("about:blank")

    response = BasePage(page).wait_for_response(
        "**/mock-api/failure",
        lambda: page.evaluate(
            """async () => {
                const response = await fetch('https://mock-api.test/mock-api/failure');
                return response.status;
            }"""
        ),
    )

    assert response.status == status
    assert response.json() == {"error": "simulated"}


@pytest.mark.ui
@allure.feature("Network diagnostics")
@allure.story("Network controls")
@pytest.mark.negative
@pytest.mark.integration
def test_slow_mocked_response_is_observable(page, mock_route):
    mock_route("**/mock-api/slow", body={"ok": True}, delay_ms=100)
    page.goto("about:blank")

    response = BasePage(page).wait_for_response(
        "**/mock-api/slow",
        lambda: page.evaluate(
            "fetch('https://mock-api.test/mock-api/slow').then(response => response.json())"
        ),
    )

    assert response.json() == {"ok": True}


@pytest.mark.ui
@allure.feature("Network diagnostics")
@allure.story("Request abort")
@pytest.mark.negative
@pytest.mark.integration
def test_aborted_request_is_reported_to_the_page(page, mock_route):
    mock_route("**/mock-api/aborted", action="abort")
    page.goto("about:blank")

    result = page.evaluate(
        """async () => {
            try {
                await fetch('https://mock-api.test/mock-api/aborted');
                return 'unexpected-success';
            } catch (error) {
                return 'aborted';
            }
        }"""
    )

    expect(page.locator("body")).to_be_visible()
    assert result == "aborted"


@pytest.mark.ui
@allure.feature("Network diagnostics")
@allure.story("Request continuation")
@pytest.mark.integration
def test_matching_request_can_continue_to_the_application(page, mock_route):
    mock_route("**/web/index.php/auth/login", action="continue")
    page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
    expect(page.get_by_role("heading", name="Login", exact=True)).to_be_visible()