# Module containing the class for Gesture recognition
import mediapipe
from collections import deque
from time import perf_counter
from typing import Union

default_result_callback = lambda r, o, t: print('gesture recognition result: {}'.format(r))

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
    def __init__(self, gesture: str, duration_ms: int):
        self.gesture = gesture
        self.duration = duration_ms # maximum time to consider the gesture, or how long it lasted

    def __repr__(self):
        return "<GestureData>%s" % str(self.__dict__)

class GestureSequence(object):
    def __init__(self, dat: Union[dict, list, GestureData] = None, *data: Union[dict, list, GestureData]):
        self._data = list()
        if dat is not None:
            args = (dat, *data)
            if isinstance(dat, dict):
                for d in args:
                    self._data.append(GestureData(d["gesture"], d["duration"]))
            elif isinstance(dat, list):
                for d in args:
                    self._data.append(GestureData(d[0], d[1]))
            elif isinstance(dat, GestureData):
                for d in args:
                    self._data.append(d)
            else:
                raise ValueError("Invalid input data type.")
        self._update_set()

    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            return GestureSequence([
                self._data[i]
                for i in range(start, stop, step)
            ])
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
    
    def _update_set(self):
        self.gesture_set = set() if len(self._data) == 0 else set([gd.gesture for gd in self._data])

    def equals(self, sequence: "GestureSequence") -> bool:
        if (
            sequence.gesture_set != sequence.gesture_set
            or len(sequence) != len(self)
        ): return False
        idx = 0
        for gd in self._data:
            if (
                gd.gesture != sequence[idx].gesture
                or gd.duration < sequence[idx].duration
            ):
                return False
            else:
                idx += 1
        return True

    def contains(self, sequence: "GestureSequence") -> bool:
        size_diff = len(sequence) - len(self)
        if size_diff < 0: return False
        for i in range(size_diff):
            if self.equals(sequence[size_diff:len(self) + size_diff]): return True
        return False

class GestureTracker(object):
    GESTURES = set(["None", "Closed_Fist", "Open_Palm", "Pointing_Up", "Thumb_Down", "Thumb_Up", "Victory", "ILoveYou"])
    
    def __init__(self, min_duration_ms: int, gesture_history_length: int):
        self._min_duration = min_duration_ms
        self._data = deque([], maxlen = gesture_history_length)
        self.last_timestamp = 0
    
    def append(self, gesture: Union[str, None], timestamp_ms: int):
        duration_ms = self._min_duration + 1 if self.last_timestamp == 0 else timestamp_ms - self.last_timestamp
        gesture = str(gesture)
        if gesture not in self.GESTURES:
            raise ValueError("%s is not a recognized gesture" % gesture)
        if duration_ms >= self._min_duration:
            if len(self._data) > 0 and self._data[-1].gesture == gesture:
                self._data[-1].duration += duration_ms
            else:
                self.last_timestamp = timestamp_ms
                self._data.append(GestureData(gesture, duration_ms))
            
    def sequence_view(self):
        return GestureSequence(*self())

    def __call__(self):
        return list(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return str(self._data)