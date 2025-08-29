from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time

PREV_BUTTON_ID = "navigation-button-up"
NEXT_BUTTON_ID = "navigation-button-down"

options = webdriver.edge.options.Options()
options.add_argument("--start-maximized")

driver = webdriver.Edge(options=options)
#driver.set_permissions('camera', 'denied')
driver.implicitly_wait(1)

driver.get("https://www.youtube.com/shorts")
wait = WebDriverWait(driver,5)  

next_button = wait.until(EC.presence_of_element_located((By.ID, NEXT_BUTTON_ID)))
prev_button = driver.find_element(By.ID, PREV_BUTTON_ID)
video_container = driver.find_element(By.TAG_NAME, "video")

while True:
    next_button.click()

driver.quit()