from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import json,time,random


with open('data/config.json') as config_file:
   data = json.load(config_file)


url_login = r'https://www.linkedin.com/login'
url_job_search = r'https://www.linkedin.com/jobs/search/?currentJobId=2514734378&f_AL=true&f_E=2&f_WRA=true&geoId=103644278&keywords=software%20engineer&location=United%20States'

webdriver = webdriver.Chrome(data['driver_path'])

webdriver.get(url_login)
username_element = webdriver.find_element_by_css_selector('#username')
username_element.clear()
username_element.send_keys(data['email'])
password_element = webdriver.find_element_by_css_selector('#password')
password_element.clear()
password_element.send_keys(data['password'])
password_element.send_keys(Keys.RETURN)

webdriver.get(url_job_search)
random_time = random.uniform(3.5, 4.9)
time.sleep(random_time)

amount_of_results = webdriver.find_element_by_css_selector('body > div.application-outlet > div.authentication-outlet > div.job-search-ext > div > div > section.jobs-search__left-rail > div > header > div.jobs-search-results-list__title-heading > small')

print(f'amount_of_results: {amount_of_results.text}')

scrollresults = webdriver.find_element_by_class_name("jobs-search-results")

for i in range(300, 3000, 100):
    webdriver.execute_script("arguments[0].scrollTo(0, {})".format(i), scrollresults)


job_links = webdriver.find_elements_by_xpath('//div[@data-job-id]')

IDs = []
for job_link in job_links:
    children = job_link.find_elements_by_xpath('.//a[@data-control-name]')
    for child in children:
        temp = job_link.get_attribute("data-job-id")
        jobID = temp.split(":")[-1]
        IDs.append(int(jobID))
        

print(IDs)

webdriver.close()