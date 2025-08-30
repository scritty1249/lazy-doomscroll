from mediapipe import solutions, Image
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2

# mostly for testing, but will add this as an optional feature in prod?
def annotate_image(image: Image, detection_result: "mediapipe.tasks.vision.GestureRecognizerResult", font_color: tuple = (88, 205, 54)):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    gestures_list = detection_result.gestures
    annotated_image = np.copy(image.numpy_view())
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
            solutions.drawing_styles.get_default_hand_connections_style()
        )

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - 10 # margin
        # Draw recognized gesture on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name} ({handedness[0].score * 100:.2f}%): {gestures_list[idx][0].category_name} ({gestures_list[idx][0].score * 100:.2f}%)",
            (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
            1, font_color, 1, cv2.LINE_AA)
    
    return annotated_image

def black_image(width_px: int, height_px: int, text: str = ""):
    font_face = cv2.FONT_HERSHEY_DUPLEX
    img = np.zeros((width_px, height_px, 3), dtype = np.uint8)
    text_width, text_height = cv2.getTextSize(text, font_face, 1, 1)[0]

    center_coords = (
        int(img.shape[1] / 2) - int(text_width / 2),
        int(img.shape[0] / 2) + int(text_height / 2)
    )
    cv2.putText(img, text, center_coords, font_face,
        1, (255, 0, 0), 1, cv2.LINE_AA)
    return img