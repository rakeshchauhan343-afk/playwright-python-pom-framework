import re

from playwright.sync_api import expect

from .base_page import BasePage


class MyInfoPage(BasePage):
    """OrangeHRM My Info / Personal Details page."""

    MY_INFO_MENU = "My Info"
    PERSONAL_DETAILS_HEADING = "Personal Details"
    PERSONAL_DETAILS_URL = re.compile(r"/web/index\.php/pim/viewPersonalDetails/")
    SAVE_BUTTON = "Save"
    SUCCESS_TOAST = ".oxd-toast"
    SUCCESS_MESSAGE = "Successfully Updated"

    def open_my_info(self) -> None:
        self.page.get_by_role("link", name=self.MY_INFO_MENU, exact=True).click()

    def expect_personal_details_page(self) -> None:
        expect(self.page).to_have_url(self.PERSONAL_DETAILS_URL)
        expect(
            self.page.get_by_role(
                "heading", name=self.PERSONAL_DETAILS_HEADING, exact=True
            )
        ).to_be_visible()

    def personal_details_save_button(self):
        return self.page.get_by_role("button", name=self.SAVE_BUTTON, exact=True).first

    def click_save(self) -> None:
        self.personal_details_save_button().click()

    def expect_save_successful(self) -> None:
        expect(self.page.locator(self.SUCCESS_TOAST)).to_contain_text(
            self.SUCCESS_MESSAGE
        )