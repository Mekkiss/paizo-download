import sys
import getpass

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from time import sleep


SHORT_DELAY = 4  # Time to start loading a webpage
DOWNLOAD_DELAY = 10  # Time before Paizo offers the download. Should be at least 5.

def download_files(username, password):
	"""
	Downloads all the files from Paizo's website of the given username
	"""
	driver = webdriver.Firefox()
	driver.implicitly_wait(20) # seconds
	driver.get('http://www.paizo.com')
	signin = driver.find_element_by_link_text('Sign in')
	signin.click()
	sleep(SHORT_DELAY)

	logonform = driver.find_element_by_class_name('bb-content')
	emailbox = logonform.find_element_by_xpath('./table/tbody/tr[1]/td[2]/input')
	emailbox.send_keys(username)
	passbox = logonform.find_element_by_xpath('./table/tbody/tr[2]/td[2]/input')
	passbox.send_keys(password)
	passbox.send_keys(webdriver.common.keys.Keys.RETURN)
	sleep(SHORT_DELAY)

	downloads = driver.find_element_by_link_text('My Downloads')
	downloads.click()
	sleep(SHORT_DELAY)
	dltable = driver.find_element_by_class_name('alternate-rows')
	links = dltable.find_elements_by_xpath('./tbody[2]//td[2]/a')

	dls = []

	for link in dltable.find_elements_by_xpath('.//td[2]/a'):
		dls.append((link.text, link.get_attribute("href")))
		
	for name, link in dls:
		print("Downloading {}".format(name.encode('ascii', 'ignore')))
		driver.get(link)
		sleep(DOWNLOAD_DELAY)

if __name__ == '__main__':
	username = input('Paizo username/email: ')
	password = getpass.getpass()
	if len(username) > 0 and len(password) > 0:
		download_files(username, password)