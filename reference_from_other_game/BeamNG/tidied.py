from collections import deque
from typing import Dict, Any

class FromBeamNG:
    def __init__(self) -> None:
        self.WINDOW_SIZE = 3
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
        self.timer = {
            "aggressionHoldOffThrottleTimer": 0
        }
        self.timerConstants = {
            "aggressionHoldOffThrottleDelay": 2.25
        }
        self.lastAggressionThrottle = 0
        self.aggressionOverride = None
        self.shiftPoints = {}
        self.shiftBehavior = {
            "shiftUpAV": 0,
            "shiftDownAV": 0
        }
        self.controlLogicModule = {}
        self.shiftPreventionData = {
            "wheelSlipShiftDown": True,
            "wheelSlipShiftUp": True,
            "wheelSlipDownThreshold": 0.3,
            "wheelSlipUpThreshold": 0.1
        }

    def smoother(self, data_dict: Dict[str, deque[float]], window_size: int) -> Dict[str, float]:
        smoothed_value = {}
        for key, deque_data in data_dict.items():
            if len(deque_data) >= window_size:
                moving_avg = sum(deque_data) / window_size
                smoothed_value[key] = moving_avg
            else:
                smoothed_value[key] = 0.0
        return smoothed_value

    def updateAggression(self, dt: float, throttle: float, brake: float, wheelspeed: float, isSportModeActive: bool, usesKeyboard: bool) -> None:
        if throttle <= 0:
            self.timer["aggressionHoldOffThrottleTimer"] = max(self.timer["aggressionHoldOffThrottleTimer"] - dt, 0)
        else:
            self.timer["aggressionHoldOffThrottleTimer"] = self.timerConstants["aggressionHoldOffThrottleDelay"]

        brakeUse = brake > 0.25
        sportModeAdjust = 0.5 if isSportModeActive else 0

        if usesKeyboard:
            aggression = brakeUse and self.smoothed_value["drivingAggression"] or throttle * 1.333
            aggression = 0.75 if wheelspeed < 1 else aggression
            aggression = max(aggression, sportModeAdjust)
        else:
            throttleHold = throttle <= 0 and wheelspeed > 2 and (self.timer["aggressionHoldOffThrottleTimer"] > 0 or isSportModeActive)
            holdAggression = brakeUse or throttleHold
            dThrottle = min(max((throttle - self.lastAggressionThrottle) / dt, 1), 20)
            aggression = holdAggression and self.smoothed_value["drivingAggression"] or throttle * 1.333 * dThrottle
            aggression = 0.0 if wheelspeed < 1 else aggression
            aggression = max(aggression, sportModeAdjust)

        self.smoothed_value["drivingAggression"] = min(aggression, 1)
        self.smoothed_value["drivingAggression"] = self.aggressionOverride or self.smoothed_value["drivingAggression"]
        self.lastAggressionThrottle = throttle

    def select_shift_points(self, gear_index: int) -> None:
        aggression: float = min(max((self.smoothed_value["drivingAggression"] - 0.2) / 0.8, 0), 1)
        aggressionCoef = min(max(aggression * aggression, 0), 1)
        shiftPoint = self.shiftPoints.get(gear_index, {"lowShiftDownAV": 2000, "highShiftDownAV": 3500, "lowShiftUpAV": 2500, "highShiftUpAV": 5000})
        self.shiftBehavior["shiftDownAV"] = shiftPoint["lowShiftDownAV"] + (shiftPoint["highShiftDownAV"] - shiftPoint["lowShiftDownAV"]) * aggressionCoef
        self.shiftBehavior["shiftUpAV"] = shiftPoint["lowShiftUpAV"] + (shiftPoint["highShiftUpAV"] - shiftPoint["lowShiftUpAV"]) * aggressionCoef
        self.controlLogicModule["shiftBehavior"] = self.shiftBehavior

    def update_wheel_slip(self, dt: float, wheel_slip: float, ground_contact: bool) -> None:
        overallWheelSlip = wheel_slip
        groundContactCoef = 1 if ground_contact else 0

        self.shiftPreventionData["wheelSlipShiftDown"] = overallWheelSlip < self.shiftPreventionData["wheelSlipDownThreshold"] and groundContactCoef >= 1
        self.shiftPreventionData["wheelSlipShiftUp"] = overallWheelSlip < self.shiftPreventionData["wheelSlipUpThreshold"] and groundContactCoef >= 1

        self.controlLogicModule["shiftPreventionData"] = self.shiftPreventionData

    def make_decision(self, dt: float, throttle: float, brake: float, wheelspeed: float, gear: int, rpm: float, isSportModeActive: bool, usesKeyboard: bool) -> None:
        self.updateAggression(dt, throttle, brake, wheelspeed, isSportModeActive, usesKeyboard)
        self.select_shift_points(gear)
        self.update_wheel_slip(dt, wheelslip, ground_contact)

        if rpm > self.shiftBehavior["shiftUpAV"] and self.shiftPreventionData["wheelSlipShiftUp"]:
            self.shift_up()
        elif rpm < self.shiftBehavior["shiftDownAV"] and self.shiftPreventionData["wheelSlipShiftDown"]:
            self.shift_down()

    def shift_up(self) -> None:
        # Implement the logic to shift up
        pass

    def shift_down(self) -> None:
        # Implement the logic to shift down
        pass
