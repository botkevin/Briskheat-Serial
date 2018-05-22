import Briskheat
import time

ports = [] #insert list of coms here, could be a param to make_briskheats()
briskheats = []
num_of_responses = 0;
data = [] #will be an array of arrays with the index of the data array corresponding with the index of the port/briskheat. This is an implicit association.

briskheat_message_to_int_message = {

#TODO: initialize all the briskheats store data in arrays
def make_briskheats():
    for port in ports:
        bh = new Briskheat(port)
        bh.connect()
        briskheats.append(bh)
        data.append([]) #make as many arrays as there are briskheats

#sends the same message to all the briskheats
def mass_send(msg):
    for i in range(briskheats.length):
        briskheats[i].quick_send(msg)
    time.sleep(1)

def mass_read():
    rv = []
    for i in range(briskheats.length):
        rv.append(briskheats.read())
    return rv
        
#TODO: Run dump on all the bh and gather data, storing it in arrays, dont forget to multiply temp by 10 so no decimals
def dump_gather():
    mass_send('dump')
    while True:
        dump_vals = mass_read();
        #print for testing purposes
        print(dump_vals)



def parse(s):
    s_arr = s.split(' ')
    #1 = time, 2 = date, 3 = zone, 4 = status, 5 = set-point, #6 = high alarm limit,
    #7 = low alarm limit, 8 = actual temp, 9 = duty cycle, 10 = heater status
    #whats important: 8 - 1 actual temp, 4 - 1 status
    return s_arr[3], s_arr[7]
