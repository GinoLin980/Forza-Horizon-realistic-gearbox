import socket, struct
import pandas as pd
import time, keyboard
from pathlib import Path


UDP_IP = "127.0.0.1"  # This sets server ip to localhost
UDP_PORT = 8000  # You can freely edit this

init = False
shift_indicator = 0
jump_gears = 0
current_gear = 0
cruising_count = 0
jump_time = (time.time() - 6) # to allow jump gear in the begining of program
count = 0
pressed_time = (time.time() - 5)
pressed = False

gas = []
brake = []
rpm_max = []
in_first_gear = []
in_overdrive = []
shift_status =  []
jump_gears_list = []

#reading data and assigning names to data types in data_types dict
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

#assigning sizes in bytes to each variable type
jumps={
    's32': 4, #Signed 32bit int, 4 bytes of size
    'u32': 4, #Unsigned 32bit int
    'f32': 4, #Floating point 32bit
    'u16': 2, #Unsigned 16bit int
    'u8': 1, #Unsigned 8bit int
    's8': 1, #Signed 8bit int
    'hzn': 12 #Unknown, 12 bytes of.. something
}

def get_data(data):
    return_dict={}

    #additional var
    passed_data = data
    
    for i in data_types:
        d_type = data_types[i]#checks data type (s32, u32 etc.)
        jump=jumps[d_type]#gets size of data
        current = passed_data[:jump]#gets data

        decoded = 0
        #complicated decoding for each type of data
        if d_type == 's32':
            decoded = int.from_bytes(current, byteorder='little', signed = True)
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
        
        #adds decoded data to the dict
        return_dict[i] = decoded
        
        
        #removes already read bytes from the variable
        passed_data = passed_data[jump:]
    
    
    
    #returns the dict
    return return_dict

def append_data():
    global gas, brake, rpm_max, shift_status, jump_gears_list, in_first_gear, in_overdrive
    gas.append(rt["Accel"] / 255)
    brake.append(rt["Brake"] / 255)
    rpm_max.append((rt["CurrentEngineRpm"] - rt["EngineIdleRpm"]) / (rt["EngineMaxRpm"] - 600))
    in_first_gear.append(1 if rt["Gear"] == 1 else 0)
    in_overdrive.append(1 if rt["Gear"] > 4 else 0)
    shift_status.append(1)
    jump_gears_list.append(0)

def csv_update(gas: list, brake: list, rpm_max: list, in_first_gear: list, in_overdrive: list, shift_status: list, jump_gears: list, mode: str):
    PATH = Path(f'data/{mode}')
    PATH.mkdir(parents=True, exist_ok=True)
    # Create the CSV file if it doesn't exist
    PATH = Path(f'data/{mode}/data.csv')
    if not PATH.is_file():
        df = pd.DataFrame({'rpm/max': [], 'gas': [], 'brake': [], 'in_first_gear': [], 'in_overdrive': [], 'shift_status': [], 'jump_gears': []})
        df.to_csv(f'data/{mode}/data.csv', index=False)

    # Append the row to the CSV file
    new_row = pd.DataFrame({'rpm/max': rpm_max, 'gas': gas, 'brake': brake, 'in_first_gear': in_first_gear, 'in_overdrive': in_overdrive, 'shift_status': shift_status, 'jump_gears': jump_gears})
    new_row.to_csv(f'data/{mode}/data.csv', index=False, mode='a', header=False)

def detect_shift():
    global shift_indicator, current_gear, shift_status
    if rt['Gear'] > current_gear:
        shift_status[-1] = 2
        current_gear = rt['Gear']
        append_data()
    elif rt['Gear'] < current_gear:
        shift_status[-1] = 0
        current_gear = rt['Gear']
        append_data()
    elif rt['Gear'] == current_gear:
        shift_indicator = 1
        current_gear = rt['Gear']

def continuous_down():
    global jump_gears, jump_time, shift_indicator
    if rt['Accel'] /255 > 0.7 and rt['Gear'] > 4 and (rt['CurrentEngineRpm'] - rt['EngineIdleRpm']) / rt["EngineMaxRpm"] < 0.35:
        print("ump_gears", (1 - rt['CurrentEngineRpm']/rt['EngineMaxRpm']) / 2.2 * 12)
        jump_gears = 1
        shift_indicator = 0
        if time.time() - jump_time > 5:
            append_data() 
            for i in range(int((1 - rt['CurrentEngineRpm']/rt['EngineMaxRpm']) / 2.2 * 12)):
                keyboard.press_and_release('q')
                time.sleep(0.03)
        jump_time = time.time()
    else:
        jump_gears = 0

def manual_jump_gear():
    global jump_gears, pressed, pressed_time, shift_indicator
    if keyboard.is_pressed('ctrl'):
        if not pressed:
            jump_gears = 1
            shift_indicator = 0
            append_data()
            for i in range(3):
                time.sleep(0.03)
                keyboard.press('q')
            pressed_time = time.time()
        pressed = True
    jump_gears = 0

    if time.time() - pressed_time > 2:
        pressed = False

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def receive_data(data_length: int = 5000):
    global init, shift_indicator, current_gear, jump_gears, jump_time, count, cruising_count, rt, addr
    while True:
        data, addr = sock.recvfrom(1500)
        rt = get_data(data)
    
        if rt["IsRaceOn"] == 0:
            continue
        if init == False:
            current_gear = rt['Gear']
            init = True
        
        if rt["Gear"] == 0:
            continue
        
        if rt['Accel'] /255 == 0 and rt['Brake'] / 255 == 0:
            cruising_count += 1
        if rt['Accel'] /255 > 0 or rt["Brake"] / 255> 0:
            cruising_count = 0
        if cruising_count % 50 != 0:
            continue
        
        
        
        detect_shift()
        # continuous_down()
        # manual_jump_gear()
        
        count += 1
        # csv_update(gas=rt['Accel'] /255, brake=rt['Brake'] / 255, rpm=rt['CurrentEngineRpm'], idle_rpm=rt['EngineIdleRpm'], max_shift_rpm=rt['EngineMaxRpm'], gear=rt['Gear'], shift_status=shift_indicator, jump_gears=jump_gears)
        if count % 30 == 0:
            # print(rt['Accel'] /255, rt['Brake'] / 255, rt['CurrentEngineRpm'], rt['EngineIdleRpm'], rt['EngineMaxRpm'], rt['Gear'], shift_indicator, jump_gears, ((1 - rt['CurrentEngineRpm']/rt['EngineMaxRpm']) / 2.2)*10)
            # count = 0
            append_data()
        

        # shift_indicator = 1
        if len(gas) > data_length or keyboard.is_pressed('esc'):
            print('ending.................')
            break
        if len(gas) > 1:
            print(gas[-1], brake[-1], rpm_max[-1], in_first_gear[-1], in_overdrive[-1], shift_status[-1], jump_gears_list[-1], len(gas), end='\r')
        
def main():
    receive_data(data_length=2000)

    csv_update(gas=gas, brake=brake, rpm_max=rpm_max, in_first_gear=in_first_gear, in_overdrive=in_overdrive, shift_status=shift_status, jump_gears=jump_gears_list, mode="Comfort")
    
main()