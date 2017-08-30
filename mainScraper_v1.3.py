from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import threading, time, csv, os, sys, platform

def takeFirst(elem):
    return elem[0]

class mainScraper():
    def __init__(self):
        self.input_data = []
        self.output_data = []
        self.start_url = 'https://www.yelp.com/login'
        self.drivers = []
        self.cnt = 0

        self.output = open('result.csv', 'w', encoding='utf-8', newline='')
        self.writer = csv.writer(self.output)
        header = ['Email', 'Yelp Name', 'Yelp Profile URL', 'Yelp Reviews', 'Yelp Friends', 'Yelp City', 'Yelp Elite?']
        self.writer.writerow(header)

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

        self.output.close()
        for driver in self.drivers:
            driver.quit()

    def inputFile(self):
        try:
            input_csv = open('Data/split_cs.csv', 'r')
            reader = csv.reader(input_csv)

            for i,row in enumerate(reader):
                if i==0:
                    continue
                self.input_data.append([i, row[0]])
            self.input_data.reverse()
            logTxt = 'Input csv file successfully'
            print(logTxt)
        except:
            logTxt = '(Warning) There is no csv file. Please input it'
            print(logTxt)


        try:
            config_txt = open('Config/Config.txt', 'r').read()
            config_txt = config_txt.split('\n')
            self.id = config_txt[0].split(' ')[1].strip()
            self.pw = config_txt[1].split(' ')[1].strip()

            logTxt = 'Input config file successfully'
            print(logTxt)
        except:
            logTxt = '(Warning) There is no csv file. Please input it'
            print(logTxt)

    def extractDetails(self):

        yelp_name = 'none'
        yelp_url = ''
        yelp_reviews = ''
        yelp_friends = ''
        yelp_city = ''
        yelp_elite = ''

        row = self.input_data.pop()
        email = row[1]
        index = row[0]

        logTxt = "+-+-+-+-+-+-+-+- {0} +-+-+-+-+-+-+-+-\n".format(email)

        driver = self.drivers.pop()

        if driver is None:
            if platform.system() is 'Windows':
                driver = webdriver.Chrome(os.getcwd() + '/WebDriver/chromedriver.exe')
            else:
                driver = webdriver.Chrome(os.getcwd() + '/WebDriver/chromedriver')

            driver.maximize_window()
            driver.get(self.start_url)

            try:
                login = WebDriverWait(driver, 200).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form#ajax-login > input#email"))
                )
                password = driver.find_element_by_css_selector('form#ajax-login > input#password')
                submit_btn = driver.find_element_by_css_selector('form#ajax-login > button.submit')

                login.send_keys(self.id)
                time.sleep(5)
                password.send_keys(self.pw)
                time.sleep(5)
                submit_btn.click()
                logTxt = logTxt + '\tLogin Successfully!\n'

                usr_btn = WebDriverWait(driver, 200).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "span.icon.icon--14-triangle-down.icon--size-14.icon--inverse."
                                          "icon--fallback-inverted.u-triangle-direction-down."
                                          "user-account_button-arrow.responsive-visible-large-inline-block"))
                )
                usr_btn.click()

                logTxt = logTxt + "\tClicked 'Popup' Successfully!\n"

                find_friends = WebDriverWait(driver, 200).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "ul.drop-menu-group--nav.drop-menu-group > li"))
                )
                find_friends[1].click()
                logTxt = logTxt + "\tClicked 'Find Friends' Successfully!\n"

            except:
                logTxt = logTxt + "\t(Warning) We can't access to first page of yelp\n"
                print(logTxt)
                driver.quit()
                self.drivers.append(None)
                return

        try:
            query = WebDriverWait(driver, 200).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='query']"))
            )
            logTxt = logTxt + "\tFound 'Query Box' Successfully!\n"
        except:
            logTxt = logTxt + "\tCan't find 'Query Box' inputbox\n"
            print(logTxt)
            self.input_data.append(row)
            time.sleep(10)
            driver.refresh()
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
            WebDriverWait(driver, 200).until(
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
                yelp_city = member_row.find_element_by_css_selector("li.user-location.responsive-hidden-small").text
            except:
                yelp_city = ''

            try:
                yelp_friends = member_row.find_element_by_css_selector("li.friend-count.responsive-small-display-inline-block").text
            except:
                yelp_friends = ''

            try:
                yelp_reviews = member_row.find_element_by_css_selector("li.review-count.responsive-small-display-inline-block").text
            except:
                yelp_reviews = ''

            try:
                yelp_elite = member_row.find_element_by_css_selector(
                    "li.is-elite.responsive-small-display-inline-block")
                yelp_elite = 'yes'
            except:
                yelp_elite = 'no'

        except:
            logTxt = logTxt + "\tCan't find details\n"

        self.cnt += 1
        logTxt = logTxt + "\t~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" + \
                 "\tYelp Name: {0}\n\tYelp URL: {1}\n\tYelp Reviews: {2}\n\tYelp Friends: {3}\n\tYelp City: {4}\n" \
                 "\tYelp Elite: {5}\n\n\tTotal Scraped: {6}\n". \
                     format(yelp_name, yelp_url, yelp_reviews, yelp_friends, yelp_city, yelp_elite, self.cnt)
        print(logTxt)

        #self.output_data.append([index, email, yelp_name, yelp_url, yelp_reviews, yelp_friends, yelp_city, yelp_elite])
        self.drivers.append(driver)
        self.writer.writerow([email, yelp_name, yelp_url, yelp_reviews, yelp_friends, yelp_city, yelp_elite])

    def saveCSV(self):

        logTxt = '------------------------ Saving data! ------------------------\n'
        self.output_data.sort(key=takeFirst)

        output = open('result.csv', 'w', encoding='utf-8', newline='')
        writer = csv.writer(output)
        header = ['Email', 'Yelp Name', 'Yelp Profile URL', 'Yelp Reviews', 'Yelp Friends', 'Yelp City', 'Yelp Elite?']
        writer.writerow(header)

        for i, row in enumerate(self.output_data):
            writer.writerow(row[1:])

        output.close()

        logTxt = logTxt + 'All completed successfully!'
        print(logTxt)

if __name__ == '__main__':
    app = mainScraper()
    app.startScraping()
    #app.saveCSV()


