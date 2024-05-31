from colorama import Fore, Back, Style
from pyapriltags import Detector
import yaml, os, sys, inspect, time
import numpy as np
from enum import Enum, auto
import smbus
import time

global pins
global debug 

class LogLevel(Enum): 
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    FAILURE = 4
    def __init__(self, _): 
        color_mapping = {
            'DEBUG': 'WHITE', 
            'INFO': 'WHITE', 
            'WARNING': "YELLOW", 
            'ERROR': "RED", 
            'FAILURE': "RED"
        }
        self.color = color_mapping[self.name]
    def __int__(self): 
        return self.value
    def __str__(self): 
        return self.name
    
def get_params():
    with open( './config.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p 

def get_pins():
    with open( './pins.yaml', 'r') as stream:
        p= yaml.safe_load(stream)
    return p

def get_debug(): 
    global debug
    debug = parameters['User']['debug']


def pprint(text:str, level:LogLevel=LogLevel.INFO, textcolor:str="WHITE",  **kwargs):
        
    frm = inspect.stack()[1]
    parent = inspect.getmodule(frm[0]).__name__
    try: 
        #Try to get color from parent script 
        c = str(parameters[f'{parent}']['logcolor'])
    except Exception as e:
        #Log color not found, throwing exception.
        print("COLOR EXCEPTION: invalid log color string." + str(e))
        c = "WHITE"
    if(int(level) < parameters['User']['log_level']):
        ##not printed since prority too low. 
        return
    #print(textcolor)
    #print(eval('Fore.'+str(textcolor)))
    print(eval('Fore.'+ c) + f"{str(parent)}: \t" + eval('Fore.' + level.color)+ f"{level.name}\t"+ Style.RESET_ALL + eval('Fore.'+textcolor) + str(text) + Style.RESET_ALL, **kwargs)
    return

def patch():
    return parameters['Camera']['libcameraloglevel']

def overwrite_yaml_attribute(attribute, new_value):
    """
    Overwrites an existing attribute in a YAML file.

    :param attribute: The attribute to overwrite.
    :param new_value: The new value to set for the attribute.
    """
    try:
        # Read the existing YAML file
        with open('./config.yaml', 'r') as file:
            data = yaml.safe_load(file)

        # Split the attribute to handle nested attributes
        keys = attribute.split('.')
        d = data
        for key in keys[:-1]:
            d = d[key]

        # Overwrite the attribute
        d[keys[-1]] = new_value

        # Write the updated data back to the YAML file
        with open('./config.yaml', 'w') as file:
            yaml.safe_dump(data, file)

        print(f"Attribute '{attribute}' updated successfully.")

    except Exception as e:
        print(f"Error updating attribute '{attribute}': {e}")

def true_if_wait2s(oldtime): 
    return True if time.time()-oldtime>=2 else False


def shoelace_formula(vertices:list)->float:
    n = len(vertices)
    area:float = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    area = abs(area) / 2.0
    return area



class Drone:

    _angle:float
    _speed:float
    _height:float
    _active:bool
    
    def __init__(self, speed=0.0, angle=0.0, height=0.0):
        
        self._speed = speed
        self._height = height
        self._active = True
        self._angle = angle
    
    @property
    def speed(self)->float:
        return self.speed
    
    @speed.setter
    def speed(self, v:float)->None: 
        if not 0<v<100: #Plausibility check.
            raise ValueError("Drone speed can not be greater than 100 or smaller than 0.")    
        self._speed = v
    @property
    def angle(self)->float:
        return self._angle
    
    @angle.setter
    def angle(self, a:float)->None:
        self._angle = a
    
    @property 
    def height(self)-> float:
        return self._height
    @height.setter
    def height(self, h:float): 
        if not 0<h<10:
            raise ValueError("Height can not be outside 0 to 10 meters.")
        self._height=height
    

class Fire:
    center:list
    corners:list 
    active:bool
    height:float
    time_to_drop:float
    current_target:list

    def __init__(self, d:Detector):
        ##Transform to new coordinate system: Origin in middle of Frame. 
        self.center = [d.center[0]-960, d.center[1]-540, 0] 
        for i in enumerate(d.corners): 
            self.corners[i]=[d.corners[i][0]-960, d.corners[i][1]-540, 0]
        self.current_target = [0, 0, 0]
        active = True
    
    def __str__(self):
        return f"fire with image center at: {self.center}" 
 
    def arc_calc(self, vel:float, h:float) -> None: # setter method for the current_target.
        if h == 0: return# make sure height is set.
        g:float = 9.81
        self.current_target = [np.sqrt(2*h*vel^2/g), 0]
        self.time_to_drop = 0
        return 


#Implementierung des Gyroskops
    bus = smbus.SMBus(1)
 # I2C address of the device
MPU6000_DEFAULT_ADDRESS				= 0x68

# MPU6000 Register Map
MPU6000_REG_WHOAMI					= 0x75 # Who AM I Register
MPU6000_REG_SMPLRT_DIV				= 0x19 # Sample Rate Divider Register
MPU6000_REG_CONFIG					= 0x1A # Configuration Register
MPU6000_REG_GYRO_CONFIG				= 0x1B # Gyroscope Configuration Register
MPU6000_REG_ACCEL_CONFIG			= 0x1C # Accelerometer Configuration Register
MPU6000_REG_FIFO_EN					= 0x23 # FIFO Enable
MPU6000_REG_INT_ENABLE				= 0x38 # Interrupt Enable
MPU6000_REG_INT_STATUS				= 0x3A # Interrupt Status
MPU6000_REG_ACCEL_XOUT_H			= 0x3B # X-Axis Data MSB
MPU6000_REG_ACCEL_XOUT_L			= 0x3C # X-Axis Data LSB
MPU6000_REG_ACCEL_YOUT_H			= 0x3D # Y-Axis Data MSB
MPU6000_REG_ACCEL_YOUT_L			= 0x3E # Y-Axis Data LSB
MPU6000_REG_ACCEL_ZOUT_H			= 0x3F # Z-Axis Data MSB
MPU6000_REG_ACCEL_ZOUT_L			= 0x40 # Z-Axis Data LSB
MPU6000_REG_TEMP_OUT_H				= 0x41 # Temperature Output MSB
MPU6000_REG_TEMP_OUT_L				= 0x42 # Temperature Output LSB
MPU6000_REG_GYRO_XOUT_H				= 0x43 # X-Axis Data MSB
MPU6000_REG_GYRO_XOUT_L				= 0x44 # X-Axis Data LSB
MPU6000_REG_GYRO_YOUT_H				= 0x45 # Y-Axis Data MSB
MPU6000_REG_GYRO_YOUT_L				= 0x46 # Y-Axis Data LSB
MPU6000_REG_GYRO_ZOUT_H				= 0x47 # Z-Axis Data MSB
MPU6000_REG_GYRO_ZOUT_L				= 0x48 # Z-Axis Data LSB
MPU6000_REG_USER_CTRL				= 0x6A # User Control
MPU6000_REG_PWR_MGMT_1				= 0x6B # Power Management-1
MPU6000_REG_PWR_MGMT_2				= 0x6C # Power Management-2
MPU6000_REG_FIFO_COUNTH				= 0x72 # FIFO Count Register High
MPU6000_REG_FIFO_COUNTL				= 0x73 # FIFO Count Registers Low
MPU6000_REG_FIFO_R_W				= 0x74 # FIFO Read Write
MPU6000_REG_PRODUCT_ID				= 0x0C # Product ID

# MPU6000 Configuration Register
MPU6000_DLPF_CFG_256HZ				= 0x00 # Bandwidth = 256Hz
MPU6000_DLPF_CFG_188HZ				= 0x01 # Bandwidth = 188Hz
MPU6000_DLPF_CFG_98HZ				= 0x02 # Bandwidth = 98Hz
MPU6000_DLPF_CFG_42HZ				= 0x03 # Bandwidth = 42Hz
MPU6000_DLPF_CFG_20HZ				= 0x04 # Bandwidth = 20Hz
MPU6000_DLPF_CFG_10HZ				= 0x05 # Bandwidth = 10Hz
MPU6000_DLPF_CFG_5HZ				= 0x06 # Bandwidth = 5Hz

# MPU6000 Gyroscope Configuration Register
MPU6000_FS_250DPS					= 0x00 # Full Scale = 250dps
MPU6000_FS_500DPS					= 0x08 # Full Scale = 500dps
MPU6000_FS_1000DPS					= 0x10 # Full Scale = 100dps
MPU6000_FS_2000DPS					= 0x18 # Full Scale = 2000dps

# MPU6000 Accelerometer Configuration Register
MPU6000_FS_2G						= 0x00 # Full Scale Range = 2G
MPU6000_FS_4G						= 0x08 # Full Scale Range = 4G
MPU6000_FS_8G						= 0x10 # Full Scale Range = 8G
MPU6000_FS_16G						= 0x18 # Full Scale Range = 16G

# MPU6000 Power Management-1 Register
MPU6000_DEVICE_RESET				= 0x80 # Resets all internal registers to their default values
MPU6000_SLEEP						= 0x40 # Puts the MPU-6000 into Sleep Mode
MPU6000_CYCLE						= 0x20 # SLEEP is disabled, the MPU-6000 will cycle between sleep mode and waking up
MPU6000_TEMP_DIS					= 0x08 # Disables the Temperature sensor
MPU6000_CLKSEL_19_2					= 0x05 # PLL with external 19.2MHz reference
MPU6000_CLKSEL_32_768				= 0x04 # PLL with external 32.768kHz reference
MPU6000_CLKSEL_Z					= 0x03 # PLL with Z axis gyroscope reference
MPU6000_CLKSEL_Y					= 0x02 # PLL with Z axis gyroscope reference
MPU6000_CLKSEL_X					= 0x01 # PLL with Z axis gyroscope reference

# MPU6000 Power Management-2 Register
MPU6000_LP_WAKE_CTRL_1_25			= 0x00 # Wake-up Frequency = 1.25Hz
MPU6000_LP_WAKE_CTRL_5				= 0x40 # Wake-up Frequency = 5Hz
MPU6000_LP_WAKE_CTRL_20				= 0x80 # Wake-up Frequency = 20Hz
MPU6000_LP_WAKE_CTRL_40				= 0xC0 # Wake-up Frequency = 40Hz
MPU6000_STBY_XA						= 0x20 # X axis accelerometer into standby mode
MPU6000_STBY_YA						= 0x10 # Y axis accelerometer into standby mode
MPU6000_STBY_ZA						= 0x08 # Z axis accelerometer into standby mode
MPU6000_STBY_XG						= 0x04 # X axis gyroscope into standby mode
MPU6000_STBY_YG						= 0x02 # Y axis gyroscope into standby mode
MPU6000_STBY_ZG						= 0x01 # Z axis gyroscope into standby mode


class MPU6000():
    def __init__(self):
		self.gyro_config()
		self.accl_config()
		self.power_management_1()
	
	def gyro_config(self):
		"""Select the Gyroscope Configuration Register data from the given provided value"""
		bus.write_byte_data(MPU6000_DEFAULT_ADDRESS, MPU6000_REG_GYRO_CONFIG, MPU6000_FS_2000DPS)
	
	def accl_config(self):
		"""Select the Accelerometer Configuration Register data from the given provided value"""
		bus.write_byte_data(MPU6000_DEFAULT_ADDRESS, MPU6000_REG_ACCEL_CONFIG, MPU6000_FS_16G)
	
	def power_management_1(self):
		"""Select the Power Management-1 Register data from the given provided value"""
		bus.write_byte_data(MPU6000_DEFAULT_ADDRESS, MPU6000_REG_PWR_MGMT_1, MPU6000_CLKSEL_X)
	
	def read_accl(self):
		"""Read data back from MPU6000_REG_ACCEL_XOUT_H(0x3B), 6 bytes
		Accelerometer X-Axis MSB, X-Axis LSB, Y-Axis MSB, Y-Axis LSB, Z-Axis MSB, Z-Axis LSB"""
		data = bus.read_i2c_block_data(MPU6000_DEFAULT_ADDRESS, MPU6000_REG_ACCEL_XOUT_H, 6)
		
		# Convert the data
		xAccl = data[0] * 256 + data[1]
		if xAccl > 32767 :
			xAccl -= 65536
		
		yAccl = data[2] * 256 + data[3]
		if yAccl > 32767 :
			yAccl -= 65536
		
		zAccl = data[4] * 256 + data[5]
		if zAccl > 32767 :
			zAccl -= 65536
		
		return {'x' : xAccl, 'y' : yAccl, 'z' : zAccl}
	
	def read_gyro(self):
		"""Read data back from MPU6000_REG_GYRO_XOUT_H(0x43), 6 bytes
		Gyrometer X-Axis MSB, X-Axis LSB, Y-Axis MSB, Y-Axis LSB, Z-Axis MSB, Z-Axis LSB"""
		data = bus.read_i2c_block_data(MPU6000_DEFAULT_ADDRESS, MPU6000_REG_GYRO_XOUT_H, 6)
		
		# Convert the data
		xGyro = data[0] * 256 + data[1]
		if xGyro > 32767 :
			xGyro -= 65536
		
		yGyro = data[2] * 256 + data[3]
		if yGyro > 32767 :
			yGyro -= 65536
		
		zGyro = data[4] * 256 + data[5]
		if zGyro > 32767 :
			zGyro -= 65536
		
		return {'x' : xGyro, 'y' : yGyro, 'z' : zGyro}

from MPU6000 import MPU6000
mpu6000 = MPU6000()

while True:
	mpu6000.gyro_config()
	mpu6000.accl_config()
	mpu6000.power_management_1()
	
	accl = mpu6000.read_accl()
	print "Acceleration in X-Axis : %d"%(accl['x'])
	print "Acceleration in Y-Axis : %d"%(accl['y'])
	print "Acceleration in Z-Axis : %d"%(accl['z'])
	gyro = mpu6000.read_gyro()
	print "X-Axis of Rotation : %d" %(gyro['x'])
	print "Y-Axis of Rotation : %d" %(gyro['y'])
	print "Z-Axis of Rotation : %d" %(gyro['z'])
	print " ************************************ "
	


if __name__ == "__main__": 
    print("henlo") ##never called.
    overwrite_yaml_attribute('Helper.Test', "Boo")
else: 
    global parameters 
    parameters = get_params()
    pins = get_pins()
    get_debug()