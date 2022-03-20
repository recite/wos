from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import sys

DOWNLOAD_PATH = os.getcwd() + '/search_results/citing_articles'
WEB_SCIENCE_USERNAME = ""
WEB_SCIENCE_PASSWORD = ""
LOGIN_URL = ('https://ezpa.library.ualberta.ca/ezpAuthen.cgi'
             '?url=https://www.webofscience.com/wos/alldb/basic-search')

dt = pd.read_csv(os.getcwd()+'/selected_records.csv')

try:
    start = int(sys.argv[1])
except Exception as e:
    start = 0

while True:
    if start >= len(dt):
        break
    try:
        # Set the default download folder
        chrome_driver = os.path.abspath("chromedriver")
        os.environ["webdriver.chrome.driver"] = chrome_driver
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        #options.add_argument("--disable-gpu")
        #options.add_argument("--no-sandbox")  # linux only
        #options.add_argument("--headless")
        #options.add_argument("--remote-debugging-port=9222")
        #options.add_argument("--window-size=1280,1024")
        options.add_argument("--window-size=1024,760")
        default_download_path = {"download.default_directory": DOWNLOAD_PATH}
        options.add_experimental_option("prefs", default_download_path)
        browser = webdriver.Chrome(executable_path=chrome_driver,
                                   options=options)
        browser.implicitly_wait(5)
        browser.get(LOGIN_URL)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=user]")
        elem.send_keys(WEB_SCIENCE_USERNAME)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=pass]")
        elem.send_keys(WEB_SCIENCE_PASSWORD)
        elem = browser.find_element(By.CSS_SELECTOR, "form[name=loginForm]")
        elem.submit()

        time.sleep(5)

        # ESCAPE to close popup
        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()

        try:
            print('Wait for cookie popup')
            loc = (By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.visibility_of_element_located(loc))
            print('Close Cookie popup')
            # close cookie popup
            xpath = "//button[@id='onetrust-accept-btn-handler']"
            elem = browser.find_element(By.XPATH, xpath)
            elem.click()
        except Exception as e:
            print(e)

        first_search = True
        for i in range(0, 200):
            webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
            if start >= len(dt):
                break
            a = dt['Article Title'][start]
            b = dt['name_each_file'][start]
            print(start)
            ofn = DOWNLOAD_PATH + '/' + str(b) + '.tsv'
            if os.path.exists(ofn):
                start += 1
                continue

            try:
                # "Advanced Search" click
                elem = browser.find_element(By.LINK_TEXT, "Advanced Search")
                elem.click()

                # Wait until the `advancedSearchInputArea` element appear
                # (up to 5 seconds)
                wait = WebDriverWait(browser, 5)
                loc = (By.ID, "advancedSearchInputArea")
                wait.until(EC.presence_of_element_located(loc))
                # enter the query string in textarea 
                xpath = "//span[contains(., 'Clear')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                elem = browser.find_element(By.ID, "advancedSearchInputArea")
                s = 'TI=(' + a + ')'
                print(s)
                elem.send_keys(s)

                # click 'Search' button
                xpath = "//button[contains(., 'Search')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                time.sleep(1)

                webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()

                print(browser.current_url)

                xpath = "//div[contains(@class, 'stats-section-section')]/div"
                elems = browser.find_elements(By.XPATH, xpath)
                stats_count = len(elems)
                print('Stats Count = %d' % stats_count)

                if stats_count < 2:
                    print('No citations')
                    start += 1
                    continue

                # click 'Citations'
                try:
                    print('Wait for Citations')
                    xpath = "//div[contains(@class, 'citations')]"
                    loc = (By.XPATH, xpath)
                    wait = WebDriverWait(browser, 2)
                    wait.until(EC.presence_of_element_located(loc))
                except Exception as e:
                    print(e)
                    print('No citations')
                    start += 1
                    continue

                try:
                    xpath = "//div[contains(@class, 'citations')]/a"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                except Exception as e:
                    print(e)
                    print('No citations')
                    start += 1
                    continue

                loc = (By.XPATH, "//button[contains(., 'Export')]")
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                # click 'Export' dropdown button
                xpath = "//button[contains(., 'Export')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                xpath = "//button[contains(., 'Tab delimited file')]"
                loc = (By.XPATH, xpath)
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                try:
                    xpath = "//button[contains(., 'Tab delimited file')]"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                    print('Click on Tab delimeted file')
                except Exception as e:
                    print(e)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                    elem.click()
                    print('Click on Tab delimted file (again)')

                xpath = "//button[contains(., 'Author, Title, Source')]"
                loc = (By.XPATH, xpath)
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                xpath = "//button[contains(., 'Author, Title, Source')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                # tick to 'Records from:'
                xpath = "//span[contains(., 'Records from:')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                # export file
                xpath = "//span[contains(., 'Export')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                dfn = DOWNLOAD_PATH + '/' + 'savedrecs.txt'
                r = 0
                while (r < 20):
                    print('Downloading...')
                    time.sleep(1)
                    if os.path.exists(dfn):
                        os.rename(dfn, ofn)
                        break
                    r += 1
                if r == 20:
                    xpath = "//span[contains(., 'Cancel')]"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                    print('ERROR: Cannot download', start)
            except Exception as e:
                print(e)
                webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                try:
                    txt = "< BACK TO BASIC SEARCHES"
                    elem = browser.find_element(By.LINK_TEXT, txt)
                    elem.click()
                    time.sleep(1)
                    # ESCAPE to close popup (if any)
                    webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                except Exception as e:
                    print(e)
            start += 1
    except Exception as e:
        print(e)
    finally:
        browser.quit()
