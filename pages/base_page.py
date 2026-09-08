from collections.abc import Callable
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, Response, expect


class BasePage:
    """Shared browser operations used by page objects."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, url: str) -> None:
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

    def click(self, selector: str) -> None:
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        self.page.locator(selector).fill(value)

    def wait_for_visible(self, selector: str, timeout: float = 10_000) -> None:
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def wait_for_url(self, url: str, timeout: float = 10_000) -> None:
        expect(self.page).to_have_url(url, timeout=timeout)

    def wait_for_load_state(self, state: str = "domcontentloaded") -> None:
        self.page.wait_for_load_state(state)

    def take_screenshot(self, path: str | Path, full_page: bool = True) -> None:
        self.page.screenshot(path=str(path), full_page=full_page)

    def assert_title(self, title: str) -> None:
        expect(self.page).to_have_title(title)

    def current_url(self) -> str:
        return self.page.url

    def wait_for_response(
        self,
        url_or_predicate: str | Callable[[Response], bool],
        action: Callable[[], Any],
        timeout: float = 10_000,
    ) -> Response:
        with self.page.expect_response(url_or_predicate, timeout=timeout) as response_info:
            action()
        return response_info.value
