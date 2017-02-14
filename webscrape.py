#Web Scraping from Itslearning using Selenium
#Based on Scraping example given by Audun Liberg

from selenium import webdriver
import selenium.webdriver.support.ui as ui
from getpass import getpass

il_username = input("NTNU username: ")
il_password = getpass("NTNU password: ") # Function for hiding password input

def init_driver():
    global driver
    driver = webdriver.Chrome()

def scrape():
    # Log in via Feide
    driver.get("http://www.ilearn.sexy") # Shortcut to itslearning
    username = driver.find_element_by_name("feidename")
    username.send_keys(il_username)
    password = driver.find_element_by_name("password")
    password.send_keys(il_password)
    password.submit()

    wait = ui.WebDriverWait(driver, 10)
    wait.until(lambda driver: driver.find_element_by_id('l-header')) # Wait for the site to load properly
    driver.switch_to.frame(driver.find_element_by_name("mainmenu")) # itslearning uses iframes, let's go to the corrct one

    # Fetch and print assignment deadlines including coursename
    courses = driver.find_elements_by_class_name("h-pdr20")
    for i in range(len(courses)):
        print(courses[i].text[:-2]) # Removing the 2 last characters which are '\n' and 'x', in that order
    driver.quit() #Closing the browser

if __name__ == "__main__":
    init_driver()
    scrape()
