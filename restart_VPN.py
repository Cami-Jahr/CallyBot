import pyautogui
import time
import credentials
import help_methods

pw = help_methods.decrypt(credentials.Credentials().feide[1])


def restart_vpn():  # Server screen is 1366x768
    """Assume no program is above server, and icons in correct position"""
    pyautogui.moveTo(1201, 748)  # The location of the VPN in the toolbar
    pyautogui.click()
    pyautogui.moveTo(1289, 641)  # Location of connect button
    pyautogui.click()
    time.sleep(6)
    pyautogui.click()
    time.sleep(6)  # Wait of login to open
    pyautogui.typewrite(pw)
    pyautogui.press('enter')
    time.sleep(12)
