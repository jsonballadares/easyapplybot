from logging import exception
from warnings import catch_warnings
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import json,time,random
import math
import string


class EasyApplyLinkedin:
    def __init__(self,data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome(data['driver_path'])

    def login_linkedin(self):
        random_time = random.uniform(3.5, 4.9)
        time.sleep(random_time)
        #make driver go to linkedin login page
        self.driver.get('https://www.linkedin.com/login')
        #type email and password and click enter
        username_element = self.driver.find_element_by_css_selector('#username')
        username_element.clear()
        username_element.send_keys(self.email)
        password_element = self.driver.find_element_by_css_selector('#password')
        password_element.clear()
        password_element.send_keys(self.password)
        password_element.send_keys(Keys.RETURN)
        random_time = random.uniform(3.5, 4.9)
        time.sleep(random_time)

    def job_search(self):
        #go to job section
        self.driver.get(r'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2&f_WRA=true&geoId=103644278&keywords=software%20engineer&location=United%20States')
        random_time = random.uniform(3.5, 4.9)
        time.sleep(random_time)

    def find_offers(self):
        random_time = random.uniform(3.5, 4.9)
        time.sleep(random_time)
        page_urls = self.get_page_urls()
        IDs = set()
        for page_url in page_urls:
            try:
                self.driver.get(page_url)
                random_time = random.uniform(3.5, 4.9)
                time.sleep(random_time)
                scroll_results = self.driver.find_element_by_class_name("jobs-search-results")
                for i in range(300, 3000, 100):
                    self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scroll_results)
                random_time = random.uniform(3.5, 4.9)
                time.sleep(random_time)
                job_links = self.driver.find_elements_by_xpath('//div[@data-job-id]')
                for job_link in job_links:
                    children = job_link.find_elements_by_xpath('.//a[@data-control-name]')
                    for child in children:
                        temp = job_link.get_attribute("data-job-id")
                        jobID = temp.split(":")[-1]
                        IDs.add(int(jobID))  
            except Exception as e:
                print(e)
                continue
        print(str(len(IDs)))
        print(IDs)
        self.one_click_apply(IDs)         

    def one_click_apply(self,IDs):
        for id in IDs:
            self.driver.get(self.get_job_page_url(id))
            random_time = random.uniform(3.5, 4.9)
            time.sleep(random_time)
            try:
                easy_apply_button = self.driver.find_element_by_xpath('//button[contains(@class, "jobs-apply")]/span[1]')
                easy_apply_button.click()
                random_time = random.uniform(3.5, 4.9)
                time.sleep(random_time)
                submit_application_button = self.driver.find_element_by_xpath('/html/body/div[3]/div/div/div[2]/div/form/footer/div[3]/button')
                random_time = random.uniform(3.5, 4.9)
                time.sleep(random_time)
                submit_application_button.click()
                random_time = random.uniform(3.5, 4.9)
                time.sleep(random_time)
            except Exception as e:
                print(e)

    def get_job_page_url(self, job_id):
        return 'https://www.linkedin.com/jobs/view/' + str(job_id)

    def get_page_urls(self):
        amount_of_results = self.driver.find_element_by_css_selector('body > div.application-outlet > div.authentication-outlet > div.job-search-ext > div > div > section.jobs-search__left-rail > div > header > div.jobs-search-results-list__title-heading > small')
        amount_of_results = amount_of_results.text.split()[0]
        print(f'amount_of_results: {amount_of_results}')
        page_count = int(math.ceil(int(amount_of_results) / 25))
        print(f'page count: ' + str(page_count))
        base_url = self.driver.current_url + '&start='
        page_urls = []
        while page_count > 0:
            page_urls.append(base_url + str((page_count - 1) * 25))
            page_count = page_count - 1
        return page_urls

if __name__ == "__main__":
    with open('data/config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.login_linkedin()
    bot.job_search()
    bot.find_offers()
    bot.driver.close()