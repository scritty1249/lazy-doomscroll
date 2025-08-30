# Module containing the class for Gesture recognition
import mediapipe
from collections import deque
from time import perf_counter
from typing import Union, Literal, Set

default_result_callback = lambda r, o, t: print('gesture recognition result: {}'.format(r))

HANDEDNESS_MASK = Literal[0, 1, 2, 3]
GESTURE_SET = set(["", "None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"])
class GestureModelWrapper(object):
    """Wrapper class for MediaPipe's Recognizer.

    Args:
        model_path (str): Filepath to the model.task file.
        result_callback (\
            Callable[\
                result:       mediapipe.tasks.vision.GestureRecognizerResult,\
                output_image: mediapipe.Image,\
                timestamp_ms: int\
            ]\
        ): Callback handler for processed images. Callback method will be called asynchronously, but does not need to be asynchronous.
        gpu_enabled (bool, optional): Delegate model recognition processing to the GPU. At time of writing, this feature is not available for Windows. Defaults to False.

    Returns:
        GestureModelWrapper object containing a GestureRecognizer instance.
    """
    # frame states
    EMPTY = -1
    PROCESSING = 0
    READY = 1

    def __init__(self, model_path: str, result_callback = default_result_callback, gpu_enabled = False):
        BaseOptions = mediapipe.tasks.BaseOptions
        GestureRecognizerOptions = mediapipe.tasks.vision.GestureRecognizerOptions
        base_options = BaseOptions(model_asset_path=model_path, delegate = mediapipe.tasks.BaseOptions.Delegate.GPU) if gpu_enabled else BaseOptions(model_asset_path = model_path)
        options = GestureRecognizerOptions(
            base_options = base_options,
            running_mode = mediapipe.tasks.vision.RunningMode.LIVE_STREAM,
            num_hands = 2,
            result_callback = self._result_callback_wrapper
        )
        self._result_callback = result_callback
        self.recognizer = mediapipe.tasks.vision.GestureRecognizer.create_from_options(options)
        self.last_gesture = "None"
        self.frame_state = self.EMPTY
        self.start_time = None
        self.last_callback_result = None
        
    def _result_callback_wrapper(self, *args, **kwargs):
        self.frame_state = self.READY
        self.last_callback_result = self._result_callback(*args, **kwargs)

    def process(self, mediapipe_image: mediapipe.Image):
        """
        Args:
            mediapipe_image (mediapipe.Image): MediaPipe format Image
        """
        self.frame_state = self.PROCESSING
        self.recognizer.recognize_async(mediapipe_image, self._get_time_ms())

    def _get_time_ms(self):
        if self.start_time is None:
            self.start_time = int(perf_counter() * 1000)
            return 0
        else:
            return int(perf_counter() * 1000) - self.start_time

    def close(self):
        self.recognizer.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

class GestureData(object):
    def __init__(self, gesture: str, duration_ms: int, handedness: int):
        """_summary_

        Args:
            gesture (str): _description_
            duration_ms (int): _description_
            handedness (Set[0, 1, 2, 3]): binary value, each bit corrosponds to each hand, right/left. False for both hands means either hand is accepted.
        """
        self.gesture = gesture
        self.duration = duration_ms # maximum time to consider the gesture, or how long it lasted

        self.handedness = handedness

    def check_handedness(self, hand: Set[Literal["Right", "Left"]]):
        return (
            (self.handedness == 1 and hand == set(["Right"])) # right only b01
            or (self.handedness == 2 and hand == set(["Left"])) # left only b10
            or (self.handedness == 3 and hand == set(["Right", "Left"])) # right and left b11
            or (self.handedness == 0 and (hand == set(["Left"]) or hand == set(["Right"]))) # right or left b00
        )

    def __repr__(self):
        return "<GestureData>%s" % str(self.__dict__)

    def __eq__(self, other): 
        if not isinstance(other, GestureData):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.gesture == other.gesture and self.duration == other.duration and (
            (self.handedness == 0 and other.handedness != 0 and other.handedness != 3) or (self.handedness == other.handedness and self.handedness != 0)
        )
    
    def __contains__(self, other):
        """Evaluates if the other GestureData object meets the criteria of this one."""
        if not isinstance(other, GestureData):
            return False
        return ((self.duration <= other.duration) and (
            (self.handedness == 0 and other.handedness != 0 and other.handedness != 3)
            or (self.handedness == other.handedness and self.handedness != 0))
            and self.gesture == other.gesture
        )

