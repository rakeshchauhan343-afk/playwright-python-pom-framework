import re

from playwright.sync_api import expect

from .base_page import BasePage


class RecruitmentPage(BasePage):
    """OrangeHRM Recruitment / Candidates page."""

    RECRUITMENT_MENU = "Recruitment"
    RECRUITMENT_HEADING = "Recruitment"
    CANDIDATES_TAB = "Candidates"
    ADD_BUTTON = "Add"
    ADD_CANDIDATE_HEADING = "Add Candidate"
    RECRUITMENT_URL = re.compile(r"/web/index\.php/recruitment/viewCandidates/?$")
    ADD_CANDIDATE_URL = re.compile(r"/web/index\.php/recruitment/addCandidate/?$")

    def open_recruitment(self) -> None:
        self.page.get_by_role("link", name=self.RECRUITMENT_MENU, exact=True).click()
        expect(self.page).to_have_url(self.RECRUITMENT_URL)
        expect(
            self.page.get_by_role("heading", name=self.RECRUITMENT_HEADING, exact=True)
        ).to_be_visible()

    def expect_candidates_page(self) -> None:
        expect(self.page).to_have_url(self.RECRUITMENT_URL)
        expect(self.page.get_by_role("link", name=self.CANDIDATES_TAB, exact=True)).to_be_visible()

    def click_add(self) -> None:
        self.page.get_by_text(self.ADD_BUTTON, exact=True).click()

    def expect_add_candidate_page(self) -> None:
        expect(self.page).to_have_url(self.ADD_CANDIDATE_URL)
        expect(
            self.page.get_by_role("heading", name=self.ADD_CANDIDATE_HEADING, exact=True)
        ).to_be_visible()