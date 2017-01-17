import sys
import getpass
import argparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from time import sleep
from datetime import datetime

import parsedatetime as pdt

SHORT_DELAY = 10  # Time to start loading a webpage
DOWNLOAD_DELAY = 10  # Time before Paizo offers the download. Should be at least 5.

def download_files(username, password, download_all=False):
	"""
	Downloads all the files from Paizo's website of the given username
	"""
	
	cal = pdt.Calendar()
	now = datetime.now()
	
	fp = webdriver.FirefoxProfile()
	fp.set_preference("browser.download.manager.showWhenStarting",False)
	fp.set_preference("browser.download.folderList",2)
	fp.set_preference("browser.download.dir", "C:\\temp\\")
	fp.set_preference("browser.download.downloadDir", "C:\\temp\\")
	fp.set_preference("browser.download.defaultFolder", "C:\\temp\\")
	fp.set_preference('browser.helperApps.neverAsk.saveToDisk',"application/zip")
	fp.set_preference("permissions.default.image", 2)
	
	driver = webdriver.Firefox(fp)
	driver.implicitly_wait(20) # seconds
	driver.get('http://www.paizo.com')
	signin = driver.find_element_by_link_text('Sign in')
	signin.click()
	sleep(SHORT_DELAY)
	try:
		logonform = driver.find_element_by_class_name('bb-content')
	except exceptions.InvalidSelectorException:
		print("Taking a bit long to load...")
		sleep(6 * SHORT_DELAY)
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

	dls = []
	for body in dltable.find_elements_by_xpath('.//tbody'):
		if body.find_element_by_xpath('./tr/td').get_attribute("colspan") == '5':
			continue  # This is the title.
		for row in body.find_elements_by_xpath('./tr'):
			lastdl = row.find_element_by_xpath('./td[3]').text
			if lastdl == 'never':
				lastdl_time = datetime(1970, 1, 1)
			else:
				lastdl_time = cal.parseDT(lastdl, now)[0]
			lastupdate = cal.parseDT(row.find_element_by_xpath('./td[4]').text)[0]
			added = cal.parseDT(row.find_element_by_xpath('./td[5]').text)[0]
			print('{} - {} - {} - {}'.format(
				row.find_element_by_xpath('./td[2]/a').text.encode('ascii', 'ignore'),
				lastdl_time, lastupdate, added))
			if lastdl_time < lastupdate or download_all:
				link = row.find_element_by_xpath('./td[2]/a')
				dls.append((link.text, link.get_attribute("href")))


	
	for name, link in dls:
		print("Downloading {}".format(name.encode('ascii', 'ignore')))
		driver.get(link)
		sleep(DOWNLOAD_DELAY)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Batch download from Paizo account")
	parser.add_argument('-u', '--username')
	parser.add_argument('-a', '--all', action='store_true', help="Download all files, not just new ones")
	args = parser.parse_args()
	username = args.username
	if username is None:
		username = input('Paizo username/email: ')
	password = getpass.getpass()
	if len(username) > 0 and len(password) > 0:
		download_files(username, password, args.all)