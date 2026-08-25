from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse


class BaseApiClient:
    """Thin wrapper for Playwright API requests shared by endpoint clients."""

    def __init__(self, request_context: APIRequestContext) -> None:
        self.request_context = request_context

    def get(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request_context.get(path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request_context.post(path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request_context.put(path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request_context.patch(path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> APIResponse:
        return self.request_context.delete(path, **kwargs)

    @staticmethod
    def assert_status(response: APIResponse, expected_status: int = 200) -> None:
        assert response.status == expected_status, (
            f"Expected HTTP {expected_status}, got {response.status}: {response.text()}"
        )

    @staticmethod
    def json_body(response: APIResponse) -> dict[str, Any]:
        body = response.json()
        assert isinstance(body, dict), "Expected the API response body to be a JSON object"
        return body

    @staticmethod
    def assert_json_keys(response: APIResponse, *keys: str) -> dict[str, Any]:
        body = BaseApiClient.json_body(response)
        missing_keys = [key for key in keys if key not in body]
        assert not missing_keys, f"Response is missing JSON keys: {missing_keys}"
        return body