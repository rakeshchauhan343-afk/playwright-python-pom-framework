import re

from playwright.sync_api import expect

from .base_page import BasePage


class AdminPage(BasePage):
    """OrangeHRM Admin / User Management page."""

    ADMIN_MENU = "Admin"
    ADMIN_HEADING = "Admin"
    USERNAME_LABEL = "Username"
    USER_ROLE_LABEL = "User Role"
    EMPLOYEE_NAME_PLACEHOLDER = "Type for hints..."
    STATUS_LABEL = "Status"
    SEARCH_BUTTON = "Search"
    ADD_BUTTON = "Add"
    ADD_USER_HEADING = "Add User"

    def open_admin(self) -> None:
        self.page.get_by_role("link", name=self.ADMIN_MENU, exact=True).click()
        expect(self.page.get_by_role("heading", name=self.ADMIN_HEADING, exact=True)).to_be_visible()

    def enter_username(self, username: str) -> None:
        self._form_group(self.USERNAME_LABEL).locator("input").fill(username)

    def select_user_role(self, role: str) -> None:
        self._select_option(self.USER_ROLE_LABEL, role)

    def enter_employee_name(self, employee_name: str) -> None:
        employee_input = self.page.get_by_placeholder(self.EMPLOYEE_NAME_PLACEHOLDER)
        employee_input.fill(employee_name)
        suggestion = self.page.locator(".oxd-autocomplete-option").filter(has_text=employee_name)
        if suggestion.count() > 0:
            suggestion.first.click()
        else:
            expect(employee_input).to_have_value(employee_name)

    def select_status(self, status: str) -> None:
        self._select_option(self.STATUS_LABEL, status)

    def click_search(self) -> None:
        self.page.get_by_role("button", name=self.SEARCH_BUTTON, exact=True).click()

    def verify_search_result(self, username: str) -> None:
        records_found = self.page.get_by_text("Records Found", exact=False).first
        expect(records_found).to_be_visible()

    def click_add(self) -> None:
        self.page.get_by_role("button", name=re.compile(r"Add")).click()

    def verify_add_user_page(self) -> None:
        expect(self.page.get_by_role("heading", name=self.ADD_USER_HEADING, exact=True)).to_be_visible()

    def _form_group(self, label: str):
        return self.page.locator(".oxd-input-group").filter(has_text=label).first

    def _select_option(self, label: str, option: str) -> None:
        self._form_group(label).locator(".oxd-select-text").click()
        self.page.get_by_role("option", name=option, exact=True).click()