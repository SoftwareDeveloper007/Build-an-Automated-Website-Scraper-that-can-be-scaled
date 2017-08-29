from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import threading, time, csv, os, sys

SLEEP_TIME = 0.5

class mainScraper():
    def __init__(self, id = 'Your Email Address', pw='Your Password'):
        self.input_data = []
        self.output_data = []
        self.start_url = 'https://www.yelp.com/'
        self.drivers = []

    def startScraping(self):
        self.inputFile()

        self.threads = []
        self.max_threads = 1

        for i in range(self.max_threads):
            self.drivers.append(None)

        logTxt = "------------------------ Scraping started on! ------------------------"
        print(logTxt)

        while self.threads or self.input_data or self.drivers:
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)

            while len(self.threads) < self.max_threads and self.input_data and self.drivers:
                thread = threading.Thread(target=self.extractDetails)
                thread.setDaemon(True)
                thread.start()
                self.threads.append(thread)

    def inputFile(self):
        try:
            input_csv = open('Data/split_cq.csv', 'r')
            reader = csv.reader(input_csv)

            for i,row in enumerate(reader):
                if i==0:
                    continue
                self.input_data.append([i, row[0]])
            self.input_data.reverse()
            logTxt = 'Input csv file successfully'
            print(logTxt)
        except:
            logTxt = 'Warning1: There is no csv file. Please input it'
            print(logTxt)

    def extractDetails(self):

        yelp_name = 'none'
        yelp_url = ''
        yelp_reviews = ''
        yelp_friends = ''
        yelp_city = ''
        yelp_elite = ''

        email = self.input_data.pop()[1]

        logTxt = "+-+-+-+-+-+-+-+- {0} +-+-+-+-+-+-+-+-\n".format(email)

        driver = self.drivers.pop()

        if driver is None:
            driver = webdriver.Chrome(os.getcwd() + '/WebDriver/chromedriver.exe')
            driver.maximize_window()
            driver.get(self.start_url)

            try:
                login = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "a.header-nav_link.header-nav_link--log-in.js-analytics-click"))
                )
                login.click()
                login = WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form#ajax-login > input#email"))
                )
                password = driver.find_element_by_css_selector('form#ajax-login > input#password')
                submit_btn = driver.find_element_by_css_selector('form#ajax-login > button.submit')

                login.send_keys(id)
                time.sleep(5)
                password.send_keys(pw)
                time.sleep(5)
                submit_btn.click()
                logTxt = logTxt + '\tLogin Successfully!\n'

                self.handle = driver.current_window_handle
                self.url = driver.current_url

                usr_btn = WebDriverWait(driver, 100).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "span.icon.icon--14-triangle-down.icon--size-14.icon--inverse."
                                          "icon--fallback-inverted.u-triangle-direction-down."
                                          "user-account_button-arrow.responsive-visible-large-inline-block"))
                )
                usr_btn.click()

                find_friends = WebDriverWait(driver, 100).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "ul.drop-menu-group--nav.drop-menu-group > li"))
                )
                find_friends[1].click()

            except:
                logTxt = logTxt + "\tWe can't access to first page of yelp\n"
                print(logTxt)
                self.drivers.append(None)
                return

        try:
            query = WebDriverWait(driver, 100).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='query']"))
            )
        except:
            logTxt = logTxt + "\tCan't find query inputbox\n"
            print(logTxt)
            self.drivers.append(driver)
            return

        try:
            action_chain = ActionChains(driver)
            action_chain.click(query).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE) \
                .perform()

            query.send_keys(email)
            query.send_keys(Keys.ENTER)
        except:
            logTxt = logTxt + "\tCan't input email into query inputbox\n"
            print(logTxt)
            self.drivers.append(driver)
            return

        try:
            WebDriverWait(driver, 100).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-header_block-main"))
                )

            member_row = driver.find_element_by_css_selector("div.member-row")

            try:
                yelp_name = member_row.find_element_by_id("dropdown_user-name").text
            except:
                yelp_name = ''

            try:
                yelp_url = member_row.find_element_by_id("dropdown_user-name").get_attribute('href')
            except:
                yelp_url = ''

            try:
                yelp_city = member_row.find_element_by_class_name("li.user-location.responsive-hidden-small").text
            except:
                yelp_city = ''

            try:
                yelp_friends = member_row.find_element_by_class_name("li.friend-count.responsive-small-display-inline-block").text
            except:
                yelp_friends = ''

            try:
                yelp_reviews = member_row.find_element_by_class_name("li.review-count.responsive-small-display-inline-block").text
            except:
                yelp_reviews = ''

            try:
                yelp_elite = member_row.find_element_by_class_name(
                    "li.review-count.responsive-small-display-inline-block")
                yelp_elite = 'yes'
            except:
                yelp_elite = 'no'

        except:
            logTxt = logTxt + "\tCan't find details\n"

        logTxt = logTxt + "\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" + \
                 "\tYelp Name: {0}\n\tYelp URL: {1}\n\tYelp Reviews: {2}\n\tYelp Friends: {3}\n\tYelp City: {4}\n" \
                 "\tYelp Elite: {5}\n".format(yelp_name, yelp_url, yelp_reviews, yelp_friends, yelp_city, yelp_elite)
        print(logTxt)

        self.output_data.append([yelp_name, yelp_url, yelp_reviews, yelp_friends, yelp_city, yelp_elite])
        self.drivers.append(driver)


if __name__ == '__main__':
    app = mainScraper()
    app.startScraping()


