

from mediapipe import Image, ImageFormat
from mediapipelib.gesture_recognize import *
from webdriverlib.yt_browser import *
from videolib.opencv_draw import *

import cv2

MODEL_PATH = "./src/models/gesture_recognizer.task"

INFO_MSGS = True # testing
SHOW_CAM = True
MIN_GESTURE_MS = 750
GESTURE_HISTORY_LEN = 4
CAMERA_INPUT = 0


# Gestures
gestures = { # deault: ["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"]
    "next": GestureSequence(
        ["None", 500],
        ["Open_Palm", 1500],
        ["None", 500]
    ),
    "prev": GestureSequence(
        ["None", 500],
        ["Pointing_Up", 2500]
    ),
    "like": GestureSequence(
        ["Thumb_Up", 3000]
    ),
    "dislike": GestureSequence(
        ["Thumb_Down", 3000]
    ),
    "pause": GestureSequence(
        ["Victory", 1000]
    )
}


if INFO_MSGS: print("[main] Initalizaing Gesture Trackers")
RightTracker = GestureTracker(MIN_GESTURE_MS, GESTURE_HISTORY_LEN)
LeftTracker = GestureTracker(MIN_GESTURE_MS, GESTURE_HISTORY_LEN)
if INFO_MSGS: print("[main] Initalizaing Webdriver")
browser = YTDriver(left_monitor = True)


# Gesture actions
actions = {
    "next": browser.next_video,
    "prev": browser.prev_video,
    "like": browser.toggle_like,
    "dislike": browser.toggle_dislike,
    "pause": browser.toggle_pause
}


def gestureCallback(result: "mediapipe.tasks.vision.GestureRecognizerResult", output_image: Image, timestamp_ms: int):
    hand_landmarks_list = result.hand_landmarks
    handedness_list = result.handedness
    gestures_list = result.gestures

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand = handedness_list[idx][0].category_name
        if INFO_MSGS: print(f"[callback] {hand} ({handedness_list[idx][0].score * 100:.2f}%): {gestures_list[idx][0].category_name} ({gestures_list[idx][0].score * 100:.2f}%)")
        if hand == "Right":
            RightTracker.append(gestures_list[idx][0].category_name, timestamp_ms)
        else: # left hand
            LeftTracker.append(gestures_list[idx][0].category_name, timestamp_ms)

    for name, gs in gestures.items():
        if RightTracker.contains(gs):
            actions[name]()
            break

    if SHOW_CAM:
        return annotate_image(output_image, result)

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
        if SHOW_CAM and recognizer.last_callback_result is not None and recognizer.frame_state == 1:
            cv2.imshow('press Q to exit', cv2.cvtColor(recognizer.last_callback_result, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except Exception as e:
    print("[main] Something went wrong. Trace:")
    print(e)
finally:
    browser.close()
    recognizer.close()
    cap.release()
    cv2.destroyAllWindows()