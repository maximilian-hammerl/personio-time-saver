import logging
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import configparser

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

config = configparser.ConfigParser()
config.read('config.ini')

service = FirefoxService(executable_path=GeckoDriverManager().install())

profile_path = config['firefox']['profile_path']
firefox_options = webdriver.FirefoxOptions()
firefox_options.set_preference('profile', profile_path)

firefox_options.add_argument("-profile")
firefox_options.add_argument(profile_path)

email_address_input_xpath = '//input[@id="email"]'
password_input_xpath = '//input[@id="password"]'
login_button_xpath = '//button[@type="submit" and contains(text(), "Einloggen")]'

token_input_xpath = '//input[@id="token"]'
continue_login_button_xpath = '//button[@type="submit" and contains(text(), "Login")]'


def do_stuff():
    subdomain = config['personio']['subdomain']
    domain = f'https://{subdomain}.personio.de'

    # with webdriver.Firefox(service=service, options=firefox_options) as driver:
    driver = webdriver.Firefox(service=service, options=firefox_options)
    wait = WebDriverWait(driver, 10)

    logging.info(f'Opening {domain=} ({subdomain=})')
    driver.get(domain)

    try:
        logging.info('Waiting for login button')
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, login_button_xpath)))

        logging.info('Found login button, filling form data')
        driver.find_element(by=By.XPATH, value=email_address_input_xpath).send_keys(config['personio']['email_address'])
        driver.find_element(by=By.XPATH, value=password_input_xpath).send_keys(config['personio']['password'])

        logging.info('Clicking login button')
        driver.find_element(By.XPATH, login_button_xpath).click()
    except TimeoutException:
        logging.info('No login button, skipping login page')

    try:
        logging.info('Waiting for continue login button')
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, continue_login_button_xpath)))

        logging.warning('Found continue login button, waiting for you to enter the token')

        while True:
            token_input = driver.find_element(by=By.XPATH, value=token_input_xpath)
            if token_input.is_selected() and len(token_input.text) > 0:
                logging.warning('Token entered, continuing')
                break
            logging.warning('No token, sleeping')
            time.sleep(1)

        logging.info('Clicking continue login button')
        driver.find_element(By.XPATH, continue_login_button_xpath).click()
    except TimeoutException:
        logging.info('No continue login button, skipping token page')




if __name__ == '__main__':
    do_stuff()
