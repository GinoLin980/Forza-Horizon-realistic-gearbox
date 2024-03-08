# 2024/3/8 v1.1
# The code of this project is mostly taken from other people's project. You can freely use and edit this code.
import socket
import struct
import time
import keyboard
from inputimeout import inputimeout
import msvcrt as m
import os

print('WORKED')
UDP_IP = "127.0.0.1"  # This sets server ip to the RPi ip
UDP_PORT = 8000  # You can freely edit this

# initializing all the variables
count = 0

maxRPM = 0
gear = 0
gas = 0
brake = 0
rpm = 0
speed = 0

waitTimeBetweenDownShifts = 2
lastShiftTime = 0
lastShiftUpTime = 0
lastShiftDownTime = 0

last_inc_aggr_time = 0
aggressiveness = 0

# define the settings for different driving modes
# 0 index is : used in agressiveness increase decision
# 1 index is : used in agressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time
gas_thresholds = [0.95, 0.4, 12, 0.1]  # Normal drive mode

# reading data and assigning names to data types in data_types dict
data_types = {
    'IsRaceOn': 's32',
    'TimestampMS': 'u32',
    'EngineMaxRpm': 'f32',
    'EngineIdleRpm': 'f32',
    'CurrentEngineRpm': 'f32',
    'AccelerationX': 'f32',
    'AccelerationY': 'f32',
    'AccelerationZ': 'f32',
    'VelocityX': 'f32',
    'VelocityY': 'f32',
    'VelocityZ': 'f32',
    'AngularVelocityX': 'f32',
    'AngularVelocityY': 'f32',
    'AngularVelocityZ': 'f32',
    'Yaw': 'f32',
    'Pitch': 'f32',
    'Roll': 'f32',
    'NormalizedSuspensionTravelFrontLeft': 'f32',
    'NormalizedSuspensionTravelFrontRight': 'f32',
    'NormalizedSuspensionTravelRearLeft': 'f32',
    'NormalizedSuspensionTravelRearRight': 'f32',
    'TireSlipRatioFrontLeft': 'f32',
    'TireSlipRatioFrontRight': 'f32',
    'TireSlipRatioRearLeft': 'f32',
    'TireSlipRatioRearRight': 'f32',
    'WheelRotationSpeedFrontLeft': 'f32',
    'WheelRotationSpeedFrontRight': 'f32',
    'WheelRotationSpeedRearLeft': 'f32',
    'WheelRotationSpeedRearRight': 'f32',
    'WheelOnRumbleStripFrontLeft': 's32',
    'WheelOnRumbleStripFrontRight': 's32',
    'WheelOnRumbleStripRearLeft': 's32',
    'WheelOnRumbleStripRearRight': 's32',
    'WheelInPuddleDepthFrontLeft': 'f32',
    'WheelInPuddleDepthFrontRight': 'f32',
    'WheelInPuddleDepthRearLeft': 'f32',
    'WheelInPuddleDepthRearRight': 'f32',
    'SurfaceRumbleFrontLeft': 'f32',
    'SurfaceRumbleFrontRight': 'f32',
    'SurfaceRumbleRearLeft': 'f32',
    'SurfaceRumbleRearRight': 'f32',
    'TireSlipAngleFrontLeft': 'f32',
    'TireSlipAngleFrontRight': 'f32',
    'TireSlipAngleRearLeft': 'f32',
    'TireSlipAngleRearRight': 'f32',
    'TireCombinedSlipFrontLeft': 'f32',
    'TireCombinedSlipFrontRight': 'f32',
    'TireCombinedSlipRearLeft': 'f32',
    'TireCombinedSlipRearRight': 'f32',
    'SuspensionTravelMetersFrontLeft': 'f32',
    'SuspensionTravelMetersFrontRight': 'f32',
    'SuspensionTravelMetersRearLeft': 'f32',
    'SuspensionTravelMetersRearRight': 'f32',
    'CarOrdinal': 's32',
    'CarClass': 's32',
    'CarPerformanceIndex': 's32',
    'DrivetrainType': 's32',
    'NumCylinders': 's32',
    'HorizonPlaceholder': 'hzn',
    'PositionX': 'f32',
    'PositionY': 'f32',
    'PositionZ': 'f32',
    'Speed': 'f32',
    'Power': 'f32',
    'Torque': 'f32',
    'TireTempFrontLeft': 'f32',
    'TireTempFrontRight': 'f32',
    'TireTempRearLeft': 'f32',
    'TireTempRearRight': 'f32',
    'Boost': 'f32',
    'Fuel': 'f32',
    'DistanceTraveled': 'f32',
    'BestLap': 'f32',
    'LastLap': 'f32',
    'CurrentLap': 'f32',
    'CurrentRaceTime': 'f32',
    'LapNumber': 'u16',
    'RacePosition': 'u8',
    'Accel': 'u8',
    'Brake': 'u8',
    'Clutch': 'u8',
    'HandBrake': 'u8',
    'Gear': 'u8',
    'Steer': 's8',
    'NormalizedDrivingLine': 's8',
    'NormalizedAIBrakeDifference': 's8'
}


