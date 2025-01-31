import os
import time
import requests

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.desktop.base import Base
from scripts import reusables


class Login(Base):
    """The following variables need to be set as Environment Variables
     when running tests locally. These variables are also set in CircleCI's
    Project level Environment Variables and are picked up at runtime"""

    # 1. user that performs normal operations on the site, like writing add-on reviews
    REGULAR_USER_EMAIL = os.environ.get('REGULAR_USER_EMAIL')
    REGULAR_USER_PASSWORD = os.environ.get('REGULAR_USER_PASSWORD')
    # 2. user with elevated permissions that can perform special actions on the site
    ADMIN_USER_EMAIL = os.environ.get('ADMIN_USER_EMAIL')
    ADMIN_USER_PASSWORD = os.environ.get('ADMIN_USER_PASSWORD')
    # 3. user who has published add-ons on AMO
    DEVELOPER_EMAIL = os.environ.get('DEVELOPER_EMAIL')
    DEVELOPER_PASSWORD = os.environ.get('DEVELOPER_PASSWORD')
    # 4. user who re-creates accounts on AMO after having deleted them previously
    REUSABLE_USER_EMAIL = os.environ.get('REUSABLE_USER_EMAIL')
    REUSABLE_USER_PASSWORD = os.environ.get('REUSABLE_USER_PASSWORD')
    # 5. user used for the ratings tests
    RATING_USER_EMAIL = os.environ.get('RATING_USER_EMAIL')
    RATING_USER_PASSWORD = os.environ.get('RATING_USER_PASSWORD')
    # 6. user used for collections tests
    COLLECTION_USER_EMAIL = os.environ.get('COLLECTION_USER_EMAIL')
    COLLECTION_USER_PASSWORD = os.environ.get('COLLECTION_USER_PASSWORD')
    # 7. user used for add-on submissions
    SUBMISSIONS_USER_EMAIL = os.environ.get('SUBMISSIONS_USER_EMAIL')
    SUBMISSIONS_USER_PASSWORD = os.environ.get('SUBMISSIONS_USER_PASSWORD')
    # 8. user used in API tests
    API_USER_EMAIL = os.environ.get('API_USER_EMAIL')
    API_USER_PASSWORD = os.environ.get('API_USER_PASSWORD')
    # 9. user with a mozilla account that has specific submission permissions
    STAFF_USER_EMAIL = os.environ.get('STAFF_USER_EMAIL')
    STAFF_USER_PASSWORD = os.environ.get('STAFF_USER_PASSWORD')
    # 10. account added to the list of banned user emails for rating and addon submissions
    RESTRICTED_USER_EMAIL = os.environ.get('RESTRICTED_USER_EMAIL')
    RESTRICTED_USER_PASSWORD = os.environ.get('RESTRICTED_USER_PASSWORD')

    _email_locator = (By.NAME, 'email')
    _continue_locator = (By.CSS_SELECTOR, '.button-row button')
    _password_locator = (By.ID, 'password')
    _login_btn_locator = (By.ID, 'submit-btn')
    _repeat_password_locator = (By.ID, 'vpassword')
    _age_locator = (By.ID, 'age')
    _code_input_locator = (By.CSS_SELECTOR, '.tooltip-below')
    _login_card_header_locator = (By.CSS_SELECTOR, '.card header h1')

    def account(self, user):
        if user == 'reusable_user':
            self.fxa_login(self.REUSABLE_USER_EMAIL, self.REUSABLE_USER_PASSWORD)
        elif user == 'admin':
            self.fxa_login(self.ADMIN_USER_EMAIL, self.ADMIN_USER_PASSWORD)
        elif user == 'developer':
            self.fxa_login(self.DEVELOPER_EMAIL, self.DEVELOPER_PASSWORD)
        elif user == 'rating_user':
            self.fxa_login(self.RATING_USER_EMAIL, self.RATING_USER_PASSWORD)
        elif user == 'collection_user':
            self.fxa_login(self.COLLECTION_USER_EMAIL, self.COLLECTION_USER_PASSWORD)
        elif user == 'submissions_user':
            self.fxa_login(self.SUBMISSIONS_USER_EMAIL, self.SUBMISSIONS_USER_PASSWORD)
        elif user == 'api_user':
            self.fxa_login(self.API_USER_EMAIL, self.API_USER_PASSWORD)
        elif user == 'staff_user':
            self.fxa_login(self.STAFF_USER_EMAIL, self.STAFF_USER_PASSWORD)
        elif user == 'restricted_user':
            self.fxa_login(self.RESTRICTED_USER_EMAIL, self.RESTRICTED_USER_PASSWORD)
        else:
            self.fxa_login(self.REGULAR_USER_EMAIL, self.REGULAR_USER_PASSWORD)

    def fxa_login(self, email, password):
        self.find_element(*self._email_locator).send_keys(email)
        # sometimes, the login function fails on the 'continue_btn.click()' event with a TimeoutException
        # triggered by the built in timeout of the 'click()' method;
        # however, the screenshot captured by the html report at test fail time shows that the click occurred
        # since the expected page has been loaded;
        # this seems to be a reoccurring issue in geckodriver as explained in
        # https://github.com/mozilla/geckodriver/issues/1608;
        # here, I'm capturing that TimeoutException and trying to push the script to continue to the next steps.
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'submit-btn'))
            )
            continue_btn.click()
        except TimeoutException as error:
            print(error.msg)
            pass
        print('The "click continue button" event occurred.')
        self.wait.until(
            EC.element_to_be_clickable(self._password_locator),
            message=f'Password input field not displayed; '
            f'FxA card header was {self.find_element(*self._login_card_header_locator).text}',
        )
        print(
            f'The script should be on the password input screen here. We should see "Sign in" in the header.'
            f' The card  header title is "{self.find_element(*self._login_card_header_locator).text}"'
        )
        self.find_element(*self._password_locator).send_keys(password)
        # waits for the password to be filled in
        self.wait.until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '.password.empty')),
            message='There was no input added in the password field',
        )
        self.find_element(*self._login_btn_locator).click()

    def fxa_register(self):
        email = f'{reusables.get_random_string(10)}@restmail.net'
        password = reusables.get_random_string(10)
        self.find_element(*self._email_locator).send_keys(email)
        # catching the geckodriver click() issue, in cae it happens here
        # issue - https://github.com/mozilla/geckodriver/issues/1608
        try:
            continue_btn = self.wait.until(
                EC.element_to_be_clickable((By.ID, 'submit-btn'))
            )
            continue_btn.click()
        except TimeoutException as error:
            print(error.msg)
            pass
        # verify that the fxa register form was opened
        self.wait.until(
            EC.element_to_be_clickable(self._password_locator),
            message=f'Password input field not displayed; '
            f'FxA card header was {self.find_element(*self._login_card_header_locator).text}',
        )
        self.find_element(*self._password_locator).send_keys(password)
        self.find_element(*self._repeat_password_locator).send_keys(password)
        self.find_element(*self._age_locator).send_keys(23)
        self.find_element(*self._login_btn_locator).click()
        # sleep to allow FxA to process the request and communicate with the email client
        time.sleep(3)
        verification_code = self.get_verification_code(email)
        self.find_element(*self._code_input_locator).send_keys(verification_code)
        self.find_element(*self._login_btn_locator).click()

    def get_verification_code(self, mail):
        request = requests.get(f'https://restmail.net/mail/{mail}', timeout=10)
        response = request.json()
        # creating a timed loop to address a possible communication delay between
        # FxA and restmail; this loop polls the endpoint for 20s to await a response
        # and exits if there was no response received in the given amount of time
        timeout_start = time.time()
        while time.time() < timeout_start + 20:
            if response:
                verification_code = [
                    key['headers']['x-verify-short-code'] for key in response
                ]
                return verification_code
            elif not response:
                requests.get(f'https://restmail.net/mail/{mail}', timeout=10)
                print('Restmail did not receive an email from FxA')
        return self
