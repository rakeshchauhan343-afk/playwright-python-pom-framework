import re

from playwright.sync_api import Locator, expect

from .base_page import BasePage


class PimPage(BasePage):
    """OrangeHRM PIM / Employee List page."""

    PIM_MENU = "PIM"
    PIM_HEADING = "PIM"
    EMPLOYEE_LIST_HEADING = re.compile(r"Employee (List|Information)")
    EMPLOYEE_ROWS = ".oxd-table-card"
    ACTIONS_CELL = ".oxd-table-cell-actions"
    DELETE_DIALOG = ".oxd-dialog"
    DELETE_DIALOG_HEADING = "Are you Sure?"
    CONFIRM_DELETE_BUTTON = "Yes, Delete"
    SUCCESS_TOAST = ".oxd-toast"

    def open_pim(self) -> None:
        self.page.get_by_role("link", name=self.PIM_MENU, exact=True).click()
        expect(self.page.get_by_role("heading", name=self.PIM_HEADING, exact=True)).to_be_visible()

    def expect_employee_list_visible(self) -> None:
        expect(
            self.page.get_by_role("heading", name=self.EMPLOYEE_LIST_HEADING, exact=True)
        ).to_be_visible()

    def search_employee(self, employee_name: str) -> None:
        employee_input = self.page.get_by_placeholder("Type for hints...").first
        employee_input.fill(employee_name)
        suggestion = self.page.locator(".oxd-autocomplete-option").filter(has_text=employee_name)
        if suggestion.count() > 0:
            suggestion.first.click()
        self.page.get_by_role("button", name="Search", exact=True).click()

    def expect_employee_visible(self, employee_name: str) -> None:
        expect(self.page.get_by_text(employee_name, exact=True)).to_be_visible()

    def edit_employee(self, row: Locator) -> None:
        edit_button = row.locator(self.ACTIONS_CELL).get_by_role("button").first
        expect(edit_button).to_be_visible()
        edit_button.click()

    def update_first_name(self, first_name: str) -> None:
        first_name_input = self.page.locator(".oxd-input-group").filter(has_text="First Name").first.locator("input")
        expect(first_name_input).to_be_visible()
        first_name_input.fill(first_name)
        self.page.get_by_role("button", name="Save", exact=True).click()
        expect(self.page.locator(self.SUCCESS_TOAST)).to_contain_text("Successfully Updated")

    def scroll_employee_list(self) -> None:
        expect(self.employee_rows).not_to_have_count(0)
        self.employee_rows.last.scroll_into_view_if_needed()

    @property
    def employee_rows(self) -> Locator:
        return self.page.locator(self.EMPLOYEE_ROWS)

    def first_employee_row(self) -> Locator:
        row = self.employee_rows.first
        expect(row).to_be_visible()
        return row

    def delete_employee(self, row: Locator) -> None:
        delete_button = row.locator(self.ACTIONS_CELL).get_by_role("button").last
        expect(delete_button).to_be_visible()
        delete_button.click()

    def expect_delete_confirmation_visible(self) -> None:
        dialog = self.page.locator(self.DELETE_DIALOG)
        expect(dialog).to_be_visible()
        expect(
            dialog.get_by_role("heading", name=self.DELETE_DIALOG_HEADING, exact=True)
        ).to_be_visible()

    def confirm_delete(self) -> None:
        self.page.get_by_role(
            "button", name=self.CONFIRM_DELETE_BUTTON, exact=True
        ).click()

    def expect_employee_deleted(self, row: Locator) -> None:
        expect(self.page.locator(self.SUCCESS_TOAST)).to_contain_text("Successfully Deleted")
        expect(row).not_to_be_visible()