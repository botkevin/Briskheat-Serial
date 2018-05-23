import serial
import time

#connecting to Port COM3, check device manager
#returns the initialized serialport
#TODO: find out a way to raise an error if no connection

class Briskheat:
    #Serial ser;
    #String port
    
    def __init__(self, path):
        self.port = path
        self.open(path)

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
        self.connect()
        print('BH> ', end='')
        while True:
            try:
                s = input().lower()
                if s == 'dump':
                    self.get_dump()
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
                
    #starts dump command for briskheat
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
            print('BH> ', end='')
            return

    def get_dump_and_parse():
        return

    def restart():
        self.close()
        self.open()
        
    def __repr__(self):
        return 'Port: ' + self.port + self.send_and_read('show')

