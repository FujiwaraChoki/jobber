from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from classes.Database import Database
from helpers import _send_email
from termcolor import colored
from typing import List
from uuid import uuid4
from config import *

import markdownify
import time
import re


def _construct_url(job_query, place_query) -> str:
    """
    Creates the URL for the Indeed Search.

    :param job_query:
    :param place_query:
    :return: The URL for the Indeed Search
    """
    base_url = "https://www.indeed.com/jobs?q={}&l={}"

    url = base_url.format(job_query, place_query)

    return url


def _parse_job(url, driver) -> dict:
    """
    Parses a job page and returns an entire job dictionary.

    :param url:
    :return: job dictionary
    """
    job = {}

    print(colored(f"=> Parsing Job: {url}", "blue"))

    # Open
    driver.get(url)
    try:
        job["salary"] = driver.find_element(By.ID, "salaryInfoAndJobType") \
            .find_element(By.TAG_NAME, "span").text or "N/A"
    except:
        job["salary"] = "N/A"

    # Check if benefits exists
    try:
        driver.find_element(By.ID, "benefits")
        job["benefits"] = [
                    benefit.text for benefit in
                    driver.find_element(By.ID, "benefits").find_elements(By.TAG_NAME, "li")
                ] or []
    except:
        job["benefits"] = []

    job_description_div = driver.find_element(By.ID, "jobDescriptionText") or None

    job_description_html = job_description_div.get_attribute("innerHTML") \
        if job_description_div else None
    job["job_description_markdown"] = markdownify.markdownify(job_description_html) \
        if job_description_html else "N/A"

    buttons = driver.find_elements(By.TAG_NAME, "button") or []
    apply_button = None
    for button in buttons:
        try:
            if "apply" in button.text.lower():
                apply_button = button
                break
        except:
            continue

    if apply_button is not None:
        job["apply_button"] = apply_button.get_attribute("href")

    return job


class Indeed:
    def __init__(self, db: Database = None, job_query: str = "", place_query: str = ""):
        """
        Initializes the Indeed Class.
        """
        self.indeed_conf = get_indeed_settings()
        self.chrome_conf = get_chrome_config()
        self.db = db
        self.jobs = []

        # Initialize chrome options
        self.chrome_options = Options()

        if self.chrome_conf["headless"]:
            self.chrome_options.add_argument("--headless")

        # Set user data dir
        self.chrome_options.add_argument(f"--user-data-dir={self.chrome_conf['userDataDir']}")
        self.chrome_options.add_argument(f"--profile-directory={self.chrome_conf['profileName']}")

        # Initialize driver
        self.driver = WebDriver(options=self.chrome_options, \
                                service=Service(ChromeDriverManager().install()))

        url = _construct_url(job_query or self.indeed_conf["jobQuery"], \
                             place_query or self.indeed_conf["placeQuery"])

        self.driver.get(url)

        time.sleep(3)

    def search(self, advanced: bool = False) -> List[dict]:
        """
        Returns a list of available jobs.

        :param advanced: If True, will parse the job page for more information.

        :return: List of available jobs, in dictionaries.
        """
        driver = self.driver

        mosaic_job_results = driver.find_element(By.ID, "mosaic-jobResults")

        jobs_list = mosaic_job_results.find_element(By.XPATH, \
            "/html/body/main/div/div[2]/div/div[5]/div/div[1]/div[5]/div/ul")

        if jobs_list:
            # Get all list items.
            jobs = jobs_list.find_elements(By.TAG_NAME, "li")
            cmpny_index = 0

            for job in jobs:
                try:
                    job_h2 = job.find_element(By.TAG_NAME, "h2")
                    job_url = job_h2.find_element(By.CLASS_NAME, "jcs-JobTitle") \
                        .get_attribute("href")
                    job_title = job_h2.find_element(By.TAG_NAME, "span") \
                        .get_attribute("title")
                    spans = driver.find_elements(By.CLASS_NAME, "company_location")
                    company_name = spans[cmpny_index].text if len(spans) > 0 else None
                    company_location = spans[cmpny_index + 1].text if len(spans) > 1 else None
                    print(colored(f"=> Found Job Location: {company_location}", "green"))

                    job_id = str(uuid4())

                    if self.db:
                        self.db.insert_job({
                            "id": job_id,
                            "url": job_url,
                            "title": job_title,
                            "company": company_name,
                            "location": company_location
                        })

                    cmpny_index += 2
                except:
                    continue

                self.jobs.append({
                    "id": job_id,
                    "url": job_url,
                    "title": job_title,
                    "company": company_name,
                    "location": company_location
                })

            if advanced:
                for job in self.jobs:
                    parsed = _parse_job(job["url"], driver)

                    job["salary"] = parsed["salary"]
                    job["benefits"] = parsed["benefits"]
                    job["job_description_markdown"] = parsed["job_description_markdown"]
                    job["apply_button"] = parsed["apply_button"]

                    if self.db:
                        self.db.update_job({
                            "id": job["id"],
                            "title": job["title"],
                            "location": job["location"],
                            "salary": job["salary"],
                            "benefits": job["benefits"],
                            "job_description_markdown": job["job_description_markdown"],
                            "apply_button": job["apply_button"],
                            "url": job["url"]
                        })

        else:
            print(colored("=> No Jobs List found.", "red"))

        return self.jobs

    def apply(self, job_id: str, cover_letter: str, resume: str) -> bool:
        """
        Applies to a job.

        :param job_id: The job ID to apply to.
        :return: True if successful, False if not.
        """
        job = self.db.get_job(job_id)

        if job:
            driver = self.driver

            driver.get(job["url"])

            time.sleep(3)

            # Find all anchors
            anchors = driver.find_elements(By.TAG_NAME, "a")

            # Find emails
            emails = []

            for anchor in anchors:
                if re.match(regexp, anchor.text):
                    emails.append(anchor.text)

            if len(emails) > 0:
                print(colored(f"\t=> Found Email: {emails[0]}", "green"))

                return True
            else:
                # Try and find all URLs
                urls = []

                for anchor in anchors:
                    if anchor.get_attribute("href"):
                        urls.append(anchor.get_attribute("href"))

                if len(urls) > 0:
                    urls = list(set(urls))
                    # Go to each URL and try to find an email
                    for url in urls:
                        driver.get(url)

                        time.sleep(3)

                        anchors = driver.find_elements(By.TAG_NAME, "a")
                        regexp = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

                        for anchor in anchors:
                            if re.match(regexp, anchor.text):
                                emails.append(anchor.text)

                        if len(emails) > 0:
                            print(colored(f"\t=> Found Email: {emails[0]}", "green"))

                            for mail in emails:
                                _send_email(mail, job["title"], cover_letter, resume)

                            return True
                        else:
                            continue

        return False
