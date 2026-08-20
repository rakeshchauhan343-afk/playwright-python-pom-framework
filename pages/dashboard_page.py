import re

from playwright.sync_api import expect

from .base_page import BasePage


class DashboardPage(BasePage):
    """OrangeHRM dashboard page."""

    DASHBOARD_HEADING = "Dashboard"
    DASHBOARD_URL = re.compile(r"/web/index\.php/dashboard/index/?$")

    def expect_loaded(self) -> None:
        expect(self.page.get_by_role("heading", name=self.DASHBOARD_HEADING)).to_be_visible()

    def expect_url(self) -> None:
        expect(self.page).to_have_url(self.DASHBOARD_URL)