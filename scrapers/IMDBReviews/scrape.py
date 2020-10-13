from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("https://www.imdb.com/title/tt0451279/reviews?ref_=tt_ql_3")

elem = driver.find_element_by_id('load-more-trigger')

while 1 == 1:
	try:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)
		elem.click()
		continue
	except:
		print("Done")
		break


nelem = driver.find_elements_by_class_name('expander-icon-wrapper')
for i in nelem:
	try:
		i.click()
		time.sleep(0.2)
	except:
		print("Arrow not needed")
		continue

print("Scraping complete...now attempting a save")

page = driver.page_source
file_ = open('npage.html', 'w')
file_.write(page)
file_.close()
