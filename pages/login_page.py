from .base_page import BasePage


class LoginPage(BasePage):
    """OrangeHRM login page."""

    USERNAME_PLACEHOLDER = "Username"
    PASSWORD_PLACEHOLDER = "Password"
    LOGIN_BUTTON_NAME = "Login"
    ERROR_MESSAGE = ".oxd-alert-content-text"

    def open(self, url: str) -> None:
        self.navigate(url)

    def enter_username(self, username: str) -> None:
        self.page.get_by_placeholder(self.USERNAME_PLACEHOLDER).fill(username)

    def enter_password(self, password: str) -> None:
        self.page.get_by_placeholder(self.PASSWORD_PLACEHOLDER).fill(password)

    def submit(self) -> None:
        self.page.get_by_role("button", name=self.LOGIN_BUTTON_NAME).click()

    def login(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

    def error_is_visible(self) -> None:
        self.wait_for_visible(self.ERROR_MESSAGE)