class GestureSequence(object):
    def __init__(self, dat: Union[dict, list, GestureData] = None, *data: Union[dict, list, GestureData]):
        self._data = list()
        if dat is not None:
            args = (dat, *data)
            if isinstance(dat, dict):
                for d in args:
                    self._data.append(GestureData(d["gesture"], d["duration"], d["handedness"]))
            elif isinstance(dat, list):
                for d in args:
                    self._data.append(GestureData(d[0], d[1], d[2]))
            elif isinstance(dat, GestureData):
                for d in args:
                    self._data.append(d)
            else:
                raise ValueError("Invalid input data type.")
        self._update_set()

    def __getitem__(self, index):
        if isinstance(index, slice):
            return GestureSequence(*self._data[index])
        else:
            return self._data[index]
    
    def __setitem__(self, index, value: GestureData):
        self._data[index] = value
        self._update_set()

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "<GestureSequence>%s" % str(self.__dict__)

    def __call__(self):
        return self._data

    def __iter__(self):
        for gesture_data in self._data:
            yield gesture_data
    
    def _update_set(self):
        self.gesture_set = set([]) if len(self._data) == 0 else set([gd.gesture for gd in self._data])

    def __eq__(self, other: "GestureSequence") -> bool:
        if not isinstance(other, GestureSequence):
            return False
        if (
            other.gesture_set != other.gesture_set
            or len(other) != len(self)
        ): return False
        idx = 0
        for gd in self._data:
            if gd != other[idx]:
                return False
            else:
                idx += 1
        return True

    def __contains__(self, other: "GestureSequence") -> bool:
        if not isinstance(other, GestureSequence):
            # don't attempt to compare against unrelated types
            return False
        size_diff = len(self) - len(other)
        if size_diff < 0:
            # cannot contain something bigger than itself
            return False
        if size_diff == 0:
            if self.gesture_set != other.gesture_set:
                return False
            else:
                for gd, other_gd in zip(self, other):
                    if gd not in other_gd:
                        return False
                return True
        else:
            for i in range(size_diff + 1):
                search_slice = self[i:len(other) + i]
                if search_slice.gesture_set != other.gesture_set:
                    continue
                for gd, other_gd in zip(search_slice, other):
                    if gd not in other_gd:
                        return False
                return True

class GestureTracker(object):
    """We do something finicky here to apply minimum duration for gestures.
    GestureTracker only evaulates/applies the minimum duration threshold when a new gesture is processed, or when sequence_view is called.
    because of this, it is imperative that getter methods be the only way data in GestureTracker is accessed.
    """
    
    def __init__(self, min_duration_ms: int, gesture_history_length: int, gesture_history_age_ms: int):
        self._min_duration = min_duration_ms
        self._history_age = gesture_history_age_ms
        self._data = deque([], maxlen = gesture_history_length)
        self._last_timestamp = 0
    
    def append(self, gesture: Union[str, None], hand: HANDEDNESS_MASK, timestamp_ms: int):
        """Adds a new gesture to the Tracker.

        Args:
            gesture (Union[str, None]): The name of the gesture.
            hand (Literal[0, 1, 2, 3]): Binary mask for what hand is performing the gesture.
            timestamp_ms (int): The timestamp in milliseconds.

        Raises:
            ValueError: If the gesture is not recognized as part of the gesture set.
        """        
        self.update_queue_age(timestamp_ms) # shouldnt matter if last timestamp is 0 since thats only when queue is already empty anyways
        gesture = str(gesture)
        if gesture not in GESTURE_SET:
            raise ValueError("%s is not a recognized gesture" % gesture)
        elif len(self._data) == 0:
            self._data.append(GestureData(gesture, 0, hand))
        else:
            if len(self) == self._data.maxlen:
                self._apply_duration_threshold()
            self._data[-1].duration += timestamp_ms - self._last_timestamp
            self._last_timestamp = timestamp_ms
            if self._data[-1].gesture != gesture:
                self._data.append(GestureData(gesture, 0, hand))
            
    def sequence_view(self):
        return GestureSequence(*(gd for gd in self() if gd.duration >= self._min_duration))

    def update_queue_age(self, timestamp_ms: int = 0): # wtf is this naming idk man
        """prune aged / old gestures from queue"""
        length = len(self)
        offset_ms = timestamp_ms - self._last_timestamp
        if length > 0:
            ages = [sum(g.duration for g in self()[i:]) + offset_ms for i in range(length)]
            for i in range(length):
                if ages[i] > self._history_age:
                    self._data.popleft()
                else:
                    # cut down on runtime- the ages get younger the more we loop- stop once we find one that doesnt expire yet
                    break
    def clear_queue(self):
        self.update_queue_age(self._last_timestamp + self._history_age + 1)

    def _apply_duration_threshold(self):
        length = len(self) 
        if length > 0:
            for i in range(length):
                temp = self._data.popleft()
                if temp.duration >= self._min_duration:
                    self._data.append(temp)
                elif i == length - 1: # removing last element, make sure it doesnt add onto a new element
                    # if we're removing the last element we now have space to add a new one, so this shouldnt be an issue
                    self._data.append(GestureData("", self._min_duration, 3))
                    self._last_timestamp = 0

    def __call__(self):
        return list(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "<GestureTracker>{'queue': %s, 'max_len': %d, 'min_duration_ms': %d, 'history_age_ms': %d}" % (str(self()), self._data.maxlen, self._min_duration, self._history_age)