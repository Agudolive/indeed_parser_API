import csv
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.indeed.fr/jobs?q=data+engineer"

# No need to manually add the chrome driver here, ChromeDriverManager will do it automatically
driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get(URL)

def check_exists_by_class_name(class_name, item, get_value):
    try:
        value = item.find_element_by_class_name(class_name).text
    except NoSuchElementException:
        return "null" if get_value else False
    return value if get_value else True

# Indeed.com will reprocess the request and update results each time you refresh or go to the next/previous page
# Some cards you found on the first page may appear again on the second or third page etc...
# That's why I had to create a "Set" to check if the cards have already been saved
# The Set is not the most memory efficient data structure but its speed efficiency
# and the low number of keys we have here makes it the best for the situation

saved_offers = set()

# I open my CSV file here as I wont use cache and write in the file immediatly after reading each job offer
with open("job_offers.csv", "w", newline="") as file:

    writer = csv.writer(file)

    # I write the header of my CSV file
    writer.writerow(
        [
            "job_name",
            "company",
            "location",
            "department",
            "easy_apply",
            "remote",
            "salary",
            "urgently_hiring",
            "company_rating",
        ]
    )

    # I want to scrap 20 pages of job offer
    for i in range(20):

        # On each page, I start to get all the elements with the class "jobsearch-SerpJobCard"
        # They are individuals job offer cards
        job_offer_container = driver.find_elements_by_class_name("jobsearch-SerpJobCard")

        # I loop through all the cards of the page
        for job_offer_item in job_offer_container:

            # I retrieve the job offer ID, it will help me to avoid duplicates entries
            job_offer_id = job_offer_item.get_attribute("id")

            # If the card is not already saved, I save it
            if job_offer_id not in saved_offers:

                saved_offers.add(job_offer_id)

                # I retrieve all the data I need
                job_name = job_offer_item.find_element_by_xpath(".//h2[@class='title']/a").text

                # I decided not to clean data about salary. These data comes in multiple formats : hourly, monthly, annualy, salary range, strict salary...
                # Implicitly, it means that there is differents contract types (Freelance contracts are hourly and daily, long term contracts are annualy or monhly...)
                # In real conditions, the way to handle these data must be discussed beforhand because it can lead to misunderstanding
                # (for example : freelance contracts can last only a few days, therefore, translating hourly to annual salary can be odd)
                salary = check_exists_by_class_name("salary", job_offer_item, True)
                company = check_exists_by_class_name("company", job_offer_item, True)
                location = check_exists_by_class_name("location", job_offer_item, True)

                # I use regex to parse the string containing "location (department)" to split it into "location" and "department"
                regex_match = re.search(r'(.*)(\s)(\([0-9]{1,2}\))', location)

                if regex_match:
                    location = regex_match.group(1)
                    department = int(regex_match.group(3)[1:-1])
                else:
                    department = 'unknown'

                company_rating = check_exists_by_class_name("ratingsContent", job_offer_item, True)

                remote = check_exists_by_class_name("remote", job_offer_item, False)
                easy_apply = check_exists_by_class_name("indeedApply", job_offer_item, False)
                urgently_hiring = check_exists_by_class_name("urgentlyHiring", job_offer_item, False)

                # Here I tranform the company rating to float in order to use it as a filter in the futur
                if company_rating != 'null':
                    company_rating = company_rating.replace(',', '.')
                    company_rating = float(company_rating)

                # And I write the line in my file
                writer.writerow(
                    [
                        job_name,
                        company,
                        location,
                        department,
                        easy_apply,
                        remote,
                        salary,
                        urgently_hiring,
                        company_rating,
                    ]
                )

        # I save the current url
        current_url = driver.current_url

        # I locate the "next page" button and click it
        next_page_button = driver.find_element_by_xpath(
            "//ul[@class='pagination-list']/li[last()]/a"
        )

        # I use excute_script and not click() because the button can be hidden by some GDPR or cookies banner
        driver.execute_script("arguments[0].click();", next_page_button)

        # I wait until the URL has changed to be sure no to process data I already retrieved (especially when network is slow)
        WebDriverWait(driver, 15).until(EC.url_changes(current_url))

driver.quit()
