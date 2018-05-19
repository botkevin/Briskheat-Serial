import Briskheat

ports = [] #insert list of coms here
briskheats = []
data = []
briskheat_message_to_int_message = {

#TODO: initialize all the briskheats store data in arrays
def make_briskheats():
    for port in ports:
        bh = new Briskheat(port)
        bh.connect()
        briskheats.append(bh)
        data.append([port])
    #TODO: need to deal with failure to connect/open serial port
        
#TODO: Run dump on all the bh and gather data, storing it in arrays, dont forget to multiply temp by 10 so no decimals
def dump_gather():
    for i in range(briskheats.length):
        briskheats[i].send('dump
                          
def parse(s):
    s_arr = s.split(' ')
    #1 = time, 2 = date, 3 = zone, 4 = status, 5 = set-point, #6 = high alarm limit,
    #7 = low alarm limit, 8 = actual temp, 9 = duty cycle, 10 = heater status
    #whats important: 8 - 1 actual temp, 4 - 1 status
    return s_arr[3], s_arr[7]
