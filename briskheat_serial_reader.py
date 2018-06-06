import serial
import time

#connecting to Port COM3, check device manager
#returns the initialized serialport
#TODO: find out a way to raise an error if no connection

class Briskheat:
    #Serial ser;
    #String port
    error_ref = {    
        '001' : 'STATUS_OK Current temperature is within alarm limits',
        '002' : 'STATUS_HIGH Current temperature is above high alarm limit',
        '004' : 'STATUS_LOW Current temperature is below the low alarm limit',
        '008' : 'STATUS_RTD_SHORT RTD is shorted',
        '010' : 'STATUS_RTD_OPEN RTD is open',
        '080' : 'STATUS_TRIAC_DRIVER_BAD Triac driver is not responding',
        '100' : 'STATUS_TRIAC_DRIVER_BAD Triac driver is not responding',
        '101' : 'STATUS_NETWORK_COMMS_BAD Communications channel is bad',
        '200' : 'STATUS_NETWORK_COMMS_BAD Communications channel is bad',
        '201' : 'STATUS_HEATER_CONFIG_COMM_BAD Communication failed during heater configuration',
        '400' : 'STATUS_HEATER_CONFIG_COMM_BAD Communication failed during heater configuration',
        '401' : 'STATUS_LINE_CTRL_COMM_BAD Communication error with heater line module',
        '000' : 'STATUS_HEATER_DISABLED Zone is disabled'
    }
    communication_errors = [080, 100, 101, 200, 201, 400, 401]
    reconnect_try_limit = 3
    
    def __init__(self, path):
        self.port = path
        self.open(path)
        self.start = True
        self.reconnect_tries = 0
        self.data = {}
        self.connect()

    #opens serialport
    def open(self, path):
        self.ser = serial.Serial(
                port=path,
                baudrate=19200,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout=1,
                write_timeout=1
                )
        assert(self.ser.isOpen())

    def reconnect(self):
        self.close()
        self.open(self.port)
        self.connect()

    #writes to briskheat
    def send(self, message):
        message = message + "\r" #takes \r carriage return
        msg = message.encode('ascii')
        self.ser.write(msg)
        time.sleep(1) #wait for briskheat to respond


    #writes but does not wait
    def quick_send(self, message):
        message = message + "\r" #takes \r carriage return
        msg = message.encode('ascii')
        self.ser.write(msg)

    #reads from serialport
    def read(self):
        out = ''
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1).decode('ascii')
        return out

    #send and read
    def send_and_read(self, message):
        self.send(message)
        return self.read()

    def wPrint(self, message):
        print(self.send_and_read(message), end='') #no newline print

    #Inputs the password and connects to the briskheat 
    def connect(self):
        pswd = 'briskheat' #default
        self.send_and_read(pswd)
        time.sleep(.5)
        self.send_and_read(pswd)

    #closes connection to the briskheat
    def close(self):
        self.wPrint('bye')
        self.ser.close()

    #user friendly terminal interface for briskheat interaction, enter '?' to see commands   
    def ez_terminal(self):
        print('BH> ', end='')
        while True:
            try:
                s = input().lower()
                if s == 'dump':
                    self.get_dump()
                    print('BH> ', end='')
                    continue
                self.wPrint(s)
                if s == 'bye':
                    return
            except KeyboardInterrupt:
                e = input('Are you sure you want to exit?([y]/n)')
                if (e == 'y'):
                    return
                elif (e == 'n'):
                    print('BH> ', end='')
                    continue
                else:
                    print("Unrecognized, continuing...")
                    print('BH> ', end='')
                    continue

    #gets list of zones
    def sm():
        r = self.send_and_read('sm')
        zones = r.split('\r')[-1].split(', ')
        return zones
                
    #starts dump command for briskheat ez_terminal()
    def get_dump(self):
        print("Press Ctrl-C to stop dump, this will not stop the program")
        self.send('dump')
        try:
            while True:
                print(self.read(), end='')
                time.sleep(2)
        except KeyboardInterrupt:
            time.sleep(.2)
            self.read()
            return

    def make_zones():
        zones = sm()
        for zone in zones
            self.data[zone] = []

    def save_dump(self):
        print("Press Ctrl-C to stop dump, this will not stop the program")
        self.send('dump')
        while True:
            zones_data = self.read().split('\r')
            for zone in zones_data:
                if len(zone) != 0:
                    record = True
            if record:
                for zone in zones_data:
                    parsed_data = parse(zone)
                    if parsed_data = []: #get help from dump gather
                        error_msg = "bad data error: one error every 1000 secs is normal"
                        raised_errors.append(error_msg)
                        print(error_msg)
                        continue
                    #add temp to the array associated with the zone number
                    self.data[parsed_data[0]].add[parsed_data[1]]
            time.sleep(4.63)

    #parses the dump log.
    def parse(s):
        s_arr = s.split(' ')
        #0 = time, 1 = date, 2 = zone, 3 = status, 4 = set-point, 5 = high alarm limit,
        #6 = low alarm limit, 7 = actual temp, 8 = duty cycle, 9 = heater status

        if len(s_arr) != 10: #bad data, error
            return []
        
        error_check(s_arr)
        if self.start == True:
            self.opened_time = s_arr[1] + '-' + re.sub(':', ';', s_arr[0])
            self.start = False
        #print('s_arr: ' + s_arr.__str__())
        temp_C = int(float(s_arr[7][2:8]) * 10) #temperature in celsius, changed from string to float, then it is multiplied by ten for int
        z_num = int(s_arr[2][1:])
        return [z_num, temp_C] #can change how much information you want to return

    def error_check(info):
        code = info[3][-3:] #trims the string down to it's last 3 characters
        if (code != '001'): #error has happened
            error_msg = code + ': ' + self.error_ref[code]
            #TODO: not sure what to do with the error, store it for now
            raised_errors.append(info)
            print('error msg: ' + error_msg.__str__())

            print(raised_errors)
            
            if code in self.communication_errors:
                self.reconnect()
            if self.reconnect_tries > self.reconnect_try_limit or code == '008' or code == '010':
                #todo: something theres a hardware error
                print("hardware error")
            if code == '002' or code == '004':
                #todo: temperature is outside of temp limit
                print("temp alarm")
        
    def __repr__(self):
        return 'Port: ' + self.port + self.send_and_read('show')

