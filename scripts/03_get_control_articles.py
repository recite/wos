from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.command import Command
from selenium.webdriver.chrome.options import Options

import pandas as pd
import time
import os
import calendar
import datetime

DOWNLOAD_PATH = os.getcwd() + '/search_results'
WEB_SCIENCE_USERNAME = ""
WEB_SCIENCE_PASSWORD = ""
LOGIN_URL = ('https://ezpa.library.ualberta.ca/ezpAuthen.cgi'
             '?url=https://www.webofscience.com/wos/alldb/basic-search')

# Create query strings
dt = pd.read_excel(os.getcwd() + '/new_retracted_articles.xlsx')
li_mon = []
for i in dt.PD:
    if (type(i) == str) & (str(i).title() in list(calendar.month_abbr)):
        li_mon.append(list(calendar.month_abbr).index(i.title()))
    elif type(i) == datetime.datetime:
        li_mon.append(i.month)
    else:
        li_mon.append(1)
dt['month'] = li_mon
li_date = []
for i in dt.PD:
    if type(i) == datetime.datetime:
        li_date.append(i.day)
    else:
        li_date.append(1)
dt['date'] = li_date
dt['start'] = (dt.PY.astype(str) + '-' + dt.month.astype(str) + '-'
               + dt.date.astype(str))

li_date_end = []
for a, b in zip(dt.PD, dt.start):
    if type(a) == datetime.datetime:
        li_date_end.append(a.day)
    else:
        li_date_end.append(pd.Period(b).days_in_month)
dt['date_end'] = li_date_end
dt['end'] = (dt.PY.astype(str) + '-' + dt.month.astype(str) + '-'
             + dt.date_end.astype(str))

dt['start'] = dt['start'].apply(pd.to_datetime)
dt['end'] = dt['end'].apply(pd.to_datetime)
# FIXME: change from WC to SC
dt['query'] = ('(SO=(' + dt.SO + ')) AND DOP=(' + dt.start.astype(str) + '/'
               + dt.end.astype(str) + ') AND DT=(Article) AND SU=('
               + dt.SC + ')')

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
        options.add_argument("--headless")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--window-size=1280,1024")
        default_download_path = {"download.default_directory": DOWNLOAD_PATH}
        options.add_experimental_option("prefs", default_download_path)
        browser = webdriver.Chrome(executable_path=chrome_driver,
                                   options=options)
        browser.implicitly_wait(15)
        browser.get(LOGIN_URL)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=user]")
        elem.send_keys(WEB_SCIENCE_USERNAME)
        elem = browser.find_element(By.CSS_SELECTOR, "input[name=pass]")
        elem.send_keys(WEB_SCIENCE_PASSWORD)
        elem = browser.find_element(By.CSS_SELECTOR, "form[name=loginForm]")
        elem.submit()

        try:
            loc = (By.XPATH, "//button[@id='onetrust-accept-btn-handler']")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.visibility_of_element_located(loc))
            # close cookies popup
            xpath = "//button[@id='onetrust-accept-btn-handler']"
            elem = browser.find_element(By.XPATH, xpath)
            elem.click()
        except Exception as e:
            print(e)

        try:
            loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
            wait = WebDriverWait(browser, 30)
            wait.until(EC.visibility_of_element_located(loc))
            # close popup guide
            xpath = "//button[@class='_pendo-close-guide']"
            elem = browser.find_element(By.XPATH, xpath)
            elem.click()
        except Exception as e:
            print(e)

        for i in range(0, 100):
            print(start)
            if start >= len(dt):
                break
            ofn = DOWNLOAD_PATH + '/' + str(start + 1) + '.xls'
            if os.path.exists(ofn):
                start += 1
                continue
            try:
                # "Advanced Search" click
                elem = browser.find_element(By.LINK_TEXT, "Advanced Search")
                elem.click()

                # Wait until the `advancedSearchInputArea` element appear
                # (up to 5 seconds)
                loc = (By.ID, "advancedSearchInputArea")
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                # enter the query string in textarea
                xpath = "//span[contains(., ' Clear ')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()
                elem = browser.find_element(By.ID, "advancedSearchInputArea")
                elem.send_keys(dt['query'][start])

                # click 'Search' button
                xpath = "//button[contains(., ' Search ')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                # FIXME: it seems popup randomly
                try:
                    loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
                    wait = WebDriverWait(browser, 3)
                    wait.until(EC.visibility_of_element_located(loc))
                    # click close popup
                    xpath = "//button[@class='_pendo-close-guide']"
                    elem = browser.find_element(By.XPATH, xpath)
                    elem.click()
                except Exception as e:
                    print(e)

                loc = (By.XPATH, "//button[contains(., ' Export ')]")
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                # click 'Export' dropdown button
                xpath = "//button[contains(., 'Export')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

                loc = (By.XPATH, "//button[contains(., 'Excel')]")
                wait = WebDriverWait(browser, 5)
                wait.until(EC.presence_of_element_located(loc))
                # choose  "Excel" selection
                xpath = "//button[contains(., 'Excel')]"
                elem = browser.find_element(By.XPATH, xpath)
                elem.click()

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

                dfn = DOWNLOAD_PATH + '/' + 'savedrecs.xls'
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
                try:
                    txt = "< BACK TO BASIC SEARCHES"
                    elem = browser.find_element(By.LINK_TEXT, txt)
                    elem.click()
                    print('Wait for popup')
                    loc = (By.XPATH, "//button[@class='_pendo-close-guide']")
                    wait = WebDriverWait(browser, 3)
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
    finally:
        browser.quit()
