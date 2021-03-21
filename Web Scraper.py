# Source:
# https://towardsdatascience.com/selenium-tutorial-scraping-glassdoor-com-in-10-minutes-3d0915c6d905
# https://github.com/arapfaik/scraping-glassdoor-selenium

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from selenium import webdriver
import time
import pandas as pd
import os


def get_jobs(url, num_jobs, verbose, path, slp_time):
    # Initializing the webdriver
    options = webdriver.ChromeOptions()

    # Uncomment the line below if you'd like to scrape without a new Chrome window every time.
    # options.add_argument('headless')

    # Change the path to where chromedriver is in your home folder.
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.set_window_size(1120, 1000)

    driver.get(url)
    jobs = []

    while len(jobs) < num_jobs:
        # If true, should be still looking for new jobs.
        
        # Test for the "Sign Up" prompt and get rid of it.
        # First we click a vacancy which makes the sign up prompt pop up.
        try:
            driver.find_element_by_class_name('react-job-listing').click()
        except:
            print('Couldn\'t trigger sign up prompt.')
            pass
        time.sleep(.1)
        try:
            # Closing th sign up prompt by clicking on the X
            driver.find_element_by_css_selector('[alt="Close"]').click()
            print('Closing sign up prompt worked')
        except NoSuchElementException:
            print('Closing sign up prompt failed')
            pass

        # Disable cookie prompt
        try:
            # TODO: open cookie prompt and reject cookies?
            # driver.find_element_by_class_name('cookie-setting-link').click()
            # sleep(5)
            # # Scroll down
            # driver.execute_script('var el=document.getElementById("ot-content");console.log("Test");el.scrollTo(0, el.scrollHeight);')
            # # Click on "Confirm My Choices"
            # driver.find_element_by_class_name('save-preference-btn-handler').click()
            driver.find_element_by_id('onetrust-accept-btn-handler').click()
            print('Accepted cookies!')
        except:
            print('Couldn\'t remove cookie bar')


        # Going through each job in this page
        job_buttons = driver.find_elements_by_class_name('react-job-listing') 
        for job_button in job_buttons:

            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break
            try:
                job_button.click()
                time.sleep(1)
                collected_successfully = False
            except ElementNotInteractableException:
                print("Click Failed")
                pass
            except ElementClickInterceptedException:
                # Scroll down and try again
                driver.execute_script('var el=document.getElementById("MainCol");el.scrollBy(0, 100);')
                try:
                    job_button.click()
                    time.sleep(1)
                    collected_succesfully = False
                except:
                    print("Click Failed")
                    pass

            while not collected_successfully:
                try:
                    company_name = driver.find_element_by_css_selector('div.css-87uc0g.e1tk4kwz1').text
                    location = driver.find_element_by_css_selector('div.css-56kyx5.e1tk4kwz5').text
                    job_title = driver.find_element_by_css_selector('div.css-1vg6q84.e1tk4kwz4').text
                    job_description = driver.find_element_by_css_selector('div.jobDescriptionContent.desc').text
                    collected_successfully = True
                except:
                    time.sleep(5)

            # Going to salary tab
            try:
                driver.find_element_by_css_selector('[data-tab-type="salary"]').click()
                try:
                    # TODO: fix salary estimate (not sure if it's an issue with css selector or if we're on the wrong page)
                    salary_estimate = driver.find_element_by_css_selector('div.css-opqngn.e14v05921').text
                except NoSuchElementException:
                    salary_estimate = -1
            except ElementClickInterceptedException:
                # Can't click on tab, scroll down and try again
                driver.execute_script('var el=document.getElementById("JDCol");el.scrollTo(0, 300);')
                try:
                    driver.find_element_by_css_selector('[data-tab-type="salary"]').click()
                    salary_estimate = driver.find_element_by_css_selector('div.css-opqngn.e14v05921').text
                except:
                    # TODO: change "not found" value from -1 to something else?
                    salary_estimate = -1
            except:
                salary_estimate = -1

            try:
                rating = driver.find_element_by_css_selector('span[data-test="detailRating"]').text
                company_name = company_name.removesuffix('\n' + rating)
            except NoSuchElementException:
                rating = -1

            # Printing for debugging
            if verbose:
                print("Job Title: {}".format(job_title))
                print("Salary Estimate: {}".format(salary_estimate))
                print("Job Description: {}".format(job_description[:500]))
                print("Rating: {}".format(rating))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))

            # Going to the Company tab...
            # clicking on this:
            # <div class="tab" data-tab-type="overview"><span>Company</span></div>
            try:
                driver.find_element_by_css_selector('[data-tab-type="overview"]').click()
            except ElementClickInterceptedException:
                # Can't click on tab, scroll down and try again
                driver.execute_script('var el=document.getElementById("JDCol");el.scrollTo(0, 300);')
                try:
                    driver.find_element_by_css_selector('[data-tab-type="overview"]').click()
                except:  # Rarely, some job postings do not have the "Company" tab.
                    headquarters = -1
                    size = -1
                    founded = -1
                    type_of_ownership = -1
                    industry = -1
                    sector = -1
                    revenue = -1
                    competitors = -1
            except NoSuchElementException:  # Rarely, some job postings do not have the "Company" tab.
                headquarters = -1
                size = -1
                founded = -1
                type_of_ownership = -1
                industry = -1
                sector = -1
                revenue = -1
                competitors = -1

            try:
                # HEADQUARTERS info doesn't seem to be available anymore
                # Also the below structure is inaccurate
                # <div class="infoEntity">
                #    <label>Headquarters</label>
                #    <span class="value">San Francisco, CA</span>
                # </div>
                headquarters = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Headquarters"]/following-sibling::*').text
            except NoSuchElementException:
                headquarters = -1

            try:
                size = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Size"]/following-sibling::*').text
                if size == 'Unknown':
                    size = -1
            except NoSuchElementException:
                size = -1

            try:
                founded = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Founded"]/following-sibling::*').text
            except NoSuchElementException:
                founded = -1

            try:
                type_of_ownership = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Type"]/following-sibling::*').text
            except NoSuchElementException:
                type_of_ownership = -1

            try:
                industry = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Industry"]/following-sibling::*').text
            except NoSuchElementException:
                industry = -1

            try:
                sector = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Sector"]/following-sibling::*').text
            except NoSuchElementException:
                sector = -1

            try:
                revenue = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Revenue"]/following-sibling::*').text
            except NoSuchElementException:
                revenue = -1

            try:
                # TODO: COMPETITORS doesn't seem to be available anymore
                competitors = driver.find_element_by_xpath('.//div[@id="EmpBasicInfo"]/div[1]/div/div/span[text()="Competitors"]/following-sibling::*').text
            except NoSuchElementException:
                competitors = -1
            
            if verbose:
                print("Headquarters: {}".format(headquarters))
                print("Size: {}".format(size))
                print("Founded: {}".format(founded))
                print("Type of Ownership: {}".format(type_of_ownership))
                print("Industry: {}".format(industry))
                print("Sector: {}".format(sector))
                print("Revenue: {}".format(revenue))
                print("Competitors: {}".format(competitors))
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"Job Title": job_title,
                         "Salary Estimate": salary_estimate,
                         "Job Description": job_description,
                         "Rating": rating,
                         "Company Name": company_name,
                         "Location": location,
                         "Headquarters": headquarters,
                         "Size": size,
                         "Founded": founded,
                         "Type of ownership": type_of_ownership,
                         "Industry": industry,
                         "Sector": sector,
                         "Revenue": revenue,
                         "Competitors": competitors})
            # add job to jobs

        # Clicking on the "next page" button
        try:
            driver.find_element_by_css_selector('[data-test="pagination-next"]').click()
            # Let the page load. Change this number based on your internet speed.
            # Or, wait until the webpage is loaded, instead of hardcoding it.
            print('Next page...')
            time.sleep(slp_time)
        except ElementClickInterceptedException:
            # Scroll down and try again
            driver.execute_script('var el=document.getElementById("MainCol");el.scrollBy(0, 200);')
            try:
                driver.find_element_by_css_selector('[data-test="pagination-next"]').click()
                print('Next page...')
                time.sleep(slp_time)
            except:
                print('Scraping terminated before reaching target number of jobs. Needed {}, got {}.'.format(num_jobs, len(jobs)))
                break
        except NoSuchElementException:
            if num_jobs < len(jobs):
                print('Scraping terminated before reaching target number of jobs. Needed {}, got {}.'.format(num_jobs, len(jobs)))
            else:
                print('Succesfully scraped {} jobs!'.format(len(jobs)))
            break
    # Convert the dictionary to pandas DataFrame and return it
    return pd.DataFrame(jobs)


keyword = "Data Science"
url1 = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=" + keyword + "&sc.keyword=" + keyword + "&locT=&locId=&jobType= "

url2 = "https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=&locT=N&locId=178&jobType=&context=Jobs&sc.keyword=&dropdown=0"

Data = get_jobs(url2, 100, False, os.path.join(os.path.dirname(__file__), 'chromedriver'), 5)

Data.to_csv(os.path.join(os.path.dirname(__file__), 'JobData.csv'))