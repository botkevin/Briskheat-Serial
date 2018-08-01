# @author Kevin Shi

import serial
import time
import re
import datetime
import database_interface

'''
This file will interact with the Briskheat, taking parameters of the port to open, interval in units of 10 seconds,
directory and filename to store the info, and directory filename for status.
Use once the briskheat object is created, use save_dump() to start logging. 
Use ez_terminal() to connect and interact with the Briskheat if debugging/ managing briskheats
Disabled zones are currently not counted as errors, see: IMPORTANT.
'''

class Briskheat:
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

    # @params tool : name of tool this briskheat is monitoring
    #         path : port to open,
    #         poll_interval_x10 : interval to poll data: unit of time is ten seconds,
    #         sql_interval_xpoll : interval to send information to datase: unit of time is 1 poll interval
    #         status_dir : directory to write status and log messages to
    #         host : host of sql databse
    #         user : username for the sql server
    #         pswd : password for the sql server
    #         db : sql database name
    #         t : table name to store the data in
    #         lt: log table to store status and log messages
    # See testBriskheatSql.py for example of usage
    def __init__(self, tool, path, poll_interval_x10, sql_interval_xpoll, status_dir, host, user, pswd, db, t, lt):
        self.port = path
        self.open(path)
        self.reconnect_tries = 0
        self.data = {}
        self.raised_errors = []
        assert(poll_interval_x10 > 0)
        self.poll_interval = poll_interval_x10
        assert(sql_interval_xpoll > 0)
        self.sql_interval = sql_interval_xpoll
        self.status_dir = status_dir
        self.connect_sql()
        self.connect()

     def connect_sql(self):
        try:
            self.db = database_interface.database_interface(host, user, pswd, db, t)
            self.log = database_interface.database_interface(host, user, pswd, db, lt, tool, path)
        except NotImplementedError:
            e = open(self.status_dir, 'a')
            e.write('SQL connection error:, ' + str(datetime.datetime.now()) +'\n')
            e.close()
            time.sleep(20)
            self.connect_sql()
            
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
        message = message + "\r" #takes \r carriage return as end of message protocal
        msg = message.encode('ascii')
        self.ser.write(msg)
        time.sleep(.1) #wait for briskheat to respond


    #writes but does not wait
    def quick_send(self, message):
        message = message + "\r" #refer to above
        msg = message.encode('ascii')
        self.ser.write(msg)

    #reads from serialport
    def read(self):
        out = ''
        while self.ser.inWaiting() > 0:
            out += self.ser.read(1).decode('ascii')
        time.sleep(.1)
        if self.ser.inWaiting() > 0: #tests if the briskheat is done outputting
            out += self.read()
        return out

    #send and read
    def send_and_read(self, message):
        self.send(message)
        return self.read()

    #debug tool to send, read, and print
    def wPrint(self, message):
        print(self.send_and_read(message), end='') #no newline print

    #Inputs the password and connects to the briskheat 
    def connect(self):
        pswd = 'briskheat' #default
        self.send_and_read(pswd)
        time.sleep(.5)
        self.send_and_read(pswd)
        self.open_time = str(datetime.datetime.now())

    #closes connection to the briskheat
    def close(self):
        self.wPrint('bye')
        self.ser.close()
        e = open(self.status_dir, 'a')
        e.write('Graceful exit:, ' + str(datetime.datetime.now()) +'\n')
        e.close()
        

    #user friendly terminal interface for briskheat interaction, enter '?' to see commands   
    def ez_terminal(self):
        print("BriskHeat Interface Terminal. Enter '?' for help.")
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
        self.read()
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

    def make_zones(self, zones):
        for zone in zones:
            self.data[zone] = []

    #starts a new file for status logs
    def start_log(self):
        e = open(self.status_dir, 'a')
        e.write('Port:, ' + self.port + '\n')
        e.write('Opened Time:, ' + self.open_time + '\n')
        e.close()
        self.log.write_log(self.open_time, 'Start Dump')

    #saves the info
    def save_dump(self):
        self.read()
        print("Press Ctrl-C to stop dump, this will not stop the program")
        self.zone_numbers = self.sm()
        self.time = []
        self.make_zones(self.zone_numbers)
        self.send('dump')
        self.start_log()
        e = open(self.status_dir, 'a')
        e.write('Dump start time:, ' + str(datetime.datetime.now()) +'\n')
        e.write('Time, Error, Zone, Dump\n')
        poll_interval_count = self.poll_interval - 1
        sql_interval_count = self.sql_interval - 1
        try:
            while True:
                info = self.read()
    #            print("info: " + info)
                zones_data = info.split('\r\n')
    #            print("zones_data: " + zones_data.__str__())
                if info != '':
                    poll_interval_count += 1
                    if poll_interval_count == self.poll_interval:
                        poll_interval_count = 0
                        sql_interval_count += 1
                        for zone in zones_data:
        #                    print("zone: " + zone.__str__())
                            parsed_data = self.parse(zone)
        #                    print("parsed data: " + parsed_data.__str__())
                            if parsed_data != []:
                                #assign temp to the associated zone number
                                self.data[parsed_data[0]].append(parsed_data[1])
                                if self.time == [] or self.time[-1] != parsed_data[2]:
                                    self.time.append(parsed_data[2])
                    if sql_interval_count == self.sql_interval:
                        self.send_sql()
                        sql_interval_count = 0
                time.sleep(5)
        except KeyboardInterrupt:
            print('Dump stopped')
            e = open(self.status_dir, 'a')
            e.write('Dump stop time:, ' + str(datetime.datetime.now()) +'\n')
            e.close()
            self.log.write_log(str(datetime.datetime.now())[:-7], 'Stop Dump')

    def send_sql(self):
        #TODO: send self.data which is a dictionary
        self.db.write(self.time, self.data)
        self.make_zones(self.zone_numbers)
        self.time = []

    #parses the dump log.
    def parse(self, s):
        s_arr = s.split(' ')
#        print("s_arr: " + s_arr.__str__())
        #0 = time, 1 = date, 2 = zone, 3 = status, 4 = set-point, 5 = high alarm limit,
        #6 = low alarm limit, 7 = actual temp, 8 = duty cycle, 9 = heater status
        if len(s_arr) != 10: #bad data, error
            return []
        temp_C = float(re.sub('[A-Z]', '', s_arr[7])) #temperature in celsius, changed from string to float
        z_num = int(s_arr[2][1:])
        z = s_arr[1]
        date = z[0:4] + '-' + z[4:6] + '-' + z[6:]
        time = date + ' ' + s_arr[0]
        return [z_num, temp_C, time] #can change how much information you want to return

    def error_check(self, info):
        code = info[3][-3:] #trims the string down to it's last 3 characters
        #IMPORTANT: I'm allowing disabled zones through for now, might change in final version
        if (code != '001' and code != '000'): #error has happened
            error_msg = code + ': ' + self.error_ref[code]
            #TODO: not sure what to do with the error, store it for now
            human_read = self.parse(info)
            e = open(self.status_dir, 'a')
            time = human_read[2]
            z_num = human_read[0]
            e.write(time + ', ' + error_msg + ', ' + zone + ',' + info.__str__() + '\n')
            e.close()
            self.log.write_log(time, 'err:' + code, zone, self.error_ref[code])
            #print('error msg: ' + error_msg)
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
