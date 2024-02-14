#!/usr/bin/env python3

import logging
import time
import configparser

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.core.logger import set_logger
from webdriver_manager.firefox import GeckoDriverManager

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(stream_handler)
set_logger(logger)

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
login_button_xpath = '//button[@type="submit"]//div[contains(text(), "Einloggen")]'


def _login(driver: WebDriver, wait: WebDriverWait) -> bool:
    try:
        logger.info('Waiting for login button')
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, login_button_xpath)))

        logger.info('Found login button, filling form data')
        driver.find_element(by=By.XPATH, value=email_address_input_xpath).send_keys(config['personio']['email_address'])
        driver.find_element(by=By.XPATH, value=password_input_xpath).send_keys(config['personio']['password'])

        logger.info('Clicking login button')
        driver.find_element(By.XPATH, login_button_xpath).click()
        return True
    except TimeoutException:
        logger.info('No login button, skipping login page')
        return False


token_input_xpath = '//input[@id="token"]'
continue_login_button_xpath = '//button[@type="submit" and contains(text(), "Login")]'


def _token(driver: WebDriver, wait: WebDriverWait) -> bool:
    try:
        logger.info('Waiting for continue login button')
        wait.until(expected_conditions.element_to_be_clickable((By.XPATH, continue_login_button_xpath)))

        logger.warning('Found continue login button, waiting for you to enter the token')

        while True:
            token_input = driver.find_element(by=By.XPATH, value=token_input_xpath)
            current_token = token_input.get_attribute('value')
            logger.info(f'Current token: "{current_token}"')
            if len(current_token) > 0:
                logger.warning('Token entered, continuing')
                break
            logger.warning('No token, sleeping')
            time.sleep(1)

        logger.info('Clicking continue login button')
        driver.find_element(By.XPATH, continue_login_button_xpath).click()
        return True
    except TimeoutException:
        logger.info('No continue login button, skipping token page')
        return False


attendance_button_xpath = '//a[@data-test-id="navsidebar-sub-myAttendance"]'


def _attendance(driver: WebDriver, wait: WebDriverWait):
    logger.info('Waiting for attendance button')
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH, attendance_button_xpath)))

    logger.info('Found attendance button, clicking')
    driver.find_element(By.XPATH, attendance_button_xpath).click()


def do_stuff():
    subdomain = config['personio']['subdomain']
    domain = f'https://{subdomain}.personio.de'

    with webdriver.Firefox(service=service, options=firefox_options) as driver:
        wait = WebDriverWait(driver, 5)

        logger.info(f'Opening {domain=} ({subdomain=})')
        driver.get(domain)

        if _login(driver, wait):
            if _token(driver, wait):
                # Sometimes, for whatever reason, the login page is opened again after the token page
                _login(driver, wait)

        _attendance(driver, wait)


if __name__ == '__main__':
    do_stuff()
