# 2024/4/17 v2.2 added high rpm hold when driving intensively with sports mode and beautified the code
# By GinoLin980
import socket, struct, os
import keyboard, time
from inputimeout import inputimeout
import GUI

VERSION = "v2.2"

# initializing all the variables
UDP_IP = "127.0.0.1"  # This sets server ip to localhost
UDP_PORT = 8000  # You can freely edit this


gas = 0
brake = 0
gear = 0
rpm = 0
speed = 0
slip = False

wait_time_between_downshifts = 0.8
last_shift_time = 0
last_upshift_time = 0
last_downshift_time = 0
kickdown = False
jump_gears = 0
sports_high_rpm = False
sports_high_rpm_time = 0
PREVENT = last_downshift_time + 1.2

aggressiveness = 0
last_inc_aggr_time = 0

# define the settings for different driving modes
# 0 index is : used in aggressiveness increase decision
# 1 index is : used in aggressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time
MODES = {
    "Normal": [0.95, 0.35, 12, 0.12],
    "Sports": [0.8, 0.4, 24, 0.35],
    "Eco": [1, 0.35, 6, 0.12],
    "Manual": [0, 0, 0, 0]
}
gas_thresholds = MODES["Normal"]  # Normal drive mode
current_drive_mode = "D"

# for main func
condition = {"stop": False, "UDP_started": False}

shift_status = 0

### tkinter section
APP = GUI.FHRG_GUI(condition=condition, VERSION=VERSION)


