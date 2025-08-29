from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2
from time import perf_counter

aframe = None
FRAME_STATE = -1 #0 - processing 1 - ready -1 - empty
MODEL_PATH = "./src/models/gesture_recognizer.task" # "./hand_landmarker.task"
CAMERA_INPUT = 0
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    gestures_list = detection_result.gestures
    annotated_image = np.copy(rgb_image.numpy_view())

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
        annotated_image,
        hand_landmarks_proto,
        solutions.hands.HAND_CONNECTIONS,
        solutions.drawing_styles.get_default_hand_landmarks_style(),
        solutions.drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

    for idx in range(len(gestures_list)):
        # Draw recognized gesture on the image.
        cv2.putText(annotated_image, f"{gestures_list[idx][0].category_name}",
                    (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                    FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)



    return annotated_image

import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a hand landmarker instance with the live stream mode:
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    global aframe
    global FRAME_STATE
    FRAME_STATE = 0
    if result:
        print('gesture recognition result: {}'.format(result))
    aframe = draw_landmarks_on_image(output_image, result)
    FRAME_STATE = 1

def perf_counter_ms():
    return int(perf_counter() * 1000)

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH), #delegate=mp.tasks.BaseOptions.Delegate.GPU), # gpu not implemented for windows yet
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)
with GestureRecognizer.create_from_options(options) as recognizer:
    # Use OpenCV’s VideoCapture to start capturing from the webcam.
    start_time = perf_counter_ms()
    cap = cv2.VideoCapture(CAMERA_INPUT)

    # Create a loop to read the latest frame from the camera using VideoCapture#read()
    while cap.isOpened():
        _ , frame = cap.read()
        #image = cv2.flip(frame, 1)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert the frame received from OpenCV to a MediaPipe’s Image object.
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        
        # Send live image data to perform hand landmarks detection.
        # The results are accessible via the `result_callback` provided in
        # the `HandLandmarkerOptions` object.
        # The hand landmarker must be created with the live stream mode.
        if FRAME_STATE == -1:
            FRAME_STATE = 0
            recognizer.recognize_async(mp_image, perf_counter_ms() - start_time)
        if FRAME_STATE == 1:
            cv2.imshow('press Q to exit', cv2.cvtColor(aframe, cv2.COLOR_RGB2BGR))
            FRAME_STATE = -1
        if FRAME_STATE == 0:
            continue
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()