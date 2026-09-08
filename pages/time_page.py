import re

from playwright.sync_api import expect

from .base_page import BasePage


class TimePage(BasePage):
    """OrangeHRM Time / employee timesheet page."""

    TIME_MENU = "Time"
    TIME_PAGE_HEADING = "Time"
    TIMESHEET_LABEL = "Timesheets"
    TIME_URL = re.compile(r"/web/index\.php/time/")
    VIEW_BUTTON = "View"

    def open_time(self) -> None:
        self.page.get_by_role("link", name=self.TIME_MENU, exact=True).click()

    def expect_time_page(self) -> None:
        expect(self.page).to_have_url(self.TIME_URL)
        expect(
            self.page.get_by_role("heading", name=self.TIME_PAGE_HEADING, exact=True)
        ).to_be_visible()

    def click_view(self) -> None:
        self.page.get_by_role("button", name=self.VIEW_BUTTON, exact=True).click()

    def expect_timesheet_page(self) -> None:
        expect(self.page).to_have_url(self.TIME_URL)
        expect(self.page.get_by_text(self.TIMESHEET_LABEL, exact=True).first).to_be_visible()