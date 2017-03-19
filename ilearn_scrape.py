# Web Scraping from Itslearning using Selenium
# Based on Scraping example given by Audun Liberg

from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException


def scrape(username, password):
    """Scrapes It'slearning. Returns a list of lists [assignment_name, cource_code, course_name, due_date, due_time]"""
    driver = webdriver.Chrome()
    # Log in via Feide
    driver.get("http://www.ilearn.sexy")  # Shortcut to itslearning
    username_field = driver.find_element_by_name("feidename")
    username_field.send_keys(username)
    password_field = driver.find_element_by_name("password")
    password_field.send_keys(password)
    password_field.submit()
    # Login complete

    wait = ui.WebDriverWait(driver, 10)
    try:
        driver.find_element_by_id("yesbutton").click()
    except:
        pass
    try:
        wait.until(lambda driver: driver.find_element_by_id('l-header'))  # Wait for the site to load properly
    except TimeoutException:
        print("Wrong username or password")
        with open("LOG/ILlogin.txt", "a", encoding="UTF-8") as f:
            f.write("un:" + username + "; pw: " + password + '\n')
        driver.quit()
        return "error"
    driver.switch_to.frame(
        driver.find_element_by_name("mainmenu"))  # itslearning uses iframes, let's go to the corrct one

    # Fetch and print assignment deadlines including coursename
    deadlines = driver.find_elements_by_class_name("h-dsp-ib")  # Gets class of the deadlines
    courses = driver.find_elements_by_class_name("h-pdr5")
    assignment = driver.find_elements_by_class_name("h-va-baseline")
    listing = []
    for i in range(len(courses)):
        course = courses[i].text.split()
        deadline = deadlines[i * 2 + 1].get_attribute('title').split()
        listing.append((assignment[i].text, course[1], " ".join(course[2:-2]), deadline[1], deadline[2]))
    # Gathers the relevant information
    # print(listing)
    # html = driver.execute_script("return document.documentElement.innerHTML;") # Get element HTML for assignments
    # with open("HTML/Itslearning_"+username+".txt", "w", encoding='utf-8') as f:  #Write to file, to easier search inner HTML for needed enteties
    #    f.write(html)
    # print(listing)
    driver.quit()  # Closing the browser
    return listing  # In format list of (assignment_name, cource_code, course_name, due_date, due_time)
