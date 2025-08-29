import json
import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient

# Load LinkedIn credentials
with open("data/config.json", "r") as f:
    config = json.load(f)
linkedin_username = config.get("username")
linkedin_password = config.get("password")

if not linkedin_username or not linkedin_password:
    raise ValueError("LinkedIn username or password missing in data/config.json")

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Change if using Docker network
db = client["linkedin_jobs"]
jobs_collection = db["jobs"]

# Setup Chrome options
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # Uncomment for headless mode
service = Service()  # Add path to chromedriver if needed
driver = webdriver.Chrome(service=service, options=options)

def human_scroll(element, pause_range=(0.5, 1.2), steps=10):
    """Scroll down an element gradually to simulate human behavior."""
    for _ in range(steps):
        driver.execute_script(
            "arguments[0].scrollTop += arguments[0].offsetHeight / arguments[1];",
            element,
            steps,
        )
        time.sleep(random.uniform(*pause_range))

try:
    print("Opening LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(linkedin_username)
    driver.find_element(By.ID, "password").send_keys(linkedin_password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "global-nav-search"))
    )

    search_url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=United%20States&f_AL=true&f_WT=2"
    driver.get(search_url)

    results_div = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list__subtitle"))
    )
    results_text = results_div.text.strip()
    results_number = int("".join(ch for ch in results_text if ch.isdigit()))
    print(f"Total results: {results_number}")

    max_results = 100  # Limit for demo purposes
    total_pages = (max_results // 25) + 1
    print(f"Total pages: {total_pages}")

    for page in range(total_pages):
        start = page * 25
        url = f"{search_url}&start={start}"
        print(f"Visiting page {page+1}/{total_pages}: {url}")
        driver.get(url)

        job_list_ul = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//ul[li[@data-occludable-job-id]]"))
        )
        human_scroll(job_list_ul, steps=8)

        job_items = job_list_ul.find_elements(By.CSS_SELECTOR, "li[data-occludable-job-id]")
        print(f"Found {len(job_items)} jobs on this page.")

        for job_item in job_items:
            try:
                job_id_str = job_item.get_attribute("data-occludable-job-id")
                if not job_id_str or not job_id_str.isdigit():
                    continue
                job_id = int(job_id_str)

                # Skip if job_id already in DB
                if jobs_collection.find_one({"job_id": job_id}):
                    continue

                # Check if already applied
                try:
                    applied_message = job_item.find_element(By.CSS_SELECTOR, "span.artdeco-inline-feedback__message")
                    applied_text = applied_message.text.strip()
                    if "Applied" in applied_text:
                        print(f"Skipping already applied job {job_id}: {applied_text}")
                        continue
                except:
                    applied_text = ""

                job_url = f"https://www.linkedin.com/jobs/view/{job_id}"
                company = ""
                title = ""
                try:
                    company = job_item.find_element(By.CSS_SELECTOR, ".base-search-card__subtitle").text.strip()
                    title = job_item.find_element(By.CSS_SELECTOR, ".base-search-card__title").text.strip()
                except:
                    pass

                job_doc = {
                    "job_id": job_id,
                    "job_url": job_url,
                    "company": company,
                    "title": title,
                    "applied_status": False,
                    "applied_text": applied_text,
                    "last_checked": datetime.utcnow(),
                }

                jobs_collection.insert_one(job_doc)
                print(f"Saved job {job_id} to MongoDB: {title} at {company}")

            except Exception as e:
                print(f"Error processing job item: {e}")

        time.sleep(random.uniform(3, 7))

finally:
    print("Closing browser.")
    driver.quit()
