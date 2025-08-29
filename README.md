# Description
thought it would be funny to say i was too lazy to doomscroll
this program should should scroll to the next youtube short/instragram reel when i flick my hand

# todo
- ~~browser action delay does not work properly as there is currently no queue to process actions synchronously, simultaneous actions execute before the delay value has a chance to update and take effect~~
    - solution: implement a queue using a main thread for actions and subprocess for making calls to it ("adding it to the queue")
    - *actual solution: fixed incorrectly named variable when updating last action timestamp*
- implement threading for action delay, and to remove script startup delay when initalizating the webdriver and OpenCV video feed
- ! add complex, multi-step gestures for more concise user input
    - implement counter / tracker consecutive gestures (ignoring delimiters like "None" gestures)
- implement try/except/finally to maintain runtime even with errors and exit gracefully
- make this script easier to execute on the fly, for daily use

# prerequisites
- must have ms edge
- must have a useable webcam bound to system bus 0 (find more [here](https://www.google.com/search?q=how+does+opencv+index+input+devices))

# libraries used
- selenium
- google mediapipe

# Google MediaPipe models
**Gesture Recognizer**\
*comes packages with hand landmrker*\
[download latest](https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task)\
[docs](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer)

**Hand Landmarker**
*individual model used in testing*
[download latest](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task)
[docs](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)




### hours wasted on this project (increment counter before commit)
- 5