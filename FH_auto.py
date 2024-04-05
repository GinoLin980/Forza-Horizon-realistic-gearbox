# 2024/4/4 v2.1 fix continuous downshift
# The code of this project is mostly taken from other people's project. You can freely use and edit this code.
import socket, struct, os
import keyboard, time
from inputimeout import inputimeout
import tkinter as tk
from tkinter import ttk

# initializing all the variables
UDP_IP = "127.0.0.1"  # This sets server ip to localhost
UDP_PORT = 8000  # You can freely edit this

count = 0


gear = 0
gas = 0
brake = 0
rpm = 0
speed = 0
slip = False

waitTimeBetweenDownShifts = 0.8
lastShiftTime = 0
lastShiftUpTime = 0
lastShiftDownTime = 0
continuous_down = False
prevent = lastShiftDownTime + 1.2

last_inc_aggr_time = 0
aggressiveness = 0


sizecount = 0 
times = 0

# define the settings for different driving modes
# 0 index is : used in agressiveness increase decision
# 1 index is : used in agressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time
modes = {"Normal" : [0.95, 0.35, 12, 0.12],
         "Sports" : [0.8, 0.4, 24, 0.35],
         "Eco" : [1, 0.35, 6, 0.12],
         "Manual" : [0, 0, 0 ,0]}

gas_thresholds = modes["Normal"]  # Normal drive mode

currentMode = "D"


### tkinter section
root = tk.Tk()
root.attributes("-topmost", True)
s = ttk.Style()

root.configure(background='black')
s.theme_use('alt')
# gas bar
s.configure('green.Horizontal.TProgressbar', thoughcolor='white', background='green')
# brake bar
s.configure('blue.Horizontal.TProgressbar', thoughcolor='white', background='red')

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

def analyzeInput():
    # if you need other types of data, they can be found at the dict data_types
    global aggressiveness, last_inc_aggr_time, rpmRangeBottom, gas, brake, rpmRangeTop, rpmRangeBottom, rpmRangeSize, gear, idleRPM, slip

    # transform gas value into 0 to 1, because the original code is designed for Assetto Corsa
    gas = rt["Accel"] / 255
    brake = rt["Brake"] / 255

    rpmRangeTop = rt["EngineMaxRpm"]
    rpmRangeSize = (rt["EngineMaxRpm"] - rt["EngineIdleRpm"]) / 3
    maxShiftRPM = rt["EngineMaxRpm"] * 0.86  # change this value if it is not capable to upshift on your car, espacially for some trucks.
    idleRPM = rt["EngineIdleRpm"]
    gear = rt["Gear"]

    # compute a new aggressiveness level depending on the gas and brake pedal pressure
    # and apply a factor from the current driving mode gas_thresholds = [0.95, 0.4, 12, 0.15]
    new_aggr =  min(1,
                    max((gas - gas_thresholds[1]) / (gas_thresholds[0] - gas_thresholds[1])*1.5,
                        (brake - (gas_thresholds[1] - 0.3)) / (gas_thresholds[0] - gas_thresholds[1]) * 1.6))

    # new_aggr = min(1, (gas - gas_thresholds[drive_mode][1]) / (gas_thresholds[drive_mode][0] - gas_thresholds[drive_mode][1]))
    # ex full accel: 1, (0.3 - 0.95) / (0.95 - 0.4)
    # 1, 0.05 / 0.55 = 0.09

    # if the newly computed agressiveness is higher than the previous one
    if new_aggr > aggressiveness and gear > 0:
        # we update it with the new one
        aggressiveness = new_aggr
        # and save the time at which we updated it
        last_inc_aggr_time = time.time()

    # if we have not increased the agressiveness for at least 2 seconds
    if time.time() > last_inc_aggr_time + 4:
        # we lower the aggressiveness by a factor given by the current driving move
        aggressiveness -= 1 / gas_thresholds[2]

    # we maintain a minimum aggressiveness defined by the current driving mode
    # it's only used by the sport mode, to maintain the aggressiveness always above 0.5
    # all other driving modes will use the actual computed aggressiveness
    # (which can be bellow 0.5)
    aggressiveness = max(aggressiveness, gas_thresholds[3])

    # adjust the allowed upshifting rpm range,
    # depending on the aggressiveness
    rpmRangeTop = idleRPM + 950 + ((maxShiftRPM - idleRPM - 300) * aggressiveness * 0.9)

    # adjust the allowed downshifting rpm range,
    # depending on the aggressiveness
    rpmRangeBottom = max(idleRPM + (min(gear, 6) * 70), rpmRangeTop - rpmRangeSize)

    if rt["TireSlipRatioFrontLeft"] > 1 or rt["TireSlipRatioFrontRight"] > 1 or rt["TireSlipRatioRearLeft"]  > 1 or rt["TireSlipRatioRearRight"] > 1:
        slip = True
    else:
        slip = False

