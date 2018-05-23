import briskheat_serial_reader
import time

ports = ['COM3'] #insert list of coms here, could be a param to make_briskheats()
briskheats = []
num_of_responses = 0;
data = [] #will be an array of arrays with the index of the data array corresponding with the index of the port/briskheat. This is an implicit association. Is a 3d array (array of all the briskheats, and in each of those an array of all the information, which is also stored in arrays
raised_errors = []
error_ref = {    
    8001 : 'STATUS_OK Current temperature is within alarm limits',
    8002 : 'STATUS_HIGH Current temperature is above high alarm limit',
    8004 : 'STATUS_LOW Current temperature is below the low alarm limit',
    8008 : 'STATUS_RTD_SHORT RTD is shorted',
    8010 : 'STATUS_RTD_OPEN RTD is open',
    8080 : 'STATUS_TRIAC_DRIVER_BAD Triac driver is not responding',
    8100 : 'STATUS_TRIAC_DRIVER_BAD Triac driver is not responding',
    8101 : 'STATUS_NETWORK_COMMS_BAD Communications channel is bad',
    8200 : 'STATUS_NETWORK_COMMS_BAD Communications channel is bad',
    8201 : 'STATUS_HEATER_CONFIG_COMM_BAD Communication failed during heater configuration',
    8400 : 'STATUS_HEATER_CONFIG_COMM_BAD Communication failed during heater configuration',
    8401 : 'STATUS_LINE_CTRL_COMM_BAD Communication error with heater line module',
    0000 : 'STATUS_HEATER_DISABLED Zone is disabled'
}

#initialize all the briskheats store data in arrays
def make_briskheats():
    for port in ports:
        bh = briskheat_serial_reader.Briskheat(port)
        bh.connect()
        briskheats.append(bh)
        data.append([]) #make as many arrays as there are briskheats

#sends the same message to all the briskheats
def mass_send(msg):
    for bh in briskheats:
        bh.quick_send(msg)
    time.sleep(1)

def mass_read():
    rv = []
    for bh in briskheats:
        rv.append(bh.read())
    return rv
        
#Run dump on all the bh and gather data, storing it in arrays
#WARNING: once in a while there is going to be a pair of bad data points due to the nature of time on machines not being exactly synced and the briskheat taking time to spew numbers. The strange numbers on time.sleep are so odd to counteract this effect.
def dump_gather():
    mass_send('dump')
    mass_read(); #get rid of first message, which is an intro message
    while True:
        dump_vals = mass_read();
        #print for testing purposes
        #print('dump_vals: ' + dump_vals.__str__())
        #TODO: check if dump_vals is empty
        record = False
        for vals in dump_vals:
            if len(vals) != 0:
                record = True;
        if record:
            buffer = []
            data_integrity = True
            for v in dump_vals:
                pv = parse(v)
                buffer.append(pv)
                if pv == 'error':
                    data_integrity = False
                    error_msg = "bad data error: one error every 1000 secs is normal"
                    raised_errors.append(error_msg)
                    print(error_msg)
            if data_integrity:
                for i in range(len(buffer)):
                    data[i].append(buffer[i])
            #for debugging
            print('data: ' + data.__str__())
        time.sleep(4.63)

#parses the dump log. Temp is multiplied by ten
def parse(s):
    s_arr = s.split(' ')
    #1 = time, 2 = date, 3 = zone, 4 = status, 5 = set-point, #6 = high alarm limit,
    #7 = low alarm limit, 8 = actual temp, 9 = duty cycle, 10 = heater status
    #whats important: 4 - 1 status, 8 - 1 actual temp,

    if len(s_arr) != 10: #bad data, return False, attempts to filter out bad data.
        return 'error'
    
    error_code = s_arr[3][-4:] #trims the string down to it's last 4 characters
    if (error_code != '8001'): #error has happened
        error_msg = error_code + ': ' + error_ref[error_code]
        #TODO: not sure what to do with the error, store it for now
        raised_errors.append(s_arr)
        print('error msg: ' + error_msg.__str__())

    #print('s_arr: ' + s_arr.__str__())
    temp = int(float(s_arr[7][2:8]) * 10)
    return [temp] #can change how much information you want to return(length of array).

make_briskheats()
dump_gather()
