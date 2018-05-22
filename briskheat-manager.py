import Briskheat
import time

ports = [] #insert list of coms here, could be a param to make_briskheats()
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
        bh = new Briskheat(port)
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
        
#TODO: Run dump on all the bh and gather data, storing it in arrays, dont forget to multiply temp by 10 so no decimals
def dump_gather():
    mass_send('dump')
    while True:
        dump_vals = mass_read();
        #print for testing purposes
        print(dump_vals)
        for i in range(dump_vals.length):
            val = parse(dump_vals[i]) #vals is an array
            data[i].append(val)

def parse(s):
    s_arr = s.split(' ')
    #1 = time, 2 = date, 3 = zone, 4 = status, 5 = set-point, #6 = high alarm limit,
    #7 = low alarm limit, 8 = actual temp, 9 = duty cycle, 10 = heater status
    #whats important: 4 - 1 status, 8 - 1 actual temp,
    error_code = s_arr[3][-4:] #trims the string down to it's last 4 characters
    if (error_code != '8001'): #error has happened
        error_msg = error_code + ': ' + error_ref[error_code]
        #TODO: not sure what to do with the error, store it for now
        raised_errors.append(s_arr)
    temp = s_arr[7]
    return [temp] #can change how much information you want to return(length of array).