def UDPconnectable(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Timeout after 1 second
    try:
        sock.connect((ip, port))
        sock.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        sock.close()

def updateDataForTk():
    # we don't analyze these var if we are in manual mode, so we get data again
    gas = rt["Accel"] / 255
    brake = rt["Brake"] / 255
    gear = rt["Gear"]
    
    gear_value = f"{current_drive_mode}{gear}" if gear != 0 else "R"

    # Update the labels
    gas_label.config(text=f"Gas: {int(gas * 100)}%", background="black", font=("Courier", 20), fg="white")
    brake_label.config(text=f"Brake: {int(brake * 100)}%", background="black", font=("Courier", 20), fg="white")
    gear_label.config(text=f"Gear: {gear_value}", background="black", font=("Courier", 20), fg="white")
    quitButton.config(text="Quit", fg="white", bg="gray", command=tkQuit)
    # Update the progress bars
    gas_progress["value"] = gas
    brake_progress["value"] = brake

    # Use after() to periodically call updateDataForTk() function
    APP.after(10, updateDataForTk)  # Update every second


### Horizon section
## get data 
# reading data and assigning names to data types in data_types dict. this is from official Forza Forum
data_types = {
    "IsRaceOn": "s32",
    "TimestampMS": "u32",
    "EngineMaxRpm": "f32",
    "EngineIdleRpm": "f32",
    "CurrentEngineRpm": "f32",
    "AccelerationX": "f32",
    "AccelerationY": "f32",
    "AccelerationZ": "f32",
    "VelocityX": "f32",
    "VelocityY": "f32",
    "VelocityZ": "f32",
    "AngularVelocityX": "f32",
    "AngularVelocityY": "f32",
    "AngularVelocityZ": "f32",
    "Yaw": "f32",
    "Pitch": "f32",
    "Roll": "f32",
    "NormalizedSuspensionTravelFrontLeft": "f32",
    "NormalizedSuspensionTravelFrontRight": "f32",
    "NormalizedSuspensionTravelRearLeft": "f32",
    "NormalizedSuspensionTravelRearRight": "f32",
    "TireSlipRatioFrontLeft": "f32",
    "TireSlipRatioFrontRight": "f32",
    "TireSlipRatioRearLeft": "f32",
    "TireSlipRatioRearRight": "f32",
    "WheelRotationSpeedFrontLeft": "f32",
    "WheelRotationSpeedFrontRight": "f32",
    "WheelRotationSpeedRearLeft": "f32",
    "WheelRotationSpeedRearRight": "f32",
    "WheelOnRumbleStripFrontLeft": "s32",
    "WheelOnRumbleStripFrontRight": "s32",
    "WheelOnRumbleStripRearLeft": "s32",
    "WheelOnRumbleStripRearRight": "s32",
    "WheelInPuddleDepthFrontLeft": "f32",
    "WheelInPuddleDepthFrontRight": "f32",
    "WheelInPuddleDepthRearLeft": "f32",
    "WheelInPuddleDepthRearRight": "f32",
    "SurfaceRumbleFrontLeft": "f32",
    "SurfaceRumbleFrontRight": "f32",
    "SurfaceRumbleRearLeft": "f32",
    "SurfaceRumbleRearRight": "f32",
    "TireSlipAngleFrontLeft": "f32",
    "TireSlipAngleFrontRight": "f32",
    "TireSlipAngleRearLeft": "f32",
    "TireSlipAngleRearRight": "f32",
    "TireCombinedSlipFrontLeft": "f32",
    "TireCombinedSlipFrontRight": "f32",
    "TireCombinedSlipRearLeft": "f32",
    "TireCombinedSlipRearRight": "f32",
    "SuspensionTravelMetersFrontLeft": "f32",
    "SuspensionTravelMetersFrontRight": "f32",
    "SuspensionTravelMetersRearLeft": "f32",
    "SuspensionTravelMetersRearRight": "f32",
    "CarOrdinal": "s32",
    "CarClass": "s32",
    "CarPerformanceIndex": "s32",
    "DrivetrainType": "s32",
    "NumCylinders": "s32",
    "HorizonPlaceholder": "hzn",
    "PositionX": "f32",
    "PositionY": "f32",
    "PositionZ": "f32",
    "Speed": "f32",
    "Power": "f32",
    "Torque": "f32",
    "TireTempFrontLeft": "f32",
    "TireTempFrontRight": "f32",
    "TireTempRearLeft": "f32",
    "TireTempRearRight": "f32",
    "Boost": "f32",
    "Fuel": "f32",
    "DistanceTraveled": "f32",
    "BestLap": "f32",
    "LastLap": "f32",
    "CurrentLap": "f32",
    "CurrentRaceTime": "f32",
    "LapNumber": "u16",
    "RacePosition": "u8",
    "Accel": "u8",
    "Brake": "u8",
    "Clutch": "u8",
    "HandBrake": "u8",
    "Gear": "u8",
    "Steer": "s8",
    "NormalizedDrivingLine": "s8",
    "NormalizedAIBrakeDifference": "s8",
}

# assigning sizes in bytes to each variable type
jumps = {
    "s32": 4,  # Signed 32bit int, 4 bytes of size
    "u32": 4,  # Unsigned 32bit int
    "f32": 4,  # Floating point 32bit
    "u16": 2,  # Unsigned 16bit int
    "u8": 1,  # Unsigned 8bit int
    "s8": 1,  # Signed 8bit int
    "hzn": 12,  # Unknown, 12 bytes of.. something
}

def get_data(data):
    return_dict = {}

    # additional var
    passed_data = data

    for i in data_types:
        d_type = data_types[i]  # checks data type (s32, u32 etc.)
        jump = jumps[d_type]  # gets size of data
        current = passed_data[:jump]  # gets data

        decoded = 0
        # complicated decoding for each type of data
        if d_type == "s32":
            decoded = int.from_bytes(current, byteorder="little", signed=True)
        elif d_type == "u32":
            decoded = int.from_bytes(current, byteorder="little", signed=False)
        elif d_type == "f32":
            decoded = struct.unpack("f", current)[0]
        elif d_type == "u16":
            decoded = struct.unpack("H", current)[0]
        elif d_type == "u8":
            decoded = struct.unpack("B", current)[0]
        elif d_type == "s8":
            decoded = struct.unpack("b", current)[0]

        # adds decoded data to the dict
        return_dict[i] = decoded
        # removes already read bytes from the variable
        passed_data = passed_data[jump:]

    # returns the dict
    return return_dict

## analyze and decision section
def analyzeInput():
    # if you need other types of data, they can be found at the dict data_types
    global gas, brake, gear, slip, idleRPM, kickdown, max_shift_rpm, shift_status, rpm_range_size, rpm_range_top, rpm_range_bottom,  aggressiveness, last_inc_aggr_time, sports_high_rpm, sports_high_rpm_time
    shift_status = 0
    # transform gas and value into 0 to 1
    gas = rt["Accel"] / 255
    brake = rt["Brake"] / 255
    gear = rt["Gear"]

    idleRPM = rt["EngineIdleRpm"]
    rpm_range_size = (rt["EngineMaxRpm"] - rt["EngineIdleRpm"]) / 3
    rpm_range_top = rt["EngineMaxRpm"]
    max_shift_rpm = rt["EngineMaxRpm"] * 0.86  # change this value if it is not capable to upshift on your car, especially for some trucks.

    # compute a new aggressiveness level depending on the gas and brake pedal pressure
    # and apply a factor from the current driving mode gas_thresholds = [0.95, 0.4, 12, 0.15]
    new_aggr = min(
        1,
        max(
            (gas - gas_thresholds[1]) / (gas_thresholds[0] - gas_thresholds[1]) * 1.5,
            (brake - (gas_thresholds[1] - 0.3)) / (gas_thresholds[0] - gas_thresholds[1]) * 1.6
        )
    )

    # new_aggr = min(1, (gas - gas_thresholds[drive_mode][1]) / (gas_thresholds[drive_mode][0] - gas_thresholds[drive_mode][1]))
    # ex full accel: 1, (1 - 0.35) / (0.95 - 0.35)*1.5
    # 1, 1.083

    # if the newly computed aggressiveness is higher than the previous one
    if new_aggr > aggressiveness and gear > 0:
        # we update it with the new one
        aggressiveness = new_aggr
        # and save the time at which we updated it
        last_inc_aggr_time = time.time()

    # if we have not increased the aggressiveness for at least 4 seconds
    if time.time() > last_inc_aggr_time + 4:
        # we lower the aggressiveness by a factor given by the current driving move
        aggressiveness -= 1 / gas_thresholds[2]

    # we maintain a minimum aggressiveness defined by the current driving mode
    # it's only used by the sport mode, to maintain the aggressiveness always above 0.5
    # all other driving modes will use the actual computed aggressiveness
    # (which can be below 0.5)
    aggressiveness = max(aggressiveness, gas_thresholds[3])

    # adjust the allowed upshifting rpm range,
    # depending on the aggressiveness
    rpm_range_top = idleRPM + 950 + ((max_shift_rpm - idleRPM - 300) * aggressiveness * 0.9)

    # adjust the allowed downshifting rpm range,
    # depending on the aggressiveness
    rpm_range_bottom = max(idleRPM + (min(gear, 6) * 70), rpm_range_top - rpm_range_size)

    if (
           rt["TireSlipRatioFrontLeft"] > 1
        or rt["TireSlipRatioFrontRight"] > 1
        or rt["TireSlipRatioRearLeft"] > 1
        or rt["TireSlipRatioRearRight"] > 1
    ):
        slip = True
    else:
        slip = False

    # (intense driving situation)
    # if we are in sports mode and the gas input is more than 60%, we want it to maintain at high rpm but not upshift when given little gas.
    if current_drive_mode is "S" and gas > 0.6:
        sports_high_rpm = True
        sports_high_rpm_time = time.time()
    # and reset it after 5 sec.
    if time.time() - sports_high_rpm_time > 5:
        sports_high_rpm = False
        
    # allow another continuous downshift after 2 sec
    if time.time() > last_downshift_time + 2:
        kickdown = False


def makeDecision():
    global gear, rpm, speed, kickdown, jump_gears, PREVENT, last_downshift_time, wait_time_between_downshifts

    speed = rt["Speed"]
    rpm = rt["CurrentEngineRpm"]

    if kickdown == False:
        # when braking we allow quick followup of downshift, but not when accelerating
        if brake > 0:
            wait_time_between_downshifts = 0.2
        elif brake == 0:
            wait_time_between_downshifts = 0.7

    ## gear changing section
    # not changing gear
    if (
        # we have already shifted in the last 0.1s
        time.time() < last_shift_time + 0.1
        or
        # or we are in neutral or reverse
        gear < 1
        or
        # or we have already shifted up in the last 1.3 sec
        time.time() < last_upshift_time + 1.3
        or
        # or we have already shifted down in the last 0.7 sec
        time.time() < last_downshift_time + wait_time_between_downshifts
    ):  # do not change gear
        return

    # upshift logic
    if (
        # we have reached the top range (upshift are rpm-allowed)
        rpm > rpm_range_top
        and
        # we are not slipping
        not slip
        and
        # we have not downshifted in the last 1.2 sec (to prevent up-down-up-down-up-down)
        time.time() > PREVENT
        and
        # we are not on the brakes
        brake == 0
        and
        # we are not coasting either
        gas > 0
        and
        # we are above 15km/h # speed value in FH is really weird, 4 equals 15km/h
        speed > 4
        # count means we can slowly accelerate like we do in real car
        # or count == 300
    ):
        # if we are in high rpm(normally 5X00 rpm) and lower than the maximum rpm, have been intensively driving and in sports mode.
        if rpm > rpm_range_size * 2 and rpm < max_shift_rpm - 500 and sports_high_rpm:
            if current_drive_mode == "S":
                return
        
        # actually UPSHIFT
        shiftUp()
        # reset the shift prevention time back to 1.2
        PREVENT = last_downshift_time + 1.2

    # downshift logic
    elif (
        # we have reached the lower rpm range (downshift are rpm-allowed)
        rpm < rpm_range_bottom
        and 
        not slip
        and
        # we are not in first gear (meaning we have gears available bellow us)
        gear > 1
        and
        # we have not downshifted in the last 0.7 sec
        time.time() > last_downshift_time + wait_time_between_downshifts
        and
        # prevent from over downshift 
        not rpm > rpm_range_size * 2.3
        and
        # depending on which gears we'll end up into
        (
            # we are NOT about to downshift into 1st, we can allow it
            gear > 2
            or (
                # we must be very very aggressive to allow that to happen
                # or be very very slow (less than 15km/h, which is always ok)
                # we are about to downshift into 1st.
                (gear == 2 and (aggressiveness >= 0.95 or speed <= 4))
                # we are in an overdrive gear # we are braking
                or (gear >= 4 and brake > 0)
            )
        )
    ):
        # allow several times of downshift in a row if we are giving heavy gas at low rpm
        if kickdown == False and gas > 0.65 and rpm < rpm_range_size * 2 and gear >  4:
            kickdown = True
            PREVENT = 0
            jump_gears = int((rpm_range_size * 3.8) // rpm)
            for i in range(jump_gears):
                #prevent from jumping too many gears
                if gear > 2:
                    shiftDown()
                    time.sleep(0.03)
                    gear -= 1
                else:
                    return
        # ignore if we are kicking down, we put it here but not in not changing gears for allowing upshift and ignore the downshift below
        if kickdown is True:
            return
        else:
            shiftDown()


def shiftUp():
    global last_shift_time, last_upshift_time, shift_status

    # shift up by press e
    keyboard.press_and_release("e")
    # update the last shifting times
    last_shift_time = time.time()
    last_upshift_time = time.time()
    shift_status = 1


def shiftDown():
    global last_shift_time, last_downshift_time, shift_status

    # shift down by press q
    keyboard.press_and_release("q")
    # update the last shifting times
    last_shift_time = time.time()
    last_downshift_time = time.time()
    shift_status = -1


# to change the drive mode during drive
def mode_changer():
    global gas_thresholds, current_drive_mode
    if keyboard.is_pressed("7"):
        os.system("cls")
        print("Normal Mode")
        current_drive_mode = "D"
        gas_thresholds = MODES["Normal"]
    elif keyboard.is_pressed("8"):
        os.system("cls")
        print("Sports Mode")
        current_drive_mode = "S"
        gas_thresholds = MODES["Sports"]
    elif keyboard.is_pressed("9"):
        os.system("cls")
        print("Eco Mode")
        current_drive_mode = "E"
        gas_thresholds = MODES["Eco"]
    elif keyboard.is_pressed("0"):
        os.system("cls")
        print("Manual Mode")
        current_drive_mode = "M"
        gas_thresholds = MODES["Manual"]

# select model in the beginning of the program
def mode_selector():
    global current_drive_mode, gas_thresholds
    try:
        answer = inputimeout(prompt="Mode: ", timeout=10)  # to wait user input
        os.system("cls")
        if answer == "":
            gas_thresholds = MODES["Normal"]  # Normal Mode
            print("Normal Mode")
            current_drive_mode = "D"
        elif answer == "s" or answer == "S":
            gas_thresholds = MODES["Sports"]  # Sports Mode
            print("Sports Mode")
            current_drive_mode = "S"
        elif answer == "e" or answer == "E":
            gas_thresholds = MODES["Eco"]  # Eco Mode
            print("Eco Mode")
            current_drive_mode = "E"
        elif answer == "m" or answer == "M":
            gas_thresholds = MODES["Manual"]  # Eco Mode
            print("Manual Mode")
            current_drive_mode = "M"
    except:
        os.system("cls")
        gas_thresholds = MODES["Normal"]  # Normal Mode
        print("Normal Mode")
        current_drive_mode = "D"


def pause():
    global stop
    if keyboard.is_pressed("`"):
        os.system("cls")
        print("You stopped the program, press \\ again to resume.")
        print("press ESC to quit the program")
        while True:
            if keyboard.is_pressed("\\"):
                print("Resumed.")
                break
            elif keyboard.is_pressed("esc"):
                print("Quitting...")
                stop["stop"] = True

def statement():
    print("OTHER LETTERS OR TIMEOUT WILL HAVE NORMAL MODE")
    print("\nMAKE SURE THAT THE SHIFTING IS BOUND TO 'Q' AND 'E'")
    print("press ` (under the esc) to stop the program")
    print("you can change the mode between Normal, Sports, Eco and Manual by hitting 7, 8, 9 ,0 ")

def main():
    global rt, addr, started

    # setting up an udp server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP

    print(f"PLEASE OPEN UP THE GAME FIRST")
    print("AND MAKE SURE THAT THE SHIFTING IS BOUND TO 'Q' AND 'E'")
    print(f"PLEASE SET THE OUTPUT IP TO {UDP_IP}")
    print(f"AND THE PORT TO {UDP_PORT}")
    APP.update()
    while not UDPconnectable(UDP_IP, UDP_PORT):
        if condition["stop"]:
            quit()
        APP.update()
    condition["UDP_started"] = True
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1500)
    rt = get_data(data)
    
    os.system("cls")
    print("WORKED\n\n")

    statement()


    while True:
        pause()
        # choosing modes by hitting 7, 8, 9, 0
        mode_changer()

        data, addr = sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket
        # received data is now in the returned_data dict
        rt = get_data(data)

        if condition["stop"]:
            quit()
        APP.update_idletasks()
        APP.update()

        # stop calculation if the mode is in manual
        if current_drive_mode == "M":
            continue
        # stop calculation if we are in menu or not driving
        if rt["IsRaceOn"] == 0:
            continue
        
        
        # actually compute and make decision
        analyzeInput()
        makeDecision()
        
if __name__ == "__main__":
    main()