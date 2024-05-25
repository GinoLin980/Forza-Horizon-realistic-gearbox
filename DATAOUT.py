import socket, struct, select

# to check the UDP server is outputing the data or not
def UDPconnectable(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((ip, port))  # Try to bind to the IP and port
        ready = select.select([sock], [], [], 0.1)  # Check if data is available (timeout is 0.1 seconds)
        if ready[0]:  # If data is available
            data, addr = sock.recvfrom(1500)  # Receive the data
            return True
        else:  # If no data is available
            return False
    except:
        raise RuntimeError("UDP connectable check failed")
    finally:
        sock.close()

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