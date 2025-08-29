from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

PREV_BUTTON_ID = "navigation-button-up"
NEXT_BUTTON_ID = "navigation-button-down"

driver = webdriver.Edge()
#driver.set_permissions('camera', 'denied')
driver.set_window_position(-2000, 1) # move it onto the left monitor- i.e. as far left as possible lmao
driver.maximize_window()
driver.get("https://www.youtube.com/shorts")
wait = WebDriverWait(driver,5)  

next_button = wait.until(EC.presence_of_element_located((By.ID, NEXT_BUTTON_ID)))
prev_button = driver.find_element(By.ID, PREV_BUTTON_ID)
video_container = driver.find_element(By.TAG_NAME, "video")

while True:
    next_button.click()

driver.quit()