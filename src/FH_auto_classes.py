# 2024/8/28 v2.3.2 added dyno and instance. wait for testing
# By GinoLin980
import sys; sys.dont_write_bytecode = True # prevent the generation of .pyc files
import socket
import keyboard, time
from DATAOUT import *
import GUI
from dyno import *

# the splash photo when startup
try:
    import pyi_splash # type: ignore
    pyi_splash.close()
except ImportError:
    pass

class Gearbox():
    def __init__(self) -> None:
        self.VERSION: str = "v2.3.1"
        
        # Network
        self.UDP_IP: str = "127.0.0.1"  # This sets server ip to localhost
        self.UDP_PORT: int = 8000  # You can freely edit this
        
        # Store data for cross file data
        self.RETURNED_DATA: dict

        # Car information
        self.gas: float = 0 # originally 0~255, transformed into 0~1
        self.brake: float # originally 0~255, transformed into 0~1
        self.gear: int # 0(reverse)~n gear
        self.slip: bool

        # Decision information
        self.kickdown: bool
        self.jump_gears: float
        self.sports_high_rpm: bool
        self.sports_high_rpm_time: float = time.time()
        self.last_shift_time: float = 0
        self.last_upshift_time: float = 0
        self.last_downshift_time: float = 0
        # self.toggle_cruise_control: bool = False
        # self.cruise_control_target: int = -1

        self.aggressiveness: float = 0
        self.last_inc_aggr_time: float = 0

        self.PREVENT: float = self.last_downshift_time + 1.2
        self.WAIT_TIME_BETWEEN_DOWNSHIFTS: float

        self.run_dyno = False

        # define the settings for different driving modes
        # 0 index is : used in aggressiveness increase decision
        # 1 index is : used in aggressiveness increase decision
        # 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
        # 3 index is : the bare minimum aggressiveness to keep at any given time
        self.MODES: dict[str, list[float]] = {
            "Normal": [0.95, 0.35, 12, 0.12],
            "Sports": [0.8, 0.4, 24, 0.35],
            "Eco": [1, 0.35, 6, 0.12],
            "Manual": [0, 0, 0, 0]
        }
        self.gas_thresholds: list[float] = self.MODES["Normal"]  # Normal drive mode
        self.current_drive_mode: str = "D" # ["D",  "S", "E", "M"]
        
        # GUI information
        # A dictionary for that stores settings across the python files
        self.condition: dict[str, bool|float|str|int] = {
            "stop": False, "UDP_started": False, 
            "gas": 0, "brake": 0, "drive_mode": "D", "gear": 0,
            "run_dyno": False, "dyno_data": {"rpm": 0, "hp": 0, "torque": 0}
            }
        self.APP = GUI.FHRG_GUI(condition=self.condition, VERSION=self.VERSION)

    def analyzeInput(self) -> None:
        """This is the function analyze and assign all variable needed in decision making"""
        # if you need other types of data, they can be found at the dict data_types

        # transform gas and value into 0 to 1
        self.gas = self.RETURNED_DATA["Accel"] / 255
        self.brake = self.RETURNED_DATA["Brake"] / 255
        self.gear = self.RETURNED_DATA["Gear"]

        idleRPM: float = self.RETURNED_DATA["EngineIdleRpm"]
        # max rpm
        if self.RETURNED_DATA["EngineMaxRpm"] <= 5000: # define a new max rpm for low rpm cars
            if self.current_drive_mode == "S":
                self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.65
            else:
                self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.6
        else:
            self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.86
        self.rpm_range_size: float = (self.RETURNED_DATA["EngineMaxRpm"] - idleRPM) / (3 if self.max_shift_rpm > 4000 and self.max_shift_rpm < 8000 else 5)
        
        # compute a new aggressiveness level depending on the gas and brake pedal pressure
        # and apply a factor from the current driving mode gas_thresholds = [0.95, 0.4, 12, 0.15]
        new_aggr = min(
            1,
            max(
                (self.gas - self.gas_thresholds[1]) / (self.gas_thresholds[0] - self.gas_thresholds[1]) * 1.5,
                (self.brake - (self.gas_thresholds[1] - 0.3)) / (self.gas_thresholds[0] - self.gas_thresholds[1]) * 1.6
            )
        )

        # new_aggr = min(1, (gas - gas_thresholds[drive_mode][1]) / (gas_thresholds[drive_mode][0] - gas_thresholds[drive_mode][1]))
        # ex full accel: 1, (1 - 0.35) / (0.95 - 0.35)*1.5
        # 1, 1.083

        # if the newly computed aggressiveness is higher than the previous one
        if new_aggr > self.aggressiveness and self.gear > 0:
            # we update it with the new one
            self.aggressiveness = new_aggr
            # and save the time at which we updated it
            self.last_inc_aggr_time = time.time()

        # if we have not increased the aggressiveness for at least 4 seconds
        if time.time() > self.last_inc_aggr_time + 4:
            # we lower the aggressiveness by a factor given by the current driving move
            self.aggressiveness -= 1 / self.gas_thresholds[2]

        # we maintain a minimum aggressiveness defined by the current driving mode
        # it's only used by the sport mode, to maintain the aggressiveness always above 0.5
        # all other driving modes will use the actual computed aggressiveness
        # (which can be below 0.5)
        self.aggressiveness = max(self.aggressiveness, self.gas_thresholds[3])

        # adjust the allowed upshifting rpm range,
        # depending on the aggressiveness
        self.rpm_range_top = idleRPM + 950 + ((self.max_shift_rpm - idleRPM - 300) * self.aggressiveness * 0.9)

        # adjust the allowed downshifting rpm range,
        # depending on the aggressiveness
        self.rpm_range_bottom = max(idleRPM + (min(self.gear, 6) * 70), self.rpm_range_top - self.rpm_range_size)

        # (slip condition)
        if (
            self.RETURNED_DATA["TireSlipRatioFrontLeft"] > 1
            or self.RETURNED_DATA["TireSlipRatioFrontRight"] > 1
            or self.RETURNED_DATA["TireSlipRatioRearLeft"] > 1
            or self.RETURNED_DATA["TireSlipRatioRearRight"] > 1
        ):
            self.slip = True
        else:
            self.slip = False

        # (intense driving situation)
        # if we are in sports mode and the gas input is more than 60%, we want it to maintain at high rpm but not upshift when given little gas.
        if self.current_drive_mode == "S" and self.gas > 0.6:
            self.sports_high_rpm = True
            self.sports_high_rpm_time = time.time()
        # and reset it after 5 sec.
        if time.time() - self.sports_high_rpm_time > 5:
            self.sports_high_rpm = False
            
        # allow another continuous downshift after 2 sec
        if time.time() > self.last_downshift_time + 2:
            self.kickdown = False

    def makeDecision(self) -> None:
        """Main logic of the whole program"""
        speed: float = self.RETURNED_DATA["Speed"]
        rpm: float = self.RETURNED_DATA["CurrentEngineRpm"]

        if self.kickdown == False:
            # when braking we allow quick followup of downshift, but not when accelerating
            if self.brake > 0:
                self.WAIT_TIME_BETWEEN_DOWNSHIFTS = 0.2
            elif self.brake == 0:
                self.WAIT_TIME_BETWEEN_DOWNSHIFTS = 0.7

        ## gear changing section
        # not changing gear
        if (
            # we have already shifted in the last 0.2s
            time.time() < self.last_shift_time + 0.2
            or
            # or we are in neutral or reverse
            self.gear < 1
            or
            # or we have already shifted up in the last 1.3 sec
            time.time() < self.last_upshift_time + 1.3
            or
            # or we have already shifted down in the last 0.7 sec
            time.time() < self.last_downshift_time + self.WAIT_TIME_BETWEEN_DOWNSHIFTS
        ):  # do not change gear
            return

        # upshift logic
        if (
            # we have reached the top range (upshift are rpm-allowed)
            rpm > self.rpm_range_top
            and
            # we are not slipping
            not self.slip
            and
            # we have not downshifted in the last 1.2 sec (to prevent up-down-up-down-up-down)
            time.time() > self.PREVENT
            and
            # we are not on the brakes
            self.brake == 0
            and
            # we are not coasting either
            self.gas > 0
            and
            # we are above 15km/h # speed value in FH is really weird, 4 equals 15km/h
            speed > 4
            # count means we can slowly accelerate like we do in real car
            # or count == 300
        ):
            # if we are in high rpm(normally 5X00 rpm) and lower than the maximum rpm, have been intensively driving and in sports mode.
            if rpm > self.rpm_range_size * 2 and rpm < self.max_shift_rpm - 500 and self.sports_high_rpm:
                if self.current_drive_mode == "S":
                    return  # do not upshift in this situation
            
            # actually UPSHIFT
            self.shiftUp()
            # reset the shift prevention time back to 1.2 (this is for continuous downshift)
            self.PREVENT = self.last_downshift_time + 1.2

        # downshift logic
        elif (
            # we have reached the lower rpm range (downshift are rpm-allowed)
            rpm < self.rpm_range_bottom
            and 
            not self.slip
            and
            # we are not in first gear (meaning we have gears available bellow us)
            self.gear > 1
            and
            # we have not downshifted in the last 0.7 sec
            time.time() > self.last_downshift_time + self.WAIT_TIME_BETWEEN_DOWNSHIFTS
            and
            # prevent from over downshift 
            not rpm > self.rpm_range_size * 2.3
            and
            # depending on which gears we'll end up into
            (
                # we are NOT about to downshift into 1st, we can allow it
                self.gear > 2
                or (
                    # we must be very very aggressive to allow that to happen
                    # or be very very slow (less than 15km/h, which is always ok)
                    # we are about to downshift into 1st.
                    (self.gear == 2 and (self.aggressiveness >= 0.95 or speed <= 4))
                    # we are in an overdrive gear # we are braking
                    or (self.gear >= 4 and self.brake > 0)
                )
            )
        ):
            # allow several times of downshift in a row if we are giving heavy gas at low rpm
            if self.kickdown == False and self.gas > 0.7 and rpm < self.rpm_range_size * 2 and self.gear >  4:
                self.kickdown = True
                self.PREVENT = 0 # allow instant upshift if the rpm reached
                jump_gears = int((self.rpm_range_size * 3.8) // rpm) # how many times we will jump down
                for _ in range(jump_gears):
                    #prevent from jumping too many gears
                    if self.gear > 2:
                        self.shiftDown()
                        time.sleep(0.03)
                        self.gear -= 1 # keep track of the gear in the loop
                    else:
                        break
            # ignore if we are kicking down, we put it here but not in not changing gears for allowing upshift and ignore the downshift below
            if self.kickdown:
                return
            self.shiftDown()

    def shiftUp(self) -> None:
        # shift up by press e
        keyboard.press_and_release("e")
        # update the last shifting times
        self.last_shift_time = time.time()
        self.last_upshift_time = time.time()


    def shiftDown(self) -> None:
        # shift down by press q
        keyboard.press_and_release("q")
        # update the last shifting times
        self.last_shift_time = time.time()
        self.last_downshift_time = time.time()


    # to change the drive mode during drive
    def mode_changer(self) -> None:
        """Detect keyboard press to change driving mode"""
        if keyboard.is_pressed("7"):
            # os.system("cls")
            # print("Normal Mode")
            self.current_drive_mode = "D"
            self.gas_thresholds = self.MODES["Normal"]
        elif keyboard.is_pressed("8"):
            # os.system("cls")
            # print("Sports Mode")
            self.current_drive_mode = "S"
            self.gas_thresholds = self.MODES["Sports"]
        elif keyboard.is_pressed("9"):
            # os.system("cls")
            # print("Eco Mode")
            self.current_drive_mode = "E"
            self.gas_thresholds = self.MODES["Eco"]
        elif keyboard.is_pressed("0"):
            # os.system("cls")
            # print("Manual Mode")
            self.current_drive_mode = "M"
            self.gas_thresholds = self.MODES["Manual"]

    def dyno_func(self):
        if keyboard.is_pressed("F1"):
                self.APP.dyno_page.show()
                self.run_dyno = True
        elif keyboard.is_pressed("F2"):
                self.APP.dyno.clear_chart()
        
        if self.run_dyno == True:
            if self.RETURNED_DATA["EngineMaxRpm"] <= 5000: # define a new max rpm for low rpm cars
                        if self.current_drive_mode == "S":
                            self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.65
                        else:
                            self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.6
            else:
                self.max_shift_rpm: float = self.RETURNED_DATA["EngineMaxRpm"] * 0.86


            if self.run_dyno and self.RETURNED_DATA["IsRaceOn"] != 0:
                if self.condition["gas"] > 0.8:
                    self.APP.dyno.add_new_power_data({"rpm": int(self.RETURNED_DATA["CurrentEngineRpm"]), "hp": self.RETURNED_DATA["Power"], "torque": self.RETURNED_DATA["Torque"]})
                    if self.RETURNED_DATA["CurrentEngineRpm"] > self.max_shift_rpm:
                        self.run_dyno = False

    def main(self) -> None:
        # wait for udp server to be ready
        while True:
            if self.condition["stop"]:
                sys.exit()
            self.APP.update()
            if UDPconnectable(self.UDP_IP, self.UDP_PORT):
                break

        # setting up an udp server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
        sock.bind((self.UDP_IP, self.UDP_PORT))
        data, _addr = sock.recvfrom(1500)
        self.RETURNED_DATA = get_data(data)
        
        self.condition["UDP_started"] = True
        self.condition["gas"] = 0
        self.condition["brake"] = 0
        self.condition["gear"] = 0
        self.condition["drive_mode"] = "D"
        self.APP.UDP_started(self.condition)

        self.APP.update_idletasks()
        self.APP.update()

        # main loop
        while True:
            # choosing modes by hitting 7, 8, 9, 0
            self.mode_changer()
            ready = select.select([sock], [], [], 3)  # Check if data is available (timeout is 3 seconds)
            if ready[0]:  # If data is available
                pass
            else:
                self.APP.quit()
                self.APP.destroy()
                sys.exit()

            data, _addr = sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket
            # received data is now in the returned_data dict
            self.RETURNED_DATA = get_data(data)
            self.condition["gas"] = self.RETURNED_DATA["Accel"] / 255
            self.condition["brake"] = self.RETURNED_DATA["Brake"] / 255
            self.condition["gear"] = self.RETURNED_DATA["Gear"]
            self.condition["drive_mode"] = self.current_drive_mode
            self.APP.update_home(self.condition)

            self.dyno_func()

            if self.condition["stop"]:
                sys.exit()

            self.APP.update()
            self.APP.update_idletasks()

            # stop calculation if we are in menu or not driving
            if self.RETURNED_DATA["IsRaceOn"] == 0:
                continue
            
            # stop calculation if the mode is in manual
            if not self.current_drive_mode == "M":
                # actually compute and make decision
                self.analyzeInput()
                self.makeDecision()
                
if __name__ == "__main__":
    FH_gearbox = Gearbox() # create an instance of the class
    FH_gearbox.main()
    sys.exit()

# these functions are for cruise control. but now it seems existing modules are using virtual gamepad, which brings negative expirience on real gamepad(interrupt with the signal)
    # def toggle_CC(self):
    #     if keyboard.is_pressed('c') and not self.toggle_cruise_control:
    #         self.toggle_cruise_control = True
    #         self.cruise_control_target = self.RETURNED_DATA['Speed']
    #     if keyboard.is_pressed('ctrl+c') and self.toggle_cruise_control:
    #         self.toggle_cruise_control = False
    #         self.cruise_control_target = -1