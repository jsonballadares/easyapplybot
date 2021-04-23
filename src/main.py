from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json,time,random


class EasyApplyLinkedin:
    def __init__(self,data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Chrome(data['driver_path'])

    def login_linkedin(self):
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

    def job_search(self):
        #go to job section
        self.driver.get(r'https://www.linkedin.com/jobs/search/?f_AL=true&f_E=2&f_WRA=true&geoId=103644278&keywords=software%20engineer&location=United%20States')
    
    def find_offers(self):
        random_time = random.uniform(3.5, 4.9)
        time.sleep(random_time)
        amount_of_results = self.driver.find_element_by_xpath('/html/body/div[6]/div[3]/div[3]/div/div/section[1]/div/header/div[1]/small')
        print(f'amount_of_results: {amount_of_results.text}')
        scroll_results = self.driver.find_element_by_class_name("jobs-search-results")
        for i in range(300, 3000, 100):
            self.driver.execute_script("arguments[0].scrollTo(0, {})".format(i), scroll_results)
        job_links = self.driver.find_elements_by_xpath('//div[@data-job-id]')
        IDs = []
        for job_link in job_links:
            children = job_link.find_elements_by_xpath('.//a[@data-control-name]')
            for child in children:
                temp = job_link.get_attribute("data-job-id")
                jobID = temp.split(":")[-1]
                IDs.append(int(jobID))
        print(IDs)



    def get_job_page_url(self, job_id):
        return 'https://www.linkedin.com/jobs/view/' + str(job_id)

    
        


if __name__ == "__main__":
    with open('data/config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.login_linkedin()
    bot.job_search()
    bot.find_offers()
    bot.driver.close()