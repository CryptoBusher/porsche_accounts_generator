"""
Registering accounts on Porsche website without email approval.
"""

from sys import stderr
from urllib3 import disable_warnings
import string
import random
import secrets
import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor

import undetected_chromedriver as uc
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import requests
from loguru import logger
from random_username.generate import generate_username

disable_warnings()
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | "
                          "<cyan>{line}</cyan> - <white>{message}</white>")


class FileManager:
    """
    Class contains functions for manipulating txt and json files.
    """

    @staticmethod
    def read_txt_file(file_name: str):
        """
        Method for reading txt files
        :param file_name: str
        :return: list
        """
        with open(f'{file_name}.txt') as file:
            return [line.rstrip() for line in file]

    @staticmethod
    def append_txt_file(file_name: str, data: str):
        """
        Method for saving txt files
        :param file_name: str
        :param data: str
        """

        with open(f'{file_name}.txt', 'a') as file:
            file.write(f'{data}\n')


class PorscheWebsiteInterface:
    """
    Object for init Xpath of elements on Porsche website.
    """

    def __init__(self):
        self.email_input = '//*[@id="EMAIL-3"]'
        self.rules_agree_checkbox = '//*[@id="checkbox"]'
        self.subscribe_button = '//*[@id="wf-form-EMAIL"]/div/input[2]'
        self.success_message_div = '/html/body/div[2]/div[1]/div/div[2]/div[1]/div/div'
        self.success_message = 'Awesome. You are just a few clicks away from entering the Porsche NFT universe. ' \
                               'Complete your registration using the link you will receive by e-mail in a few minutes.'


class MailTmAccount:
    """
    Class for creating new mail.tm account.
    """

    API_URL = 'https://api.mail.tm'

    def __init__(self):
        self.mail_login = None
        self.mail_pass = None
        self.mail_access_token = None
        self.__generate_username_and_password()

    def __generate_username_and_password(self):

        letters = string.ascii_lowercase
        additional_letters = (''.join(random.choice(letters) for _ in range(3)))

        self.mail_login = generate_username()[0].lower() + additional_letters + '@knowledgemd.com'
        self.mail_pass = secrets.token_urlsafe(10).lower()

    def create_new_mail_account(self):
        """
        Generates new email account.
        :return: bool
        """
        headers = {"Content-type": "application/json"}
        body = {"address": self.mail_login, "password": self.mail_pass}

        try:
            response = requests.post(self.API_URL + '/accounts', headers=headers, data=json.dumps(body))
            json_resp = json.loads(response.text)

            if json_resp['@context'] != '/contexts/ConstraintViolationList':
                self.mail_access_token = 'test'
                return True
                # access_token_generated = self.__generate_mail_access_token()
                # if access_token_generated:
                #     return True
        except Exception as e:
            logger.error(e)
            return False


class PorscheAccount:
    """
    Class for registration of Porsche account.
    """

    PORSCHE_WEBSITE = 'https://www.nft.porsche.com/'

    def __init__(self, driver: webdriver, email: str, password: str):
        self.driver = driver
        self.email = email
        self.password = password

    def register_account(self):
        """
        Method for registering Porsche account.
        :return: bool
        """

        interface = PorscheWebsiteInterface()
        wait = WebDriverWait(self.driver, 60)

        self.driver.get(self.PORSCHE_WEBSITE)
        self.driver.maximize_window()
        wait.until(ec.presence_of_element_located((By.XPATH, interface.email_input))).send_keys(self.email)

        wait.until(ec.element_to_be_clickable((By.XPATH, interface.rules_agree_checkbox))).click()
        wait.until(ec.presence_of_element_located((By.XPATH, interface.subscribe_button))).click()

        try:
            success_message_div = wait.until(ec.presence_of_element_located((By.XPATH, interface.success_message_div)))
            success_message = success_message_div.get_attribute('innerText')
            if success_message == interface.success_message:
                self.driver.close()
                return True

        except Exception as e:
            logger.error(e)
            self.driver.close()
            return False


def init_selenium_driver(proxy=None):
    """
    Init selenium webdriver for connecting to Dolphin profile.
    :param proxy: http proxy (http://login:pass@host:port)
    :return: selenium driver object
    """

    if proxy is None:
        chrome_options = uc.ChromeOptions()
        driver = uc.Chrome(options=chrome_options)
        return driver

    else:
        options = {
            'proxy': {
                'http': proxy,
                'https': proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(seleniumwire_options=options, options=chrome_options)
        return driver


if __name__ == "__main__":

    def main(email_object: MailTmAccount, proxy: str):
        """
        Main logic.
        """

        new_driver = init_selenium_driver(proxy)

        porsche_account = PorscheAccount(new_driver, email_object.mail_login, email_object.mail_pass)
        porsche_account_registered = porsche_account.register_account()
        if not porsche_account_registered:
            logger.error('Failed to register Porsche account.')
        else:
            logger.success('Porsche account registered.')

            if proxy is None:
                FileManager.append_txt_file('registered_accounts', f'{email_object.mail_login}'
                                                                   f':{email_object.mail_pass}')
            else:
                FileManager.append_txt_file('registered_accounts', f'{email_object.mail_login}'
                                                                   f':{email_object.mail_pass}'
                                                                   f':{proxy}')


    total_threads = int(input('Enter amount of threads: '))
    use_proxies = input('Use personal proxies? y/n: ')
    if use_proxies == 'y':
        proxies = FileManager.read_txt_file('proxies')
        accounts_to_register = len(proxies)
    elif use_proxies == 'n':
        accounts_to_register = int(input('Enter amount of accounts to be registered: '))
        proxies = [None for _ in range(accounts_to_register)]
    else:
        logger.error('Wrong entry')
        exit()

    mail_accounts = []
    i = 0
    while i < accounts_to_register:
        logger.info(f'Registering email {i + 1}/{accounts_to_register}')
        mail_account = MailTmAccount()
        mail_account_generated = mail_account.create_new_mail_account()
        if not mail_account_generated:
            logger.error('Failed to generate mail account.')
        else:
            logger.success('New email registered.')
            mail_accounts.append(mail_account)
            i += 1
            sleep(0.15)

    with ThreadPoolExecutor(max_workers=total_threads) as executor:
        executor.map(main, mail_accounts, proxies)
