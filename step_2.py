"""
Approving Porsche accounts via email.
"""

from sys import stderr
from urllib3 import disable_warnings
from concurrent.futures import ThreadPoolExecutor

from anticaptchaofficial.recaptchav2proxyless import *
import undetected_chromedriver as uc
from seleniumwire import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import requests
from loguru import logger


disable_warnings()
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | "
                          "<cyan>{line}</cyan> - <white>{message}</white>")


class FileManager:
    """
    Class contains functions for manipulating txt and json files.
    """

    @staticmethod
    def read_json_file(file_name: str):
        """
        Method for reading json files
        :param file_name: str
        :return: json data
        """
        with open(f'{file_name}.json') as json_file:
            return json.load(json_file)

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


def generate_mail_access_token(email: str, password: str):
    """
    Generates access token for account.
    :return: access token: str
    """

    headers = {"Content-type": "application/json"}
    body = {"address": email, "password": password}

    try:
        response = requests.post('https://api.mail.tm/token', headers=headers, data=json.dumps(body))
        json_resp = json.loads(response.text)

        if 'token' in json_resp:
            mail_access_token = json_resp['token']
            return mail_access_token
        else:
            return None
    except:
        return None


def read_incoming_message(token: str):
    """
    Reads received message.
    :param token: str
    :return: incoming message: str
    """

    headers = {"Authorization": "Bearer " + token}
    body = {"page": 1}

    response = requests.get('https://api.mail.tm/messages', headers=headers, data=json.dumps(body))
    json_resp = json.loads(response.text)

    messages_count = int(json_resp['hydra:totalItems'])
    if messages_count != 0:
        all_messages = json_resp['hydra:member']
        for new_message in all_messages:
            if new_message['from']['address'] == 'nftnews@porsche.digital':
                return new_message

    return None


def parse_link(email_access_token: str, token: dict):
    """
    Parses link from received message
    :param email_access_token: str
    :param token: dict
    """

    headers = {"Authorization": "Bearer " + email_access_token}

    try:
        response = requests.get('https://api.mail.tm/messages/' + token['id'], headers=headers)
        json_resp = json.loads(response.text)
        message_full_text = json_resp['text']
        final_link = message_full_text.split('to this list. (')[1].split(')')[0]
        return final_link

    except:
        return None


def init_selenium_driver(account_proxy=None):
    """
    Init selenium webdriver for connecting to Dolphin profile.
    :param account_proxy: http proxy (http://login:pass@host:port)
    :return: selenium driver object
    """

    if account_proxy is None:
        chrome_options = uc.ChromeOptions()
        driver = uc.Chrome(options=chrome_options)
        return driver

    else:
        options = {
            'proxy': {
                'http': account_proxy,
                'https': account_proxy,
                'no_proxy': 'localhost,127.0.0.1'
            }
        }

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(seleniumwire_options=options, options=chrome_options)
        return driver


def authorize_link(final_link: str, anticaptcha_api_key: str, account_proxy=None):
    """
    Authorizes final link.
    :param account_proxy: str (http://username:password@ip:port
    :param final_link: str
    :param anticaptcha_api_key: str
    """

    def solve_captcha():
        """
        Solves captcha using anti-captcha service.
        :return: captcha_response: str
        """
        solver = recaptchaV2Proxyless()
        solver.set_verbose(1)
        solver.set_key(anticaptcha_api_key)
        solver.set_website_url(final_link)
        solver.set_website_key(sitekey_clean)
        captcha_response = solver.solve_and_return_solution()
        if captcha_response != 0:
            return captcha_response

    subscribe_button_xpath = '//*[@id="templateBody"]/form/input[5]'
    sitekey_div_xpath = '//*[@id="templateBody"]/form/div/div'
    success_div = '/html/body/div[2]/div[1]/div/div[1]'

    new_driver = init_selenium_driver(account_proxy)
    wait = WebDriverWait(new_driver, 60)

    try:
        new_driver.get(final_link)
        wait.until(ec.presence_of_element_located((By.XPATH, subscribe_button_xpath)))
        sitekey_div = new_driver.find_element(By.XPATH, sitekey_div_xpath).get_attribute('outerHTML')
        sitekey_clean = sitekey_div.split('data-sitekey="')[1].split('"><div style')[0]
        g_response = solve_captcha()

        if g_response is not None:
            new_driver.execute_script('var element=document'
                                      '.getElementById("g-recaptcha-response"); element.style.display="";')
            new_driver.execute_script('document'
                                      '.getElementById("g-recaptcha-response").innerHTML = arguments[0]', g_response)
            new_driver.execute_script('var element=document'
                                      '.getElementById("g-recaptcha-response"); element.style.display="none";')

            wait.until(ec.presence_of_element_located((By.XPATH, subscribe_button_xpath))).click()
            success_message = wait.until(ec.presence_of_element_located((By.XPATH, success_div)))\
                .get_attribute('innerText')

            if 'thank you' in success_message.lower():
                new_driver.close()
                return True
            else:
                new_driver.close()
                return False
        else:
            new_driver.close()
            return False

    except Exception as e:
        logger.error(e)
        new_driver.close()
        return False


if __name__ == "__main__":

    def main(account):
        """
        Main logic.
        :return:
        """
        config_data = FileManager.read_json_file('config')
        anticaptcha_key = config_data['anticaptcha_key']

        split_data = account.split(':')
        if len(split_data) > 2:
            proxy = split_data[2] + ':' + split_data[3] + ':' + split_data[4] + ':' + split_data[5]
        else:
            proxy = None

        account_email = split_data[0]
        account_password = split_data[1]
        account_access_token = generate_mail_access_token(account_email, account_password)
        if account_access_token is None:
            logger.error('Failed to get email access token.')
            return
        else:
            logger.success('Received email access token.')

        message = read_incoming_message(account_access_token)
        if message is None:
            logger.error('No any incoming messages from Porsche.')
            return
        else:
            logger.success('Found message from Porsche.')

        link = parse_link(account_access_token, message)
        if link is None:
            logger.error('Failed to parse link.')
            return
        else:
            logger.success('Parsed link.')

        authorized = authorize_link(link, anticaptcha_key, proxy)
        if not authorized:
            logger.error('Failed to authorize account')
            return
        else:
            logger.success('Entry authorized.')
            FileManager.append_txt_file('authorized_accounts', account)


    total_threads = int(input('Enter amount of threads: '))
    registered_accounts = FileManager.read_txt_file('registered_accounts')

    with ThreadPoolExecutor(max_workers=total_threads) as executor:
        executor.map(main, registered_accounts)
