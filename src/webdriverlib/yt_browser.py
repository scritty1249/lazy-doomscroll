from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By



class YTDriver:

    UP_BUTTON_ID = "navigation-button-up"
    DOWN_BUTTON_ID = "navigation-button-down"
    LIKE_BUTTON_ID = "like-button"
    DISLIKE_BUTTON_ID = "dislike-button"
    TARGET_URL = "https://www.youtube.com/shorts"

    def __init__(self, left_monitor = True):
        self.driver = webdriver.Edge()
        if left_monitor:
            self.driver.set_window_position(-2000, 1) # move it onto the left monitor- i.e. as far left as possible lmao
        self.driver.maximize_window()
        self.driver.get(self.TARGET_URL)
        wait = WebDriverWait(self.driver, 5)
        try:
            self._down_button = wait.until(EC.presence_of_element_located((By.ID, self.DOWN_BUTTON_ID)))
            self._video_player = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
            self._like_button = wait.until(EC.presence_of_element_located((By.ID, self.LIKE_BUTTON_ID)))
            self._dislike_button = wait.until(EC.presence_of_element_located((By.ID, self.DISLIKE_BUTTON_ID)))

            self.next_video()
            self._up_button = self.driver.find_element(By.ID, self.UP_BUTTON_ID)
        except Exception as e:
            self.driver.quit()
            self._errprint("Failed to initalize webdriver. Trace:")
            print(e)

    def on_page(self, url_prefix: str) -> bool:
        return driver.current_url.startswith(url_prefix)

    def on_target_page(self) -> bool:
        return self.on_page(self.TARGET_URL)

    def _errprint(self, content):
        print("[YTDriver] Error: ", end = "")
        print(content)

    def next_video(self):
        try:
            self._down_button.click()
        except:
            self._errprint("Failed to click %s" % self.DOWN_BUTTON_ID)

    def prev_video(self):
        try:
            self._up_button.click()
        except:
            self._errprint("Failed to click %s" % self.UP_BUTTON_ID)
    
    def toggle_pause(self):
        try:
            self._video_player.click()
        except:
            self._errprint("Failed to click video element")
    
    def toggle_like(self):
        try:
            self._like_button.click()
        except:
            self._errprint("Failed to click %s" % self.LIKE_BUTTON_ID)

    def toggle_dislike(self):
        try:
            self._dislike_button.click()
        except:
            self._errprint("Failed to click %s" % self.DISLIKE_BUTTON_ID)

    def close(self):
        self.driver.quit()

    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()
