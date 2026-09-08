import re

from playwright.sync_api import expect

from .base_page import BasePage


class LeavePage(BasePage):
    """OrangeHRM Leave / Leave List page."""

    LEAVE_MENU = "Leave"
    LEAVE_HEADING = "Leave"
    LEAVE_LIST_TAB = "Leave List"
    LEAVE_LIST_URL = re.compile(r"/web/index\.php/leave/viewLeaveList/?$")
    SEARCH_BUTTON = "Search"

    def open_leave(self) -> None:
        self.page.get_by_role("link", name=self.LEAVE_MENU, exact=True).click()
        expect(
            self.page.get_by_role("heading", name=self.LEAVE_HEADING, exact=True)
        ).to_be_visible()

    def open_leave_list(self) -> None:
        self.page.get_by_role("link", name=self.LEAVE_LIST_TAB, exact=True).click()
        expect(self.page).to_have_url(self.LEAVE_LIST_URL)

    def click_search(self) -> None:
        self.page.get_by_role("button", name=self.SEARCH_BUTTON, exact=True).click()

    def expect_search_completed(self) -> None:
        expect(self.page.get_by_text("Records Found", exact=False).first).to_be_visible()