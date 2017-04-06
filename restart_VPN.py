import pyautogui
import time
import credentials
import help_methods

pw = help_methods.decrypt(credentials.Credentials().feide[1])


def restart_vpn():
    pyautogui.press('enter')
    pyautogui.moveTo(1799, 1095)
    pyautogui.click()
    time.sleep(5)  # Wait of login to open
    pyautogui.typewrite(pw)
    pyautogui.press('enter')
    time.sleep(10)
