from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep

class YTDriver:

    UP_BUTTON_ID = "navigation-button-up"
    DOWN_BUTTON_ID = "navigation-button-down"
    LIKE_BUTTON_ID = "like-button"
    DISLIKE_BUTTON_ID = "dislike-button"
    TARGET_URL = "https://www.youtube.com/shorts"

    def __init__(self, action_delay_ms: int = 650, left_monitor = True):
        self.action_delay = action_delay_ms
        self.running_action = False

        options = webdriver.EdgeOptions()
        options.add_experimental_option("excludeSwitches", ['enable-logging'])
        options.add_argument("--log-level=3")
        self.driver = webdriver.Edge(options=options)
        if left_monitor:
            self.driver.set_window_position(-2000, 1) # move it onto the left monitor- i.e. as far left as possible lmao
        self.driver.maximize_window()
        self.driver.get(self.TARGET_URL)
        wait = WebDriverWait(self.driver, 5)
        try:
            self._down_button = wait.until(EC.presence_of_element_located((By.ID, self.DOWN_BUTTON_ID)))
            self._like_button = wait.until(EC.presence_of_element_located((By.ID, self.LIKE_BUTTON_ID)))
            self._dislike_button = wait.until(EC.presence_of_element_located((By.ID, self.DISLIKE_BUTTON_ID)))
            self._video_player = wait.until(EC.presence_of_element_located((By.TAG_NAME, "video")))
        except Exception as e:
            self.driver.quit()
            self._errprint("Failed to initalize webdriver. Trace:")
            print(e)

    def is_running(self) -> bool:
        try:
            self.on_target_page()
            return True
        except:
            return False

    def on_page(self, url_prefix: str) -> bool:
        return self.driver.current_url.startswith(url_prefix)

    def on_target_page(self) -> bool:
        return self.on_page(self.TARGET_URL)

    def _errprint(self, content):
        print("[YTDriver] Error: ", end = "")
        print(content)

    def _finish_action(self):
        self.running_action = False
        sleep(self.action_delay / 1000)

    def next_video(self):
        self.running_action = True
        try:
            self._down_button.click()
        except:
            self._errprint("Failed to click %s" % self.DOWN_BUTTON_ID)
        finally:
             self._finish_action()

    def prev_video(self):
        if self.driver.find_elements(By.ID, self.UP_BUTTON_ID):
            self.running_action = True
            self._up_button = self.driver.find_element(By.ID, self.UP_BUTTON_ID)
            try:
                self._up_button.click()
            except:
                self._errprint("Failed to click %s" % self.UP_BUTTON_ID)
            finally:
                 self._finish_action()
        else:
            # button does not exist- likely at the top of the feed
            ...
    
    def toggle_pause(self):
        self.running_action = True
        try:
            self._video_player.click()
        except:
            self._errprint("Failed to click video element")
        finally:
             self._finish_action()
    
    def toggle_like(self):
        self.running_action = True
        try:
            self._like_button.click()
        except:
            self._errprint("Failed to click %s" % self.LIKE_BUTTON_ID)
        finally:
             self._finish_action()

    def toggle_dislike(self):
        self.running_action = True
        try:
            self._dislike_button.click()
        except:
            self._errprint("Failed to click %s" % self.DISLIKE_BUTTON_ID)
        finally:
             self._finish_action()

    def close(self):
        self.running_action = True
        self.driver.quit()
        self.running_action = False

    def __enter__(self):
        return self
    
    def __exit__(self):
        self.close()
