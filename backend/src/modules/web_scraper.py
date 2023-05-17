from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib.request import Request, urlopen
from datetime import timedelta
import pandas as pd
import traceback as tb

options = Options()
options.add_argument("-headless")
options.add_argument("--disable-gpu")


def get_future(timeout):
    try:
        driver = webdriver.Firefox(options=options)
        driver.get("https://www.asxenergy.com.au/futures_au")

        wait = WebDriverWait(driver, timeout)
        xpath = "//td[@title='BNZ2023']/following-sibling::td[6]"
        element = driver.find_element(
            By.XPATH, xpath
        )
        future = float(element.text)
        return future
    except TimeoutException as te:
        print(f"Element not found within specified timeout period {te}")
    finally:
        driver.quit()


def download_csv(year, month):
    try:
        print(f"downloading data for {year}, {month}")
        url = f"https://aemo.com.au/aemo/data/nem/priceanddemand/PRICE_AND_DEMAND_{year}{month}_NSW1.csv"
        req = Request(url)
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0",
        )
        with urlopen(req) as content:
            df = pd.read_csv(content)
            return upsample_download(df)

    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None
    


def upsample_download(df):
    df['SETTLEMENTDATE'] = pd.to_datetime(df['SETTLEMENTDATE'])

    df.set_index('SETTLEMENTDATE', inplace=True)

    time_diff = df.index.to_series().diff().min()
    if pd.notnull(time_diff) and time_diff > timedelta(minutes=5):
        df = df.resample("5T").ffill()    
    else: 
        df = df.resample("30T").ffill().resample("5T").ffill()

    df.reset_index(inplace=True)

    return df