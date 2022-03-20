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
import shutil

DOWNLOAD_PATH = os.getcwd() + '/retracted_articles'
WEB_SCIENCE_USERNAME = ""
WEB_SCIENCE_PASSWORD = ""
LOGIN_URL = ('https://ezpa.library.ualberta.ca/ezpAuthen.cgi'
             '?url=https://www.webofscience.com/wos/woscc/basic-search')

dt = pd.read_csv('../data/retraction_notices11622_refactored.csv',
                 usecols=['Source Title', 'new_title'])

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
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")  # linux only
        #options.add_argument("--headless")
        options.add_argument("--remote-debugging-port=9222")
        #options.add_argument("--window-size=1280,1024")
        options.add_argument("--window-size=1024,760")
        default_download_path = {"download.default_directory": DOWNLOAD_PATH}
        options.add_experimental_option("prefs", default_download_path)
        browser = webdriver.Chrome(executable_path=chrome_driver,
                                   options=options)
        browser.implicitly_wait(3)
        browser.get(LOGIN_URL)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=user]")
        elem.send_keys(WEB_SCIENCE_USERNAME)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=pass]")
        elem.send_keys(WEB_SCIENCE_PASSWORD)
        elem = browser.find_element(By.CSS_SELECTOR, "form[name=loginForm]")
        elem.submit()

        try:
            print('Wait for popup')
            loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
            wait = WebDriverWait(browser, 30, 2)
            wait.until(EC.visibility_of_element_located(loc))
            print("Close guide popup")
            # close popup guide
            xpath = "//button[@class='_pendo-close-guide']"
            elem = browser.find_element(By.XPATH, xpath)
            elem.click()
            print('Click on popup')
        except Exception as e:
            print(e)

        try:
            print('Wait for cookie popup')
            loc = (By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
            wait = WebDriverWait(browser, 30, 2)
            wait.until(EC.visibility_of_element_located(loc))
            print("Close Cookie popup")
            # close cookie popup
            xpath = "//button[@id='onetrust-accept-btn-handler']"
            elem = browser.find_element(By.XPATH, xpath)
            elem.click()
        except Exception as e:
            print(e)

        first_search = True
        for i in range(0, 200):
            if start >= len(dt):
                break
            a = dt['new_title'][start]
            b = dt['Source Title'][start]
            print(start)
            ofn = DOWNLOAD_PATH + '/' + str(start + 1) + '.txt'
            ofn2 = DOWNLOAD_PATH + '/' + str(start + 1) + '_cites.txt'
            if os.path.exists(ofn) and os.path.exists(ofn2):
                start += 1
                continue

            try:
                # "Advanced Search" click
                elem = browser.find_element(By.LINK_TEXT, "Advanced Search")
                elem.click()

                # Wait until the `advancedSearchInputArea` element appear
                # (up to 5 seconds)
                print('Wait for Advance Search input Area') 
                wait = WebDriverWait(browser, 5, 1)
                loc = (By.ID, "advancedSearchInputArea")
                wait.until(EC.presence_of_element_located(loc))
                # enter the query string in textarea 
                xpath = "//span[contains(., ' Clear ')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                elem = browser.find_element(By.ID, "advancedSearchInputArea")
                elem.send_keys('TI=(' + a + ') AND SO=(' + b + ')')

                # click 'Search' button
                xpath = "//button[contains(., ' Search ')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                print('Click on search')

                if first_search:
                    # FIXME: it seems popup randomly
                    try:
                        print('Wait for popup')
                        loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
                        wait = WebDriverWait(browser, 2, 1)
                        wait.until(EC.visibility_of_element_located(loc))
                        # click close popup
                        xpath = "//button[@class='_pendo-close-guide']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        print('Click on popup')
                        first_search = False
                    except Exception as e:
                        print(e)

                xpath = "//span[text()='Sort by:']/following-sibling::span"
                try:
                    print('Wait for search results')
                    loc = (By.XPATH, xpath)
                    wait = WebDriverWait(browser, 2, 1)
                    wait.until(EC.presence_of_element_located(loc))
                except Exception as e:
                    print('No search results')
                    try:
                        txt = "< BACK TO BASIC SEARCHES"
                        elem = browser.find_element(By.LINK_TEXT, txt)
                        elem.click()
                    except Exception as e:
                        print(e)
                    start += 1
                    continue

                elem = browser.find_element(By.XPATH, xpath)
                if elem.text != 'Date: oldest first':
                    try:
                        # click "Sort by:"
                        xpath = "//span[text()='Sort by:']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        # select "Date: oldest first"
                        xpath = "//span[text()='Date: oldest first']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                    except Exception as e:
                        print(e)
                        # close popup guide
                        xpath = "//button[@class='_pendo-close-guide']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        print('Click on popup')
                        # click "Sort by:"
                        xpath = "//span[text()='Sort by:']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        # select "Date: oldest first"
                        xpath = "//span[text()='Date: oldest first']"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()

                # select first record
                xpath = "//app-record//mat-checkbox"
                elems = browser.find_elements(By.XPATH, xpath)
                elems[0].click()

                print('Wait for Export')
                loc = (By.XPATH, "//button[contains(., 'Export')]")
                wait = WebDriverWait(browser, 5, 1)
                wait.until(EC.presence_of_element_located(loc))
                # click 'Export' dropdown button
                xpath = "//button[contains(., 'Export')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                print('Click on export')

                print('Wait for Tab delimited file')
                xpath = "//button[contains(., 'Tab delimited file')]"
                loc = (By.XPATH, xpath)
                wait = WebDriverWait(browser, 5, 1)
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

                print('Wait for Export option')
                xpath = "//button[contains(., 'Author, Title, Source')]"
                loc = (By.XPATH, xpath)
                wait = WebDriverWait(browser, 5, 1)
                wait.until(EC.presence_of_element_located(loc))
                xpath = "//button[contains(., 'Author, Title, Source')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                print('Click on Export option')
                #choose 'Full Record'
                xpath = "//span[contains(., 'Full Record')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                # export file
                xpath = "//span[contains(., 'Export')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                dfn = DOWNLOAD_PATH + '/' + 'savedrecs.txt'
                r = 0
                while (r < 20):
                    print('Download Article...')
                    time.sleep(1)
                    if os.path.exists(dfn):
                        shutil.move(dfn, ofn)
                        break
                    r += 1
                if r == 20:
                    xpath = "//span[contains(., 'Cancel')]"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                    print('ERROR: Cannot download', start)

                if not os.path.exists(ofn2):
                    # click 'Citations'
                    try:
                        print('Wait for Citations')
                        xpath = "//div[contains(@class, 'citations')]"
                        loc = (By.XPATH, xpath)
                        wait = WebDriverWait(browser, 2, 1)
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

                    print('Wait for Export citations')
                    loc = (By.XPATH, "//button[contains(., 'Export')]")
                    wait = WebDriverWait(browser, 5, 1)
                    wait.until(EC.presence_of_element_located(loc))
                    # click 'Export' dropdown button
                    xpath = "//button[contains(., 'Export')]"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                    print('Click on Export citations')

                    print('Wait for Tab delimited file')
                    xpath = "//button[contains(., 'Tab delimited file')]"
                    loc = (By.XPATH, xpath)
                    wait = WebDriverWait(browser, 5, 1)
                    wait.until(EC.presence_of_element_located(loc))
                    try:
                        xpath = "//button[contains(., 'Tab delimited file')]"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        print('Click on Tab delimted file')
                    except Exception as e:
                        print(e)
                        webdriver.ActionChains(browser).send_keys(Keys.ESCAPE).perform()
                        elem.click()
                        print('Click on Tab delimted file (again)')

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
                        print('Download Citations...')
                        time.sleep(1)
                        if os.path.exists(dfn):
                            shutil.move(dfn, ofn2)
                            break
                        r += 1
                    if r == 20:
                        xpath = "//span[contains(., 'Cancel')]"
                        elem = browser.find_element(By.XPATH, xpath)
                        elem.click()
                        print('ERROR: Cannot download', start)

            except Exception as e:
                print(e)
                try:
                    txt = "< BACK TO BASIC SEARCHES"
                    elem = browser.find_element(By.LINK_TEXT, txt)
                    elem.click()
                    print('Wait for popup')
                    loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
                    wait = WebDriverWait(browser, 3, 1)
                    wait.until(EC.visibility_of_element_located(loc))
                    # close popup guide
                    xpath = "//button[@class='_pendo-close-guide']"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                    print('Click on popup')
                except Exception as e:
                    print(e)
            start += 1
    except Exception as e:
        print(e)
        time.sleep(300)
    finally:
        browser.quit()
