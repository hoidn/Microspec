import serial
import time

PORT_NUM = 0
BAUD = 9600

class Driver(object):
    def __init__(self, addressDict):
        """
        class to connect to one or more daisychained Lin R256 drivers and access the 
        associated motors

        addressDict expects a dict with name: address pairs
        """
        motor_dict = {}
        self.serial_connection = serial.Serial(PORT_NUM, BAUD, timeout=1)
        for label in addressDict.keys():
            try:
                motor_dict[label] = Motor(self.serial_connection, addressDict[label])
            except EOFError:
                print "motor " + str(label) + " at address " + str(addressDict[label]) + ": initialization failed"

        self.motors = motor_dict

    def motors(self):
        """
        return a dict containing the Motor intances keyed by namestring
        """
        return self.motors

    def __exit__(self):
        self.serial_connection.close()


class Motor(object):
    """
    class to control a single motor

    ser: an instance of serial.Serial
    """
    BASE_POSITION = 2**30 # starting motor position
    cmdDict = {'microsteps': '?6', 'plus': 'P', 'minus': 'D', 'absolute': 'A', 'set_position': 'z', 'query_position': '?0', 'current_command': '?$', \
        'run_current': 'm', 'hold_current': 'h', 'velocity': 'V', 'acceleration': 'L', 'microstep_size': 'j'}
    def __init__(self, ser, address, position = None, run_current = 50, hold_current = 0, velocity = 5000, acceleration = 5000, microsteps = 256):
        self.ser = ser
        self.start_string = '/' + str(address)
        self.microsteps = self.query('microsteps')
        self.polarity = 1 # 1 or -1
        if position is None:
            self.position = 0
        else: 
            self.position = position
        self.send_command('microstep_size', microsteps)
        self.send_command('run_current', run_current)
        self.send_command('hold_current', hold_current)
        self.send_command('velocity', velocity)
        self.send_command('acceleration', acceleration)
        self.send_command('set_position', Motor.BASE_POSITION)

    def query(self, cmd):
        cmd_dispatch = self.start_string + Motor.cmdDict[cmd] + 'R\r\n'
        self.ser.write(cmd_dispatch)
        raw = self.ser.readline()
        # extract the returned value from the ascii stream
        value = filter(lambda x: x in map(str, range(10)), raw)[1:]
        if value != '':
            return int(value)
        else:
            raise EOFError('invalid serial port read')
        
    def send_command(self, cmd_code, argument):
        cmd_dispatch = self.start_string + Motor.cmdDict[cmd_code] + str(argument) + 'R\r\n'
        self.ser.write(cmd_dispatch)
        self.ser.readline()
        

    def rel(self, num_steps):
        """make a relative movement"""
        motor_position = self.query('query_position')
        motor_target = motor_position + num_steps
        # reverse motor polarity if needed
        if motor_target < 0 or motor_target >= 2**31:
            raise ValueError("target motor position out of bounds")
    
        self._motor_relative(num_steps)
        self.position = self.position + num_steps

    def _motor_relative(self, num_steps):
        """ make a relative motion. 

            sign of num_steps corresponds to motor (not user) polarity
        """
        # wait for serial read if this is a recursive call
        if num_steps >= 0:
            cmd_code = 'plus'
        else:
            cmd_code = 'minus'
        self.send_command(cmd_code, abs(num_steps))

    def absolute(self, position):
        """go to absolute position"""
        relative_motion = position - self.position
        self.rel(relative_motion)