def makeDecision():
    global speed, rpm, gas, count, continuous_down, lastShiftDownTime, prevent, waitTimeBetweenDownShifts, sizecount, times, gear
    
    speed = rt["Speed"]
    rpm = rt["CurrentEngineRpm"]

    if continuous_down == False:
        # when braking we allow quick followup of downshift, but not when accelerating
        if brake > 0:
            waitTimeBetweenDownShifts = 0.4
        elif brake == 0:
            waitTimeBetweenDownShifts = 0.7
    # count means we can slowly accelerate like we do in real car
    # if rpm > rpmRangeTop - 700 and rpm > 700 and rt["Speed"] > 5 and gas > 0:
    #     count += 1
    

    if (
        # we have already shifted in the last 0.1s
        time.time() < lastShiftTime + 0.1
        or
        # or we are in neutral
        gear < 1
        or
        # or we have already shifted up in the last 1.3 sec
        time.time() < lastShiftUpTime + 1.3
        or
        # or we have already shifted down in the last 1.5 sec
        time.time() < lastShiftDownTime + waitTimeBetweenDownShifts
    ):

        # do not change gear
        return
    
    if (
        # we have reached the top range (upshift are rpm-allowed)
        rpm > rpmRangeTop
        and
        # we are not slipping
        not slip
        and
        # we have not downshifted in the last 1.2 sec (to prevent up-down-up-down-up-down)
        time.time() > prevent
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
        # actually UPSHIFT

        shiftUp()
        # reset the shift prevention time back to 1.2
        prevent = lastShiftDownTime + 2

    elif (
        # we have reached the lower rpm range (downshift are rpm-allowed)
        rpm < rpmRangeBottom
        and
        not slip
        and
        # we are not in first gear (meaning we have gears available bellow us)
        gear > 1
        and
        # we have not downshifted in the last 2 sec
        time.time() > lastShiftDownTime + waitTimeBetweenDownShifts
        and
        # depending on which gears we'll end up into
        (
            # we are NOT about to downshift into 1st, we can allow it
            gear > 2
            
            or (
                # we must be very vert aggressive to allow that to happen 
                # or be very very slow (less than 15km/h, which is always ok)
                # we are about to downshift into 1st. 
                (gear == 2 and (aggressiveness >= 0.95 or speed <= 4))
                # we are in an overdrive gear # we are braking       
                or (gear >= 4 and brake > 0) 
            )
        )
    ):
        # allow 3 times of downshift in a row
        if continuous_down == False and gas > 0.65 and rpm < rpmRangeSize * 2:
            continuous_down = True
            times = int((rpmRangeSize * 3.8) // rpm)
            
            prevent = 0
            for i in range(times):
                    
                    if gear > 2:
                        time.sleep(0.03)
                        shiftDown()
                        gear -= 1
                    else:
                        return
        if continuous_down is True:
            return
        else:
            shiftDown()
    
    # allow another continuous downshift after 4 sec
    if time.time() > lastShiftDownTime + 2:
        continuous_down = False
    
    # reset the count after shifting or we are not in the condition anymore
    # if count >= 300 or ((time.time() > lastShiftTime + 5 and rpm < 1900) or gas > 0.3):
    #     count = 0

def shiftUp():
    global lastShiftTime, lastShiftUpTime

    # shift up by press e
    keyboard.press_and_release("e")
    # update the last shifting times
    lastShiftTime = time.time()
    lastShiftUpTime = time.time()

def shiftDown():
    global lastShiftTime, lastShiftDownTime

    # shift down by press q
    keyboard.press_and_release("q")
    # update the last shifting times
    lastShiftTime = time.time()
    lastShiftDownTime = time.time()

def statement():
    # Choosing modes in terminal
    print("Timeout is 10 seconds")
    print("Type in S to have Sports Mode")
    print("Type in e to have Eco Mode")
    print("Enter to have Normal Mode")
    print("OTHER LETTERS OR TIMEOUT WILL HAVE NORMAL MODE")
    print("\nMAKE SURE THAT THE SHIFTING IS BOUND TO 'Q' AND 'E'")
    
    mode_selector()
    print("press ` (under the esc) to stop the program")
    print("you can change the mode between Normal, Sports, Eco and Manual by hitting 7, 8, 9 ,0 ")

# to change the drive mode
def mode_changer():
    global gas_thresholds
    if keyboard.is_pressed("7"):
        os.system("cls")
        print("Normal Mode")
        currentMode = "D"
        gas_thresholds = modes["Normal"]
    elif keyboard.is_pressed("8"):
        os.system("cls")
        print("Sports Mode")
        currentMode = "S"
        gas_thresholds = modes["Sports"]
    elif keyboard.is_pressed("9"):
        os.system("cls")
        print("Eco Mode")
        currentMode = "E"
        gas_thresholds = modes["Eco"]
    elif keyboard.is_pressed("0"):
        os.system("cls")
        print("Manual Mode")
        currentMode = "M"
        gas_thresholds = modes["Manual"]

def mode_selector():
    try:
        answer = inputimeout(prompt="Mode: ", timeout=10)  # to wait user input
        os.system("cls")
        if answer == "":
            gas_thresholds = modes["Normal"]  # Normal Mode
            print("Normal Mode")
            currentMode = "D"
        elif answer == "s" or answer == "S":
            gas_thresholds = modes["Sports"]  # Sports Mode
            print("Sports Mode")
            currentMode = "S"
        elif answer == "e" or answer == "E":
            gas_thresholds = modes["Eco"]  # Eco Mode
            print("Eco Mode")
            currentMode = "E"
        elif answer == "m" or answer == "M":
            gas_thresholds = modes["Manual"]  # Eco Mode
            print("Manual Mode")
            currentMode = "M"
    except:
        os.system("cls")
        gas_thresholds = modes["Normal"]  # Normal Mode
        print("Normal Mode")
        currentMode = "D"

def pause():
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
                    quit()

def tkPack():
    root.title("Gas and Brake Progress Bars")

    # Create gas progress bar
    gas_label = tk.Label(root, text="Gas: 0%")
    gas_label.pack()
    gas_progress = ttk.Progressbar(root, style='green.Horizontal.TProgressbar', orient="horizontal", length=200, mode="determinate", maximum=1)
    gas_progress.pack(padx=10,pady=5)

    # Create brake progress bar
    brake_label = tk.Label(root, text="Brake: 0%")
    brake_label.pack()
    brake_progress = ttk.Progressbar(root, style='blue.Horizontal.TProgressbar', orient="horizontal", length=200, mode="determinate", maximum=1)
    brake_progress.pack(padx=10,pady=5)

    gear_label = tk.Label(root, text="Gear: 0")
    gear_label.pack()
    
    def update_data():
        gear_value = F"{currentMode}{gear}" if gear != 0 else "R"
        # Update the labels
        gas_label.config(text=f"Gas: {int(gas * 100)}%", background='black', font=('Courier', 20), fg='white')
        brake_label.config(text=f"Brake: {int(brake * 100)}%", background='black', font=('Courier', 20), fg='white')
        gear_label.config(text=F"Gear: {gear_value}", background='black', font=('Courier', 20), fg='white')
        # Update the progress bars
        gas_progress["value"] = gas
        brake_progress["value"] = brake

        # Use after() to periodically call update_data() function
        root.after(10, update_data)  # Update every second
    
    # Start updating the progress bars periodically
    update_data()


def main():
    global rt, addr

    # setting up an udp server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
    

    print(f"PLEASE OPEN UP THE GAME FIRST")
    print("AND MAKE SURE THAT THE SHIFTING IS BOUND TO 'Q' AND 'E'")
    print(f"PLEASE SET THE OUTPUT IP TO {UDP_IP}")
    print(f"AND THE PORT TO {UDP_PORT}")
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1500)
    rt = get_data(data)
    os.system("cls")
    print("WORKED")

    statement()


    while True:

        pause()
        # choosing modes by hitting 7, 8, 9, 0
        mode_changer()
        # stop calculation if the mode is in manual
        if gas_thresholds == [0, 0, 0, 0] :
            continue
        

        
        data, addr = sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket

        # received data is now in the retuturned_data dict
        rt = get_data(data)

        root.update_idletasks()
        root.update()
        
        # stop calculation if we are in menu
        if  rt["IsRaceOn"] == 0:
            continue
        analyzeInput()
        makeDecision()
        
        # print(waitTimeBetweenDownShifts, downshift_count, rpmRangeSize * 3.5, sizecount)
        # print(rpmRangeTop, rpmRangeSize, rpmRangeBottom, continuous_down, int((rpmRangeSize * 3.5) // rpm), rpm < rpmRangeSize * 2, times, gear)
        # print(f"{round(rpmRangeTop, 2)} | RPM {round(rpm, 2)} | {round(rpmRangeTop - 600, 2)} | {count} | {round(gas, 2)}")# monitor the current status(i don't know how to use graphic interface :(   )

main()
