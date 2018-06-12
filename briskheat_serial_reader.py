import serial
import time
import re
import pickle

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
    communication_errors = ['080', '100', '101', '200', '201', '400', '401']
    reconnect_try_limit = 3
    
    def __init__(self, path):
        self.port = path
        self.open(path)
        self.start = True
        self.reconnect_tries = 0
        self.data = {}
        self.connect()
        self.raised_errors = []

    #opens serialport
    def open(self, path):
        self.ser = serial.Serial(
                port=path,
                baudrate=19200,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout=1,
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
        time.sleep(.1) #wait for briskheat to respond


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
        time.sleep(.1)
        if self.ser.inWaiting() > 0:
            out += self.read()
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
    def sm(self): #do you even parse bro?
        bh.read()
        return [int(i) for i in list(filter(lambda a: a != '',re.sub('[a-zA-Z,\r\n>]', '', self.send_and_read('sm')).split(' ')))]
                
    #starts dump command for briskheat ez_terminal()
    def get_dump(self):
        print("Press Ctrl-C to stop dump, this will not stop the program")
        self.send('dump')
        try:
            while True:
                print(self.read(), end='')
                time.sleep(5)
        except KeyboardInterrupt:
            time.sleep(.2)
            self.read()
            return

    def make_zones(self):
        zones = self.sm()
        for zone in zones:
            self.data[zone] = []

    def save_dump(self):
        self.read()
        print("Press Ctrl-C to stop dump, this will not stop the program")
        self.make_zones()
        self.send('dump')
        while True:
            info = self.read()
#            print("info: " + info)
            zones_data = info.split('\r\n')
#            print("zones_data: " + zones_data.__str__())
            if info != '':
                for zone in zones_data:
#                    print("zone: " + zone.__str__())
                    parsed_data = self.parse(zone)
#                    print("parsed data: " + parsed_data.__str__())
                    if parsed_data != []: #get help from dump gather
                        #add temp to the array associated with the zone number
                        self.data[parsed_data[0]].append(parsed_data[1])
            time.sleep(5)

    #parses the dump log.
    def parse(self, s):
        s_arr = s.split(' ')
#        print("s_arr: " + s_arr.__str__())
        #0 = time, 1 = date, 2 = zone, 3 = status, 4 = set-point, 5 = high alarm limit,
        #6 = low alarm limit, 7 = actual temp, 8 = duty cycle, 9 = heater status

        if len(s_arr) != 10: #bad data, error
            return []

        self.error_check(s_arr)
        if self.start == True:
            self.opened_time = s_arr[1] + '_' + re.sub(':', '-', s_arr[0])
            self.start = False
#        print('s_arr: ' + s_arr.__str__())
        temp_C = int(float(re.sub('[A-Z]', '', s_arr[7])) * 10) #temperature in celsius, changed from string to float, then it is multiplied by ten for int
        z_num = int(s_arr[2][1:])
        return [z_num, temp_C] #can change how much information you want to return

    def error_check(self, info):
        code = info[3][-3:] #trims the string down to it's last 3 characters
        #IMPORTANT: I'm allowing disabled zones through for now, might change in final version
        if (code != '001' or code != '000'): #error has happened
            error_msg = code + ': ' + self.error_ref[code]
            #TODO: not sure what to do with the error, store it for now
            self.raised_errors.append(info)
            print('error msg: ' + error_msg)

            #print(self.raised_errors)
            
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

    #using pickle
    def save(self):
        pickle_out = open('briskheat' + self.opened_time + '.data', 'wb')
        pickle.dump({'opened_time' : self.opened_time, 'port' : self.port, 'data' : self.data}, pickle_out)
        pickle_out.close()

    def data_load(self, file_name):
        rv = 'file failed to load'
        pickle_in = open(file_name,"rb")
        rv = pickle.load(pickle_in)
        return rv