# assigning sizes in bytes to each variable type
jumps = {
    's32': 4,  # Signed 32bit int, 4 bytes of size
    'u32': 4,  # Unsigned 32bit int
    'f32': 4,  # Floating point 32bit
    'u16': 2,  # Unsigned 16bit int
    'u8': 1,  # Unsigned 8bit int
    's8': 1,  # Signed 8bit int
    'hzn': 12  # Unknown, 12 bytes of.. something
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
        if d_type == 's32':
            decoded = int.from_bytes(current, byteorder='little', signed=True)
        elif d_type == 'u32':
            decoded = int.from_bytes(current, byteorder='little', signed=False)
        elif d_type == 'f32':
            decoded = struct.unpack('f', current)[0]
        elif d_type == 'u16':
            decoded = struct.unpack('H', current)[0]
        elif d_type == 'u8':
            decoded = struct.unpack('B', current)[0]
        elif d_type == 's8':
            decoded = struct.unpack('b', current)[0]

        # adds decoded data to the dict
        return_dict[i] = decoded
        # removes already read bytes from the variable
        passed_data = passed_data[jump:]

    # returns the dict
    return return_dict


# setting up an udp server
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

sock.bind((UDP_IP, UDP_PORT))
data, addr = sock.recvfrom(1500)
rt = get_data(data)

def analyzeInput(deltaT):
    # if you need other types of data, they can be found at the dict data_types
    global aggressiveness, last_inc_aggr_time, rpmRangeBottom, gas, brake, rpmRangeTop, rpmRangeBottom, rpmRangeSize, gear, idleRPM

    # transform gas value into 0 to 1, because the original code is designed for Assetto Corsa
    gas = rt['Accel'] / 255 
    brake = rt['Brake'] / 255

    rpmRangeTop = rt['EngineMaxRpm']
    maxShiftRPM = rt['EngineMaxRpm'] * 0.9 # change this value if it is not capable to upshift on your car, mostly for some trucks.
    idleRPM = rt['EngineIdleRpm']
    gear = rt['Gear']
    rpmRangeSize = (rt['EngineMaxRpm'] - rt['EngineIdleRpm']) / 4

    # compute a new aggressiveness level depending on the gas and brake pedal pressure
    # and apply a factor from the current driving mode gas_thresholds = [0.95, 0.4, 12, 0.15]
    new_aggr = min(
        1,
        max((gas - gas_thresholds[1]) / (gas_thresholds[0] - gas_thresholds[1]),
            (brake - (gas_thresholds[1] - 0.3)) / (gas_thresholds[0] - gas_thresholds[1]) * 1.6))

    # new_aggr = min(1, (gas - gas_thresholds[drive_mode][1]) / (gas_thresholds[drive_mode][0] - gas_thresholds[drive_mode][1]))
    # ex full accel: 1, (1 - 0.95) / (0.95 - 0.4)
    # 1, 0.05 / 0.55 = 0.09

    # if the newly computed agressiveness is higher than the previous one
    if new_aggr > aggressiveness and gear > 0:
        # we update it with the new one
        aggressiveness = new_aggr
        # and save the time at which we updated it
        last_inc_aggr_time = time.time()

    # if we have not increased the agressiveness for at least 2 seconds
    if time.time() > last_inc_aggr_time + 2:
        # we lower the aggressiveness by a factor given by the current driving move
        aggressiveness -= deltaT / gas_thresholds[2]/10

    # we maintain a minimum aggressiveness defined by the current driving mode
    # it's only used by the sport mode, to maintain the aggressiveness always above 0.5
    # all other driving modes will use the actual computed aggressiveness 
    # (which can be bellow 0.5)
    aggressiveness = max(aggressiveness, gas_thresholds[3])

    # adjust the allowed upshifting rpm range, 
    # depending on the aggressiveness
    rpmRangeTop = (idleRPM + 500 + ((maxShiftRPM - idleRPM - 400) * aggressiveness *0.95))

    # adjust the allowed downshifting rpm range, 
    # depending on the aggressiveness
    rpmRangeBottom = max(idleRPM + (min(gear, 6) * 50), rpmRangeTop - rpmRangeSize)
    
    
    


def makeDecision():
    global speed, rpm, gas, count
    speed = rt['Speed']
    rpm = rt['CurrentEngineRpm']
    
    # when braking we allow quick followup of downshift, but not when accelerating
    if (brake > 0):
        waitTimeBetweenDownShifts = 0.4
    elif (brake == 0):
        waitTimeBetweenDownShifts = 0.8
    if rpm > rpmRangeTop -600 and rpm >700 and rt['Speed'] > 5 and gas > 0:
        count += 1 
    if time.time() > lastShiftTime + 5 and rpm < 1900 or gas > 0.25:
        count = 0
    
    
    if (
            # we have already shifted in the last 0.1s
            time.time() < lastShiftTime + 0.1 or
            # or we are in neutral
            gear < 1 or
            # or we have already shifted up in the last 1.3 sec
            time.time() < lastShiftUpTime + 0.9 or
            # or we have already shifted down in the last 1 sec
            time.time() < lastShiftDownTime + waitTimeBetweenDownShifts 
    ):
        
        # do not change gear
        return
    if (
            # we have reached the top range (upshift are rpm-allowed)
            rpm > rpmRangeTop and
            # we have not downshifted in the last 1 sec (to prevent up-down-up-down-up-down)
            time.time() > lastShiftDownTime + 0.4 and
            # we are not on the brakes
            brake == 0 and
            # we are not coasting either
            gas > 0 and
            # we are above 15km/h # speed value in FH is really weird, 4 equals 15km/h
            rt['Speed'] > 4
            # count means we can slowly accelerate like we do in real car
            or count == 300  
    ):
        # actually UPSHIFT
       
        shiftUp()



    elif (
            # we have reached the lower rpm range (downshift are rpm-allowed)
            rpm < rpmRangeBottom and
            # we are not in first gear (meaning we have gears available bellow us)
            gear > 1 and
            # we have not downshifted in the last 2 sec
            time.time() > lastShiftDownTime + waitTimeBetweenDownShifts and
            # depending on which gears we'll end up into
            (
                    # we are NOT about to downshift into 1st, we can allow it
                    gear > 2 or
                    (
                            # we are about to downshift into 1st
                            gear == 2 and
                            (
                                    # we must be very vert aggressive to allow that to happen or be very very slow (less than 15km/h, which is always ok)
                                    (aggressiveness >= 0.95 or speed <= 4)
                            ) or
                        (
                            # we are in an overdrive gear
                            gear >= 4 and
                            # we are braking
                            brake > 0
                        )
                    )
            )
    ):
        # shiftdown two times if we are in an overdrive gear and are flooring the gas
        # if gas >= 70 and rpm < 4000:
        #     shiftDown()
        #     shiftDown()
        #     return
        # actually DOWNSHIFT
        shiftDown()
    # reset the count after shifting
    if count >= 300:
        count = 0



def shiftUp():
    global lastShiftTime, lastShiftUpTime
    
    keyboard.press_and_release('e')
    # update the last shifting times
    lastShiftTime = time.time()
    lastShiftUpTime = time.time()

def shiftDown():
    global lastShiftTime, lastShiftDownTime
    
    keyboard.press_and_release('q')
    # update the last shifting times
    lastShiftTime = time.time()
    lastShiftDownTime = time.time()

# to change the drive mode
def mode_changer():
    global gas_thresholds
    if keyboard.is_pressed('7'):
        os.system('cls')
        print('Normal Mode')
        gas_thresholds = [0.95, 0.4, 4, 0.1]
    elif keyboard.is_pressed('8'):
        os.system('cls')
        print('Sports Mode')
        gas_thresholds = [0.8, 0.4, 24, 0.5]
    elif keyboard.is_pressed('9'):
        os.system('cls')
        print('Eco Mode')
        gas_thresholds = [1, 0.5, 3, 0]
    elif keyboard.is_pressed('0'):
        os.system('cls')
        print('Manual Mode')
        gas_thresholds = [0, 0, 0, 0]

# Choosing modes in terminal
print('Timeout is 10 seconds')
print('Type in S to have Sports Mode')
print('Type in e to have Eco Mode')
print('Enter to have Normal Mode')
print('OTHER LETTERS OR TIMEOUT WILL HAVE NORMAL MODE')

# define the settings for different driving modes
# 0 index is : used in agressiveness increase decision
# 1 index is : used in agressiveness increase decision
# 2 index is : how quickly the aggressiveness lowers when driving calmly (1/value)
# 3 index is : the bare minimum aggressiveness to keep at any given time

try:
    answer = inputimeout(prompt='Mode: ', timeout=10)# to wait user input
    os.system('cls')
    if answer == 's' or answer == 'S':
        gas_thresholds = [0.8, 0.4, 24, 0.5]#Sports Mode
    elif answer == '':
        gas_thresholds = [0.95, 0.4, 4, 0.1]#Normal Mode
    elif answer == 'e' or answer == 'E':
        gas_thresholds = [1, 0.5, 3, 0]#Eco Mode

    if gas_thresholds == [0.95, 0.4, 4, 0.1]:#Normal Mode
        print('Normal Mode')
    elif gas_thresholds == [0.8, 0.4, 24, 0.5]:#Sports Mode
        print('Sports Mode')
    elif gas_thresholds == [1, 0.5, 3, 0]:#Eco Mode
        print('Eco Mode')
except:
    os.system('cls')
    gas_thresholds = [0.95, 0.4, 4, 0.1]#Normal Mode
    print('Normal Mode')

print("press ` to stop the program")
print('you can change the mode between Normal, Sports, Eco and Manual by hitting 7, 8, 9 ,0 ')

lastTime = time.time()

max_rpm = 0

mode_count = 0

while True:
    data, addr = sock.recvfrom(1500)  # buffer size is 1500 bytes, this line reads data from the socket

    # received data is now in the retuturned_data dict
    rt = get_data(data)

    # Calculate deltaT as the time elapsed since the last frame
    current_time = time.time()
    deltaT = (current_time - lastTime) * 100 # to simulate the deltaT in Assetto Corsa

    # Update your last_time variable for the next frame
    lastTime = current_time

    # print(deltaT)
    analyzeInput(deltaT)
    makeDecision()
    if rpm > max_rpm:
        max_rpm = round(rpm, 2)
    # print(f"{round(rpmRangeTop, 2)} | RPM {round(rpm, 2)} | {round(rpmRangeTop - 600, 2)} | {count} | {round(gas, 2), max_rpm}")# monitor the current status(i don't know how to use graphic interface :(   )
    

    # choosing modes by hitting 7, 8, 9, 0
    mode_changer()


    # stop the program
    if keyboard.is_pressed('`'):
        print("You stopped the program, press \\ again to resume.")
        while True:
            if keyboard.is_pressed("\\"):
                print('Resumed.')
                break
