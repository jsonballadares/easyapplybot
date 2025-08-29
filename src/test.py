import json
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Load credentials from data/config.json
with open("data/config.json", "r") as f:
    config = json.load(f)
linkedin_username = config.get("username")
linkedin_password = config.get("password")

if not linkedin_username or not linkedin_password:
    raise ValueError("LinkedIn username or password missing in data/config.json")

# Setup Chrome options and driver
options = Options()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # Uncomment for headless

service = Service()  # Add path to chromedriver if needed
driver = webdriver.Chrome(service=service, options=options)

def human_scroll(element, pause_range=(0.5, 1.2), steps=10):
    """Scroll down an element gradually to simulate human behavior."""
    for _ in range(steps):
        driver.execute_script(
            "arguments[0].scrollTop += arguments[0].offsetHeight / arguments[1];", element, steps
        )
        time.sleep(random.uniform(*pause_range))

try:
    print("Opening LinkedIn login page...")
    driver.get("https://www.linkedin.com/login")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
    print("Entering username...")
    driver.find_element(By.ID, "username").send_keys(linkedin_username)

    print("Entering password...")
    driver.find_element(By.ID, "password").send_keys(linkedin_password)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    print("Navigating to job search page...")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "global-nav-search")))

    search_url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer&location=United%20States&f_AL=true&f_WT=2"
    driver.get(search_url)

    # Grab total results
    results_div = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list__subtitle"))
    )
    results_text = results_div.text.strip()
    results_number = int("".join(ch for ch in results_text if ch.isdigit()))
    print(f"Total results: {results_number}")
    max = 1
    total_pages = (max // 25) + 1  # For demo limit
    print(f"Total pages: {total_pages}")

    job_ids = []

    for page in range(total_pages):
        start = page * 25
        url = f"{search_url}&start={start}"
        print(f"Visiting page {page+1}/{total_pages}: {url}")
        driver.get(url)

        # Wait for the jobs list <ul>
        job_list_ul = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//ul[li[@data-occludable-job-id]]"))
        )

        # Scroll gradually to load all jobs
        human_scroll(job_list_ul, steps=8)

        # Collect job IDs
        job_items = job_list_ul.find_elements(By.CSS_SELECTOR, "li[data-occludable-job-id]")
        print(f"Collected job items: ({len(job_items)})")

        for job_item in job_items:
            try:
                job_id_str = job_item.get_attribute("data-occludable-job-id")
                if job_id_str and job_id_str.isdigit() and int(job_id_str) not in job_ids:
                    job_ids.append(int(job_id_str))
            except Exception as e:
                print(f"Skipping a stale job item: {e}")

        print(f"Collected job IDs so far ({len(job_ids)}): {job_ids}")
        time.sleep(random.uniform(3, 7))

    print(f"Final collected job IDs ({len(job_ids)}): {job_ids}")

    # Visit each job page and click Easy Apply if available
    for job_id in job_ids:
        job_url = f"https://www.linkedin.com/jobs/view/{job_id}"
        print(f"Opening job: {job_url}")
        driver.get(job_url)

        try:
            # Wait for Easy Apply container
            easy_apply_container = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-apply-button--top-card"))
            )

            easy_apply_btn = easy_apply_container.find_element(By.ID, "jobs-apply-button-id")
            driver.execute_script("arguments[0].scrollIntoView(true);", easy_apply_btn)
            ActionChains(driver).move_to_element(easy_apply_btn).perform()
            time.sleep(random.uniform(1, 2))

            print(f"Clicking Easy Apply for job {job_id}")
            try:
                easy_apply_btn.click()
            except:
                # fallback to JS click
                driver.execute_script("arguments[0].click();", easy_apply_btn)
            time.sleep(random.uniform(2, 4))

            # Loop through Next until Review appears
            while True:
                # Check for validation errors / feedback messages
                feedback_elements = driver.find_elements(By.CSS_SELECTOR, "span.artdeco-inline-feedback__message")
                if feedback_elements:
                    print(f"Found {len(feedback_elements)} validation errors, skipping Next for now.")
                    for fb in feedback_elements:
                        try:
                            question_label = fb.find_element(
                                By.XPATH, "./ancestor::div[contains(@class,'fb-dash-form-element')]//label"
                            )
                            question_text = question_label.text.strip()
                        except:
                            question_text = "Unknown question"
                        feedback_text = fb.text.strip()
                        print(f"  - Question: {question_text} | Feedback: {feedback_text}")
                    break

                try:
                    review_btn = driver.find_element(
                        By.CSS_SELECTOR, "button[data-live-test-easy-apply-review-button]"
                    )
                    print("Review button found, clicking it...")
                    driver.execute_script("arguments[0].scrollIntoView(true);", review_btn)
                    ActionChains(driver).move_to_element(review_btn).perform()
                    time.sleep(random.uniform(1, 2))
                    review_btn.click()
                    time.sleep(random.uniform(2, 4))
                    break
                except:
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, "button[data-easy-apply-next-button]")
                        print("Clicking Next button...")
                        driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                        ActionChains(driver).move_to_element(next_btn).perform()
                        time.sleep(random.uniform(1, 2))
                        next_btn.click()
                        time.sleep(random.uniform(1.5, 3))
                    except:
                        print("No more Next button, moving to next job.")
                        break

            # Click Follow Company checkbox if present
            try:
                follow_checkbox = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='follow-company-checkbox']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", follow_checkbox)
                follow_checkbox.click()
                print("Clicked follow company checkbox.")
                time.sleep(random.uniform(0.5, 1.5))
            except:
                print("Follow company checkbox not found.")

            # Click Submit button
            try:
                submit_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-live-test-easy-apply-submit-button]"))
                )
                print("Clicking Submit button...")
                submit_btn.click()
                print(f"Job {job_id} submitted successfully!")
                time.sleep(random.uniform(2, 4))
            except:
                print("Submit button not found or clickable.")

        except Exception as e:
            print(f"No Easy Apply button for job {job_id}: {e}")

        time.sleep(random.uniform(3, 6))

finally:
    print("Closing browser.")
    driver.quit()
