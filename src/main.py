import os

os.environ["GLOG_minloglevel"] = "3"
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from mediapipe import Image, ImageFormat
from mediapipelib.gesture_recognize import *
from webdriverlib.yt_browser import *
from videolib.opencv_draw import *
import traceback
import cv2
import asyncio


MODEL_PATH = "./src/models/gesture_recognizer.task"

INFO_MSGS = True # testing
SHOW_CAM = True
MIN_GESTURE_MS = 750
GESTURE_HISTORY_AGE_MS = 5500
GESTURE_HISTORY_LEN = 2
CAMERA_INPUT = 0

# Sets to make gesture settings easier for hands
BOTH_HANDS = int("11", 2)
EITHER_HAND = int("00", 2)
RIGHT_HAND = int("01", 2)
LEFT_HAND = int("10", 2)

# Gestures
gestures = { # deault: ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]
    "next": GestureSequence(
        #["None", 500, EITHER_HAND],
        ["Open_Palm", 750, EITHER_HAND],
    ),
    "prev": GestureSequence(
        ["Pointing_Up", 600, LEFT_HAND]
    ),
    "like": GestureSequence(
        ["Thumb_Up", 900, EITHER_HAND]
    ),
    "dislike": GestureSequence(
        ["Thumb_Down", 1200, EITHER_HAND]
    ),
    "pause": GestureSequence(
        ["Victory", 250, EITHER_HAND]
    ),
    "quit": GestureSequence(
        ["Closed_Fist", 2350, BOTH_HANDS]
    ),
}


if INFO_MSGS: print("[main] Initalizaing Gesture Trackers")
gestureTracker = GestureTracker(MIN_GESTURE_MS, GESTURE_HISTORY_LEN, GESTURE_HISTORY_AGE_MS)
if INFO_MSGS: print("[main] Initalizaing Webdriver")
browser = YTDriver(left_monitor = True)


# Gesture actions
actions = {
    "next": lambda: browser.on_target_page() and browser.next_video(),
    "prev": lambda: browser.on_target_page() and browser.prev_video(),
    "like": lambda: browser.on_target_page() and browser.toggle_like(),
    "dislike": lambda: browser.on_target_page() and browser.toggle_dislike(),
    "pause": lambda: browser.on_target_page() and browser.toggle_pause(),
    "quit": lambda: browser.close()
}


def gestureCallback(result: "mediapipe.tasks.vision.GestureRecognizerResult", output_image: Image, timestamp_ms: int):
    """Only designed for a maximum of two hands per frame. Things will get weird/unintended behaviour if there are more
        I am not even going to attempt to add handles that
    """
    try: #idfk man
        global gestures
        handedness_list = result.handedness
        gestures_list = result.gestures
        
        # determine if there are multiple hands in the frame, and that they belong to the same person (left and right, and not two of the same hand)
        if len(handedness_list) > 1 and handedness_list[0][0].category_name != handedness_list[1][0].category_name:
            gesture = gestures_list[0][0].category_name
            gesture_gesture = gestures_list[1][0].category_name
            hand = handedness_list[0][0].category_name
            hand_hand = handedness_list[1][0].category_name
            # are they doing the same gesture or do they need to be treated seperately>
            if gesture == gesture_gesture:
                gestureTracker.append(gesture, BOTH_HANDS, timestamp_ms)
            else:
                gestureTracker.append(
                    gesture, 
                    LEFT_HAND if hand_hand == "Left" else RIGHT_HAND,
                    timestamp_ms
                )
                gestureTracker.append(
                    gesture_gesture, 
                    LEFT_HAND if hand_hand == "Left" else RIGHT_HAND,
                    timestamp_ms
                )
        elif len(handedness_list) >= 1: # otherwise just grab the first single hand we indexed 
            gestureTracker.append(
                gestures_list[0][0].category_name,
                LEFT_HAND if handedness_list[0][0].category_name == "Left" else RIGHT_HAND,
                timestamp_ms
            )
        else: # update GestureTracker with current timestamp
            gestureTracker.append("", BOTH_HANDS, timestamp_ms)
        for name, gs in gestures.items():
            if gestureTracker.sequence_view().gesture_set != set([]) and gestureTracker.sequence_view()[-1].gesture == name:
                print(gestureTracker.sequence_view()[-1])
                print(gs)
                print(gs in gestureTracker.sequence_view())
            if gs in gestureTracker.sequence_view():
                if INFO_MSGS: print("[callback] Running action '%s'" % name)
                gestureTracker.clear_queue()
                actions[name]()
                break
        if SHOW_CAM:
            return annotate_image(output_image, result)
    except Exception as e:
        print(f"[callback] Error: ", end = "")
        print(e, end = ". ")
        print("Trace: " + traceback.format_exc())
        return black_image(500, 500, "Video stream error")

if browser.is_running(): # did we crash at startup
    if INFO_MSGS: print("[main] Initalizaing Gesture Recognizer")
    recognizer = GestureModelWrapper(MODEL_PATH, gestureCallback)

    try:
        if INFO_MSGS: print("[main] Opening video capture device")
        cap = cv2.VideoCapture(CAMERA_INPUT)
        if INFO_MSGS: print("[main] Starting main loop")
        while cap.isOpened():
            _ , frame = cap.read()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = Image(image_format=ImageFormat.SRGB, data=img)
            recognizer.process(mp_img)
            if SHOW_CAM and recognizer.last_callback_result is not None:# and recognizer.frame_state == 1:
                cv2.imshow('press Q to exit', cv2.cvtColor(recognizer.last_callback_result, cv2.COLOR_RGB2BGR))
            if cv2.waitKey(1) & 0xFF == ord('q') or not browser.is_running():
                break
    except Exception as e:
        print("[main] Something went wrong. Trace:")
        print(e)
    finally:
        if browser.is_running(): browser.close()
        cap.release()
        cv2.destroyAllWindows()
        recognizer.close()
else:
    print("[main] Webdriver crashed- something went wrong with YTWrapper initialization.")