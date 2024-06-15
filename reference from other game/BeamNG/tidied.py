from collections import deque

class FromBeamNG():
    def __init__(self) -> None:
        self.WINDOW_SIZE = 3 # # define the size of deque length and moving average's window size
        self.original_value = {
            "throttle": deque([0, 0, 0], maxlen=self.WINDOW_SIZE),
            "brake": deque([0, 0, 0], maxlen=self.WINDOW_SIZE),
            "throttleInput": deque([0, 0, 0], maxlen=self.WINDOW_SIZE),
            "brakeInput": deque([0, 0, 0], maxlen=self.WINDOW_SIZE),
            "drivingAggression": deque([0, 0, 0], maxlen=self.WINDOW_SIZE),
            "throttleUpShiftThreshold": deque([0.05, 0.05, 0.05], maxlen=self.WINDOW_SIZE),
            "avgAV": deque([0, 0, 0], maxlen=self.WINDOW_SIZE)
            }
        self.smoothed_value = self.smoother(self.original_value, self.WINDOW_SIZE)
    
    def smoother(self, data_dict: dict[str, deque[float]], window_size: int) -> dict[str, float]:
        """
        Calculates the moving average for each deque in the input dictionary and stores the results in a new dictionary.

        Args:
            data_dict (dict[str, deque[float]]): A dictionary where the keys are strings and the values are deques of floats.
            window_size (int): The size of the moving average window.

        Returns:
            dict[str, float]: A dictionary where the keys are the same as the input dictionary, and the values are the moving averages.
        """
        smoothed_value = {}

        for key, deque_data in data_dict.items():
            if len(deque_data) >= window_size:
                moving_avg = sum(deque_data) / window_size
                smoothed_value[key] = moving_avg
            else:
                smoothed_value[key] = 0.0

        return smoothed_value

    def select_shift_points(gear_index: int) -> None:
        aggression: float = max(smoothed_value)