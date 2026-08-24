from .base_page import BasePage


class LoginPage(BasePage):
    """OrangeHRM login page."""

    USERNAME_PLACEHOLDER = "Username"
    PASSWORD_PLACEHOLDER = "Password"
    LOGIN_BUTTON_NAME = "Login"
    ERROR_MESSAGE = ".oxd-alert-content-text"

    def open(self, url: str) -> None:
        self.navigate(url)

    def login_heading(self):
        return self.page.get_by_role("heading", name="Login", exact=True)

    def username_input(self):
        return self.page.get_by_placeholder(self.USERNAME_PLACEHOLDER, exact=True)

    def password_input(self):
        return self.page.get_by_placeholder(self.PASSWORD_PLACEHOLDER, exact=True)

    def login_button(self):
        return self.page.get_by_role("button", name=self.LOGIN_BUTTON_NAME, exact=True)

    def forgot_password_link(self):
        return self.page.get_by_text("Forgot your password?", exact=True)

    def enter_username(self, username: str) -> None:
        self.username_input().fill(username)

    def enter_password(self, password: str) -> None:
        self.password_input().fill(password)

    def submit(self) -> None:
        self.login_button().click()

    def login(self, username: str, password: str) -> None:
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

    def error_is_visible(self) -> None:
        self.wait_for_visible(self.ERROR_MESSAGE)
