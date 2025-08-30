# Description
thought it would be funny to say i was too lazy to doomscroll\
this program should should scroll to the next youtube short/instragram reel when i flick my hand

# todo
- initalize browser with local user profile to automate signin on personal account- im tired of seeing the default youtube feed while I test this
- implement threading for action delay, and to remove script startup delay when initalizating the webdriver and OpenCV video feed
- make this script easier to execute on the fly, for daily use
- ! fix like and dislike buttons failing to click
    - solution: try to find a clickable child element
- ~~! figure out why the program crashes with zero output, log, and doesnt execute the finally block after the `annotate_image` function~~
    - *actual solution: It wasn't the `annotate_image` function. There was an issue with GestureTracker*
- ~~add complex, multi-step gestures for more concise user input~~
    - ~~implement counter / tracker consecutive gestures (ignoring delimiters like "None" gestures)~~
    - *actual solution: done*
- ~~implement try/except/finally to maintain runtime even with errors and exit gracefully~~
    - ~~figure out why cv2 errors bypass try/except blocks- otherwise this is implemented~~
    - *actual solution: wrapped the entire method in a try/except block and handle all exceptions generically- this is bad practice*
- ~~browser action delay does not work properly as there is currently no queue to process actions synchronously, simultaneous actions execute before the delay value has a chance to update and take effect~~
    - solution: implement a queue using a main thread for actions and subprocess for making calls to it ("adding it to the queue")
    - *actual solution: fixed incorrectly named variable when updating last action timestamp*

# prerequisites
- must have ms edge
- must have a useable webcam bound to system bus 0 (find more [here](https://www.google.com/search?q=how+does+opencv+index+input+devices))

# libraries used
- selenium
- google mediapipe

# Google MediaPipe models
**Gesture Recognizer**\
*comes packaged with hand landmarker*\
[download latest](https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task)\
[docs](https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer)

**Hand Landmarker**\
*individual model used in testing*\
[download latest](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task)\
[docs](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)




### hours wasted on this project (increment counter before commiting)
- 18.5